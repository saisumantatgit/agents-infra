"""Round 9 (2026-09-13) — PROVENANCE-ONLY findings, tripwired OPEN.

The round scoped to the "closed class" that had been described as unable to
lose a red-team round. It lost three ways. Every reproduction below was re-run
by the orchestrator before being recorded.

R9P1-01 and R9P1-02 are CLOSED by J-25 (2026-10-01) and their regression
guard, with sibling shapes, now lives in test_moat_r9_provenance_closed.py.
R9P2-01 is CLOSED by J-26; its guard, with siblings, is in
tests/test_store_integrity.py. What remains OPEN here is R9P2-06, the
comment-stripper code detection (J-27).
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
