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

import csv
import dataclasses
from pathlib import Path

import pytest

from scripts.ground_check import RetrievedSource
from scripts.ground_check import _LEX_TAU_DEFAULT
from scripts.calibrate import (
    ClaimFeatureRow,
    HumanLabel,
    LabeledClaim,
    emit_claim_features,
    export_labeling_csv,
    join_labels,
    load_labels,
    predicted_is_violation,
)


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
    # S2's window is deliberately tight: the T2-only claim must clear the
    # DEPLOYED lex_tau (_LEX_TAU_DEFAULT), not merely some historical literal.
    # The looser prior wording scored 0.667 and silently pinned this test to
    # lex_tau=0.65 — it broke on the OI-CAL-01 0.65->0.71 deployment (D-06).
    s2 = _src(
        "S2",
        "Revenue grew 12% year over year.",
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
    """Claim 2: 6 content tokens, below T1's 8-token span floor — and grounded
    anyway, because the claim is EXACTLY contained in S2 (ADR-006).

    Before ADR-006 this row proved the dispatcher had used T2 (t1_verbatim was
    provably False). T2 no longer grounds anything, and this claim survived the
    demotion by a different and stronger route: the whole claim is a contiguous
    verbatim span of its source, so there is no residual to assemble and no
    ratio to game. The row is worth keeping precisely because it is the case
    that distinguishes "short" from "unsupported" — 31 of the 52 calibration
    claims are under 8 tokens, and without exact containment every one of them
    would be unreachable."""
    rows = emit_claim_features("q1", _DRAFT, _store())
    row = rows[1]
    assert row.query_id == "q1"
    assert row.claim_text == "Revenue grew 12% year over year [S2]."
    assert row.kind == "NUMERIC"
    assert row.cited_source_ids == ("S2",)
    assert row.citations_resolved is True
    assert row.t1_verbatim is True, (
        "exact containment should ground this claim via T1 (ADR-006)"
    )
    # t2_f1 is still EMITTED — as a diagnostic, never as a threshold.
    assert row.t2_f1 == pytest.approx(1.0)
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


def test_no_row_is_tier_sensitive_after_t2_demotion():
    """tier_sensitive is now False for EVERY row (ADR-006).

    The flag means "could a different lex_tau change this verdict?". Since
    ground() no longer consults lex_tau on any path, the honest answer for
    every row is no. Asserted across the whole draft rather than one row,
    because the failure this guards against is a future change quietly
    reintroducing a lexical threshold and re-enabling a sweep over verdicts
    that cannot move — which is how a fabricated operating point gets into a
    CR."""
    rows = emit_claim_features("q1", _DRAFT, _store())
    assert rows, "fixture produced no rows"
    offenders = [(r.claim_id, r.predicted_verdict) for r in rows if r.tier_sensitive]
    assert not offenders, (
        f"lex_tau governs no verdict since ADR-006, but these rows claim to be "
        f"tier_sensitive: {offenders}"
    )


def test_t1_grounded_row_is_not_tier_sensitive():
    """A T1-grounded claim (t1_verbatim True, predicted_verdict GROUNDED) is
    NOT tier_sensitive: T1 does not consult lex_tau at all, so no lex_tau
    value can flip this verdict."""
    rows = emit_claim_features("q1", _DRAFT, _store())
    row = rows[0]
    assert row.t1_verbatim is True
    assert row.predicted_verdict == "GROUNDED"
    assert row.tier_sensitive is False


def test_ungrounded_row_is_not_tier_sensitive():
    """An UNGROUNDED claim stays UNGROUNDED at any lex_tau (ADR-006).

    This test asserted the opposite until 2026-09-02: a lower lex_tau could
    once lift such a claim to GROUNDED. That path is gone — which is the whole
    point of the demotion, since it was also the path a fabrication took."""
    s3 = _src("S3", "Redis handles 100K operations per second on commodity hardware.")
    store = {"S3": s3}
    draft = "Elephants have large ears for cooling in the savanna [S3]."

    rows = emit_claim_features("q1", draft, store)
    assert len(rows) == 1
    row = rows[0]

    assert row.predicted_verdict == "UNGROUNDED"
    assert row.tier_sensitive is False


# ---------------------------------------------------------------------------
# WHOLE-BRANCH MERGE-BLOCKER regression (final review, Task 2).
#
# tier_sensitive may be True ONLY for the lex_tau-governed kinds
# {FACTUAL, ATTRIBUTION, NUMERIC} whose grounded/ungrounded outcome is decided
# by the T1/T2 tier check in ground(). RELATIONAL (ground_relational's
# two-source window rule), ABSENCE (check_absence), and NON_CLAIM (GROUNDED
# short-circuit) NEVER consult lex_tau, so their verdicts are fixed regardless
# of tau and must never be flagged tier_sensitive.
#
# The bug: `tier_sensitive = GROUNDED and not t1_verbatim` was computed for ALL
# kinds. A RELATIONAL GROUNDED claim has its two sides in DIFFERENT sources, so
# t1_verbatim is False -> it was wrongly marked tier_sensitive=True, and
# predicted_is_violation then re-thresholded its (irrelevant) t2_f1 against
# lex_tau, corrupting the sweep, the operating point, and the CR's held-out
# Error-B. Proven RED against the pre-fix code before acceptance.
# ---------------------------------------------------------------------------

def test_relational_grounded_row_is_not_tier_sensitive():
    """insulin->diabetes shape (mirrors tests/test_relational.py): side A in S1,
    side B in S2, both verbatim -> ground_relational returns GROUNDED with
    t1_verbatim False (a 6-token relational claim, too short for T1, and its two
    sides live in different sources). The verdict is FIXED regardless of lex_tau,
    so tier_sensitive MUST be False, and predicted_is_violation MUST return the
    fixed verdict-based result (NOT a violation) at EVERY lex_tau -- never the
    t2_f1<lex_tau re-threshold. This is the merge-blocker: production grounds this
    claim at every lex_tau, but the buggy tier_sensitive=True flipped it to a
    violation at lex_tau >= t2_f1, silently corrupting held-out Error-B."""
    s1 = _src(
        "S1",
        "Insulin resistance occurs when cells do not respond well to insulin. "
        "Sustained insulin resistance causes type 2 diabetes to develop. "
        # ^ OI-MOAT-05 (2026-08-30): a source must ASSERT the relation, not
        #   merely mention one endpoint — endpoint co-presence across two
        #   sources is the over-association defect (corpus q25/q26/q48).
        "Cells cannot use glucose from the blood for energy.",
    )
    s2 = _src(
        "S2",
        "Type 2 diabetes is a chronic metabolic condition where blood sugar "
        "levels remain elevated due to impaired insulin action.",
    )
    store = {"S1": s1, "S2": s2}
    draft = "Insulin resistance causes type 2 diabetes [S1][S2]."

    rows = emit_claim_features("q1", draft, store)
    assert len(rows) == 1
    row = rows[0]

    assert row.kind == "RELATIONAL"
    assert row.predicted_verdict == "GROUNDED"
    # t1_verbatim became True on 2026-09-02: ADR-006's exact-containment path
    # matches "insulin resistance causes type 2 diabetes" inside S1's "Sustained
    # insulin resistance causes type 2 diabetes to develop". Incidental to this
    # test — the verdict here comes from ground_relational, which never consults
    # a tier — and asserted rather than dropped so the change stays visible.
    assert row.t1_verbatim is True
    # t2_f1 is below 0.65: if the row were (wrongly) tier_sensitive, it would be
    # a violation at lex_tau 0.65 and 0.90 -- the exact corruption being guarded.
    assert row.t2_f1 < 0.65
    assert row.tier_sensitive is False        # RELATIONAL never consults lex_tau

    for lex_tau in (0.10, 0.65, 0.90):
        assert predicted_is_violation(row, lex_tau) is False


def test_non_claim_row_is_not_tier_sensitive():
    """A NON_CLAIM claim short-circuits to GROUNDED in ground() before the tier
    check; with no citations its t1_verbatim is False, which the buggy rule
    mis-read as tier_sensitive=True. NON_CLAIM is not a lex_tau-governed kind, so
    tier_sensitive MUST be False and predicted_is_violation is verdict-fixed."""
    rows = emit_claim_features("q1", "In conclusion.", {})
    assert len(rows) == 1
    row = rows[0]

    assert row.kind == "NON_CLAIM"
    assert row.predicted_verdict == "GROUNDED"
    assert row.t1_verbatim is False
    assert row.tier_sensitive is False
    for lex_tau in (0.10, 0.65, 0.90):
        assert predicted_is_violation(row, lex_tau) is False


# ---------------------------------------------------------------------------
# Task 3: labeling-CSV export + fail-loud label ingestion.
#
# export_labeling_csv turns ClaimFeatureRow rows into a CSV a human fills in
# with a "grounded"/"violation" verdict per claim. load_labels reads that
# filled CSV back and MUST fail loud (ValueError) on any human_label that is
# not exactly "grounded" or "violation" -- including blank -- because an
# unlabeled row silently defaulting would corrupt every threshold the
# calibration sweep later derives from it. join_labels then inner-joins
# ClaimFeatureRow rows against those labels by claim_id and MUST fail loud
# if any emitted claim has no label (no silent drop).
# ---------------------------------------------------------------------------

FIXTURES = Path(__file__).parent / "fixtures"
SYNTHETIC_LABELED_CSV = FIXTURES / "calibration" / "synthetic_labeled.csv"


def test_export_labeling_csv_writes_expected_columns(tmp_path):
    """export_labeling_csv writes the exact deterministic column order, with
    human_label left blank for the human to fill in."""
    rows = emit_claim_features("q1", _DRAFT, _store())
    out_path = tmp_path / "export.csv"

    export_labeling_csv(rows, str(out_path))

    with open(out_path, newline="", encoding="utf-8") as fh:
        reader = csv.reader(fh)
        header = next(reader)
        data_rows = list(reader)

    assert header == [
        "claim_id",
        "query_id",
        "claim_text",
        "cited_source_ids",
        "predicted_verdict",
        "t2_f1",
        "human_label",
    ]
    assert len(data_rows) == 3
    assert data_rows[0][0] == "q1#0"
    assert data_rows[0][3] == "S1"
    assert data_rows[0][4] == "GROUNDED"
    assert data_rows[0][6] == ""  # human_label: blank, for the human to fill
    assert data_rows[2][0] == "q1#2"
    assert data_rows[2][3] == "S9"
    assert data_rows[2][4] == "UNVERIFIED_CITATION"


def test_export_labeling_csv_quotes_embedded_commas(tmp_path):
    """QUOTE_MINIMAL must quote fields containing commas so they round-trip
    through a real CSV reader without corrupting column boundaries."""
    row = ClaimFeatureRow(
        claim_id="q9#0",
        query_id="q9",
        claim_text="Revenue grew, on a like-for-like basis, by 12%.",
        kind="NUMERIC",
        cited_source_ids=("S1", "S2"),
        citations_resolved=True,
        t1_verbatim=True,
        t2_f1=1.0,
        numeric_ok=True,
        predicted_verdict="GROUNDED",
        tier_sensitive=False,
    )
    out_path = tmp_path / "commas.csv"

    export_labeling_csv([row], str(out_path))

    with open(out_path, newline="", encoding="utf-8") as fh:
        record = next(csv.DictReader(fh))

    assert record["claim_text"] == "Revenue grew, on a like-for-like basis, by 12%."
    assert record["cited_source_ids"] == "S1|S2"


def test_export_labeling_csv_does_not_mutate_rows(tmp_path):
    """Pure-except-I/O contract: rows list/contents are unchanged after export."""
    rows = emit_claim_features("q1", _DRAFT, _store())
    rows_before = list(rows)

    export_labeling_csv(rows, str(tmp_path / "out.csv"))

    assert rows == rows_before


def test_load_labels_round_trip_from_synthetic_fixture():
    """load_labels reads a hand-filled CSV (3 rows, matching the emitted
    claim_ids from _DRAFT/_store()) back into 3 HumanLabel entries."""
    labels = load_labels(str(SYNTHETIC_LABELED_CSV))

    assert set(labels.keys()) == {"q1#0", "q1#1", "q1#2"}
    assert labels["q1#0"] == HumanLabel(
        claim_id="q1#0", label="grounded", violation_kind=None
    )
    assert labels["q1#1"] == HumanLabel(
        claim_id="q1#1", label="grounded", violation_kind=None
    )
    assert labels["q1#2"] == HumanLabel(
        claim_id="q1#2", label="violation", violation_kind="unverifiable_citation"
    )


def test_load_labels_raises_on_empty_human_label(tmp_path):
    """A blank human_label cell must raise ValueError, never silently pass
    through as an unlabeled row."""
    csv_text = (
        "claim_id,query_id,claim_text,cited_source_ids,predicted_verdict,"
        "t2_f1,human_label\n"
        "q1#0,q1,claim text,S1,GROUNDED,1.0,\n"
    )
    p = tmp_path / "blank_label.csv"
    p.write_text(csv_text, encoding="utf-8")

    with pytest.raises(ValueError):
        load_labels(str(p))


def test_load_labels_raises_on_invalid_human_label(tmp_path):
    """A human_label outside {"grounded", "violation"} must raise ValueError,
    never silently default."""
    csv_text = (
        "claim_id,query_id,claim_text,cited_source_ids,predicted_verdict,"
        "t2_f1,human_label\n"
        "q1#0,q1,claim text,S1,GROUNDED,1.0,maybe\n"
    )
    p = tmp_path / "invalid_label.csv"
    p.write_text(csv_text, encoding="utf-8")

    with pytest.raises(ValueError):
        load_labels(str(p))


def test_load_labels_raises_on_duplicate_claim_id(tmp_path):
    """Two rows sharing one claim_id must raise ValueError, never silently
    let the later row overwrite the earlier one in the returned dict -- a
    duplicate key discards a human label with no signal that data was
    lost."""
    csv_text = (
        "claim_id,query_id,claim_text,cited_source_ids,predicted_verdict,"
        "t2_f1,human_label\n"
        "q1#0,q1,claim text,S1,GROUNDED,1.0,grounded\n"
        "q1#0,q1,claim text,S1,GROUNDED,1.0,violation\n"
    )
    p = tmp_path / "duplicate_claim_id.csv"
    p.write_text(csv_text, encoding="utf-8")

    with pytest.raises(ValueError):
        load_labels(str(p))


def test_load_labels_normalizes_nfkc_before_validating(tmp_path):
    """A fullwidth-Unicode rendering of "grounded" must NFKC-normalize to the
    ASCII form and be accepted -- per the repo's NFKC-before-validation
    safety-gate convention, applied here to defeat homoglyph-style bypass of
    the allowed-label set."""
    fullwidth_grounded = "ｇｒｏｕｎｄｅｄ"
    csv_text = (
        "claim_id,query_id,claim_text,cited_source_ids,predicted_verdict,"
        "t2_f1,human_label\n"
        f"q1#0,q1,claim text,S1,GROUNDED,1.0,{fullwidth_grounded}\n"
    )
    p = tmp_path / "nfkc_label.csv"
    p.write_text(csv_text, encoding="utf-8")

    labels = load_labels(str(p))

    assert labels["q1#0"].label == "grounded"


def test_join_labels_round_trip_with_emitted_rows():
    """join_labels inner-joins real emitted rows against the hand-filled
    fixture's labels, in row order, carrying every ClaimFeatureRow field
    plus the human label."""
    rows = emit_claim_features("q1", _DRAFT, _store())
    labels = load_labels(str(SYNTHETIC_LABELED_CSV))

    joined = join_labels(rows, labels)

    assert len(joined) == 3
    assert [lc.claim_id for lc in joined] == ["q1#0", "q1#1", "q1#2"]

    assert joined[0].label == "grounded"
    assert joined[0].predicted_verdict == "GROUNDED"
    assert joined[0].t1_verbatim is True
    assert joined[0].tier_sensitive is False

    assert joined[2].label == "violation"
    assert joined[2].predicted_verdict == "UNVERIFIED_CITATION"
    assert joined[2].citations_resolved is False


def test_join_labels_raises_on_missing_label():
    """A claim_id emitted by emit_claim_features but absent from *labels*
    must raise ValueError -- no silent drop of unlabeled claims."""
    rows = emit_claim_features("q1", _DRAFT, _store())
    labels = {
        "q1#0": HumanLabel(claim_id="q1#0", label="grounded", violation_kind=None),
        # q1#1 and q1#2 deliberately missing.
    }

    with pytest.raises(ValueError):
        join_labels(rows, labels)


def test_human_label_is_frozen():
    """HumanLabel instances must be immutable (frozen dataclass contract)."""
    hl = HumanLabel(claim_id="q1#0", label="grounded", violation_kind=None)
    with pytest.raises(dataclasses.FrozenInstanceError):
        hl.label = "violation"  # type: ignore[misc]


def test_labeled_claim_is_frozen():
    """LabeledClaim instances must be immutable (frozen dataclass contract)."""
    lc = LabeledClaim(
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
        label="grounded",
    )
    with pytest.raises(dataclasses.FrozenInstanceError):
        lc.label = "violation"  # type: ignore[misc]


# ---------------------------------------------------------------------------
# Defense-in-depth __post_init__ label guards (fail-loud doctrine): no
# HumanLabel or LabeledClaim may carry an off-menu label. load_labels /
# join_labels already gate at their I/O boundary, but the dataclass itself
# refuses a bad label from ANY construction path — the label is the ground-truth
# crux metric error_rates keys on, so a silent bad value corrupts every derived
# rate.
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("bad_label", ["", "maybe", "GROUNDED", "grnd"])
def test_human_label_rejects_off_menu_label(bad_label):
    """HumanLabel.__post_init__ raises ValueError on any label outside
    {"grounded", "violation"}, including blank."""
    with pytest.raises(ValueError):
        HumanLabel(claim_id="q1#0", label=bad_label, violation_kind=None)


@pytest.mark.parametrize("bad_label", ["", "maybe", "VIOLATION", "ground"])
def test_labeled_claim_rejects_off_menu_label(bad_label):
    """LabeledClaim.__post_init__ raises ValueError on any label outside
    {"grounded", "violation"}, including blank."""
    with pytest.raises(ValueError):
        LabeledClaim(
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
            label=bad_label,
        )
