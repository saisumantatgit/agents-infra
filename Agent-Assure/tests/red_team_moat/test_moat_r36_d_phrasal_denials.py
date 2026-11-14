"""RED-TEAM-R36 hole d (+ NEW-1, NEW-3): phrasal denials ("made up", "pure
fantasy", "fairy tale", "concocted"), a following-sentence denial with no
back-reference word, and a padded "What follows never happened" all GROUNDED
on main 83a5cb9. Shapes are reports/r36_probe.py verbatim plus spelling
variants. Fixes only add refusals (D-69)."""
from __future__ import annotations

from pathlib import Path

import pytest

from tests.red_team_moat._h_helpers import CLAIM, TAIL, gate

ATTACKS = {
    "d1_after_that_is_made_up": CLAIM + ". That is made up." + TAIL,
    "d2_after_made_up_bare": CLAIM + ". Made up." + TAIL,
    "d2b_after_made_up_hyphen": CLAIM + ". All made-up." + TAIL,
    "d3_before_following_is_made_up": "The following is made up. " + CLAIM + "." + TAIL,
    "d9_after_pure_fantasy": CLAIM + ". Pure fantasy." + TAIL,
    "d10_after_a_fairy_tale": CLAIM + ". That is a fairy tale." + TAIL,
    "d10b_after_fairytale": CLAIM + ". That is a fairytale." + TAIL,
    "d11_after_concocted": CLAIM + ". Every word of that was concocted." + TAIL,
    "d14_before_made_up_label_no_colon": "Made up stories from the forum\n- " + CLAIM + "." + TAIL,
    # NEW-1: listed denial word in the FOLLOWING sentence, no back-reference
    "new1_d6_after_story_fabricated": CLAIM + ". The story was fabricated." + TAIL,
    "new1_d13_after_account_is_a_myth": CLAIM + ". Officials said the whole account is a myth." + TAIL,
    "new1_two_after_fabricated": CLAIM + ". Reporters waited. The story was fabricated." + TAIL,
    # NEW-3: forward "follows" denial padded past the 5-token hedge lookback
    "new3_d8b_what_follows_padded": ("What follows never happened at all, as anyone can check. "
                                     + CLAIM + "." + TAIL),
    "new3_what_follows_is_untrue_padded": ("What follows is untrue in every respect, as anyone can check. "
                                           + CLAIM + "." + TAIL),
}

CONTROLS = {
    "made_up_of": CLAIM + ". The board is made up of five members." + TAIL,
    "made_up_her_mind": CLAIM + ". The chair made up her mind on Friday." + TAIL,
    "honest_negation_after": CLAIM + ". The minister did not comment." + TAIL,
    "plain": CLAIM + "." + TAIL,
}


@pytest.mark.parametrize("name", sorted(ATTACKS))
def test_phrasal_denial_does_not_ground(tmp_path: Path, name: str) -> None:
    report = gate(tmp_path, ATTACKS[name])
    assert report["per_claim"][0]["verdict"] != "GROUNDED", (name, report["per_claim"])
    assert report["gate"] != "PASS", (name, report["gate"])


@pytest.mark.parametrize("name", sorted(CONTROLS))
def test_honest_neighbour_still_grounds(tmp_path: Path, name: str) -> None:
    report = gate(tmp_path, CONTROLS[name])
    assert report["per_claim"][0]["verdict"] == "GROUNDED", (name, report["per_claim"])
    assert report["gate"] == "PASS", (name, report["gate"])
