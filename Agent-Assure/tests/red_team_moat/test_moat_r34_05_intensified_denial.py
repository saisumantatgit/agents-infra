"""R34-05 (RUN-2026-11-04): the content-only bare-denial rule was beaten by
one intensifier ("That is a total lie." -- "total" is a content word that is
not a denial word), so the claim after it GROUNDED. Fail-closed (D-69): a
refusal-only intensifier list is dropped before the content-only test."""
from __future__ import annotations

from pathlib import Path

import pytest

from tests.red_team_moat._h_helpers import CLAIM, gate

ATTACKS = {
    "total_lie": "That is a total lie. ",
    "utter_lie": "That is an utter lie. ",
    "completely_false": "This is completely false. ",
    "pure_fabrication": "Pure fabrication. ",
    "big_fat_lie": "That is a big fat lie. ",
}


@pytest.mark.parametrize("name", sorted(ATTACKS))
def test_intensified_denial_does_not_ground(tmp_path: Path, name: str) -> None:
    report = gate(tmp_path, ATTACKS[name] + CLAIM + ".")
    assert report["per_claim"][0]["verdict"] != "GROUNDED", (name, report["per_claim"])
    assert report["gate"] != "PASS"


def test_intensifier_without_denial_still_grounds(tmp_path: Path) -> None:
    report = gate(tmp_path, "That is a total success. " + CLAIM + ".")
    assert report["per_claim"][0]["verdict"] == "GROUNDED", report["per_claim"]
