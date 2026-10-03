"""Agent-Assure: evidence-store models and loader.

No LLM, no network, no random, no wall-clock in logic.
All text inputs are NFKC-normalized before any match/regex gate.
Pure functions only — never mutate inputs or globals.
"""

from __future__ import annotations

from collections.abc import Iterable

import hashlib
import json
import os
# `re` is imported HERE, at the top, and not beside its first use. Three
# separate NameErrors in this file have had one cause: a module-level
# `_re.compile(...)` constant placed next to the function that needed it, above
# an `import re as _re` that sat 400 lines further down. Every one of them
# failed at import time rather than silently, which is the only reason they were
# cheap. Keeping the import at the top makes the class impossible rather than
# survivable.
import re as _re
import unicodedata
from pathlib import Path
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
    # J-38. DEFAULTS TO "" so every store written before 2026-10-01 keeps
    # loading (close-after-open: the demo and 47 corpus fixtures predate this).
    # The default is safe because an EMPTY session_id is treated as
    # UNATTRIBUTABLE by assert_single_session and therefore refuses under
    # enforcement — "I don't know" points away from PASS.
    session_id: str = ""


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


# Tool -> source-type contract. The gate keeps its OWN copy rather than
# importing the capture layer into the moat's call tree; the copy is made safe
# by test_tool_source_type_mapping_matches_capture_core, which fails loudly the
# day capture_core learns a tool this file does not know. (J-26, 2026-10-01)
_VERBATIM_TOOLS: frozenset[str] = frozenset({
    "mcp__exa__web_fetch_exa",
    "web_fetch_exa",
    "Read",
    "mcp__ddg-search__fetch_content",
})
_HAIKU_SUMMARY_TOOLS: frozenset[str] = frozenset({"WebFetch"})

# The full_text_source enum is CLOSED (CLAUDE.md, verdict taxonomy).
_SOURCE_TYPES: frozenset[str] = frozenset({"verbatim", "haiku_summary"})

# Required on every record, and each must be a str.
_REQUIRED_STR_FIELDS: tuple[str, ...] = (
    "source_id", "fetched_at", "tool", "content_sha256", "text",
    "full_text_source", "captured_via", "query_provenance",
)
# May be JSON null (Read has no url; a fetch has no file_path), but must be a
# str when present.
_OPTIONAL_STR_FIELDS: tuple[str, ...] = ("url", "file_path")


def _object_pairs_no_duplicates(
    pairs: list[tuple[str, object]],
) -> dict[str, object]:
    """json object hook that RAISES on a duplicated key. Pure.

    ``json.loads`` keeps the LAST of duplicated keys, so a single line could
    declare ``full_text_source`` twice — haiku_summary then verbatim — and load
    as verbatim. That makes a provenance decision by JSON key order (R9P2-03).
    """
    seen: set[str] = set()
    for key, _value in pairs:
        if key in seen:
            raise ValueError(
                f"duplicate JSON key {key!r} in one evidence record; the store "
                "is audit evidence and a record must not contradict itself"
            )
        seen.add(key)
    return dict(pairs)


def _validate_record(obj: dict[str, object], lineno: int) -> None:
    """Raise unless *obj* is a self-consistent, correctly-typed record. Pure.

    Checks, each closing a round-9 finding:
      - every required field present and a str;
      - url/file_path either null or a str;
      - full_text_source within the closed enum;
      - tool RECOGNISED, and its declared source type matching the capture
        contract (capture_core: native WebFetch is ALWAYS haiku_summary).

    An unrecognised tool RAISES rather than being trusted. The gate's rule is
    that every "I don't know" must point AWAY from PASS, and an unknown reader
    makes the record's own "verbatim" unverifiable — which is exactly the claim
    that must not be taken on trust.
    """
    for field in _REQUIRED_STR_FIELDS:
        if field not in obj:
            raise ValueError(
                f"line {lineno}: evidence record is missing required field "
                f"{field!r}"
            )
        if not isinstance(obj[field], str):
            raise TypeError(
                f"line {lineno}: field {field!r} must be a str, got "
                f"{type(obj[field]).__name__}"
            )
    for field in _OPTIONAL_STR_FIELDS:
        value = obj.get(field)
        if value is not None and not isinstance(value, str):
            raise TypeError(
                f"line {lineno}: field {field!r} must be a str or null, got "
                f"{type(value).__name__}"
            )

    source_type = obj["full_text_source"]
    if source_type not in _SOURCE_TYPES:
        raise ValueError(
            f"line {lineno}: full_text_source {source_type!r} is not one of "
            f"{sorted(_SOURCE_TYPES)}; the enum is closed"
        )

    tool = obj["tool"]
    if tool in _HAIKU_SUMMARY_TOOLS:
        expected = "haiku_summary"
    elif tool in _VERBATIM_TOOLS:
        expected = "verbatim"
    else:
        raise ValueError(
            f"line {lineno}: unrecognised tool {tool!r}. The gate cannot verify "
            f"the source type of a reader it does not know, and trusting the "
            f"record's own {source_type!r} would let an unknown capture path "
            f"certify claims. Add the tool to capture_core and to this file's "
            f"allowlist together."
        )
    if source_type != expected:
        raise ValueError(
            f"line {lineno}: tool {tool!r} always produces {expected!r} but the "
            f"record declares full_text_source={source_type!r}. A store that "
            f"contradicts the capture contract is not audit evidence."
        )


def assert_single_session(
    store: dict[str, RetrievedSource], session_id: str
) -> None:
    """Raise unless every record in *store* belongs to *session_id*. Pure.

    J-38. The founding spec promises a claim traces to a source "actually
    retrieved THIS SESSION". Before this, nothing in the code expressed a
    session at all: no record carried an id and the store was appended to
    forever, so a prior session's [S2] certified at PASS 100.0.

    IT RAISES; IT DOES NOT FILTER, and that is the whole design decision.

    Dropping foreign records looks safer and is not. The store reaches
    check_absence through two arguments at once and shrinking it moves them in
    OPPOSITE directions (proven 2026-10-01, D-54):

      - fewer cited sources    -> citations do not resolve   -> refuse  (closed)
      - fewer source_texts     -> fewer refutations found    -> CERTIFY (OPEN)
      - fewer distinct queries -> may drop below the 2-query bar -> refuse,
        but ALSO disables the blanket-corpus-word refusal -> CERTIFY   (OPEN)

    So a filtered store is not a weaker store, it is a DIFFERENTLY weak one.
    Refusing to produce a verdict is the only unambiguously fail-closed answer:
    a store holding another session's evidence is not this session's audit
    record, and the gate should say so rather than quietly score a subset.

    An EMPTY session_id is UNATTRIBUTABLE and also raises. A record that cannot
    be placed in this session cannot be certified against in it.

    R15-01 (2026-10-03), found by round 15 on the surface built to CLOSE this
    class. The paragraph above was TRUE AS A STATEMENT OF INTENT and FALSE AS A
    DESCRIPTION OF THE CODE: the comparison below is `source.session_id !=
    session_id`, so with a blank expected id and records that also carry a blank
    id it evaluates `"" != ""`, finds nothing foreign, and does not raise.
    `--session-id ""` therefore scored the shipped demo store at PASS 100.0
    **and printed the "retrieved this session" scope statement over records that
    carry no session information at all** — J-56's overclaim, reproduced by the
    J-73 disclosure meant to prevent it.

    The guard is now explicit and FIRST, because the emptiness of the expected
    id is a fact about the REQUEST, not about the store, and no amount of
    comparing it against records can establish it. Fail-closed: a run that
    previously produced a verdict now refuses.
    """
    if not session_id.strip():
        raise ValueError(
            "--session-id was given but is empty or whitespace. An empty "
            "session id is UNATTRIBUTABLE: it matches records that carry no "
            "session id at all, so enforcing it would assert session scope "
            "over evidence that has none. Pass a real session id, or omit "
            "--session-id to score without session enforcement (the report "
            "then says so explicitly)."
        )
    foreign = sorted(
        {source.session_id or "<no session_id>" for source in store.values()
         if source.session_id != session_id}
    )
    if foreign:
        raise ValueError(
            f"evidence store holds records from outside this session "
            f"{session_id!r}: {', '.join(foreign)}. The store is append-only and "
            f"is never rotated, so this is the expected state of a reused store. "
            f"Point --store at a fresh file for this session, or omit "
            f"--session-id to score without session enforcement."
        )


def load_store(path: str) -> dict[str, RetrievedSource]:
    """Read a JSONL file and return a dict indexed by NFKC-normalized source_id.

    Blank lines are skipped. Returns a new dict; does not mutate any input.

    RAISES rather than repairing (J-26, closes R9P2-01..04). Before this, the
    loader silently accepted four self-contradicting stores, and in each one a
    verdict was decided by something that is not evidence:

      - a duplicate source_id (last record wins, so LINE ORDER decided whether
        a claim citing [S1] was UNGROUNDABLE or GROUNDED);
      - two raw ids that NFKC folds onto one key (full-width vs ASCII);
      - a duplicated JSON key inside one record (KEY ORDER decided the source
        type);
      - tool/full_text_source disagreement, an out-of-enum source type, and
        mistyped or null fields, none of which were checked at all.

    CEILING: content_sha256 is required to be a str but is NOT recomputed
    against text, so a record whose text was edited after capture still loads.
    That would break the moment it is enforced, because 76 test fixtures across
    33 files carry placeholder digests. It is deliberately out of scope: the
    threat model here is the DRAFTING model's text, not an edited store, and an
    attacker who can rewrite the store can also rewrite the digest. Upgrade
    path: verify sha256(NFKC(text)) == content_sha256 — which holds by
    construction, since capture_core._sha256_nfkc hashes the NFKC form — and
    sweep the fixtures in the same commit. Tracked as J-32.
    """
    store: dict[str, RetrievedSource] = {}
    # α4 friction 1 (2026-10-02): the FIRST command the installer prints points
    # at .assure/evidence-store.jsonl, which does not exist on a fresh install
    # because no research has happened yet. A raw FileNotFoundError traceback was
    # the first thing a new user saw. Still an exception and still exit 1 — loud,
    # not silent — but now it says what to do.
    if not Path(path).exists():
        raise FileNotFoundError(
            f"no evidence store at {path!r}. The store is written by the "
            f"PostToolUse capture hook as your session retrieves sources, so it "
            f"does not exist until the hook has fired at least once. Either run "
            f"some research first with the plugin installed, or point --store at "
            f"an existing store (the shipped demo has one: "
            f"demo/evidence-store.jsonl)."
        )
    with open(path, encoding="utf-8") as fh:
        for lineno, raw_line in enumerate(fh, start=1):
            line = raw_line.strip()
            if not line:
                continue
            obj = json.loads(line, object_pairs_hook=_object_pairs_no_duplicates)
            _validate_record(obj, lineno)
            source_id = _nfkc(obj["source_id"])
            if source_id in store:
                raise ValueError(
                    f"line {lineno}: duplicate source_id {source_id!r} "
                    f"(NFKC-normalized). The earlier record would be silently "
                    f"replaced, making the verdict for a claim citing "
                    f"[{source_id}] depend on line order alone."
                )
            session_id = obj.get("session_id", "")
            if not isinstance(session_id, str):
                raise TypeError(
                    f"line {lineno}: field 'session_id' must be a str or absent, "
                    f"got {type(session_id).__name__}"
                )
            source = RetrievedSource(
                session_id=_nfkc(session_id),
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
            # Strip the separator's litter from *left* (OI-DEC-04). Splitting
            # "The written statement is in, and the case is contested" at
            # " and " leaves the left clause holding a comma it did not own:
            # "The written statement is in,". No verdict changes — punctuation
            # is stripped before tokenizing — but that trailing mark is what the
            # user sees in the report, and on real prose it made a COMPLETE
            # clause read as a sentence fragment. The gate should quote the
            # writer, not the splitter.
            left = left.rstrip(";,:—–- \t").strip()
            right = right.strip()
            return [_propagate_sentence_citation(left, right), right]
    return [sentence]


def _propagate_sentence_citation(left: str, right: str) -> str:
    """Return *left* with the sentence's trailing citation appended, if it has none.

    OI-DEC-01. A marker at the END of a compound sentence cites the SENTENCE,
    so the clause the splitter carved off the front is cited too. Without this
    the left clause reads UNCITED and — post-ADR-005 — blocks PASS, which
    penalises an author who cited correctly.

    This is the cohort's only PASS-ENABLING change (ratified by Sai 2026-09-02
    with a red-team gate: tests/test_citation_propagation.py). Note what it does
    and does not buy: it converts UNCITED into *run the normal tiers against
    the cited source*. The clause still has to ground. The PASS-enabling path is
    exactly as wide as the tiers are correct and no wider.

    Two things it must never do, both tested:

    * **Overwrite.** A clause carrying its OWN citation keeps it. Re-pointing a
      claim at a source the author did not cite for it is the fabrication the
      gate exists to catch, and doing it in the decomposer would be invisible.
    * **Invent.** Only a marker that is genuinely sentence-final propagates. A
      mid-sentence marker belongs to its own clause; treating it as
      sentence-scoped would attach a source to text the author placed it
      before. That case cannot arise here (a mid-sentence marker lands in
      *left*, which then has a citation and is skipped) and is pinned by test.

    Pure function — returns a new string, mutates nothing.
    """
    if _CITATION_RE.search(left):
        return left
    trailing = _TRAILING_CITATIONS_RE.search(right)
    if not trailing:
        return left
    return f"{left} {trailing.group(1)}"


def _propagate_across_semicolon(sentence: str, following: str) -> str:
    """Return *sentence* with *following*'s trailing citation, if it is a clause.

    OI-DEC-01, second path. syntok treats "; " as a SENTENCE boundary, so
    "Redis is fast; PostgreSQL is durable [S1]." never reaches
    _conjunction_split as one string — it arrives as two segments, and the
    first reads UNCITED. (This is why _conjunction_split's own "; " separator is
    effectively unreachable for that shape.)

    The discriminator is the author's own punctuation: a segment ending in ";"
    is NOT a terminated sentence, so the terminal citation of the sentence it
    runs into covers it. A segment ending in "." IS terminated, and propagating
    across a full stop would attach a source to a sentence the author never
    cited — the same "invent" failure _propagate_sentence_citation refuses. The
    trailing ";" is what separates the two cases, and it is set by the author
    for grammatical reasons, not to satisfy the gate.

    Only the IMMEDIATELY following segment is consulted, so a citation cannot
    travel back across an intervening terminated sentence.

    Pure function — returns a new string, mutates nothing.
    """
    body = sentence.rstrip()
    if not body.endswith(";") or _CITATION_RE.search(body):
        return sentence
    trailing = _TRAILING_CITATIONS_RE.search(following.strip())
    if not trailing:
        return sentence
    return f"{body.rstrip(';').rstrip()} {trailing.group(1)}"


def _strip_html_comments(text: str) -> str:
    """Remove well-formed HTML comments from *text* (OI-DEC-03).

    An authoring comment is not prose: it is not rendered, not published, and
    not read. Before this, a draft's own working notes decomposed into scored
    claims — "[Sn] anchors are working-draft verification tags (store:
    .assure/evidence-store.jsonl)" became a FACTUAL claim, and the bare "-->"
    became another. A gate that flags the writer's TODO notes as ungrounded is
    not measuring the document the reader gets.

    **Only WELL-FORMED pairs are removed, and that is the load-bearing choice.**
    An unterminated "<!--" is left in place, so the text after it stays scored.
    Stripping to end-of-document would mean one stray, possibly accidental,
    "<!--" silently deletes every claim below it from the denominator — a
    catastrophic-and-invisible failure, versus the mild and visible one of
    scoring a malformed comment. Unparseable input must not shrink the thing
    being checked.

    Pure function.
    """
    return _HTML_COMMENT_RE.sub(" ", text)


# OI-MOAT-29 (round 7). `<!--` appearing in VISIBLE prose — inside a backtick
# code span, where no renderer treats it as a comment — paired with a genuine
# comment's `-->` further down and swallowed every sentence between. The
# demonstrated draft lost "MongoDB lost all data under sustained write load."
# from the report entirely: never scored, so never flagged.
#
# D-17 restricted stripping to WELL-FORMED pairs, reasoning about an
# unterminated `<!--` running to end of file. It did not consider a stray opener
# finding a real closer downstream — which is well-formed by construction. The
# repair is renderer-faithfulness, the same principle D-24 rests on: a comment
# delimiter inside a code span is not a comment, so it must not be treated as
# one. Fail-closed — strictly less text is removed, so strictly more is scored.
_CODE_SPAN_RE = _re.compile(r"```.*?```|``.*?``|`[^`\n]*`", _re.DOTALL)


# J-27 (2026-10-01), closing R8B-01/02 and R9P2-05/06/07 as ONE class.
#
# OI-MOAT-29 protected comment delimiters inside BACKTICK code only. CommonMark
# has more ways to make `<!--` literal, and in each one a stray opener pairs
# with a real closer downstream and DELETES every paragraph between them from
# the scored denominator. Deleted prose is never scored, so it is never
# flagged: the gate reports PASS 100.0 over a page whose reader can plainly see
# fabrications.
#
# THE DIRECTION OF SAFETY IS COUNTER-INTUITIVE AND DECIDES THE WHOLE DESIGN.
# Stripping REMOVES text from the denominator, so stripping TOO MUCH is the
# FAIL-OPEN direction. Therefore this scanner may freely OVER-detect code
# (strip less, score more, fail closed) and must never UNDER-detect it. That
# is why it does not aim at CommonMark exactness and why no Markdown parser was
# added as a dependency: what is needed is a generous code-region detector, not
# a correct renderer, and third-party code in the moat's verdict path is a
# worse trade than a conservative 40-line scan.
#
# Rejected alternative, recorded because it is the obvious one: "a comment may
# not span a blank line". It is NOT sufficient — a tilde-fenced attack with no
# blank lines anywhere still hides visible prose. Verified before this was
# written, and pinned as test_tilde_fence_with_no_blank_lines.
_FENCE_RE = _re.compile(r"^(?P<indent> {0,3})(?P<fence>`{3,}|~{3,})(?P<info>.*)$")
_INDENTED_CODE_RE = _re.compile(r"^(?: {4,}|\t)")


def _code_line_spans(text: str) -> list[tuple[int, int]]:
    """Return (start, end) character spans of BLOCK-level code. Pure.

    Covers fenced blocks (backtick or tilde, any length >= 3, opener indented
    up to 3 spaces, with or without an info string) and indented code blocks
    (4+ spaces or a tab) outside any fence.

    Deliberately generous: an indented line is treated as code without checking
    CommonMark's "cannot interrupt a paragraph" rule. Over-detection strips
    less, which is the safe direction.
    """
    spans: list[tuple[int, int]] = []
    pos = 0
    fence_char: str | None = None
    fence_len = 0
    fence_start = 0
    for line in text.splitlines(keepends=True):
        stripped = line.rstrip("\r\n")
        m = _FENCE_RE.match(stripped)
        if fence_char is None:
            if m is not None:
                fence_char = m.group("fence")[0]
                fence_len = len(m.group("fence"))
                fence_start = pos
            elif _INDENTED_CODE_RE.match(stripped):
                spans.append((pos, pos + len(line)))
        else:
            # Inside a fence: a closer is the same char, at least as long, and
            # carries no info string.
            if (m is not None
                    and m.group("fence")[0] == fence_char
                    and len(m.group("fence")) >= fence_len
                    and not m.group("info").strip()):
                spans.append((fence_start, pos + len(line)))
                fence_char = None
        pos += len(line)
    if fence_char is not None:
        # An unclosed fence runs to end of input. Treating the remainder as
        # code strips less, so it is the safe reading.
        spans.append((fence_start, len(text)))
    return spans


def _is_escaped(text: str, index: int) -> bool:
    r"""True if text[index] is preceded by an ODD number of backslashes. Pure.

    CommonMark backslash-escaping makes `\<!--` literal text, which the raw
    regex happily treats as a comment opener (R9P2-07).
    """
    backslashes = 0
    cursor = index - 1
    while cursor >= 0 and text[cursor] == "\\":
        backslashes += 1
        cursor -= 1
    return backslashes % 2 == 1


# J-28B (2026-10-01, round 10 adversary A). J-27's code-region scanner was a
# BLACKLIST after all: every one of round 10's five findings was a new way to be
# code that the scanner had not enumerated — a blockquote marker in front of a
# fence, a space-plus-tab indent, a forged line boundary. That is the shape this
# repo has watched fail five times, and extending the scanner a fifth time would
# have been the sixth.
#
# The structural question is not "is this inside code?" but "does this opener
# genuinely OPEN AN HTML BLOCK?" CommonMark (HTML block type 2) says a `<!--`
# beginning a line with at most 3 spaces of indent does. Anything else — mid
# paragraph, behind a `>` blockquote marker, behind a tab — is literal text, and
# literal text can only be a comment WITHIN ITS OWN BLOCK.
#
# So: strip when the opener is a real HTML-block opener, OR when opener and
# closer lie in the same block (no blank line, no change of blockquote depth).
# Otherwise leave the text alone. This keys on document STRUCTURE, not on a
# surface character the author picks, which is the property the project's own
# law demands.
# J-41r (2026-10-01, ratified by Sai). The rule is now STRUCTURAL and tiny:
# a comment is stripped only if its opener and closer sit on the SAME LINE.
#
# Why this ends a sequence that three previous designs did not. Every attack in
# rounds 9, 10 and 11 worked by pairing an opener with a closer in a DIFFERENT
# block, so that the reader-visible prose between them was deleted from the
# scored denominator. All of them need the two delimiters on different lines —
# that is what "spanning" means. A comment that cannot cross a line cannot
# cross a block, so there is no renderer block-model to get wrong, and nothing
# left to enumerate. The three predecessors (backtick-only, a code-region
# scanner, a block-structure rule) were each a blacklist over "ways to be code"
# or "ways to end a block", and each lost the next round.
#
# Measured before ratification: 9 of 9 known attacks score the fabrication, and
# every single-line authoring note still PASSes.
#
# D-54 (2026-10-01): the multi-line BLOCK branch I added beyond Sai's
# ratification is REMOVED. An adversary found 3 ERROR-B in it within the hour,
# and I reproduced the unconditional one: `_BLANK_LINE_BETWEEN_RE` (`\n[ \t]*\n`)
# never matches a CRLF blank line, so the no-blank-line guard was VOID on every
# CRLF document and the branch deleted unbounded multi-paragraph prose —
# gate PASS, score 100.0, fabrication absent from the report.
#
# The claim "renderer-faithful BY CONSTRUCTION" was FALSE. The construction
# assumed `-->` is the only way an HTML comment closes; the abrupt-close forms
# `<!-->`, `<!--->` and `<!-- x --!>` end it on the opener line.
#
# The cost of removing it: OI-DEC-03 reopens — a MULTI-LINE authoring note is
# scored again. That is Error-A, recoverable, and registered as J-48 for Sai. I
# traded an unrecoverable error for a recoverable one in the wrong direction
# once; the invariant says do not do it twice.
#
# TWO PROTECTIONS SURVIVE, and both were checked rather than assumed:
#   - `_is_escaped`: `\<!--` renders as LITERAL text, so a same-line
#     `\<!-- ... -->` leaves the text between VISIBLE. Stripping it would be a
#     NEW Error-B introduced by this very rule. Deleting this helper was the
#     mistake this comment exists to prevent.
#   - `_code_line_spans` + `_CODE_SPAN_RE`: keep the rule from deleting
#     comment-shaped text inside code, which is scored today.
#
# CEILING: `_code_line_spans` remains an incomplete detector (round 11 showed it
# misses `>`-prefixed fences and space+tab indents). The consequence is now much
# smaller than it was — at worst a same-line comment inside undetected code is
# stripped, removing CODE text from the denominator, never reader-visible prose,
# because the same-line rule bounds the damage to one line. It is no longer on
# the Error-B path.
_SAME_LINE_COMMENT_RE = _re.compile(r"<!--[^\n]*?-->")

def _strip_html_comments_outside_code(text: str) -> str:
    """Strip SAME-LINE HTML comments, outside code, unescaped. Pure function.

    A comment is removed only when all three hold:
      - opener and closer are on the SAME LINE;
      - neither delimiter sits inside a code region;
      - the opener is not backslash-escaped.

    Any doubt leaves the text in place, which can only ADD claims to the scored
    denominator — the fail-closed direction, because stripping is what REMOVES
    text from scoring.
    """
    protected: list[tuple[int, int]] = _code_line_spans(text)
    protected += [(m.start(), m.end()) for m in _CODE_SPAN_RE.finditer(text)]

    def _protected(index: int) -> bool:
        return any(start <= index < end for start, end in protected)

    out: list[str] = []
    last = 0
    # D-54: iterate the SAME-LINE pattern directly. Driving the loop from the
    # multi-line _HTML_COMMENT_RE and classifying afterwards is what let the
    # block branch exist, and that branch cost an unrecoverable Error-B.
    for m in _SAME_LINE_COMMENT_RE.finditer(text):
        if (_protected(m.start())
                or _protected(m.end() - 1)
                or _is_escaped(text, m.start())):
            continue
        out.append(text[last:m.start()])
        out.append(" ")
        last = m.end()
    out.append(text[last:])
    return "".join(out)


# OI-MOAT-30 (round 7). syntok does not break after an UNPUNCTUATED Markdown
# header, so the body line below it was welded into the header's sentence and
# inherited the header's NON_CLAIM exemption:
#
#     "### TODO\nMongoDB lost all data under load"   -> nothing scored
#     "MongoDB lost all data under load"             -> scored
#
# A blank line is a paragraph boundary to syntok, and inserting one after a
# header changes no character of the header or the body — only where the
# segmenter is willing to cut. Fail-closed: it can only ADD claims to the
# denominator.
_HEADER_LINE_RE = _re.compile(r"^(#{1,6} [^\n]*)$", _re.MULTILINE)


def _break_after_headers(text: str) -> str:
    """Force a paragraph break after every Markdown header line. Pure function."""
    return _HEADER_LINE_RE.sub(lambda m: m.group(1) + "\n", text)


def _iter_raw_sentences(text: str) -> Iterator[str]:
    """Yield NFKC-normalized sentence strings from *text* using syntok.

    ORDER IS LOAD-BEARING: comments are stripped from the RAW text, BEFORE
    NFKC (OI-MOAT-26, round 7). NFKC folds compatibility variants, and the
    full-width forms "＜！－－" / "－－＞" fold to "<!--" / "-->". Stripping
    after NFKC therefore let an author MANUFACTURE a comment delimiter out of
    characters that no renderer hides — deleting reader-visible prose from the
    text being judged. The demonstrated attack welded a delimiter pair into the
    middle of a sentence and reversed it:

        draft   "The appliance ships with ＜！－－at most one, and never
                 with－－＞ dual power supplies [S6]."
        judged  "The appliance ships with   dual power supplies [S6]."
        verdict GROUNDED, gate PASS, score 100.0

    The gate certified the OPPOSITE of the sentence the author wrote, and
    printed the rewritten sentence back to them as if it were theirs. Stripping
    first means only genuine ASCII comment syntax is removed, and a full-width
    lookalike stays in the text and gets scored — fail-closed, and it is also
    the only reading under which the gate quotes the author faithfully.

    This is why CLAUDE.md bars NFKC from content paths: it silently rewrites
    authored characters. Here the rewrite was load-bearing for a moat rule.
    """
    import syntok.segmenter as segmenter  # lazy import — keeps top-level pure

    normalized = _nfkc(_break_after_headers(_strip_html_comments_outside_code(text)))
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
    raw_sentences = list(_iter_raw_sentences(draft))
    for position, raw_sentence in enumerate(raw_sentences):
        following = (
            raw_sentences[position + 1] if position + 1 < len(raw_sentences) else ""
        )
        raw_sentence = _propagate_across_semicolon(raw_sentence, following)
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

# A WELL-FORMED HTML/Markdown comment. Non-greedy and DOTALL so a multi-line
# authoring note is removed as one unit and two separate comments are not merged
# into one span that swallows the prose between them.
_HTML_COMMENT_RE = _re.compile(r"<!--.*?-->", _re.DOTALL)

# Citation pattern: [S1], [S12], [source:some-text]
# S\d+ plus optional letter suffix (OI-CITE-01): `[S1a]` is a citation MARKER
# even though capture never emits letter-suffixed ids — leaving it unmatched
# made the marker invisible (claim read UNCITED and the bracket digit leaked
# into numeric_tokens). Matched, it resolves like any key: absent from the
# store -> the precise UNVERIFIED_CITATION verdict.
_CITATION_RE = _re.compile(r"\[(?:S\d+[a-zA-Z]*|source:[^\]]+)\]")

# One or more citation markers at the very END of a clause, optionally followed
# by terminal punctuation. Anchored with $ on purpose: only a SENTENCE-FINAL
# marker cites the whole sentence, which is what makes propagating it to an
# earlier clause faithful to the author rather than a guess (OI-DEC-01, used by
# _propagate_sentence_citation).
_TRAILING_CITATIONS_RE = _re.compile(
    r"((?:\[(?:S\d+[a-zA-Z]*|source:[^\]]+)\])+)\s*[.!?]*\s*$"
)

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
        # RT4-01 (2026-08-30): the capitalized-token skip is GONE from this
        # path. It was a proper-noun heuristic — reasonable for the CONJUNCTION
        # SPLITTER, where under-splitting is the safe error and _has_verb_like_
        # token still keeps it — but here it decided whether a fragment escapes
        # the scored denominator, and CASE IS ONE BIT PER WORD THAT THE
        # ATTACKER OWNS. "PostgreSQL Fails." had no detectable verb purely
        # because "Fails" was capitalised; Title Case defeated the whole rule.
        # Detection is now case-insensitive, which errs toward calling things
        # claims — the fail-closed direction for a denominator test.
        w_orig = t.lower()
        if len(w_orig) >= min_len and any(w_orig.endswith(s) for s in suffixes):
            return True
    return False


def _header_asserts(header_body: str) -> bool:
    """Return True if *header_body* reads as an assertion rather than a label.

    An auxiliary anywhere, or a verb-like token that is not the final content
    token. See the discussion in ``_is_non_claim``. Pure function.
    """
    raw = [tok for tok in header_body.split() if tok.strip(".,;:!?\"'()[]{}")]
    content = [
        tok for tok in raw
        if tok.strip(".,;:!?\"'()[]{}").casefold() not in _STOP_WORDS
    ]
    if not content:
        return False
    for tok in raw:
        if tok.rstrip(".,;:!?").lower() in _AUXILIARIES:
            return True
    # R5-04 (2026-08-30): the suffix test ran on RAW tokens, so a trailing comma
    # made "Corrupts," not end in "s" and "### PostgreSQL Corrupts, Data"
    # escaped while the unpunctuated form was caught. Strip punctuation first —
    # the same normalisation every other token test in this module performs.
    for tok in content[:-1] if len(content) > 1 else []:
        w = tok.strip(".,;:!?\"'()[]{}").lower()
        if len(w) >= _VERB_SUFFIX_MIN_LEN and any(w.endswith(s) for s in _VERB_SUFFIXES):
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
    # ZERO content words -> NON_CLAIM (OI-DEC-06). Markdown furniture reached
    # this function and was scored: "---", "***", "|---|---|" all classified
    # FACTUAL and were flagged UNGROUNDED against the store.
    #
    # Note the rule is ZERO, not "few". Round 3 killed a ">= 6 content tokens"
    # floor by writing a five-token fabrication, and round 4 killed its
    # capitalisation-based replacement with the Shift key — any positive
    # threshold is a line the author can step under while still asserting
    # something. Zero is not that kind of line: a span with no content words has
    # no subject and no predicate, so there is nothing to assert and nothing to
    # smuggle. It is a property of the span, not a budget to spend up to.
    #
    # Numerics and citations are checked FIRST and override, so "99% [S9]" —
    # which has no content WORDS but plenty of verifiable content — stays a
    # scored claim.
    # OI-MOAT-32 (round 7): the comment above says citations are checked FIRST
    # and override — but the code only checked numerics, and _strip_citations
    # runs BEFORE the test, so the marker it was supposed to notice had already
    # been removed. "It is not [S1]." left the denominator entirely. A gap
    # between a docstring's guarantee and its code is worse than a missing
    # guarantee: the next reader builds on something that is not there.
    if _CITATION_RE.search(text):
        return False
    body = _strip_citations(text)
    if not _NUMERIC_RE.search(body) and not _content_words(_tokenize(body)):
        return True

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
        # RT3-02 (2026-08-30): this branch used to return True here, so ANY
        # header without a numeric or citation left the scored denominator no
        # matter what it asserted — "### Redis silently drops writes above ten
        # thousand concurrent clients" was NON_CLAIM and rode inside a PASS.
        # A heading that PREDICATES something is an assertion wearing a
        # heading's clothes, and must be scored.
        #
        # Headers need their own verb test (RT4-01 follow-through). The body
        # rule is now case-insensitive, and applied to headers it scores
        # "## Results" — the suffix heuristic cannot tell a plural noun from a
        # third-person verb, and an ordinary heading blocking PASS on every
        # document is an Error-A cost that would get the tool switched off,
        # which is its own kind of moat failure.
        #
        # The positional signal separates them without a count and without
        # relying on case: an English HEADING ends in its head noun
        # ("Results", "Key Findings"), while an ASSERTION puts its verb
        # medially and continues ("Redis LOSES Data"). So a header is scored
        # when it carries a verb-like token that is not its final content
        # token. Auxiliaries count wherever they appear.
        #
        # KNOWN RESIDUE, recorded not hidden: a verb-FINAL header
        # ("### PostgreSQL Fails") still reads structural. Tracked as
        # OI-MOAT-19 with a strict-xfail tripwire — the honest mechanism this
        # repo uses for a hole it has not closed, rather than a silent gap.
        return not _header_asserts(header_body)
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
        # OI-MOAT-07, hardened after RT3-01 (2026-08-30). "No finite verb" is
        # a gameable proxy for structure, and so was the >=6-content-token
        # floor that first replaced it: the attacker simply writes a shorter
        # fabrication ("PostgreSQL: unrecoverable corruption under load." — 5
        # content tokens, gate PASS 100.0). ANY count is a dial the attacker
        # owns, so the count is gone.
        #
        # The structural test that is NOT a dial: a label or list NAMES things;
        # an assertion PREDICATES something about them. A verbless fragment
        # whose content words are all proper nouns is a name list ("Redis
        # Postgres MongoDB"); one that introduces lower-case descriptive
        # content is predicating ("PostgreSQL: unrecoverable corruption") and
        # is scored. The attacker cannot shorten their way out — a fabrication
        # must say something about its subject, and saying it requires exactly
        # the descriptive tokens this test looks for.
        #
        # Error-A cost, accepted deliberately: a bare non-header section label
        # written in sentence case ("Results and discussion" with no '#') is
        # now scored → UNCITED → blocks PASS. That is recoverable (add the
        # '#', or cite it); a smuggled fabrication is not.
        # RT4-01 (2026-08-30): the "all content words are proper nouns" test is
        # GONE. It was the right IDEA — a list names, an assertion predicates —
        # but implemented with str.isupper(), i.e. keyed on case, which the
        # attacker sets freely: "PostgreSQL: Catastrophic Data Loss." satisfied
        # it exactly. Two rounds running, a test that keyed on a surface
        # property the author controls was defeated by setting that property.
        #
        # With verb detection now case-insensitive above, a genuinely verbless
        # fragment carrying content is rare and is SCORED. NON_CLAIM is reduced
        # to what document furniture actually is: markdown headers with no
        # assertion (handled above), pure transition phrases (above), and
        # fragments with no content words at all.
        #
        # Accepted Error-A, stated plainly: a bare name-list line ("Redis
        # Postgres MongoDB") is now scored -> UNCITED -> blocks PASS. That is
        # recoverable by citing or removing the line; a smuggled fabrication is
        # not recoverable at all.
        content_tokens = [
            tok for tok in _CITATION_RE.sub("", text).split()
            if tok.strip(".,;:!?\"'()[]{}") and
            tok.strip(".,;:!?\"'()[]{}").casefold() not in _STOP_WORDS
        ]
        return not content_tokens
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
    # OI-NUM-02: rstrip the token. _NUMERIC_RE's optional `\s?` exists so
    # "$4 million" stays one token, but with no suffix present it also eats a
    # trailing space, yielding "5000000 ". That token is then substring-matched
    # against the source window (t2's numeric-presence gate), where it cannot
    # match a number ending a sentence — a false alarm on a real claim.
    # rstrip only touches the tail, so "$4 million"'s internal space survives.
    numeric_tokens: tuple[str, ...] = tuple(
        (t[:-1] if t.endswith(".") else t).rstrip() for t in _raw_numeric
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

# OI-MOAT-25 (J-20). The tokenizer is \w+, which treats an apostrophe as a
# separator: "isn't" -> ["isn", "t"]. Neither piece is "not", so a NEGATION
# expressed as a contraction is destroyed before any rule can read it — and two
# rules depend on reading it. _span_is_hedged looks for "not" among the tokens
# before a mined span, and _ABSENCE_NEGATION_RE looks for it in claim and source
# text. Round 7 turned that into a one-character evasion of the quote-mining
# guard:
#
#     source "It is not true that the cache loses data on restart."  -> FAIL
#     source "It isn't true that the cache loses data on restart."   -> PASS, 100.0
#
# ONE RULE, NOT A TOKEN LIST. Every contracted negation in English is the suffix
# "n't", so expanding the suffix covers isn't / doesn't / haven't / didn't /
# won't / can't / shouldn't / mustn't and any other, including ones nobody
# enumerated. A list of contracted forms would be a blacklist over a class the
# author draws from, which is the shape of rule this project has now watched
# fail five times.
#
# BOTH APOSTROPHES. NFKC does NOT fold U+2019 (') to U+0027 ('), so a curly
# apostrophe would walk straight through a straight-quote-only rule — the same
# surface-property evasion one layer down. Both are matched explicitly.
#
# The irregulars are deliberately NOT special-cased: "can't" expands to "ca not"
# and "won't" to "wo not", which are not English but ARE symmetric — claim and
# source pass through the same function, so matching is unaffected and the "not"
# that the guards need is present. This function serves MATCHING only; the text
# shown to the author comes from _reconstruct_sentence, which has its own
# separate fidelity defect (it renders "doesn't" as "doesnot") that is
# PASS-enabling and remains Sai's call.
_NEGATION_CONTRACTION_RE = _re.compile(r"n['’]t\b", _re.IGNORECASE)


def _expand_negation_contractions(text: str) -> str:
    """Return *text* with the "n't" suffix expanded to " not".

    Pure function — returns a new string, mutates nothing.
    """
    return _NEGATION_CONTRACTION_RE.sub(" not", text)


def _tokenize(text: str) -> list[str]:
    r"""Return NFKC-casefolded word tokens from *text*, negations expanded.

    Tokenizer: re.findall(r"\w+", ...) on NFKC + casefold, after expanding
    contracted negations (OI-MOAT-25) so that "isn't" yields ["is", "not"]
    rather than ["isn", "t"].
    Pure function.
    """
    return _re.findall(r"\w+",
                       _expand_negation_contractions(_nfkc(text)).casefold())


def _strip_citations(text: str) -> str:
    """Remove citation markers (e.g. [S1], [S12], [source:...]) from *text*.

    Used before tokenizing claim text so that citation tokens do not pollute
    span matching or F1 computation.

    The whitespace left behind is collapsed (OI-DEC-06). Removing the marker
    from "the guarantee was invoked [S3]." used to yield "the guarantee was
    invoked ." — a space the writer never typed, in front of their own full
    stop. No verdict depends on it (the tokenizer discards whitespace), but the
    report quotes claim text back to the user, and text they did not write is
    corrosive in the one artifact whose entire job is fidelity to what they
    wrote.
    """
    stripped = _CITATION_RE.sub("", text)
    stripped = _re.sub(r"\s+([.,;:!?])", r"\1", stripped)
    return _re.sub(r"[ \t]{2,}", " ", stripped)


# Tokens that make the text AFTER them someone else's assertion, or a denial of
# it, rather than the source speaking in its own voice. Used ONLY by the
# exact-containment path (OI-T2-01): lowering T1's length floor to zero means a
# short span can be lifted out of "critics claim X" or "it is not true that X"
# and re-published as X, so containment is refused when one of these governs the
# span. Set membership on the tokens immediately preceding the span — a
# deliberately blunt, deterministic test, not an attempt at parsing.
_SPAN_HEDGE_TOKENS: frozenset[str] = frozenset({
    # attribution — the source reports that SOMEONE ELSE said this
    "claim", "claims", "claimed", "claiming", "alleges", "alleged", "allege",
    "allegedly", "asserts", "asserted", "argues", "argued", "contends",
    "contended", "purports", "purported", "purportedly", "suggests",
    "suggested", "reportedly", "rumored", "rumoured", "supposedly", "says",
    "said", "believes", "believed", "according", "per",
    # denial / falsity — the source says this is NOT so
    "not", "no", "never", "untrue", "false", "falsely", "incorrectly",
    "wrongly", "denies", "denied", "denying", "disputes", "disputed",
    "refutes", "refuted", "myth", "misconception", "contrary", "without",
    # conditionals / hypotheticals — the source is not asserting this
    "if", "unless", "whether", "would", "could", "might", "hypothetically",
    "suppose", "supposing", "assume", "assuming",
})

# How many source tokens before the span are inspected for a hedge. Five covers
# "it is not true that X", "according to the vendor, X" and "critics have long
# claimed X" without reaching back into an unrelated preceding clause.
_SPAN_HEDGE_LOOKBACK: int = 5


def _span_is_hedged(source_tokens: list[str], start: int) -> bool:
    """Return True iff the span at *start* sits under an attribution or denial.

    Looks at the up-to-_SPAN_HEDGE_LOOKBACK tokens immediately preceding the
    span. A hit means the source is reporting or denying the statement rather
    than making it, so quoting the span alone misrepresents the source.

    Fail-closed by construction: an ambiguous or unparseable context is one
    where a hedge token happens to be nearby, and that returns True (refuse),
    never False. Pure function.
    """
    window = source_tokens[max(0, start - _SPAN_HEDGE_LOOKBACK):start]
    return any(tok in _SPAN_HEDGE_TOKENS for tok in window)


# --- OI-MOAT-27 / J-19: factivity, not a longer blacklist -------------------
#
# Round 7 defeated _SPAN_HEDGE_TOKENS five ways: a hedge beyond the 5-token
# window, an unlisted reporting verb, a Cyrillic confusable, a structural hedge,
# and a hedge AFTER the span. The reviewer's diagnosis of WHY is the part worth
# keeping: every rule that has failed in this project was a BLACKLIST over a
# class the attacker draws from. Length, capitalisation, a noun's final letter,
# an apostrophe, one keystroke of punctuation — and a list of reporting verbs.
# The defect is not surface properties. It is putting the attacker on the
# enumerating side of the rule.
#
# Factivity inverts that. A factive verb PRESUPPOSES its complement:
#
#     "X has shown that P"   entails P      -- factive      -> may ground
#     "X argued that P"      does not       -- non-factive  -> refuse
#
# and crucially it is a WHITELIST, so an unlisted verb refuses. `maintain`,
# `posit`, `insist`, `hold` all refuse without ever being enumerated. It also
# satisfies CLAUDE.md's actual requirement — a property the attacker cannot set
# without giving up the attack — because to ground a mined span he must find a
# source whose verb asserts the claim, and at that point grounding it is
# CORRECT. The gate certifies source-support, not truth.
#
# The decisive control, from the solo gate: swap the subjects and the
# endorsement follows the VERB, not who is speaking.
#
#     REFUSE   Critics have argued ...         that Redis loses data on restart
#     GROUND   Our own benchmark has shown ... that Redis loses data on restart
#     GROUND   Critics have shown ...          that Redis loses data on restart
#     REFUSE   Our own benchmark has argued ... that Redis loses data on restart
#
# SCOPE, STATED HONESTLY. This closes the `that`-COMPLEMENT family only. A
# zero-complementizer complement ("The vendor claims the array rebuilds ...")
# and a retraction AFTER the span ("..., which is simply not the case") are
# different mechanisms and stay open and tripwired. Claiming this closes
# OI-MOAT-27 entirely would repeat the narrowing the solo gate caught.
#
# NEGATION IS A REQUIRED CONJUNCT, and it is why J-20 had to land first:
# "Critics haven't shown that P" is a NEGATED factive, and before the tokenizer
# repair "haven't" tokenized to ["haven","t"] and the negation was invisible.
# Neither fix is sufficient alone.
_COMPLEMENTIZERS: frozenset[str] = frozenset({"that"})

# Determiners that may sit between a complementizer and the start of a matched
# span ("... that THE Redis cache ..."). A CLOSED function-word class on
# purpose: unlike a token count or a capitalisation, an author cannot pad this
# to escape the guard without changing the sentence a reader sees.
_SPAN_LEADING_DETERMINERS: frozenset[str] = frozenset({
    "the", "a", "an", "this", "these", "those", "its", "their", "his", "her",
    "our", "my", "your", "such", "said",
})

_FACTIVE_VERBS: frozenset[str] = frozenset({
    "show", "shows", "showed", "shown",
    "demonstrate", "demonstrates", "demonstrated",
    "prove", "proves", "proved", "proven",
    "establish", "establishes", "established",
    "reveal", "reveals", "revealed",
    "confirm", "confirms", "confirmed",
    "find", "finds", "found",
    "discover", "discovers", "discovered",
    "observe", "observes", "observed",
    "measure", "measures", "measured",
    "verify", "verifies", "verified",
    "document", "documents", "documented",
    # J-22, ratified by Sai 2026-10-01 (D-51 ruling 4). PASS-ENABLING, so it was
    # his call, not mine.
    #
    # The argument that decided it was CONSISTENCY, not taste: `find/finds/found`
    # is already above, and "Smith found that P" carries exactly the same
    # attribution ambiguity as "Smith concluded that P". Excluding `conclude`
    # while including `find` was an inconsistency, not a caution. `indicate` is
    # safer still — its subject is typically the evidence ("the data indicates").
    #
    # `report*` is DELIBERATELY ABSENT and must stay absent. Its canonical
    # subject is a PUBLICATION relaying someone else's claim: "The blog reported
    # that P" does not assert P. Admitting it would make attribution
    # indistinguishable from assertion, which is the confusion rounds 3-8 kept
    # exploiting. A test pins that negative.
    #
    # CEILING: this whitelist is SUBJECT-BLIND. The real distinction is who the
    # verb's subject is, not which verb it is, so "Critics concluded that P" is
    # the next attack on this surface.
    "conclude", "concludes", "concluded",
    "indicate", "indicates", "indicated",
})

_NEGATION_TOKENS: frozenset[str] = frozenset({
    "not", "no", "never", "nor", "neither", "without",
})


def _span_under_nonfactive_complement(
    source_tokens: list[str], start: int
) -> bool:
    """Return True iff the span at *start* is a complement the source does not assert.

    The span is treated as a complement clause when a complementizer ("that")
    sits immediately before it. The governing predicate is then whatever verb
    precedes the complementizer, and the span may ground only if that verb is
    factive AND is not negated.

    Fail-closed at every branch:

    * complementizer present, NO factive verb before it  -> True (refuse).
      This is the whitelist's whole point — an unlisted verb refuses.
    * complementizer present, factive verb, but negated  -> True (refuse).
    * no complementizer                                  -> False here, and the
      blacklist in _span_is_hedged still applies. This function only ADDS
      refusals; it never grants a grounding the old rule denied.

    Pure function.
    """
    # R8A-01 follow-on (round 8, 2026-09-12): the complementizer is rarely
    # the token IMMEDIATELY before the span. On the contiguous-span path the
    # window is anchored to the claim's first CONTENT word, so "that the
    # Redis cache ..." puts a determiner between "that" and the span start and
    # the guard silently declined to fire — "A blogger speculated that the
    # <13-token span>" grounded. Skip leading DETERMINERS only (a closed
    # function-word class), never content words: a determiner cannot be added
    # or removed without changing the sentence a reader sees, so this is not a
    # surface the author can use to switch the rule off.
    cursor = start
    while cursor > 0 and source_tokens[cursor - 1] in _SPAN_LEADING_DETERMINERS:
        cursor -= 1
    if cursor == 0 or source_tokens[cursor - 1] not in _COMPLEMENTIZERS:
        return False
    prefix = source_tokens[:cursor - 1]
    if not prefix:
        return True
    if any(tok in _NEGATION_TOKENS for tok in prefix):
        return True
    return not any(tok in _FACTIVE_VERBS for tok in prefix)


def _claim_contained_verbatim(
    claim_tokens: list[str], sources: list[RetrievedSource]
) -> bool:
    """Return True iff the claim's ENTIRE token sequence is a contiguous,
    un-hedged span of some source (OI-T2-01, ADR-006).

    Why this is sound where a length floor is not. T1's ≥8-token floor exists
    so a short, high-frequency fragment cannot be assembled out of a source's
    vocabulary. But when the span IS the whole claim, there is no residual to
    assemble and no ratio to game: the source contains the claim, character for
    character, in order. An attacker cannot fabricate by exact quotation —
    doing so means giving up the fabrication.

    This became load-bearing when T2 was demoted. 31 of the 52 calibration
    claims are shorter than 8 content tokens, so without this path a claim
    quoted word-for-word from its source reads UNGROUNDED — which the gate's
    own end-to-end fixture did ("Redis handles 100K ops per second", 6 tokens).

    The one thing exact containment CAN do that a long span cannot is
    quote-mining: lifting "Redis is slow" out of "Critics claim Redis is slow,
    but our benchmark disagrees." _span_is_hedged is the guard, and it is the
    reason this is not simply `min_quote_len=0`.

    Pure function.
    """
    if not claim_tokens:
        return False
    width = len(claim_tokens)
    for source in sources:
        source_tokens = _tokenize(source.text)
        for start in range(len(source_tokens) - width + 1):
            if source_tokens[start:start + width] != claim_tokens:
                continue
            if (_span_is_hedged(source_tokens, start)
                    or _span_under_nonfactive_complement(source_tokens, start)):
                continue
            return True
    return False


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

    # Exact containment: the claim IS the span (OI-T2-01, ADR-006). Checked
    # BEFORE the length floor, because the floor is precisely what this path
    # exists to bypass — for a claim shorter than min_quote_len, this is the
    # only way T1 can fire, and after T2's demotion it is the only way the
    # claim can be grounded at all.
    if _claim_contained_verbatim(claim_tokens, sources):
        return True

    if n < min_quote_len:
        return False

    # Coverage is evaluated PER SOURCE, against the same source that supplied
    # the span (RT3-03, 2026-08-30). The first version of this check tested the
    # claim's tokens against the UNION of the cited sources, which meant adding
    # a citation WIDENED the vocabulary available to cover a fabrication:
    # "PostgreSQL sustained approximately 128000 operations per second ...
    # [S1]" correctly FAILED, and the identical claim cited "[S1][S2]" PASSED
    # at 100.0 — S2 contributed the word "postgresql" and nothing else. Citing
    # more evidence made a false claim pass, inverting the tool's premise.
    #
    # Per-source is also the principled reading: T1 is the VERBATIM tier, and a
    # quotation comes from ONE document. Splitting the evidentiary burden
    # across sources is the relational tier's job, and even there it now
    # requires a window that asserts the link. A genuine multi-source claim
    # simply falls through to T2 — fail-closed, recoverable.
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
        # Map each source n-gram to EVERY position it occurs at, not merely to
        # the fact that it occurs (R8A-01, 2026-09-12). The position is what
        # the endorsement guards below need: "does this span appear in the
        # source" and "does the source ASSERT it" are different questions, and
        # a set of n-grams can only answer the first.
        source_ngram_starts: dict[tuple[str, ...], list[int]] = {}
        for i in range(m - min_quote_len + 1):
            source_ngram_starts.setdefault(
                tuple(source_tokens[i : i + min_quote_len]), []).append(i)
        source_ngrams = source_ngram_starts.keys()
        # Check each claim window of length min_quote_len.
        span_matched = False
        for j in range(n - min_quote_len + 1):
            if tuple(claim_tokens[j : j + min_quote_len]) in source_ngrams:
                span_matched = True
                break
        if not span_matched:
            continue

        # This source supplied the span; it must also cover the residual.
        source_vocab = set(source_tokens)
        if not all(tok in source_vocab for tok in _content_words(claim_tokens)):
            continue

        # RT4-03 (2026-08-30): coverage is SET MEMBERSHIP, and a set has no
        # notion of who did what to whom. Every content token of "The
        # disk-backed alternative sustained approximately 128000 operations per
        # second ... twelve times the throughput of Redis" is in S1, and an
        # 8-gram is verbatim — but the claim REVERSES the subjects, handing
        # Redis's measured throughput to the system it beat.
        #
        # The span must therefore be anchored to the claim's own subject: the
        # matched window has to START at the claim's first content token. An
        # honest quotation restates its subject and then continues, so the
        # source contains "<subject> ... <span>" contiguously; a subject swap
        # does not, because the source never said that subject did that thing.
        # Fail-closed: a claim quoting mid-sentence falls through to T2.
        claim_content = _content_words(claim_tokens)
        if not claim_content:
            continue
        subject = claim_content[0]
        subject_positions = [
            i for i, tok in enumerate(claim_tokens) if tok == subject
        ]
        # R8A-01/R8A-02 (round 8, 2026-09-12) — THE ENDORSEMENT GUARDS APPLY
        # HERE TOO.
        #
        # _span_is_hedged and _span_under_nonfactive_complement were called
        # from exactly one place: _claim_contained_verbatim, the EXACT-
        # containment path. This span path applied neither. The guards
        # therefore fired for claims SHORTER than min_quote_len and were
        # silent for longer ones, which put the moat's endorsement check
        # behind a threshold the draft's author sets by typing more words.
        #
        # Reproduced: source "It is not true that the Redis cache silently
        # loses acknowledged writes on restart under default settings",
        # claim "The Redis cache silently loses acknowledged writes on
        # restart under default settings [S1]" -> GROUNDED, gate PASS,
        # score 100.0. The gate asserted the exact opposite of its source.
        # Shorten the same shape below 8 tokens and it correctly FAILED.
        #
        # This is the project's own standing law broken by the fix written
        # to uphold it: NEVER KEY A MOAT RULE ON A SURFACE PROPERTY THE
        # AUTHOR CONTROLS. Round 3 killed a token-count rule; round 4 killed
        # a capitalisation rule; this is claim length, found on the J-19
        # whitelist the same day it shipped.
        #
        # "At least one clean occurrence" mirrors _claim_contained_verbatim
        # deliberately: a source that BOTH reports an attributed claim and
        # independently asserts it does endorse it, and the two paths must
        # not disagree about what endorsement means.
        anchored = False
        for start in subject_positions:
            if start + min_quote_len > n:
                continue
            window = tuple(claim_tokens[start : start + min_quote_len])
            for src_start in source_ngram_starts.get(window, ()):
                if (_span_is_hedged(source_tokens, src_start)
                        or _span_under_nonfactive_complement(
                            source_tokens, src_start)):
                    continue
                anchored = True
                break
            if anchored:
                break
        if anchored:
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
    r"""Return tokens that are not stop words and carry at least one letter or digit.

    The alphanumeric requirement is a 2026-09-03 correction. The tokenizer is
    `\w+`, and in Python `\w` includes the UNDERSCORE — so a Markdown
    horizontal rule written as "___" tokenized to the single "word" `___` and
    counted as content. That made "___" a scored FACTUAL claim, flagged
    UNGROUNDED against the store, while the visually identical "---" was
    correctly ignored. Whether a rule is drawn with dashes or underscores is
    not a fact about the document.

    Purely fail-closed in the tiers (a token nobody can match was inflating
    both sides of an F1) and it is what makes the zero-content NON_CLAIM rule
    mean what it says.
    """
    return [
        t for t in tokens
        if t not in _STOP_WORDS and any(ch.isalnum() for ch in t)
    ]


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
    # rstrip per OI-NUM-02 — must stay identical to classify()'s extraction.
    return tuple((t[:-1] if t.endswith(".") else t).rstrip() for t in raw_numeric)


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


# ---------------------------------------------------------------------------
# THE T2 OPERATING POINT (thresholds are data, not code).
#
# 0.71 is CR-001's calibrated operating point (n=12, leave-one-out, held-out
# Error-A=0.20 / Error-B=0.143), selected under the moat-integrity rule
# (drive Error-B under its bound first, then minimise Error-A; ties broken
# toward the STRICTER tau).
#
# 0.76 is CR-002's operating point: n=52 SAI-RATIFIED GOLD labels, leave-one-out,
# held-out Error-A=0.200 / Error-B=0.111. It supersedes CR-001's 0.71 (n=12,
# Error-B=0.143) — Error-B monotonicity holds, 0.143 -> 0.111, so this is not
# buying Error-A down by raising Error-B.
#
# Deployed 2026-09-02. Measurement-neutral on the corpus: ZERO tier_sensitive
# rows fall in [0.71, 0.76), so no observed prediction changes; the move is the
# calibration speaking, not a retune. (The prior 0.65 -> 0.71 deployment on
# 2026-08-30 closed OI-CAL-01, where the gate ran 0.65 while every doc quoted
# 0.71.)
#
# Read the CR's independence caveat before quoting these rates: the ratifier is
# the project owner and the final labels differ from the machine's candidates on
# only 4 of 52 rows. Change this constant only via a calibration run + a new CR
# (never inline).
_LEX_TAU_DEFAULT: float = 0.76


def t2_lexical(
    claim: Claim,
    sources: list[RetrievedSource],
    lex_tau: float = _LEX_TAU_DEFAULT,
    other_source_texts: list[str] | None = None,
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

    # R5-01 (2026-08-30): T2 needed the SAME constraints T1 got in round 4.
    # `ground()` is `t1_verbatim(...) or t2_lexical(...)`, round 4 hardened T1
    # only, and the attacker took the other branch: a claim handing Redis's
    # 128000 ops/sec to PostgreSQL and citing [S1] scored GROUNDED at 100.0 —
    # although "postgresql" occurs NOWHERE in S1 — because content-word F1 over
    # the rest of the sentence cleared lex_tau.
    #
    # Raising lex_tau cannot fix this and never could: F1 is a RATIO whose
    # denominator includes the claim's own length, and the attacker writes the
    # claim. Round 5 produced a variant scoring F1=1.000 by reciting the
    # source's whole vocabulary in a false order. A threshold on an
    # attacker-controlled ratio is not a soundness test at any value.
    #
    # Two constraints, both fail-closed, neither a retune:
    #   (1) SUBJECT COVERAGE — the claim's first content token must occur in
    #       the source T2 is matching against. An honest claim names its
    #       subject in the source it cites; cross-entity attribution cannot.
    #   (2) POLARITY — the claim and the matched source must not disagree about
    #       negation. "Redis NEVER sustained..." shares nearly every content
    #       word with the sentence it contradicts, which is exactly what a
    #       bag-of-words tier scores as agreement.
    # Constraint (1) is a MISATTRIBUTION check, and getting here took two
    # discarded attempts worth recording.
    #
    # "Require the claim's SUBJECT to appear in the cited source" fails on a
    # fronted adverbial: "In our controlled benchmark on a single node,
    # PostgreSQL sustained..." has first-content-token "our", which IS in S1.
    # Guessing grammar positionally is the same class of error as guessing it
    # with a count.
    #
    # "Require EVERY content token to appear in the cited source" closes the
    # attack but destroys T2's reason to exist: it rejects
    # "PostgreSQL query optimization ACHIEVES high throughput" against a source
    # saying "...DELIVERS high throughput" — a one-word synonym, which is
    # precisely the paraphrase T2 was built to ground. (Proven by the golden
    # matrix, not by argument.)
    #
    # What actually distinguishes the attack: the substituted entity is not
    # merely absent from the cited source, it is present in a DIFFERENT source
    # the same session retrieved. A synonym the author chose ("achieves") is
    # absent from the whole store; a misattributed entity ("postgresql", cited
    # to S1) is sitting in S2. **Using source B's vocabulary while citing
    # source A is what misattribution IS**, and it needs no grammar, no case,
    # and no threshold.
    #
    # Residual, stated plainly: this catches misattribution only when the
    # session actually retrieved the other entity. It does not make T2 sound —
    # see OI-MOAT-21, which carries round 5's finding that a ratio over
    # attacker-controlled length cannot be a soundness test at any lex_tau.
    claim_negated = bool(_ABSENCE_NEGATION_RE.search(
        _expand_negation_contractions(_nfkc(claim.text)).casefold()))
    elsewhere: set[str] = set()
    for text in (other_source_texts or []):
        elsewhere.update(_tokenize(text))

    for source in sources:
        if t2_lexical_score(claim.text, source.text) < lex_tau:
            continue
        source_vocab = set(_tokenize(source.text))
        misattributed = [
            tok for tok in claim_content
            if tok not in source_vocab and tok in elsewhere
        ]
        if misattributed:
            continue
        # (2) POLARITY — a negated restatement shares nearly all its content
        # words with the sentence it contradicts, which a bag-of-words tier
        # scores as agreement.
        if claim_negated != bool(
            _ABSENCE_NEGATION_RE.search(
                _expand_negation_contractions(_nfkc(source.text)).casefold())
        ):
            continue
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

# --- Numeric CONTEXT extraction: quantity + rate (OI-MOAT-01, round 2) ------
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
        # RT3-05 (2026-08-30): this used to `break` unconditionally, so ONE
        # unrecognised token in the quantity slot left quantity=None — which
        # numeric_ok reads as "the claim asserts no dimension" and therefore
        # imposes NO constraint. "128000 node per second" was grounded by
        # "128000 operations per second": a singular or unknown noun switched
        # off the dimensional check that OI-MOAT-01/-09 exist to enforce.
        #
        # When a RATE trigger is present the construction is unambiguously
        # "<number> <measured noun> per <unit>", so an unrecognised noun in
        # that slot is a quantity ASSERTION we cannot canonicalise — not an
        # absence of one. Carry it through as itself so it must still match
        # the source's quantity (it will not), i.e. fail CLOSED.
        #
        # Scoped to rate-bearing mentions on purpose: with no rate trigger the
        # slot is genuinely ambiguous ("$4M last year" would assert a quantity
        # of "last"), and reading it there is the Error-A regression this
        # loop's skip-list was built to avoid. No rate -> unchanged behaviour.
        if rate is not None:
            quantity = tok
            break
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
    - Dimensional unit (OI-MOAT-01, completed round 2): a numeric mention
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
# J-43 — a figure SPELLED IN WORDS, inside a relational claim.
#
# `_NUMERIC_RE` requires a digit, so "ninety-seven percent of all type 2
# diabetes" produced no numeric_tokens, the R10C-04 guard was skipped
# vacuously, and the claim certified GROUNDED at PASS 100.0 against a store
# holding no such figure. One keystroke separated "97%" (refused) from
# "ninety-seven percent" (certified) — and the spelled form is the one a
# reader quotes without noticing it was never checked.
#
# WHY THIS IS NOT THE ENUMERATION THE PROJECT'S OWN LAW FORBIDS. The law says
# never key a moat rule on a surface property the AUTHOR CONTROLS (round 3's
# token count, round 4's Title Case). The set below is not such a property: the
# English cardinal number words are a CLOSED lexicon — a writer cannot invent a
# new word for 97 and still be understood, which is the whole point of writing
# the figure in words. That is the difference between this set and, say, a list
# of comment syntaxes (J-41r), where the space of ways to write the same thing
# is genuinely open.
#
# WHAT IT DOES NOT DO. It does not parse. There is no value, no unit, no
# comparison — "ninety-seven" is never turned into 97, and therefore never
# matched against a source's "97%". The rule is pure VERBATIM PRESENCE, exactly
# as Sai ruled on 2026-10-02: the spelled phrase must occur, contiguously, in a
# source the claim CITES. A source that spells the figure the same way grounds
# it; a source that writes it in digits does not, and the honest verdict there
# is a refusal, because proving "ninety-seven" means "97" requires a parser the
# moat does not have.
#
# "one" IS DELIBERATELY ABSENT. Its determiner and pronoun uses ("one of the
# mechanisms", "no one") dominate its numeric use by a wide margin, and every
# one of them would become a refusal. A spelled figure of one that carries a
# scale word is still checked, because the scale word is in the set
# ("one million" -> the phrase "one million" is checked via "million").
# CEILING: a bare spelled "one" with no scale word is NOT checked; it breaks on
# a draft asserting a fabricated count of exactly one. Upgrade path is
# part-of-speech disambiguation, which needs a tagger the verdict path may not
# import — so the hole is recorded rather than closed.
#
# ORDINALS AND VAGUE QUANTIFIERS ARE ALSO ABSENT, for opposite reasons:
# ordinals ("the third mechanism") are overwhelmingly non-quantitative in this
# position, and vague quantifiers ("almost all", "the vast majority") are an
# OPEN class — there is no closed lexicon of ways to be vague, so enumerating
# them is precisely the trap this comment opens by naming. That residue stays
# pinned as a strict xfail in test_moat_r10c04_relational_numeric.py.
_SPELLED_NUMBER_WORDS: frozenset[str] = frozenset({
    "zero", "two", "three", "four", "five", "six", "seven", "eight", "nine",
    "ten", "eleven", "twelve", "thirteen", "fourteen", "fifteen", "sixteen",
    "seventeen", "eighteen", "nineteen", "twenty", "thirty", "forty", "fifty",
    "sixty", "seventy", "eighty", "ninety",
    "hundred", "thousand", "million", "billion", "trillion", "dozen",
    # R12-05 (round 12): these five were MISSING, and they are the ordinary way
    # a draft overstates a magnitude — "causes thousands of customer refunds"
    # produced NO phrase, so J-43's guard ran vacuously and the claim certified
    # at PASS 100.0 while the digit form was refused on the same store. That is
    # the round-4 anti-pattern ("an unreadable field read as UNCONSTRAINED")
    # inside the very change whose comment cites it. They are members of the
    # same closed lexicon — a writer cannot invent a new word for "thousands"
    # either — so omitting them was not the open-class trap, it was five
    # missing strings.
    "hundreds", "thousands", "millions", "billions", "trillions", "dozens",
})


def _spelled_quantity_phrases(text: str) -> tuple[str, ...]:
    """Return the maximal runs of spelled number words in *text*, in order.

    "causes ninety-seven percent of all type 2 diabetes" -> ("ninety seven",).
    Each run is the tokenizer's view of the phrase, space-joined, so hyphenation
    and NFKC variants collapse into one canonical form ("ninety-seven",
    "ninety seven" and full-width digits-as-words all normalise together).

    Runs break at any non-number word, including the connector "and" — so
    "two hundred and fifty" yields ("two hundred", "fifty"). That is
    deliberate via-negativa: both runs still occur contiguously inside a source
    that spells the whole figure out, so an honest source is unaffected, and
    handling the connector would add a rule whose only effect is on drafts.

    Duplicates are preserved: a claim naming two different spelled figures must
    have both of them present.

    Pure function — no mutation, no LLM/network/random/wall-clock.
    """
    tokens = _tokenize(_strip_citations(text))
    phrases: list[str] = []
    run: list[str] = []
    for tok in tokens:
        if tok in _SPELLED_NUMBER_WORDS:
            run.append(tok)
            continue
        if run:
            phrases.append(" ".join(run))
            run = []
    if run:
        phrases.append(" ".join(run))
    return tuple(phrases)


def spelled_quantity_ok(
    claim: Claim, sources: list[RetrievedSource]
) -> bool:
    """True iff every spelled quantity phrase in *claim* occurs VERBATIM in one
    of *sources*.

    Each phrase must appear, contiguously and on word boundaries, in a SINGLE
    source — not assembled across two. A relational claim cites the sources
    that corroborate its relation, and a figure belongs to one statement, so a
    "ninety" in one document and a "seven" in another is not evidence of
    "ninety-seven".

    - No spelled phrase in the claim  -> True (nothing asserted, nothing to
      check). This is the vacuous case and it is the status quo for every claim
      written in digits.
    - A spelled phrase and NO sources -> False. Every "I don't know" points
      away from PASS.

    CEILING: one claim combining two spelled figures that live in two different
    cited sources ("causes seventy percent of A and thirty percent of B") is
    satisfied phrase-by-phrase, each against whichever source carries it — so
    that case works. What does NOT work is a single phrase split across
    sources, and that is the intended refusal.

    Pure function — no LLM, no network, no random, no wall-clock.
    """
    phrases = _spelled_quantity_phrases(claim.text)
    if not phrases:
        return True
    if not sources:
        return False

    # Compare token stream to token stream: both sides go through _tokenize, so
    # a phrase match is a match on WORDS, never on a substring that happens to
    # straddle them. Sentinel spaces make the containment test exact without a
    # second regex dialect ( _contains_word's lookarounds are for needles that
    # carry punctuation; these never do).
    streams = [" " + " ".join(_tokenize(source.text)) + " " for source in sources]
    for phrase in phrases:
        needle = " " + phrase + " "
        if not any(needle in stream for stream in streams):
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
# Negation cues that mark a source window as REPORTING an absence rather than
# asserting the thing claimed absent (RT3-04 content-contradiction check).
_ABSENCE_NEGATION_RE = _re.compile(
    r"\b(?:no|not|none|never|zero|without|absent|lacks?|lacking|"
    r"nothing|neither|nor|failed to|unable to|did not|does not|"
    r"could not|were not|was not|is not|are not)\b",
    _re.IGNORECASE,
)

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
    capitalization is the entity signal (OI-MOAT-04 fix).

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


# Prepositions that introduce the DOMAIN an absence is asserted over, as opposed
# to ones that introduce an argument of the subject. "no antidote FOR the toxin"
# names what the antidote is for (subject); "no antidote ... IN current
# guidelines" names where the looking happened (scope). Only the latter set is
# used, deliberately: "of" and "for" attach to the subject and treating them as
# scope would fire this rule on ordinary noun phrases.
_ABSENCE_SCOPE_PREPS: frozenset[str] = frozenset({
    "in", "within", "across", "throughout", "among", "amongst", "under",
    "outside", "beyond",
})

# Quantifiers and deictics that carry no searchable content. "any regulated
# market" is searchable as *regulated market*; "any" is not something a query
# can be expected to contain, and requiring it would make the rule unsatisfiable.
_ABSENCE_SCOPE_GENERIC: frozenset[str] = frozenset({
    "any", "all", "every", "each", "some", "no", "other", "current", "such",
    "these", "those", "this", "that", "its", "their", "our", "known", "given",
})


def _absence_scope_terms(text: str) -> set[str]:
    """Return the stemmed content terms of the claim's SCOPE phrase, if any.

    The scope is the trailing prepositional phrase headed by one of
    `_ABSENCE_SCOPE_PREPS` — the domain the absence is asserted over. The LAST
    such preposition wins, because the scope is what the sentence closes on:
    "no mention of battery defects IN the X200 manual" scopes to the manual.

    An empty result means the claim asserts no explicit scope, and the caller
    must then leave the query rule exactly as it was. That is the fail-SAFE
    direction for this particular check: an unscoped absence is not thereby
    suspicious, and the corpus's only gold-GROUNDED absence ("...affecting the
    X200 drone") is unscoped by this definition — `affecting` is a subject
    modifier, not a domain.

    Pure function.
    """
    tokens = _tokenize(text)
    last = -1
    for i, tok in enumerate(tokens):
        if tok in _ABSENCE_SCOPE_PREPS:
            last = i
    if last == -1:
        return set()
    tail = tokens[last + 1:]
    return {
        _stem(w) for w in _content_words(tail)
        if w not in _ABSENCE_SCOPE_GENERIC
    }


def _query_covers_scope(query: str, scope_terms: set[str]) -> bool:
    """Return True iff *query* addresses the claim's scope.

    No scope asserted → vacuously True (the rule is off). Otherwise the query
    must carry at least one scope term, stem-matched for parity with the rest
    of this path.

    Pure function.
    """
    if not scope_terms:
        return True
    query_stems = {_stem(w) for w in _re.findall(r"\w+", _nfkc(query).casefold())}
    return bool(scope_terms & query_stems)


def check_absence(
    claim: Claim,
    queries: list[str],
    min_absence_searches: int = 2,
    source_texts: list[str] | None = None,
) -> Verdict:
    """Return ABSENCE_SUPPORTED or UNVERIFIED_ABSENCE for an absence claim.

    Anchoring (OI-MOAT-04 fix — discriminating tokens, not the bare head noun):

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

    # RT3-04 (2026-08-30): CONTENT CONTRADICTION — check what was FOUND, not
    # only what was SEARCHED.
    #
    # Until now the absence path reasoned exclusively over query_provenance.
    # That left it structurally unable to notice the loudest possible
    # refutation: the retrieved sources containing the very thing claimed
    # absent. Against a store that is nothing but benchmark throughput
    # figures, "No benchmark throughput figures exist." was certified
    # ABSENCE_SUPPORTED at 100.0 — the gate asserting the opposite of its own
    # evidence, which is the single worst thing a grounding gate can do.
    #
    # The test mirrors the query-side rule exactly (head noun + at least one
    # corroborating content word, within ONE source) so that "discriminating"
    # means the same thing on both sides. A source that speaks to the subject
    # refutes the absence; refusing is fail-closed.
    if source_texts:
        others = {w for w in subject_content if w != head_noun}
        # Symmetry with the query side (R5-03): when the subject is NOT
        # specific enough for the query rule to demand a corroborator, this
        # rule must not demand one either — otherwise a non-specific subject
        # switches the contradiction check off while leaving the (weaker)
        # query check on, which is precisely backwards.
        contradiction_needs_corroborator = (
            len(subject_content) >= _ABSENCE_SPECIFIC_SUBJECT_MIN
        )
        # RT4-02 (2026-08-30): with a ONE-content-word subject there is no
        # "other" word, so the contradiction test below (`any(w in body for w
        # in others)`) is vacuously False and silently declines to run. The
        # gate then certified `No benchmark.` — the entire document — as
        # ABSENCE_SUPPORTED against a store of nothing but benchmarks.
        #
        # This is the round-4 anti-pattern in its purest form: a field too thin
        # to CHECK was read as a check that found NO OBJECTION. An absence
        # whose subject cannot be discriminated is not thereby supported; it is
        # unverifiable, and unverifiable must point away from PASS.
        if not strong and (not head_noun or not others):
            return Verdict.UNVERIFIED_ABSENCE
        for text in source_texts:
            for window in _split_sentences(text) or [text]:
                body = _nfkc(window).casefold()
                # Stem parity (RT4-02): the QUERY side stems its comparisons
                # while this side matched raw substrings, so a plural spelling
                # slipped past the contradiction check that the query check
                # would have caught. Both sides now stem.
                body_stems = {_stem(w) for w in _re.findall(r"\w+", body)}
                head_present = bool(head_noun) and (
                    head_noun in body or _stem(head_noun) in body_stems
                )
                corroborated = (
                    any(w in body or _stem(w) in body_stems for w in others)
                    if contradiction_needs_corroborator
                    else True
                )
                mentions = (
                    (head_present and corroborated)
                    or (strong and all(a in body for a in strong))
                )
                if not mentions:
                    continue
                # An AFFIRMATIVE mention of the subject refutes the absence; a
                # NEGATED one corroborates it. Without this distinction the
                # check flips its own meaning: the corpus's labeled-grounded
                # absences (q13/q14/q37) are supported by sources that say
                # "No recall evidence was found" / "returned zero results" —
                # text that carries the subject's words precisely BECAUSE it
                # reports the absence. The first version of this check read
                # those as contradictions and turned three human-labeled
                # GROUNDED rows into false alarms (caught by the mandatory
                # corpus regeneration diff, not by the test suite).
                if _ABSENCE_NEGATION_RE.search(
                    _expand_negation_contractions(body)):
                    continue
                return Verdict.UNVERIFIED_ABSENCE

    # Distinct, non-empty, normalized queries.
    seen: set[str] = set()
    distinct: list[str] = []
    for q in queries:
        q_norm = _nfkc(q).casefold().strip()
        if q_norm and q_norm not in seen:
            seen.add(q_norm)
            distinct.append(q_norm)

    # OI-ABS-01 (2026-09-03): a query counts toward the two-search minimum ONLY
    # if it also addresses the claim's SCOPE — the domain the absence is
    # asserted over.
    #
    # Until now this path checked only the negated SUBJECT, so a writer could
    # search narrowly and assert broadly and be certified: "no recall of the
    # Zentara inhaler IN ANY REGULATED MARKET" was ABSENCE_SUPPORTED by two
    # queries carrying "zentara" and "recall", one of them explicitly the FDA —
    # a single jurisdiction standing in for all of them. Those two rows (q14,
    # q37) were the entire remaining Error-B in the corpus after ADR-006.
    #
    # The principle: to establish that something is absent from a domain you
    # must have looked in that domain. A search outside the claimed scope is
    # not weak evidence for the claim, it is NO evidence, so it must not count
    # toward the minimum rather than merely counting for less.
    #
    # Fail-closed: this can only remove queries from the count, never add them,
    # so no absence can move TOWARD ABSENCE_SUPPORTED because of it. When the
    # claim asserts no scope, _absence_scope_terms returns empty and every
    # query passes — the rule is off, and the corpus's one gold-GROUNDED
    # absence stays supported.
    scope_terms = _absence_scope_terms(_nfkc(claim.text))
    distinct = [q for q in distinct if _query_covers_scope(q, scope_terms)]

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
        # R5-03 (2026-08-30): the two sides disagreed about "specific", and the
        # attacker stood in the disagreement. `There are no throughput
        # figures.` has a 2-content-word subject, so the QUERY side treats it
        # as non-specific and asks only for the head noun ("throughput",
        # present in both session queries) — while the CONTRADICTION side above
        # always demanded a corroborator ("figures", absent from every source),
        # so it could never fire. Result: the absence of the very thing every
        # source reports was certified at 100.0.
        # The fix is symmetry, applied above via _absence_specific().
        containing = [
            q
            for q in distinct
            if head_stem in q
            and (not specific or any(w in q for w in others))
        ]
        # A head noun present in a strict majority of a >=3-query session is a
        # blanket corpus word and evidences no targeted search.
        #
        # The >=3 gate is DELIBERATE and was re-validated on 2026-08-30: in a
        # 2-query session, "both queries mention the head noun" is the
        # signature of a TARGETED search, not of a blanket word. Removing the
        # gate rejected four legitimate absences (a changelog searched twice,
        # corpus q37's antidote+toxin pair, contraindications) — Error-A on
        # exactly the claims the absence path exists to support. RT3-04 is a
        # different defect and is fixed below, against the store's CONTENT.
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

def _is_quantity_token(token: str) -> bool:
    """True iff *token* expresses a QUANTITY rather than an identity.

    Hyphen-joined compounds are judged part by part, because "ninety-seven" is
    one whitespace token and `_SPELLED_NUMBER_WORDS` holds single words — a
    compound slipped through and became part of the endpoint phrase, which
    would have checked the same figure twice under a weaker rule than J-43's.

    Pure function.
    """
    parts = [part for part in token.replace("/", "-").split("-") if part]
    if not parts:
        return False
    return all(
        any(ch.isdigit() for ch in part) or part in _SPELLED_NUMBER_WORDS
        for part in parts
    )


# Where an endpoint PHRASE stops growing (J-39). Two closed classes:
#
#   1. The module's existing stop-word sets, reused rather than re-listed —
#      `_STOP_WORDS` (the tier content-word filter) and `_HEAD_NOUN_STOPS` (the
#      absence head-noun filter). One of the two already covers "the", "a",
#      "of", "its".
#   2. QUANTIFIERS, DETERMINERS AND DEGREE WORDS, which neither set carried.
#      These express SCOPE, not IDENTITY: "causes almost all type 2 diabetes"
#      and "causes type 2 diabetes" name the same endpoint, and a source
#      discussing it is under no obligation to repeat the draft's quantifier.
#      Swallowing them into the phrase was pure Error-A — it refused the
#      corpus's own labeled-grounded relational rows (caught by the suite, in
#      the same run that proved the tightening worked).
#
# Function words are a CLOSED class, which is what makes this a lexicon rather
# than a guess at author behaviour — the same argument that licenses
# `_SPELLED_NUMBER_WORDS`. An attacker gains nothing by dropping a quantifier:
# the identifying nouns are still required.
#   3. PREPOSITIONS AND SUBORDINATORS WERE ADDED HERE AFTER ROUND 12 (R12-11)
#      AND IMMEDIATELY WITHDRAWN (D-71). R12-11 is real: the union of the two
#      inherited sets is INCOMPLETE — `_HEAD_NOUN_STOPS` carries in/on/at/to/
#      for/of/with/by/from and `_ABSENCE_SCOPE_PREPS`, in this same file,
#      carries across/within/among/under, but neither carries between/during/
#      without/through. So "causes data loss across regions" makes the endpoint
#      "data loss across regions" and demands the draft's own preposition from
#      the source. Error-A, and the lesson stands: a closed class is only
#      closed once ENUMERATED, and reusing two partial sets does not complete
#      the union.
#
#      BUT THE FIX MADE THINGS WORSE, and measuring it is the only reason that
#      is known. Making a preposition a boundary does not shorten the endpoint
#      to "data loss" — it moves side_B's ANCHOR, because the anchor is the
#      LAST content token of the whole segment. Measured:
#
#        "The pipeline causes data loss across regions"
#          preposition NOT a boundary -> ('pipeline', 'data loss across regions')
#          preposition IS  a boundary -> ('pipeline', 'regions')
#
#      The second is a ONE-TOKEN endpoint — precisely the coincidence surface
#      J-39 exists to remove. So the choice is a recoverable Error-A against an
#      unrecoverable Error-B surface, and the invariant decides it.
#
#      R12-11 and R12-03 are therefore ONE design decision, not two findings:
#      the preposition boundary is only safe once side_B anchors on the FIRST
#      content run after the trigger instead of the last. That moves the
#      Error-A/Error-B trade-off, so it is Escalation #1 — registered as J-58
#      with both halves named together.
_ENDPOINT_PHRASE_STOPS: frozenset[str] = (
    frozenset(_HEAD_NOUN_STOPS) | frozenset(_STOP_WORDS) | frozenset({        "all", "almost", "nearly", "most", "mostly", "every", "each", "many",
        "much", "several", "few", "fewer", "more", "less", "least", "about",
        "roughly", "approximately", "around", "both", "either", "neither",
        "any", "none", "such", "same", "other", "another", "various",
        "multiple", "numerous", "certain", "total", "overall", "entire",
        "whole",
    })
)


def extract_arguments(text: str) -> tuple[str, str] | None:
    """Extract (side_A, side_B) head-noun phrases flanking the relational trigger.

    Strategy:
    1. NFKC-normalize input.
    2. Strip citation markers.
    3. Find the first relational trigger (longest-match-first).
    4. side_A = the contiguous head-noun PHRASE ending at the last content
       token before the trigger, extended LEFTWARD through contiguous content
       tokens (modifiers precede the head in English).
       side_B = the same construction anchored on the LAST non-quantity content
       token of the post-trigger segment.
    5. Return None when either side resolves to the empty phrase (fail-closed).

    KNOWN DEFECT, round 12 (R12-03 / R12-10, registered as J-58, owner Sai):
    side_B's anchor is the last content token of the WHOLE segment, so a
    trailing attribution or adverbial clause replaces the asserted object
    ("... causes X, researchers confirmed" anchors on "confirmed"). It cuts
    both ways — Error-B when the trailing phrase is in the source and the
    object is not, Error-A when the reverse. Moving the anchor changes the
    Error-A/Error-B trade-off, which is Escalation #1.

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

    # --- Extract the head-noun PHRASE on each side of the trigger ----------
    #
    # J-39 (round 10, closed 2026-10-02): this kept ONE TOKEN per side. "The
    # ingestion pipeline causes silent data loss" became ("pipeline", "loss"),
    # and two unrelated documents that each happened to use one of those common
    # nouns satisfied the two-source rule — an FT deal-flow page ("a thinner
    # pipeline leads to a wider loss") and an NEJM trial page ("sensorineural
    # hearing loss") certified a causal claim nobody had made, at PASS 100.0.
    #
    # The modifiers are not decoration. "silent data loss" and "a pre-tax loss"
    # are different objects, and the only thing separating them was the words
    # the extractor discarded.
    #
    # The ANCHOR is unchanged — still the last content token before the trigger,
    # and still the last non-digit content token after it (English noun-phrase
    # heads sit rightmost). The change is that the phrase then EXTENDS LEFTWARD
    # from that anchor through contiguous content tokens, because modifiers
    # precede the head. Keeping the old anchor is what makes this a pure
    # tightening: the needle can only grow, so a relation can only become
    # harder to corroborate.
    #
    # Boundaries of the run: a stop word, a token that is pure punctuation
    # (which is how a comma or clause break shows up after `split()`), or the
    # start of the segment. A bare digit is SKIPPED WITHOUT BREAKING the run —
    # "type 2 diabetes" is one phrase, and dropping the digit lets a source
    # write "type II" — the exact behaviour the old side_B extractor had.
    _stop = _ENDPOINT_PHRASE_STOPS

    def _cells(segment: str) -> list[tuple[str, bool]]:
        """Return (casefolded token, is_content) for each whitespace token.

        is_content is False for a run BOUNDARY: a stop word, or a token that is
        empty once punctuation is stripped (which is how a comma or clause break
        survives `split()`).

        A QUANTITY EXPRESSION is returned as ("", True) — inside the run,
        contributing nothing to the phrase. That covers a digit-bearing token
        ("2", "97%", "12.5%") and a spelled number word ("ninety", "million").
        A quantity is verified by the numeric guards (R10C-04 for digits, J-43
        for spelled figures) against the CITED sources; it is not part of the
        endpoint's identity, and requiring it here would check the same figure
        twice under a weaker rule. It also lets a source write "type II" where
        the draft wrote "type 2" — the behaviour the old side_B extractor had.
        """
        out: list[tuple[str, bool]] = []
        for raw in segment.split():
            tok = raw.strip(".,;:!?\"'()[]{}").casefold()
            if not tok or tok in _stop:
                out.append((tok, False))
            elif _is_quantity_token(tok):
                out.append(("", True))
            else:
                out.append((tok, True))
            # A clause break ends the run even when its punctuation is attached
            # to the word before it — which is the normal case, so testing only
            # for a standalone punctuation token would have made the documented
            # "never read across a comma" property false. "After the migration,
            # data loss causes outages" must yield "data loss", not "migration
            # data loss": a modifier on the far side of a clause boundary is not
            # modifying this head. Recorded as a BOUNDARY cell after the token,
            # so the token itself still counts.
            if raw.rstrip("\"')]}").endswith((",", ";", ":", "—", "–")):
                out.append(("", False))
        return out

    def _phrase_ending_at(cells: list[tuple[str, bool]], anchor: int) -> str:
        """Join the contiguous content run that ends at *anchor*, left-extended."""
        i = anchor
        while i - 1 >= 0 and cells[i - 1][1]:
            i -= 1
        return " ".join(tok for tok, is_content in cells[i:anchor + 1] if tok)

    def _side_a_phrase(segment: str) -> str:
        cells = _cells(segment)
        for i in range(len(cells) - 1, -1, -1):
            if cells[i][1] and cells[i][0]:
                return _phrase_ending_at(cells, i)
        return ""

    def _side_b_phrase(segment: str) -> str:
        """Anchor on the LAST non-digit content token, then extend leftward.

        The fallback for an all-numeric side is gone with the digit-skip: a
        segment whose only content is digits now yields "" and the caller
        returns None, which is UNVERIFIED_RELATION. That is fail-closed, and it
        replaces a fallback that handed `window_supports` a bare digit to match.
        """
        cells = _cells(segment)
        last = -1
        for i, (tok, is_content) in enumerate(cells):
            if is_content and tok:
                last = i
        if last == -1:
            return ""
        return _phrase_ending_at(cells, last)

    side_a = _side_a_phrase(before_text)
    side_b = _side_b_phrase(after_text)

    if not side_a or not side_b:
        return None

    return (side_a, side_b)


def _endpoint_in_window(window_text: str, endpoint: str) -> bool:
    """True iff EVERY content token of *endpoint* occurs in *window_text*, each
    on word boundaries.

    THE ONE DEFINITION OF "CONTAINS AN ENDPOINT". Until 2026-10-02 there were
    two, inside the same verdict branch: `window_supports` used a bare substring
    (so "loss" was supported by "lossless", and a multi-token phrase had to
    appear CONTIGUOUSLY), while `_relation_asserted` used `_contains_word`.
    Two definitions of containment in one branch is a seam, and J-44 was filed
    against exactly that seam. Both callers now route through here.

    Word order is free and intervening words are allowed ("loss of data"
    supports "data loss"), because a faithful source is not obliged to use the
    draft's word order — demanding contiguity is Error-A with no Error-B closed.
    What is NOT free is dropping a token: every modifier must be present
    somewhere in the window.

    An empty endpoint is False — never vacuously supported.

    Pure function — no mutation, no LLM/network/random/wall-clock.
    """
    tokens = [tok for tok in _nfkc(endpoint).casefold().split() if tok]
    if not tokens:
        return False
    window = _nfkc(window_text).casefold()

    # J-44 WAS LANDED HERE ON 2026-10-02 AND WITHDRAWN THE SAME DAY (D-69).
    #
    # The clause was `_contains_word(window, tok) or _stem(tok) in window_stems`
    # — a symmetric plural stem, endpoints only, triggers excluded. Round 12
    # refuted it in one line: `_stem` strips a trailing "s" with no
    # part-of-speech test, so it maps the NOUN "news" to the ADJECTIVE "new".
    #
    #   "The recall causes negative news [S1][S2]"
    #     against two sources containing no "news" at all
    #     -> UNVERIFIED_RELATION before J-44, GROUNDED / PASS 100.0 after it,
    #        with evidence_basis reporting "checked verbatim".
    #
    # The argument that J-39's longer phrase bounded the stem was WRONG, and
    # this is exactly how: when the collision lands on the HEAD noun and the
    # modifier is a word the unrelated source happens to contain, the extra
    # modifiers buy nothing. Same class: species/specie, ethics/ethic,
    # damages/damage, lens/len.
    #
    # WHY IT IS NOT REPAIRED INSTEAD. Telling "news"/"new" from "cost"/"costs"
    # requires knowing that "news" is not a plural — which is a DICTIONARY
    # fact, not a suffix fact. Every repair that stays inside this file is a
    # blacklist of s-final singular nouns, and an incomplete blacklist on a
    # loosening is an Error-B generator: the one word missing from it is the
    # attack. English s-final singulars are not a lexicon I can close the way
    # the cardinal number words are closed.
    #
    # So the moat invariant decides it, literally: no change may reduce Error-A
    # by raising Error-B. The Error-A is real and stays open as J-44, now
    # Escalation #1 with its two candidate designs named. Reopening it needs a
    # real morphological analyser, which is a dependency the verdict path may
    # not import — i.e. it is a product decision, not a fix.
    return all(_contains_word(window, tok) for tok in tokens)


def window_supports(source: RetrievedSource, argument_text: str) -> bool:
    """Return True iff *argument_text* appears (as content words) in any T2 window
    of *source*.

    Uses the T1 verbatim path for short arguments (exact token inclusion) or the
    T2 window scoring machinery for longer phrases. For a single-token argument,
    NFKC-casefold substring match against each ±2-sentence window suffices.

    Pure function — no mutation, no LLM/network/random/wall-clock.
    """
    if not _nfkc(argument_text).casefold().strip():
        return False

    sentences = _split_sentences(source.text)
    if not sentences:
        # Single-block source — check the whole text.
        return _endpoint_in_window(source.text, argument_text)

    n = len(sentences)
    for c in range(n):
        lo = max(0, c - 2)
        hi = min(n, c + 3)
        if _endpoint_in_window(" ".join(sentences[lo:hi]), argument_text):
            return True

    return False


# ---------------------------------------------------------------------------
# Relational grounding
# ---------------------------------------------------------------------------

def _contains_word(haystack: str, needle: str) -> bool:
    """True iff *needle* occurs in *haystack* on word boundaries. Pure.

    R10C-02 (round 10): endpoint and trigger matching used a BARE SUBSTRING
    test, so "AI drives mass layoffs [S1][S2]" certified GROUNDED against two
    sources whose only "ai" was inside the word "said". Two-source corroboration
    of a relation nobody asserted.

    Boundaries are expressed as lookarounds on word characters rather than \b,
    because \b is defined relative to the adjacent character's class and
    therefore misbehaves when the needle begins or ends with punctuation — which
    a head-noun phrase extracted from real prose regularly does.

    Strictly fail-closed: it can only REMOVE spurious matches, so a relation can
    only become harder to corroborate, never easier.
    """
    if not needle:
        return False
    return _re.search(
        r"(?<!\w)" + _re.escape(needle) + r"(?!\w)", haystack
    ) is not None


def _relation_asserted(
    sources: list[RetrievedSource], side_a: str, side_b: str
) -> bool:
    """Return True iff some ±2-sentence window of some source asserts a relation
    between *side_a* and *side_b*.

    A window asserts the relation when it carries BOTH endpoints AND at least
    one relational trigger from the lexicon (``_RELATIONAL_TRIGGERS``). The
    trigger family is deliberately not required to match the claim's own
    trigger verbatim: "causes" / "leads to" / "results in" express the same
    relation, and demanding a surface match would raise Error-A on faithful
    paraphrase without closing any Error-B path (a window with NO trigger
    asserts no relation at all, whichever word the claim chose).

    OI-MOAT-05. Pure function — no mutation, no LLM/network/random/wall-clock.
    """
    a = _nfkc(side_a).casefold().strip()
    b = _nfkc(side_b).casefold().strip()
    if not a or not b:
        return False

    for source in sources:
        sentences = _split_sentences(source.text)
        if not sentences:
            sentences = [source.text]
        n = len(sentences)
        for c in range(n):
            lo = max(0, c - 2)
            hi = min(n, c + 3)
            window = _nfkc(" ".join(sentences[lo:hi])).casefold()
            if not _endpoint_in_window(window, a) or not _endpoint_in_window(
                    window, b):
                continue
            if any(_contains_word(window, trigger)
                   for trigger in _RELATIONAL_TRIGGERS):
                return True
    return False


# ADR-007 diagnostic values. A closed set, like the verdict taxonomy — a new
# one needs the ADR amended, for the same reason.
RELATION_CORROBORATED = "corroborated_by_two_sources"
RELATION_NOT_CORROBORATED = "not_corroborated"
RELATION_FIGURE_ABSENT = "figure_not_in_cited_sources"


def relational_diagnostic(claim: Claim, store: dict[str, RetrievedSource]) -> str:
    """Report what the DEMOTED relational rule would have concluded. Decides nothing.

    This is the whole of the pre-ADR-007 relational branch, moved intact out of
    the verdict path: the two-source corroboration rule (`ground_relational`),
    the numeric check (R10C-04) and the spelled-figure check (J-43). It is kept
    rather than deleted on this repo's standing rule that a demoted computation
    stays a VISIBLE no-op — `tier_sensitive` is kept for the same reason — so
    that a future change cannot silently re-enable a path nobody re-validated.

    Keeping it whole also keeps every tripwire written against it STRICT. Round
    10's and round 12's findings are assertions about what this function
    returns, not about a gate verdict, so they stay red-able at full strength
    instead of being softened to "the claim does not PASS" — which would have
    been true for the wrong reason and would have stopped measuring anything.

    Returns one of RELATION_CORROBORATED / RELATION_NOT_CORROBORATED /
    RELATION_FIGURE_ABSENT. Pure function — no mutation, no LLM/network/
    random/wall-clock.
    """
    if ground_relational(claim, store) != Verdict.GROUNDED:
        return RELATION_NOT_CORROBORATED

    cited_verbatim = [
        source
        for source in (resolve(c, store) for c in claim.citations)
        if source is not None
        and source.full_text_source == "verbatim"
        and source.text
    ]
    if claim.numeric_tokens and not numeric_ok(claim, cited_verbatim):
        return RELATION_FIGURE_ABSENT
    if not spelled_quantity_ok(claim, cited_verbatim):
        return RELATION_FIGURE_ABSENT
    return RELATION_CORROBORATED


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
    endpoints_split_across_sources = any(
        s_a_id != s_b_id for s_a_id in a_supported_in for s_b_id in b_supported_in
    )
    if not endpoints_split_across_sources:
        return Verdict.UNVERIFIED_RELATION

    # OI-MOAT-05 predicate check (2026-08-30): endpoint PRESENCE in two
    # disjoint sources is not support for the RELATION. "Marketing spend rose"
    # in S1 and "signups rose" in S2 are two independent facts; the causal link
    # between them is the draft's own invention, and the old rule certified it.
    # Some cited verbatim source must actually ASSERT a relation between the two
    # endpoints: a window carrying a relational trigger AND both endpoints.
    # This is the corpus's own discriminator — q12/q36 (labeled grounded) each
    # have such a window ("insulin resistance ... causes type 2 diabetes");
    # q25/q26/q48 (labeled violation) have none.
    # Fail-closed: this can only move a relation AWAY from GROUNDED.
    if not _relation_asserted(sources_list, side_a, side_b):
        return Verdict.UNVERIFIED_RELATION

    return Verdict.GROUNDED


# ---------------------------------------------------------------------------
# Per-claim verdict dispatcher (spec §4.4)
# ---------------------------------------------------------------------------

def _session_queries(store: dict[str, RetrievedSource]) -> list[str]:
    """Return the DISTINCT query_provenance values across the store.

    Order-insensitive content (the caller — check_absence — counts distinct
    matches). A list is returned to satisfy check_absence's signature.
    Pure function — no mutation, no LLM/network/random/wall-clock.
    """
    return _distinct_queries(store.values())


def _distinct_queries(sources: "Iterable[RetrievedSource]") -> list[str]:
    """Distinct query_provenance values across *sources*, order-preserving. Pure."""
    seen: set[str] = set()
    out: list[str] = []
    for source in sources:
        q = source.query_provenance
        if q not in seen:
            seen.add(q)
            out.append(q)
    return out


def ground(
    claim: Claim,
    store: dict[str, RetrievedSource],
    lex_tau: float = _LEX_TAU_DEFAULT,
    self_source_ids: frozenset[str] = frozenset(),
) -> Verdict:
    """Return the grounding Verdict for a single ALREADY-CLASSIFIED claim.

    Implements spec §4.4 decision logic in exact order. The input `claim` is
    assumed to carry a resolved `kind`, `citations`, and `numeric_tokens`
    (i.e. it has passed through classify()).

    Branch order (first match wins):
      1. NON_CLAIM                     → GROUNDED (excluded from denominator
                                         upstream in Task 9).
      2. any citation unresolved       → UNVERIFIED_CITATION. Runs BEFORE the
                                         kind dispatch (J-25): provenance is a
                                         fact about the store, independent of
                                         claim kind, and RELATIONAL/ABSENCE
                                         never reached it when it sat lower.
      3. RELATIONAL                    → delegate to ground_relational.
      4. ABSENCE                       → delegate to check_absence with the
                                         session's distinct queries.
      5. no citations                  → UNCITED.
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

    # PROVENANCE PRECEDES KIND (J-25, closes R9P1-01 and R9P1-02, 2026-10-01).
    #
    # This check USED to sit below the kind dispatch, which meant RELATIONAL
    # and ABSENCE claims never reached it: ground_relational skips a citation
    # it cannot resolve, and check_absence never inspects claim.citations at
    # all. So "Insulin resistance causes type 2 diabetes [S2][S3][S99]" and
    # "[S99] We found no evidence of a recall" both certified PASS 100.0 with
    # a source that was never retrieved — while evidence_basis on the SAME row
    # reported that S99 had never been retrieved. The gate contradicted its own
    # explanation of itself.
    #
    # Whether a cited marker names something the session actually retrieved is
    # a fact about the STORE, prior to and independent of what kind of claim
    # cites it. Nothing downstream can re-derive it: once the kind dispatch has
    # run, the unresolvable marker has already been discarded. Fail-closed —
    # it can only move a claim away from PASS, never toward it.
    #
    # An UNCITED claim is unaffected: an empty citation list makes any() False,
    # so absence claims that cite nothing still reach check_absence as before.
    if any(resolve(c, store) is None for c in claim.citations):
        return Verdict.UNVERIFIED_CITATION

    # ======================================================================
    # RELATIONAL GROUNDING IS DEMOTED (ADR-007, Sai's ruling 2026-10-02).
    # A RELATIONAL claim IS NEVER CERTIFIED. The two-source corroboration
    # result is reported as a DIAGNOSTIC only (`relation_diagnostic`).
    #
    # WHY THE RULE WENT. Round 12 demonstrated SEVEN Error-B shapes on it, two
    # CRITICAL, all pre-existing: a negated endpoint grounded by the positive, a
    # trailing clause replacing the asserted object, a trigger merely
    # CO-LOCATED in the window, direction-blindness, a window that DENIES the
    # relation satisfying it, both endpoints resolving to one phrase, and the
    # absence variant. Seven shapes on one rule is a CLASS: it was
    # reconstructing "this source asserts a relation between A and B" from
    # token co-occurrence, against an adversary who writes the document — the
    # trap the comment stripper lost five rounds to (J-41), and the reason
    # ADR-006 demoted T2.
    #
    # WHY A FLAT REFUSAL AND NOT FALL-THROUGH — D-74 WITHDRAWN (D-76).
    # ADR-007 first let a relational claim fall through to the ordinary
    # verbatim path, on the measured argument that it cost 0.360 Error-A
    # against a flat refusal's 0.400. Round 13 refuted it: T1 and corroboration
    # are NOT NESTED. T1 certifies on an 8-token contiguous span anchored at the
    # claim's SUBJECT plus set-membership coverage, so a causal claim with a
    # long subject phrase had its entire PREDICATE checked only by "do these
    # words appear anywhere in this source". Direction reversal with no planted
    # vocabulary, a source that explicitly DENIES the relation, and negation
    # reversal ("causes no X" grounded by "causes X", because `no` is a stop
    # word) all certified PASS 100.0. J-57, J-60 and J-61 were not closed by
    # the demotion — they were MOVED ONTO T1.
    #
    # So the four points of Error-A that fall-through saved bought six Error-B
    # shapes. The invariant is not a preference: Error-B is unrecoverable and no
    # change may reduce Error-A by raising it. Sai priced the flat refusal at
    # 0.400 and ruled on it; the refinement was mine and it was wrong.
    #
    # The machinery is KEPT, not deleted — `relational_diagnostic`,
    # `ground_relational`, `extract_arguments`, `_endpoint_in_window` and
    # `spelled_quantity_ok` all still run and still report, so every round-10
    # and round-12 tripwire stays strict and a future change cannot silently
    # re-enable a path nobody re-validated (the `tier_sensitive` precedent).
    # `UNVERIFIED_RELATION` is therefore the verdict again — reachable, and
    # meaning exactly one thing: this gate does not certify relations.
    # ======================================================================
    if claim.kind == ClaimKind.RELATIONAL:
        return Verdict.UNVERIFIED_RELATION

    if claim.kind == ClaimKind.ABSENCE:
        # R10C-03: a store of ONLY haiku_summary records certified an absence at
        # PASS 100.0, breaking the named invariant that a summary can never
        # ground a claim.
        #
        # THE DIRECTION HERE IS A TRAP. The naive repair — filter source_texts
        # to verbatim — is FAIL-OPEN: source_texts is scanned for a REFUTATION,
        # so removing summaries removes chances to find one and makes absence
        # EASIER to certify. So summaries stay in that scan, and what is
        # restricted is the BASIS for certification: at least one verbatim
        # source must exist, and only verbatim records may contribute the
        # distinct searches. A summary may refuse, never approve.
        # R17-01 (round 17, 2026-10-03) — J-83 DID NOT REACH THIS BRANCH.
        #
        # A store containing nothing but `Read` records OF THE DRAFT returned
        # ABSENCE_SUPPORTED at PASS 100.0, while `_self_source_ids` had
        # correctly identified 2 of 2 records as the draft. The filter lived in
        # the verbatim path and this branch returns above it — **the identical
        # placement error as R16-01, on the same branch, fixed this morning.**
        # An agent that reads its own draft and nothing else has done no
        # searching, and an absence claim certified on that is the emptiest
        # possible PASS.
        #
        # WHY ONLY THE *BASIS* NARROWS, AND NOT THE SCAN. D-54: shrinking the
        # store for check_absence moves its two arguments in OPPOSITE
        # directions — fewer `source_texts` means fewer refutations found
        # (CERTIFY, fail-OPEN), and fewer distinct queries can disable the
        # blanket-corpus-word refusal (CERTIFY, fail-OPEN). So a filtered store
        # is not a weaker store, it is a DIFFERENTLY weak one. What narrows is
        # the BASIS requirement, exactly as it already does for summaries
        # (R10C-03): at least one verbatim source that is NOT the draft must
        # exist before any absence can be certified. Strictly fail-closed.
        if not any(s.full_text_source == "verbatim" and s.text
                   and s.source_id not in self_source_ids
                   for s in store.values()):
            return Verdict.UNVERIFIED_ABSENCE
        # R11B-01 (round 11) — WITHDRAWN: passing only VERBATIM queries here was
        # my own Error-B, introduced hours earlier and claimed fail-closed.
        #
        # `queries` is BOTH a numerator and a DENOMINATOR. It supplies the
        # matches that certify an absence, AND the population size for the
        # blanket-corpus-word refusal at the `len(distinct) >= 3` gate below.
        # Shrinking it therefore switches that REFUSAL OFF: the same claim over
        # the same sources reads UNVERIFIED_ABSENCE with four queries and
        # ABSENCE_SUPPORTED with two.
        #
        # I identified the direction trap in this function (source_texts, above)
        # and then walked into a second instance of it. The full list is
        # restored; the verbatim-BASIS requirement above stays, which is what
        # closes the original R10C-03 headline (a store of only summaries cannot
        # certify). That a summary can still supply a counting query is OPEN
        # again, registered as J-42 — a smaller hole than the one I created.
        # J-62 + J-71 (2026-10-03, Sai's GO). THE FIGURE CHECKS REACH ABSENCE.
        #
        # Round 14 R14-03a: the digit 4200, present in NO source text, certified
        # `ABSENCE_SUPPORTED` at PASS 100.0 / exit 0 — because this branch
        # returns ABOVE the two figure checks, so `numeric_ok` was unreachable
        # from here. J-62 is the same hole for a figure spelled in words. One
        # defect, two spellings; they were briefly registered as two jobs with
        # different owners, which would have made the register incoherent.
        #
        # D-77 made those checks kind-agnostic for the claims that REACH them,
        # and ADR-007's amendment records that it was written up as covering
        # ABSENCE when it did not — ABSENCE and RELATIONAL both return earlier.
        # This closes the ABSENCE half for FIGURES THE EXTRACTOR SEES —
        # NOT the whole class. Round 16 enumerated the remainder: a bare
        # `one`, ordinals, `a third`, `half`, `double` and vague
        # quantifiers all still reach ABSENCE_SUPPORTED, because
        # `_SPELLED_NUMBER_WORDS` excludes them by a recorded CEILING.
        #
        # WHY `store.values()` AND NOT THE CITED SOURCES. An absence claim is
        # checked against what was SEARCHED, not what was cited, and it often
        # cites nothing at all (`check_absence` never inspects claim.citations).
        # Restricting to citations would make the check vacuous on exactly the
        # claims that need it. Verbatim-only, because a summary may refuse but
        # never certify (R10C-03).
        #
        # DIRECTION: strictly fail-closed. It can only return UNVERIFIED_NUMBER
        # where ABSENCE_SUPPORTED would have been returned, never the reverse.
        # MEASURED, not assumed: Error-A 10/25 = 0.400 and Error-B 0/27 = 0.000
        # are UNCHANGED, and the corpus does exercise this path — 2 of its 7
        # ABSENCE rows carry a figure (q13, q22), so the zero delta is a
        # measurement rather than non-measurement. CEILING: both of those
        # figures are product model numbers (`X200` extracts as `200`, and
        # `X200 manual` as `200 m` — J-72), so the shape the corpus tests with
        # is not a quantity. A real-quantity absence row would measure this
        # better and needs a gold label, which is Sai's.
        # PLACEMENT CORRECTED 2026-10-03 (R16-01). The figure checks ran HERE,
        # ABOVE check_absence, and round 16 measured the cost: of the 1,910
        # verdicts the change altered across 57 stores, **1,904 were
        # UNVERIFIED_ABSENCE -> UNVERIFIED_NUMBER relabels** — including the
        # RT3-04 content-contradiction verdict, the absence branch's STRONGEST
        # refusal. The check was pre-empting better reasons and reporting a
        # weaker one, so D-46 masking became the default rather than a one-off:
        # it masked J-33, J-31, J-42 and the r9 control within hours.
        #
        # So the checks now run only on a claim check_absence would CERTIFY.
        # That is the only population the hole ever existed in — R14-03a was a
        # fabricated figure inside a SUPPORTED absence — and it leaves every
        # existing refusal with its own reason intact.
        #
        # Still strictly fail-closed: the only transition it can cause is
        # ABSENCE_SUPPORTED -> UNVERIFIED_NUMBER. Round 16 confirmed the
        # direction structurally as well as empirically — UNVERIFIED_NUMBER is
        # not in _NUMERATOR_VERDICTS — across 3,705 differential comparisons
        # with zero moves toward PASS.
        absence_verdict = check_absence(
            claim,
            _session_queries(store),
            source_texts=[s.text for s in store.values() if s.text],
        )
        if absence_verdict is not Verdict.ABSENCE_SUPPORTED:
            return absence_verdict
        # R18-01 — THE FOURTH INSTANCE OF THE PLACEMENT CLASS, AND IT IS FOUR
        # LINES BELOW THE THIRD. R17-01 narrowed the BASIS check above to
        # exclude self-sources; this list, which feeds the two FIGURE checks,
        # was left reading `store.values()`. Adding ONE `Read` record of the
        # draft flipped `UNVERIFIED_NUMBER` -> `ABSENCE_SUPPORTED` at PASS
        # 100.0 for a figure present in no retrieved source, because the draft
        # contains the figure and so "verifies" it.
        #
        # The cross-kind guard did not catch it: its ABSENCE fixture carries no
        # figure, so it never reached this return. That is the CEILING that
        # file's own docstring records — it enumerates KINDS, not the 15 return
        # statements — biting within the hour. The fixture now carries a figure.
        _absence_verbatim = [
            source for source in store.values()
            if source.full_text_source == "verbatim" and source.text
            and source.source_id not in self_source_ids
        ]
        if claim.numeric_tokens and not numeric_ok(claim, _absence_verbatim):
            return Verdict.UNVERIFIED_NUMBER
        if not spelled_quantity_ok(claim, _absence_verbatim):
            return Verdict.UNVERIFIED_NUMBER
        return absence_verdict

    if not claim.citations:
        return Verdict.UNCITED

    # Every marker resolved above. Narrow the type by construction rather
    # than by a filter: a filter would silently shrink the cited set, which is
    # the exact failure mode J-25 just closed. If the invariant is ever broken
    # the gate must fail loudly, not quietly certify against fewer sources.
    sources: list[RetrievedSource] = []
    for _citation in claim.citations:
        _source = resolve(_citation, store)
        if _source is None:
            raise AssertionError(
                f"citation {_citation!r} unresolved past the provenance check "
                "in ground(); the check above must precede this loop"
            )
        sources.append(_source)

    if any(not s.text for s in sources):
        return Verdict.UNGROUNDABLE

    # J-83: a source that IS the draft cannot certify the draft. Narrowed in the
    # same breath as the summary rule because it is the same shape — present in
    # the store, incapable of grounding. A claim citing the draft AND a real
    # source still grounds on the real one.
    verbatim = [
        s for s in sources
        if s.full_text_source == "verbatim" and s.source_id not in self_source_ids
    ]
    if not verbatim:
        return Verdict.UNGROUNDABLE

    # R13-01 / R13-02 (round 13) — A CHECK GATED ON A CLASSIFIER BRANCH IS A
    # CHECK AN AUTHOR CAN ROUTE AROUND BY ADDING ONE WORD.
    #
    # This read `claim.kind == ClaimKind.NUMERIC`. `classify`'s cascade is
    # NON_CLAIM -> RELATIONAL -> ABSENCE -> NUMERIC, so a figure inside a causal
    # sentence is kind RELATIONAL and never reached here. Before ADR-007 the
    # relational branch ran `numeric_ok` itself (R10C-04); ADR-007 deleted that
    # branch and I did not re-home the check, so for a few hours the gate
    # certified a fabricated monetary figure at PASS 100.0 / exit 0 while
    # PRINTING `figure_not_in_cited_sources` in the same record:
    #
    #   "The 2019 federal review of interbank settlement latency across the
    #    eurozone causes a 3.7 million euro shortfall [S1][S2]."
    #
    # The deeper defect is the gating itself, and it predates ADR-007: a figure
    # is a figure whatever sentence it sits in. So this check no longer asks
    # what KIND the claim is — every claim THAT REACHES HERE and carries a
    # figure must have it present in a cited source. Strictly fail-closed: it
    # can only move claims away from PASS.
    #
    # SCOPE, CORRECTED 2026-10-02 (R14-06, R14-03). An earlier version of this
    # comment said "an ABSENCE claim carrying a figure skipped this check too",
    # in the past tense, and ADR-007 shipped the same sentence. That overstated
    # D-77 and the same text reached the ADR: **ABSENCE and RELATIONAL return
    # ABOVE this line and so never reach it.** "Kind-independent" is true only
    # of the claims that arrive here at all.
    #
    # Demonstrated, not inferred (R14-03a): the digit 4200 appearing in NO
    # source text certifies `ABSENCE_SUPPORTED` at PASS 100.0 / exit 0, because
    # numeric_ok is unreachable from the absence branch. Tripwired in
    # tests/red_team_moat/test_moat_r14_hedge_classifier_absence.py and
    # registered J-71 — NOT fixed here, because moving these two checks above
    # the kind dispatch changes which claims can pass and is Escalation #1.
    if claim.numeric_tokens and not numeric_ok(claim, verbatim):
        return Verdict.UNVERIFIED_NUMBER

    # The same hole, for a figure spelled in words (J-43). `spelled_quantity_ok`
    # lived only in the deleted relational branch, so after ADR-007 it was
    # reachable from nothing at all.
    if not spelled_quantity_ok(claim, verbatim):
        return Verdict.UNVERIFIED_NUMBER

    # T2 IS NO LONGER CONSULTED HERE (ADR-006, 2026-09-02). T1 alone certifies.
    #
    # T2 scored lexical overlap, and overlap is not support. Two measurements
    # ended the question. (a) Matched pairs: a true claim and a false one can be
    # the SAME one-token delta against the same source and score an IDENTICAL
    # t2_f1 — 5 pairs, 5 ties (tests/red_team_moat/test_moat_oi_moat_21.py), so
    # no lex_tau orders them and none ever could. (b) Reordering: a bag of words
    # has no word order, so reciting a source's whole vocabulary in a FALSE
    # order scored f1=1.000 (round 5). A tier that cannot distinguish a claim
    # from its inversion cannot be sufficient for GROUNDED.
    #
    # Why not the coverage repair (require the source to contain every claim
    # token) — it measured better (Error-A 0.240 vs 0.320): it closes the
    # argument-swap class but leaves REORDERING wide open, because a reordering
    # introduces no new token. Verified by mutation: the round-5 tripwire still
    # XFAILs under it. The two options are not nested, and demotion is the only
    # one that closes both. Error-B is unrecoverable; Error-A is not.
    #
    # The Error-A this costs is real and measured, not waved away: honest
    # paraphrase now reads UNGROUNDED (see tests/honest_drafts/). Recovering it
    # needs a tier that reads MEANING rather than counting words — T3/NLI,
    # ADR-004 — which is the only mechanism that can separate a synonym
    # substitution from an argument substitution. Until it exists, the gate is
    # deliberately stricter than it is smart.
    if t1_verbatim(claim, verbatim):
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


# ---------------------------------------------------------------------------
# Evidence basis — what the gate consulted, in a sentence (OI-UX-01)
# ---------------------------------------------------------------------------

def _plural(n: int, one: str, many: str) -> str:
    """Return *one* when n == 1 else *many*. Pure."""
    return one if n == 1 else many


def _absence_figure_note(claim: Claim) -> str:
    """J-82 (2026-10-03): an absence claim carrying a figure can be refused by
    the FIGURE check, not by the search rules — and the basis described only the
    search rules.

    Reproduced: "There is no fatality record for the 4200 aviation deaths."
    against a store whose searches DO qualify returns `UNVERIFIED_NUMBER`, while
    the explanation listed the queries, the scope rule and the head-noun rule —
    none of which refused it. A reader would go and improve their searching. The
    D-35 class: a display describing a code path the verdict did not take.

    Stated UNCONDITIONALLY for any absence claim bearing a figure, so this needs
    no knowledge of the verdict. Display must not consult the decision (D-34),
    and a note that is true either way cannot contradict one.

    Pure.
    """
    if not claim.numeric_tokens:
        return ""
    quoted = ", ".join(f'"{tok}"' for tok in claim.numeric_tokens)
    return (
        f" This claim also asserts {len(claim.numeric_tokens)} "
        f"{_plural(len(claim.numeric_tokens), 'figure', 'figures')}: {quoted}. "
        f"A figure that appears in no retrieved verbatim source refuses the "
        f"claim on its own, whatever the search record shows — and a model, "
        f"standard or version number is read as a figure."
    )


def evidence_basis(claim: Claim, store: dict[str, RetrievedSource]) -> str:
    """Return a plain sentence naming what the gate CONSULTED for *claim*.

    This is a display function, not a decision function. It reports the
    inputs a verdict was computed over; it never computes, alters or implies
    a verdict, and nothing in ``ground``'s call tree consults it.

    **The defect it closes (OI-UX-01).** Every surface in this project that
    showed evidence rendered the ABSENCE of evidence as either an empty cell
    or an internal token — ``""`` for an uncited claim, ``[NOT IN STORE]``
    for a fabricated citation, a bare query list for an absence claim. All
    three read as *the tool broke*, not as *the tool looked and there was
    nothing there*, and those two readings are opposite verdicts on the
    gate's trustworthiness. The project's own author stalled on 6 of 20
    calibration rows on 2026-09-12 — every one of them a row whose evidence
    reads as absent — and asked "nothing here?". A stranger reading a
    grounding report has strictly less context than he did.

    The rule this function applies, and which every future evidence surface
    must apply: **state what was consulted and what was found, as an
    assertion.** Never render the absence of a thing by showing nothing.

    **Branch coverage is INCOMPLETE and the contract is stated honestly.**
    An earlier version of this docstring claimed the branch order "mirrors
    ``ground``'s exactly, so the basis can never describe a path the verdict
    did not take". **That claim was FALSE when written** (round 8, R8C-11):
    ``ground`` dispatches RELATIONAL to ``ground_relational`` before anything
    below, and this function has no RELATIONAL branch, so every relational
    claim falls through to the citation branches and is misdescribed —
    including a two-source claim whose basis reports "2 cited sources" in the
    row whose verdict exists precisely because only one of them carried the
    link.

    Known-wrong outputs, tripwired in
    ``tests/red_team_moat/test_moat_r8_display.py`` and OPEN:
      * RELATIONAL claims (no branch) — R8C-11.
      * ``query_provenance`` is interpolated RAW, so store-controlled text can
        speak in the gate's own voice — R8C-04.
      * the query count can differ from the set ``check_absence`` used
        (case / NFKC / empty-string divergence) — R8C-06, R8C-09.

    Until those close, read this field as *indicative*, never as an audit
    record. A display that is wrong is worse than one that is absent, and the
    previous docstring asserted a guarantee the code did not provide.

    **Deliberately NOT shared with the calibration scaffold**
    (``build_corpus._evidence_text``). The haiku_summary branch below states
    the governing POLICY outright, which is right for a user who must act on
    a verdict and wrong for a labeller whose agreement is being measured: a
    display that tells the rater the answer makes reliability measure
    rule-reading (Goodhart). Two surfaces, opposite requirements. See D-34,
    which quarantined those same rows out of kappa rather than explaining
    them.

    Pure function — no LLM, no network, no random, no wall-clock; does not
    mutate *claim* or *store*.
    """
    if claim.kind == ClaimKind.NON_CLAIM:
        return ("Not scored: this line was not classified as a factual claim, "
                "so no evidence was sought for it.")

    if claim.kind == ClaimKind.ABSENCE:
        queries = _session_queries(store)
        n_src = sum(1 for s in store.values() if s.text)
        if not queries:
            # J-56, the SIBLING: the same overclaim as the citation branch
            # above. Without --session-id the gate cannot say "this session";
            # it can only speak about the store it was handed. Found by the
            # AST guard after the first instance was fixed, which is the point
            # of having the guard rather than a grep.
            return ("The evidence store recorded NO search queries. An absence "
                    "claim is substantiated by searches that were actually "
                    "run, and there are none to show.")
        # J-45 (2026-10-02): this listing used to end at the queries, which
        # read as "all of these counted". They do not. check_absence narrows
        # them twice before anything is certified — by the claim's SCOPE
        # (OI-ABS-01: to establish absence FROM a domain you must have looked
        # IN it) and then by requiring the subject's head noun, plus a
        # corroborating content word when the subject is specific.
        #
        # So a user reading "3 distinct search queries" next to a REFUSAL had
        # no way to see that only one of the three was eligible, which is
        # precisely the information needed to fix the draft. That is the D-35
        # class: a display that states something the verdict does not.
        #
        # WHY THIS DOES NOT RECOMPUTE THE COUNT. Re-deriving match_count here
        # would put the absence rule in two places, and two copies of a moat
        # rule diverge — the failure this file has already paid for. The
        # display's job is to report what was CONSULTED and to name the rule
        # that narrows it; the verdict remains the single authority on how many
        # qualified. Display must never become decision (D-34).
        listed = "; ".join(f'"{q}"' for q in queries)
        return (f"An absence claim is checked against what was SEARCHED, not "
                f"what was cited. Complete record consulted: "
                f"{len(queries)} distinct search "
                f"{_plural(len(queries), 'query', 'queries')} and the text of "
                f"{n_src} retrieved {_plural(n_src, 'source', 'sources')}. "
                f"The {_plural(len(queries), 'query was', 'queries were')}: "
                f"{listed}. NOTE: this is the complete record consulted, not "
                f"the set that counted. A query counts toward the minimum only "
                f"if it addresses the claim's asserted SCOPE and carries the "
                f"subject's head noun, so fewer of the above may have "
                f"qualified than are listed.{_absence_figure_note(claim)}")

    if not claim.citations:
        n_src = len(store)
        return (f"No source is cited, so the gate had nothing to check this "
                f"claim against. The store holds {n_src} retrieved "
                f"{_plural(n_src, 'source', 'sources')}; none was named by "
                f"this claim. This is an uncited claim, NOT a retrieval "
                f"failure.")

    missing = [_nfkc(c).strip().strip("[]")
               for c in claim.citations if resolve(c, store) is None]
    if missing:
        n_src = len(store)
        # J-56: this used to say "NEVER RETRIEVED this session". It cannot know
        # that — the store is session-bounded only when the caller passes
        # --session-id, and evidence_basis is not told whether they did. All the
        # gate knows here is that the id is absent from the store. Found by a
        # real `claude -p` session running /assure-verify, which noticed the
        # overclaim in its own output; it is the same claim CLAIM-1 retired from
        # the four shipped surfaces, surviving one layer down in runtime text.
        return (f"{', '.join(missing)} "
                f"{_plural(len(missing), 'is', 'are')} cited but "
                f"{_plural(len(missing), 'is', 'are')} NOT IN THE EVIDENCE "
                f"STORE. The store holds {n_src} "
                f"{_plural(n_src, 'source', 'sources')} and does not contain "
                f"{_plural(len(missing), 'it', 'them')}, so nothing exists to "
                f"check the claim against.")

    sources = [resolve(c, store) for c in claim.citations]
    empty = [s.source_id for s in sources if not s.text]
    if empty:
        return (f"{', '.join(empty)} "
                f"{_plural(len(empty), 'was', 'were')} retrieved but captured "
                f"no full text (snippet only), so there is no text to match "
                f"the claim against.")

    summaries = [s.source_id for s in sources
                 if s.full_text_source != "verbatim"]
    verbatim = [s for s in sources if s.full_text_source == "verbatim"]
    if not verbatim:
        return (f"{', '.join(summaries)} "
                f"{_plural(len(summaries), 'was', 'were')} captured as an "
                f"AI-generated SUMMARY, not the source's own words. "
                f"Agent-Assure never grounds a claim on a summary, whatever "
                f"the summary says — the words checked would be the "
                f"summariser's, not the source's.")

    checked = ", ".join(f"{s.source_id} ({len(s.text)} chars)"
                        for s in verbatim)
    note = ""
    if summaries:
        note = (f" {', '.join(summaries)} "
                f"{_plural(len(summaries), 'was', 'were')} also cited but is "
                f"an AI summary and was excluded.")
    # J-72 (display half, 2026-10-03). A figure refusal used to read only
    # "Checked verbatim against 1 cited source: S1 (70 chars)." — the user was
    # told a number failed but never WHICH number, and the commonest cause is
    # not a number at all: `X200` yields the token `200`, `ISO 27001` yields
    # `27001`, and 20/20 tested identifiers do the same (round 16, R16-05). A
    # reader who sees `200` listed beside their claim about the X200 drone
    # diagnoses it instantly; a reader shown `UNVERIFIED_NUMBER` cannot.
    #
    # NARROWING THE REFUSAL ITSELF IS **NOT** MINE: dropping `200` from
    # numeric_tokens turns a refusal into a pass, which is PASS-ENABLING and
    # Escalation #1 (J-72, owner Sai). So the refusal stays and becomes legible.
    #
    # DELIBERATELY DOES NOT SAY WHICH FIGURE FAILED. That would re-derive
    # numeric_ok's value+unit+rate-qualifier rule in the display layer, and two
    # copies of a moat rule diverge — the reason J-45 was fixed by removing
    # false precision rather than by recomputing a count. Listing what the claim
    # ASSERTS is read-only and duplicates nothing.
    figures = ""
    if claim.numeric_tokens:
        quoted = ", ".join(f'"{tok}"' for tok in claim.numeric_tokens)
        figures = (
            f" The claim asserts {len(claim.numeric_tokens)} "
            f"{_plural(len(claim.numeric_tokens), 'figure', 'figures')}: "
            f"{quoted} — each must appear in a cited source with the same "
            f"value, unit and rate qualifier."
        )
        # THE IDENTIFIER NOTE IS UNCONDITIONAL, after a conditional version was
        # written and withdrawn in the same sitting (2026-10-03).
        #
        # The gate was `[A-Za-z]\d|\d[A-Za-z]` — a digit against a letter. It
        # fired on `100K`, an ordinary quantity, and MISSED `iPhone 15` and
        # `ISO 27001`, which are space-separated. Over- and under-inclusive at
        # once, which is precisely J-72's own difficulty and the reason J-72 is
        # an open job owned by Sai rather than a tidy-up. **Distinguishing an
        # identifier from a quantity is the hard problem; it does not get easier
        # because the answer is only being displayed.**
        #
        # So the note states a FACT about the extractor rather than a judgement
        # about this sentence. Always true, never a false positive, and it still
        # gives a reader staring at `"200"` the insight they need.
        figures += (
            " Figures are extracted from the sentence as written, so a model, "
            "standard or version number (X200, ISO 27001, 5G) is read as a "
            "figure too and must then be found in a source."
        )
    return (f"Checked verbatim against {len(verbatim)} cited "
            f"{_plural(len(verbatim), 'source', 'sources')}: {checked}."
            f"{note}{figures}")


# ======================================================================
# A DRAFT MAY NOT CERTIFY ITSELF (J-83, 2026-10-03).
#
# FOUND BY ACCIDENT, NOT BY AN ADVERSARY. The capture hook's matcher includes
# `Read`, so an agent reading the draft it is about to verify captures that
# draft AS A SOURCE. Add a citation to it and the gate checks the draft against
# its own text: gate PASS, score 100.0, exit 0, verdict GROUNDED. Reproduced
# 2026-10-03 against the store Sai's live J-54 plugin test wrote.
#
# `--session-id` DOES NOT CLOSE THIS, and that is the uncomfortable part: the
# draft genuinely was retrieved this session, so session scoping is satisfied by
# a self-citation. Reading one's own draft is ordinary behaviour, which makes
# this reachable without any attacker at all.
#
# WHY UNGROUNDABLE AND NOT A NEW VERDICT. The taxonomy is closed (a new state
# needs an ADR first) and `UNGROUNDABLE` already means "the cited evidence
# exists but cannot ground anything" — which is exactly the summary case. A
# self-source is the same shape: present in the store, incapable of certifying.
# So this mirrors the haiku_summary narrowing rather than inventing a state or
# stretching UNVERIFIED_CITATION, whose documented meaning is that the marker is
# ABSENT from the store.
#
# A claim citing the draft AND a real source still grounds on the real one; only
# the self-source is removed from the certifying set. Strictly fail-closed.
#
# WHAT THIS DOES NOT CLOSE — say it here so no future reader conflates them.
# **J-35's general write-then-Read laundering is untouched and remains Sai's
# (Escalation #4).** Write fabricated claims to a DIFFERENT file, Read it, cite
# it: the path differs from the draft's and so does the digest, so nothing here
# fires. This closes the degenerate self-citation case only.
#
# CEILING: `self_source_ids` defaults to EMPTY, so a library caller that does
# not pass it gets no protection. The CLI always passes it. That default is
# fail-OPEN, chosen because a function given no draft identity cannot
# distinguish "no self-citation" from "I was not told" — and refusing every
# claim on that basis would be worse. Upgrade path: make the parameter required
# once every in-repo caller is updated.
def _identity_digest(text: str) -> str:
    """Digest of *text* for IDENTITY comparison: NFKC, citation markers removed,
    whitespace collapsed, casefolded.

    Deliberately coarser than `content_sha256`, which must stay an exact digest
    of what was captured. This one answers a different question — "is this the
    same document?" — where a trailing newline, a reflow or a CRLF is not a
    difference. Coarser means it matches MORE records, so it can only refuse
    more claims: fail-closed by construction. Pure.
    """
    normalised = _nfkc(_strip_citations(text)).strip()
    return hashlib.sha256(normalised.encode("utf-8")).hexdigest()


def _self_source_ids(
    draft_path: str, draft_text: str, store: dict[str, RetrievedSource]
) -> frozenset[str]:
    """Return ids of sources that ARE the draft, by resolved path or by digest.

    Pure. Two independent tests, because either can be defeated alone: a path
    comparison misses a copy of the draft captured from elsewhere, and a digest
    comparison misses a draft edited after capture.
    """
    try:
        draft_resolved = str(Path(draft_path).resolve())
    except (OSError, ValueError):
        # R17-02: pathlib raises ValueError (not OSError) on a NUL byte, which
        # escaped this handler and crashed the gate. A crash is worse than any
        # verdict: it takes down the whole run and bypasses the fail-loud
        # contract, which promises an error naming the offending line or key.
        draft_resolved = ""
    # STRIP CITATIONS BEFORE HASHING. Measured 2026-10-03, not assumed: the
    # captured source text is the draft WITHOUT markers, because the agent read
    # the draft before any marker was added — and even when markers are present
    # they are the gate's own annotation, not content. The gate strips them
    # before tokenizing everywhere else; the identity test compares the same
    # thing. Hashing the raw draft misses the realistic case by exactly one
    # bracketed token, which is how the first version of this check silently
    # failed to fire.
    # R19-01 (2026-10-03): THE DIGEST WAS EXACT-BYTE AND ONE NEWLINE DEFEATED IT.
    # A copy of the draft with no trailing newline certified itself at PASS
    # 100.0 / exit 0, because stripping citations removes the MARKER and not
    # the whitespace, so "…newer." != "…newer.\n". The same held for a trailing
    # space, CRLF, or any reflow. Comparing a normalised, whitespace-collapsed
    # form instead turns "one byte" into "one word" — still fail-closed,
    # because collapsing can only make MORE records match and refuse MORE
    # claims, never fewer.
    draft_digest = _identity_digest(draft_text)
    matched: set[str] = set()
    for source_id, source in store.items():
        if source.file_path:
            try:
                # R19-02: `resolve()` follows symlinks but does NOT fold case on
                # a case-insensitive volume (APFS), and cannot see a HARDLINK —
                # both let the same file through under another name.
                # `os.path.samefile` compares (st_dev, st_ino) and catches both.
                # It needs BOTH files to exist, so the string compare stays as
                # the fallback for a path recorded from a file since deleted.
                if os.path.exists(source.file_path) and os.path.exists(draft_path) \
                        and os.path.samefile(source.file_path, draft_path):
                    matched.add(source_id)
                    continue
                if str(Path(source.file_path).resolve()) == draft_resolved:
                    matched.add(source_id)
                    continue
            except (OSError, ValueError):
                pass  # R17-02, as above: a NUL byte raises ValueError.
        # R17-03: the stored digest is NEVER recomputed against `text` (J-32),
        # so trusting it alone lets a record whose text IS the draft escape by
        # carrying a forged `content_sha256` and a different path. Hash the
        # source's OWN TEXT as well. Both tests are ORs, so this can only match
        # more records and refuse more claims — strictly fail-closed, and it
        # does not depend on J-32 ever being fixed.
        if source.content_sha256 and source.content_sha256 == draft_digest:
            matched.add(source_id)
            continue
        if source.text and _identity_digest(source.text) == draft_digest:
            matched.add(source_id)
    return frozenset(matched)


# ======================================================================
# THE SUPPORT DIAGNOSTIC (J-74, 2026-10-03) — A MEASUREMENT, NEVER A VERDICT.
#
# WHAT IT REPORTS. For a claim that cites a verbatim source, it finds the
# sentence in that source with the greatest content-word overlap with the claim
# — the sentence the claim is effectively resting on — and reports whether that
# sentence carries an attribution, denial or conditional token. "We found no
# evidence that X" fires. "X happened in three regions" does not.
#
# WHY IT IS NOT A VERDICT, AND MUST NEVER BECOME ONE. The thing it approximates
# is entailment, and the state of the art at entailment is 65-75% balanced
# accuracy (MiniCheck-FT5 74.7, GPT-4 75.3 on LLM-AggreFact, EMNLP 2024;
# HHEM-2.1-Open 64.4/74.3 on RAGTruth). Godbole & Jia (arXiv 2501.14883) find
# SOTA evaluators disagree per instance and miss close paraphrases. A token
# scan is cruder still. **Gating on it would manufacture Error-A at scale while
# still missing cases** — so it reports, and `ground()` never sees it. ADR-008.
#
# WHY IT CAN BE SENTENCE-SCOPED WHERE `_span_is_hedged` CANNOT. That function
# receives a TOKEN LIST, and `_tokenize` strips punctuation, so sentence
# boundaries are unrecoverable inside it (measured 2026-10-02 — this is the
# reason J-70's narrow repair cannot be written at that layer). This runs on the
# RAW source text, which still has its full stops.
#
# WHY IT REUSES `_SPAN_HEDGE_TOKENS` RATHER THAN A NEW LIST. A new lexicon would
# own new gaps, and this project has paid for one of those already (J-44's stem,
# D-69). The vocabulary is not what is wrong with the verdict path; the SCOPE
# is. Chesterton's Fence: change one thing.
#
# CEILING: a token scan cannot tell "the study found no link" from "no study
# found a link" — both fire. It over-flags by construction, which is the safe
# direction for a REPORT (nothing is refused because of it) and the wrong
# direction for a verdict. Its false-positive rate on `tests/honest_drafts/`
# and on the n=52 gold corpus is published in CR-009 rather than tuned away:
# tuning a signal nobody has re-validated is how 2026-10-02 went. Upgrade path
# is J-70, which is Sai's (Escalation #1).
SUPPORT_NO_CITED_SOURCE = "no_cited_verbatim_source"
SUPPORT_SENTENCE_MAY_NOT_ASSERT = "cited_sentence_may_not_assert_claim"
SUPPORT_NO_HEDGE_FOUND = "no_hedge_in_cited_sentence"


def _most_overlapping_sentence(claim_text: str, source_text: str) -> str:
    """Return the sentence of *source_text* sharing most content words with the claim.

    Empty string when the source has no sentences. Ties go to the first, which
    is arbitrary but deterministic — and determinism is the point: this function
    must return the same answer on the same bytes forever. Pure.
    """
    claim_words = set(_content_words(_tokenize(_strip_citations(claim_text))))
    best, best_score = "", -1
    for sentence in _split_sentences(source_text):
        overlap = len(claim_words & set(_content_words(_tokenize(sentence))))
        if overlap > best_score:
            best, best_score = sentence, overlap
    return best


def support_diagnostic(claim: Claim, store: dict[str, RetrievedSource]) -> str:
    """Report whether the cited sentence appears to ASSERT the claim. Pure.

    DIAGNOSTIC ONLY. No verdict path may reference this function; an AST guard
    in tests/test_support_diagnostic.py enforces it, exactly as one does for
    evidence_basis (D-34: display must never become decision).
    """
    cited = [
        source for source in (resolve(c, store) for c in claim.citations)
        if source is not None
        and source.full_text_source == "verbatim"
        and source.text
    ]
    if not cited:
        return SUPPORT_NO_CITED_SOURCE
    for source in cited:
        sentence = _most_overlapping_sentence(claim.text, source.text)
        if not sentence:
            continue
        # J-79 (2026-10-03): A HEDGE WORD THE CLAIM ITSELF USES IS SHARED
        # VOCABULARY, NOT EVIDENCE THE SOURCE IS HEDGING.
        #
        # `per` is in `_SPAN_HEDGE_TOKENS` (for "per the vendor"), so every
        # claim about "operations per second" matched a source about
        # "operations per second" and fired — a flag for the wrong reason, and
        # it was inflating the published false-alarm rate.
        #
        # WHY NOT JUST REMOVE `per` FROM THE LEXICON: that set also feeds
        # `_span_is_hedged`, which is IN THE VERDICT PATH, and removing a hedge
        # token makes T1 certify MORE. That is PASS-ENABLING and Escalation #1,
        # so the lexicon is untouched and only this DISPLAY consumer narrows.
        #
        # WHY NOT A SECOND LEXICON: two copies of a word list diverge, and this
        # file has paid for that (J-44, D-69). This needs no list — it is a
        # relation between the claim and the sentence, computed from both.
        #
        # MEASURED before landing, both directions: false alarms on claims the
        # gate passes **4/15 → 0/15**, recall on the 14-vector denial set
        # **unchanged at 7/14**, positive control clean. **"0/15" is a rate on
        # fifteen rows, not a claim that no false alarm exists** — the corpus
        # cannot represent shapes nobody labelled.
        claim_tokens = set(_tokenize(_strip_citations(claim.text)))
        hedges = set(_tokenize(sentence)) & _SPAN_HEDGE_TOKENS
        if hedges - claim_tokens:
            return SUPPORT_SENTENCE_MAY_NOT_ASSERT
    return SUPPORT_NO_HEDGE_FOUND


# ======================================================================
# THE SCOPE STATEMENT (J-73, 2026-10-03). Every report carries it.
#
# WHY IT IS IN THE PRODUCT AND NOT IN THE README. Ding et al. (AAAI 2025)
# measured that user trust RISES when output carries citations **even when the
# citations are random**, and falls only when users actually check them. So a
# PASS verdict buys unearned trust by default, and a disclosure the reader never
# opens does not spend it back. Magesh et al. (Stanford, JELS) is what happens
# to an unqualified claim: it quotes a vendor's "100% hallucination-free linked
# legal citations" beside a measured 17-33% hallucination rate.
#
# WHAT IT MUST NOT SAY. "this session" is a claim about SCOPE, and the gate can
# only make it when --session-id was passed (J-56: evidence_basis once said
# "NEVER RETRIEVED this session" about a store it had no session information
# for). So there are two variants and the caller's scoping decides which. The
# unscoped one is the weaker, truthful statement.
#
# Deliberately NOT the word "verified" and NOT "grounded" unqualified, anywhere.
_SCOPE_SESSION = (
    "PASS means every claim in this draft is traceable to text in a source "
    "retrieved this session; it does not mean the source agrees with the "
    "claim, and a source that denies or hedges a claim can still satisfy this "
    "check."
)
_SCOPE_STORE = (
    "PASS means every claim in this draft is traceable to text in a source "
    "present in the evidence store supplied to this run; it does not mean the "
    "source agrees with the claim, and a source that denies or hedges a claim "
    "can still satisfy this check. Session scope is NOT asserted: pass "
    "--session-id to require that the sources were retrieved this session."
)


def scope_statement(session_scoped: bool) -> str:
    """Return the scope statement matching what this run can actually claim.

    Pure. `session_scoped` is True only when the caller passed --session-id,
    which is the only circumstance under which the gate knows the store belongs
    to one session.
    """
    return _SCOPE_SESSION if session_scoped else _SCOPE_STORE


def score_report(
    claims: list[Claim],
    store: dict[str, RetrievedSource],
    threshold: float = 90.0,
    lex_tau: float = _LEX_TAU_DEFAULT,
    session_scoped: bool = False,
    self_source_ids: frozenset[str] = frozenset(),
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
    2026-07-12; closes the threshold-dilution vector, OI-MOAT-02/-006). The
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
              {"index": int, "text": str, "kind": str, "verdict": str,
               "evidence_basis": str}, ...
          ],
          "retained_appendix": [               # non-grounded SCORED claims only
              {"index": int, "text": str, "verdict": str,
               "evidence_basis": str}, ...
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
        verdict = ground(claim, store, lex_tau, self_source_ids)
        entry = {
            "index": claim.index,
            "text": claim.text,
            "kind": claim.kind.value,
            "verdict": verdict.value,
            "evidence_basis": evidence_basis(claim, store),
        }
        # ADR-007: the relational corroboration result is INFORMATION, not a
        # verdict. It is reported so a human can see what the two-source rule
        # would have said, and it is deliberately NOT consulted by `ground` —
        # pinned by an AST guard, because a diagnostic that creeps back into
        # the verdict path is how a demotion silently un-demotes itself.
        if claim.kind == ClaimKind.RELATIONAL:
            entry["relation_diagnostic"] = relational_diagnostic(claim, store)
        # J-74: emitted for EVERY claim, not gated on kind. A check gated on a
        # classifier branch is a check an author routes around by adding one
        # word — that was R14-01, and D-77 learned it the expensive way.
        # J-83 sibling (FMEA): the DIAGNOSTIC must not compare the draft to
        # itself either, or it reports "no hedge in the cited sentence" about
        # the draft's own prose. Passing a store without the self-sources is
        # safe here because this function only READS cited sources; it is not
        # the store-shrinking trap of D-54, which applies to check_absence's
        # two-argument path.
        entry["support_diagnostic"] = support_diagnostic(
            claim,
            {k: v for k, v in store.items() if k not in self_source_ids},
        )
        per_claim.append(entry)

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
                "evidence_basis": evidence_basis(claim, store),
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
        # J-73: the report states its own scope. Additive and display-only —
        # nothing reads it back, and no verdict consults it.
        "scope": scope_statement(session_scoped),
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
      --session-id STR  Assert every record was captured in this session; the
                        gate REFUSES a store containing any other session's
                        evidence (J-38). Omitted => no session enforcement.

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
    parser.add_argument("--lex-tau", type=float, default=None,
                        metavar="FLOAT", dest="lex_tau",
                        help="RETIRED (ADR-006). T2 no longer decides any "
                             "verdict, so this value governs nothing. Passing "
                             "it is an error rather than a no-op: a flag that "
                             "silently does nothing is the silent-fallback "
                             "failure this codebase forbids.")
    parser.add_argument("--session-id", dest="session_id", default=None,
                        metavar="STR",
                        help="Assert every record was captured in this session; "
                             "REFUSE a store containing another session's "
                             "evidence (J-38). Omit for no enforcement.")
    parser.add_argument("--json", dest="json_mode", action="store_true",
                        help="Print JSON report to stdout; skip writing YAML file.")
    args = parser.parse_args()

    # Fail loud, never no-op. Before ADR-006 this flag moved the T2 operating
    # point; T2 now decides nothing, so honouring it would be a lie and
    # ignoring it would be a silent fallback. Both are worse than an error that
    # says what changed.
    if args.lex_tau is not None:
        parser.error(
            "--lex-tau is RETIRED (ADR-006, 2026-09-02). T2 was demoted from "
            "sufficient-for-GROUNDED, so no verdict depends on a lexical "
            "threshold and this value would change nothing. Re-run without it. "
            "Paraphrase recovery is the T3/NLI tier's job (ADR-004)."
        )

    # Pipeline: read → decompose → classify → score_report
    with open(args.draft, encoding="utf-8") as fh:
        draft_text = fh.read()

    store = load_store(args.store)
    # J-38: enforce BEFORE any scoring, so a foreign-session store never
    # produces a verdict at all. Raising here rather than filtering is
    # deliberate — see assert_single_session.
    if args.session_id is not None:
        assert_single_session(store, args.session_id)
    claims = [classify(c) for c in decompose(draft_text)]
    report = score_report(
        claims, store, threshold=args.threshold,
        session_scoped=args.session_id is not None,
        self_source_ids=_self_source_ids(args.draft, draft_text, store),
    )

    gate: str = report["gate"]

    if args.json_mode:
        # Print JSON to stdout; sort_keys for determinism.
        print(_json.dumps(report, sort_keys=True))
    else:
        # Write grounding-report.yaml to CWD.
        with open("grounding-report.yaml", "w", encoding="utf-8") as fh:
            _yaml.safe_dump(report, fh, sort_keys=True, allow_unicode=True)
        # One-line human summary to stdout, PLUS the scope statement (J-73).
        # The human path is the one a person actually reads, so the disclosure
        # has to be here and not only in the file. Printed on every verdict,
        # not just PASS: a reader deciding whether to trust a FAIL needs to
        # know what the check does and does not cover just as much.
        print(f"gate={gate} grounding_score={report['grounding_score']}")
        print(report["scope"])

    _sys.exit(0 if gate == "PASS" else 1)


if __name__ == "__main__":
    main()
