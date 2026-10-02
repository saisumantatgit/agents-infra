"""J-33 OPEN — an UNRECOGNISED citation marker is worse than an unresolved one.

Found by the solo gate on J-25 (SOLO-GATE-J25-2026-10-01.md) and reproduced
independently by the orchestrator before being recorded.

J-25 made an UNRESOLVED citation fail closed. It did nothing about an
UNRECOGNISED one, and the difference is the whole finding:

    _CITATION_RE = \\[(?:S\\d+[a-zA-Z]*|source:[^\\]]+)\\]

is case-sensitive and narrow, so a marker it does not match does not become an
unresolved citation — it becomes NO citation. `claim.citations` is empty of the
fake, J-25's `any(resolve(...) is None ...)` has nothing to object to, and
RELATIONAL and ABSENCE claims certify with zero citations BY DESIGN.

Net effect: show the reader a citation the parser cannot see, and the claim
certifies against unrelated store contents at PASS 100.0.

One Shift keystroke separates `[S99]` (FAIL, UNVERIFIED_CITATION) from `[s99]`
(PASS). That is round 4's lesson — never key a moat rule on a surface property
the author controls — for the THIRD time in this project.

POSITION IS ALSO LOAD-BEARING, and it caught me out: with the fake marker
trailing the sentence, its leftover text breaks `extract_arguments` and the
claim is refused by accident. With the marker LEADING, it certifies. My first
reproduction used the trailing position and I wrongly reported the RELATIONAL
half as not reproducing.

Fixing this is NOT simply widening the regex: a widened matcher also catches
`[sic]`, `[1]`, `[see Appendix A]`, each of which would become an unresolvable
citation and a refusal. That is Error-A on honest prose, and it is unmeasured
by the n=52 corpus, which contains none of these shapes. Hence OPEN, with a
recommendation recorded in docs/jobs/REGISTER.md rather than a patch at 03:30.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))

import ground_check as g  # noqa: E402


def _rec(sid, text, qp):
    return {"source_id": sid, "url": None, "file_path": "/tmp/a",
            "fetched_at": "2026-09-13T00:00:00Z", "tool": "Read",
            "content_sha256": "a" * 64, "text": text,
            "full_text_source": "verbatim", "captured_via": "inline",
            "query_provenance": qp}


REL = [
    _rec("S2", "Insulin resistance impairs glucose uptake and is a central "
               "mechanism that causes type 2 diabetes to develop.", "q-S2"),
    _rec("S3", "Type 2 diabetes develops when insulin resistance progresses "
               "and the pancreas can no longer compensate.", "q-S3"),
]

ABS = [
    _rec("SA1", "No recall evidence was found in the manufacturer's safety "
                "bulletin archive for the X200 drone line.",
         "recall evidence search X200 drone"),
    _rec("SA2", "The public recall database returned zero results for X200 "
                "drone safety evidence.",
         "regulatory database evidence query X200"),
]


def _run(tmp_path, draft, records):
    p = tmp_path / "s.jsonl"
    p.write_text("".join(json.dumps(r) + "\n" for r in records), encoding="utf-8")
    return g.score_report([g.classify(c) for c in g.decompose(draft)],
                          g.load_store(str(p)))


# Spellings a human reader treats as a citation and _CITATION_RE does not match.
# "[S99]" is deliberately ABSENT: it is the one spelling J-25 DOES catch, and it
# is the control below. The set deliberately spans FOUR different mechanisms —
# case, internal whitespace, trailing punctuation, a non-ASCII homoglyph — so
# that a fix addressing only one of them cannot green this file.
# VERIFIED to evade, in the leading position, on this tree. The solo gate
# reported 13 of 18 spellings evading; only these FOUR reproduced for me on the
# relational path, so four is what is recorded. The gate's wider number is not
# disputed for other configurations - it is simply not what I measured, and the
# register carries the count I could reproduce rather than the one I was handed.
# MASKED BY J-39, NOT FIXED (2026-10-02). "[Sxx]" was the LAST live relational
# demonstrator of J-33. J-39 made each endpoint the contiguous head-noun phrase
# rather than one token, so the unparsed marker's leftover text ("sxx") is now
# swallowed into side_A — "sxx insulin resistance" — which no source carries,
# and the claim is refused. The refusal has nothing to do with the citation: it
# is the SAME accident already pinned for trailing position below, now reaching
# leading position too.
#
# So J-33's relational shape is fully masked: digits leak for three spellings
# (J-40) and leftover text pollutes the endpoint for the fourth (J-39). The
# finding itself is untouched — _CITATION_RE still cannot parse these markers,
# so they are still NO citation rather than an unresolved one — and it stays
# live and strict on the ABSENCE path below, which does not extract arguments.
#
# Pinned here with the explanation rather than deleted, per the standing rule:
# when a fix makes an unrelated tripwire pass, assume it MASKED the finding
# until proven CLOSED. A tripwire that goes silent while looking healthy is
# worse than one that stays red.
MASKED_BY_ENDPOINT_PHRASE = [
    "[Sxx]",
]

UNRECOGNISED: list[str] = []

# MASKED BY J-40, NOT FIXED. These three still parse as NO citation — J-33 is
# untouched for them. They are refused only because the unparsed marker leaves
# its DIGITS in the sentence, "99" leaks into claim.numeric_tokens, and J-40's
# new relational numeric check cannot find 99 in the store. Drop the digits and
# the attack returns, which is exactly what "[Sxx]" above demonstrates.
#
# They are pinned HERE, as controls with this explanation, rather than quietly
# converted to passing tests. Converting them would have made the register read
# as though J-33 had shrunk from four shapes to one, when all that happened is
# that an unrelated fix masked three of them. That is a tripwire going silent
# while looking healthy — the same failure J-26 exposed in the r8 fixtures
# earlier the same night.
MASKED_BY_DIGIT_LEAK = [
    "[s99]",
    "[ S99]",
    "[\u040599]",
]


@pytest.mark.parametrize("marker", MASKED_BY_DIGIT_LEAK)
def test_marker_refused_only_because_its_digits_leak(tmp_path, marker):
    rep = _run(tmp_path,
               f"{marker} Insulin resistance causes type 2 diabetes [S2][S3].\n",
               REL)
    assert rep["gate"] != "PASS"
    assert rep["per_claim"][0]["relation_diagnostic"] == g.RELATION_FIGURE_ABSENT, (
        "if this stops being FIGURE_ABSENT the masking has gone and J-33 "
        "is live again for this spelling")
    # RESTORED after the ADR-007 migration audit. Re-pointing the assertion at
    # the diagnostic lost the J-33 signal itself: the FINDING is that the marker
    # is never checked AS A CITATION, and only the VERDICT can say that. Without
    # this line the day someone teaches _CITATION_RE these spellings, the
    # diagnostic goes on reading FIGURE_ABSENT and the tripwire passes in
    # silence — blind, while looking healthy.
    assert rep["per_claim"][0]["verdict"] != "UNVERIFIED_CITATION", (
        "J-33 is CLOSED for this spelling — the marker is now checked as a "
        "citation. Move it out of MASKED_BY_DIGIT_LEAK and update J-33.")

# Markers a reader ALSO reads as citations, which _CITATION_RE likewise fails to
# match, but which are refused anyway - by ACCIDENT, because their leftover text
# breaks extract_arguments, exactly like the trailing-position case below.
# Pinned as controls, not counted as coverage: improve argument extraction and
# each of these becomes a new Error-B.
REFUSED_BY_ACCIDENT = [
    "[S99.]",
    "[S-99]",
    "[S99, S100]",
    "[Source:acme-report]",
]


@pytest.mark.parametrize("marker", REFUSED_BY_ACCIDENT)
def test_unparsed_marker_refused_only_because_its_text_breaks_extraction(
    tmp_path, marker
):
    rep = _run(tmp_path,
               f"{marker} Insulin resistance causes type 2 diabetes [S2][S3].\n",
               REL)
    assert rep["gate"] != "PASS"


@pytest.mark.parametrize("marker", MASKED_BY_ENDPOINT_PHRASE)
def test_leading_unrecognised_marker_is_refused_by_ACCIDENT(tmp_path, marker):
    """Refused, but not for the reason a reader would assume — see the comment
    on MASKED_BY_ENDPOINT_PHRASE. The assertion below proves the ACCIDENT is
    what refuses it: the verdict is UNVERIFIED_RELATION (the endpoint could not
    be found) and NOT UNVERIFIED_CITATION (the marker was never checked).

    If someone later teaches _CITATION_RE these spellings, this test keeps
    passing and the second assertion flips — which is the signal that J-33 was
    actually closed rather than hidden."""
    rep = _run(tmp_path,
               f"{marker} Insulin resistance causes type 2 diabetes [S2][S3].\n",
               REL)
    assert rep["gate"] != "PASS"
    assert rep["per_claim"][0]["relation_diagnostic"] == g.RELATION_NOT_CORROBORATED, (
        "the endpoint accident is what refuses this, not the citation")
    # The assertion this message used to carry. See the note above: the
    # diagnostic cannot express "J-33 is closed", only the verdict can.
    assert rep["per_claim"][0]["verdict"] != "UNVERIFIED_CITATION", (
        "J-33 is CLOSED for this shape — move the marker out of "
        "MASKED_BY_ENDPOINT_PHRASE and update J-33")


@pytest.mark.parametrize("marker", ["[s99]", "[Ѕ99]"])
@pytest.mark.xfail(strict=True, reason=(
    "J-33 OPEN: same gap on the absence path — ABSENCE_SUPPORTED at PASS "
    "100.0 with a visible citation the gate never checked."))
def test_absence_claim_with_unrecognised_marker_is_not_certified(tmp_path, marker):
    rep = _run(tmp_path,
               f"{marker} We found no evidence of a safety recall affecting "
               f"the X200 drone.\n", ABS)
    assert rep["gate"] != "PASS"


# --- controls: these keep the tripwires above honest ------------------------

def test_the_one_recognised_spelling_is_refused(tmp_path):
    """[S99] — what J-25 DOES close. One Shift keystroke from the xfails above."""
    rep = _run(tmp_path,
               "[S99] Insulin resistance causes type 2 diabetes [S2][S3].\n", REL)
    assert rep["gate"] != "PASS"


def test_trailing_position_is_refused_by_accident_not_by_design(tmp_path):
    """Documents the ACCIDENTAL protection so nobody mistakes it for a fix: the
    unparsed marker's leftover text breaks extract_arguments. Remove that
    accident (e.g. by improving argument extraction) and this becomes a third
    Error-B, so it is pinned here deliberately."""
    rep = _run(tmp_path,
               "Insulin resistance causes type 2 diabetes [S2][S3][s99].\n", REL)
    assert rep["gate"] != "PASS"


def test_honest_relational_claim_is_corroborated_but_NOT_certified(tmp_path):
    """Under ADR-007 this control moved from the verdict to the diagnostic:
    corroboration is still measured (relation_diagnostic), it just no longer
    votes on the gate, so this is not a weakening."""
    rep = _run(tmp_path,
               "Insulin resistance causes type 2 diabetes [S2][S3].\n", REL)
    assert rep["per_claim"][0]["relation_diagnostic"] == g.RELATION_CORROBORATED
    assert rep["per_claim"][0]["verdict"] == "UNGROUNDED"
    assert rep["gate"] == "FAIL"
