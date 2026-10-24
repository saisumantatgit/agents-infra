"""H2 (2026-10-25): a short reply ("No." / "Not so." / "Untrue." / "False." /
"Hardly.") immediately AFTER the grounding sentence denies it and must not
ground. The AFTER cases were seen PASS on the pre-fix code (H1 committed).
The BEFORE cases were already refused (the 5-token hedge lookback crosses the
sentence boundary) EXCEPT "Nope." (seen PASS pre-fix); the rest are pinned as
guards, not claimed as H2 coverage."""
from __future__ import annotations

from pathlib import Path

import pytest

from tests.red_team_moat._h_helpers import CLAIM, TAIL, gate

REPLIES = ["No.", "Not so.", "Untrue.", "False.", "Hardly.", "Nope."]


@pytest.mark.parametrize("reply", REPLIES)
def test_h2_short_denial_after_does_not_ground(tmp_path: Path, reply: str) -> None:
    report = gate(tmp_path, CLAIM + ". " + reply + TAIL)
    assert report["per_claim"][0]["verdict"] != "GROUNDED", (reply, report["per_claim"])


@pytest.mark.parametrize("reply", REPLIES)
def test_h2_guard_short_denial_before_does_not_ground(tmp_path: Path, reply: str) -> None:
    report = gate(tmp_path, reply + " " + CLAIM + "." + TAIL)
    assert report["per_claim"][0]["verdict"] != "GROUNDED", (reply, report["per_claim"])


@pytest.mark.parametrize("reply", ["Yes.", "Indeed.", "Confirmed."])
def test_h2_control_short_affirmation_still_grounds(tmp_path: Path, reply: str) -> None:
    report = gate(tmp_path, CLAIM + ". " + reply + TAIL)
    assert report["per_claim"][0]["verdict"] == "GROUNDED", (reply, report["per_claim"])
