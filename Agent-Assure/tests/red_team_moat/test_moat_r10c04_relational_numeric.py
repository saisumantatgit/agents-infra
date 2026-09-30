"""R10C-04 — the relation was corroborated and the FIGURE was never checked.

`classify` orders RELATIONAL ahead of NUMERIC, and `ground()`'s relational
branch returned above the numeric branch. So a number inside a relational claim
was never looked at: "Insulin resistance causes 97% of all type 2 diabetes"
certified GROUNDED at PASS 100.0 against a store containing no percentage.

That is the worst shape a grounding error can take for a reader, because the
FIGURE is the part they quote. The relation ("causes") was genuinely
corroborated by two sources, which is exactly what makes the number look safe.

The fix is fail-closed: it can only downgrade an otherwise-GROUNDED relational
claim to UNVERIFIED_NUMBER, never create a PASS.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))

import ground_check as g  # noqa: E402


def _rec(sid, text):
    return {"source_id": sid, "url": None, "file_path": "/tmp/a",
            "fetched_at": "2026-09-13T00:00:00Z", "tool": "Read",
            "content_sha256": "a" * 64, "text": text,
            "full_text_source": "verbatim", "captured_via": "inline",
            "query_provenance": "q-" + sid}


NO_NUMBER = [
    _rec("S2", "Insulin resistance impairs glucose uptake and is a central "
               "mechanism that causes type 2 diabetes to develop."),
    _rec("S3", "Type 2 diabetes develops when insulin resistance progresses "
               "and the pancreas can no longer compensate."),
]

WITH_97 = [
    _rec("S2", "Insulin resistance impairs glucose uptake and causes 97% of "
               "type 2 diabetes to develop."),
    _rec("S3", "Type 2 diabetes develops in 97% of cases when insulin "
               "resistance progresses and the pancreas cannot compensate."),
]


def _report(tmp_path, draft, records):
    p = tmp_path / "s.jsonl"
    p.write_text("".join(json.dumps(r) + "\n" for r in records), encoding="utf-8")
    return g.score_report([g.classify(c) for c in g.decompose(draft)],
                          g.load_store(str(p)))


@pytest.mark.parametrize("figure", [
    "97% of all",        # percentage absent from the store
    "4321 cases of",     # count absent from the store
    "12.5% of all",      # decimal percentage
])
def test_a_figure_absent_from_the_store_is_refused(tmp_path, figure):
    rep = _report(tmp_path,
                  f"Insulin resistance causes {figure} type 2 diabetes "
                  f"[S2][S3].\n", NO_NUMBER)
    assert rep["per_claim"][0]["verdict"] == "UNVERIFIED_NUMBER"
    assert rep["gate"] != "PASS"


def test_the_relation_is_still_corroborated_without_a_figure(tmp_path):
    """CONTROL. The fix must not break relational grounding itself — otherwise
    it is 'refuse all relational claims' wearing a numeric costume."""
    rep = _report(tmp_path,
                  "Insulin resistance causes type 2 diabetes [S2][S3].\n",
                  NO_NUMBER)
    assert rep["per_claim"][0]["verdict"] == "GROUNDED"
    assert rep["gate"] == "PASS"


def test_a_figure_PRESENT_in_the_store_still_certifies(tmp_path):
    """The control that matters most: this must not become 'any number fails'."""
    rep = _report(tmp_path,
                  "Insulin resistance causes 97% of all type 2 diabetes "
                  "[S2][S3].\n", WITH_97)
    assert rep["per_claim"][0]["verdict"] == "GROUNDED"
    assert rep["gate"] == "PASS"


def test_percent_does_not_match_a_bare_number(tmp_path):
    """numeric_ok treats percent and absolute as distinct units. A relational
    claim must inherit that, or the fix leaks the exact confusion it inherits
    the machinery to prevent."""
    bare = [
        _rec("S2", "Insulin resistance impairs glucose uptake and causes 97 "
                   "distinct downstream effects that lead to type 2 diabetes."),
        _rec("S3", "Type 2 diabetes develops in 97 separate documented "
                   "pathways when insulin resistance progresses."),
    ]
    rep = _report(tmp_path,
                  "Insulin resistance causes 97% of all type 2 diabetes "
                  "[S2][S3].\n", bare)
    assert rep["gate"] != "PASS"
