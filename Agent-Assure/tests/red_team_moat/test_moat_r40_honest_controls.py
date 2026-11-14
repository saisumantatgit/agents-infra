"""R40: honest controls for the R40 fail-closed rules. Each is the nearest
honest shape to one new rule; main ef3ae1f grounds every one, and R40 must
keep grounding it (an Error-A guard, not a red test: these pass on both).
Shapes R40 knowingly refuses are listed in reports/R40-FIXES.md, not here."""
from __future__ import annotations

from pathlib import Path

import pytest

from tests.red_team_moat._h_helpers import CLAIM, TAIL, gate

S = CLAIM + "." + TAIL
F = " Staff left. Records were filed. "

HONEST_SOURCES = {
    # H1: an honest correction after the claim in the same sentence
    "same_sentence_which_clause": CLAIM + ", which surprised analysts." + TAIL,
    "same_sentence_paren_aside": CLAIM + " (the second failure that year)." + TAIL,
    # H2/H3: constituting / manufacturing / invention senses
    "make_up_quantity": "Retail deposits make up two thirds of funding." + F + S,
    "make_up_the_bulk": "Students make up the bulk of the audience." + F + S,
    "invented_no_discourse_subject": "The telephone was invented in 1876." + F + S,
    "it_was_invented_by": "It was invented by engineers in 1990." + F + S,
    "an_invention_of": "It is an invention of the 1950s." + F + S,
    "fabricates_steel_adjacent": "The plant fabricates steel beams. " + S,
    "disinformation_campaigns_adjacent": "The agency tracks disinformation campaigns. " + S,
    "answer_lies_in": "The answer lies in the audit trail." + F + S,
    "falsely_accused": "He was falsely accused of fraud." + F + S,
    "dinner_cooked_up_far": "The chef cooked up a feast." + F + S,
    # H4: "real" as an attributive adjective, "occur" positive
    "not_a_real_number": "The value is not a real number." + F + S,
    "not_real_time": "The system is not real-time." + F + S,
    "did_occur": "The audit did occur in March." + F + S,
    # H5: "found false positives"
    "found_false_positives": "The scan found false positives in two files." + F + S,
    # H8: a long single-line pointing negative with no truth word
    "long_pointing_no_veracity": "This release does not change the default settings for any of the older plugins listed in the index." + F + S,
    # H10: a truth-word sub-heading ends a denial heading's scope; FAQ headings untouched
    "facts_subheading_ends_scope": "## Myths about the bank\n\nPeople talked.\n\n### The facts\n\nStaff left. Records were filed. Reporters waited.\n\n" + S,
    "next_same_level_heading_ends_scope": "## Myths about the bank\n\nPeople talked.\n\n## Results\n\nStaff left. Records were filed. Reporters waited.\n\n" + S,
    "myths_and_facts_then_short_line": "## Myths and facts\n\nPeople talked.\n\nAnd so\n\n" + S,
    # H11: honest headings with the new label words
    "lie_groups_heading": "## Lie groups\n\nPeople talked. Some wrote. Others posted.\n\n" + S,
    "false_positives_heading": "## False positives\n\nPeople talked. Some wrote. Others posted.\n\n" + S,
    "where_the_problem_lies": "## Where the problem lies\n\nPeople talked. Some wrote. Others posted.\n\n" + S,
    "what_went_wrong_heading": "## What went wrong\n\nPeople talked. Some wrote. Others posted.\n\n" + S,
    # H7: accented / non-Latin text with no denial word
    "accented_source": "Le caf\u00e9 a ferm\u00e9 en mars." + F + S,
    "soft_hyphen_honest": "The infor\u00admation was filed." + F + S,
}

HONEST_HEADINGS = [
    "## Results",
    "## Record-keeping",
    "## Long-term plans",
    "## Packet drops",
    "## Configuration defaults",
]

HEAD_SOURCE = CLAIM + "."
HEAD_BODY = CLAIM + " [S1].\n"


@pytest.mark.parametrize("name", sorted(HONEST_SOURCES))
def test_r40_honest_source_grounds(tmp_path: Path, name: str) -> None:
    report = gate(tmp_path, HONEST_SOURCES[name])
    assert report["per_claim"][0]["verdict"] == "GROUNDED", (name, report["per_claim"])
    assert report["gate"] == "PASS", (name, report["gate"])


@pytest.mark.parametrize("heading", HONEST_HEADINGS)
def test_r40_honest_heading_is_non_claim(tmp_path: Path, heading: str) -> None:
    report = gate(tmp_path, HEAD_SOURCE, heading + "\n\n" + HEAD_BODY)
    assert report["per_claim"][0]["kind"] == "NON_CLAIM", (heading, report["per_claim"][0])
    assert report["gate"] == "PASS", (heading, report["gate"])
