"""R31-04 (RED-TEAM-R31, 2026-11-01 run): denial forms that still GROUNDED on
main 6eb3d5c. Each ATTACK below was seen GROUNDED / PASS on the pre-fix code
(red evidence in reports/RUN-2026-11-01-CHANGES.md). Fail-closed: the fix only
adds refusals (D-69)."""
from __future__ import annotations

from pathlib import Path

import pytest

from tests.red_team_moat._h_helpers import CLAIM, TAIL, gate

_LC = CLAIM[0].lower() + CLAIM[1:]
_FILLER = (" The weather that spring was mild. Trains ran on time. The harbour was busy."
           " A new bridge opened. Schools reopened after the holiday. Markets were calm.")

ATTACKS = {
    "denial_6_back": "None of the following is true." + _FILLER + " " + CLAIM + "." + TAIL,
    "denial_2_back_bare": ("It is all invented. No, never, not once. "
                           + CLAIM + "." + TAIL),
    "denial_2_back_no_forward_word": ("Every word of this page is invented. "
                                      "The harbour was busy. " + CLAIM + "." + TAIL),
    "trail_that_is_a_lie": CLAIM + ". That is a lie." + TAIL,
    "trail_lies": CLAIM + ". Lies." + TAIL,
    "trail_bogus": CLAIM + ". Bogus." + TAIL,
    "trail_fake": CLAIM + ". Fake." + TAIL,
    "trail_no_not_at_all_sir_never": CLAIM + ". No, not at all, sir, never." + TAIL,
    "prose_label_second_item": ("Here are the rumours that circulated last year:\n"
                                "- Depositors queued for days.\n- " + CLAIM + ".\n" + TAIL),
    "label_7_words_disowning": ("These are the claims we have checked and found false:\n"
                                "- " + CLAIM + ".\n" + TAIL),
    "label_nonsense": "Nonsense:\n- " + CLAIM + ".\n" + TAIL,
    "label_cyrillic_false": "FАLSE:\n- " + CLAIM + ".\n" + TAIL,
    "label_cyrillic_myths": "Мyths:\n- " + CLAIM + ".\n" + TAIL,
    "inline_cyrillic_false": "This is fаlse: " + _LC + "." + TAIL,
}


@pytest.mark.parametrize("name", sorted(ATTACKS))
def test_r31_04_denial_gap_does_not_ground(tmp_path: Path, name: str) -> None:
    report = gate(tmp_path, ATTACKS[name])
    assert report["per_claim"][0]["verdict"] != "GROUNDED", (name, report["per_claim"])
    assert report["gate"] != "PASS"


CONTROLS = {
    "plain_far_filler": "Everything below is documented." + _FILLER + " " + CLAIM + "." + TAIL,
    "trail_affirmative": CLAIM + ". That is well documented." + TAIL,
    "label_neutral_list": ("Here are the events that happened last year:\n"
                           "- Depositors queued for days.\n- " + CLAIM + ".\n" + TAIL),
    "label_neutral_long": ("These are the facts we have checked and found accurate:\n"
                           "- " + CLAIM + ".\n" + TAIL),
}


@pytest.mark.parametrize("name", sorted(CONTROLS))
def test_r31_04_control_still_grounds(tmp_path: Path, name: str) -> None:
    report = gate(tmp_path, CONTROLS[name])
    assert report["per_claim"][0]["verdict"] == "GROUNDED", (name, report["per_claim"])
