"""Re-derive the DEPLOYED error rates in one command. Read-only, by design.

    cd Agent-Assure && uv run python -m calibration.measure_rates

Why this file exists (R1, 2026-10-10). ``Error-A 10/25 = 0.400`` and
``Error-B 0/27 = 0.000`` are the two numbers this product is described by — in
seven calibration records, in CLAUDE.md, in three overnight instrument files and
in the launch claim. On 2026-10-10 three KINDS of search (the literals, the
script names, the CRs themselves) found no command that produces them. The
verdict was NOT_LOCATED_UNDER those vectors, never ABSENT — and this module
settles it rather than leaving a number quoted and un-rederivable.

**Read-only is the point, not a convenience.** The one runner that did exist,
``calibration.run_calibration``, is the n=12 bootstrap and it REWRITES
``CR-001`` as a side effect — a measurement that mutates the record it is
measured against. Nothing here writes a file. If a CR is wanted, a human asks
for one; a measurement command may not author the record.

**The rates are recomputed from the GATE, not read back from the corpus
JSONL.** Reading ``feature_rows-v2.jsonl`` would report what the gate said on
the day that file was written; rebuilding the rows calls the live
``ground()``, so the number tracks the code. That is the whole purpose.

**The gold labels are AUTHORED and this module only reads them.**
``load_gold_labels`` is the join and it fails loud on all six ways the human
labels and the derived scaffold can disagree — including a STALE label, where
the claim's text changed under a judgment a person made about different words.
A stale-label crash here is the correct outcome, not a bug to route around.
"""
from __future__ import annotations

import sys
from pathlib import Path

_AGENT_ASSURE = Path(__file__).resolve().parents[1]
if str(_AGENT_ASSURE) not in sys.path:
    sys.path.insert(0, str(_AGENT_ASSURE))

from calibration.build_corpus import emit_rows_for_cases          # noqa: E402
from calibration.build_corpus_v2 import build_candidate_cases     # noqa: E402
from scripts.calibrate import (                                   # noqa: E402
    ErrorRates,
    error_rates,
    join_labels,
    load_gold_labels,
)

LABELS_PATH = "calibration/labels-v2.csv"
SCAFFOLD_PATH = "calibration/labeling-v2.csv"

# ADR-006 retired lex_tau: `tier_sensitive` is ALWAYS False, so
# `predicted_is_violation` never consults a threshold and every tau must give
# the same confusion matrix. These two are deliberately far apart so that
# equality is a PROPERTY being tested, not an arithmetic accident.
_PROBE_TAUS = (0.0, 1.0)


def measure() -> tuple[ErrorRates, list]:
    """Return (rates, labeled) recomputed from the live gate. Writes nothing."""
    cases = [candidate.case for candidate in build_candidate_cases()]
    rows = emit_rows_for_cases(cases)
    labels = load_gold_labels(LABELS_PATH, SCAFFOLD_PATH)
    labeled = join_labels(rows, labels)

    rates = error_rates(labeled, _PROBE_TAUS[0])
    for tau in _PROBE_TAUS[1:]:
        other = error_rates(labeled, tau)
        if other != rates:
            raise AssertionError(
                "The confusion matrix MOVED between lex_tau "
                f"{_PROBE_TAUS[0]} and {tau}:\n"
                f"  {rates}\n  {other}\n"
                "ADR-006 retired lex_tau and pinned tier_sensitive to False, so "
                "no verdict may depend on a lexical threshold. A row has become "
                "tier_sensitive again, which means a threshold is silently back "
                "in the verdict path. HALT — this is not a measurement problem."
            )
    return rates, labeled


def main() -> None:
    rates, labeled = measure()
    grounded_total = rates.fp + rates.tn
    violation_total = rates.fn + rates.tp

    print(f"n = {rates.n} gold-labeled claims "
          f"({grounded_total} grounded, {violation_total} violation)")
    print(f"  tp={rates.tp}  fp={rates.fp}  tn={rates.tn}  fn={rates.fn}")
    print()
    print(f"Error-A (false alarm, RECOVERABLE)   "
          f"fp/(fp+tn) = {rates.fp}/{grounded_total} = {rates.error_a:.3f}")
    print(f"Error-B (miss, UNRECOVERABLE)        "
          f"fn/(fn+tp) = {rates.fn}/{violation_total} = {rates.error_b:.3f}")
    print()
    print("Positive class = VIOLATION. Error-B 0 means no KNOWN violation "
          "escapes; the 95% upper bound on "
          f"0/{violation_total} is ~10.5%, so never quote it as zero.")
    print("Provenance: single ratifier (the project owner), gold labels differ "
          "from the machine candidates on 4/52 rows. Quote as "
          f"(n={rates.n}, single ratifier).")
    print("Nothing was written. This command is read-only.")


if __name__ == "__main__":
    main()
