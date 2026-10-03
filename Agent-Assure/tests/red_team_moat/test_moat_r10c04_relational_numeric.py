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
    assert rep["per_claim"][0]["relation_diagnostic"] == g.RELATION_FIGURE_ABSENT
    assert rep["gate"] != "PASS"


def test_the_relation_is_still_corroborated_without_a_figure(tmp_path):
    """CONTROL. The fix must not break relational grounding itself — otherwise
    it is 'refuse all relational claims' wearing a numeric costume.

    Under ADR-007 this control moved from the verdict to the diagnostic: corroboration is still measured (relation_diagnostic), it just no longer votes on the gate, so this is not a weakening."""
    rep = _report(tmp_path,
                  "Insulin resistance causes type 2 diabetes [S2][S3].\n",
                  NO_NUMBER)
    assert rep["per_claim"][0]["relation_diagnostic"] == g.RELATION_CORROBORATED
    assert rep["per_claim"][0]["verdict"] == "UNVERIFIED_RELATION"
    assert rep["gate"] == "FAIL"


def test_a_figure_PRESENT_in_the_store_leaves_the_diagnostic_clean(tmp_path):
    """The control that matters most: this must not become 'any number fails'.

    Under ADR-007 this control moved from the verdict to the diagnostic: corroboration is still measured (relation_diagnostic), it just no longer votes on the gate, so this is not a weakening."""
    rep = _report(tmp_path,
                  "Insulin resistance causes 97% of all type 2 diabetes "
                  "[S2][S3].\n", WITH_97)
    assert rep["per_claim"][0]["relation_diagnostic"] == g.RELATION_CORROBORATED
    assert rep["per_claim"][0]["verdict"] == "UNVERIFIED_RELATION"
    assert rep["gate"] == "FAIL"


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
    assert rep["per_claim"][0]["relation_diagnostic"] == g.RELATION_FIGURE_ABSENT
    assert rep["gate"] != "PASS"


def test_the_figure_satisfies_the_diagnostic_when_the_CITED_source_carries_it(tmp_path):
    """CONTROL for the above: cited-only must not become 'never grounds'.

    Under ADR-007 this control moved from the verdict to the diagnostic: corroboration is still measured (relation_diagnostic), it just no longer votes on the gate, so this is not a weakening."""
    rep = _report(tmp_path,
                  "Insulin resistance causes 97% of all type 2 diabetes "
                  "[S2][S3].\n", WITH_97)
    assert rep["per_claim"][0]["relation_diagnostic"] == g.RELATION_CORROBORATED
    assert rep["per_claim"][0]["verdict"] == "UNVERIFIED_RELATION"
    assert rep["gate"] == "FAIL"


# J-43 — CLOSED 2026-10-02 for the SPELLED-NUMBER class (Sai's ruling).
#
# A figure a reader would quote, written without a digit, was never extracted by
# _NUMERIC_RE and therefore never checked: all four variants below certified
# PASS 100.0 against a store holding no such figure.
#
# THE RULING, and why it is not the enumeration the round-11 note feared. That
# note rejected a number-word list as "a blacklist over ways to WRITE a number".
# The distinction Sai drew is the one that matters: a code comment syntax is an
# OPEN set (a new language can add one tomorrow), whereas the English cardinal
# number words are CLOSED — a writer cannot invent a new word for 97 and still
# be understood, and being understood is the entire reason for spelling it out.
# So the set is a lexicon, not a guess at author behaviour.
#
# The check is VERBATIM PRESENCE, not parsing: the spelled phrase must occur
# contiguously in a source the claim CITES. "ninety-seven" is never converted to
# 97 and never compared to a source's "97%" — a digits-only source is a refusal,
# which is the honest verdict when proving the two equal needs a parser the moat
# does not have.
@pytest.mark.parametrize("figure", [
    "ninety-seven percent of all",
    "ninety seven percent of all",
    "ninety-seven of all",            # the unit dropped
])
def test_a_figure_spelled_in_words_is_also_checked(tmp_path, figure):
    rep = _report(tmp_path,
                  f"Insulin resistance causes {figure} type 2 diabetes "
                  f"[S2][S3].\n", NO_NUMBER)
    assert rep["gate"] != "PASS"
    assert rep["per_claim"][0]["relation_diagnostic"] == g.RELATION_FIGURE_ABSENT


# R12-05 — the lexicon's own omission, which is NOT the open-class trap above.
#
# PROVEN RED: "The outage causes thousands of customer refunds [S1][S2]"
# certified GROUNDED at PASS 100.0 while "fifty thousand" was refused on the
# SAME store, because the plural scale words were missing from
# _SPELLED_NUMBER_WORDS and _spelled_quantity_phrases therefore returned () —
# read downstream as "no quantity asserted". That is the round-4 anti-pattern
# (an unreadable field read as UNCONSTRAINED) inside the very guard whose
# comment cites it. Five missing strings, not an open class.
@pytest.mark.parametrize("figure", [
    "thousands of", "hundreds of", "millions of", "billions of", "dozens of",
])
def test_a_plural_scale_word_is_checked_R12_05(tmp_path, figure):
    rep = _report(tmp_path,
                  f"Insulin resistance causes {figure} type 2 diabetes "
                  f"[S2][S3].\n", NO_NUMBER)
    assert rep["per_claim"][0]["relation_diagnostic"] == g.RELATION_FIGURE_ABSENT
    assert rep["gate"] != "PASS"


def test_a_spelled_figure_the_CITED_SOURCE_CARRIES_satisfies_the_diagnostic(tmp_path):
    """The other direction, which is what makes this a check and not a ban.

    Without this, `spelled_quantity_ok` returning False unconditionally would
    satisfy every test above — the tautology INS-005 exists to catch.

    Under ADR-007 this control moved from the verdict to the diagnostic: corroboration is still measured (relation_diagnostic), it just no longer votes on the gate, so this is not a weakening.
    """
    spelled = [
        _rec("S2", "Insulin resistance impairs glucose uptake and causes "
                   "ninety-seven percent of type 2 diabetes to develop."),
        _rec("S3", "Type 2 diabetes develops in ninety-seven percent of cases "
                   "when insulin resistance progresses."),
    ]
    rep = _report(tmp_path,
                  "Insulin resistance causes ninety-seven percent of all type 2 "
                  "diabetes [S2][S3].\n", spelled)
    assert rep["per_claim"][0]["relation_diagnostic"] == g.RELATION_CORROBORATED
    assert rep["per_claim"][0]["verdict"] == "UNVERIFIED_RELATION"
    assert rep["gate"] == "FAIL"


def test_a_spelled_phrase_may_not_be_ASSEMBLED_from_two_sources(tmp_path):
    """"ninety" in one document and "seven" in another is not "ninety-seven"."""
    split = [
        _rec("S2", "Insulin resistance causes type 2 diabetes in roughly "
                   "ninety of the reviewed cohorts."),
        _rec("S3", "Type 2 diabetes develops when insulin resistance "
                   "progresses, across seven distinct mechanisms."),
    ]
    rep = _report(tmp_path,
                  "Insulin resistance causes ninety-seven percent of all type 2 "
                  "diabetes [S2][S3].\n", split)
    assert rep["per_claim"][0]["relation_diagnostic"] == g.RELATION_FIGURE_ABSENT


def test_a_relational_claim_with_no_spelled_figure_is_untouched(tmp_path):
    """The guard must be invisible to every claim that does not spell a figure —
    otherwise J-43's fix is an Error-A tax on the whole relational class.

    Under ADR-007 this control moved from the verdict to the diagnostic: corroboration is still measured (relation_diagnostic), it just no longer votes on the gate, so this is not a weakening."""
    rep = _report(tmp_path,
                  "Insulin resistance causes type 2 diabetes [S2][S3].\n",
                  NO_NUMBER)
    assert rep["per_claim"][0]["relation_diagnostic"] == g.RELATION_CORROBORATED
    assert rep["per_claim"][0]["verdict"] == "UNVERIFIED_RELATION"
    assert rep["gate"] == "FAIL"


@pytest.mark.xfail(strict=True, reason=(
    "J-43 RESIDUE, deliberately open: a quantity with no number word in it. "
    "'almost all', 'the vast majority', 'nearly every' are an OPEN class — "
    "there is no closed lexicon of ways to be vague, so enumerating them IS "
    "the trap the number-word set avoids by being a lexicon. Refusing them "
    "would also tax honest hedged prose the n=52 corpus does not contain, so "
    "the Error-A is unmeasured. Escalation #1 if anyone wants it closed. "
    "NOT to be confused with a MISSING MEMBER of the closed lexicon, which is "
    "an ordinary bug and was one: round 12 (R12-05) found 'thousands' / "
    "'hundreds' / 'millions' absent, so the guard ran vacuously on the "
    "commonest fabricated magnitude. Closed 2026-10-02 and pinned below."))
def test_a_vague_quantifier_is_still_not_checked(tmp_path):
    rep = _report(tmp_path,
                  "Insulin resistance causes almost all type 2 diabetes "
                  "[S2][S3].\n", NO_NUMBER)
    assert rep["per_claim"][0]["relation_diagnostic"] == g.RELATION_FIGURE_ABSENT
    assert rep["gate"] != "PASS"


def test_per_cent_refuses_an_UNRELATED_digit_J53(tmp_path):
    """J-53 — inserting the words "per cent" flips an unrelated digit's verdict.

    The control moved from the verdict to the diagnostic under ADR-007: corroboration
    is still measured, it just no longer votes, so this is not a weakening.

    RE-PINNED 2026-10-02 (D-46). This test used to use the claim "... causes
    ninety-seven per cent of all type 2 diabetes", and J-43's fix would now
    refuse that claim for a GENUINE reason (the spelled phrase is absent from
    the store) — which would have left this assertion passing while saying
    nothing at all about J-53. A fix that makes an unrelated tripwire pass has
    MASKED it until proven otherwise, so the fixture moved to the isolated repro
    from its own docstring: a bare digit, no spelled number word anywhere.

        "... causes diabetes in 2 distinct ways [S2][S3]"          -> GROUNDED
        "... causes per cent diabetes in 2 distinct ways [S2][S3]" -> UNVERIFIED_NUMBER

    `_RATE_BEFORE_RE` reads "per <word>" out of the window BEFORE the number, so
    "per cent" is taken as the rate "cent" and the source's absolute 2 cannot
    match it. Error-A, fail-closed, and still open: fixing it is PASS-ENABLING
    (a claim that is refused today would certify), which is Escalation #1 and
    Sai's call, so J-43 deliberately did not touch it.
    """
    two_ways = [
        _rec("S2", "Insulin resistance impairs glucose uptake and causes "
                   "diabetes in 2 distinct ways."),
        _rec("S3", "Diabetes develops in 2 distinct ways once insulin "
                   "resistance progresses."),
    ]
    control = _report(tmp_path,
                      "Insulin resistance causes diabetes in 2 distinct ways "
                      "[S2][S3].\n", two_ways)
    assert control["per_claim"][0]["relation_diagnostic"] == g.RELATION_CORROBORATED, (
        "the control must corroborate, or this test proves nothing about per cent")
    assert control["per_claim"][0]["verdict"] == "UNVERIFIED_RELATION"

    rep = _report(tmp_path,
                  "Insulin resistance causes per cent diabetes in 2 distinct "
                  "ways [S2][S3].\n", two_ways)
    assert rep["per_claim"][0]["relation_diagnostic"] == g.RELATION_FIGURE_ABSENT
    assert _spelled_quantity_phrases_absent(rep), (
        "the fixture must contain no spelled number word, or J-43's guard "
        "would be what refuses it and J-53 would be masked again")


def _spelled_quantity_phrases_absent(report) -> bool:
    """True iff no claim in *report* contains a spelled number word.

    Guards the J-53 fixture against the exact masking D-46 describes: if someone
    later edits that claim text to include a number word, J-43's guard starts
    producing the verdict and the J-53 assertion becomes a tautology.
    """
    return all(
        not g._spelled_quantity_phrases(pc["text"])
        for pc in report["per_claim"]
    )
