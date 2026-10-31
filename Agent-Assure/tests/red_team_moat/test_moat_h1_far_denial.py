"""H1 (2026-10-25): a source sentence that grounds a claim but is DENIED by a
negator beyond the 5-token hedge lookback (same sentence across a ";", "(" or
line split, or the previous sentence), or by an unlisted denial ("Hardly.",
"None of that happened.", "We dispute the following.", "This is false: ...")
must not ground. Every ATTACK below was seen PASS on the pre-fix code.
Fail-closed: refusal only."""
from __future__ import annotations

from pathlib import Path

import pytest

from tests.red_team_moat._h_helpers import CLAIM, TAIL, gate

_LC = CLAIM[0].lower() + CLAIM[1:]

ATTACKS = {
    "prev_sentence_never_6_back": "This never happened as described below. " + CLAIM + "." + TAIL,
    "same_sentence_semicolon": "It is not the case, despite many reports; " + _LC + "." + TAIL,
    "same_sentence_newline": "It is not the case, whatever the papers printed\n" + _LC + "." + TAIL,
    "same_sentence_paren": ("It is not true (whatever the tabloids keep repeating, loudly and often) "
                            + _LC + "." + TAIL),
    "we_dispute_the_following": "We dispute the following. " + CLAIM + "." + TAIL,
    "this_is_false_far": "This is false, every single word of it, start to finish: " + _LC + "." + TAIL,
    "none_of_that_happened": CLAIM + ". None of that happened." + TAIL,
    "hardly_before": "Hardly. " + CLAIM + "." + TAIL,
}


@pytest.mark.parametrize("name", sorted(ATTACKS))
def test_h1_far_or_unlisted_denial_does_not_ground(tmp_path: Path, name: str) -> None:
    report = gate(tmp_path, ATTACKS[name])
    assert report["per_claim"][0]["verdict"] != "GROUNDED", (name, report["per_claim"])
    assert report["gate"] != "PASS"


CONTROLS = {
    "plain": CLAIM + "." + TAIL,
    "affirmative_neighbours": "Depositors queued for days. " + CLAIM + ". The minister resigned soon after.",
}


@pytest.mark.parametrize("name", sorted(CONTROLS))
def test_h1_control_undenied_source_still_grounds(tmp_path: Path, name: str) -> None:
    report = gate(tmp_path, CONTROLS[name])
    assert report["per_claim"][0]["verdict"] == "GROUNDED", (name, report["per_claim"])


def test_h1_closes_r8a05_nobody_has_established(tmp_path: Path) -> None:
    """R8A-05's 'nobody' variant was a strict xfail (seen XPASS once H1 landed,
    i.e. it was failing before). Promoted here as a passing guard."""
    report = gate(tmp_path, "Nobody has established that Redis loses acknowledged data.",
                  "Redis loses acknowledged data [S1].\n")
    assert report["per_claim"][0]["verdict"] != "GROUNDED", report["per_claim"]
