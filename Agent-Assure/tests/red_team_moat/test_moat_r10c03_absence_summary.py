"""R10C-03 — a summary may REFUSE an absence claim, never CERTIFY one.

Round 10 adversary C: `ground()`'s ABSENCE branch passed the whole store with no
`full_text_source` filter, so a store of ONLY `haiku_summary` WebFetch records
certified "we found no evidence of X" at PASS 100.0. That breaks the invariant
named in CLAUDE.md: a haiku_summary can never ground a claim.

THE DIRECTION OF THE FIX IS A TRAP, and it is the whole point of this file.
`source_texts` is scanned for a REFUTATION of the absence. Filtering it to
verbatim would REMOVE chances to find one and make absence EASIER to certify —
fail-OPEN. So summaries remain in that scan, and what is restricted is the BASIS
for certification: at least one verbatim source must exist, and only verbatim
records may contribute the distinct searches.

That is the asymmetric-authority rule this whole system rests on, applied to
evidence rather than to a model: may add a flag, never lift one.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))

import ground_check as g  # noqa: E402

T1 = ("No recall evidence was found in the manufacturer safety bulletin "
      "archive for the X200 drone line.")
T2 = ("The public recall database returned zero results for X200 drone safety "
      "evidence.")
Q1 = "recall evidence search X200 drone"
Q2 = "regulatory database evidence query X200"
CLAIM = "We found no evidence of a safety recall affecting the X200 drone.\n"


def _rec(sid, text, qp, fts, tool):
    return {"source_id": sid, "url": "https://x.invalid/" + sid,
            "file_path": None, "fetched_at": "2026-09-13T00:00:00Z",
            "tool": tool, "content_sha256": "a" * 64, "text": text,
            "full_text_source": fts, "captured_via": "inline",
            "query_provenance": qp}


def _verb(sid, text, qp):
    return _rec(sid, text, qp, "verbatim", "Read")


def _summ(sid, text, qp):
    return _rec(sid, text, qp, "haiku_summary", "WebFetch")


def _report(tmp_path, records, draft=CLAIM):
    p = tmp_path / "s.jsonl"
    p.write_text("".join(json.dumps(r) + "\n" for r in records), encoding="utf-8")
    return g.score_report([g.classify(c) for c in g.decompose(draft)],
                          g.load_store(str(p)))


def test_store_of_only_summaries_cannot_certify_an_absence(tmp_path):
    """The reproduction. Was PASS / ABSENCE_SUPPORTED / 100.0."""
    rep = _report(tmp_path, [_summ("SA1", T1, Q1), _summ("SA2", T2, Q2)])
    assert rep["gate"] != "PASS"
    assert rep["per_claim"][0]["verdict"] == "UNVERIFIED_ABSENCE"


def test_summaries_cannot_supply_the_distinct_searches(tmp_path):
    """SIBLING: one verbatim source exists, so the basis check passes, but the
    SECOND distinct search comes only from a summary. It must not count."""
    rep = _report(tmp_path, [_verb("SA1", T1, Q1), _summ("SA2", T2, Q2)])
    assert rep["gate"] != "PASS"


def test_a_summary_may_still_REFUSE_an_absence(tmp_path):
    """The asymmetry, stated as a test. A summary that REFUTES the absence must
    still be able to block it — removing summaries from the refutation scan
    would have been fail-OPEN, which is the mistake this file exists to prevent.
    """
    refutation = _summ("SA3", "The X200 drone was recalled in March after a "
                              "battery defect was confirmed.", "recall check")
    rep = _report(tmp_path,
                  [_verb("SA1", T1, Q1), _verb("SA2", T2, Q2), refutation])
    assert rep["gate"] != "PASS", (
        "a summary refuting the absence must still be able to block it")


def test_verbatim_control_still_certifies(tmp_path):
    """Without this the fix could be 'refuse every absence claim'."""
    rep = _report(tmp_path, [_verb("SA1", T1, Q1), _verb("SA2", T2, Q2)])
    assert rep["gate"] == "PASS"
    assert rep["per_claim"][0]["verdict"] == "ABSENCE_SUPPORTED"


def test_empty_store_still_refuses(tmp_path):
    """THE NULL CASE: no sources at all must not certify."""
    rep = _report(tmp_path, [])
    assert rep["gate"] != "PASS"
