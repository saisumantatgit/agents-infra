#!/usr/bin/env python3
"""Agent-Assure Phase 1b — Task 4: PostToolUse hook ENTRY.

Reads a PostToolUse event JSON from stdin, maps it to a RetrievedSource via
``make_record``, and (if it is a retrieval tool) atomically appends it to the
evidence store.

CONTRACT: a hook must NEVER block the tool.  This entry ALWAYS exits 0, even on
malformed input, an unrecognized response shape, or a write error.  Failures are
reported on stderr (visible in the hook debug log) but never propagate a
non-zero exit code.

# TASK-4-VALIDATION — assumed PostToolUse stdin payload shape
# Whether Claude Code actually FIRES this hook live, and the exact field names
# it delivers, is NOT unit-testable here.  Flag for live user validation.
# Assumed top-level fields of the stdin JSON object:
#
#   {
#       "tool_name":     "<str>",   # e.g. "mcp__exa__web_fetch_exa", "Read"
#       "tool_input":    { ... },   # the tool's input dict (url / file_path / query)
#       "tool_response": <str|dict>,# the tool's result (see capture_core docstring)
#       "session_id":    "<str>",   # optional — used as provenance fallback
#       ...                          # other fields (cwd, hook_event_name, ...) ignored
#   }
#
# query_provenance derivation (first non-empty wins):
#   tool_input["query"]  →  tool_input["url"]  →  tool_input["file_path"]
#   →  event["session_id"]  →  "" (empty string)
#
# If the live harness names these fields differently (e.g. "toolName",
# "input", "response", "result"), ONLY _parse_event below needs updating.
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

# Make `scripts` importable when invoked as a bare file (hook context: the CWD
# is the user's project, not this package root).
_THIS = Path(__file__).resolve()
_REPO_ROOT = _THIS.parents[1]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from scripts.capture_core import (  # noqa: E402
    assign_and_append,
    is_retrieval_tool,
    make_record,
)


# Deterministic placeholder timestamp. PostToolUse events do not carry a
# trustworthy fetch time and CLAUDE.md forbids wall-clock in logic; the real
# fetched_at is stamped by upstream provenance when available. We store a fixed
# sentinel so the field is well-typed and deterministic.
_FETCHED_AT_SENTINEL = "1970-01-01T00:00:00Z"


def _resolve_store_path() -> str:
    """Resolve the evidence-store path.

    Honors the ``ASSURE_EVIDENCE_STORE`` env override; otherwise defaults to
    ``<CWD>/.assure/evidence-store.jsonl``.
    """
    override = os.environ.get("ASSURE_EVIDENCE_STORE")
    if override:
        return override
    return str(Path.cwd() / ".assure" / "evidence-store.jsonl")


def _derive_query_provenance(tool_input: dict, event: dict) -> str:
    """Derive query_provenance from the tool input or session.

    First non-empty of: query, url, file_path, session_id; else "".
    """
    for key in ("query", "url", "file_path"):
        value = tool_input.get(key)
        if isinstance(value, str) and value:
            return value
    session_id = event.get("session_id")
    if isinstance(session_id, str) and session_id:
        return session_id
    return ""


def _parse_event(raw: str) -> dict | None:
    """Parse the stdin JSON into an event dict, or return None if unusable."""
    raw = raw.strip()
    if not raw:
        return None
    try:
        event = json.loads(raw)
    except (json.JSONDecodeError, ValueError):
        return None
    if not isinstance(event, dict):
        return None
    return event


def process_event(event: dict, store_path: str) -> str | None:
    """Map an event to a record and atomically append it if it is a retrieval tool.

    Returns the assigned source_id, or None when the tool is non-retrieval (or
    make_record returns None for any other reason).
    """
    tool_name = event.get("tool_name")
    if not isinstance(tool_name, str) or not tool_name:
        return None

    tool_input = event.get("tool_input")
    if not isinstance(tool_input, dict):
        tool_input = {}

    tool_response = event.get("tool_response")

    # A retrieval tool that fired with no response carries no text to ground.
    # Dropping it is correct, but it MUST be diagnostically DISTINCT from a
    # genuine payload-shape mismatch (which raises TypeError below and is logged
    # as "capture skipped"), so live validation can tell "benign empty response"
    # from "the extractor is broken because the live field name differs".
    if is_retrieval_tool(tool_name) and tool_response is None:
        print(
            f"[assure-hook] TASK-4-VALIDATION: retrieval tool {tool_name!r} fired "
            "with no tool_response (None/absent) — nothing to capture. If a real "
            "response was expected, the live payload field name may differ.",
            file=sys.stderr,
        )
        return None

    query_provenance = _derive_query_provenance(tool_input, event)

    record = make_record(
        tool_name=tool_name,
        tool_input=tool_input,
        tool_response=tool_response,
        source_id="UNASSIGNED",  # replaced atomically by assign_and_append
        query_provenance=query_provenance,
        fetched_at=_FETCHED_AT_SENTINEL,
    )
    if record is None:
        return None

    return assign_and_append(record, store_path)


def main() -> int:
    """Hook entry. ALWAYS returns 0 — a hook must never block the tool."""
    try:
        raw = sys.stdin.read()
    except Exception as exc:  # pragma: no cover - stdin read failure is non-blocking
        print(f"[assure-hook] stdin read failed: {exc}", file=sys.stderr)
        return 0

    event = _parse_event(raw)
    if event is None:
        # Malformed / empty stdin: nothing to capture, but never block the tool.
        return 0

    store_path = _resolve_store_path()
    try:
        process_event(event, store_path)
    except Exception as exc:
        # Fail loud on stderr (debug log) but NEVER block the tool with a
        # non-zero exit. Shape mismatches (TypeError from _extract_text) and
        # overflow-file misses (FileNotFoundError) land here and are surfaced
        # for TASK-4-VALIDATION without breaking the user's tool call.
        print(f"[assure-hook] capture skipped: {type(exc).__name__}: {exc}",
              file=sys.stderr)
        return 0

    return 0


if __name__ == "__main__":
    sys.exit(main())
