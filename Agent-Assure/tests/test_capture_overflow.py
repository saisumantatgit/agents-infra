"""Task 2: overflow-file reconstruction tests for capture_core.

These tests MUST be run red against the pre-implementation code to prove
coverage before the implementation is applied.

Assumed truncation shape (TASK-4-VALIDATION — must be verified in Task 4
against live Claude Code PostToolUse events):

    {
        "preview": "<first N chars of the full content>",
        "file_path": "/tmp/claude_output_<hash>.txt"   # absolute path to full content
    }

Detection predicate: a dict that has BOTH a "file_path" key (non-empty string)
AND either a "preview" key OR (to handle edge cases) neither a "text" key nor a
"content" key. We treat the presence of "file_path" + "preview" as the canonical
truncation signal. The current _extract_text falls through to TypeError for the
{"preview":..., "file_path":...} shape — the new reconstruct_text intercepts it
first.

If the live Claude Code truncation form uses different field names (e.g.
"truncated_content" / "output_file"), only the _is_overflow_payload predicate
in reconstruct_text needs updating. All other logic is field-name agnostic.
"""

from __future__ import annotations

import hashlib
import os
import tempfile
import unicodedata

import pytest

from scripts.capture_core import make_record, reconstruct_text
from scripts.ground_check import RetrievedSource


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _sha(text: str) -> str:
    normalized = unicodedata.normalize("NFKC", text)
    return hashlib.sha256(normalized.encode()).hexdigest()


FIXED_AT = "2026-06-27T10:00:00Z"
FIXED_ID = "S1"
FIXED_QP = "overflow reconstruction test"

# A body of text large enough to prove reconstruction (>10,000 chars).
_LARGE_CONTENT = "X" * 10_001 + " end-of-large-content"


# ---------------------------------------------------------------------------
# reconstruct_text unit tests
# ---------------------------------------------------------------------------

class TestReconstructText:
    """Unit tests for reconstruct_text(tool_response) -> (str, str)."""

    def test_inline_plain_string(self):
        text, via = reconstruct_text("hello world")
        assert text == "hello world"
        assert via == "inline"

    def test_inline_dict_text_key(self):
        text, via = reconstruct_text({"text": "page content"})
        assert text == "page content"
        assert via == "inline"

    def test_inline_dict_content_key(self):
        text, via = reconstruct_text({"content": "file content"})
        assert text == "file content"
        assert via == "inline"

    def test_overflow_reads_file(self, tmp_path):
        full_content = _LARGE_CONTENT
        overflow_file = tmp_path / "output_full.txt"
        overflow_file.write_text(full_content, encoding="utf-8")

        payload = {
            "preview": full_content[:200],
            "file_path": str(overflow_file),
        }
        text, via = reconstruct_text(payload)

        assert via == "overflow_file"
        assert text == full_content
        assert len(text) > 10_000

    def test_overflow_text_is_not_preview(self, tmp_path):
        """The reconstructed text must NOT equal the preview stub."""
        full_content = _LARGE_CONTENT
        overflow_file = tmp_path / "output_full.txt"
        overflow_file.write_text(full_content, encoding="utf-8")
        preview = full_content[:200]

        payload = {"preview": preview, "file_path": str(overflow_file)}
        text, via = reconstruct_text(payload)

        assert text != preview
        assert text == full_content

    def test_overflow_missing_file_raises(self, tmp_path):
        """Missing overflow file must raise — no silent fallback to preview."""
        payload = {
            "preview": "truncated preview...",
            "file_path": str(tmp_path / "nonexistent_full.txt"),
        }
        with pytest.raises(FileNotFoundError):
            reconstruct_text(payload)

    def test_inline_unrecognized_shape_raises(self):
        """Non-overflow, non-standard shape raises TypeError (same as Task 1)."""
        with pytest.raises(TypeError):
            reconstruct_text({"completely_unknown_key": 42})


# ---------------------------------------------------------------------------
# make_record integration tests — overflow path
# ---------------------------------------------------------------------------

class TestMakeRecordOverflow:
    """make_record must delegate to reconstruct_text for overflow payloads."""

    def test_full_content_stored_not_preview(self, tmp_path):
        """Core invariant: stored text is the full file content, not the preview."""
        overflow_file = tmp_path / "full_output.txt"
        overflow_file.write_text(_LARGE_CONTENT, encoding="utf-8")
        preview = _LARGE_CONTENT[:200]

        result = make_record(
            tool_name="mcp__exa__web_fetch_exa",
            tool_input={"url": "https://example.com/long-page"},
            tool_response={"preview": preview, "file_path": str(overflow_file)},
            source_id=FIXED_ID,
            query_provenance=FIXED_QP,
            fetched_at=FIXED_AT,
        )

        assert result is not None
        assert len(result.text) > 10_000
        assert result.text == _LARGE_CONTENT
        assert result.text != preview

    def test_captured_via_is_overflow_file(self, tmp_path):
        overflow_file = tmp_path / "full_output.txt"
        overflow_file.write_text(_LARGE_CONTENT, encoding="utf-8")

        result = make_record(
            tool_name="mcp__exa__web_fetch_exa",
            tool_input={"url": "https://example.com/long-page"},
            tool_response={
                "preview": _LARGE_CONTENT[:200],
                "file_path": str(overflow_file),
            },
            source_id=FIXED_ID,
            query_provenance=FIXED_QP,
            fetched_at=FIXED_AT,
        )

        assert result is not None
        assert result.captured_via == "overflow_file"

    def test_sha256_over_full_content(self, tmp_path):
        """content_sha256 must be sha256(NFKC(full_text)), not sha256(NFKC(preview))."""
        overflow_file = tmp_path / "full_output.txt"
        overflow_file.write_text(_LARGE_CONTENT, encoding="utf-8")
        preview = _LARGE_CONTENT[:200]

        result = make_record(
            tool_name="mcp__exa__web_fetch_exa",
            tool_input={"url": "https://example.com/long-page"},
            tool_response={"preview": preview, "file_path": str(overflow_file)},
            source_id=FIXED_ID,
            query_provenance=FIXED_QP,
            fetched_at=FIXED_AT,
        )

        assert result is not None
        assert result.content_sha256 == _sha(_LARGE_CONTENT)
        # Confirm it is NOT the sha of the preview (anti-tautology guard).
        assert result.content_sha256 != _sha(preview)

    def test_inline_payload_captured_via_inline(self):
        """Non-overflow payload preserves captured_via == 'inline' (Task 1 regression)."""
        content = "Short inline content."
        result = make_record(
            tool_name="mcp__exa__web_fetch_exa",
            tool_input={"url": "https://example.com/short"},
            tool_response={"text": content},
            source_id=FIXED_ID,
            query_provenance=FIXED_QP,
            fetched_at=FIXED_AT,
        )

        assert result is not None
        assert result.captured_via == "inline"
        assert result.text == content

    def test_missing_overflow_file_raises(self, tmp_path):
        """make_record must propagate the FileNotFoundError — no silent fallback."""
        payload = {
            "preview": "truncated...",
            "file_path": str(tmp_path / "does_not_exist.txt"),
        }
        with pytest.raises(FileNotFoundError):
            make_record(
                tool_name="mcp__exa__web_fetch_exa",
                tool_input={"url": "https://example.com/long-page"},
                tool_response=payload,
                source_id=FIXED_ID,
                query_provenance=FIXED_QP,
                fetched_at=FIXED_AT,
            )

    def test_overflow_works_for_read_tool(self, tmp_path):
        """Overflow reconstruction must work for the Read tool as well."""
        overflow_file = tmp_path / "large_source.py"
        overflow_file.write_text(_LARGE_CONTENT, encoding="utf-8")

        result = make_record(
            tool_name="Read",
            tool_input={"file_path": "/project/src/large_module.py"},
            tool_response={
                "preview": _LARGE_CONTENT[:200],
                "file_path": str(overflow_file),
            },
            source_id="S2",
            query_provenance="read large file",
            fetched_at=FIXED_AT,
        )

        assert result is not None
        assert result.captured_via == "overflow_file"
        assert len(result.text) > 10_000
        assert result.text == _LARGE_CONTENT
