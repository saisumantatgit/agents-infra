"""prev_denial_stray / fence_unclosed_then_fence (RUN-2026-11-04): denials of
the claim that GROUNDED on main 41a7e2e. Shapes are the r32 probe's verbatim
(c.json). Fail-closed: the fixes only add refusals (D-69)."""
from __future__ import annotations

from pathlib import Path

import pytest

from tests.red_team_moat._h_helpers import CLAIM, gate

ATTACKS = {
    # r32 probe prev_denial_stray, verbatim: the denial is TWO sentences back
    "prev_denial_stray": "The ` char. None of this is true. Use `z`.\n" + CLAIM + ".",
    "prev_denial_no_backtick": "The char. None of this is true. Use z.\n" + CLAIM + ".",
    "prev_bare_denial_two_back": "The harbour was busy. Lies. Use z.\n" + CLAIM + ".",
}

CONTROLS = {
    "two_back_neutral": "The harbour was busy. All of this is documented. Use z.\n" + CLAIM + ".",
}


@pytest.mark.parametrize("name", sorted(ATTACKS))
def test_denial_two_sentences_back_does_not_ground(tmp_path: Path, name: str) -> None:
    report = gate(tmp_path, ATTACKS[name])
    assert report["per_claim"][0]["verdict"] != "GROUNDED", (name, report["per_claim"])
    assert report["gate"] != "PASS"


@pytest.mark.parametrize("name", sorted(CONTROLS))
def test_neutral_two_back_still_grounds(tmp_path: Path, name: str) -> None:
    report = gate(tmp_path, CONTROLS[name])
    assert report["per_claim"][0]["verdict"] == "GROUNDED", (name, report["per_claim"])
