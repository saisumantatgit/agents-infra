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
#   - file_path is read from tool_input["file_path"].
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

import hashlib
import json
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


def _url_from_input(tool_input: dict) -> str | None:
    """Extract URL from tool_input; returns None if absent.

    LIVE-VALIDATED (2026-07-03): mcp__exa__web_fetch_exa carries a PLURAL
    ``{"urls": [<url>, ...]}`` list — the first element is used. Native tools
    (WebFetch) carry a singular ``{"url": <url>}``.
    """
    url = tool_input.get("url")
    if isinstance(url, str) and url:
        return url
    urls = tool_input.get("urls")
    if isinstance(urls, list) and urls and isinstance(urls[0], str) and urls[0]:
        return urls[0]
    return None


def _file_path_from_input(tool_input: dict) -> str | None:
    """Extract file_path from tool_input; returns None if absent."""
    return tool_input.get("file_path") or None


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

def make_record(
    tool_name: str,
    tool_input: dict,
    tool_response: object,
    source_id: str,
    query_provenance: str,
    fetched_at: str,
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
        file_path: str | None = _file_path_from_input(tool_input)
    elif tool_name in _HAIKU_SUMMARY_TOOLS:
        full_text_source = "haiku_summary"
        url = _url_from_input(tool_input)
        file_path = None
    else:
        # mcp__exa__web_fetch_exa, web_fetch_exa, mcp__ddg-search__fetch_content
        full_text_source = "verbatim"
        url = _url_from_input(tool_input)
        file_path = None

    return RetrievedSource(
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
    )


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
    """Return a copy of *record* with its source_id replaced (pure)."""
    return RetrievedSource(
        source_id=source_id,
        url=record.url,
        file_path=record.file_path,
        fetched_at=record.fetched_at,
        tool=record.tool,
        content_sha256=record.content_sha256,
        text=record.text,
        full_text_source=record.full_text_source,
        captured_via=record.captured_via,
        query_provenance=record.query_provenance,
    )


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
