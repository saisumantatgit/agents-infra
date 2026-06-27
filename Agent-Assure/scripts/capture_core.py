"""Agent-Assure Phase 1b — Task 1: EvidenceStore capture hook (pure mapping).

make_record(tool_name, tool_input, tool_response, source_id, query_provenance,
            fetched_at) -> RetrievedSource | None

Returns a RetrievedSource for retrieval tools; None for non-retrieval tools.
No I/O, no network, no wall-clock, no random. Pure function.

# TASK-4-VALIDATION: tool_response shape assumptions
# These must be verified against live Claude tool events in Task 4.
#
# mcp__exa__web_fetch_exa / web_fetch_exa:
#   - Primary assumption: dict with key "text" containing page content.
#   - Fallback: plain str (the full page content).
#   - If neither, _extract_text raises ValueError — flagged in Task 4.
#
# WebFetch (native Claude tool):
#   - Primary assumption: plain str containing Haiku-summarized page content.
#   - Fallback: dict with key "text".
#   - HARD SPEC: full_text_source must be "haiku_summary" regardless of response shape.
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

    text = _extract_text(tool_response)

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
        captured_via="inline",
        query_provenance=query_provenance,
    )
