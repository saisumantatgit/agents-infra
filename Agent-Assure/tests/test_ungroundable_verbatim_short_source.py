"""UNGROUNDABLE on a short verbatim source (alpha walkthrough, 2026-11-15).

WHAT THE TESTER SAW. An honest draft that copies a short source nearly in full
reads UNGROUNDABLE with support diagnostic ``no_cited_verbatim_source``, although
the store line says ``full_text_source=verbatim``; the same row's evidence_basis
says "Checked verbatim against 1 cited source: S2". In a meeting-summary draft
the same refusal hid a fabricated figure (90000 where the source says 25000).

ROOT CAUSE (traced, reports/UNGROUNDABLE-SHORT-SOURCE.md). Not source
classification. ``_self_source_ids`` applies the R26-04 near-copy rule: a Read
source is treated AS THE DRAFT when >= 80% of its word bigrams occur in the
draft (``_NEAR_COPY_BIGRAM_SHARE``). A draft that quotes a short source nearly
whole meets that bar (min repro 10/11, d5 37/39, d2 42/46), so ``ground`` drops
the source from the certifying set and returns UNGROUNDABLE. Three surfaces then
disagree, which is the defect this file pins:

  1. ``evidence_basis`` ignored ``self_source_ids`` in its citation branch and
     announced a check against the very source the verdict excluded (D-35).
  2. ``support_diagnostic`` was handed a store with the source removed and
     reported "no cited verbatim source" -- the wrong reason.
  3. ``ground`` returned UNGROUNDABLE before the figure check, so a figure that
     appears in NO cited text was never reported as UNVERIFIED_NUMBER.

WHAT IS NOT FIXED HERE. Grounding the honest claim is PASS-ENABLING: by text
alone it is the same object as R26-04's "whole read of a file holding only the
claim" attack (tests/red_team_moat/test_moat_s2_near_copy.py). That is
Escalation #1 and held for Sai. It is pinned below as a STRICT xfail, so the day
the rule changes this file goes red and forces the twin attack to be re-read.
"""
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path

import pytest

_ROOT = Path(__file__).resolve().parents[1]
_GATE = _ROOT / "scripts" / "ground_check.py"

_RETRY = ("The function retry_with_backoff calls the wrapped function up to "
          "five times")
_MEETING_SRC = (
    "Meeting summary source: The platform team met on Tuesday and agreed to "
    "freeze the release branch on 14 March. Maria will own the migration "
    "checklist and Devon will review the rollback plan before the freeze. The "
    "budget request of 25000 dollars was deferred to the next quarter.")
_MEETING_DRAFT = (
    "# Meeting summary\n\n"
    "The platform team met on Tuesday and agreed to freeze the release branch "
    "on 14 March [S2].\n\n"
    "Maria will own the migration checklist and Devon will review the rollback "
    "plan before the freeze [S2].\n\n"
    "The budget request of 90000 dollars was deferred to the next quarter "
    "[S2].\n")


def _record(source_id: str, text: str) -> dict:
    """The exact record shape the alpha tester hand-built (work/mk.py)."""
    return {"source_id": source_id, "url": None,
            "file_path": f"/x/{source_id}.txt",
            "fetched_at": "2026-11-15T12:00:00Z", "tool": "Read",
            "content_sha256": hashlib.sha256(text.encode()).hexdigest(),
            "text": text, "full_text_source": "verbatim",
            "captured_via": "inline", "query_provenance": f"src {source_id}"}


def _gate(tmp_path: Path, draft: str, sources: dict[str, str]) -> dict:
    store = tmp_path / "store.jsonl"
    store.write_text("".join(json.dumps(_record(k, v)) + "\n"
                             for k, v in sources.items()), encoding="utf-8")
    draft_path = tmp_path / "draft.md"
    draft_path.write_text(draft, encoding="utf-8")
    proc = subprocess.run(
        [sys.executable, str(_GATE), "--draft", str(draft_path), "--store",
         str(store), "--json"],
        capture_output=True, text=True, cwd=str(tmp_path), check=False)
    assert proc.stdout, proc.stderr
    return json.loads(proc.stdout)


def _row(report: dict, needle: str) -> dict:
    rows = [r for r in report["per_claim"] if needle in r["text"]]
    assert len(rows) == 1, report["per_claim"]
    return rows[0]


# --- 1. the honest claim: HELD for Sai (PASS-enabling, Escalation #1) -------

@pytest.mark.xfail(strict=True, reason=(
    "HELD for Sai: textually identical to R26-04's 'file holding only the "
    "claim' attack; grounding it re-opens that shape. See "
    "reports/UNGROUNDABLE-SHORT-SOURCE.md section 7."))
def test_honest_short_verbatim_source_grounds(tmp_path):
    report = _gate(tmp_path, _RETRY + " [S1].\n", {"S1": _RETRY + ". Other."})
    assert _row(report, "retry_with_backoff")["verdict"] == "GROUNDED", report


# --- 2. the fabricated figure is refused for the RIGHT reason -----------------

def test_fabricated_number_in_near_copy_shape_reads_unverified_number(tmp_path):
    """90000 appears in no cited text. Whatever S2 is (a source, or a copy of
    the draft), the figure is unverified -- and the report must say so rather
    than hide it behind a store-shaped refusal."""
    report = _gate(tmp_path, _MEETING_DRAFT, {"S2": _MEETING_SRC})
    row = _row(report, "90000")
    assert row["verdict"] == "UNVERIFIED_NUMBER", row
    assert report["gate"] != "PASS"


def test_figure_present_in_excluded_source_stays_ungroundable(tmp_path):
    """Control for the test above: the figure check over an excluded source
    may only REFUSE. A figure that IS in the excluded text must not turn the
    claim GROUNDED -- it stays UNGROUNDABLE."""
    honest = _MEETING_DRAFT.replace("90000", "25000")
    report = _gate(tmp_path, honest, {"S2": _MEETING_SRC})
    assert _row(report, "25000")["verdict"] == "UNGROUNDABLE", report


# --- 3. verdict, evidence_basis and support_diagnostic agree ------------------

def test_evidence_basis_does_not_claim_a_check_the_verdict_excluded(tmp_path):
    report = _gate(tmp_path, _RETRY + " [S1].\n", {"S1": _RETRY + ". Other."})
    row = _row(report, "retry_with_backoff")
    assert row["verdict"] == "UNGROUNDABLE", row
    basis = row["evidence_basis"]
    assert "Checked verbatim against" not in basis, basis
    assert "S1" in basis and "copy of this draft" in basis, basis


def test_support_diagnostic_names_the_draft_not_a_missing_source(tmp_path):
    report = _gate(tmp_path, _RETRY + " [S1].\n", {"S1": _RETRY + ". Other."})
    row = _row(report, "retry_with_backoff")
    assert row["support_diagnostic"] == "cited_source_is_the_draft", row


def test_partial_exclusion_is_named_beside_the_sources_checked(tmp_path):
    """One cited source is a near-copy, another is genuine: the claim may still
    ground on the genuine one, and the basis must list only what was checked
    and name the one excluded."""
    long_src = (_RETRY + ". After each failure it sleeps for two to the power "
                "of the attempt number seconds. If the fifth attempt fails the "
                "function raises the last exception it saw. Logging is "
                "configured by the caller and defaults to the warning level.")
    report = _gate(tmp_path, _RETRY + " [S1][S2].\n",
                   {"S1": _RETRY + ". Other.", "S2": long_src})
    row = _row(report, "retry_with_backoff")
    basis = row["evidence_basis"]
    assert "Checked verbatim against 1 cited source: S2" in basis, basis
    assert "S1" in basis and "copy of this draft" in basis, basis


def test_ground_and_evidence_basis_share_one_certifying_predicate():
    """Structural guard (the J-45 pattern): the set the verdict certifies on and
    the set the display announces come from ONE function, so they cannot drift
    apart again. AST, not substring (D-41)."""
    import ast
    import inspect
    import textwrap
    sys.path.insert(0, str(_ROOT / "scripts"))
    import ground_check as g

    def calls(func) -> set[str]:
        tree = ast.parse(textwrap.dedent(inspect.getsource(func)))
        return {getattr(n.func, "id", None) or getattr(n.func, "attr", None)
                for n in ast.walk(tree) if isinstance(n, ast.Call)}

    assert "_certifying_verbatim" in calls(g.ground)
    assert "_certifying_verbatim" in calls(g.evidence_basis)
