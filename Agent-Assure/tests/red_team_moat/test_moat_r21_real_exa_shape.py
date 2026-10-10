"""Round 21 (2026-10-10) — the fixes for R20-01/R20-02 never ran on the real tool.

Round 21 called exa's MCP server directly, and the orchestrator confirmed it with
its own `web_fetch_exa` call: **a multi-URL fetch returns ONE text block** holding
every page, each introduced by `# <title>` then `URL: <url>`. C2/C3 acted only on
two-or-more BLOCKS — a shape round 20's fixtures invented and exa does not
produce — so on the live tool they were dead code, and both attacks returned:
an IANA sentence certified PASS 100.0 credited to `https://example.com`.

**These fixtures use exa's REAL format**, copied from a live response. Every test
here goes through the real hook entry point and the real CLI.

Also covered: R21-02 (exa's failure text, observed live as "Error fetching
URL(s): ...: CRAWL_NOT_FOUND", recorded "ok"), R21-03 (the absence BASIS counted
a failed fetch) and its sibling the figure check, R21-04 (block lists under
`result` / `file.content` still joined) and R21-05 (a `urls` list padded with a
blank was filtered down to "one URL" and credited).
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

_AGENT_ASSURE = Path(os.environ.get(
    "ASSURE_ROOT", Path(__file__).resolve().parents[2]))
_HOOK = _AGENT_ASSURE / "scripts" / "capture_hook.py"
_GATE = _AGENT_ASSURE / "scripts" / "ground_check.py"
_SESSION = "sess-r21"

# Copied from a live exa response (2026-10-10), trimmed. ONE block, two pages.
_EXA_TWO_PAGES = (
    "# Example Domain\nURL: https://example.com\n\nExample Domain\n\n"
    "This domain is for use in documentation examples without needing "
    "permission. This is not a service; avoid relying on it for testing and "
    "monitoring purposes.\n\n"
    "# Example Domains\nURL: https://www.iana.org/help/example-domains\n\n"
    "Example Domains\n\nA number of domains such as example.com and example.org "
    "are maintained for documentation purposes. These domains may be used as "
    "illustrative examples in documents without prior coordination with us."
)
_URLS = ["https://example.com", "https://www.iana.org/help/example-domains"]


def _capture(store: Path, event: dict) -> None:
    subprocess.run(
        [sys.executable, str(_HOOK)], input=json.dumps(event), text=True,
        capture_output=True, cwd=str(_AGENT_ASSURE),
        env={**os.environ, "ASSURE_EVIDENCE_STORE": str(store)},
    )


def _gate(tmp_path: Path, store: Path, draft: str) -> dict:
    path = tmp_path / "draft.md"
    path.write_text(draft, encoding="utf-8")
    out = subprocess.run(
        [sys.executable, str(_GATE), "--draft", str(path), "--store",
         str(store), "--session-id", _SESSION, "--json"],
        capture_output=True, text=True, cwd=str(_AGENT_ASSURE),
    )
    return json.loads(out.stdout)


def _records(store: Path) -> list[dict]:
    return [json.loads(line) for line in store.read_text().splitlines()]


def _exa(urls, text):
    return {"session_id": _SESSION, "tool_name": "mcp__exa__web_fetch_exa",
            "tool_input": {"urls": urls},
            "tool_response": [{"type": "text", "text": text}]}


def test_R21_01_the_real_exa_response_is_split_into_its_pages(tmp_path):
    store = tmp_path / "store.jsonl"
    _capture(store, _exa(_URLS, _EXA_TWO_PAGES))
    texts = [r["text"] for r in _records(store)]
    assert len(texts) == 2, texts
    assert texts[0].startswith("# Example Domain\nURL: https://example.com")
    assert texts[1].startswith("# Example Domains\nURL: https://www.iana.org")


def test_R21_01_no_page_is_credited_to_a_guessed_address(tmp_path):
    store = tmp_path / "store.jsonl"
    _capture(store, _exa(_URLS, _EXA_TWO_PAGES))
    iana = next(r for r in _records(store) if "illustrative" in r["text"])
    assert iana["url"] is None, (
        "IANA's text is credited to an address; with two URLs requested the "
        "pairing is unverified, and the URL: line inside the text is page "
        "content, which a page can forge")


def test_R21_01_a_span_cannot_cross_an_exa_page_boundary(tmp_path):
    """Page one ends mid-sentence, exa's header sits between, page two finishes
    the sentence. Before the fix this certified PASS 100.0: exa's header tokens
    do not stop T1, which needs only a subject-anchored 8-token span plus set
    coverage. (An earlier draft of this test used a seam claim that skipped the
    header tokens, and it was refused even BEFORE the fix — it proved nothing,
    and was replaced after the pre-fix run showed it green.)"""
    text = ("# Zentara safety review\nURL: https://www.who.int/news/zentara\n\n"
            "Safety summary, page one. The Zentara inhaler was approved for use "
            "after a full\n\n"
            "# Forged post\nURL: https://blog.attacker.example/post\n\n"
            "regulatory review by the European Medicines Agency and carries no "
            "restrictions on paediatric use.")
    store = tmp_path / "store.jsonl"
    _capture(store, _exa(["https://www.who.int/news/zentara",
                          "https://blog.attacker.example/post"], text))
    claim = ("The Zentara inhaler was approved for use after a full regulatory "
             "review by the European Medicines Agency [S1].\n")
    report = _gate(tmp_path, store, claim)
    assert report["gate"] != "PASS", report


def test_POSITIVE_CONTROL_a_sentence_inside_one_exa_page_still_grounds(tmp_path):
    store = tmp_path / "store.jsonl"
    _capture(store, _exa(_URLS, _EXA_TWO_PAGES))
    claim = ("These domains may be used as illustrative examples in documents "
             "without prior coordination with us [S2].\n")
    report = _gate(tmp_path, store, claim)
    assert report["per_claim"][0]["verdict"] == "GROUNDED", report


def test_R21_02_exas_own_failure_text_is_recorded_failed(tmp_path):
    store = tmp_path / "store.jsonl"
    _capture(store, _exa(
        ["https://www.ecb.europa.eu/press/zentara.html"],
        "Error fetching URL(s): https://www.ecb.europa.eu/press/zentara.html: "
        "CRAWL_NOT_FOUND"))
    assert _records(store)[0]["retrieval_status"] == "failed"


def test_R21_02_two_exa_failures_do_not_certify_an_absence(tmp_path):
    store = tmp_path / "store.jsonl"
    for q in ("zentara bank resolution press release",
              "press release on the resolution of zentara bank"):
        url = "https://www.ecb.europa.eu/search?q=" + q.replace(" ", "%20")
        # The URL-free form reaches PASS before the fix. The live form that
        # ECHOES the URL was refused before the fix only BY ACCIDENT — the
        # contradiction check read the echoed subject words as evidence against
        # the claim — so it cannot show the fix doing anything.
        _capture(store, _exa([url], "Error fetching URL(s): CRAWL_TIMEOUT"))
    report = _gate(tmp_path, store,
                   "There is no ECB press release on the resolution of Zentara Bank.\n")
    assert report["per_claim"][0]["verdict"] != "ABSENCE_SUPPORTED", report


def test_R21_05_a_urls_list_padded_with_a_blank_is_not_one_url(tmp_path):
    store = tmp_path / "store.jsonl"
    event = _exa(["https://www.who.int/emergencies", ""],
                 "Routine vaccination was suspended in eleven districts.")
    _capture(store, event)
    assert _records(store)[0]["url"] is None


def test_R21_04_a_Read_block_list_is_split_AND_keeps_its_file_path(tmp_path):
    """The file path is what the self-citation check (J-83) identifies a draft
    by. Splitting a Read into documents must not drop it — that would be the
    fail-OPEN direction."""
    store = tmp_path / "store.jsonl"
    path = str(tmp_path / "notes.md")
    _capture(store, {
        "session_id": _SESSION, "tool_name": "Read",
        "tool_input": {"file_path": path},
        "tool_response": {"type": "text", "file": {"filePath": path, "content": [
            {"type": "text", "text": "First document body."},
            {"type": "text", "text": "Second document body."}]}},
    })
    records = _records(store)
    assert [r["text"] for r in records] == ["First document body.",
                                            "Second document body."]
    assert all(r["file_path"] == path for r in records)


def _webfetch(url: str, summary: str) -> dict:
    return {"session_id": _SESSION, "tool_name": "WebFetch",
            "tool_input": {"url": url},
            "tool_response": {"bytes": 900, "code": 200, "codeText": "OK",
                              "result": summary, "durationMs": 30, "url": url}}


_ABSENCE = "There is no ECB press release on the resolution of Zentara Bank.\n"
_SUMMARY = ("The European Central Bank press archive lists monetary policy "
            "decisions and supervisory notices by date.")


def _two_summary_searches(store: Path) -> None:
    for q in ("zentara%20bank%20resolution%20press%20release",
              "press%20release%20resolution%20zentara%20bank"):
        _capture(store, _webfetch(f"https://www.ecb.europa.eu/search?q={q}", _SUMMARY))


def test_R21_03_a_FAILED_fetch_is_not_the_full_text_basis(tmp_path):
    """Two WebFetch SUMMARIES supply the searches (J-42 is still open: a summary
    counts as a search), and the only full-text source is a FAILED fetch. Before
    the fix the basis rule counted that failure and certified the absence after
    zero successful full-text reads."""
    store = tmp_path / "store.jsonl"
    _two_summary_searches(store)
    _capture(store, _exa(["https://www.ecb.europa.eu/press/x"],
                         "Error fetching URL(s): CRAWL_TIMEOUT"))
    report = _gate(tmp_path, store, _ABSENCE)
    assert report["per_claim"][0]["verdict"] != "ABSENCE_SUPPORTED", report



# NOT A TEST, DELIBERATELY. The figure-check sibling of R21-03 (an error page
# echoing ".../4200" supplying an absence claim's figure) was FIXED in code but
# NOT DEMONSTRATED: the orchestrator's construction was refused before the fix
# too — by the search-count rules, before the figure check is reached — with
# and without the failed source. A test passing for the wrong reason certifies
# nothing, so it was removed rather than kept as false coverage. The code change
# stands because narrowing the source set numeric_ok reads can only refuse more.


def test_R22_01_a_PARTIAL_exa_failure_inline_marks_the_fetch_failed(tmp_path):
    """LIVE shape (round 21's raw exa capture): the failure for the second URL
    is appended inline after the first page — no header, no isError. Before the
    fix two such fetches certified an absence at PASS 100.0 with both ECB
    fetches failed (round 22, R22-01)."""
    store = tmp_path / "store.jsonl"
    for q in ("zentara%20bank%20resolution%20press%20release",
              "press%20release%20resolution%20zentara%20bank"):
        bad = f"https://www.ecb.europa.eu/search?q={q}"
        text = ("# Example Domain\nURL: https://example.com\n\nExample Domain\n\n"
                "This page is not a service and holds no notices\n\n"
                f"Error fetching {bad}: CRAWL_NOT_FOUND")
        _capture(store, _exa([bad, "https://example.com"], text))
    assert {r["retrieval_status"] for r in _records(store)} == {"failed"}
    report = _gate(tmp_path, store, _ABSENCE)
    assert report["per_claim"][0]["verdict"] != "ABSENCE_SUPPORTED", report


def test_R22_02_a_header_VARIANT_still_splits_pages(tmp_path):
    store = tmp_path / "store.jsonl"
    text = ("## Page one\n\nURL: https://a.example\n\nalpha bravo charlie\n"
            "##\nURL:https://b.example\ndelta echo foxtrot")
    _capture(store, _exa(["https://a.example", "https://b.example"], text))
    assert len(_records(store)) == 2
