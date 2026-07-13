"""Agent-Assure: evidence-store models and loader.

No LLM, no network, no random, no wall-clock in logic.
All text inputs are NFKC-normalized before any match/regex gate.
Pure functions only — never mutate inputs or globals.
"""

from __future__ import annotations

import json
import unicodedata
from collections import Counter
from dataclasses import dataclass
from enum import Enum
from typing import Iterator


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------

class Verdict(str, Enum):
    GROUNDED = "GROUNDED"
    UNGROUNDED = "UNGROUNDED"
    UNCITED = "UNCITED"
    UNVERIFIED_CITATION = "UNVERIFIED_CITATION"
    UNVERIFIED_NUMBER = "UNVERIFIED_NUMBER"
    UNVERIFIED_ABSENCE = "UNVERIFIED_ABSENCE"
    UNVERIFIED_RELATION = "UNVERIFIED_RELATION"
    UNGROUNDABLE = "UNGROUNDABLE"
    ABSENCE_SUPPORTED = "ABSENCE_SUPPORTED"


class ClaimKind(str, Enum):
    FACTUAL = "FACTUAL"
    NUMERIC = "NUMERIC"
    ABSENCE = "ABSENCE"
    ATTRIBUTION = "ATTRIBUTION"
    RELATIONAL = "RELATIONAL"
    NON_CLAIM = "NON_CLAIM"


# ---------------------------------------------------------------------------
# Data models
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class RetrievedSource:
    source_id: str
    url: str | None
    file_path: str | None
    fetched_at: str
    tool: str
    content_sha256: str
    text: str
    full_text_source: str
    captured_via: str
    query_provenance: str


@dataclass(frozen=True)
class Claim:
    index: int
    text: str
    kind: ClaimKind
    citations: tuple[str, ...]
    numeric_tokens: tuple[str, ...]


# ---------------------------------------------------------------------------
# Functions
# ---------------------------------------------------------------------------

def _nfkc(s: str) -> str:
    """Return NFKC-normalized form of s."""
    return unicodedata.normalize("NFKC", s)


def load_store(path: str) -> dict[str, RetrievedSource]:
    """Read a JSONL file and return a dict indexed by NFKC-normalized source_id.

    Blank lines are skipped. Returns a new dict; does not mutate any input.
    """
    store: dict[str, RetrievedSource] = {}
    with open(path, encoding="utf-8") as fh:
        for raw_line in fh:
            line = raw_line.strip()
            if not line:
                continue
            obj = json.loads(line)
            source_id = _nfkc(obj["source_id"])
            source = RetrievedSource(
                source_id=source_id,
                url=obj.get("url"),
                file_path=obj.get("file_path"),
                fetched_at=obj["fetched_at"],
                tool=obj["tool"],
                content_sha256=obj["content_sha256"],
                text=_nfkc(obj["text"]),
                full_text_source=obj["full_text_source"],
                captured_via=obj["captured_via"],
                query_provenance=obj["query_provenance"],
            )
            store[source_id] = source
    return store


# ---------------------------------------------------------------------------
# Claim decomposition
# ---------------------------------------------------------------------------

# Common auxiliary/copula verbs for conjunction-split verb detection.
_AUXILIARIES: frozenset[str] = frozenset({
    "is", "are", "was", "were", "has", "have", "had",
    "do", "does", "did", "can", "could", "will", "would",
    "should", "may", "might", "must", "shall", "be", "been", "being",
})

# Verb-ending suffixes used in conservative verb-like detection.
_VERB_SUFFIXES: tuple[str, ...] = ("s", "ed", "ing", "en")
_VERB_SUFFIX_MIN_LEN: int = 4


def _has_verb_like_token(tokens: list[str]) -> bool:
    """Return True if any token in *tokens* is verb-like.

    Conservative heuristic:
    1. Auxiliary/copula membership (case-insensitive): the token with trailing
       punctuation stripped is checked against _AUXILIARIES so that "is." and
       "are," still match.
    2. Lowercase suffix rule (length >= 4, ends in a common verb suffix) — BUT
       only when the original token does NOT start with an uppercase letter.
       Capitalized tokens are treated as proper nouns, not verbs, so that a
       compound subject like "Redis and Postgres are fast." is not over-split.
       The suffix check uses the original token (no punctuation stripping) to
       preserve the original conservative behaviour — "oranges." ends in '.'
       not 's', so it does not falsely fire.
       Under-split beats over-split (spec §9).
    """
    for t in tokens:
        # Auxiliary check: strip trailing punctuation so "is." → "is" matches.
        t_core = t.rstrip(".,;:!?")
        w_core = t_core.lower()
        if w_core in _AUXILIARIES:
            return True
        # Suffix rule: skip capitalized tokens (likely proper nouns).
        if t_core and t_core[0].isupper():
            continue
        # Use original token (with punctuation) for suffix check — preserves
        # prior conservative behaviour where "oranges." ≠ ends-in-'s'.
        w_orig = t.lower()
        if len(w_orig) >= _VERB_SUFFIX_MIN_LEN and any(w_orig.endswith(s) for s in _VERB_SUFFIXES):
            return True
    return False


def _reconstruct_sentence(sentence_tokens: list) -> str:  # sentence_tokens: list[Token]
    """Reconstruct a sentence string from syntok Token objects.

    Each Token carries a *spacing* attribute (the whitespace that precedes it)
    and a *value* attribute (the token text). The first token has no leading
    space by convention (spacing == '').
    """
    parts: list[str] = []
    for i, tok in enumerate(sentence_tokens):
        if i == 0:
            parts.append(tok.value)
        else:
            parts.append(tok.spacing + tok.value)
    return "".join(parts)


def _conjunction_split(sentence: str) -> list[str]:
    """Split *sentence* on '; ' or ' and ' only when both halves carry a verb-like token.

    Conservative: under-split beats over-split (spec §9).
    Only one level of splitting is attempted per sentence; nested splits are
    not performed.
    """
    for sep in ("; ", " and "):
        pos = sentence.find(sep)
        if pos == -1:
            continue
        left = sentence[:pos]
        right = sentence[pos + len(sep):]
        left_tokens = left.split()
        right_tokens = right.split()
        if _has_verb_like_token(left_tokens) and _has_verb_like_token(right_tokens):
            # Strip trailing punctuation carried into *left* from the separator
            return [left.rstrip(";").strip(), right.strip()]
    return [sentence]


def _iter_raw_sentences(text: str) -> Iterator[str]:
    """Yield NFKC-normalized sentence strings from *text* using syntok."""
    import syntok.segmenter as segmenter  # lazy import — keeps top-level pure

    normalized = _nfkc(text)
    for paragraph in segmenter.process(normalized):
        for sentence_tokens in paragraph:
            yield _reconstruct_sentence(sentence_tokens)


def decompose(draft: str) -> list[Claim]:
    """Decompose *draft* into atomic Claim objects.

    Steps:
    1. NFKC-normalize (inside _iter_raw_sentences via _nfkc).
    2. Segment into sentences with syntok.
    3. Apply conservative conjunction split on '; ' / ' and ' only when
       both sides carry a verb-like token.
    4. Emit one Claim per sentence with index, text, kind=FACTUAL (placeholder),
       citations=(), numeric_tokens=().

    Pure function — no LLM, no network, no random, no wall-clock.
    """
    if not draft or not draft.strip():
        return []

    claims: list[Claim] = []
    index = 0
    for raw_sentence in _iter_raw_sentences(draft):
        for text in _conjunction_split(raw_sentence):
            text = text.strip()
            if not text:
                continue
            claims.append(Claim(
                index=index,
                text=text,
                kind=ClaimKind.FACTUAL,
                citations=(),
                numeric_tokens=(),
            ))
            index += 1
    return claims


# ---------------------------------------------------------------------------
# Claim classification
# ---------------------------------------------------------------------------

import re as _re

# Citation pattern: [S1], [S12], [source:some-text]
# S\d+ plus optional letter suffix (OI-CITE-01): `[S1a]` is a citation MARKER
# even though capture never emits letter-suffixed ids — leaving it unmatched
# made the marker invisible (claim read UNCITED and the bracket digit leaked
# into numeric_tokens). Matched, it resolves like any key: absent from the
# store -> the precise UNVERIFIED_CITATION verdict.
_CITATION_RE = _re.compile(r"\[(?:S\d+[a-zA-Z]*|source:[^\]]+)\]")

# Relational trigger lexicon for argument extraction (ordered longest-first so
# multi-word triggers match before their shorter prefixes; e.g. "caused by"
# before "causes").
_RELATIONAL_TRIGGERS: tuple[str, ...] = (
    "gives rise to",
    "is responsible for",
    "the reason for",
    "results in",
    "because of",
    "caused by",
    "leads to",
    "due to",
    "causes",
    "drives",
)

# NumericToken pattern: optional $, digit cluster with optional suffix
_NUMERIC_RE = _re.compile(
    r"\$?\d[\d,.]*\s?(?:%|million|billion|k|m|bn)?",
    _re.IGNORECASE,
)

# Relational trigger lexicon (order-independent; checked via search)
_RELATIONAL_RE = _re.compile(
    r"\b(?:causes|caused by|leads to|results in|drives|because of|due to"
    r"|gives rise to|is responsible for|the reason for)\b",
    _re.IGNORECASE,
)

# Absence triggers
_ABSENCE_RE = _re.compile(
    r"\b(?:no |not |does not exist|there is no|we found no)",
    _re.IGNORECASE,
)

# Attribution triggers
_ATTRIBUTION_RE = _re.compile(
    r"\b(?:according to|per |states that)\b",
    _re.IGNORECASE,
)

# Finite-verb detection: simple heuristic — if the string has at least one
# word that is an auxiliary or ends in a common verb suffix and is ≥4 chars.
_NO_FINITE_VERB_RE = _re.compile(r"^#+\s")  # header pattern sufficient for NON_CLAIM first check

# Pure transition phrases (no claim content)
_TRANSITION_PHRASES: frozenset[str] = frozenset({
    "in summary", "to summarise", "to summarize", "in conclusion",
    "in other words", "for example", "for instance", "that is",
    "in addition", "furthermore", "moreover", "however", "therefore",
    "thus", "hence", "consequently", "as a result", "on the other hand",
})


def _has_finite_verb(text: str) -> bool:
    """Return True if *text* appears to contain a finite verb (rough heuristic).

    Mirrors _has_verb_like_token: capitalized tokens (likely proper nouns) are
    excluded from the suffix rule so that both verb-detection paths share
    identical behaviour.
    """
    tokens = _re.split(r"\s+", text)
    auxiliaries = _AUXILIARIES
    suffixes = _VERB_SUFFIXES
    min_len = _VERB_SUFFIX_MIN_LEN
    for t in tokens:
        t_core = t.rstrip(".,;:!?")
        w_core = t_core.lower()
        if w_core in auxiliaries:
            return True
        # Skip capitalized tokens — treat as proper nouns, not verbs.
        if t_core and t_core[0].isupper():
            continue
        w_orig = t.lower()
        if len(w_orig) >= min_len and any(w_orig.endswith(s) for s in suffixes):
            return True
    return False


def _is_non_claim(text: str) -> bool:
    """Return True if *text* is a header, pure transition, or a verbless fragment
    carrying NO verifiable content.

    MOAT-SAFE rule (anti-gaming): a verbless sentence that carries a numeric token
    or a citation marker is real, verifiable claim content — it MUST NOT be
    excluded as NON_CLAIM, or a draft of purely verbless fabricated claims (e.g.
    "A 99% market share for our product [S9].") would shrink the denominator to
    zero and post a vacuous PASS. NON_CLAIM stays reserved for headers, pure
    transitions, and verbless fragments with no numeric/citation content. When
    unsure, classify as a real claim — over-scoring is safe; silently excluding a
    fabricated claim is the failure.
    """
    # Header ('#'-prefixed): a heading that carries a citation marker or a numeric
    # token is real, verifiable claim content and MUST NOT be excluded — otherwise
    # a fabricated claim hides behind '# ...' and vanishes from the denominator
    # (a false PASS). This is the IDENTICAL moat-safe rule the verbless-fragment
    # guard below applies; the Phase-1a fix installed it there but not here, so
    # header-wrapped fabrications reached PASS. A heading with no such content is a
    # genuine heading → NON_CLAIM.
    header_match = _NO_FINITE_VERB_RE.match(text)
    if header_match:
        header_body = text[header_match.end():]
        has_citation = bool(_CITATION_RE.search(header_body))
        # Numeric content on the citation-stripped body so bracket digits (e.g.
        # [S9] → '9') do not count as numeric content.
        has_numeric = bool(_NUMERIC_RE.search(_CITATION_RE.sub("", header_body)))
        if has_citation or has_numeric:
            return False
        return True
    # Pure transition: strip citations, lowercase, and check against transition set
    stripped = _CITATION_RE.sub("", text).strip().rstrip(".,;:!?").lower()
    if stripped in _TRANSITION_PHRASES:
        return True
    # Verbless fragment: NON_CLAIM only if it carries no verifiable content.
    # A numeric token or a citation marker is verifiable content → real claim.
    if not _has_finite_verb(text):
        has_citation = bool(_CITATION_RE.search(text))
        # Numeric content is detected on the citation-stripped text so that bracket
        # digits (e.g. [S9] → '9') do not count as numeric content.
        has_numeric = bool(_NUMERIC_RE.search(_CITATION_RE.sub("", text)))
        if has_citation or has_numeric:
            return False
        return True
    return False


def classify(claim: Claim) -> Claim:
    """Return a new Claim with kind, citations, and numeric_tokens populated.

    Classification order (first match wins):
      NON_CLAIM → RELATIONAL → ABSENCE → NUMERIC → ATTRIBUTION → FACTUAL

    Hedging (likely/probably/it is believed) does NOT exempt a numeric or
    factual core.

    Pure function — returns a new frozen Claim; never mutates the input.
    NFKC normalization is applied before every regex gate.
    """
    text = _nfkc(claim.text)

    # --- Extract citations (from original normalized text) ---
    citations: tuple[str, ...] = tuple(_CITATION_RE.findall(text))

    # --- Extract numeric tokens from citation-stripped scratch copy ---
    # This prevents bracket digits like [S3] → '3' from leaking into numeric_tokens.
    _text_for_numeric = _CITATION_RE.sub("", text)
    _raw_numeric = _NUMERIC_RE.findall(_text_for_numeric)
    # Strip a single trailing period from each token (sentence-boundary artifact).
    # Preserves $4M, 25%, $4,000,000 unchanged since they don't end with '.'.
    numeric_tokens: tuple[str, ...] = tuple(
        t[:-1] if t.endswith(".") else t for t in _raw_numeric
    )

    # --- Ordered classification cascade ---
    if _is_non_claim(text):
        kind = ClaimKind.NON_CLAIM
    elif _RELATIONAL_RE.search(text):
        kind = ClaimKind.RELATIONAL
    elif _ABSENCE_RE.search(text):
        kind = ClaimKind.ABSENCE
    elif numeric_tokens:
        kind = ClaimKind.NUMERIC
    elif _ATTRIBUTION_RE.search(text):
        kind = ClaimKind.ATTRIBUTION
    else:
        kind = ClaimKind.FACTUAL

    return Claim(
        index=claim.index,
        text=claim.text,  # preserve original (pre-normalization) text
        kind=kind,
        citations=citations,
        numeric_tokens=numeric_tokens,
    )


# ---------------------------------------------------------------------------
# T1 — Verbatim grounding tier
# ---------------------------------------------------------------------------

def _tokenize(text: str) -> list[str]:
    """Return NFKC-casefolded word tokens from *text*.

    Tokenizer: re.findall(r"\\w+", ...) on NFKC + casefold.
    Pure function.
    """
    return _re.findall(r"\w+", _nfkc(text).casefold())


def _strip_citations(text: str) -> str:
    """Remove citation markers (e.g. [S1], [S12], [source:...]) from *text*.

    Used before tokenizing claim text so that citation tokens do not pollute
    span matching or F1 computation.
    """
    return _CITATION_RE.sub("", text)


def t1_verbatim(
    claim: Claim,
    sources: list[RetrievedSource],
    min_quote_len: int = 8,
) -> bool:
    """Return True iff a contiguous span of ≥ min_quote_len tokens from the
    claim appears verbatim in at least one source's text.

    Comparison is done under NFKC + case-fold + whitespace-collapse (i.e.
    tokens from re.findall(r"\\w+") on the casefolded NFKC form of both
    strings).  Citation markers (e.g. [S1]) are stripped from the claim
    before tokenizing so they do not inflate the token list.

    Default min_quote_len=8 per spec/design contract.  The canonical hit-test
    claim ("Redis handles 100K operations per second on commodity hardware
    [S1].") yields exactly 8 content tokens after citation stripping, matching
    the default threshold.

    Caller is responsible for filtering sources to verbatim-only before
    calling this function — do NOT filter by full_text_source here.

    Pure function — no mutation, no LLM/network/random/wall-clock.
    """
    if not sources:
        return False

    # Strip citations before tokenizing so bracket tokens (e.g. 's1' from '[S1]')
    # do not inflate the claim token list and prevent contiguous-span matching.
    claim_tokens = _tokenize(_strip_citations(claim.text))
    n = len(claim_tokens)
    if n < min_quote_len:
        return False

    for source in sources:
        source_tokens = _tokenize(source.text)
        # Build a set of all contiguous n-grams in the source for O(n) lookup.
        # For each window size from min_quote_len up to n, check if any
        # contiguous claim sub-sequence appears in source.
        # Strategy: slide a window of min_quote_len over claim tokens and
        # check membership in source via tuple comparison.
        m = len(source_tokens)
        if m < min_quote_len:
            continue
        # Build a set of source n-grams of length min_quote_len.
        source_ngrams: set[tuple[str, ...]] = set()
        for i in range(m - min_quote_len + 1):
            source_ngrams.add(tuple(source_tokens[i : i + min_quote_len]))
        # Check each claim window of length min_quote_len.
        for j in range(n - min_quote_len + 1):
            if tuple(claim_tokens[j : j + min_quote_len]) in source_ngrams:
                return True

    return False


# ---------------------------------------------------------------------------
# T2 — Lexical-F1 + numeric-presence grounding tier
# ---------------------------------------------------------------------------

# Stop words for content-word filtering (small functional set).
_STOP_WORDS: frozenset[str] = frozenset({
    "a", "an", "the", "and", "or", "but", "in", "on", "at", "to", "for",
    "of", "with", "by", "from", "as", "is", "are", "was", "were", "be",
    "been", "being", "have", "has", "had", "do", "does", "did", "will",
    "would", "could", "should", "may", "might", "must", "shall", "it",
    "its", "this", "that", "these", "those", "i", "we", "you", "he",
    "she", "they", "not", "no", "so", "if", "then", "than", "about",
    "more", "also", "just", "up", "out", "into", "over", "after", "s",
    "per",
})


def _content_words(tokens: list[str]) -> list[str]:
    """Return tokens that are not stop words."""
    return [t for t in tokens if t not in _STOP_WORDS]


def _f1(claim_words: list[str], window_words: list[str]) -> float:
    """Compute content-word F1 between claim_words and window_words.

    Spec metric = content-word F1; claim-recall (no precision penalty) may
    suit verbose sources better — deferred to the calibration phase
    (spec §12.5), not silently substituted.

        P = |intersection| / |window_words|
        R = |intersection| / |claim_words|
        F1 = 0 if P+R==0 else 2*P*R / (P+R)

    Uses multiset intersection (each token matched at most once).
    Returns 0.0 when either list is empty.
    """
    if not claim_words or not window_words:
        return 0.0

    claim_counter = Counter(claim_words)
    window_counter = Counter(window_words)

    # |intersection| = sum of min counts over shared keys
    intersection = sum(
        min(claim_counter[t], window_counter[t]) for t in claim_counter
    )

    precision = intersection / len(window_words)
    recall = intersection / len(claim_words)
    if precision + recall == 0:
        return 0.0
    return 2 * precision * recall / (precision + recall)


def _split_sentences(text: str) -> list[str]:
    """Split *text* into sentences on '.', '!', '?' boundaries.

    Simple regex-based splitter; sufficient for T2 windowing.
    Returns list of non-empty stripped sentence strings.
    """
    parts = _re.split(r"(?<=[.!?])\s+", _nfkc(text).strip())
    return [p.strip() for p in parts if p.strip()]


def _best_window_score(
    claim_content: list[str],
    claim_numeric: tuple[str, ...],
    sentences: list[str],
) -> float:
    """Return the best F1 over all ±2-sentence windows across *sentences*.

    For each centre sentence index c, the window is sentences[max(0,c-2) : c+3].
    Returns 0.0 when no window satisfies the numeric-presence gate.
    """
    best = 0.0
    n = len(sentences)
    for c in range(n):
        lo = max(0, c - 2)
        hi = min(n, c + 3)
        window_text = " ".join(sentences[lo:hi])
        window_tokens = _tokenize(window_text)

        # Numeric-presence gate: every claim numeric token must appear in the
        # window token list (NFKC-casefolded comparison).
        if claim_numeric:
            numeric_tokens_cf = [_nfkc(nt).casefold() for nt in claim_numeric]
            # numeric tokens may contain non-word characters (e.g. '%', '$')
            # so we match against the raw casefolded window text, not just \w+ tokens
            window_text_cf = _nfkc(window_text).casefold()
            if not all(nt in window_text_cf for nt in numeric_tokens_cf):
                continue

        window_content = _content_words(window_tokens)
        score = _f1(claim_content, window_content)
        if score > best:
            best = score

    return best


def _numeric_tokens_from_text(text: str) -> tuple[str, ...]:
    """Return numeric tokens extracted from *text*.

    Mirrors the numeric-token extraction embedded in classify(): NFKC-
    normalize, strip citation markers (so bracket digits like '[S3]' cannot
    leak in), find numeric expressions via _NUMERIC_RE, then strip a single
    trailing period from each token (sentence-boundary artifact).

    For any Claim produced by classify(), this always yields the same tuple
    as claim.numeric_tokens — kept as a standalone helper (rather than
    reusing classify()) so t2_lexical_score can work from raw claim text
    alone, per its (str, str) -> float interface.
    """
    normalized = _nfkc(text)
    text_for_numeric = _CITATION_RE.sub("", normalized)
    raw_numeric = _NUMERIC_RE.findall(text_for_numeric)
    return tuple(t[:-1] if t.endswith(".") else t for t in raw_numeric)


def t2_lexical_score(claim_text: str, source_text: str) -> float:
    """Return the max content-word F1 between *claim_text* and the best
    ±2-sentence window of *source_text*, subject to the numeric-presence gate
    (every numeric token extracted from claim_text must appear in the
    window) — i.e. the raw score t2_lexical thresholds against lex_tau.

    Extracted from t2_lexical so a calibration sweep can re-threshold
    lex_tau post-hoc over a stored score, without re-running the gate.

    Returns 0.0 when claim_text has no content words, source_text has no
    sentences, or (for claims with numeric tokens) no window contains a
    verbatim match for every one of them.

    Pure function — no mutation, no LLM/network/random/wall-clock.
    """
    claim_tokens = _tokenize(_strip_citations(claim_text))
    claim_content = _content_words(claim_tokens)
    if not claim_content:
        return 0.0

    claim_numeric = _numeric_tokens_from_text(claim_text)

    sentences = _split_sentences(source_text)
    if not sentences:
        return 0.0

    return _best_window_score(claim_content, claim_numeric, sentences)


def t2_lexical(
    claim: Claim,
    sources: list[RetrievedSource],
    lex_tau: float = 0.65,
) -> bool:
    """Return True iff content-word F1 between the claim and the best ±2-sentence
    window of some source ≥ lex_tau AND every claim.numeric_token is present in
    that window.

    Caller is responsible for filtering sources to verbatim-only before
    calling this function — do NOT filter by full_text_source here.

    Pure function — no mutation, no LLM/network/random/wall-clock.
    """
    if not sources:
        return False

    # Strip citations before tokenizing so bracket tokens (e.g. 's1' from '[S1]')
    # do not pollute content-word F1 computation.
    claim_tokens = _tokenize(_strip_citations(claim.text))
    claim_content = _content_words(claim_tokens)

    if not claim_content:
        return False

    for source in sources:
        if t2_lexical_score(claim.text, source.text) >= lex_tau:
            return True

    return False


# ---------------------------------------------------------------------------
# T3 — Numeric grounding check
# ---------------------------------------------------------------------------

# Pattern to find numeric expressions in source text.
# Captures: optional $, digit cluster with commas, optional space + suffix.
# Word-boundary anchored on suffix to avoid substring matches (e.g. "25%" in
# source must not also yield a stray "5" or "2" match from inside the token).
_SOURCE_NUMERIC_RE = _re.compile(
    r"\$?\d[\d,.]*\s?(?:million|billion|percent|k|m|bn|%)?(?!\d)",
    _re.IGNORECASE,
)

# Multiplier table for absolute-unit suffixes (case-insensitive).
# Percent/percent are intentionally ABSENT here — they form the "percent" unit type.
_ABSOLUTE_MULTIPLIERS: dict[str, int] = {
    "k": 1_000,
    "m": 1_000_000,
    "million": 1_000_000,
    "bn": 1_000_000_000,
    "billion": 1_000_000_000,
}

# Suffixes that mark the "percent" unit type.
_PERCENT_SUFFIXES: frozenset[str] = frozenset({"%", "percent"})

# --- Numeric CONTEXT extraction: quantity + rate (AA-MOAT-001, round 2) ------
# A numeric mention carries a DIMENSIONAL UNIT beyond its magnitude:
#   "128000 operations per second" -> quantity "operation", rate "second".
# Round 1 (2026-07-12) compared only the rate, and only in `per <word>` /
# `/<word>` form within two words of the number. Round 2 (2026-07-14) found
# nine evasions of that narrow reading (each/every/a/one <unit>, hyphenated
# per-minute, adverbial hourly, qualifier before the number or further from it,
# and a Cyrillic homoglyph in "per"). This extractor is the completion of the
# ruled fix: "compare value AND dimensional unit; fail-closed on any
# unit/quantity mismatch."

# Homoglyph fold for the numeric-context window. NFKC does NOT map Cyrillic
# 'р' (U+0440) to Latin 'p', so "рer minute" evaded the rate reader entirely
# and collapsed to "no rate asserted" — a bare number that matched the
# per-second source. Applying the global homoglyph rule at THIS gate's
# boundary (scoped: the numeric window only, so tokenization elsewhere and
# therefore the calibration corpus are untouched).
_CONFUSABLES: dict[int, str] = str.maketrans({
    "а": "a", "е": "e", "о": "o", "р": "p", "с": "c",
    "х": "x", "у": "y", "і": "i", "ј": "j", "һ": "h",
    "ο": "o", "α": "a", "ρ": "p", "υ": "u", "ɡ": "g",
})

# Rate triggers AFTER the number: "per second", "per-second", "/sec",
# "each minute", "every minute", "a minute", "one minute". Up to three
# intervening words (the quantity phrase, e.g. "write operations for the
# cluster") may sit between the number and the trigger.
_RATE_AFTER_RE = _re.compile(
    r"^(?:\s+[a-z-]+){0,6}?"
    r"(?:\s*(?P<strong>/)\s*|\s+(?P<strong2>per)[\s-]+"
    r"|\s+(?P<weak>each|every|a|one)\s+)"
    r"([a-z]+)",
    _re.IGNORECASE,
)

# Adverbial rate AFTER the number: "128000 operations hourly".
_RATE_ADVERB_RE = _re.compile(
    r"^(?:\s+[a-z-]+){0,4}?\s+(hourly|daily|weekly|monthly|yearly|annually|"
    r"secondly)\b",
    _re.IGNORECASE,
)

# Rate stated BEFORE the number: "at a per-minute rate of 128000",
# "the hourly figure of 128000". Searched in the tail of the preceding text.
_RATE_BEFORE_RE = _re.compile(
    r"(?:per[\s-]+([a-z]+)|(hourly|daily|weekly|monthly|yearly|annually))"
    r"(?:[\s-]+[a-z]+){0,3}\s*$",
    _re.IGNORECASE,
)

_ADVERB_TO_UNIT: dict[str, str] = {
    "secondly": "second", "hourly": "hour", "daily": "day", "weekly": "week",
    "monthly": "month", "yearly": "year", "annually": "year",
}

# Canonical names for common time denominators; an unknown qualifier word is
# kept as its casefolded, singularized self (still deterministically compared).
_RATE_UNIT_CANON: dict[str, str] = {
    "s": "second", "sec": "second", "secs": "second",
    "second": "second", "seconds": "second",
    "min": "minute", "mins": "minute", "minute": "minute", "minutes": "minute",
    "h": "hour", "hr": "hour", "hrs": "hour", "hour": "hour", "hours": "hour",
    "day": "day", "days": "day",
    "week": "week", "weeks": "week",
    "month": "month", "months": "month",
    "year": "year", "years": "year", "annum": "year",
    "ms": "millisecond", "millisecond": "millisecond",
    "milliseconds": "millisecond",
}

# Words that follow a rate trigger without naming a denominator — "per the
# report" is attribution, not a rate. A capture here means NO qualifier.
_RATE_NON_UNITS: frozenset[str] = frozenset({
    "the", "a", "an", "this", "that", "these", "those", "our", "their",
    "its", "his", "her", "your", "my", "of", "in", "on", "at", "and", "or",
})

# Quantity-noun abbreviations folded to a common form so that a legitimate
# paraphrase ("128000 ops/sec" vs "128000 operations per second") still
# grounds — Error-A control on the quantity comparison.
_QUANTITY_CANON: dict[str, str] = {
    "op": "operation", "ops": "operation", "operation": "operation",
    "operations": "operation",
    "req": "request", "reqs": "request", "request": "request",
    "requests": "request",
    "txn": "transaction", "txns": "transaction",
    "transaction": "transaction", "transactions": "transaction",
    "qry": "query", "queries": "query", "query": "query",
    "msg": "message", "msgs": "message",
    "message": "message", "messages": "message",
}

# Modifier words that may sit between the number and its quantity noun
# ("128000 write operations", "11000 sustained write ops").
_QUANTITY_SKIP: frozenset[str] = frozenset({
    "approximately", "about", "around", "roughly", "nearly", "almost",
    "over", "under", "up", "to", "more", "than", "least", "most", "some",
    "total", "of", "the", "a", "an", "its", "our", "their",
    "read", "write", "reads", "writes", "sustained", "peak", "average",
    "mean", "median", "raw", "net", "gross", "full", "additional", "extra",
})

# A numeric-context window never crosses a clause/sentence boundary.
_RATE_WINDOW_STOP_RE = _re.compile(r"[.,;:!?\n]")


def _fold(text: str) -> str:
    """NFKC-normalize, fold homoglyphs, casefold. Used only inside the
    numeric-context window (see _CONFUSABLES). Pure function."""
    return _nfkc(text).translate(_CONFUSABLES).casefold()


def _canon_rate(word: str) -> str | None:
    """Canonicalize a rate-denominator word, or None when it names no unit."""
    w = word.casefold()
    if w in _RATE_NON_UNITS:
        return None
    return _RATE_UNIT_CANON.get(w, w)


def _canon_quantity(word: str) -> str:
    """Canonicalize a quantity noun (abbreviation fold, then naive
    singularization). Pure function."""
    w = word.casefold()
    if w in _QUANTITY_CANON:
        return _QUANTITY_CANON[w]
    if len(w) > 3 and w.endswith("s") and not w.endswith("ss"):
        w = w[:-1]
    return w


def _numeric_context(before_text: str, after_text: str) -> tuple[str | None, str | None]:
    """Return (quantity, rate) for a numeric mention sitting between
    *before_text* and *after_text*.

    quantity — the canonicalized measured noun ("operation", "gigabyte"), or
               None when the number names no quantity.
    rate     — the canonicalized rate denominator ("second", "minute"), or
               None when the mention asserts no rate.

    Both windows are homoglyph-folded and cut at the nearest clause boundary,
    so context is never read across a comma or sentence end. The rate is looked
    for after the number first, then (adverbially) after, then before it.

    Pure function — no mutation, no LLM/network/random/wall-clock.
    """
    # A leading space is prepended because the numeric regexes' optional `\s?`
    # may have consumed the boundary space into the numeric match itself.
    after = " " + _fold(after_text)
    stop = _RATE_WINDOW_STOP_RE.search(after)
    after_window = after[: stop.start()] if stop else after

    before = _fold(before_text)
    before_parts = _RATE_WINDOW_STOP_RE.split(before)
    before_window = before_parts[-1] if before_parts else before

    # --- rate ---
    rate: str | None = None
    m = _RATE_AFTER_RE.match(after_window)
    if m:
        word = m.group(m.lastindex)
        # A STRONG trigger ("per", "/") names a rate whatever follows, so an
        # exotic denominator ("per fortnight") is still compared. A WEAK
        # trigger ("a", "each", "one") is only a rate when it names a KNOWN
        # time unit — otherwise "$4M in a filing" would read as a rate
        # (Error-A). Fail-open here is safe: an unread weak rate leaves the
        # claim compared by value+unit, exactly as before this fix.
        is_strong = bool(m.group("strong") or m.group("strong2"))
        if is_strong or word.casefold() in _RATE_UNIT_CANON:
            rate = _canon_rate(word)
    if rate is None:
        m = _RATE_ADVERB_RE.match(after_window)
        if m:
            rate = _ADVERB_TO_UNIT[m.group(1).casefold()]
    if rate is None:
        m = _RATE_BEFORE_RE.search(before_window)
        if m:
            if m.group(1):
                rate = _canon_rate(m.group(1))
            elif m.group(2):
                rate = _ADVERB_TO_UNIT[m.group(2).casefold()]

    # --- quantity: the measured noun after the number, before any rate
    # trigger. "128000 write operations per second" -> "operation".
    #
    # Only a QUANTITY-SHAPED token counts: a plural noun ("operations",
    # "gigabytes", "users") or a known abbreviation ("ops", "req"). Anything
    # else is skipped rather than guessed — reading the first bare word as the
    # quantity made "$4M last year" assert a quantity of "last" and broke
    # legitimate grounding (Error-A). An unread quantity imposes no
    # constraint, so this fail-open is safe: it can only preserve prior
    # behavior, never create a new PASS.
    quantity: str | None = None
    for raw in after_window.split():
        tok = raw.strip("-/").strip()
        if not tok or not tok.isalpha():
            continue
        if tok in {"per", "each", "every", "one"} or tok in _ADVERB_TO_UNIT:
            break
        if tok in _QUANTITY_SKIP:
            continue
        is_plural = len(tok) > 3 and tok.endswith("s") and not tok.endswith("ss")
        if is_plural or tok in _QUANTITY_CANON:
            quantity = _canon_quantity(tok)
        break

    return quantity, rate


def _parse_numeric_token(token: str) -> tuple[float, str] | None:
    """Parse a numeric token string into a canonical (value, unit) pair.

    unit is one of:
      "percent"  — token ends with '%' or the word 'percent'
      "absolute" — all other parseable tokens (plain integers, $, k/m/M/million/bn/billion)

    Handles:
      - Currency prefix: $4M → (4_000_000, "absolute")
      - Comma-separated digits: $4,000,000 → (4_000_000, "absolute")
      - Magnitude suffixes: k / m / M / million / bn / billion → scale × "absolute"
      - Percent suffixes: % / percent → (base, "percent")  [no scaling]
      - Plain integers and decimals: 4000000 → (4000000.0, "absolute")

    Returns None when parsing fails (fail-closed for exotic units).
    Pure function — no mutation, no I/O.
    """
    raw = _nfkc(token).strip()
    # Strip currency prefix
    raw = raw.lstrip("$")
    # Remove commas (thousands separators)
    raw = raw.replace(",", "")
    # Extract trailing suffix (letters/%) and numeric body
    match = _re.match(r"^([\d.]+)\s*([a-zA-Z%]*)$", raw.strip())
    if not match:
        return None
    num_str, suffix = match.group(1), match.group(2).lower()
    try:
        base = float(num_str)
    except ValueError:
        return None
    if suffix == "":
        return (base, "absolute")
    if suffix in _PERCENT_SUFFIXES:
        return (base, "percent")
    multiplier = _ABSOLUTE_MULTIPLIERS.get(suffix)
    if multiplier is None:
        # Exotic unit — fail-closed
        return None
    return (base * multiplier, "absolute")


def _extract_numeric_mentions(
    text: str,
) -> list[tuple[float, str, str | None, str | None]]:
    """Return all parseable (value, unit, rate, quantity) tuples in *text*.

    NFKC-normalizes before scanning; the dimensional context (measured quantity
    + rate denominator) is read from the windows around each numeric mention:
    "128000 operations per second" → (128000.0, "absolute", "second",
    "operation"). `rate`/`quantity` are None when the mention asserts none.
    May contain duplicates. Pure function.
    """
    normalized = _nfkc(text)
    out: list[tuple[float, str, str | None, str | None]] = []
    for m in _SOURCE_NUMERIC_RE.finditer(normalized):
        result = _parse_numeric_token(m.group(0))
        if result is not None:
            value, unit = result
            quantity, rate = _numeric_context(
                normalized[: m.start()], normalized[m.end():]
            )
            out.append((value, unit, rate, quantity))
    return out


def numeric_ok(claim: Claim, sources: list[RetrievedSource]) -> bool:
    """Return True iff every numeric_token in the claim matches a (value, unit)
    pair present in at least one source, after unit normalization.

    Matching rules:
    - NFKC-normalize all text before any comparison.
    - Parse claim token and source numeric expressions into canonical (value, unit) pairs.
    - Two tokens match iff BOTH value AND unit are equal.
    - "percent" and "absolute" are distinct unit types:
        25% ≠ bare 25  (percent vs absolute — CRITICAL: prevents false grounding)
        25% == 25%     (same unit)
        25% == 25 percent (both map to unit="percent")
    - Order-of-magnitude mismatches are always False (e.g. $4M ≠ $4,000).
    - Unit normalization: $4M ≡ $4,000,000 ≡ 4 million USD ≡ 4000000 (all "absolute").
    - Only k / m / M / million / bn / billion suffixes normalized within "absolute".
    - Exotic units → fail-closed (parse returns None → no match).
    - Dimensional unit (AA-MOAT-001, completed round 2): a numeric mention
      carries a measured QUANTITY ("operations", "gigabytes") and a RATE
      denominator ("per second") beyond its magnitude. Whenever the CLAIM
      states one of these, the matching source mention must carry the SAME
      canonical value — a differently-qualified or differently-measured source
      occurrence does not match (fail-closed). Surface form is irrelevant:
      "each minute", "per-minute", "a minute", "hourly", a qualifier before
      the number, and homoglyph spellings ("рer") all read as the rate they
      assert. When the claim states no rate/quantity, matching is by
      value+unit as before (a bare claim number asserts no dimension).
    - If claim.numeric_tokens is empty, returns True (vacuously grounded).
    - If sources is empty and numeric_tokens non-empty, returns False.

    Pure function — no LLM, no network, no random, no wall-clock.
    """
    if not claim.numeric_tokens:
        return True

    if not sources:
        return False

    # Pre-compute all source (value, unit, rate, quantity) mentions once.
    source_mentions: list[tuple[float, str, str | None, str | None]] = []
    for source in sources:
        source_mentions.extend(_extract_numeric_mentions(source.text))

    # Read each claim token's dimensional context from the claim text. Tokens
    # are consumed left-to-right so a repeated value takes successive
    # occurrences. A token not locatable in the text (e.g. a hand-built Claim)
    # carries no context — status-quo semantics, never a new false PASS.
    claim_text_normalized = _CITATION_RE.sub("", _nfkc(claim.text))
    search_from = 0
    for token in claim.numeric_tokens:
        claim_pair = _parse_numeric_token(token)
        if claim_pair is None:
            # Cannot parse claim token — fail-closed.
            return False
        claim_val, claim_unit = claim_pair

        claim_rate: str | None = None
        claim_quantity: str | None = None
        pos = claim_text_normalized.find(token, search_from)
        if pos == -1:
            pos = claim_text_normalized.find(token)
        if pos != -1:
            token_end = pos + len(token)
            claim_quantity, claim_rate = _numeric_context(
                claim_text_normalized[:pos], claim_text_normalized[token_end:]
            )
            search_from = token_end

        matched = False
        for s_val, s_unit, s_rate, s_quantity in source_mentions:
            if claim_val != s_val or claim_unit != s_unit:
                continue
            # An asserted rate/quantity must be matched by the source mention;
            # an unasserted one imposes no constraint.
            if claim_rate is not None and claim_rate != s_rate:
                continue
            if claim_quantity is not None and claim_quantity != s_quantity:
                continue
            matched = True
            break
        if not matched:
            return False

    return True


# ---------------------------------------------------------------------------
# ---------------------------------------------------------------------------
# Absence check — verdict against query log
# ---------------------------------------------------------------------------

# Tokens to strip before head-noun extraction.
_ABSENCE_LEAD: tuple[str, ...] = (
    "there is no ", "there are no ", "we found no ", "no ", "not ",
    "does not exist ", "does not ",
)

# Stop words for head-noun extraction: determiners, prepositions, articles.
_HEAD_NOUN_STOPS: frozenset[str] = frozenset({
    "a", "an", "the", "any", "some", "this", "that", "these", "those",
    "in", "on", "at", "to", "for", "of", "with", "by", "from", "as",
    "is", "are", "was", "were", "be", "been", "being", "have", "has",
    "had", "do", "does", "did", "will", "would", "could", "should",
    "may", "might", "must", "shall", "not", "no", "nor", "and", "or",
    "but", "so", "if", "then", "than", "about", "more", "also", "it",
    "its", "we", "you", "he", "she", "they", "there",
})


# Absence trigger phrases as one regex (longest alternative first so
# "there is no " wins over the embedded "no " at the same position).
_ABSENCE_LEAD_RE = _re.compile(
    "|".join(_re.escape(lead) for lead in sorted(_ABSENCE_LEAD, key=len, reverse=True)),
    _re.IGNORECASE,
)

_ANCHOR_PUNCT = ".,;:!?\"'()[]{}"


def _extract_absence_anchors(
    text: str,
) -> tuple[frozenset[str], str, frozenset[str]]:
    """Extract (strong_anchors, head_noun, subject_content) for the absence
    subject of *text*.

    *text* must already be NFKC-normalized and keep its ORIGINAL case —
    capitalization is the entity signal (AA-MOAT-004 fix).

    strong_anchors:  casefolded discriminating tokens of the negated subject —
                     named entities (capitalized after the trigger) and numeric
                     tokens (any token containing a digit), stop words excluded.
    head_noun:       the first non-stop content word (casefolded).
    subject_content: ALL non-stop content words of the negated subject. Round 2
                     (2026-07-14) showed head-noun-only anchoring still leaks:
                     "no benchmark for the streaming ingest workload" was
                     ABSENCE_SUPPORTED by two queries that merely said
                     "benchmark" and never touched a streaming ingest workload.
                     Coverage of the subject's content is what makes an
                     entity-free absence discriminating.

    Pure function.
    """
    match = _ABSENCE_LEAD_RE.search(text)
    remainder = text[match.end():] if match else text

    strong: set[str] = set()
    content: set[str] = set()
    head_noun = ""
    for raw_tok in remainder.split():
        tok = raw_tok.strip(_ANCHOR_PUNCT)
        if not tok:
            continue
        tok_cf = tok.casefold()
        if tok_cf in _HEAD_NOUN_STOPS:
            continue
        if not head_noun:
            head_noun = tok_cf
        content.add(tok_cf)
        if tok[0].isupper() or any(ch.isdigit() for ch in tok):
            strong.add(tok_cf)

    return frozenset(strong), head_noun, frozenset(content)


# A SPECIFIC entity-free subject (>= this many content words) demands more of a
# query than its head noun: the query must also carry at least one other content
# word of the subject. "No benchmark for the streaming ingest workload" is not
# evidenced by a session that only searched "benchmark"; "no changelog
# available" (a 2-word subject) still is, by "changelog release notes".
#
# Fractional coverage was tried first and rejected: it counts adjectives the
# subject carries but no query ever would ("no antidote APPROVED for the toxin
# in CURRENT guidelines"), which flipped a labeled-grounded corpus case to a
# false alarm (q37). Requiring one corroborating content word — rather than a
# fraction of all of them — is what distinguishes "the session searched for
# this" from "the session used this word".
_ABSENCE_SPECIFIC_SUBJECT_MIN: int = 3


def _stem(word: str) -> str:
    """Naive plural stem, used only for absence-subject matching so a claim's
    'guidelines' matches a query's 'guideline'. Substring matching already
    handles the reverse. Pure function."""
    if len(word) > 3 and word.endswith("s") and not word.endswith("ss"):
        return word[:-1]
    return word


def check_absence(
    claim: Claim,
    queries: list[str],
    min_absence_searches: int = 2,
) -> Verdict:
    """Return ABSENCE_SUPPORTED or UNVERIFIED_ABSENCE for an absence claim.

    Anchoring (AA-MOAT-004 fix — discriminating tokens, not the bare head noun):

    - **Strong anchors present** (named entities / numerics in the negated
      subject): a query supports the absence ONLY IF it mentions EVERY strong
      anchor AND the subject's head noun. "We found no benchmark comparing
      MongoDB against Redis" is supported only by queries that went looking
      for a MongoDB-and-Redis *benchmark* — not by any two queries that
      happen to contain "benchmark", and not by queries that merely mention
      the entities while searching something else ("X200 pricing" cannot
      support "no mention of battery defects in the X200 manual"; the
      head-noun requirement is what blocks the generic-entity collision).
    - **No strong anchors** (entity-free subject): fall back to the head noun,
      but ONLY IF it is discriminating — a head noun present in a strict
      majority (>50%) of the session's distinct queries is a blanket corpus
      word and cannot evidence a targeted absence search (fail-closed:
      UNVERIFIED_ABSENCE).

    ABSENCE_SUPPORTED iff at least `min_absence_searches` DISTINCT non-empty
    queries (NFKC + casefold) support the absence under the applicable rule.

    The `queries` list is the session's distinct search/fetch queries
    (query_provenance values from the EvidenceStore). Matching is
    case-insensitive, NFKC-normalized, substring-based.

    Pure function — no LLM, no network, no random, no wall-clock.
    """
    strong, head_noun, subject_content = _extract_absence_anchors(_nfkc(claim.text))

    # Distinct, non-empty, normalized queries.
    seen: set[str] = set()
    distinct: list[str] = []
    for q in queries:
        q_norm = _nfkc(q).casefold().strip()
        if q_norm and q_norm not in seen:
            seen.add(q_norm)
            distinct.append(q_norm)

    if strong:
        match_count = sum(
            1
            for q in distinct
            if head_noun in q and all(a in q for a in strong)
        )
    else:
        if not head_noun or not subject_content:
            return Verdict.UNVERIFIED_ABSENCE
        # Entity-free subject: a query counts only if it carries the head noun
        # AND — when the subject is specific — at least one OTHER of its
        # content words. Head-noun-only matching let a session that merely
        # searched "benchmark" support "no benchmark for the streaming ingest
        # workload" (round 2, 2026-07-14).
        head_stem = _stem(head_noun)
        others = {_stem(w) for w in subject_content if w != head_noun}
        specific = len(subject_content) >= _ABSENCE_SPECIFIC_SUBJECT_MIN
        containing = [
            q
            for q in distinct
            if head_stem in q
            and (not specific or any(w in q for w in others))
        ]
        # A head noun present in a strict majority of a >=3-query session is a
        # blanket corpus word and evidences no targeted search.
        if len(distinct) >= 3 and 2 * len([q for q in distinct if head_noun in q]) > len(distinct):
            return Verdict.UNVERIFIED_ABSENCE
        match_count = len(containing)

    if match_count >= min_absence_searches:
        return Verdict.ABSENCE_SUPPORTED
    return Verdict.UNVERIFIED_ABSENCE


# ---------------------------------------------------------------------------
# Citation resolution
# ---------------------------------------------------------------------------

def resolve(citation: str, store: dict[str, RetrievedSource]) -> RetrievedSource | None:
    """Resolve a citation marker (e.g. '[S1]' or 'S1') to a RetrievedSource.

    Returns None when the key is absent from store.
    Does not mutate store or citation.
    """
    normalized = _nfkc(citation).strip()
    if normalized.startswith("[") and normalized.endswith("]"):
        key = normalized[1:-1]
    else:
        key = normalized
    return store.get(key)


# ---------------------------------------------------------------------------
# Relational grounding helpers
# ---------------------------------------------------------------------------

def extract_arguments(text: str) -> tuple[str, str] | None:
    """Extract (side_A, side_B) head-noun phrases flanking the relational trigger.

    Strategy:
    1. NFKC-normalize input.
    2. Strip citation markers.
    3. Find the first relational trigger (longest-match-first).
    4. side_A = last contiguous non-stop-word token before the trigger.
       side_B = first contiguous non-stop-word token after the trigger.
    5. Return None when either side cannot be isolated (fail-closed).

    Returns a (side_A, side_B) pair of casefolded strings, or None.
    Pure function — no LLM, no network, no random, no wall-clock.
    """
    normalized = _nfkc(text)
    stripped = _CITATION_RE.sub("", normalized)

    lower = stripped.lower()

    # Find trigger (longest match first — _RELATIONAL_TRIGGERS is already ordered).
    trigger_start: int = -1
    trigger_end: int = -1
    for trigger in _RELATIONAL_TRIGGERS:
        idx = lower.find(trigger)
        if idx != -1:
            trigger_start = idx
            trigger_end = idx + len(trigger)
            break

    if trigger_start == -1:
        # No relational trigger found — cannot extract arguments.
        return None

    before_text = stripped[:trigger_start].strip()
    after_text = stripped[trigger_end:].strip()

    # --- Extract side_A: last content word(s) before trigger ---
    # Tokenize on whitespace; strip punctuation; filter stop words; take last token.
    _stop = _HEAD_NOUN_STOPS  # reuse absence-check stop-word set

    def _last_content_token(segment: str) -> str:
        """Return the last non-stop-word token from segment (casefolded)."""
        tokens = segment.split()
        for raw in reversed(tokens):
            tok = raw.strip(".,;:!?\"'()[]{}")
            if tok and tok.casefold() not in _stop:
                return tok.casefold()
        return ""

    def _first_content_token(segment: str) -> str:
        """Return the head content token for side_B (casefolded).

        Strategy: collect all non-stop-word tokens; skip bare-numeric tokens
        (tokens whose stripped form is entirely digits, e.g. '2' in 'type 2
        diabetes'); return the last surviving token.  The last position is used
        because English noun-phrase heads sit rightmost: 'type 2 diabetes' →
        'diabetes', 'elevated cortisol' → 'cortisol'.

        If filtering leaves no tokens, fall back to the first non-stop-word
        token regardless of numeric status (fail-closed: return something rather
        than empty, letting the downstream window_supports decide).
        """
        tokens = segment.split()
        content_tokens: list[str] = []
        fallback: str = ""
        for raw in tokens:
            tok = raw.strip(".,;:!?\"'()[]{}")
            if tok and tok.casefold() not in _stop:
                if not fallback:
                    fallback = tok.casefold()
                # Skip bare-numeric tokens (pure digit strings, e.g. '2', '10').
                if tok.isdigit():
                    continue
                content_tokens.append(tok.casefold())
        if content_tokens:
            return content_tokens[-1]
        return fallback

    side_a = _last_content_token(before_text)
    side_b = _first_content_token(after_text)

    if not side_a or not side_b:
        return None

    return (side_a, side_b)


def window_supports(source: RetrievedSource, argument_text: str) -> bool:
    """Return True iff *argument_text* appears (as content words) in any T2 window
    of *source*.

    Uses the T1 verbatim path for short arguments (exact token inclusion) or the
    T2 window scoring machinery for longer phrases. For a single-token argument,
    NFKC-casefold substring match against each ±2-sentence window suffices.

    Pure function — no mutation, no LLM/network/random/wall-clock.
    """
    arg_normalized = _nfkc(argument_text).casefold().strip()
    if not arg_normalized:
        return False

    sentences = _split_sentences(source.text)
    if not sentences:
        # Single-block source — check the whole text.
        return arg_normalized in _nfkc(source.text).casefold()

    n = len(sentences)
    for c in range(n):
        lo = max(0, c - 2)
        hi = min(n, c + 3)
        window_text = _nfkc(" ".join(sentences[lo:hi])).casefold()
        if arg_normalized in window_text:
            return True

    return False


# ---------------------------------------------------------------------------
# Relational grounding
# ---------------------------------------------------------------------------

def ground_relational(claim: Claim, store: dict[str, RetrievedSource]) -> Verdict:
    """Return GROUNDED or UNVERIFIED_RELATION for a RELATIONAL claim.

    Spec §4.8 — two-distinct-source rule:
    1. Resolve claim.citations → distinct sources; keep only full_text_source=="verbatim".
       If fewer than 2 distinct verbatim sources → UNVERIFIED_RELATION.
    2. extract_arguments(claim.text) → (side_A, side_B).
       If extraction fails → UNVERIFIED_RELATION (fail-closed).
    3. side_A supported in at least one verbatim source AND
       side_B supported in at least one DIFFERENT verbatim source → GROUNDED.
    4. Otherwise → UNVERIFIED_RELATION.

    NFKC normalization is applied inside extract_arguments and window_supports.
    Pure function — no mutation, no LLM/network/random/wall-clock.
    """
    # Step 1: resolve and filter to distinct verbatim sources.
    verbatim_sources: dict[str, RetrievedSource] = {}
    for citation in claim.citations:
        source = resolve(citation, store)
        if source is None:
            continue
        if source.full_text_source != "verbatim":
            continue
        # Deduplicate by source_id (NFKC-normalized in load_store; use as-is).
        if source.source_id not in verbatim_sources:
            verbatim_sources[source.source_id] = source

    if len(verbatim_sources) < 2:
        return Verdict.UNVERIFIED_RELATION

    # Step 2: extract arguments.
    args = extract_arguments(claim.text)
    if args is None:
        return Verdict.UNVERIFIED_RELATION

    side_a, side_b = args

    # Step 3: side_A in some source S_a; side_B in a DIFFERENT source S_b.
    sources_list = list(verbatim_sources.values())

    # Collect all source IDs where side_A is supported.
    a_supported_in: set[str] = {
        s.source_id for s in sources_list if window_supports(s, side_a)
    }
    # Collect all source IDs where side_B is supported.
    b_supported_in: set[str] = {
        s.source_id for s in sources_list if window_supports(s, side_b)
    }

    # There must exist at least one (s_a, s_b) pair where s_a != s_b.
    for s_a_id in a_supported_in:
        for s_b_id in b_supported_in:
            if s_a_id != s_b_id:
                return Verdict.GROUNDED

    return Verdict.UNVERIFIED_RELATION


# ---------------------------------------------------------------------------
# Per-claim verdict dispatcher (spec §4.4)
# ---------------------------------------------------------------------------

def _session_queries(store: dict[str, RetrievedSource]) -> list[str]:
    """Return the DISTINCT query_provenance values across the store.

    Order-insensitive content (the caller — check_absence — counts distinct
    matches). A list is returned to satisfy check_absence's signature.
    Pure function — no mutation, no LLM/network/random/wall-clock.
    """
    seen: set[str] = set()
    out: list[str] = []
    for source in store.values():
        q = source.query_provenance
        if q not in seen:
            seen.add(q)
            out.append(q)
    return out


def ground(claim: Claim, store: dict[str, RetrievedSource]) -> Verdict:
    """Return the grounding Verdict for a single ALREADY-CLASSIFIED claim.

    Implements spec §4.4 decision logic in exact order. The input `claim` is
    assumed to carry a resolved `kind`, `citations`, and `numeric_tokens`
    (i.e. it has passed through classify()).

    Branch order (first match wins):
      1. NON_CLAIM                     → GROUNDED (excluded from denominator
                                         upstream in Task 9).
      2. RELATIONAL                    → delegate to ground_relational.
      3. ABSENCE                       → delegate to check_absence with the
                                         session's distinct queries.
      4. no citations                  → UNCITED.
      5. any citation unresolved       → UNVERIFIED_CITATION.
      6. any resolved source has falsy text → UNGROUNDABLE (snippet-only / no
                                         full text).
      7. no verbatim source among cited → UNGROUNDABLE (all haiku_summary).
      8. NUMERIC and numeric_ok(verbatim) is False → UNVERIFIED_NUMBER.
      9. T1 or T2 supports on verbatim → GROUNDED.
     10. otherwise                     → UNGROUNDED.

    ATTRIBUTION and FACTUAL fall through to the citation/verbatim/tier path
    (the default). Tiers (t1_verbatim, t2_lexical) and numeric_ok run ONLY on
    the verbatim-filtered sources.

    Pure function — no mutation, no LLM/network/random/wall-clock.
    """
    if claim.kind == ClaimKind.NON_CLAIM:
        return Verdict.GROUNDED
    if claim.kind == ClaimKind.RELATIONAL:
        return ground_relational(claim, store)
    if claim.kind == ClaimKind.ABSENCE:
        return check_absence(claim, _session_queries(store))

    if not claim.citations:
        return Verdict.UNCITED

    sources = [resolve(c, store) for c in claim.citations]
    if any(s is None for s in sources):
        return Verdict.UNVERIFIED_CITATION
    if any(not s.text for s in sources):
        return Verdict.UNGROUNDABLE

    verbatim = [s for s in sources if s.full_text_source == "verbatim"]
    if not verbatim:
        return Verdict.UNGROUNDABLE

    if claim.kind == ClaimKind.NUMERIC and not numeric_ok(claim, verbatim):
        return Verdict.UNVERIFIED_NUMBER

    if t1_verbatim(claim, verbatim) or t2_lexical(claim, verbatim):
        return Verdict.GROUNDED

    return Verdict.UNGROUNDED


# ---------------------------------------------------------------------------
# Grounding SCORE + threshold + hard override (spec §4.5)
# ---------------------------------------------------------------------------

# Verdicts that count toward the numerator (a claim is "grounded enough").
_NUMERATOR_VERDICTS: frozenset[Verdict] = frozenset({
    Verdict.GROUNDED,
    Verdict.ABSENCE_SUPPORTED,
})

# Score floor below which the gate is always FAIL.
_FAIL_FLOOR: float = 60.0


def score_report(
    claims: list[Claim],
    store: dict[str, RetrievedSource],
    threshold: float = 90.0,
) -> dict:
    """Compute the grounding SCORE, gate, and retained-violation appendix (spec §4.5).

    Denominator S = claims whose kind != NON_CLAIM. EVERY scored verdict stays in
    S — violations (UNGROUNDED, UNCITED, UNVERIFIED_*, UNGROUNDABLE) are NEVER
    removed from the denominator. That non-removal is the anti-gaming invariant:
    a fabricated-citation draft cannot shrink its own denominator to post a passing
    score.

    Numerator = claims in S whose verdict is GROUNDED or ABSENCE_SUPPORTED.

    grounding_score = 100.0 * numerator / |S|, rounded to 1 decimal for reporting
    (so 2/3 → 66.7).

    Gate (ADR-005 semantics — empty-appendix hard-cap):
      FAIL       if score < 60.0
      NEEDS_WORK if score < threshold OR retained_appendix is non-empty
                 OR any claim's verdict == UNVERIFIED_CITATION
      PASS       otherwise
    PASS therefore means "every scored claim is grounded", not "at least
    threshold% are". The score threshold is retained as a secondary bar; it is
    no longer sufficient on its own — a single retained violation-class verdict
    caps the gate at NEEDS_WORK regardless of score (ADR-005, accepted
    2026-07-12; closes the threshold-dilution vector, AA-MOAT-002/-006). The
    pre-existing UNVERIFIED_CITATION hard override is kept as defense in depth
    (it is subsumed by the appendix cap for scored claims). Neither override
    ever lifts a FAIL upward (FAIL is checked first).

    Empty-denominator edge (|S| == 0, i.e. all NON_CLAIM / no scored claims):
    MOAT-SAFE defense in depth — a report with zero verifiable claims CANNOT be
    certified trustworthy, so the gate is NEEDS_WORK (never PASS). grounding_score
    is reported as 100.0 (there are no failed claims), but the GATE — the
    certification signal — is NEEDS_WORK and the report carries "vacuous": true so
    callers can distinguish "nothing to verify" from a genuine low score. The CLI
    exits non-zero for any non-PASS gate, so a vacuous report never exits 0.

    Returns:
        {
          "grounding_score": float,           # rounded to 1 decimal
          "gate": str,                         # "FAIL" | "NEEDS_WORK" | "PASS"
          "scored_claims": int,                # |S|
          "vacuous": bool,                     # True iff scored_claims == 0
          "per_claim": [                       # ALL claims, in input order
              {"index": int, "text": str, "kind": str, "verdict": str}, ...
          ],
          "retained_appendix": [               # non-grounded SCORED claims only
              {"index": int, "text": str, "verdict": str}, ...
          ],
        }

    Verdict and kind are reported as their string values (Verdict/ClaimKind are
    str-enums; .value yields the plain string).

    Pure function — no LLM, no network, no random, no wall-clock; does not mutate
    *claims* or *store*.
    """
    per_claim: list[dict] = []
    retained_appendix: list[dict] = []
    scored_count = 0
    numerator = 0
    has_unverified_citation = False

    for claim in claims:
        verdict = ground(claim, store)
        per_claim.append({
            "index": claim.index,
            "text": claim.text,
            "kind": claim.kind.value,
            "verdict": verdict.value,
        })

        if verdict == Verdict.UNVERIFIED_CITATION:
            has_unverified_citation = True

        # NON_CLAIM is excluded from the denominator (and thus from scoring and
        # the retained appendix), but still appears in per_claim for transparency.
        if claim.kind == ClaimKind.NON_CLAIM:
            continue

        scored_count += 1
        if verdict in _NUMERATOR_VERDICTS:
            numerator += 1
        else:
            retained_appendix.append({
                "index": claim.index,
                "text": claim.text,
                "verdict": verdict.value,
            })

    vacuous = scored_count == 0

    if vacuous:
        # No verifiable claims. Defense in depth: a zero-denominator report cannot
        # be certified — gate NEEDS_WORK (never PASS), independent of score.
        grounding_score = 100.0
        gate = "NEEDS_WORK"
    else:
        grounding_score = round(100.0 * numerator / scored_count, 1)
        if grounding_score < _FAIL_FLOOR:
            gate = "FAIL"
        elif (
            grounding_score < threshold
            or retained_appendix  # ADR-005: any retained violation blocks PASS
            or has_unverified_citation
        ):
            gate = "NEEDS_WORK"
        else:
            gate = "PASS"

    return {
        "grounding_score": grounding_score,
        "gate": gate,
        "scored_claims": scored_count,
        "vacuous": vacuous,
        "per_claim": per_claim,
        "retained_appendix": retained_appendix,
    }


# ---------------------------------------------------------------------------
# CLI entry point (Task 10)
# ---------------------------------------------------------------------------

def main() -> None:
    """CLI entry point for Agent-Assure ground_check.

    argparse interface:
      --draft PATH      Path to the draft text file (required).
      --store PATH      Path to the evidence JSONL store (required).
      --threshold FLOAT Grounding score threshold (default 90.0).
      --json            Print JSON report to stdout; skip writing YAML file.

    Exit codes:
      0  gate == "PASS"
      1  gate == "NEEDS_WORK" or "FAIL"
    """
    import argparse
    import sys as _sys
    import json as _json
    import yaml as _yaml

    parser = argparse.ArgumentParser(
        prog="ground_check",
        description="Agent-Assure: ground a draft against an evidence store.",
    )
    parser.add_argument("--draft", required=True, metavar="PATH",
                        help="Path to the draft text file.")
    parser.add_argument("--store", required=True, metavar="PATH",
                        help="Path to the evidence JSONL store.")
    parser.add_argument("--threshold", type=float, default=90.0, metavar="FLOAT",
                        help="Grounding score threshold (default 90.0).")
    parser.add_argument("--json", dest="json_mode", action="store_true",
                        help="Print JSON report to stdout; skip writing YAML file.")
    args = parser.parse_args()

    # Pipeline: read → decompose → classify → score_report
    with open(args.draft, encoding="utf-8") as fh:
        draft_text = fh.read()

    store = load_store(args.store)
    claims = [classify(c) for c in decompose(draft_text)]
    report = score_report(claims, store, threshold=args.threshold)

    gate: str = report["gate"]

    if args.json_mode:
        # Print JSON to stdout; sort_keys for determinism.
        print(_json.dumps(report, sort_keys=True))
    else:
        # Write grounding-report.yaml to CWD.
        with open("grounding-report.yaml", "w", encoding="utf-8") as fh:
            _yaml.safe_dump(report, fh, sort_keys=True, allow_unicode=True)
        # One-line human summary to stdout.
        print(f"gate={gate} grounding_score={report['grounding_score']}")

    _sys.exit(0 if gate == "PASS" else 1)


if __name__ == "__main__":
    main()
