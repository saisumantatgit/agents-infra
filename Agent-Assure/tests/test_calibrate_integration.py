"""Closed-loop integration test for the whole Phase-2a calibration harness.

Runs EVERY harness stage end to end over a synthetic, hand-labeled corpus that
deliberately INCLUDES a relational claim:

    emit_claim_features (2 queries, incl. a RELATIONAL claim)
      -> export_labeling_csv
      -> (human) fill human_label + load_labels
      -> join_labels
      -> sweep_thresholds
      -> select_operating_point
      -> loo_operating_point
      -> derive_report_gate (synthetic ReportLabels)
      -> emit_cr

Two things this test guarantees at the integration level:

  1. The harness composes: a <= 80-line Calibration Record is produced from
     genuinely-emitted features, real human labels, a real sweep, a real
     leave-one-out held-out estimate, and a real derived report gate.

  2. THE MERGE-BLOCKER GUARD: the relational claim (grounded via
     ground_relational's two-source rule, which never consults lex_tau) does
     NOT enter the sweep as a tier_sensitive row. Its t2_f1 is below every
     swept lex_tau, so a regression to the buggy `GROUNDED and not t1` rule
     would re-threshold it into a spurious violation at lex_tau >= t2_f1 and
     silently corrupt the held-out Error-B — the exact defect being guarded.
"""

import csv

from scripts.ground_check import RetrievedSource
from scripts.calibrate import (
    ReportLabel,
    derive_report_gate,
    emit_claim_features,
    emit_cr,
    export_labeling_csv,
    join_labels,
    load_labels,
    loo_operating_point,
    predicted_is_violation,
    select_operating_point,
    sweep_thresholds,
)


# ---------------------------------------------------------------------------
# Synthetic corpus builders.
# ---------------------------------------------------------------------------

def _src(source_id: str, text: str) -> RetrievedSource:
    """Build a minimal verbatim RetrievedSource."""
    return RetrievedSource(
        source_id=source_id,
        url=None,
        file_path=None,
        fetched_at="2026-01-01T00:00:00Z",
        tool="Read",
        content_sha256="abc",
        text=text,
        full_text_source="verbatim",
        captured_via="inline",
        query_provenance="q",
    )


# Query q1: a single RELATIONAL claim grounded across two distinct verbatim
# sources (side A in S1, side B in S2). ground_relational's two-source window
# rule grounds it WITHOUT ever consulting lex_tau.
#   q1#0  RELATIONAL  -> GROUNDED (ground_relational)  tier_sensitive False
_Q1_STORE = {
    "S1": _src(
        "S1",
        "Insulin resistance occurs when cells in your body do not respond "
        "well to insulin and cannot use glucose from your blood for energy.",
    ),
    "S2": _src(
        "S2",
        "Type 2 diabetes is a chronic metabolic condition where blood sugar "
        "levels remain elevated due to impaired insulin action.",
    ),
}
_Q1_DRAFT = "Insulin resistance causes type 2 diabetes [S1][S2]."

# Query q2: a FACTUAL claim citing an ABSENT source (a fixed, always-caught
# violation) + a NUMERIC claim grounded verbatim by T1 + a NUMERIC claim
# grounded only by T2 (tier_sensitive). Single-citation sentences so syntok
# segments them cleanly into three claims.
#   q2#0  FACTUAL   -> UNVERIFIED_CITATION  tier_sensitive False
#   q2#1  NUMERIC   -> GROUNDED via T1      tier_sensitive False
#   q2#2  NUMERIC   -> GROUNDED via T2      tier_sensitive True
_Q2_STORE = {
    "S3": _src("S3", "Redis handles 100K operations per second on commodity hardware."),
    "S4": _src(
        "S4",
        "Company filings show that revenue grew 12% year over year "
        "across the segment.",
    ),
}
_Q2_DRAFT = (
    "Solar panels reduce carbon emissions significantly [S9]. "
    "Redis handles 100K operations per second on commodity hardware [S3]. "
    "Revenue grew 12% year over year [S4]."
)

# Hand labels for the four emitted claims. Only q2#0 is a violation
# (UNVERIFIED_CITATION), and it is a FIXED, always-caught violation — so
# error_b is 0 on the full set and on every leave-one-out fold, keeping
# select_operating_point / loo_operating_point feasible at error_b_bound 0.0.
_LABELS = {
    "q1#0": "grounded",    # relational, grounded across two sources
    "q2#0": "violation",   # unverifiable citation
    "q2#1": "grounded",    # T1-grounded numeric
    "q2#2": "grounded",    # T2-grounded numeric (tier_sensitive)
}

_TAUS = [0.30, 0.65, 0.90]
_ERROR_B_BOUND = 0.0


def _fill_human_labels(src_path: str, dst_path: str, label_map: dict[str, str]) -> None:
    """Simulate the human filling in the exported labeling CSV's human_label
    column, preserving every other column and the column order."""
    with open(src_path, newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        fieldnames = list(reader.fieldnames or [])
        records = list(reader)
    for rec in records:
        rec["human_label"] = label_map[rec["claim_id"]]
    with open(dst_path, "w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(records)


def _synthetic_report_labels() -> list[ReportLabel]:
    """Cleanly-separable whole-report labels for derive_report_gate:
    max(untrustworthy)=0.70 < min(trustworthy)=0.92 -> single winning
    interval (0.70, 0.92) -> gate = midpoint = 0.81 (no multi-modal tie)."""
    return [
        ReportLabel(query_id="q1", grounding_score=0.92, trustworthy=True),
        ReportLabel(query_id="q2", grounding_score=0.95, trustworthy=True),
        ReportLabel(query_id="q3", grounding_score=0.60, trustworthy=False),
        ReportLabel(query_id="q4", grounding_score=0.70, trustworthy=False),
    ]


# ---------------------------------------------------------------------------
# THE closed-loop test.
# ---------------------------------------------------------------------------

def test_full_harness_closed_loop_produces_cr_and_guards_relational(tmp_path):
    # --- Stage 1: emit raw features for two queries (incl. a relational claim).
    rows_q1 = emit_claim_features("q1", _Q1_DRAFT, _Q1_STORE)
    rows_q2 = emit_claim_features("q2", _Q2_DRAFT, _Q2_STORE)
    rows = rows_q1 + rows_q2

    assert [r.claim_id for r in rows] == ["q1#0", "q2#0", "q2#1", "q2#2"]

    # The relational claim is present, GROUNDED, and — the blocker guard —
    # NOT tier_sensitive at emit time, despite t1_verbatim being False.
    relational_row = rows[0]
    assert relational_row.kind == "RELATIONAL"
    assert relational_row.predicted_verdict == "GROUNDED"
    assert relational_row.t1_verbatim is False
    assert relational_row.t2_f1 < min(_TAUS[1:])  # below 0.65 and 0.90
    assert relational_row.tier_sensitive is False

    # --- Stage 2: export the labeling CSV.
    export_path = str(tmp_path / "labeling.csv")
    export_labeling_csv(rows, export_path)

    # --- Stage 3: human fills human_label, then load_labels reads it back.
    filled_path = str(tmp_path / "labeling_filled.csv")
    _fill_human_labels(export_path, filled_path, _LABELS)
    labels = load_labels(filled_path)
    assert set(labels.keys()) == set(_LABELS)

    # --- Stage 4: join emitted rows against their labels.
    labeled = join_labels(rows, labels)
    assert len(labeled) == 4

    # The relational claim survives the join still NON-tier — so it can never
    # enter the sweep's lex_tau re-threshold. This is the integration-level
    # assertion of the merge-blocker guard.
    relational_labeled = next(lc for lc in labeled if lc.claim_id == "q1#0")
    assert relational_labeled.tier_sensitive is False
    # predicted_is_violation must use the FIXED verdict (GROUNDED -> not a
    # violation) at every swept lex_tau, never t2_f1 < lex_tau. If the row had
    # regressed to tier_sensitive, it would be a violation at 0.65 and 0.90.
    for tau in _TAUS:
        assert predicted_is_violation(relational_labeled, tau) is False

    # --- Stage 5: sweep thresholds.
    sweep = sweep_thresholds(labeled, _TAUS)
    assert [tau for tau, _ in sweep] == sorted(_TAUS)
    # Error-B is 0 across the whole sweep (the one violation is a fixed,
    # always-caught UNVERIFIED_CITATION) -> the bound is feasible everywhere.
    assert all(rates.error_b == 0.0 for _, rates in sweep)

    # --- Stage 6: moat-integrity operating point on the full set.
    selected_tau = select_operating_point(sweep, _ERROR_B_BOUND)
    assert selected_tau in _TAUS

    # --- Stage 7: leave-one-out genuinely-held-out rates.
    modal_tau, held_out = loo_operating_point(labeled, _TAUS, _ERROR_B_BOUND)
    assert modal_tau in _TAUS
    assert held_out.n == len(labeled)              # == n_claims below
    # The fabrication-free labeling means held-out Error-B stays 0 (the fixed
    # violation is caught in every fold); the guard is that the harness RAN and
    # produced a coherent held-out estimate, not any particular rate value.
    assert 0.0 <= held_out.error_a <= 1.0
    assert 0.0 <= held_out.error_b <= 1.0

    # --- Stage 8: derive the report gate from synthetic whole-report labels.
    report_gate = derive_report_gate(_synthetic_report_labels())
    assert report_gate == 0.81                     # midpoint(0.70, 0.92)

    # --- Stage 9: emit the Calibration Record and assert the <= 80-line ceiling.
    projection = {"lex_tau": 0.65, "gate": 0.90, "nli_tau": 0.80}
    actual = {"lex_tau": selected_tau, "gate": report_gate, "nli_tau": None}
    cr_path = str(tmp_path / "CR-integration.md")

    emit_cr(
        projection,
        actual,
        held_out,
        n_claims=len(labeled),
        n_queries=2,
        split_method="leave-one-out",
        path=cr_path,
    )

    with open(cr_path, encoding="utf-8") as fh:
        cr_content = fh.read()
    cr_lines = cr_content.splitlines()

    assert len(cr_lines) <= 80
    # The two honesty guarantees survived the whole pipeline into the CR.
    assert "n≈2 queries is calibration, not proof" in cr_content
    assert "leave-one-out" in cr_content
    assert "HELD-OUT" in cr_content
