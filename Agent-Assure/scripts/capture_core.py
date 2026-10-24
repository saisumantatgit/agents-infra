"""Agent-Assure Phase 1b — Tasks 1 & 2: EvidenceStore capture hook.

make_record(tool_name, tool_input, tool_response, source_id, query_provenance,
            fetched_at) -> RetrievedSource | None

Returns a RetrievedSource for retrieval tools; None for non-retrieval tools.
No network, no wall-clock, no random.  Reading an overflow file referenced
inside the tool_response dict IS permitted (that is the whole point of Task 2).

# LIVE-VALIDATED tool_response shapes (2026-07-03, real headless Claude Code
# session; raw PostToolUse stdin payloads captured via a tap hook — regression
# fixtures in tests/test_live_shapes.py):
#
# Read (native):
#   {"type": "text", "file": {"filePath": str, "content": str, "numLines": int,
#    "startLine": int, "totalLines": int[, "truncatedByTokenCap": true]}}
#   - content is RAW file text — NO cat-n line-number prefixes (the prefixes
#     exist only in the model-rendered view, never in the hook payload).
#   - Large results truncate INLINE: content is cut at the token cap and
#     truncatedByTokenCap=true with numLines < totalLines. No temp-file
#     offload shape was observed. The store holds exactly what was delivered
#     (= what the model saw this session), which is the correct grounding set.
#   - file_path: file.filePath (absolute), else tool_input["file_path"]
#     resolved with ~ and the event cwd (W2D-01); read_extent from the counts.
#
# WebFetch (native):
#   {"bytes": int, "code": int, "codeText": str, "result": str,
#    "durationMs": int, "url": str}
#   - HARD SPEC: full_text_source must be "haiku_summary" regardless of shape.
#     The native WebFetch tool always returns a Haiku-summarized form, never verbatim.
#
# mcp__exa__web_fetch_exa / web_fetch_exa:
#   TOP-LEVEL MCP content-block list: [{"type": "text", "text": str, "_meta": {...}}]
#   (Exa caps page content server-side; no harness-level truncation observed.)
#
# mcp__ddg-search__fetch_content:
#   plain str (verbatim fetched page content).
#
# mcp__ddg-search__search:
#   - Returns snippets (not full page content) → None (not a retrieval tool).
#
# Any other tool (Bash, Edit, Write, Grep, WebSearch, etc.) → None.
#
# Pre-validation fallback shapes (str / dict-"text" / dict-"content") are kept:
# they are harmless, cover older payload variants, and keep the extractor
# permissive across harness versions. The assumed overflow shape
# {"preview", "file_path"} was NOT observed live; its fail-loud path is kept
# as a defensive guard (see _is_overflow_payload).
"""

from __future__ import annotations

import dataclasses
import hashlib
import json
import os
import re
import unicodedata
from pathlib import Path

from scripts.ground_check import RetrievedSource


# ---------------------------------------------------------------------------
# Retrieval tool registry
# ---------------------------------------------------------------------------

# Tools that return verbatim full-page or full-file content.
_VERBATIM_TOOLS: frozenset[str] = frozenset({
    "mcp__exa__web_fetch_exa",
    "web_fetch_exa",
    "Read",
    "mcp__ddg-search__fetch_content",
})

# Tools that return Haiku-summarized content (not verbatim).
_HAIKU_SUMMARY_TOOLS: frozenset[str] = frozenset({
    "WebFetch",
})

# All recognized retrieval tools (union of the above).
_RETRIEVAL_TOOLS: frozenset[str] = _VERBATIM_TOOLS | _HAIKU_SUMMARY_TOOLS


def is_retrieval_tool(tool_name: str) -> bool:
    """Return True iff *tool_name* is a recognized retrieval tool.

    Public predicate so the hook entry can distinguish "a retrieval tool fired
    but carried no usable response" (worth a distinct diagnostic) from a
    non-retrieval tool (silently ignored) without importing the private registry.
    """
    return tool_name in _RETRIEVAL_TOOLS


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _coerce_text_value(value: object) -> str:
    """Coerce a 'text'/'content' value to a string, FAIL-LOUD on shape drift.

    - a plain ``str`` is returned as-is;
    - the standard MCP content-block list — ``[{"type": "text", "text": "..."}, …]``,
      the most common live tool-result envelope — is normalized by concatenating
      the ``text`` fields of its blocks (the genuine retrieved content);
    - anything else (an int, a list of non-text blocks, an empty list) raises
      ``TypeError`` so the mismatch trips the hook's distinct 'capture skipped'
      diagnostic rather than being silently ``str()``-coerced (repr) into the
      verbatim store. (CLAUDE.md: raise errors explicitly — no silent fallbacks.)
    """
    if isinstance(value, str):
        return value
    if isinstance(value, list):
        parts: list[str] = []
        for block in value:
            if isinstance(block, dict) and isinstance(block.get("text"), str):
                parts.append(block["text"])
            else:
                raise TypeError(
                    "Unrecognized content-block in text/content list: "
                    f"{type(block).__name__!r}. Expected {{'type':'text','text':str}}. "
                    "Flag as TASK-4-VALIDATION — live response shape must be verified."
                )
        if not parts:
            raise TypeError(
                "Empty content-block list — no text blocks to store. "
                "Flag as TASK-4-VALIDATION."
            )
        return "\n".join(parts)
    raise TypeError(
        f"Non-string text/content value: {type(value).__name__!r}. "
        "Expected str or an MCP content-block list. "
        "Flag as TASK-4-VALIDATION — live response shape must be verified."
    )


def _extract_text(tool_response: object) -> str:
    """Extract the text content from a tool response.

    Handles every LIVE-VALIDATED shape (2026-07-03; see module docstring) plus
    the pre-validation fallbacks, in this order:

      - plain str: returned as-is (LIVE: mcp__ddg-search__fetch_content).
      - top-level MCP content-block list: blocks concatenated
        (LIVE: mcp__exa__web_fetch_exa).
      - dict with "text" key: coerced value (str or nested content-block list).
      - dict with "content" key: coerced value (MCP alternate shape).
      - dict with "result" key: coerced value (LIVE: native WebFetch envelope).
      - dict with a "file" dict carrying "content": coerced value (LIVE: native
        Read envelope; content is raw file text, truncated inline when large).

    If no shape matches — or a recognized key holds a non-string,
    non-content-block value — raises TypeError to surface the shape mismatch
    rather than silently repr-coercing it into the store.
    """
    if isinstance(tool_response, str):
        return tool_response
    if isinstance(tool_response, list):
        return _coerce_text_value(tool_response)
    if isinstance(tool_response, dict):
        if "text" in tool_response:
            return _coerce_text_value(tool_response["text"])
        if "content" in tool_response:
            return _coerce_text_value(tool_response["content"])
        if "result" in tool_response:
            return _coerce_text_value(tool_response["result"])
        file_obj = tool_response.get("file")
        if isinstance(file_obj, dict) and "content" in file_obj:
            return _coerce_text_value(file_obj["content"])
    raise TypeError(
        f"Unrecognized tool_response shape: {type(tool_response).__name__!r}. "
        "Expected str, a content-block list, or a dict with a "
        "'text'/'content'/'result'/'file.content' key. Live shapes were "
        "validated 2026-07-03 — a NEW shape means the harness changed; "
        "extend _extract_text."
    )


def _sha256_nfkc(text: str) -> str:
    """NFKC-normalize then SHA-256 hash."""
    normalized = unicodedata.normalize("NFKC", text)
    return hashlib.sha256(normalized.encode()).hexdigest()


def _file_path_from_input(tool_input: dict) -> str | None:
    """Extract file_path from tool_input; returns None if absent."""
    return tool_input.get("file_path") or None


def _harness_file(tool_response: object) -> dict:
    """The Read response's `file` dict, or {} when the shape lacks one. Pure."""
    if isinstance(tool_response, dict):
        file_obj = tool_response.get("file")
        if isinstance(file_obj, dict):
            return file_obj
    return {}


def _read_file_path(tool_input: dict, tool_response: object,
                    cwd: str) -> str | None:
    """ABSOLUTE path of the file a Read returned (W2D-01). Pure, no I/O.

    Order: the harness's own `tool_response.file.filePath` when absolute; else
    `tool_input.file_path` with `~` expanded and, if still relative, joined to
    the event's `cwd` when that is absolute. A path that cannot be made
    absolute is stored AS GIVEN — the gate treats any non-absolute stored path
    as matching a draft with the same basename (fail-closed), so the unknown
    origin points away from PASS.
    """
    harness = _harness_file(tool_response).get("filePath")
    if isinstance(harness, str) and harness and os.path.isabs(harness):
        return os.path.normpath(harness)
    given = _file_path_from_input(tool_input)
    if not isinstance(given, str) or not given:
        return given
    expanded = os.path.expanduser(given)
    if os.path.isabs(expanded):
        return os.path.normpath(expanded)
    if cwd and os.path.isabs(cwd):
        return os.path.normpath(os.path.join(cwd, expanded))
    return given


def _read_extent(tool_input: dict, tool_response: object) -> str:
    """"partial", "whole", or "" (unknown) for a Read (W2D-02). Pure.

    Partial when the harness reports startLine > 1, numLines < totalLines or
    truncatedByTokenCap, or the input asked for an offset/limit. "whole" only
    when the harness's own line counts say the whole file came back; anything
    the counts cannot confirm is "" — which the gate treats like "partial".
    """
    file_obj = _harness_file(tool_response)
    start = file_obj.get("startLine")
    num = file_obj.get("numLines")
    total = file_obj.get("totalLines")
    if file_obj.get("truncatedByTokenCap") is True:
        return "partial"
    if isinstance(start, int) and start > 1:
        return "partial"
    if isinstance(num, int) and isinstance(total, int) and num < total:
        return "partial"
    if tool_input.get("offset") is not None or tool_input.get("limit") is not None:
        return "partial"
    if isinstance(start, int) and isinstance(num, int) and isinstance(total, int):
        return "whole"
    return ""


# ---------------------------------------------------------------------------
# Overflow-file reconstruction (Task 2)
# ---------------------------------------------------------------------------

def _is_overflow_payload(tool_response: object) -> bool:
    """Return True iff tool_response is a Claude Code truncation payload.

    Assumed truncation shape (TASK-4-VALIDATION):
        {"preview": "<partial text>", "file_path": "<abs path to full content>"}

    Both keys must be present and file_path must be a non-empty string.

    A dict that also contains a non-empty "text" or "content" key is treated as
    a normal inline response — the presence of full inline content is a definitive
    inline signal that takes precedence over the overflow discriminators.
    """
    if not isinstance(tool_response, dict):
        return False
    file_path = tool_response.get("file_path")
    if not file_path or not isinstance(file_path, str):
        return False
    # Inline-content keys are definitive: if present and non-empty, the caller
    # already has the full text and must NOT be routed to read an external file.
    if tool_response.get("text") or tool_response.get("content"):
        return False
    # "preview" is the canonical discriminator for a truncation payload.
    return "preview" in tool_response


def reconstruct_text(tool_response: object) -> tuple[str, str]:
    """Extract the full text from a tool response, reading the overflow file if needed.

    Returns:
        (full_text, captured_via) where captured_via is one of:
          "overflow_file"  — tool_response was a truncation payload; full_text
                             was read from the referenced overflow file (UTF-8).
          "inline"         — tool_response carried the content directly (plain str
                             or dict with "text"/"content" key).

    Raises:
        FileNotFoundError  — overflow payload detected but the file does not exist.
                             NEVER falls back silently to the preview stub —
                             storing a preview as if it were full text is the exact
                             bug this function guards against.
        TypeError          — response is not an overflow payload AND has an
                             unrecognized inline shape (propagated from _extract_text).
    """
    if _is_overflow_payload(tool_response):
        # tool_response is a dict here — _is_overflow_payload returns False for
        # any non-dict, so the cast below is type-safe without a runtime assert.
        tool_response_dict: dict = tool_response  # type: ignore[assignment]
        file_path_str: str = tool_response_dict["file_path"]
        overflow_path = Path(file_path_str)
        # Fail loud — no silent fallback to preview.
        if not overflow_path.exists():
            raise FileNotFoundError(
                f"Overflow file referenced in tool_response does not exist: "
                f"{file_path_str!r}. "
                "Storing the preview stub as full text would silently under-ground "
                "evidence. Raise this as TASK-4-VALIDATION if the path scheme differs."
            )
        full_text = overflow_path.read_text(encoding="utf-8")
        return full_text, "overflow_file"

    # Inline path — delegates to existing _extract_text (raises TypeError on mismatch).
    return _extract_text(tool_response), "inline"


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

# Any word character. The gate's tokenizer is `re.findall(r"\w+", ...)`, so a
# text with no match here can never contribute a token to any check — it is
# not a document, whatever the tool says.
_ANY_WORD_RE = re.compile(r"\w")


def _retrieval_status(tool_name: str, tool_response: object, text: str) -> str:
    """"ok" if the fetch returned content, else "failed". Pure.

    R20-04 + R20-06 (2026-10-10): the absence rule counted STORED RECORDS, not
    SUCCESSFUL READS, so two fetches that failed with HTTP 503 — or returned
    only whitespace — certified "there is no X" at PASS 100.0. This is the
    POSITIVE requirement that replaces patching each symptom: a record
    demonstrates content, or it does not count as a search.

    A record is "failed" when the tool SIGNALS failure or the text holds no word:
      * an MCP result carrying `isError: true` (exa);
      * a native WebFetch result whose `code` is outside 200-299;
      * any text with no word character after NFKC.

    The record is still WRITTEN — the store is audit evidence of what was
    attempted — and the failure body is kept verbatim. Only its standing as a
    search changes, and that decision is the gate's.

    CEILING: a failure the tool does not SIGNAL is not caught. DDG returns a
    plain `str` with no error flag, and a captcha, a login wall or an "Access
    denied" page all arrive as a 2xx with words in them. Recognising those
    needs a model of what a document is, which the zero-LLM rule forbids. The
    upgrade path is upstream — capturing real search results (J-36) — not a
    longer list of error phrases here, because a phrase list that LICENSES a
    record as content would make its own gaps the attack (D-69).
    """
    if isinstance(tool_response, dict):
        if tool_response.get("isError") is True:
            return "failed"
        if tool_name in _HAIKU_SUMMARY_TOOLS:
            code = tool_response.get("code")
            if isinstance(code, int) and not 200 <= code < 300:
                return "failed"
    if tool_name in _EXA_TOOLS:
        # R24-01 (round 24, a regression I introduced in ca466a4): the status is
        # decided ONCE from the WHOLE response, whatever its envelope. A plain
        # string or a dict "text" used to fall back to the per-page text, so an
        # inline partial failure after the last page marked only that page and
        # left the earlier pages "ok" under the failed URL's search label.
        whole = _block_list(tool_response)
        haystack = ("\n".join(whole) if whole is not None
                    else reconstruct_text(tool_response)[0])
        if _EXA_ERROR_LINE_RE.search(haystack) or _EXA_ERROR_LINE_RE.search(text):
            return "failed"
    if not _ANY_WORD_RE.search(unicodedata.normalize("NFKC", text)):
        return "failed"
    return "ok"


def make_record(
    tool_name: str,
    tool_input: dict,
    tool_response: object,
    source_id: str,
    query_provenance: str,
    fetched_at: str,
    session_id: str = "",
    cwd: str = "",
) -> RetrievedSource | None:
    """Map a tool event to a RetrievedSource, or None for non-retrieval tools.

    Args:
        tool_name: The name of the tool that was called.
        tool_input: The tool's input dict (as provided by the Claude event stream).
        tool_response: The tool's response object (str or dict; see module docstring).
        source_id: Caller-assigned identifier for this source.
        query_provenance: The query that prompted this retrieval.
        fetched_at: ISO-8601 timestamp string (PASSED IN — no wall-clock here).

    Returns:
        RetrievedSource if tool_name is a retrieval tool; None otherwise.

    Pure function: no I/O, no network, no random, no wall-clock.
    NFKC normalization is applied before SHA-256 hashing (CLAUDE.md safety gate).
    """
    if tool_name not in _RETRIEVAL_TOOLS:
        return None
    # R20-01: a single record for a multi-document response would glue the
    # documents together, so a verbatim span could cross between them. Refuse
    # loudly; `make_records` is the path that keeps them apart.
    if _documents(tool_name, tool_response) is not None or (
            tool_name in _EXA_TOOLS
            and len([p for p in _EXA_SECTION_LOOSE_RE.split(
                reconstruct_text(tool_response)[0]) if p]) >= 2):
        raise ValueError(
            "make_record received a response holding several content blocks. "
            "One record would join them, letting a verbatim span cross from one "
            "fetched document into another (R20-01). Use make_records."
        )

    # reconstruct_text handles both overflow-file and inline paths.
    # captured_via reflects which path was taken.
    text, captured_via = reconstruct_text(tool_response)

    # Determine source classification and coordinate fields by tool type.
    if tool_name == "Read":
        # LIVE-VALIDATED (2026-07-03): the hook payload carries RAW file text —
        # the cat-n line-number prefixes exist only in the model-rendered view.
        # Store byte-identical content; stripping would corrupt files whose
        # lines genuinely start with <digits><TAB> (e.g. TSV).
        full_text_source = "verbatim"
        url: str | None = None
        file_path: str | None = _read_file_path(tool_input, tool_response, cwd)
        read_extent = _read_extent(tool_input, tool_response)
    elif tool_name in _HAIKU_SUMMARY_TOOLS:
        full_text_source = "haiku_summary"
        url = _certain_url(tool_input)
        file_path = None
        read_extent = ""
    else:
        # mcp__exa__web_fetch_exa, web_fetch_exa, mcp__ddg-search__fetch_content
        # R20-02 / R21-01: `_certain_url`, not "the first URL" — a multi-URL
        # response that arrives as ONE document (no exa headers) must not be
        # credited to whichever address the agent listed first.
        full_text_source = "verbatim"
        url = _certain_url(tool_input)
        file_path = None
        read_extent = ""

    return RetrievedSource(
        session_id=session_id,
        source_id=source_id,
        url=url,
        file_path=file_path,
        fetched_at=fetched_at,
        tool=tool_name,
        content_sha256=_sha256_nfkc(text),
        text=text,
        full_text_source=full_text_source,
        captured_via=captured_via,
        query_provenance=query_provenance,
        retrieval_status=_retrieval_status(tool_name, tool_response, text),
        read_extent=read_extent,
    )



# exa's fetch tools. Named separately because exa's response FORMAT, not just its
# envelope, carries document boundaries — see _documents.
_EXA_TOOLS: frozenset[str] = frozenset({"mcp__exa__web_fetch_exa", "web_fetch_exa"})

# LIVE-OBSERVED 2026-10-10 (round 21 called exa's MCP server; the orchestrator
# confirmed with its own `web_fetch_exa` call): a multi-URL fetch returns ONE
# text block holding every page, each introduced by a `# <title>` line followed
# by a `URL: <url>` line. The lookahead splits BEFORE each such header and keeps
# the header with its own section.

# R22-02 (round 22, 2026-10-10): header VARIANTS — "#"/"##" with or without a
# title, leading whitespace, a blank line before "URL:", "URL:" with no space.
# NONE has been observed from live exa; they are recognised anyway because a
# split can only stop a span from crossing (fail-closed). Used in place of the
# canonical pattern above, which it subsumes.
_EXA_SECTION_LOOSE_RE = re.compile(
    r"(?m)^(?=[ \t\ufeff\u200b]*#+[^\n]*\n(?:[ \t]*\n)?[ \t]*URL:[ \t]*\S)")

# R22-01 (round 22, LIVE-OBSERVED in round 21's raw exa capture): a PARTIAL
# failure in a multi-URL fetch is appended INLINE after the page that worked —
# "Error fetching <url>: CRAWL_NOT_FOUND", no header, no isError. The fetch's one
# search label cannot say which URL succeeded, so ANY such line marks EVERY
# record of that response failed. Case-insensitive, after stripping invisible
# characters (R22-03). Refusal-only, so over-matching is safe (D-69).
_EXA_ERROR_LINE_RE = re.compile(r"(?mi)^[\s\ufeff\u200b]*error fetching\b")

# LIVE-OBSERVED 2026-10-10: exa reports a failed fetch as an ordinary text block
# beginning with this phrase (e.g. "...: CRAWL_NOT_FOUND"). Its server response
# also carries `isError: true`, but the hook payload validated for exa is a bare
# block LIST, which has nowhere to put that flag — so whether the flag reaches
# the hook is UNKNOWN, and this does not depend on it.
#
# This is a list that drives a REFUSAL (it can only mark a record "failed"), so a
# missing phrase leaves a failure counted as a search — today's behaviour — and
# can never certify anything (D-69: refusal lists are safe to get wrong; lists
# that LICENSE an acceptance are not).


def _block_list(tool_response: object) -> list[str] | None:
    """The text of every content block when *tool_response* is a content-block
    LIST (top level, or under "text", "content", "result" or "file.content");
    None for every other shape. Pure.

    R21-04: C3 originally looked only at the top level, "text" and "content", so
    a block list under "result" or "file.content" was still joined. A non-text
    block raises TypeError, exactly as `_coerce_text_value` does.
    """
    if isinstance(tool_response, list):
        blocks = tool_response
    elif isinstance(tool_response, dict):
        candidate = None
        for key in ("text", "content", "result"):
            if key in tool_response:
                candidate = tool_response[key]
                break
        else:
            file_obj = tool_response.get("file")
            if isinstance(file_obj, dict):
                candidate = file_obj.get("content")
        if not isinstance(candidate, list):
            return None
        blocks = candidate
    else:
        return None
    texts: list[str] = []
    for block in blocks:
        if isinstance(block, dict) and isinstance(block.get("text"), str):
            texts.append(block["text"])
        else:
            raise TypeError(
                "Unrecognized content-block in a block list: "
                f"{type(block).__name__!r}. Expected {{'type':'text','text':str}}."
            )
    return texts


def _documents(tool_name: str, tool_response: object) -> list[str] | None:
    """The separate DOCUMENTS in a response, when there are TWO OR MORE; None
    when the response holds one document. Pure.

    R20-01 / R21-01. Joining documents let a verbatim span start in one and end
    in another. A document boundary is either a content-block boundary or, for
    exa, a section header INSIDE a block — exa's real multi-URL response is ONE
    block, so splitting on blocks alone never ran on the live tool (R21-01).

    A page can FORGE an exa header in its own text. That only adds a split, and a
    split can only stop a span from crossing, so forgery here is fail-closed. The
    header's `URL:` line is NEVER used for attribution — that would let a page
    choose which address its text is credited to.
    """
    blocks = _block_list(tool_response)
    if blocks is None:
        return None
    pieces: list[str] = []
    for block in blocks:
        if tool_name in _EXA_TOOLS:
            pieces.extend(part for part in _EXA_SECTION_LOOSE_RE.split(block) if part)
        else:
            pieces.append(block)
    return pieces if len(pieces) >= 2 else None


def _certain_url(tool_input: dict) -> str | None:
    """The fetched URL when it is CERTAIN, else None. Pure.

    R20-02 / R21-05. Certain means exactly one URL was requested: a singular
    `url`, or a `urls` list of exactly one non-empty string. Several URLs — or a
    `urls` list padded with blanks or non-strings, which used to be filtered down
    to "one" — mean the address of any given document is a guess, and a guessed
    address is a silent failure. Both keys present is ambiguous, and also None.
    """
    url = tool_input.get("url")
    urls = tool_input.get("urls")
    if urls is not None:
        if url is not None:
            return None
        if (isinstance(urls, list) and len(urls) == 1
                and isinstance(urls[0], str) and urls[0]):
            return urls[0]
        return None
    if isinstance(url, str) and url:
        return url
    return None


def make_records(
    tool_name: str,
    tool_input: dict,
    tool_response: object,
    source_id: str,
    query_provenance: str,
    fetched_at: str,
    session_id: str = "",
    cwd: str = "",
) -> list[RetrievedSource]:
    """Map a tool event to ONE RECORD PER FETCHED DOCUMENT. Pure.

    The hook's path. A one-document response yields exactly `make_record`'s
    record. A multi-document response (separate blocks, or exa sections inside
    one block) yields one record per document, so no span crosses between them.

    ADDRESS: `_certain_url` — the requested URL when exactly one was requested,
    else None. Never taken from the text.

    FILE PATH: kept for `Read`. Dropping it would blind the self-citation check
    (J-83 identifies the draft by its resolved file path) — the fail-OPEN
    direction, caught while designing R21-04's fix.

    `query_provenance` is the SAME on every document, deliberately: a label per
    document would turn one fetch into N searches and RAISE the absence count —
    PASS-enabling, so not done here.

    CEILING: a content block, or an exa section, is assumed to be one document.
    If a tool splits one document across blocks, a quote spanning the break is
    refused — an Error-A, fail-closed, unmeasured on any live multi-block payload.
    """
    if tool_name not in _RETRIEVAL_TOOLS:
        return []
    documents = _documents(tool_name, tool_response)
    captured_via = "inline"
    if documents is None and tool_name in _EXA_TOOLS:
        # REVIEW-PR12 HIGH (2026-10-22): exa text that does NOT arrive as a
        # block list — a plain string, a dict whose "text" is a string, or an
        # overflow file — skipped the split, so two pages stayed one record
        # and R20-01's cross-page span still certified. Split whatever text
        # capture actually extracted, whatever its envelope.
        text, captured_via = reconstruct_text(tool_response)
        pieces = [part for part in _EXA_SECTION_LOOSE_RE.split(text) if part]
        documents = pieces if len(pieces) >= 2 else None
    if documents is None:
        record = make_record(tool_name, tool_input, tool_response, source_id,
                             query_provenance, fetched_at, session_id, cwd)
        return [] if record is None else [record]
    is_read = tool_name == "Read"
    full_text_source = ("haiku_summary" if tool_name in _HAIKU_SUMMARY_TOOLS
                        else "verbatim")
    return [
        RetrievedSource(
            session_id=session_id,
            source_id=source_id,
            url=None if is_read else _certain_url(tool_input),
            file_path=(_read_file_path(tool_input, tool_response, cwd)
                       if is_read else None),
            fetched_at=fetched_at,
            tool=tool_name,
            content_sha256=_sha256_nfkc(text),
            text=text,
            full_text_source=full_text_source,
            captured_via=captured_via,
            query_provenance=query_provenance,
            retrieval_status=_retrieval_status(tool_name, tool_response, text),
            # One block of several is never the whole file.
            read_extent="partial" if is_read else "",
        )
        for text in documents
    ]


# ---------------------------------------------------------------------------
# Task 3: EvidenceStore — source_id assignment + append-only store writer
# ---------------------------------------------------------------------------

def next_source_id(store_path: str) -> str:
    """Return the next monotonic source ID for the given JSONL store.

    Reads the existing store (if present and non-empty), finds the highest
    ``S<n>`` source_id, and returns ``S<n+1>``.  An empty or absent store
    returns ``"S1"``.

    Pure with respect to outputs: does not write to disk; deterministic; no
    wall-clock or random.

    Args:
        store_path: Path to the JSONL evidence store (may not exist yet).

    Returns:
        ``"S1"`` when the store is absent or empty, ``"S<n+1>"`` otherwise.
    """
    path = Path(store_path)
    if not path.exists():
        return "S1"

    max_n: int = 0
    with path.open(encoding="utf-8") as fh:
        for raw_line in fh:
            line = raw_line.strip()
            if not line:
                continue
            try:
                obj = json.loads(line)
            except json.JSONDecodeError:
                continue
            sid = obj.get("source_id", "")
            if isinstance(sid, str) and sid.startswith("S"):
                try:
                    n = int(sid[1:])
                    if n > max_n:
                        max_n = n
                except ValueError:
                    pass

    return f"S{max_n + 1}"


def append_record(record: RetrievedSource, store_path: str) -> None:
    """Append ONE JSONL line for *record* to the store at *store_path*.

    Creates the parent directory if it does not exist.  Opens the file in
    append mode so existing lines are never rewritten or truncated.

    Serializes all 10 ``RetrievedSource`` fields as a JSON object with keys
    in the exact order that ``load_store`` expects:
        source_id, url, file_path, fetched_at, tool, content_sha256, text,
        full_text_source, captured_via, query_provenance.

    ``None`` field values are serialized as JSON ``null`` and round-trip
    correctly through ``load_store`` (which uses ``dict.get()``).

    Unicode is preserved verbatim (``ensure_ascii=False``).

    Args:
        record: The ``RetrievedSource`` to append.
        store_path: Absolute or relative path to the JSONL evidence store.
    """
    path = Path(store_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    obj = {
        "source_id": record.source_id,
        "url": record.url,
        "file_path": record.file_path,
        "fetched_at": record.fetched_at,
        "tool": record.tool,
        "content_sha256": record.content_sha256,
        "text": record.text,
        "full_text_source": record.full_text_source,
        "captured_via": record.captured_via,
        "query_provenance": record.query_provenance,
        "session_id": record.session_id,
        "retrieval_status": record.retrieval_status,
        "read_extent": record.read_extent,
    }
    line = json.dumps(obj, ensure_ascii=False)
    with path.open(mode="a", encoding="utf-8") as fh:
        fh.write(line + "\n")


# ---------------------------------------------------------------------------
# Task 4: atomic source_id assignment + append under an OS file lock
# ---------------------------------------------------------------------------

try:
    import fcntl  # noqa: E402  (kept beside its only user)
except ImportError:  # pragma: no cover - POSIX-only; absent on Windows
    # capture_core must still IMPORT on non-POSIX platforms so the pure
    # functions (make_record, append_record, next_source_id) remain usable;
    # only assign_and_append needs the lock, and it fails loud below.
    fcntl = None  # type: ignore[assignment]


def _record_with_source_id(record: RetrievedSource, source_id: str) -> RetrievedSource:
    """Return a copy of *record* with its source_id replaced (pure).

    `dataclasses.replace`, not a field-by-field rebuild: the rebuild had to be
    edited every time RetrievedSource gained a field, and a missed edit drops
    the field SILENTLY — the copy still type-checks and every hand-written
    JSONL test still passes while nothing reaches disk. Found again on
    2026-10-10 adding `retrieval_status`; this closes the class, not the case.
    """
    return dataclasses.replace(record, source_id=source_id)


def assign_and_append(record: RetrievedSource, store_path: str) -> str:
    """Atomically assign the next source_id to *record* and append it.

    The ``next_source_id`` read and the append are guarded together by an
    exclusive OS file lock (``fcntl.flock``) on a sidecar ``.lock`` file, so two
    concurrent hook fires (parallel tool calls) can never read the same
    high-water mark and therefore never collide on a source_id, and their lines
    never interleave.  The incoming ``record.source_id`` is ignored and
    overwritten with the freshly assigned id.

    Args:
        record: The ``RetrievedSource`` to persist (its source_id is replaced).
        store_path: Path to the JSONL evidence store.

    Returns:
        The assigned source_id (e.g. ``"S1"``).
    """
    if fcntl is None:  # exercised via monkeypatch in tests; real on Windows
        raise RuntimeError(
            "assign_and_append requires POSIX fcntl for atomic source_id "
            "assignment, which is unavailable on this platform (e.g. Windows). "
            "Cross-platform locking is a Phase-2 item; until then the hook fails "
            "CLOSED (no capture) here rather than risk duplicate source_ids — the "
            "gate then reports an under-populated store, never a false PASS."
        )

    path = Path(store_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    lock_path = path.with_name(path.name + ".lock")

    # The lock file is a stable, independent handle; holding it serialises the
    # read-modify-write across processes/threads. It is opened in append mode so
    # concurrent openers never truncate each other. It is intentionally NOT
    # removed on exit: deleting it would race a concurrent holder and defeat the
    # lock — a 0-byte sidecar is the correct, standard cost of file locking.
    with lock_path.open(mode="a", encoding="utf-8") as lock_fh:
        fcntl.flock(lock_fh.fileno(), fcntl.LOCK_EX)
        try:
            source_id = next_source_id(store_path)
            stamped = _record_with_source_id(record, source_id)
            append_record(stamped, store_path)
        finally:
            fcntl.flock(lock_fh.fileno(), fcntl.LOCK_UN)

    return source_id
