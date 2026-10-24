"""H3 (2026-10-25): DuckDuckGo failure texts that are NOT shaped "Error: ..."
were stored retrieval_status "ok" and counted as a successful read.

Every failure string below is copied from the installed DDG MCP server source,
duckduckgo_mcp_server 0.7.0 (server.py md5 b7d61b6791f8aad2fd78172f36a13fa4,
uv cache), not guessed:
  * format_results_for_llm (search, no results): "No results were found for your
    search query. This could be due to DuckDuckGo's bot detection ..."
  * search tool except-branch: "An error occurred while searching: {e}"
  * _CLOUDFLARE_BODY_SIGNALS — challenge bodies that are passed through as page
    text when the curl retry is challenged too: "Just a moment...",
    "Enable JavaScript and cookies to continue", "Checking your browser before
    accessing", "cf-mitigated".
  * fetch_and_parse metadata trailer on an EMPTY page: the body is only
    "\n\n---\n[Content info: Showing characters 0-0 of 0 total ...]" — it has
    words, so the no-word rule never fired.
Every FAILURE case was seen "ok" on the pre-fix code. Refusal-only (D-69).
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

_AA = Path(__file__).resolve().parents[2]
_HOOK = _AA / "scripts" / "capture_hook.py"

_NO_RESULTS = ("No results were found for your search query. This could be due to "
               "DuckDuckGo's bot detection or the query returned no matches. Please try "
               "rephrasing your search or try again in a few minutes.")

FAILURES = {
    "no_results": _NO_RESULTS,
    "search_exception": "An error occurred while searching: ReadTimeout('timed out')",
    "cf_just_a_moment": "Just a moment...\nEnable JavaScript and cookies to continue",
    "cf_checking_browser": "Checking your browser before accessing example.com.\nThis process is automatic.",
    "cf_mitigated": "cf-mitigated: challenge\nPlease wait while we verify you are human.",
    "empty_page_trailer": "\n\n---\n[Content info: Showing characters 0-0 of 0 total | cache=miss]",
    "empty_page_trailer_parse": "\n\n---\n[Content info: Showing characters 0-0 of 0 total | parse=markdown]",
    "json_wrapped_no_results": json.dumps({"result": _NO_RESULTS}),
}


def _ddg_status(tmp_path: Path, body: str) -> str:
    store = tmp_path / "store.jsonl"
    out = subprocess.run(
        [sys.executable, str(_HOOK)],
        input=json.dumps({"session_id": "sess-h3", "tool_name": "mcp__ddg-search__fetch_content",
                          "tool_input": {"url": "https://example.com/page"}, "tool_response": body}),
        text=True, capture_output=True, cwd=str(_AA),
        env={**os.environ, "ASSURE_EVIDENCE_STORE": str(store)},
    )
    lines = store.read_text(encoding="utf-8").splitlines() if store.exists() else []
    assert len(lines) == 1, (out.returncode, out.stderr)
    return json.loads(lines[0])["retrieval_status"]


@pytest.mark.parametrize("name", sorted(FAILURES))
def test_h3_ddg_failure_text_is_not_ok(tmp_path: Path, name: str) -> None:
    assert _ddg_status(tmp_path, FAILURES[name]) != "ok", name


CONTROLS = {
    "real_page": ("Redis is an in-memory data store used as a cache.\n\n---\n"
                  "[Content info: Showing characters 0-52 of 52 total | cache=miss]"),
    "page_mentioning_results": "The study found no results were significant at p<0.05.",
}


@pytest.mark.parametrize("name", sorted(CONTROLS))
def test_h3_control_real_page_stays_ok(tmp_path: Path, name: str) -> None:
    assert _ddg_status(tmp_path, CONTROLS[name]) == "ok", name
