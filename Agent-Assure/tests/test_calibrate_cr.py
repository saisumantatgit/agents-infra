"""Tests for scripts/calibrate.py — Calibration Record emission (Task 8,
ADR-025, calibration-plan.md §6).

``emit_cr`` is the CLOSING step of the harness: it takes ALREADY-COMPUTED
values (the caller has already run Tasks 4-7 — projection is the shipped
provisional defaults, actual is the derived values, held_out is Task 6's
``loo_operating_point`` result) and writes the ADR-025 Calibration Record
markdown. It does NOT re-run any harness function itself.

Two things this task exists to guarantee:

1. THE TWO HONESTY LINES (calibration-plan.md §6) must appear verbatim /
   near-verbatim in every emitted CR — a reader must never be able to
   mistake a small-n threshold for a validated one, or an in-sample rate
   for a held-out one.
2. THE 80-LINE CEILING (ADR-025) is a hard wall ``emit_cr`` enforces on
   itself: it RAISES (ValueError) and writes NOTHING rather than silently
   emitting an over-long CR. Because the projection/actual table is driven
   by the metric KEYS present in the two dicts (not a hardcoded 3-row
   table), a caller who hands emit_cr enough metrics can genuinely blow the
   budget — that is exactly what the overflow test below exercises, non-
   tautologically: it is the same code path a real 3-metric call takes,
   just with more rows.

TDD sequence:
  Step 1: Write tests (this file) — fail at import (emit_cr absent from
          scripts.calibrate).
  Step 2: Run -> FAIL (proves test integrity).
  Step 3: Implement emit_cr.
  Step 4: Run -> PASS (new + all existing 306).
"""

import os

import pytest

from scripts.calibrate import ErrorRates, emit_cr


# ---------------------------------------------------------------------------
# Fixture builders. n_claims=42 (matches held_out.n) across n_queries=18 —
# deliberately DIFFERENT numbers so a test can tell which one landed where.
# ---------------------------------------------------------------------------

def _projection() -> dict:
    return {"lex_tau": 0.65, "gate": 0.90, "nli_tau": 0.80}


def _actual_nli_off() -> dict:
    # nli_tau actual is None -> NLI tier is off -> table cell reads "deferred".
    return {"lex_tau": 0.62, "gate": 0.83, "nli_tau": None}


def _actual_nli_on() -> dict:
    return {"lex_tau": 0.62, "gate": 0.83, "nli_tau": 0.77}


def _held_out() -> ErrorRates:
    return ErrorRates(n=42, tp=16, fp=4, tn=18, fn=4, error_a=0.2, error_b=0.2)


_SPLIT_METHOD = "leave-one-out"


# ---------------------------------------------------------------------------
# Mandatory test 1: file is <= 80 lines and contains both honesty sentences,
# the delta column, and the held-out rates.
# ---------------------------------------------------------------------------

def test_cr_within_ceiling_contains_both_honesty_lines_delta_and_holdout(tmp_path):
    path = str(tmp_path / "CR-000-test.md")
    emit_cr(
        _projection(), _actual_nli_off(), _held_out(),
        n_claims=42, n_queries=18, split_method=_SPLIT_METHOD, path=path,
    )

    with open(path, encoding="utf-8") as fh:
        content = fh.read()
    lines = content.splitlines()

    assert len(lines) <= 80

    # Honesty line 1 — the brief's exact sentence, n_queries substituted.
    assert (
        "n≈18 queries is calibration, not proof — provisional until "
        "production data widens it"
    ) in content

    # Honesty line 2 — split method named + explicit HELD-OUT / not-in-sample.
    assert _SPLIT_METHOD in content
    assert "HELD-OUT" in content
    assert "not in-sample" in content

    # Delta column present in the projection-vs-actual table.
    assert "Delta" in content

    # Held-out Error-A/Error-B rendered (the actual ErrorRates values, not
    # some recomputed in-sample stand-in).
    assert str(_held_out().error_a) in content
    assert str(_held_out().error_b) in content


# ---------------------------------------------------------------------------
# Mandatory test 2: RAISES (does not write) if the content would exceed
# 80 lines. Non-tautological — it is the SAME rendering path as test 1,
# just with enough extra projection/actual metric keys to blow the budget.
# ---------------------------------------------------------------------------

def test_cr_raises_and_writes_nothing_when_over_ceiling(tmp_path):
    path = str(tmp_path / "CR-001-overflow.md")
    projection = _projection()
    actual = _actual_nli_off()
    for i in range(100):
        key = f"extra_metric_{i}"
        projection[key] = 0.5
        actual[key] = 0.5

    with pytest.raises(ValueError, match="80"):
        emit_cr(
            projection, actual, _held_out(),
            n_claims=42, n_queries=18, split_method=_SPLIT_METHOD, path=path,
        )

    assert not os.path.exists(path)


# ---------------------------------------------------------------------------
# Control for the overflow test: proves the ceiling is genuinely about line
# COUNT, not "any extra metric at all" — a modest number of extra metrics
# that still fits under 80 lines must NOT raise.
# ---------------------------------------------------------------------------

def test_cr_with_a_few_extra_metrics_under_ceiling_does_not_raise(tmp_path):
    path = str(tmp_path / "CR-002-small-extra.md")
    projection = {**_projection(), "extra_1": 1.0, "extra_2": 2.0}
    actual = {**_actual_nli_off(), "extra_1": 1.1, "extra_2": 1.9}

    emit_cr(
        projection, actual, _held_out(),
        n_claims=42, n_queries=18, split_method=_SPLIT_METHOD, path=path,
    )
    assert os.path.exists(path)
    with open(path, encoding="utf-8") as fh:
        assert len(fh.read().splitlines()) <= 80


# ---------------------------------------------------------------------------
# nli_tau deferred vs derived — the brief's explicit branch.
# ---------------------------------------------------------------------------

def test_nli_tau_deferred_when_actual_is_none(tmp_path):
    path = str(tmp_path / "CR-003-nli-off.md")
    emit_cr(
        _projection(), _actual_nli_off(), _held_out(),
        n_claims=42, n_queries=18, split_method=_SPLIT_METHOD, path=path,
    )
    with open(path, encoding="utf-8") as fh:
        content = fh.read()
    assert "deferred" in content
    # The projected nli_tau value (0.8) still appears (the projection is not
    # hidden just because NLI is off).
    assert "0.8" in content


def test_nli_tau_derived_when_nli_on_shows_no_deferred(tmp_path):
    path = str(tmp_path / "CR-004-nli-on.md")
    emit_cr(
        _projection(), _actual_nli_on(), _held_out(),
        n_claims=42, n_queries=18, split_method=_SPLIT_METHOD, path=path,
    )
    with open(path, encoding="utf-8") as fh:
        content = fh.read()
    assert "deferred" not in content
    assert "0.77" in content


# ---------------------------------------------------------------------------
# Delta values are hand-computed, not just "some number present" — pins the
# exact percent so a wrong formula is caught.
#
#   lex_tau: (0.62 - 0.65) / 0.65 * 100 = -4.615...  -> "-4.6%"
#   gate:    (0.83 - 0.90) / 0.90 * 100 = -7.777...  -> "-7.8%"
# ---------------------------------------------------------------------------

def test_delta_values_hand_computed(tmp_path):
    path = str(tmp_path / "CR-005-delta.md")
    emit_cr(
        _projection(), _actual_nli_off(), _held_out(),
        n_claims=42, n_queries=18, split_method=_SPLIT_METHOD, path=path,
    )
    with open(path, encoding="utf-8") as fh:
        content = fh.read()
    assert "-4.6%" in content
    assert "-7.8%" in content


# ---------------------------------------------------------------------------
# Fail-loud invariants: mismatched keys, mismatched n_claims/held_out.n.
# ---------------------------------------------------------------------------

def test_mismatched_projection_actual_keys_raises(tmp_path):
    path = str(tmp_path / "CR-006-mismatch.md")
    projection = _projection()
    actual = {"lex_tau": 0.62, "gate": 0.83}  # missing nli_tau
    with pytest.raises(ValueError):
        emit_cr(
            projection, actual, _held_out(),
            n_claims=42, n_queries=18, split_method=_SPLIT_METHOD, path=path,
        )
    assert not os.path.exists(path)


def test_held_out_n_mismatch_with_n_claims_raises(tmp_path):
    path = str(tmp_path / "CR-007-n-mismatch.md")
    with pytest.raises(ValueError):
        emit_cr(
            _projection(), _actual_nli_off(), _held_out(),
            n_claims=41,  # held_out().n is 42 -> deliberate mismatch
            n_queries=18, split_method=_SPLIT_METHOD, path=path,
        )
    assert not os.path.exists(path)


# ---------------------------------------------------------------------------
# Purity of the caller-owned inputs (I/O boundary function, like
# export_labeling_csv — the file write is the only side effect).
# ---------------------------------------------------------------------------

def test_emit_cr_does_not_mutate_inputs(tmp_path):
    path = str(tmp_path / "CR-008-purity.md")
    projection = _projection()
    actual = _actual_nli_off()
    held_out = _held_out()
    projection_before = dict(projection)
    actual_before = dict(actual)
    held_out_before = held_out

    emit_cr(
        projection, actual, held_out,
        n_claims=42, n_queries=18, split_method=_SPLIT_METHOD, path=path,
    )

    assert projection == projection_before
    assert actual == actual_before
    assert held_out == held_out_before
