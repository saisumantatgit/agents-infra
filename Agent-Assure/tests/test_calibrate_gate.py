"""Tests for scripts/calibrate.py — report-gate separation-point derivation
(Task 7, spec §5.4).

``derive_report_gate`` REPLACES the provisional 0.90 report-gate placeholder
(``ground_check.score_report``'s ``threshold`` default) with the EMPIRICAL
score that best separates human-approved (trustworthy) reports from
human-rejected (untrustworthy) ones. It does NOT touch the
``UNVERIFIED_CITATION`` hard override — that is categorical, out of scope
here (spec §5.4).

THE RULE: try every threshold t that partitions the observed grounding_score
values into "predict trustworthy iff score >= t" / "predict untrustworthy
iff score < t"; return the t that maximizes the count of correctly
classified reports. Because correctness only changes AT an observed score
(never strictly between two adjacent ones), every interior candidate is
really a whole open interval of tied t values bounded by two adjacent
distinct observed scores -- so the return value is ALWAYS resolved via the
documented tie-break: the MIDPOINT of the winning interval's two bounding
scores. In the perfectly-separable case those two bounding scores are
exactly the highest untrustworthy score and the lowest trustworthy score
(spec's own phrasing); under overlap they are simply the two scores
immediately straddling the winning interval, which is the generalization
this task exercises.

TDD sequence:
  Step 1: Write tests (this file) — fail at import (derive_report_gate,
          ReportLabel absent from scripts.calibrate).
  Step 2: Run -> FAIL (proves test integrity).
  Step 3: Implement ReportLabel + derive_report_gate.
  Step 4: Run -> PASS (new + all existing 292).
"""

import pytest

from scripts.calibrate import ReportLabel, derive_report_gate


def _label(query_id: str, grounding_score: float, trustworthy: bool) -> ReportLabel:
    return ReportLabel(
        query_id=query_id, grounding_score=grounding_score, trustworthy=trustworthy
    )


# ---------------------------------------------------------------------------
# Mandatory test 1: clean separation, brief's exact fixture values.
#
#   trustworthy (approved): 0.88, 0.92, 0.95
#   untrustworthy (rejected): 0.60, 0.75, 0.84
#
# max(rejected)=0.84 < min(approved)=0.88 -> a threshold anywhere in
# (0.84, 0.88) classifies all 6 correctly (6/6); every other threshold does
# strictly worse (verified below by hand for the two flanking breakpoints).
# Tie-break: midpoint(0.84, 0.88) = 0.86, which is in (0.84, 0.88] per the
# brief.
# ---------------------------------------------------------------------------

def _clean_separation_fixture() -> list[ReportLabel]:
    return [
        _label("q1", 0.88, True),
        _label("q2", 0.92, True),
        _label("q3", 0.95, True),
        _label("q4", 0.60, False),
        _label("q5", 0.75, False),
        _label("q6", 0.84, False),
    ]


def test_clean_separation_gate_in_documented_range():
    gate = derive_report_gate(_clean_separation_fixture())
    assert 0.84 < gate <= 0.88


def test_clean_separation_gate_is_exact_midpoint():
    """Pins the exact value, not just the range: midpoint(0.84, 0.88) = 0.86.
    A test asserting only the range would pass for any value in it; this one
    fails if the tie-break lands anywhere else in that range (e.g. at 0.84 or
    0.88 themselves, which a boundary-inclusive-off-by-one bug would produce)."""
    gate = derive_report_gate(_clean_separation_fixture())
    assert gate == pytest.approx(0.86)


def test_clean_separation_gate_separates_every_report():
    """The returned gate, applied as 'trustworthy iff score >= gate', must
    reproduce every label in the clean-separation fixture exactly -- proving
    the returned float is not just numerically in range but functionally
    achieves the claimed 6/6 separation."""
    gate = derive_report_gate(_clean_separation_fixture())
    for report in _clean_separation_fixture():
        predicted_trustworthy = report.grounding_score >= gate
        assert predicted_trustworthy == report.trustworthy


# ---------------------------------------------------------------------------
# Mandatory test 2: overlapping distributions -> unique max-separation point,
# hand-computed. One inversion (a trustworthy report scores BELOW several
# untrustworthy ones), so perfect separation is impossible; the winning
# breakpoint is still unique.
#
#   trustworthy: 0.60, 0.85, 0.88          (T, n=3)
#   untrustworthy: 0.55, 0.65, 0.70, 0.95  (U, n=4)
#
# Sorted: 0.55(U) 0.60(T) 0.65(U) 0.70(U) 0.85(T) 0.88(T) 0.95(U)
#
# correct(t) = |{T: score>=t}| + |{U: score<t}|, evaluated at each interior
# breakpoint (midpoint of adjacent distinct scores):
#   (0.55,0.60)->0.575: T>=t={0.60,0.85,0.88}=3, U<t={0.55}=1        -> 4
#   (0.60,0.65)->0.625: T>=t={0.85,0.88}=2,      U<t={0.55}=1        -> 3
#   (0.65,0.70)->0.675: T>=t={0.85,0.88}=2,      U<t={0.55}=1        -> 3
#   (0.70,0.85)->0.775: T>=t={0.85,0.88}=2,      U<t={0.55,0.65,0.70}=3 -> 5  <- max
#   (0.85,0.88)->0.865: T>=t={0.88}=1,           U<t={0.55,0.65,0.70}=3 -> 4
#   (0.88,0.95)->0.915: T>=t={}=0,               U<t={0.55,0.65,0.70}=3 -> 3
#
# Unique max=5 at breakpoint (0.70, 0.85) -> gate = midpoint = 0.775.
# At that gate, 0.60(T) and 0.95(U) are the two claims the overlap forces
# onto the "wrong" side -- 5/7 correct, not 7/7, which is exactly what
# "overlapping distributions" means operationally.
# ---------------------------------------------------------------------------

def _overlapping_fixture() -> list[ReportLabel]:
    return [
        _label("t1", 0.60, True),
        _label("t2", 0.85, True),
        _label("t3", 0.88, True),
        _label("u1", 0.55, False),
        _label("u2", 0.65, False),
        _label("u3", 0.70, False),
        _label("u4", 0.95, False),
    ]


def test_overlapping_distributions_max_separation_point():
    gate = derive_report_gate(_overlapping_fixture())
    assert gate == pytest.approx(0.775)


def test_overlapping_distributions_achieves_five_of_seven():
    """The hand-computed max is 5/7, not 6/7 or 7/7 -- pins that overlap
    genuinely caps achievable separation, and that the gate found IS that
    cap (not some lower-scoring threshold)."""
    gate = derive_report_gate(_overlapping_fixture())
    correct = sum(
        1
        for r in _overlapping_fixture()
        if (r.grounding_score >= gate) == r.trustworthy
    )
    assert correct == 5


# ---------------------------------------------------------------------------
# Multi-modal tie: TWO OR MORE disjoint breakpoints achieve the identical max
# count. ADJUDICATED (controller decision, overriding the original
# implementer's undocumented "prefer widest margin" extension): this case
# now RAISES ValueError naming every tied candidate gate, rather than
# silently picking one. Rationale: a widest-margin heuristic is
# outlier-sensitive (one extreme score can swing the pick to a materially
# different, worse operating point while claiming equal sample accuracy), it
# is undocumented in the brief, and it diverges from every other genuine
# ambiguity in this module (empty input, single-class input,
# select_operating_point's no-feasible-tau), all of which RAISE rather than
# silently guess. A multi-modal tie means the report labels don't cleanly
# separate at any single threshold; the human calibrator must decide, not
# have the tool silently guess.
#
# NOTE: the brief-specified WITHIN-gap tie-break (a SINGLE winning interval
# -> midpoint of its two bounding scores) is UNCHANGED and unaffected by
# this -- see test_clean_separation_gate_is_exact_midpoint and
# test_overlapping_distributions_max_separation_point above, both of which
# still resolve to their single winning interval's midpoint.
#
#   trustworthy: 0.60, 0.62, 0.90, 0.92
#   untrustworthy: 0.55, 0.65, 0.70, 0.95
#
# Sorted: 0.55(U) 0.60(T) 0.62(T) 0.65(U) 0.70(U) 0.90(T) 0.92(T) 0.95(U)
#
#   (0.55,0.60)->0.575: T>=t=4, U<t={0.55}=1                -> 5
#   (0.60,0.62)->0.610: T>=t=3, U<t={0.55}=1                -> 4
#   (0.62,0.65)->0.635: T>=t=2, U<t={0.55}=1                -> 3
#   (0.65,0.70)->0.675: T>=t=2, U<t={0.55,0.65}=2           -> 4
#   (0.70,0.90)->0.800: T>=t=2, U<t={0.55,0.65,0.70}=3      -> 5  <- tied
#   (0.90,0.92)->0.910: T>=t=1, U<t={0.55,0.65,0.70}=3      -> 4
#   (0.92,0.95)->0.935: T>=t=0, U<t={0.55,0.65,0.70}=3      -> 3
#
# Tied at (0.55,0.60) [width 0.05] and (0.70,0.90) [width 0.20] -- two
# disjoint intervals, same max count (5/8). The removed heuristic used to
# pick the wider one (0.80); derive_report_gate now RAISES instead.
# ---------------------------------------------------------------------------

def _multimodal_tie_fixture() -> list[ReportLabel]:
    return [
        _label("t1", 0.60, True),
        _label("t2", 0.62, True),
        _label("t3", 0.90, True),
        _label("t4", 0.92, True),
        _label("u1", 0.55, False),
        _label("u2", 0.65, False),
        _label("u3", 0.70, False),
        _label("u4", 0.95, False),
    ]


def test_multimodal_tie_raises_valueerror():
    """Two disjoint breakpoints ((0.55,0.60) width 0.05 and (0.70,0.90) width
    0.20) both score 5/8. ADJUDICATED: the removed 'prefer widest margin'
    heuristic used to silently return 0.80 here; it now raises ValueError
    naming both tied candidate gates, so a human resolves the ambiguity
    rather than the tool silently guessing."""
    with pytest.raises(ValueError, match="multi-modal") as exc_info:
        derive_report_gate(_multimodal_tie_fixture())
    message = str(exc_info.value)
    assert "0.55" in message and "0.6" in message
    assert "0.7" in message and "0.9" in message


# ---------------------------------------------------------------------------
# Second, independent multi-modal-tie fixture -- proves the raise is general
# (not an artifact of one dataset shape) and demonstrates the exact
# outlier-sensitivity the adjudication flagged: a single outlier (0.02) makes
# the (0.02, 0.50) interval 0.07 WIDER than (0.58, 0.99), so the removed
# widest-margin heuristic would have picked the worse-looking end of the
# score range purely because of that one point.
#
#   untrustworthy: 0.02, 0.55, 0.58
#   trustworthy:   0.50, 0.53, 0.99
#
# Sorted: 0.02(U) 0.50(T) 0.53(T) 0.55(U) 0.58(U) 0.99(T)
#
#   (0.02,0.50)->0.26 : T>=t={0.50,0.53,0.99}=3, U<t={0.02}=1           -> 4  <- tied
#   (0.50,0.53)->0.515: T>=t={0.53,0.99}=2,      U<t={0.02}=1           -> 3
#   (0.53,0.55)->0.54 : T>=t={0.99}=1,           U<t={0.02}=1           -> 2
#   (0.55,0.58)->0.565: T>=t={0.99}=1,           U<t={0.02,0.55}=2      -> 3
#   (0.58,0.99)->0.785: T>=t={0.99}=1,           U<t={0.02,0.55,0.58}=3 -> 4  <- tied
#
# Tied at (0.02,0.50) [width 0.48] and (0.58,0.99) [width 0.41]. Before this
# fix, derive_report_gate silently returned ~0.26 here (the widest-margin
# pick) -- proven RED against the pre-fix implementation before this test
# was accepted as coverage.
# ---------------------------------------------------------------------------

def _multimodal_tie_fixture_outlier() -> list[ReportLabel]:
    return [
        _label("u1", 0.02, False),
        _label("u2", 0.55, False),
        _label("u3", 0.58, False),
        _label("t1", 0.50, True),
        _label("t2", 0.53, True),
        _label("t3", 0.99, True),
    ]


def test_multimodal_tie_raises_valueerror_names_tied_gates():
    """Before the fix, derive_report_gate silently returned ~0.26 for this
    fixture -- an outlier-sensitive pick driven entirely by the single 0.02
    score. ADJUDICATED: it must instead raise ValueError naming both tied
    candidate intervals (0.02/0.50 and 0.58/0.99), so a human resolves the
    ambiguity rather than the tool silently guessing."""
    with pytest.raises(ValueError, match="multi-modal") as exc_info:
        derive_report_gate(_multimodal_tie_fixture_outlier())
    message = str(exc_info.value)
    assert "0.02" in message and "0.5" in message
    assert "0.58" in message and "0.99" in message


# ---------------------------------------------------------------------------
# Degenerate inputs: fail loud (ValueError), never a silently-wrong number.
# Decided behavior for this task: empty / single-class / single-shared-score
# inputs give no meaningful separation to derive, so each raises ValueError
# naming the reason -- never a sentinel like 0.0, 0.5, or 1.0 masquerading as
# a real empirical threshold.
# ---------------------------------------------------------------------------

def test_empty_reports_raises():
    with pytest.raises(ValueError, match="empty"):
        derive_report_gate([])


def test_all_trustworthy_raises():
    """No untrustworthy example exists to anchor a separation boundary --
    returning any number here (e.g. 0.0, letting everything pass) would be a
    silently-fabricated threshold with zero empirical support."""
    reports = [_label("q1", 0.70, True), _label("q2", 0.90, True)]
    with pytest.raises(ValueError, match="untrustworthy"):
        derive_report_gate(reports)


def test_all_untrustworthy_raises():
    """Symmetric to the all-trustworthy case: no trustworthy example exists
    to anchor the boundary from above."""
    reports = [_label("q1", 0.30, False), _label("q2", 0.50, False)]
    with pytest.raises(ValueError, match="trustworthy"):
        derive_report_gate(reports)


def test_single_shared_score_raises():
    """Every report -- both classes -- shares one identical grounding_score.
    No threshold value can distinguish them (every t places both on the same
    side), so there is no breakpoint to derive a gate from at all."""
    reports = [
        _label("q1", 0.80, True),
        _label("q2", 0.80, False),
    ]
    with pytest.raises(ValueError):
        derive_report_gate(reports)


# ---------------------------------------------------------------------------
# Purity, determinism, dataclass frozenness.
# ---------------------------------------------------------------------------

def test_report_label_is_frozen():
    report = _label("q1", 0.90, True)
    with pytest.raises(Exception):
        report.grounding_score = 0.10  # type: ignore[misc]


def test_derive_report_gate_does_not_mutate_input():
    reports = _clean_separation_fixture()
    before = list(reports)
    derive_report_gate(reports)
    assert reports == before


def test_derive_report_gate_is_deterministic():
    reports = _overlapping_fixture()
    first = derive_report_gate(reports)
    second = derive_report_gate(reports)
    assert first == second
