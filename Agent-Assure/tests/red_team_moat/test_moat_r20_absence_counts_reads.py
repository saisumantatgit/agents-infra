"""R20-04 + R20-06 — the absence rule counted STORED RECORDS, not SUCCESSFUL READS.

One hole, found as two in round 20 (2026-10-10) and reproduced by the
orchestrator with its own fixtures:

* **R20-04.** Two `mcp__exa__web_fetch_exa` calls that both FAILED
  (`isError: true`, an HTTP 503 body) were stored as two `verbatim` sources and
  certified *"There is no ECB press release on the resolution of Zentara
  Bank"* at **PASS 100.0 ABSENCE_SUPPORTED**, the report stating it consulted
  "2 distinct search queries and the text of 2 retrieved sources".
* **R20-06.** The same, with two fetches that returned only whitespace. An
  EMPTY block list was already refused at capture; a list holding one blank
  block was admitted — the same emptiness, fail-closed through one door and
  fail-open through the other.

**The repair is a positive requirement, not two symptom patches.** A record
counts as a SEARCH toward an absence only if it demonstrably returned content:
the capture hook now records `retrieval_status`, and a search counts only when
it is `"ok"` AND its text holds at least one word. A record written before this
field existed carries no status, and an unknown status does not count —
"I don't know" points away from PASS.

**Why the gate checks it TWICE rather than filtering the list.** Dropping a
failed search from the query list also shrinks the denominator of the
blanket-corpus-word gate, and that gate can then switch OFF and certify a claim
it used to refuse — the D-54 trap, which J-84/J-85 nearly fell into. So the
caller runs `check_absence` on the FULL population (the existing behaviour,
denominator intact) AND on the content-bearing population, and certifies only
when both agree. A conjunction with the existing verdict can only turn a yes
into a no.

**CEILING, stated so nobody reads this as closing the class.** A failure the
tool does not SIGNAL is not caught: a DDG fetch returns a plain string with no
error flag, and a captcha page, a login wall or "Access denied" HTML all arrive
as a 200 with words in them. Catching those needs a model of what a document
is, which the zero-LLM moat forbids. That remainder, together with J-36 (the
agent chooses the "query" strings), is why absence claims stay the weakest
verdict this tool emits.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
import urllib.parse
from pathlib import Path

_AGENT_ASSURE = Path(__file__).resolve().parents[2]
_HOOK = _AGENT_ASSURE / "scripts" / "capture_hook.py"
_GATE = _AGENT_ASSURE / "scripts" / "ground_check.py"

_DRAFT = "There is no ECB press release on the resolution of Zentara Bank.\n"
_QUERIES = (
    "zentara bank resolution press release",
    "press release on the resolution of zentara bank",
)
_SESSION = "sess-r20"


def _search_url(query: str) -> str:
    return "https://www.ecb.europa.eu/search?q=" + urllib.parse.quote(query)


def _exa_event(query: str, response: object) -> dict:
    return {
        "session_id": _SESSION,
        "tool_name": "mcp__exa__web_fetch_exa",
        "tool_input": {"urls": [_search_url(query)]},
        "tool_response": response,
    }


def _capture(store: Path, event: dict) -> subprocess.CompletedProcess:
    """Drive the REAL hook entry point, exactly as a live session does."""
    return subprocess.run(
        [sys.executable, str(_HOOK)],
        input=json.dumps(event), text=True, capture_output=True,
        cwd=str(_AGENT_ASSURE),
        env={**os.environ, "ASSURE_EVIDENCE_STORE": str(store)},
    )


def _gate(tmp_path: Path, store: Path) -> dict:
    draft = tmp_path / "draft.md"
    draft.write_text(_DRAFT, encoding="utf-8")
    result = subprocess.run(
        [sys.executable, str(_GATE), "--draft", str(draft),
         "--store", str(store), "--session-id", _SESSION, "--json"],
        capture_output=True, text=True, cwd=str(_AGENT_ASSURE),
    )
    return json.loads(result.stdout)


def _content(text: str) -> dict:
    return {"content": [{"type": "text", "text": text}]}


_REAL_PAGE = (
    "Search results for the European Central Bank press archive. The archive "
    "lists monetary policy decisions, supervisory notices and speeches by "
    "date. No matching documents were returned for this query."
)


def test_R20_04_two_FAILED_fetches_do_not_certify_an_absence(tmp_path):
    store = tmp_path / "store.jsonl"
    for q in _QUERIES:
        failed = {**_content("Error 503: service temporarily unavailable, "
                             "please retry later."), "isError": True}
        _capture(store, _exa_event(q, failed))
    report = _gate(tmp_path, store)
    assert report["per_claim"][0]["verdict"] != "ABSENCE_SUPPORTED", report
    assert report["gate"] != "PASS"


def test_R20_06_two_BLANK_fetches_do_not_certify_an_absence(tmp_path):
    store = tmp_path / "store.jsonl"
    for q in _QUERIES:
        _capture(store, _exa_event(q, _content("   ")))
    report = _gate(tmp_path, store)
    assert report["per_claim"][0]["verdict"] != "ABSENCE_SUPPORTED", report
    assert report["gate"] != "PASS"


def test_POSITIVE_CONTROL_two_SUCCESSFUL_fetches_still_certify(tmp_path):
    """Without this, the two tests above are satisfiable by a gate that
    refuses every absence. Same URLs, same draft, same session — only the
    retrieval outcome differs, so the refusals above are about the failures."""
    store = tmp_path / "store.jsonl"
    for q in _QUERIES:
        _capture(store, _exa_event(q, _content(_REAL_PAGE)))
    report = _gate(tmp_path, store)
    # J-97: certification demoted; the control now rests on absence_diagnostic
    assert report["per_claim"][0]["verdict"] == "UNVERIFIED_ABSENCE", report
    assert report["gate"] != "PASS"
    assert report["per_claim"][0]["absence_diagnostic"] == "searches_would_qualify", report


def test_the_hook_RECORDS_the_failure_rather_than_dropping_it(tmp_path):
    """The store is audit evidence: a failed fetch is kept, verbatim, and
    MARKED — not silently dropped and not rewritten."""
    store = tmp_path / "store.jsonl"
    failed = {**_content("Error 503: service temporarily unavailable."),
              "isError": True}
    _capture(store, _exa_event(_QUERIES[0], failed))
    _capture(store, _exa_event(_QUERIES[1], _content("   ")))
    _capture(store, _exa_event("ecb archive", _content(_REAL_PAGE)))
    records = [json.loads(line) for line in store.read_text().splitlines()]
    assert [r["retrieval_status"] for r in records] == ["failed", "failed", "ok"]
    assert records[0]["text"].startswith("Error 503"), "failure body rewritten"


def test_SIBLING_a_WebFetch_with_a_non_2xx_code_is_recorded_failed(tmp_path):
    """The native tool signals failure differently — a status code, not an
    `isError` flag. Its records feed the absence query population too."""
    store = tmp_path / "store.jsonl"
    event = {
        "session_id": _SESSION, "tool_name": "WebFetch",
        "tool_input": {"url": "https://www.ecb.europa.eu/missing"},
        "tool_response": {"bytes": 9, "code": 404, "codeText": "Not Found",
                          "result": "Not Found", "durationMs": 40,
                          "url": "https://www.ecb.europa.eu/missing"},
    }
    _capture(store, event)
    record = json.loads(store.read_text().splitlines()[0])
    assert record["retrieval_status"] == "failed"


def test_a_record_with_NO_status_is_not_counted_as_a_search(tmp_path):
    """Stores written before 2026-10-10 carry no `retrieval_status`. Whether
    those fetches returned content is UNKNOWN, and unknown points away from
    PASS. This is a deliberate Error-A on legacy stores, not an oversight."""
    store = tmp_path / "store.jsonl"
    for q in _QUERIES:
        _capture(store, _exa_event(q, _content(_REAL_PAGE)))
    legacy = []
    for line in store.read_text().splitlines():
        record = json.loads(line)
        del record["retrieval_status"]
        legacy.append(json.dumps(record))
    store.write_text("\n".join(legacy) + "\n", encoding="utf-8")
    report = _gate(tmp_path, store)
    assert report["per_claim"][0]["verdict"] != "ABSENCE_SUPPORTED", report


def test_the_report_does_not_claim_failed_fetches_were_searches(tmp_path):
    """R20-04's second half: the report said "2 distinct search queries and the
    text of 2 retrieved sources" when neither fetch returned anything. A
    refusal explained by the wrong facts sends the reader to fix the wrong
    thing (the J-82 class)."""
    store = tmp_path / "store.jsonl"
    for q in _QUERIES:
        failed = {**_content("Error 503: unavailable."), "isError": True}
        _capture(store, _exa_event(q, failed))
    basis = _gate(tmp_path, store)["per_claim"][0]["evidence_basis"]
    assert "returned no content" in basis, basis
