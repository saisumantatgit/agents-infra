"""The policy/evidence split — and the line it must not cross.

INTRA-RATER-2026-09-12 found that the corpus mixes two kinds of item:

  * **evidence-derivable** — the label follows from what the labeller is shown;
  * **policy** — the label follows from a gate rule that is not in the item.

Only `haiku_summary` rows are policy today. Their evidence supports their claim
word for word, and gold says violation because an AI summary cannot ground
anything, whoever wrote it. Three raters judged those two rows; all three
disagreed with gold in the same direction, including the author of the labels
judging blind.

The split governs RELIABILITY only. Error-A and Error-B include every row,
always — and that is what these tests pin, because the tempting next step after
"exclude them from κ" is "exclude them from the rates", which would score the
gate only on the questions it finds easy.
"""

from __future__ import annotations

import csv
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(REPO_ROOT))

from calibration.build_corpus_v2 import _label_basis  # noqa: E402
from scripts.calibrate import POLICY_SOURCE_TYPES, reliability_eligible  # noqa: E402

SCAFFOLD = REPO_ROOT / "calibration" / "labeling-v2.csv"


def _rows() -> list[dict]:
    with SCAFFOLD.open(encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def test_label_basis_is_emitted_for_every_row() -> None:
    rows = _rows()
    assert rows, "scaffold is empty"
    assert all(r["label_basis"] in ("policy", "evidence") for r in rows)


def test_only_haiku_summary_rows_are_policy() -> None:
    """Pinned deliberately narrow.

    If a future change widens the policy class, this test fails and forces the
    widening to be argued rather than absorbed — because every row moved into
    "policy" is a row that stops counting toward reproducibility.
    """
    for r in _rows():
        expected = "policy" if r["source_type"] == "haiku_summary" else "evidence"
        assert r["label_basis"] == expected, r["claim_id"]


def test_the_policy_rows_are_the_two_we_measured() -> None:
    policy = sorted(r["claim_id"] for r in _rows() if r["label_basis"] == "policy")
    assert policy == ["q24#0", "q44#0"], (
        f"the policy set changed to {policy}; the 0/6 three-rater evidence in "
        "INTRA-RATER-2026-09-12 covers q24 and q44 only"
    )


def test_reliability_excludes_policy_rows() -> None:
    rows = _rows()
    types = {r["claim_id"]: r["source_type"] for r in rows}
    ids = [r["claim_id"] for r in rows]
    eligible = reliability_eligible(types, ids)
    assert len(eligible) == len(ids) - 2
    assert "q24#0" not in eligible and "q44#0" not in eligible


def test_error_rates_still_see_every_row() -> None:
    """The line that must not be crossed.

    `reliability_eligible` is for κ. The gate must still be right about policy
    claims, so nothing in the error-rate path may consult it. This asserts the
    corpus the rates are computed over is the WHOLE corpus.
    """
    import inspect  # noqa: PLC0415

    from scripts import calibrate  # noqa: PLC0415

    for name in ("error_rates", "loo_operating_point", "select_operating_point"):
        src = inspect.getsource(getattr(calibrate, name))
        assert "reliability_eligible" not in src, (
            f"{name}() consults reliability_eligible — policy rows have been "
            "dropped from the ERROR RATES, which scores the gate only on the "
            "questions it finds easy"
        )
        assert "POLICY_SOURCE_TYPES" not in src, f"{name}() filters on policy type"

    assert len(_rows()) == 52
