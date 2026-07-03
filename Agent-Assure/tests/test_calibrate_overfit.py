"""Tests for scripts/calibrate.py — leave-one-out held-out error rates (Task 6).

THE HONESTY GUARANTEE of the whole calibration harness. ``loo_operating_point``
must report genuinely HELD-OUT error rates, never in-sample rates dressed up as
held-out. For EACH claim, the operating-point tau is selected on the OTHER n-1
claims (the held-out claim is NEVER in the set its own tau was chosen on), then
the held-out claim is predicted at that tau, and the held-out confusion cells are
accumulated across all n folds. The return is (modal selected tau, held-out
ErrorRates).

The bug this task exists to prevent is LEAKAGE: training-and-testing on the same
claim. A leaky implementation (select tau on the FULL set, then predict the
held-out claim at that same tau) collapses held-out rates toward in-sample rates,
making the detector look better than it is. ``_leaky_loo`` below is exactly that
bug; the anti-leakage test asserts the real function diverges from it.

Fold-selection failure: when a fold's n-1 training set cannot meet
``error_b_bound``, ``select_operating_point`` raises ``ValueError``.
``loo_operating_point`` PROPAGATES it (enriched with the failing fold's claim_id)
— it does NOT skip the fold. Skipping the hardest folds would optimistically bias
the held-out estimate, the exact dishonesty this task guards against.

Modal-tau tie-break: when two taus are selected equally often across folds, the
HIGHER tau wins (stricter grounding) — consistent with select_operating_point's
own tie-break.

TDD sequence:
  Step 1: Write tests (this file) — fail at import (loo_operating_point absent).
  Step 2: Run -> FAIL (proves test integrity).
  Step 3: Implement loo_operating_point.
  Step 4: Run -> PASS (new + all existing 282).
"""

import pytest

from scripts.calibrate import (
    LabeledClaim,
    error_rates,
    loo_operating_point,
    select_operating_point,
    sweep_thresholds,
)


# ---------------------------------------------------------------------------
# Fixture builder (mirrors test_calibrate_metrics._labeled): full control over
# the three fields predicted_is_violation reads (tier_sensitive, t2_f1,
# predicted_verdict) plus the ground-truth label. All rows here are
# tier_sensitive, so the gate's call is exactly ``t2_f1 < lex_tau``.
# ---------------------------------------------------------------------------

def _labeled(
    claim_id: str,
    *,
    label: str,
    t2_f1: float,
    tier_sensitive: bool = True,
    predicted_verdict: str = "UNGROUNDED",
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
# THE overfit fixture — hand-computed, tier_sensitive (violation iff t2_f1 < tau).
#
#   taus = [0.30, 0.50, 0.70, 0.90] ;  error_b_bound = 0.0 (catch every violation)
#
#   violations : V_hi t2_f1=0.65, V_lo t2_f1=0.10
#   grounded   : G1=0.40, G2=0.55, G3=0.80, G4=0.85
#
# IN-SAMPLE (select on the full 6, then error_rates at that tau):
#   error_b<=0 needs both violations caught -> tau in {0.70, 0.90}.
#   0.70: fp=2 (G1,G2) tn=2 (G3,G4)  error_a=0.50  ;  0.90: fp=4 error_a=1.0
#   -> select 0.70. In-sample: tp=2 fp=2 tn=2 fn=0, error_a=0.50, error_b=0.00.
#
# LEAVE-ONE-OUT (select on the OTHER 5, predict the held-out one):
#   hold V_hi(0.65): others have one violation V_lo(0.10), caught by ALL taus,
#       so error_b=0 at every tau; lowest error_a is tau=0.30 (flags no grounded).
#       predict V_hi @0.30: 0.65<0.30? NO -> passed as grounded -> fn (Error-B!).
#       In-sample this same claim was a tp @0.70. THIS is the overfit gap.
#   hold V_lo(0.10): others' only violation is V_hi(0.65) -> need tau>0.65 ->
#       {0.70,0.90}, min error_a 0.70. predict V_lo @0.70: 0.10<0.70 -> tp.
#   hold G1(0.40): two violations remain -> {0.70,0.90}, pick 0.70.
#       predict G1 @0.70: 0.40<0.70 -> flagged -> fp (Error-A).
#   hold G2(0.55): -> 0.70. predict 0.55<0.70 -> fp (Error-A).
#   hold G3(0.80): -> 0.70. predict 0.80<0.70? no -> tn.
#   hold G4(0.85): -> 0.70. predict 0.85<0.70? no -> tn.
#
#   Held-out confusion: tp=1 (V_lo) fn=1 (V_hi) fp=2 (G1,G2) tn=2 (G3,G4), n=6.
#   Held-out error_b = 1/2 = 0.50  (>> in-sample 0.00)
#   Held-out error_a = 2/4 = 0.50
#   Selected taus per fold: 0.30, 0.70, 0.70, 0.70, 0.70, 0.70 -> modal 0.70.
# ---------------------------------------------------------------------------

_OVERFIT_TAUS = [0.30, 0.50, 0.70, 0.90]
_OVERFIT_BOUND = 0.0


def _overfit_fixture() -> list[LabeledClaim]:
    return [
        _labeled("q1#Vhi", label="violation", t2_f1=0.65),
        _labeled("q1#Vlo", label="violation", t2_f1=0.10),
        _labeled("q1#G1", label="grounded", t2_f1=0.40, predicted_verdict="GROUNDED"),
        _labeled("q1#G2", label="grounded", t2_f1=0.55, predicted_verdict="GROUNDED"),
        _labeled("q1#G3", label="grounded", t2_f1=0.80, predicted_verdict="GROUNDED"),
        _labeled("q1#G4", label="grounded", t2_f1=0.85, predicted_verdict="GROUNDED"),
    ]


def _in_sample_rates(labeled, taus, bound):
    """The in-sample operating point + rates a LEAK-FREE method must diverge from:
    select ONE tau on the full set, then score the SAME full set at it."""
    tau = select_operating_point(sweep_thresholds(labeled, taus), bound)
    return tau, error_rates(labeled, tau)


def _leaky_loo(labeled, taus, bound):
    """The EXACT leakage bug this task exists to prevent: pick tau on the FULL
    set (each held-out claim is in its own selection set) and predict every claim
    at that one tau. Collapses held-out rates onto in-sample rates. The real
    ``loo_operating_point`` MUST NOT equal this."""
    tau = select_operating_point(sweep_thresholds(labeled, taus), bound)
    return tau, error_rates(labeled, tau)


# ---------------------------------------------------------------------------
# Mandatory test 1: held-out Error-A/B DIFFER from in-sample.
# ---------------------------------------------------------------------------

def test_holdout_rates_differ_from_in_sample():
    """Genuinely held-out: the (error_a, error_b) pair returned by LOO differs
    from the in-sample pair. If LOO merely re-reported in-sample rates (the
    leakage failure mode), these would be identical. Here in-sample error_b=0.00
    but held-out error_b=0.50 — the pair differs, and specifically on error_b."""
    labeled = _overfit_fixture()
    _in_tau, in_rates = _in_sample_rates(labeled, _OVERFIT_TAUS, _OVERFIT_BOUND)
    _modal, held = loo_operating_point(labeled, _OVERFIT_TAUS, _OVERFIT_BOUND)

    assert (held.error_a, held.error_b) != (in_rates.error_a, in_rates.error_b)
    assert held.error_b != in_rates.error_b          # differs on the crux error
    assert in_rates.error_b == pytest.approx(0.0)     # in-sample looks perfect
    assert held.error_b == pytest.approx(0.5)         # held-out tells the truth


# ---------------------------------------------------------------------------
# Mandatory test 2: overfit fixture -> held-out Error-B > in-sample Error-B.
# ---------------------------------------------------------------------------

def test_overfit_holdout_error_b_exceeds_in_sample():
    """The deliberately-overfit fixture: in-sample selection catches every
    violation (error_b=0.00), but under leave-one-out the fold that holds out the
    pivotal high-scoring violation (V_hi, t2_f1=0.65) selects a lax tau (0.30) on
    the remaining data and MISSES it — so held-out error_b (0.50) strictly exceeds
    in-sample error_b (0.00). Overfitting made visible."""
    labeled = _overfit_fixture()
    _in_tau, in_rates = _in_sample_rates(labeled, _OVERFIT_TAUS, _OVERFIT_BOUND)
    _modal, held = loo_operating_point(labeled, _OVERFIT_TAUS, _OVERFIT_BOUND)

    assert held.error_b > in_rates.error_b
    assert held.error_b == pytest.approx(0.5)
    assert in_rates.error_b == pytest.approx(0.0)


# ---------------------------------------------------------------------------
# Anti-leakage: the test that FAILS if the implementation trained-and-tested on
# the same claim. ``_leaky_loo`` is that bug spelled out; the real function must
# diverge from it. Non-tautological: both sides computed from the same public
# primitives, only the fold discipline differs.
# ---------------------------------------------------------------------------

def test_leakage_would_collapse_holdout_to_in_sample():
    """If loo_operating_point kept the held-out claim in its own selection set,
    its held-out rates would EQUAL the leaky (== in-sample) rates. They must not.
    real held-out error_b (0.50) != leaky error_b (0.00). Swap in a leaky impl and
    THIS assertion is the first to fail."""
    labeled = _overfit_fixture()
    _leak_tau, leak_rates = _leaky_loo(labeled, _OVERFIT_TAUS, _OVERFIT_BOUND)
    _modal, held = loo_operating_point(labeled, _OVERFIT_TAUS, _OVERFIT_BOUND)

    # A leaky impl would make these equal; a leak-free one keeps them apart.
    assert held.error_b != leak_rates.error_b
    assert (held.tp, held.fp, held.tn, held.fn) != (
        leak_rates.tp, leak_rates.fp, leak_rates.tn, leak_rates.fn
    )
    assert leak_rates.error_b == pytest.approx(0.0)
    assert held.error_b == pytest.approx(0.5)


def test_holdout_exact_confusion_counts_and_modal_tau():
    """Pin the ENTIRE held-out computation to hand-computed values so any single
    fold mis-assignment changes an asserted number. tp/fp/tn/fn = 1/2/2/1, n=6,
    error_a=error_b=0.50, modal selected tau=0.70 (five folds pick 0.70, one picks
    0.30). A leaky impl yields 2/2/2/0 instead — a different, detectable answer."""
    modal, held = loo_operating_point(
        _overfit_fixture(), _OVERFIT_TAUS, _OVERFIT_BOUND
    )
    assert (held.tp, held.fp, held.tn, held.fn) == (1, 2, 2, 1)
    assert held.n == 6
    assert held.error_a == pytest.approx(0.5)
    assert held.error_b == pytest.approx(0.5)
    assert modal == 0.70


# ---------------------------------------------------------------------------
# Fold-selection failure PROPAGATES (documented decision: propagate, never skip).
# The sneaky violation (t2_f1=0.95) is never caught for any swept tau <= 0.90, so
# error_b floors at 0.5 on every fold that still contains it; bound=0.10 is
# unreachable -> select_operating_point raises -> loo_operating_point propagates.
# ---------------------------------------------------------------------------

def _unreachable_fixture() -> list[LabeledClaim]:
    return [
        _labeled("q1#0", label="violation", t2_f1=0.20),
        _labeled("q1#1", label="violation", t2_f1=0.95, predicted_verdict="GROUNDED"),
        _labeled("q1#2", label="grounded", t2_f1=0.50, predicted_verdict="GROUNDED"),
    ]


def test_fold_selection_failure_propagates_not_skipped():
    """When a fold's n-1 training set cannot meet the bound, the error is
    PROPAGATED (enriched with the failing fold's claim_id), NOT silently skipped.
    Skipping the hardest folds would optimistically bias the held-out estimate —
    the exact dishonesty this task guards against."""
    with pytest.raises(ValueError) as exc:
        loo_operating_point(_unreachable_fixture(), [0.30, 0.60, 0.90], 0.10)
    msg = str(exc.value)
    assert "loo_operating_point" in msg           # our enriching frame, not swallowed
    assert "q1#" in msg                            # names the failing fold
    assert "error_b" in msg                        # carries the inner diagnostic


def test_fold_success_when_bound_reachable_on_every_fold():
    """Control for the propagate test: with a reachable bound the overfit fixture
    runs to completion and returns finite held-out rates — proving the propagate
    path is triggered by genuine unreachability, not by any bound at all."""
    modal, held = loo_operating_point(
        _overfit_fixture(), _OVERFIT_TAUS, _OVERFIT_BOUND
    )
    assert 0.0 <= held.error_b <= 1.0
    assert modal in _OVERFIT_TAUS


# ---------------------------------------------------------------------------
# Modal-tau tie-break: two folds, one selects 0.40, the other 0.80 (1-1 tie).
# The rule breaks toward the HIGHER tau -> 0.80.
#
#   c0: violation t2_f1=0.30 ; c1: grounded t2_f1=0.60 ; bound=1.0 (always met).
#   hold c0 -> others={c1 grounded}: error_a min at 0.40 (flags nothing) -> 0.40.
#   hold c1 -> others={c0 violation}: no grounded, error_a=0 tie -> higher -> 0.80.
# ---------------------------------------------------------------------------

def _tie_fixture() -> list[LabeledClaim]:
    return [
        _labeled("q1#c0", label="violation", t2_f1=0.30),
        _labeled("q1#c1", label="grounded", t2_f1=0.60, predicted_verdict="GROUNDED"),
    ]


def test_modal_tau_tie_breaks_to_higher():
    """Folds select 0.40 and 0.80 exactly once each; the modal tie-break returns
    the HIGHER tau (0.80), matching select_operating_point's stricter-grounding
    bias. A lower-tau tie-break would return 0.40 and fail here."""
    modal, _held = loo_operating_point(_tie_fixture(), [0.40, 0.80], 1.0)
    assert modal == 0.80


# ---------------------------------------------------------------------------
# Purity, determinism, and the empty-input guard.
# ---------------------------------------------------------------------------

def test_loo_does_not_mutate_inputs():
    """Pure function: neither the labeled list nor the taus list is mutated."""
    labeled = _overfit_fixture()
    labeled_before = list(labeled)
    taus = [0.70, 0.30, 0.90, 0.50]
    taus_before = list(taus)
    loo_operating_point(labeled, taus, _OVERFIT_BOUND)
    assert labeled == labeled_before
    assert taus == taus_before


def test_loo_is_deterministic():
    """Same inputs -> identical (modal tau, held-out ErrorRates)."""
    labeled = _overfit_fixture()
    first = loo_operating_point(labeled, _OVERFIT_TAUS, _OVERFIT_BOUND)
    second = loo_operating_point(labeled, _OVERFIT_TAUS, _OVERFIT_BOUND)
    assert first == second


def test_loo_raises_on_empty_labeled():
    """No claims -> no folds -> no held-out prediction and no modal tau to report.
    ValueError, not a silent empty result or an index crash."""
    with pytest.raises(ValueError):
        loo_operating_point([], _OVERFIT_TAUS, _OVERFIT_BOUND)
