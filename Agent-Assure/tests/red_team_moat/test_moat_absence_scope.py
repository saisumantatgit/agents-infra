"""OI-ABS-01 — an absence claim's SCOPE must be searched, not just its subject.

`check_absence` verifies that the negated SUBJECT was searched at least twice.
It never looks at the claim's SCOPE — the trailing phrase that says over what
domain the absence is asserted. So a writer can search narrowly and assert
broadly, and the gate certifies it:

    claim  "There is no recall of the Zentara inhaler IN ANY REGULATED MARKET."
    queries "Zentara inhaler recall search" / "FDA recall database Zentara recall"

Both queries carry the subject (zentara, recall), so the 2-search rule is
satisfied and the verdict was ABSENCE_SUPPORTED. But the searches establish
nothing about "any regulated market" — one of them is explicitly the FDA, a
single jurisdiction. The claim is global; the evidence is American.

These are the last two Error-B rows in the calibration corpus (q14, q37, both
gold-labeled VIOLATION), and they are the whole remaining Error-B after ADR-006.

THE PRINCIPLE: to establish that something is absent from a domain, you must
have looked in that domain. A search outside the claimed scope is not weak
evidence for the claim — it is no evidence at all. So a query counts toward the
two-search minimum ONLY if it also addresses the scope.

Fail-closed: adding a requirement can only move an absence AWAY from
ABSENCE_SUPPORTED, never toward it.
"""

from __future__ import annotations

import pytest

from scripts.ground_check import Verdict, check_absence, classify, decompose


def _absence(text: str) -> object:
    claim = classify(next(iter(decompose(text))))
    assert claim.kind.value == "ABSENCE", f"fixture is not an ABSENCE claim: {claim.kind}"
    return claim


# --- The attack: search narrowly, assert broadly ----------------------------

SCOPE_OVERREACH = [
    pytest.param(
        "There is no recall of the Zentara inhaler in any regulated market.",
        ["Zentara inhaler recall search", "FDA recall database Zentara recall"],
        "queries cover one jurisdiction (FDA); the claim covers all of them",
        id="q14-global-scope-from-one-jurisdiction",
    ),
    pytest.param(
        "There is no antidote approved for the toxin in current guidelines.",
        ["toxin antidote guideline search", "antidote literature review toxin"],
        "only ONE of the two searches addresses guidelines; the other is a "
        "literature review, which is a different corpus",
        id="q37-guidelines-scope-with-one-guideline-search",
    ),
    pytest.param(
        "There is no published trial of the compound in peer-reviewed journals.",
        ["compound trial search", "compound trial registry lookup"],
        "neither search touches peer-reviewed journals",
        id="synthetic-journal-scope-never-searched",
    ),
]


@pytest.mark.parametrize("text,queries,why", SCOPE_OVERREACH)
def test_absence_scope_must_be_searched(text: str, queries: list[str], why: str) -> None:
    verdict = check_absence(_absence(text), queries)
    assert verdict == Verdict.UNVERIFIED_ABSENCE, (
        f"OI-ABS-01: absence certified over a scope that was never searched "
        f"({why}); got {verdict}"
    )


# --- The other direction: a searched scope must still be supportable --------

def test_absence_with_searched_scope_still_supported() -> None:
    """The same claim, with searches that DO cover the scope, must pass.

    Without this the 'fix' is just a blanket refusal of scoped absences, which
    would close the hole by making the whole absence tier useless.
    """
    verdict = check_absence(
        _absence("There is no recall of the Zentara inhaler in any regulated market."),
        ["Zentara inhaler recall regulated market search",
         "regulated market recall database Zentara inhaler"],
    )
    assert verdict == Verdict.ABSENCE_SUPPORTED, (
        f"scope was searched in both queries, yet the absence was refused "
        f"({verdict}). The rule has over-reached into Error-A."
    )


def test_unscoped_absence_is_unaffected() -> None:
    """q13's shape: no scope phrase at all, so the rule must not fire.

    This is the corpus's only gold-GROUNDED absence. If the scope rule reads a
    subject modifier ('affecting the X200 drone') as a scope, it turns a
    human-labeled grounded row into a false alarm — the exact failure the
    mandatory corpus diff caught twice before.
    """
    verdict = check_absence(
        _absence("We found no evidence of a safety recall affecting the X200 drone."),
        ["recall evidence search X200 drone", "regulatory database evidence query X200"],
    )
    assert verdict == Verdict.ABSENCE_SUPPORTED, (
        f"an unscoped absence was refused ({verdict}); the scope rule is firing "
        f"on a subject modifier."
    )
