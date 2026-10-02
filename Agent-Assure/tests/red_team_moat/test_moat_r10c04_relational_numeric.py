"""R10C-04 — the relation was corroborated and the FIGURE was never checked.

`classify` orders RELATIONAL ahead of NUMERIC, and `ground()`'s relational
branch returned above the numeric branch. So a number inside a relational claim
was never looked at: "Insulin resistance causes 97% of all type 2 diabetes"
certified GROUNDED at PASS 100.0 against a store containing no percentage.

That is the worst shape a grounding error can take for a reader, because the
FIGURE is the part they quote. The relation ("causes") was genuinely
corroborated by two sources, which is exactly what makes the number look safe.

The fix is fail-closed: it can only downgrade an otherwise-GROUNDED relational
claim to UNVERIFIED_NUMBER, never create a PASS.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))

import ground_check as g  # noqa: E402


def _rec(sid, text):
    return {"source_id": sid, "url": None, "file_path": "/tmp/a",
            "fetched_at": "2026-09-13T00:00:00Z", "tool": "Read",
            "content_sha256": "a" * 64, "text": text,
            "full_text_source": "verbatim", "captured_via": "inline",
            "query_provenance": "q-" + sid}


NO_NUMBER = [
    _rec("S2", "Insulin resistance impairs glucose uptake and is a central "
               "mechanism that causes type 2 diabetes to develop."),
    _rec("S3", "Type 2 diabetes develops when insulin resistance progresses "
               "and the pancreas can no longer compensate."),
]

WITH_97 = [
    _rec("S2", "Insulin resistance impairs glucose uptake and causes 97% of "
               "type 2 diabetes to develop."),
    _rec("S3", "Type 2 diabetes develops in 97% of cases when insulin "
               "resistance progresses and the pancreas cannot compensate."),
]


def _report(tmp_path, draft, records):
    p = tmp_path / "s.jsonl"
    p.write_text("".join(json.dumps(r) + "\n" for r in records), encoding="utf-8")
    return g.score_report([g.classify(c) for c in g.decompose(draft)],
                          g.load_store(str(p)))


@pytest.mark.parametrize("figure", [
    "97% of all",        # percentage absent from the store
    "4321 cases of",     # count absent from the store
    "12.5% of all",      # decimal percentage
])
def test_a_figure_absent_from_the_store_is_refused(tmp_path, figure):
    rep = _report(tmp_path,
                  f"Insulin resistance causes {figure} type 2 diabetes "
                  f"[S2][S3].\n", NO_NUMBER)
    assert rep["per_claim"][0]["verdict"] == "UNVERIFIED_NUMBER"
    assert rep["gate"] != "PASS"


def test_the_relation_is_still_corroborated_without_a_figure(tmp_path):
    """CONTROL. The fix must not break relational grounding itself — otherwise
    it is 'refuse all relational claims' wearing a numeric costume."""
    rep = _report(tmp_path,
                  "Insulin resistance causes type 2 diabetes [S2][S3].\n",
                  NO_NUMBER)
    assert rep["per_claim"][0]["verdict"] == "GROUNDED"
    assert rep["gate"] == "PASS"


def test_a_figure_PRESENT_in_the_store_still_certifies(tmp_path):
    """The control that matters most: this must not become 'any number fails'."""
    rep = _report(tmp_path,
                  "Insulin resistance causes 97% of all type 2 diabetes "
                  "[S2][S3].\n", WITH_97)
    assert rep["per_claim"][0]["verdict"] == "GROUNDED"
    assert rep["gate"] == "PASS"


def test_percent_does_not_match_a_bare_number(tmp_path):
    """numeric_ok treats percent and absolute as distinct units. A relational
    claim must inherit that, or the fix leaks the exact confusion it inherits
    the machinery to prevent."""
    bare = [
        _rec("S2", "Insulin resistance impairs glucose uptake and causes 97 "
                   "distinct downstream effects that lead to type 2 diabetes."),
        _rec("S3", "Type 2 diabetes develops in 97 separate documented "
                   "pathways when insulin resistance progresses."),
    ]
    rep = _report(tmp_path,
                  "Insulin resistance causes 97% of all type 2 diabetes "
                  "[S2][S3].\n", bare)
    assert rep["gate"] != "PASS"


# --- R11B-03: the figure must be grounded by what the claim CITES -----------

def test_a_figure_in_an_uncited_source_does_not_ground_the_claim(tmp_path):
    """Round 11 found J-40's first version drew from store.values(), so a
    figure appearing ONLY in an unrelated, UNCITED source satisfied the check.

    That is the same confusion the whole product exists to prevent: 'somewhere
    in the session' is not 'the source this claim points at'. The NUMERIC
    branch has always used the claim's own cited sources; the relational check
    now matches it."""
    distractor = _rec("S9", "An unrelated market report notes that 97% of "
                            "respondents preferred the blue packaging.")
    rep = _report(tmp_path,
                  "Insulin resistance causes 97% of all type 2 diabetes "
                  "[S2][S3].\n", NO_NUMBER + [distractor])
    assert rep["per_claim"][0]["verdict"] == "UNVERIFIED_NUMBER"
    assert rep["gate"] != "PASS"


def test_the_figure_still_grounds_when_the_CITED_source_carries_it(tmp_path):
    """CONTROL for the above: cited-only must not become 'never grounds'."""
    rep = _report(tmp_path,
                  "Insulin resistance causes 97% of all type 2 diabetes "
                  "[S2][S3].\n", WITH_97)
    assert rep["per_claim"][0]["verdict"] == "GROUNDED"
    assert rep["gate"] == "PASS"


# J-43: a figure a reader would quote, written without a digit, is never
# extracted by _NUMERIC_RE and therefore never checked. Each of these certifies.
#
# WHY IT IS NOT FIXED HERE. Every candidate design is an ENUMERATION, and the
# project's own law forbids keying a moat rule on a property the author controls:
#   (a) a number-word list is a blacklist over ways to WRITE a number — miss a
#       spelling and the attack survives ("ninety-seven" / "ninety seven" /
#       "0.97" / "97 per cent");
#   (b) unit-anchoring (refuse when a unit word appears with no verified digit)
#       looks like a whitelist over the small closed set of units, but the
#       attacker simply drops the unit: "ninety-seven OF ALL CASES".
# Either way it refuses honest prose that the n=52 corpus does not contain, so
# the Error-A cost is UNMEASURED. That moves the Error-A/Error-B trade-off, which
# is Escalation #1 and Sai's. Registered with both designs.
#
# The variants below exist so round 12 inherits the shape of the class rather
# than one fixture of it.
@pytest.mark.parametrize("figure", [
    "ninety-seven percent of all",
    "ninety seven percent of all",
    "ninety-seven of all",            # the unit dropped — defeats design (b)
    "almost all",                     # a quantity with no number at all
])
@pytest.mark.xfail(strict=True, reason=(
    "J-43 OPEN (round 11): the numeric guard keys on claim.numeric_tokens and "
    "_NUMERIC_RE requires a DIGIT, so a figure spelled in words is never "
    "extracted and never checked. One keystroke separates '97%' (refused) from "
    "'ninety-seven percent' (certified). Both candidate fixes are enumerations "
    "and both refuse unmeasured honest prose - Escalation #1, see D-58."))
def test_a_figure_spelled_in_words_is_also_checked(tmp_path, figure):
    rep = _report(tmp_path,
                  f"Insulin resistance causes {figure} type 2 diabetes "
                  f"[S2][S3].\n", NO_NUMBER)
    assert rep["gate"] != "PASS"


def test_per_cent_refuses_by_accident_not_by_design_J53(tmp_path):
    """"ninety-seven PER CENT of all" is refused where "ninety-seven PERCENT of
    all" certifies — and NOT because the spelled figure was detected.

    Isolated: inserting the words "per cent" anywhere in a claim flips an
    UNRELATED digit from GROUNDED to UNVERIFIED_NUMBER. Same claim, same source,
    the only difference being two words that have nothing to do with the digit:

        "... causes diabetes in 2 distinct ways [S2][S3]"            -> GROUNDED
        "... causes per cent diabetes in 2 distinct ways [S2][S3]"   -> UNVERIFIED_NUMBER

    So "per cent" makes a bare digit read as a percentage, and the source's
    absolute 2 then fails to match. That is Error-A (J-53), and it is the only
    reason this J-43 variant does not certify. Pinned as an ACCIDENT so nobody
    reads it as coverage: fix J-53 and this spelling joins the other four.
    """
    rep = _report(tmp_path,
                  "Insulin resistance causes ninety-seven per cent of all type "
                  "2 diabetes [S2][S3].\n", NO_NUMBER)
    assert rep["per_claim"][0]["verdict"] == "UNVERIFIED_NUMBER"
