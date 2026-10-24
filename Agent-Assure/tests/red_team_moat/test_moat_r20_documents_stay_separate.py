"""R20-01 + R20-02 — one fetched DOCUMENT is one SOURCE, and its address is never guessed.

Round 20 (2026-10-10), both reproduced by the orchestrator with its own fixtures:

* **R20-01.** `_coerce_text_value` joined an MCP response's content blocks with
  "\\n", and the gate's tokenizer is `\\w+`, so the seam was invisible: a
  verbatim span could START in one fetched document and END in another. A claim
  present in NEITHER document certified at PASS 100.0 — also under
  `--session-id`, with the report saying "retrieved this session".
* **R20-02.** A multi-URL fetch stored every document under `urls[0]`, which the
  agent orders. An anonymous blog's sentence certified at PASS 100.0 attributed
  to `https://www.who.int/...`.

**The repair.** Each content block becomes its own record, so no span can cross
from one into the next. A block's `url` is set only when it is CERTAIN: one
requested URL means every block came from it; several URLs mean the record's
`url` is None. Pairing block i with url i would assume the tool answers in
request order, which nothing here verifies — and a wrong address is a SILENT
failure, where a missing one is visible.

**Deliberately NOT changed:** `query_provenance` still takes the first URL.
Giving each block its own URL as a search label would ADD searches to the
absence count — PASS-enabling, so it belongs to Escalation #1, not to a
fail-closed run.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

_AGENT_ASSURE = Path(__file__).resolve().parents[2]
_HOOK = _AGENT_ASSURE / "scripts" / "capture_hook.py"
_GATE = _AGENT_ASSURE / "scripts" / "ground_check.py"
_SESSION = "sess-r20-docs"


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


_DOC_A = ("Regulatory filings for the period were reviewed by the external "
          "auditor. No irregularity was found in the custodial reconciliation")
_DOC_B = ("of the Frankfurt desk resulted in a restatement of 41 million euro, "
          "according to an anonymous blog post.")
_SEAM_CLAIM = ("The custodial reconciliation of the Frankfurt desk resulted in a "
               "restatement of 41 million euro [S1].\n")


def test_R20_01_a_span_cannot_cross_from_one_document_into_another(tmp_path):
    store = tmp_path / "store.jsonl"
    _capture(store, {
        "session_id": _SESSION, "tool_name": "mcp__exa__web_fetch_exa",
        "tool_input": {"urls": ["https://www.who.int/report"]},
        "tool_response": {"content": [{"type": "text", "text": _DOC_A},
                                      {"type": "text", "text": _DOC_B}]},
    })
    report = _gate(tmp_path, store, _SEAM_CLAIM)
    assert report["gate"] != "PASS", report
    assert report["per_claim"][0]["verdict"] != "GROUNDED", report


def test_each_content_block_is_stored_as_its_own_source(tmp_path):
    store = tmp_path / "store.jsonl"
    _capture(store, {
        "session_id": _SESSION, "tool_name": "mcp__exa__web_fetch_exa",
        "tool_input": {"urls": ["https://www.who.int/report"]},
        "tool_response": {"content": [{"type": "text", "text": _DOC_A},
                                      {"type": "text", "text": _DOC_B}]},
    })
    records = _records(store)
    assert [r["text"] for r in records] == [_DOC_A, _DOC_B]
    assert [r["source_id"] for r in records] == ["S1", "S2"]
    # One requested URL: every block can only have come from it.
    assert {r["url"] for r in records} == {"https://www.who.int/report"}


_WHO = "The organisation publishes weekly epidemiological updates for member states."
_BLOG = "Routine vaccination was suspended in eleven districts of Bavaria in March."


def test_R20_02_a_multi_url_fetch_never_credits_a_document_to_a_guessed_url(tmp_path):
    store = tmp_path / "store.jsonl"
    _capture(store, {
        "session_id": _SESSION, "tool_name": "mcp__exa__web_fetch_exa",
        "tool_input": {"urls": ["https://www.who.int/emergencies",
                                "https://anonymous-health-blog.example/post"]},
        "tool_response": {"content": [{"type": "text", "text": _WHO},
                                      {"type": "text", "text": _BLOG}]},
    })
    records = _records(store)
    blog = next(r for r in records if r["text"] == _BLOG)
    assert blog["url"] != "https://www.who.int/emergencies", (
        "the blog's sentence is still attributed to the WHO")
    assert blog["url"] is None, (
        "with several URLs the pairing is unverified; the address must be "
        "absent rather than guessed")


def test_POSITIVE_CONTROL_a_claim_inside_ONE_document_still_grounds(tmp_path):
    """Without this, the seam test passes on a gate that refuses everything."""
    store = tmp_path / "store.jsonl"
    _capture(store, {
        "session_id": _SESSION, "tool_name": "mcp__exa__web_fetch_exa",
        "tool_input": {"urls": ["https://www.who.int/report"]},
        "tool_response": {"content": [{"type": "text", "text": _DOC_A},
                                      {"type": "text", "text": _DOC_B}]},
    })
    claim = ("Regulatory filings for the period were reviewed by the external "
             "auditor [S1].\n")
    report = _gate(tmp_path, store, claim)
    assert report["per_claim"][0]["verdict"] == "GROUNDED", report


def test_SIBLING_the_absence_query_population_is_unchanged(tmp_path):
    """Splitting one fetch into N records must not turn one search into N:
    every block carries the same query_provenance, so `distinct` is unchanged.
    The fail-OPEN direction would be N distinct searches from one fetch."""
    store = tmp_path / "store.jsonl"
    _capture(store, {
        "session_id": _SESSION, "tool_name": "mcp__exa__web_fetch_exa",
        "tool_input": {"urls": ["https://a.example/x", "https://b.example/y"]},
        "tool_response": {"content": [{"type": "text", "text": _WHO},
                                      {"type": "text", "text": _BLOG}]},
    })
    assert len({r["query_provenance"] for r in _records(store)}) == 1
