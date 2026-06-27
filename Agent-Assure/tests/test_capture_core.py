"""Tests for capture_core.make_record — TDD suite.

Tool-response shape assumptions (TASK-4-VALIDATION):
  exa (mcp__exa__web_fetch_exa): response is a dict with key "text" containing
      the fetched page text. May also appear as a plain string — both shapes tested.
  WebFetch: response is a string (Haiku-summarized page text, returned directly
      by the native Claude tool). Also tested as dict {"text": ...}.
  Read: response is a string (raw file content) returned by the native Read tool.
      Also tested as dict {"content": ...}.
  Bash: not a retrieval tool — make_record must return None regardless of response.
"""

import hashlib
import unicodedata

import pytest

from scripts.capture_core import make_record
from scripts.ground_check import RetrievedSource


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _sha(text: str) -> str:
    normalized = unicodedata.normalize("NFKC", text)
    return hashlib.sha256(normalized.encode()).hexdigest()


FIXED_AT = "2026-06-27T10:00:00Z"
FIXED_ID = "S1"
FIXED_QP = "what is Redis throughput"


# ---------------------------------------------------------------------------
# Test 1: exa fetch → verbatim record
# ---------------------------------------------------------------------------

class TestExaFetch:
    def test_full_text_source_is_verbatim(self):
        result = make_record(
            tool_name="mcp__exa__web_fetch_exa",
            tool_input={"url": "https://example.com/redis-perf"},
            tool_response={"text": "Redis handles 100K ops per second."},
            source_id=FIXED_ID,
            query_provenance=FIXED_QP,
            fetched_at=FIXED_AT,
        )
        assert result is not None
        assert result.full_text_source == "verbatim"

    def test_url_populated(self):
        result = make_record(
            tool_name="mcp__exa__web_fetch_exa",
            tool_input={"url": "https://example.com/redis-perf"},
            tool_response={"text": "Redis handles 100K ops per second."},
            source_id=FIXED_ID,
            query_provenance=FIXED_QP,
            fetched_at=FIXED_AT,
        )
        assert result.url == "https://example.com/redis-perf"

    def test_file_path_is_none(self):
        result = make_record(
            tool_name="mcp__exa__web_fetch_exa",
            tool_input={"url": "https://example.com/redis-perf"},
            tool_response={"text": "Redis handles 100K ops per second."},
            source_id=FIXED_ID,
            query_provenance=FIXED_QP,
            fetched_at=FIXED_AT,
        )
        assert result.file_path is None

    def test_text_extracted(self):
        content = "Redis handles 100K ops per second on commodity hardware."
        result = make_record(
            tool_name="mcp__exa__web_fetch_exa",
            tool_input={"url": "https://example.com/redis-perf"},
            tool_response={"text": content},
            source_id=FIXED_ID,
            query_provenance=FIXED_QP,
            fetched_at=FIXED_AT,
        )
        assert result.text == content

    def test_sha256_correct(self):
        content = "Redis handles 100K ops per second on commodity hardware."
        result = make_record(
            tool_name="mcp__exa__web_fetch_exa",
            tool_input={"url": "https://example.com/redis-perf"},
            tool_response={"text": content},
            source_id=FIXED_ID,
            query_provenance=FIXED_QP,
            fetched_at=FIXED_AT,
        )
        assert result.content_sha256 == _sha(content)

    def test_captured_via_is_inline(self):
        result = make_record(
            tool_name="mcp__exa__web_fetch_exa",
            tool_input={"url": "https://example.com/redis-perf"},
            tool_response={"text": "Redis handles 100K ops per second."},
            source_id=FIXED_ID,
            query_provenance=FIXED_QP,
            fetched_at=FIXED_AT,
        )
        assert result.captured_via == "inline"

    def test_source_id_and_query_provenance(self):
        result = make_record(
            tool_name="mcp__exa__web_fetch_exa",
            tool_input={"url": "https://example.com/redis-perf"},
            tool_response={"text": "Redis handles 100K ops per second."},
            source_id=FIXED_ID,
            query_provenance=FIXED_QP,
            fetched_at=FIXED_AT,
        )
        assert result.source_id == FIXED_ID
        assert result.query_provenance == FIXED_QP

    def test_tool_field_is_tool_name(self):
        result = make_record(
            tool_name="mcp__exa__web_fetch_exa",
            tool_input={"url": "https://example.com/redis-perf"},
            tool_response={"text": "Redis handles 100K ops per second."},
            source_id=FIXED_ID,
            query_provenance=FIXED_QP,
            fetched_at=FIXED_AT,
        )
        assert result.tool == "mcp__exa__web_fetch_exa"

    def test_short_alias_web_fetch_exa(self):
        result = make_record(
            tool_name="web_fetch_exa",
            tool_input={"url": "https://example.com/redis-perf"},
            tool_response={"text": "Some content."},
            source_id=FIXED_ID,
            query_provenance=FIXED_QP,
            fetched_at=FIXED_AT,
        )
        assert result is not None
        assert result.full_text_source == "verbatim"

    def test_response_as_plain_string(self):
        # TASK-4-VALIDATION: if real exa response is a plain string, this must work.
        content = "Redis handles 100K ops per second."
        result = make_record(
            tool_name="mcp__exa__web_fetch_exa",
            tool_input={"url": "https://example.com/redis-perf"},
            tool_response=content,
            source_id=FIXED_ID,
            query_provenance=FIXED_QP,
            fetched_at=FIXED_AT,
        )
        assert result is not None
        assert result.text == content
        assert result.full_text_source == "verbatim"

    def test_fetched_at_passed_through(self):
        result = make_record(
            tool_name="mcp__exa__web_fetch_exa",
            tool_input={"url": "https://example.com/redis-perf"},
            tool_response={"text": "content"},
            source_id=FIXED_ID,
            query_provenance=FIXED_QP,
            fetched_at=FIXED_AT,
        )
        assert result.fetched_at == FIXED_AT

    def test_nfkc_applied_to_sha256(self):
        # Cyrillic 'а' (U+0430) normalizes the same as Latin 'a' under NFKC.
        # The sha must use the normalized form.
        content_raw = "café"  # 'café' precomposed
        content_nfc = unicodedata.normalize("NFC", content_raw)  # same here
        content_nfkc = unicodedata.normalize("NFKC", content_raw)
        result = make_record(
            tool_name="mcp__exa__web_fetch_exa",
            tool_input={"url": "https://example.com/"},
            tool_response={"text": content_raw},
            source_id=FIXED_ID,
            query_provenance=FIXED_QP,
            fetched_at=FIXED_AT,
        )
        expected_sha = hashlib.sha256(content_nfkc.encode()).hexdigest()
        assert result.content_sha256 == expected_sha


# ---------------------------------------------------------------------------
# Test 2: WebFetch → haiku_summary (HARD SPEC REQUIREMENT)
# ---------------------------------------------------------------------------

class TestWebFetch:
    def test_full_text_source_is_haiku_summary(self):
        result = make_record(
            tool_name="WebFetch",
            tool_input={"url": "https://docs.example.com/api"},
            tool_response="This is a Haiku-summarized version of the API docs.",
            source_id="S2",
            query_provenance="API docs summary",
            fetched_at=FIXED_AT,
        )
        assert result is not None
        assert result.full_text_source == "haiku_summary"

    def test_not_verbatim(self):
        result = make_record(
            tool_name="WebFetch",
            tool_input={"url": "https://docs.example.com/api"},
            tool_response="Summary text.",
            source_id="S2",
            query_provenance="API docs",
            fetched_at=FIXED_AT,
        )
        assert result.full_text_source != "verbatim"

    def test_url_populated(self):
        result = make_record(
            tool_name="WebFetch",
            tool_input={"url": "https://docs.example.com/api"},
            tool_response="Summary text.",
            source_id="S2",
            query_provenance="API docs",
            fetched_at=FIXED_AT,
        )
        assert result.url == "https://docs.example.com/api"

    def test_file_path_is_none(self):
        result = make_record(
            tool_name="WebFetch",
            tool_input={"url": "https://docs.example.com/api"},
            tool_response="Summary text.",
            source_id="S2",
            query_provenance="API docs",
            fetched_at=FIXED_AT,
        )
        assert result.file_path is None

    def test_text_and_sha(self):
        content = "Summarized page content."
        result = make_record(
            tool_name="WebFetch",
            tool_input={"url": "https://docs.example.com/api"},
            tool_response=content,
            source_id="S2",
            query_provenance="API docs",
            fetched_at=FIXED_AT,
        )
        assert result.text == content
        assert result.content_sha256 == _sha(content)

    def test_response_as_dict(self):
        # TASK-4-VALIDATION: WebFetch may sometimes return dict with "text" key.
        content = "Summarized page content."
        result = make_record(
            tool_name="WebFetch",
            tool_input={"url": "https://docs.example.com/api"},
            tool_response={"text": content},
            source_id="S2",
            query_provenance="API docs",
            fetched_at=FIXED_AT,
        )
        assert result is not None
        assert result.text == content
        assert result.full_text_source == "haiku_summary"


# ---------------------------------------------------------------------------
# Test 3: Read → verbatim, file_path set, url is None
# ---------------------------------------------------------------------------

class TestRead:
    def test_full_text_source_is_verbatim(self):
        result = make_record(
            tool_name="Read",
            tool_input={"file_path": "/project/docs/notes.md"},
            tool_response="# Notes\n\nSome content here.",
            source_id="S3",
            query_provenance="local file read",
            fetched_at=FIXED_AT,
        )
        assert result is not None
        assert result.full_text_source == "verbatim"

    def test_file_path_set(self):
        result = make_record(
            tool_name="Read",
            tool_input={"file_path": "/project/docs/notes.md"},
            tool_response="# Notes\n\nSome content here.",
            source_id="S3",
            query_provenance="local file read",
            fetched_at=FIXED_AT,
        )
        assert result.file_path == "/project/docs/notes.md"

    def test_url_is_none(self):
        result = make_record(
            tool_name="Read",
            tool_input={"file_path": "/project/docs/notes.md"},
            tool_response="# Notes\n\nSome content here.",
            source_id="S3",
            query_provenance="local file read",
            fetched_at=FIXED_AT,
        )
        assert result.url is None

    def test_text_and_sha(self):
        content = "# Notes\n\nSome content here."
        result = make_record(
            tool_name="Read",
            tool_input={"file_path": "/project/docs/notes.md"},
            tool_response=content,
            source_id="S3",
            query_provenance="local file read",
            fetched_at=FIXED_AT,
        )
        assert result.text == content
        assert result.content_sha256 == _sha(content)

    def test_captured_via_inline(self):
        result = make_record(
            tool_name="Read",
            tool_input={"file_path": "/project/docs/notes.md"},
            tool_response="content",
            source_id="S3",
            query_provenance="local file read",
            fetched_at=FIXED_AT,
        )
        assert result.captured_via == "inline"

    def test_response_as_dict_content_key(self):
        # TASK-4-VALIDATION: Read tool may sometimes return {"content": "..."}.
        content = "File contents here."
        result = make_record(
            tool_name="Read",
            tool_input={"file_path": "/project/docs/notes.md"},
            tool_response={"content": content},
            source_id="S3",
            query_provenance="local file read",
            fetched_at=FIXED_AT,
        )
        assert result is not None
        assert result.text == content
        assert result.file_path == "/project/docs/notes.md"
        assert result.url is None


# ---------------------------------------------------------------------------
# Test 4: Bash (non-retrieval) → None
# ---------------------------------------------------------------------------

class TestNonRetrievalTools:
    def test_bash_returns_none(self):
        result = make_record(
            tool_name="Bash",
            tool_input={"command": "ls -la"},
            tool_response="total 8\ndrwxr-xr-x  2 user group 64 Jun 27 10:00 .",
            source_id="S4",
            query_provenance="bash output",
            fetched_at=FIXED_AT,
        )
        assert result is None

    def test_edit_returns_none(self):
        result = make_record(
            tool_name="Edit",
            tool_input={"file_path": "/foo.py", "old_string": "a", "new_string": "b"},
            tool_response={"success": True},
            source_id="S5",
            query_provenance="edit op",
            fetched_at=FIXED_AT,
        )
        assert result is None

    def test_grep_returns_none(self):
        result = make_record(
            tool_name="Grep",
            tool_input={"pattern": "foo", "path": "."},
            tool_response="scripts/foo.py:10: def foo():",
            source_id="S6",
            query_provenance="grep search",
            fetched_at=FIXED_AT,
        )
        assert result is None

    def test_write_returns_none(self):
        result = make_record(
            tool_name="Write",
            tool_input={"file_path": "/foo.py", "content": "x=1"},
            tool_response={"success": True},
            source_id="S7",
            query_provenance="write op",
            fetched_at=FIXED_AT,
        )
        assert result is None

    def test_websearch_returns_none(self):
        # WebSearch (snippet-only, no full page text) is NOT a retrieval tool in this mapping.
        result = make_record(
            tool_name="WebSearch",
            tool_input={"query": "redis performance"},
            tool_response={"results": [{"title": "Redis", "snippet": "Fast."}]},
            source_id="S8",
            query_provenance="web search",
            fetched_at=FIXED_AT,
        )
        assert result is None

    def test_unknown_tool_returns_none(self):
        result = make_record(
            tool_name="SomeUnknownTool",
            tool_input={},
            tool_response="whatever",
            source_id="S9",
            query_provenance="unknown",
            fetched_at=FIXED_AT,
        )
        assert result is None


# ---------------------------------------------------------------------------
# Test 5: DDG fetch → verbatim
# ---------------------------------------------------------------------------

class TestDDGFetch:
    def test_ddg_fetch_content_returns_verbatim(self):
        content = "Full page content from DuckDuckGo fetch."
        result = make_record(
            tool_name="mcp__ddg-search__fetch_content",
            tool_input={"url": "https://example.com/page"},
            tool_response={"text": content},
            source_id="S10",
            query_provenance="ddg fetch",
            fetched_at=FIXED_AT,
        )
        assert result is not None
        assert result.full_text_source == "verbatim"
        assert result.url == "https://example.com/page"
        assert result.text == content

    def test_ddg_search_snippets_returns_none(self):
        # mcp__ddg-search__search returns snippets, not full content → None.
        result = make_record(
            tool_name="mcp__ddg-search__search",
            tool_input={"query": "redis performance"},
            tool_response={"results": [{"snippet": "Redis is fast."}]},
            source_id="S11",
            query_provenance="ddg search",
            fetched_at=FIXED_AT,
        )
        assert result is None


# ---------------------------------------------------------------------------
# Test 6: RetrievedSource is a frozen dataclass (not re-defined in capture_core)
# ---------------------------------------------------------------------------

class TestReturnType:
    def test_returns_retrieved_source_instance(self):
        result = make_record(
            tool_name="mcp__exa__web_fetch_exa",
            tool_input={"url": "https://example.com/"},
            tool_response={"text": "content"},
            source_id="S1",
            query_provenance="q",
            fetched_at=FIXED_AT,
        )
        assert isinstance(result, RetrievedSource)

    def test_result_is_frozen(self):
        result = make_record(
            tool_name="mcp__exa__web_fetch_exa",
            tool_input={"url": "https://example.com/"},
            tool_response={"text": "content"},
            source_id="S1",
            query_provenance="q",
            fetched_at=FIXED_AT,
        )
        with pytest.raises((AttributeError, TypeError)):
            result.text = "mutated"  # type: ignore[misc]
