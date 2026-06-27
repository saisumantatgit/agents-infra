"""Agent-Assure Phase 1b — Tasks 1 & 2: EvidenceStore capture hook.

make_record(tool_name, tool_input, tool_response, source_id, query_provenance,
            fetched_at) -> RetrievedSource | None

Returns a RetrievedSource for retrieval tools; None for non-retrieval tools.
No network, no wall-clock, no random.  Reading an overflow file referenced
inside the tool_response dict IS permitted (that is the whole point of Task 2).

# TASK-4-VALIDATION: tool_response shape assumptions
# These must be verified against live Claude tool events in Task 4.
#
# --- Overflow / truncation shape (Task 2) ---
# Claude Code truncates large tool results before delivering them to the
# PostToolUse hook.  The assumed truncation shape is:
#
#   {
#       "preview":   "<first N chars of full content>",   # str
#       "file_path": "/tmp/claude_output_<hash>.txt"      # str — absolute path
#   }
#
# Detection predicate (_is_overflow_payload):
#   isinstance(r, dict) AND "file_path" in r AND "preview" in r
#
# TASK-4-VALIDATION — if the live Claude Code harness uses different field
# names (e.g. "truncated_content" / "output_file"), ONLY the predicate in
# _is_overflow_payload needs updating.  All downstream logic is field-name
# agnostic once the path is extracted.
#
# --- Inline shapes ---
# mcp__exa__web_fetch_exa / web_fetch_exa:
#   - Primary assumption: dict with key "text" containing page content.
#   - Fallback: plain str (the full page content).
#   - If neither, _extract_text raises TypeError — flagged in Task 4.
#
# WebFetch (native Claude tool):
#   - Primary assumption: plain str containing Haiku-summarized page content.
#   - Fallback: dict with key "text".
#   - HARD SPEC: full_text_source must be "haiku_summary" regardless of shape.
#     The native WebFetch tool always returns a Haiku-summarized form, never verbatim.
#
# Read (native Claude tool):
#   - Primary assumption: plain str containing raw file content.
#   - Fallback: dict with key "content" (some tool APIs use this key for file content).
#   - Fallback: dict with key "text".
#   - file_path is read from tool_input["file_path"].
#
# mcp__ddg-search__fetch_content:
#   - Primary assumption: dict with key "text" containing fetched page content.
#   - Fallback: plain str.
#
# mcp__ddg-search__search:
#   - Returns snippets (not full page content) → None (not a retrieval tool).
#
# Any other tool (Bash, Edit, Write, Grep, WebSearch, etc.) → None.
"""

from __future__ import annotations

import hashlib
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


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _extract_text(tool_response: object) -> str:
    """Extract the text content from a tool response.

    Handles:
      - plain str: returned as-is.
      - dict with "text" key: returns the value.
      - dict with "content" key: returns the value (Read tool alternate shape).

    TASK-4-VALIDATION: if neither shape matches, raises TypeError to surface
    the shape mismatch rather than silently returning empty string.
    """
    if isinstance(tool_response, str):
        return tool_response
    if isinstance(tool_response, dict):
        if "text" in tool_response:
            return str(tool_response["text"])
        if "content" in tool_response:
            return str(tool_response["content"])
    raise TypeError(
        f"Unrecognized tool_response shape: {type(tool_response).__name__!r}. "
        "Expected str or dict with 'text'/'content' key. "
        "Flag as TASK-4-VALIDATION — live response shape must be verified."
    )


def _sha256_nfkc(text: str) -> str:
    """NFKC-normalize then SHA-256 hash."""
    normalized = unicodedata.normalize("NFKC", text)
    return hashlib.sha256(normalized.encode()).hexdigest()


def _url_from_input(tool_input: dict) -> str | None:
    """Extract URL from tool_input; returns None if absent."""
    return tool_input.get("url") or None


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
