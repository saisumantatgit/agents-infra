"""Agent-Assure: evidence-store models and loader.

No LLM, no network, no random, no wall-clock in logic.
All text inputs are NFKC-normalized before any match/regex gate.
Pure functions only — never mutate inputs or globals.
"""

from __future__ import annotations

import json
import unicodedata
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
