"""Round 9 (2026-09-13) — PROVENANCE-ONLY findings, tripwired OPEN.

The round scoped to the "closed class" that had been described as unable to
lose a red-team round. It lost three ways. Every reproduction below was re-run
by the orchestrator before being recorded.

Not fixed tonight on purpose: the R9P1 fix belongs in ``ground()`` ahead of the
kind dispatch, the R9P2 store fixes belong in ``load_store``; both are
fail-closed and small, and both deserve daylight and their own adversary.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))

import ground_check as g  # noqa: E402


def _rec(sid, text, fts="verbatim", tool="Read"):
    return {"source_id": sid, "url": None, "file_path": "/tmp/a",
            "fetched_at": "2026-09-13T00:00:00Z", "tool": tool,
            "content_sha256": "a", "text": text, "full_text_source": fts,
            "captured_via": "inline", "query_provenance": "q-" + sid}


def _run(tmp_path, draft, records):
    store = tmp_path / "s.jsonl"
    store.write_text("".join(json.dumps(r) + "\n" for r in records),
                     encoding="utf-8")
    claims = [g.classify(c) for c in g.decompose(draft)]
    return g.score_report(claims, g.load_store(str(store)))


REL = [
    _rec("S2", "Insulin resistance impairs glucose uptake and is a central "
               "mechanism that causes type 2 diabetes to develop."),
    _rec("S3", "Type 2 diabetes develops when insulin resistance progresses "
               "and the pancreas can no longer compensate."),
]

ABS = [
    {**_rec("SA1", "No recall evidence was found in the manufacturer's safety "
                   "bulletin archive for the X200 drone line."),
     "query_provenance": "recall evidence search X200 drone"},
    {**_rec("SA2", "The public recall database returned zero results for X200 "
                   "drone safety evidence."),
     "query_provenance": "regulatory database evidence query X200"},
]


@pytest.mark.xfail(strict=True, reason=(
    "R9P1-01 OPEN: ground_relational skips unresolvable citations, so a "
    "fabricated [S99] beside two real sources certifies PASS 100.0 — while "
    "evidence_basis on the same row says S99 was NEVER RETRIEVED."))
def test_relational_claim_with_fabricated_citation_is_not_certified(tmp_path):
    rep = _run(tmp_path,
               "Insulin resistance causes type 2 diabetes [S2][S3][S99].\n", REL)
    assert rep["gate"] != "PASS"


@pytest.mark.xfail(strict=True, reason=(
    "R9P1-02 OPEN: check_absence never inspects claim.citations, so an "
    "absence claim citing a source that does not exist certifies PASS 100.0."))
def test_absence_claim_with_fabricated_citation_is_not_certified(tmp_path):
    rep = _run(tmp_path,
               "[S99] We found no evidence of a safety recall affecting the "
               "X200 drone.\n", ABS)
    assert rep["gate"] != "PASS"


def test_relational_control_without_fabrication_still_passes(tmp_path):
    """Keeps the tripwire above honest: the real two-source claim DOES pass."""
    rep = _run(tmp_path,
               "Insulin resistance causes type 2 diabetes [S2][S3].\n", REL)
    assert rep["gate"] == "PASS"


@pytest.mark.xfail(strict=True, raises=None, reason=(
    "R9P2-01 OPEN: load_store accepts a duplicate source_id and keeps the LAST "
    "record, so an AI summary is laundered to verbatim by line order alone. "
    "The store is audit evidence; a self-contradicting store must raise."))
def test_duplicate_source_id_is_rejected(tmp_path):
    good = "Redis handles 100K ops per second [S1].\n"
    with pytest.raises(Exception):
        _run(tmp_path, good, [
            _rec("S1", "Redis handles 100K ops per second.", "haiku_summary",
                 "WebFetch"),
            _rec("S1", "Redis handles 100K ops per second."),
        ])


@pytest.mark.xfail(strict=True, reason=(
    "R9P2-06 OPEN: a <!-- / --> pair inside 4-space indented code blocks is "
    "code to every CommonMark renderer but is stripped as a comment, deleting "
    "the visible prose between them from the scored denominator. PASS 100.0 "
    "with 1 claim scored and 2 uncited fabrications on the page."))
def test_indented_code_comment_delimiters_do_not_delete_prose(tmp_path):
    draft = ("Redis handles 100K ops per second [S1].\n\n    <!--\n\n"
             "MongoDB lost all customer data under sustained write load.\n\n"
             "PostgreSQL silently corrupts indexes after every failover.\n\n"
             "    -->\n")
    rep = _run(tmp_path, draft, [_rec("S1", "Redis handles 100K ops per second.")])
    assert rep["gate"] != "PASS"
