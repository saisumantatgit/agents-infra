"""Live-validated PostToolUse payload shapes — regression tests.

These fixtures are distilled from RAW PostToolUse stdin payloads captured from
a real Claude Code headless session on 2026-07-03 (TASK-4-VALIDATION executed).
Each test encodes the shape Claude Code ACTUALLY delivers, per tool:

  Read      -> {"type": "text", "file": {"filePath", "content", "numLines",
                "startLine", "totalLines"[, "truncatedByTokenCap"]}}
               content is RAW file text — NO cat-n line-number prefixes.
  WebFetch  -> {"bytes", "code", "codeText", "result": <str>, "durationMs", "url"}
  exa fetch -> TOP-LEVEL MCP content-block list: [{"type": "text", "text": ..., "_meta": ...}]
  DDG fetch -> plain str.

The assumed overflow shape {"preview", "file_path"} was NOT observed live:
large Read results truncate INLINE (truncatedByTokenCap: true, numLines <
totalLines). The store must hold exactly what was delivered — what the model
actually saw this session — no more, no less.
"""

from __future__ import annotations

import hashlib
import unicodedata

from scripts.capture_core import make_record

FIXED_AT = "1970-01-01T00:00:00Z"


def _sha(text: str) -> str:
    return hashlib.sha256(unicodedata.normalize("NFKC", text).encode()).hexdigest()


# ---------------------------------------------------------------------------
# Read — live envelope {"type": "text", "file": {"content": ...}}
# ---------------------------------------------------------------------------

_READ_CONTENT = (
    "The Eiffel Tower is 330 metres tall and was completed in March 1889.\n"
    "It was the tallest man-made structure in the world for 41 years.\n"
    "The tower has three levels accessible to visitors.\n"
)


def _read_envelope(content: str, **extra: object) -> dict:
    file_obj: dict = {
        "filePath": "/project/notes.txt",
        "content": content,
        "numLines": 4,
        "startLine": 1,
        "totalLines": 4,
    }
    file_obj.update(extra)
    return {"type": "text", "file": file_obj}


class TestReadLiveEnvelope:
    def test_captures_nested_file_content(self):
        rec = make_record(
            tool_name="Read",
            tool_input={"file_path": "/project/notes.txt"},
            tool_response=_read_envelope(_READ_CONTENT),
            source_id="S1",
            query_provenance="/project/notes.txt",
            fetched_at=FIXED_AT,
        )
        assert rec is not None, (
            "LIVE-SHAPE MISMATCH: the real Read PostToolUse payload nests content "
            "at tool_response['file']['content'] — the extractor must accept it."
        )
        assert rec.text == _READ_CONTENT
        assert rec.content_sha256 == _sha(_READ_CONTENT)
        assert rec.full_text_source == "verbatim"
        assert rec.file_path == "/project/notes.txt"
        assert rec.url is None
        assert rec.captured_via == "inline"

    def test_content_stored_verbatim_no_cat_n_stripping(self):
        # Live Read payloads carry RAW file text (no cat-n prefixes), so the
        # stored text must be byte-identical to the file content. A file whose
        # lines genuinely start with <digits><TAB> (e.g. TSV) must NOT be
        # mangled by line-number stripping.
        tsv = "123\tvalue_a\n456\tvalue_b\n"
        rec = make_record(
            tool_name="Read",
            tool_input={"file_path": "/project/data.tsv"},
            tool_response=_read_envelope(tsv),
            source_id="S1",
            query_provenance="/project/data.tsv",
            fetched_at=FIXED_AT,
        )
        assert rec is not None
        assert rec.text == tsv, (
            "REGRESSION: leading '<digits>\\t' content was altered. Live Read "
            "payloads are raw file text; nothing may be stripped from them."
        )

    def test_truncated_read_stores_delivered_content(self):
        # Live truncation is INLINE: truncatedByTokenCap=true, numLines < totalLines.
        # The store holds exactly what the model saw — the truncated text.
        delivered = "Line 1\nLine 2\nLine 3\n"
        rec = make_record(
            tool_name="Read",
            tool_input={"file_path": "/project/big.txt"},
            tool_response=_read_envelope(
                delivered, numLines=3, totalLines=1801, truncatedByTokenCap=True
            ),
            source_id="S1",
            query_provenance="/project/big.txt",
            fetched_at=FIXED_AT,
        )
        assert rec is not None
        assert rec.text == delivered
        assert rec.captured_via == "inline"


# ---------------------------------------------------------------------------
# WebFetch — live envelope {"result": <str>, "code", "bytes", ...}
# ---------------------------------------------------------------------------

_WEBFETCH_RESULT = (
    "# Purpose of This Page\n\n"
    "This webpage is for documentation and educational purposes."
)


class TestWebFetchLiveEnvelope:
    def test_captures_result_key_as_haiku_summary(self):
        rec = make_record(
            tool_name="WebFetch",
            tool_input={"url": "https://example.com", "prompt": "what is this page for"},
            tool_response={
                "bytes": 559,
                "code": 200,
                "codeText": "OK",
                "result": _WEBFETCH_RESULT,
                "durationMs": 2827,
                "url": "https://example.com",
            },
            source_id="S2",
            query_provenance="https://example.com",
            fetched_at=FIXED_AT,
        )
        assert rec is not None, (
            "LIVE-SHAPE MISMATCH: the real WebFetch PostToolUse payload wraps the "
            "summary in a {'result': str, ...} envelope — the extractor must accept it."
        )
        assert rec.text == _WEBFETCH_RESULT
        # HARD SPEC: native WebFetch is Haiku-summarized, never verbatim.
        assert rec.full_text_source == "haiku_summary"
        assert rec.url == "https://example.com"


# ---------------------------------------------------------------------------
# mcp__exa__web_fetch_exa — live shape: TOP-LEVEL content-block list
# ---------------------------------------------------------------------------

_EXA_TEXT = "# Example Domain\nURL: https://example.com\n\nExample Domain\n"


class TestExaLiveShape:
    def test_captures_top_level_content_block_list(self):
        rec = make_record(
            tool_name="mcp__exa__web_fetch_exa",
            tool_input={"url": "https://example.com"},
            tool_response=[
                {"type": "text", "text": _EXA_TEXT, "_meta": {"searchTime": 8.012}}
            ],
            source_id="S3",
            query_provenance="https://example.com",
            fetched_at=FIXED_AT,
        )
        assert rec is not None, (
            "LIVE-SHAPE MISMATCH: the real exa MCP PostToolUse payload is a "
            "TOP-LEVEL content-block list [{'type':'text','text':...}] — the "
            "extractor must normalize it exactly like a nested block list."
        )
        assert rec.text == _EXA_TEXT
        assert rec.full_text_source == "verbatim"

    def test_multi_block_list_concatenates(self):
        rec = make_record(
            tool_name="mcp__exa__web_fetch_exa",
            tool_input={"url": "https://example.com"},
            tool_response=[
                {"type": "text", "text": "part one"},
                {"type": "text", "text": "part two"},
            ],
            source_id="S3",
            query_provenance="https://example.com",
            fetched_at=FIXED_AT,
        )
        assert rec is not None
        assert rec.text == "part one\npart two"


# ---------------------------------------------------------------------------
# mcp__ddg-search__fetch_content — live shape: plain str (green control)
# ---------------------------------------------------------------------------

class TestDdgLiveShape:
    def test_plain_str_captured_verbatim(self):
        content = "Example Domain. This domain is for use in illustrative examples."
        rec = make_record(
            tool_name="mcp__ddg-search__fetch_content",
            tool_input={"url": "https://example.com"},
            tool_response=content,
            source_id="S4",
            query_provenance="https://example.com",
            fetched_at=FIXED_AT,
        )
        assert rec is not None
        assert rec.text == content
        assert rec.full_text_source == "verbatim"


# ---------------------------------------------------------------------------
# exa tool_input — live shape uses PLURAL "urls": [<url>, ...]
# ---------------------------------------------------------------------------

class TestExaLiveInputUrls:
    def test_url_taken_from_urls_list(self):
        rec = make_record(
            tool_name="mcp__exa__web_fetch_exa",
            tool_input={"urls": ["https://example.com"]},
            tool_response=[{"type": "text", "text": _EXA_TEXT}],
            source_id="S3",
            query_provenance="https://example.com",
            fetched_at=FIXED_AT,
        )
        assert rec is not None
        assert rec.url == "https://example.com", (
            "LIVE-SHAPE MISMATCH: exa's tool_input carries {'urls': [<url>]} "
            "(plural, list) — the record's url must come from its first element."
        )

    def test_query_provenance_derived_from_urls_list(self, tmp_path):
        from scripts.capture_hook import process_event

        store = tmp_path / "evidence-store.jsonl"
        event = {
            "tool_name": "mcp__exa__web_fetch_exa",
            "tool_input": {"urls": ["https://example.com"]},
            "tool_response": [{"type": "text", "text": _EXA_TEXT}],
            "session_id": "sess-123",
        }
        sid = process_event(event, str(store))
        assert sid == "S1"
        import json as _json

        rec = _json.loads(store.read_text().strip())
        assert rec["query_provenance"] == "https://example.com", (
            "query_provenance must derive from tool_input['urls'][0], not fall "
            "back to the session_id."
        )
