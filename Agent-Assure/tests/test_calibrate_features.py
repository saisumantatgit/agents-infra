"""Tests for scripts/calibrate.py — per-claim raw feature emission (Task 2).

Phase 2a calibration harness. emit_claim_features runs
decompose -> classify -> ground per claim and records the RAW tier features
(t1_verbatim, t2_f1 via t2_lexical_score, numeric_ok) alongside the CURRENT
predicted_verdict, so a later calibration sweep can re-threshold lex_tau /
min_quote_len post-hoc over the stored features without re-running the
pipeline.

TDD sequence:
  Step 1: Write tests (this file) — fail at import (scripts.calibrate does
          not exist yet).
  Step 2: Run -> FAIL (proves test integrity).
  Step 3: Implement ClaimFeatureRow + emit_claim_features in
          scripts/calibrate.py.
  Step 4: Run -> PASS (new + all existing).
"""

import dataclasses

import pytest

from scripts.ground_check import RetrievedSource
from scripts.calibrate import ClaimFeatureRow, emit_claim_features


# ---------------------------------------------------------------------------
# Fixture store: 2 sources (S1, S2) — S9 is deliberately absent.
# ---------------------------------------------------------------------------

def _src(source_id: str, text: str) -> RetrievedSource:
    """Build a minimal verbatim RetrievedSource (mirrors tests/test_ground.py)."""
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


def _store() -> dict[str, RetrievedSource]:
    s1 = _src("S1", "Redis handles 100K operations per second on commodity hardware.")
    s2 = _src(
        "S2",
        "Company filings show that revenue grew 12% year over year "
        "across the segment.",
    )
    return {"S1": s1, "S2": s2}


# Draft with exactly 3 claims:
#   1. T1-grounded  — cites [S1], exact verbatim 9-token span in S1.
#   2. T2-only-grounded — cites [S2], too short for T1 (6 content tokens
#      < min_quote_len=8) but high content-word F1 over an S2 window.
#   3. Absent citation — cites [S9], which is not in the store.
_DRAFT = (
    "Redis handles 100K operations per second on commodity hardware [S1]. "
    "Revenue grew 12% year over year [S2]. "
    "Solar panels reduce carbon emissions significantly [S9]."
)


# ---------------------------------------------------------------------------
# emit_claim_features: row count, ordering, per-field values
# ---------------------------------------------------------------------------

def test_emits_one_row_per_claim():
    """3-claim draft over a 2-source store yields exactly 3 rows, in claim order."""
    rows = emit_claim_features("q1", _DRAFT, _store())
    assert len(rows) == 3
    assert [r.claim_id for r in rows] == ["q1#0", "q1#1", "q1#2"]


def test_t1_grounded_claim_row():
    """Claim 1: exact verbatim span in S1 -> t1_verbatim=True, resolved citation,
    predicted_verdict=GROUNDED. t2_f1 is also recorded (claim text is a near-exact
    subset of S1's single-sentence text, so F1 == 1.0)."""
    rows = emit_claim_features("q1", _DRAFT, _store())
    row = rows[0]
    assert row.query_id == "q1"
    assert row.claim_text == (
        "Redis handles 100K operations per second on commodity hardware [S1]."
    )
    assert row.kind == "NUMERIC"
    assert row.cited_source_ids == ("S1",)
    assert row.citations_resolved is True
    assert row.t1_verbatim is True
    assert row.t2_f1 == pytest.approx(1.0)
    assert row.numeric_ok is True
    assert row.predicted_verdict == "GROUNDED"


def test_t2_only_grounded_claim_row():
    """Claim 2: too short for T1 (6 content tokens < min_quote_len=8) but scores
    high lexical F1 against an S2 window -> t1_verbatim=False, t2_f1 high enough
    to ground, predicted_verdict=GROUNDED via the T2 path (proves the dispatcher
    used T2, not T1, since T1 is provably False here)."""
    rows = emit_claim_features("q1", _DRAFT, _store())
    row = rows[1]
    assert row.query_id == "q1"
    assert row.claim_text == "Revenue grew 12% year over year [S2]."
    assert row.kind == "NUMERIC"
    assert row.cited_source_ids == ("S2",)
    assert row.citations_resolved is True
    assert row.t1_verbatim is False
    assert row.t2_f1 == pytest.approx(2 / 3)
    assert row.t2_f1 >= 0.65  # the actual grounding threshold this claim clears
    assert row.numeric_ok is True
    assert row.predicted_verdict == "GROUNDED"


def test_absent_citation_claim_row():
    """Claim 3: cites [S9], absent from the store -> citations_resolved=False,
    no verbatim evidence to score (t1_verbatim=False, t2_f1=0.0), and
    predicted_verdict=UNVERIFIED_CITATION (the verdict ground() reserves
    exclusively for this branch)."""
    rows = emit_claim_features("q1", _DRAFT, _store())
    row = rows[2]
    assert row.query_id == "q1"
    assert row.claim_text == "Solar panels reduce carbon emissions significantly [S9]."
    assert row.kind == "FACTUAL"
    assert row.cited_source_ids == ("S9",)
    assert row.citations_resolved is False
    assert row.t1_verbatim is False
    assert row.t2_f1 == 0.0
    assert row.predicted_verdict == "UNVERIFIED_CITATION"


# ---------------------------------------------------------------------------
# Structural contract: frozen dataclass, pure function
# ---------------------------------------------------------------------------

def test_claim_feature_row_is_frozen():
    """ClaimFeatureRow instances must be immutable (frozen dataclass contract)."""
    row = ClaimFeatureRow(
        claim_id="q1#0",
        query_id="q1",
        claim_text="x",
        kind="FACTUAL",
        cited_source_ids=(),
        citations_resolved=True,
        t1_verbatim=False,
        t2_f1=0.0,
        numeric_ok=True,
        predicted_verdict="UNCITED",
        tier_sensitive=False,
    )
    with pytest.raises(dataclasses.FrozenInstanceError):
        row.claim_text = "y"  # type: ignore[misc]


def test_emit_claim_features_does_not_mutate_store():
    """Pure function contract: the input store dict must be unchanged after the call."""
    store = _store()
    store_ids_before = sorted(store.keys())
    emit_claim_features("q1", _DRAFT, store)
    assert sorted(store.keys()) == store_ids_before


# ---------------------------------------------------------------------------
# tier_sensitive: only GROUNDED-via-T2 and UNGROUNDED flip with lex_tau.
#
# Reviewer finding: ground() runs its "any resolved source has falsy text"
# check across ALL cited sources (verbatim + non-verbatim) BEFORE narrowing
# to verbatim, while _resolve_verbatim_sources narrows to verbatim FIRST.
# A claim can therefore show maximal raw signal (t1_verbatim=True, t2_f1=1.0)
# from its verbatim citation while predicted_verdict is UNGROUNDABLE, because
# a co-cited non-verbatim source with empty text short-circuits ground()
# first. A calibration sweep that re-thresholds lex_tau over t2_f1 for such a
# row would miscount — the row is fixed regardless of lex_tau.
# ---------------------------------------------------------------------------

def _non_verbatim_src(source_id: str, full_text_source: str = "haiku_summary") -> RetrievedSource:
    """Build a RetrievedSource with empty text and a non-verbatim source type."""
    return RetrievedSource(
        source_id=source_id,
        url=None,
        file_path=None,
        fetched_at="2026-01-01T00:00:00Z",
        tool="Read",
        content_sha256="def",
        text="",
        full_text_source=full_text_source,
        captured_via="inline",
        query_provenance="q",
    )


def test_ungroundable_with_high_tier_signal_is_not_tier_sensitive():
    """Reviewer's counter-case: a claim citing BOTH a verbatim source with an
    exact matching span (driving t1_verbatim=True, t2_f1=1.0) AND a second
    cited source that is non-verbatim with empty text.

    ground() resolves both citations, then checks `any(not s.text for s in
    sources)` across ALL resolved sources (verbatim + non-verbatim) BEFORE
    narrowing to verbatim -> the empty-text non-verbatim source trips this
    check first, so predicted_verdict == UNGROUNDABLE despite maximal T1/T2
    signal. tier_sensitive must be False: UNGROUNDABLE is lex_tau-invariant,
    so re-thresholding lex_tau over this row's t2_f1 would miscount it.
    """
    s1 = _src("S1", "Redis handles 100K operations per second on commodity hardware.")
    s2 = _non_verbatim_src("S2")
    store = {"S1": s1, "S2": s2}
    draft = "Redis handles 100K operations per second on commodity hardware [S1][S2]."

    rows = emit_claim_features("q1", draft, store)
    assert len(rows) == 1
    row = rows[0]

    # High raw tier signal from the verbatim citation alone.
    assert row.t1_verbatim is True
    assert row.t2_f1 == pytest.approx(1.0)

    # Yet ground() short-circuits on the co-cited empty-text source.
    assert row.predicted_verdict == "UNGROUNDABLE"
    assert row.tier_sensitive is False


def test_t2_only_grounded_row_is_tier_sensitive():
    """A T2-only-grounded claim (t1_verbatim False, predicted_verdict GROUNDED)
    is tier_sensitive: a higher lex_tau could push it below threshold and flip
    it to UNGROUNDED."""
    rows = emit_claim_features("q1", _DRAFT, _store())
    row = rows[1]
    assert row.t1_verbatim is False
    assert row.predicted_verdict == "GROUNDED"
    assert row.tier_sensitive is True


def test_t1_grounded_row_is_not_tier_sensitive():
    """A T1-grounded claim (t1_verbatim True, predicted_verdict GROUNDED) is
    NOT tier_sensitive: T1 does not consult lex_tau at all, so no lex_tau
    value can flip this verdict."""
    rows = emit_claim_features("q1", _DRAFT, _store())
    row = rows[0]
    assert row.t1_verbatim is True
    assert row.predicted_verdict == "GROUNDED"
    assert row.tier_sensitive is False


def test_ungrounded_row_is_tier_sensitive():
    """An UNGROUNDED claim (verbatim evidence exists but T1/T2 both miss) is
    tier_sensitive: a lower lex_tau could push its t2_f1 above threshold and
    flip it to GROUNDED."""
    s3 = _src("S3", "Redis handles 100K operations per second on commodity hardware.")
    store = {"S3": s3}
    draft = "Elephants have large ears for cooling in the savanna [S3]."

    rows = emit_claim_features("q1", draft, store)
    assert len(rows) == 1
    row = rows[0]

    assert row.predicted_verdict == "UNGROUNDED"
    assert row.tier_sensitive is True
