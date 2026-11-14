"""RED-TEAM-R36 hole a (+ NEW-2): a denial three or more sentences before the
copied claim, or a denial heading with no colon, GROUNDED on main 83a5cb9.
Shapes are reports/r36_probe.py verbatim. The denial lives in the SOURCE; the
draft copies the denied sentence as fact. Fixes only add refusals (D-69)."""
from __future__ import annotations

from pathlib import Path

import pytest

from tests.red_team_moat._h_helpers import CLAIM, TAIL, gate

ATTACKS = {
    "a1_none_of_this_3back": "None of this is true. Use z. Ok then. " + CLAIM + "." + TAIL,
    "a2_did_not_happen_3back": ("The collapse the tabloids describe did not happen. Staff left early. "
                                "Records were filed. " + CLAIM + "." + TAIL),
    "a3_it_is_false_that_long_following": (
        "It is false that any of the following events occurred as the press rumoured all year. "
        "The harbour was busy. Depositors queued. " + CLAIM + "." + TAIL),
    "a4_no_evidence_4back": ("There is no evidence for any of this. Staff left. Records were filed. "
                             "Reporters waited outside. " + CLAIM + "." + TAIL),
    # NEW-2: a denial heading with no colon, two paragraphs above the claim.
    "a5_paragraph_header_denial": ("Rumours we investigated and found to be false\n\nPeople talked. "
                                   "Some wrote letters. Others posted online.\n\n" + CLAIM + "." + TAIL),
    "new2_markdown_heading_myths": ("## Myths about the bank\n\nPeople talked. Some wrote letters. "
                                    "Others posted online.\n\n" + CLAIM + "." + TAIL),
    "a_far_six_back": ("This never happened. One. Two. Three. Four. Five. " + CLAIM + "." + TAIL),
}

CONTROLS = {
    # r36 control: neutral sentence three back still grounds
    "neutral_3back": "All of this is documented. Use z. Ok then. " + CLAIM + "." + TAIL,
    # an honest negative three back, with no forward/back reference and no
    # falsity word, is not a denial of the claim
    "honest_negation_3back": ("The bank did not pay a dividend. Staff left. Records were filed. "
                              + CLAIM + "." + TAIL),
    # an honest heading over the claim
    "honest_heading": "## Banking news\n\nPeople talked.\n\n" + CLAIM + "." + TAIL,
}


@pytest.mark.parametrize("name", sorted(ATTACKS))
def test_far_denial_does_not_ground(tmp_path: Path, name: str) -> None:
    report = gate(tmp_path, ATTACKS[name])
    assert report["per_claim"][0]["verdict"] != "GROUNDED", (name, report["per_claim"])
    assert report["gate"] != "PASS", (name, report["gate"])


@pytest.mark.parametrize("name", sorted(CONTROLS))
def test_honest_context_still_grounds(tmp_path: Path, name: str) -> None:
    report = gate(tmp_path, CONTROLS[name])
    assert report["per_claim"][0]["verdict"] == "GROUNDED", (name, report["per_claim"])
    assert report["gate"] == "PASS", (name, report["gate"])
