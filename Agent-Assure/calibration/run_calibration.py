"""Agent-Assure calibration: Phase 2a bootstrap sweep + CR emission.

Runs the labeled bootstrap corpus (calibration/feature_rows.jsonl joined
against calibration/labeling.csv) through the full Task 4-8 pipeline:

  read_feature_rows_jsonl -> load_labels -> join_labels
  -> sweep_thresholds -> select_operating_point -> loo_operating_point
  -> emit_cr

n=12 claims / 12 queries is a FIRST bootstrap pass, not the "few hundred"
claims calibration-plan.md §3 names as the eventual deliverable -- the CR
this emits documents that limitation explicitly (per calibration-plan.md §6's
two honesty constraints), and does not claim a validated bar.

The report-level gate ("gate" in the projection/actual dicts) is emitted as
"deferred", not derived, this round: derive_report_gate needs REPORTS with a
genuine spread of grounding_score values (multiple claims per report,
percentages other than 0.0/100.0) to find a real separation point. This
corpus's 12 reports each carry exactly one claim, so every report's
grounding_score is degenerate (0.0 or 100.0) -- deriving a "gate" from that
would produce a number (the 0.0/100.0 midpoint) with no real interpretive
content, which is worse than being honest that this step needs multi-claim
draft reports plus holistic per-report trustworthy/not judgments from a
human -- a follow-up round, not a fabricated value. nli_tau is deferred for
the more direct reason that the NLI (T3) tier is not implemented yet
(Phase 2b).

Pure functions except main(), the file-I/O boundary.
"""

from __future__ import annotations

import json

from scripts.calibrate import (
    ClaimFeatureRow,
    error_rates,
    join_labels,
    load_labels,
    loo_operating_point,
    select_operating_point,
    sweep_thresholds,
    emit_cr,
)

_FEATURE_ROWS_PATH = "calibration/feature_rows.jsonl"
_LABELING_CSV_PATH = "calibration/labeling.csv"
_CR_PATH = "calibration/CR-001-bootstrap-lex-tau.md"

# Fine grid over the full [0, 1] range: the sweep behavior only changes AT an
# observed t2_f1 value (predicted_is_violation is a strict "<" comparison
# against tau for tier_sensitive rows), so a 0.01 step is far finer than
# needed to bracket every breakpoint in a 12-claim corpus, at negligible cost.
_TAU_GRID: list[float] = [round(i / 100, 2) for i in range(0, 101)]

# Chosen empirically (confirmed by the module-level sweep printout in
# main()), not hardcoded blindly, and revised once by running loo_operating_
# point rather than trusting a hand-derivation: this bootstrap corpus has
# exactly one FIXED (non-tau-sensitive) held-out miss (q05's RELATIONAL
# over-association finding, see calibration/build_corpus.py), giving an
# IN-SAMPLE error_b floor of 1/7 (~0.143) at every tau >= ~0.58. An initial
# bound of 0.15 (just above that in-sample floor) made select_operating_point
# succeed in-sample but made loo_operating_point RAISE: n=12 is small enough
# that some leave-one-out folds hold out a different truly-violation claim,
# shrinking that fold's own violation denominator to 6 — the SAME fixed q05
# miss then costs 1/6 (~0.167) in that fold, which 0.15 cannot admit. 0.20
# clears the worst observed per-fold floor with margin. This is exactly the
# small-n LOO fragility calibration-plan.md §4.3 warns about ("guard
# overfitting... with n≈few-hundred claims") — n=12 sits far below that, and
# the CR this run emits says so explicitly rather than papering over it.
_ERROR_B_BOUND: float = 0.20

_PROJECTION: dict = {"lex_tau": 0.65, "gate": 0.90, "nli_tau": 0.80}


def read_feature_rows_jsonl(path: str) -> list[ClaimFeatureRow]:
    """Read *path* (one JSON object per line, as written by
    calibration.build_corpus.write_feature_rows_jsonl) and return the
    corresponding ClaimFeatureRow list, in file order.

    cited_source_ids round-trips list -> tuple (JSON has no tuple type;
    ClaimFeatureRow is frozen and requires a tuple for that field).

    I/O boundary — the file read is the only side effect.
    """
    rows: list[ClaimFeatureRow] = []
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            data = json.loads(line)
            data["cited_source_ids"] = tuple(data["cited_source_ids"])
            rows.append(ClaimFeatureRow(**data))
    return rows


def main() -> None:
    rows = read_feature_rows_jsonl(_FEATURE_ROWS_PATH)
    labels = load_labels(_LABELING_CSV_PATH)
    labeled = join_labels(rows, labels)

    print(f"Loaded {len(labeled)} labeled claims across "
          f"{len({c.query_id for c in labeled})} queries.")
    print(f"  truth violations: {sum(1 for c in labeled if c.label == 'violation')}")
    print(f"  truth grounded:   {sum(1 for c in labeled if c.label == 'grounded')}")
    print()

    # Print the full sweep so the chosen error_b_bound's rationale (module
    # docstring) is directly checkable against real output, not asserted.
    sweep = sweep_thresholds(labeled, _TAU_GRID)
    print("Sweep (collapsed to breakpoints where error_a/error_b change):")
    prev = None
    for tau, rates in sweep:
        key = (rates.error_a, rates.error_b)
        if key != prev:
            print(f"  tau>={tau:.2f}: error_a={rates.error_a:.4f} "
                  f"error_b={rates.error_b:.4f} (fp={rates.fp} fn={rates.fn})")
            prev = key
    print()

    selected_tau = select_operating_point(sweep, _ERROR_B_BOUND)
    in_sample = error_rates(labeled, selected_tau)
    print(f"Selected operating point (in-sample, bound={_ERROR_B_BOUND}): "
          f"lex_tau={selected_tau}")
    print(f"  in-sample error_a={in_sample.error_a:.4f} "
          f"error_b={in_sample.error_b:.4f}")
    print()

    modal_tau, held_out = loo_operating_point(labeled, _TAU_GRID, _ERROR_B_BOUND)
    print(f"Leave-one-out modal tau: {modal_tau}")
    print(f"  held-out error_a={held_out.error_a:.4f} "
          f"error_b={held_out.error_b:.4f} "
          f"(tp={held_out.tp} fp={held_out.fp} tn={held_out.tn} fn={held_out.fn})")
    print()

    actual: dict = {
        "lex_tau": selected_tau,
        # Deferred, not derived — see module docstring: this corpus's
        # single-claim reports cannot support a real report-gate separation
        # point. Needs a follow-up round with multi-claim draft reports and
        # holistic per-report trustworthy/not judgments.
        "gate": None,
        # Deferred — the NLI (T3) tier is not implemented yet (Phase 2b).
        "nli_tau": None,
    }

    emit_cr(
        projection=_PROJECTION,
        actual=actual,
        held_out=held_out,
        n_claims=len(labeled),
        n_queries=len({c.query_id for c in labeled}),
        split_method="leave-one-out (per-claim)",
        path=_CR_PATH,
    )
    print(f"CR written to {_CR_PATH}")


if __name__ == "__main__":
    main()
