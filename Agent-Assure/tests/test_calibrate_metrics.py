"""Tests for scripts/calibrate.py — Error-A / Error-B at a threshold (Task 4).

THE CRUX of the calibration harness. The positive class is pinned to
"claim is a grounding VIOLATION" — the gate is a violation detector. The two
error types are asymmetric and the whole calibration bias depends on keeping
them distinct:

  * Error A (false positive, ``fp``) — a truly-GROUNDED claim the gate FLAGS
    as a violation. Recoverable: it lands in an appendix a human sees.
  * Error B (false negative, ``fn``) — a truly-VIOLATION claim the gate PASSES
    as grounded. UNRECOVERABLE: a fabrication ships inside a "verified" report.
    This is THE error the whole tool exists to prevent.

``predicted_is_violation(row, lex_tau)`` recomputes the gate's violation call
at a candidate ``lex_tau`` and MUST key on ``row.tier_sensitive``:
  * tier_sensitive rows flip with lex_tau → violation iff ``row.t2_f1 < lex_tau``
    (strict: below the T2 threshold → UNGROUNDED → violation). predicted_verdict
    is IGNORED for these rows — it is recomputed from t2_f1.
  * non-tier_sensitive rows have a FIXED verdict → violation iff
    ``row.predicted_verdict not in ("GROUNDED", "ABSENCE_SUPPORTED")``, regardless
    of lex_tau. A high-t2_f1 UNGROUNDABLE row stays a violation at EVERY lex_tau.

``error_rates(labeled, lex_tau)`` returns a frozen ``ErrorRates`` with, for
positive = violation: ``tp`` (violation predicted violation), ``fp``/Error-A
(grounded predicted violation), ``tn`` (grounded predicted grounded),
``fn``/Error-B (violation predicted grounded), plus
``error_a = fp/(fp+tn)`` and ``error_b = fn/(fn+tp)`` (0.0 on a zero denominator,
counts still exposed).

TDD sequence:
  Step 1: Write tests (this file) — fail at import (predicted_is_violation,
          ErrorRates, error_rates do not exist yet).
  Step 2: Run -> FAIL (proves test integrity).
  Step 3: Implement predicted_is_violation + ErrorRates + error_rates.
  Step 4: Run -> PASS (new + all existing).
"""

import dataclasses

import pytest

from scripts.calibrate import (
    ErrorRates,
    LabeledClaim,
    error_rates,
    predicted_is_violation,
)


# ---------------------------------------------------------------------------
# Fixture builder: construct a LabeledClaim with full control over the three
# fields predicted_is_violation reads (tier_sensitive, t2_f1, predicted_verdict)
# and the ground-truth label. Everything else is filler that does not affect
# the classification under test.
# ---------------------------------------------------------------------------

def _labeled(
    claim_id: str,
    *,
    label: str,
    tier_sensitive: bool,
    t2_f1: float,
    predicted_verdict: str,
) -> LabeledClaim:
    return LabeledClaim(
        claim_id=claim_id,
        query_id="q1",
        claim_text=f"claim {claim_id}",
        kind="FACTUAL",
        cited_source_ids=("S1",),
        citations_resolved=True,
        t1_verbatim=False,
        t2_f1=t2_f1,
        numeric_ok=True,
        predicted_verdict=predicted_verdict,
        tier_sensitive=tier_sensitive,
        label=label,
    )


# ---------------------------------------------------------------------------
# predicted_is_violation — tier_sensitive rows key on t2_f1 < lex_tau (strict).
# ---------------------------------------------------------------------------

def test_tier_sensitive_violation_when_t2f1_below_lex_tau():
    """tier_sensitive row with t2_f1 strictly below lex_tau → violation."""
    row = _labeled("q1#0", label="violation", tier_sensitive=True, t2_f1=0.30,
                   predicted_verdict="UNGROUNDED")
    assert predicted_is_violation(row, 0.65) is True


def test_tier_sensitive_grounded_when_t2f1_at_or_above_lex_tau():
    """tier_sensitive row with t2_f1 at/above lex_tau → NOT a violation."""
    row = _labeled("q1#0", label="grounded", tier_sensitive=True, t2_f1=0.90,
                   predicted_verdict="GROUNDED")
    assert predicted_is_violation(row, 0.65) is False


def test_tier_sensitive_boundary_is_strict_less_than():
    """t2_f1 == lex_tau is NOT a violation — the threshold is strict `<`, so a
    claim exactly at the bar counts as grounded (UNGROUNDED is `t2_f1 < lex_tau`).
    An off-by-one flip to `<=` here would silently reclassify boundary claims."""
    row = _labeled("q1#0", label="grounded", tier_sensitive=True, t2_f1=0.65,
                   predicted_verdict="GROUNDED")
    assert predicted_is_violation(row, 0.65) is False


def test_tier_sensitive_ignores_predicted_verdict_grounded_string():
    """For a tier_sensitive row, predicted_is_violation recomputes from t2_f1 and
    MUST NOT read predicted_verdict. A row whose stored verdict LOOKS grounded
    ("GROUNDED") but whose t2_f1 is below lex_tau is a violation at that lex_tau."""
    row = _labeled("q1#0", label="violation", tier_sensitive=True, t2_f1=0.30,
                   predicted_verdict="GROUNDED")
    assert predicted_is_violation(row, 0.65) is True


def test_tier_sensitive_ignores_predicted_verdict_ungrounded_string():
    """Mirror of the above: a tier_sensitive row whose stored verdict LOOKS like a
    violation ("UNGROUNDED") but whose t2_f1 clears lex_tau is NOT a violation at
    that lex_tau. Proves predicted_verdict is ignored for tier rows."""
    row = _labeled("q1#0", label="grounded", tier_sensitive=True, t2_f1=0.90,
                   predicted_verdict="UNGROUNDED")
    assert predicted_is_violation(row, 0.65) is False


# ---------------------------------------------------------------------------
# predicted_is_violation — non-tier rows key on predicted_verdict (FIXED).
# ---------------------------------------------------------------------------

def test_non_tier_grounded_verdict_is_not_violation():
    """non-tier GROUNDED (T1) row is never a violation, at any lex_tau."""
    row = _labeled("q1#0", label="grounded", tier_sensitive=False, t2_f1=1.0,
                   predicted_verdict="GROUNDED")
    for lex_tau in (0.0, 0.5, 0.65, 1.0):
        assert predicted_is_violation(row, lex_tau) is False


def test_non_tier_absence_supported_is_not_violation():
    """non-tier ABSENCE_SUPPORTED is grounded — it is in the numerator set."""
    row = _labeled("q1#0", label="grounded", tier_sensitive=False, t2_f1=0.0,
                   predicted_verdict="ABSENCE_SUPPORTED")
    assert predicted_is_violation(row, 0.65) is False


def test_non_tier_ungroundable_high_t2f1_stays_violation_at_every_lex_tau():
    """Task-2 reviewer counter-case: a non-tier_sensitive row with HIGH t2_f1
    (1.0) but verdict UNGROUNDABLE must stay a violation at EVERY lex_tau —
    including lex_tau values (0.0, 1.0) at which a tier_sensitive row with the
    same t2_f1 would be grounded. Lowering lex_tau must NOT spuriously re-ground
    it: the dispatcher never reached the tier check for this claim."""
    row = _labeled("q1#0", label="violation", tier_sensitive=False, t2_f1=1.0,
                   predicted_verdict="UNGROUNDABLE")
    for lex_tau in (0.0, 0.5, 0.65, 0.99, 1.0):
        assert predicted_is_violation(row, lex_tau) is True


def test_non_tier_unverified_citation_is_violation():
    """non-tier UNVERIFIED_CITATION is a violation regardless of lex_tau."""
    row = _labeled("q1#0", label="violation", tier_sensitive=False, t2_f1=0.0,
                   predicted_verdict="UNVERIFIED_CITATION")
    assert predicted_is_violation(row, 0.65) is True


# ---------------------------------------------------------------------------
# THE mandatory fixture: exact tp/fp/tn/fn at lex_tau = 0.65.
#
# 9 claims, deliberately built so that EVERY confusable pair differs — so any
# single-point error changes an asserted number and is caught:
#   * error_a (0.20) != error_b (0.50)            -> catches an error_a<->error_b swap
#   * fp (1) != fn (2), tp (2) != tn (4)           -> catches an fp<->fn / tp<->tn swap
#   * grounded_total (5) != violation_total (4)    -> catches a denominator swap
#     (a fixture with equal denominators would let a denominator swap pass).
#
#  claim  tier  t2_f1  verdict            label      pred@0.65  cell
#  G1     F     1.00   GROUNDED           grounded   grounded   tn
#  G2     F     0.00   ABSENCE_SUPPORTED  grounded   grounded   tn
#  G3     T     0.80   GROUNDED           grounded   grounded   tn
#  G4     T     0.75   GROUNDED           grounded   grounded   tn
#  G5     T     0.40   UNGROUNDED         grounded   VIOLATION  fp  (Error-A)
#  V1     T     0.90   GROUNDED           violation  grounded   fn  (Error-B *)
#  V2     F     1.00   UNGROUNDABLE       violation  VIOLATION  tp
#  V3     T     0.20   UNGROUNDED         violation  VIOLATION  tp
#  V4     T     0.70   GROUNDED           violation  grounded   fn  (Error-B)
#
#  tp=2 (V2,V3)  fp=1 (G5)  tn=4 (G1,G2,G3,G4)  fn=2 (V1,V4)  n=9
#  grounded_total = fp+tn = 5 ;  violation_total = fn+tp = 4
#  error_a = fp/(fp+tn) = 1/5 = 0.20
#  error_b = fn/(fn+tp) = 2/4 = 0.50
#
#  (* V1 is the fabrication-passed claim: a violation-labeled claim with HIGH
#     t2_f1 (0.90 ≥ 0.65) the gate PASSES as grounded — counted as Error-B/fn,
#     the unrecoverable error. This is the non-tautological heart of the test:
#     the scenario is constructed by hand and the classification asserted.)
# ---------------------------------------------------------------------------

def _crux_fixture() -> list[LabeledClaim]:
    return [
        _labeled("q1#0", label="grounded", tier_sensitive=False, t2_f1=1.00,
                 predicted_verdict="GROUNDED"),            # G1 -> tn
        _labeled("q1#1", label="grounded", tier_sensitive=False, t2_f1=0.00,
                 predicted_verdict="ABSENCE_SUPPORTED"),   # G2 -> tn
        _labeled("q1#2", label="grounded", tier_sensitive=True, t2_f1=0.80,
                 predicted_verdict="GROUNDED"),            # G3 -> tn
        _labeled("q1#3", label="grounded", tier_sensitive=True, t2_f1=0.75,
                 predicted_verdict="GROUNDED"),            # G4 -> tn
        _labeled("q1#4", label="grounded", tier_sensitive=True, t2_f1=0.40,
                 predicted_verdict="UNGROUNDED"),          # G5 -> fp (Error-A)
        _labeled("q1#5", label="violation", tier_sensitive=True, t2_f1=0.90,
                 predicted_verdict="GROUNDED"),            # V1 -> fn (Error-B *)
        _labeled("q1#6", label="violation", tier_sensitive=False, t2_f1=1.00,
                 predicted_verdict="UNGROUNDABLE"),        # V2 -> tp
        _labeled("q1#7", label="violation", tier_sensitive=True, t2_f1=0.20,
                 predicted_verdict="UNGROUNDED"),          # V3 -> tp
        _labeled("q1#8", label="violation", tier_sensitive=True, t2_f1=0.70,
                 predicted_verdict="GROUNDED"),            # V4 -> fn (Error-B)
    ]


def test_crux_counts_exact_at_lex_tau_065():
    """Hand-computed confusion counts at lex_tau=0.65 over the 9-claim fixture."""
    rates = error_rates(_crux_fixture(), 0.65)
    assert rates.n == 9
    assert rates.tp == 2
    assert rates.fp == 1
    assert rates.tn == 4
    assert rates.fn == 2
    # Every cell distinct from its confusable twin, so a swap is observable.
    assert (rates.tp, rates.fp, rates.tn, rates.fn) == (2, 1, 4, 2)


def test_crux_error_rates_exact_at_lex_tau_065():
    """error_a and error_b differ (0.20 vs 0.50) AND their denominators differ
    (5 vs 4), so an error_a<->error_b swap OR a wrong denominator each change
    an asserted value here — not only in the isolated single-class tests."""
    rates = error_rates(_crux_fixture(), 0.65)
    assert rates.error_a == pytest.approx(0.20)   # fp/(fp+tn) = 1/5
    assert rates.error_b == pytest.approx(0.50)   # fn/(fn+tp) = 2/4
    # Guard against a silent error_a<->error_b swap slipping through.
    assert rates.error_a != rates.error_b


def test_error_b_counts_the_fabrication_passed_claim():
    """THE Error-B property, isolated and non-tautological: a single
    violation-labeled claim with HIGH t2_f1 (0.90 ≥ lex_tau) the gate passes as
    grounded is counted as fn (Error-B) — a fabrication shipped inside a
    'verified' report — and NOT as tp/fp/tn. error_b = 1/1 = 1.0."""
    fabrication = _labeled("q1#0", label="violation", tier_sensitive=True,
                           t2_f1=0.90, predicted_verdict="GROUNDED")
    # Pre-check: the gate really does pass this fabrication at lex_tau=0.65.
    assert predicted_is_violation(fabrication, 0.65) is False

    rates = error_rates([fabrication], 0.65)
    assert rates.fn == 1          # the fabrication is Error-B
    assert rates.tp == 0
    assert rates.fp == 0
    assert rates.tn == 0
    assert rates.error_b == pytest.approx(1.0)
    assert rates.error_a == 0.0   # no truly-grounded claim in this set


def test_error_a_counts_a_false_alarm_on_a_grounded_claim():
    """Error-A property isolated: a single grounded-labeled claim with LOW t2_f1
    (0.40 < lex_tau) the gate flags as a violation is counted as fp (Error-A) —
    the recoverable false alarm — and error_a = 1/1 = 1.0."""
    false_alarm = _labeled("q1#0", label="grounded", tier_sensitive=True,
                           t2_f1=0.40, predicted_verdict="UNGROUNDED")
    assert predicted_is_violation(false_alarm, 0.65) is True

    rates = error_rates([false_alarm], 0.65)
    assert rates.fp == 1
    assert rates.tp == 0
    assert rates.fn == 0
    assert rates.tn == 0
    assert rates.error_a == pytest.approx(1.0)
    assert rates.error_b == 0.0


# ---------------------------------------------------------------------------
# Case (a): a T1-grounded true claim is error-free at every lex_tau.
# ---------------------------------------------------------------------------

def test_t1_grounded_true_claim_is_error_free_at_every_lex_tau():
    """A non-tier GROUNDED (T1) claim that is truly grounded lands in tn — never
    fp, never fn — at every lex_tau. T1 does not consult lex_tau, so no threshold
    move can turn this correct pass into an error."""
    row = _labeled("q1#0", label="grounded", tier_sensitive=False, t2_f1=1.0,
                   predicted_verdict="GROUNDED")
    for lex_tau in (0.0, 0.25, 0.5, 0.65, 0.9, 1.0):
        rates = error_rates([row], lex_tau)
        assert rates.tn == 1
        assert rates.fp == 0
        assert rates.fn == 0
        assert rates.error_a == 0.0
        assert rates.error_b == 0.0


# ---------------------------------------------------------------------------
# Case (b): the asymmetry is LIVE — one lex_tau move converts an Error-B into a
# true-positive WHILE raising Error-A. Two tier_sensitive claims:
#   * a violation-labeled claim with t2_f1 = 0.60
#   * a grounded-labeled claim  with t2_f1 = 0.50
# Raising lex_tau from 0.40 (below both) to 0.70 (above both):
#   - violation claim: 0.60 < 0.40? no  -> grounded -> fn (Error-B)
#                      0.60 < 0.70? yes -> violation -> tp   (Error-B -> TP)
#   - grounded claim:  0.50 < 0.40? no  -> grounded -> tn    (Error-A = 0)
#                      0.50 < 0.70? yes -> violation -> fp    (Error-A raised)
# The parenthetical in the brief — "(raising Error A)" — pins the direction:
# the move that converts Error-B into a true-positive is the SAME move that
# raises Error-A, i.e. RAISING lex_tau. (See report for the spec-wording note.)
# ---------------------------------------------------------------------------

def _asymmetry_fixture() -> list[LabeledClaim]:
    return [
        _labeled("q1#0", label="violation", tier_sensitive=True, t2_f1=0.60,
                 predicted_verdict="UNGROUNDED"),
        _labeled("q1#1", label="grounded", tier_sensitive=True, t2_f1=0.50,
                 predicted_verdict="GROUNDED"),
    ]


def test_asymmetry_low_lex_tau_has_error_b_and_no_error_a():
    """At the LENIENT bar (lex_tau=0.40, below both t2_f1 values): the violation
    is missed (Error-B) and the grounded claim is correctly passed (Error-A=0)."""
    rates = error_rates(_asymmetry_fixture(), 0.40)
    assert rates.fn == 1           # violation missed -> Error-B
    assert rates.tp == 0
    assert rates.fp == 0           # grounded claim not yet flagged
    assert rates.tn == 1
    assert rates.error_b == pytest.approx(1.0)
    assert rates.error_a == 0.0


def test_asymmetry_high_lex_tau_converts_error_b_to_tp_and_raises_error_a():
    """Raising the bar to lex_tau=0.70 (above both t2_f1 values) converts the
    Error-B into a true-positive (the violation is now caught) but simultaneously
    turns the correctly-passed grounded claim into a false alarm (Error-A rises
    from 0 to 1). This is the live asymmetry: you cannot lower Error-B by moving
    lex_tau without paying in Error-A."""
    rates = error_rates(_asymmetry_fixture(), 0.70)
    assert rates.tp == 1           # violation now caught (was Error-B)
    assert rates.fn == 0           # Error-B eliminated
    assert rates.fp == 1           # grounded claim now flagged -> Error-A
    assert rates.tn == 0
    assert rates.error_b == 0.0    # dropped from 1.0
    assert rates.error_a == pytest.approx(1.0)  # rose from 0.0


def test_asymmetry_is_a_tradeoff_not_a_free_lunch():
    """Cross-check the two thresholds side by side: error_b falls (1.0 -> 0.0) as
    error_a rises (0.0 -> 1.0). The tool CANNOT reduce the unrecoverable error
    without increasing the recoverable one — the calibration must choose."""
    lenient = error_rates(_asymmetry_fixture(), 0.40)
    strict = error_rates(_asymmetry_fixture(), 0.70)
    assert lenient.error_b > strict.error_b   # 1.0 > 0.0
    assert strict.error_a > lenient.error_a   # 1.0 > 0.0


# ---------------------------------------------------------------------------
# Zero-denominator guards: 0.0 while still exposing the counts.
# ---------------------------------------------------------------------------

def test_error_b_denominator_zero_when_no_violation_labels():
    """With no violation-labeled claims (fn+tp == 0), error_b is guarded to 0.0
    — not a ZeroDivisionError — while fn and tp counts stay exposed as 0."""
    grounded_only = [
        _labeled("q1#0", label="grounded", tier_sensitive=False, t2_f1=1.0,
                 predicted_verdict="GROUNDED"),
        _labeled("q1#1", label="grounded", tier_sensitive=True, t2_f1=0.40,
                 predicted_verdict="UNGROUNDED"),  # fp (Error-A)
    ]
    rates = error_rates(grounded_only, 0.65)
    assert rates.fn == 0
    assert rates.tp == 0
    assert rates.error_b == 0.0     # guarded 0/0
    assert rates.fp == 1
    assert rates.tn == 1
    assert rates.error_a == pytest.approx(0.5)  # fp/(fp+tn) = 1/2


def test_error_a_denominator_zero_when_no_grounded_labels():
    """With no grounded-labeled claims (fp+tn == 0), error_a is guarded to 0.0
    while fp and tn counts stay exposed as 0."""
    violation_only = [
        _labeled("q1#0", label="violation", tier_sensitive=True, t2_f1=0.20,
                 predicted_verdict="UNGROUNDED"),  # tp
        _labeled("q1#1", label="violation", tier_sensitive=True, t2_f1=0.90,
                 predicted_verdict="GROUNDED"),    # fn (Error-B)
    ]
    rates = error_rates(violation_only, 0.65)
    assert rates.fp == 0
    assert rates.tn == 0
    assert rates.error_a == 0.0     # guarded 0/0
    assert rates.tp == 1
    assert rates.fn == 1
    assert rates.error_b == pytest.approx(0.5)  # fn/(fn+tp) = 1/2


def test_empty_labeled_list_yields_all_zero_rates():
    """error_rates over an empty list is well-defined: n=0, all counts 0, both
    error rates guarded to 0.0 (no crash)."""
    rates = error_rates([], 0.65)
    assert rates.n == 0
    assert (rates.tp, rates.fp, rates.tn, rates.fn) == (0, 0, 0, 0)
    assert rates.error_a == 0.0
    assert rates.error_b == 0.0


# ---------------------------------------------------------------------------
# Structural + purity contracts.
# ---------------------------------------------------------------------------

def test_error_rates_is_frozen():
    """ErrorRates instances must be immutable (frozen dataclass contract)."""
    rates = ErrorRates(n=1, tp=1, fp=0, tn=0, fn=0, error_a=0.0, error_b=0.0)
    with pytest.raises(dataclasses.FrozenInstanceError):
        rates.tp = 5  # type: ignore[misc]


def test_error_rates_does_not_mutate_input_list():
    """Pure function contract: the input list is unchanged after the call."""
    fixture = _crux_fixture()
    before = list(fixture)
    error_rates(fixture, 0.65)
    assert fixture == before


def test_error_rates_is_deterministic():
    """Same inputs -> identical ErrorRates (pure/deterministic)."""
    fixture = _crux_fixture()
    assert error_rates(fixture, 0.65) == error_rates(fixture, 0.65)


def test_counts_sum_to_n():
    """Invariant: tp + fp + tn + fn == n for any labeled set."""
    rates = error_rates(_crux_fixture(), 0.65)
    assert rates.tp + rates.fp + rates.tn + rates.fn == rates.n
