"""E1: a source disowns the copied claim via a phrasal falsity predicate."""
from pathlib import Path
import os

import pytest

from tests.red_team_moat import _h_helpers as helpers

gate = helpers.gate


@pytest.fixture(autouse=True)
def baseline_gate(monkeypatch: pytest.MonkeyPatch) -> None:
    if os.environ.get("E1_GATE_PATH"):
        monkeypatch.setattr(helpers, "GATE", Path(os.environ["E1_GATE_PATH"]))

CLAIM = "Quay Trust was acquired by a larger rival last spring"
DRAFT = CLAIM + " [S1]."
FILLERS = ["Staff filed records.", "The meeting ended."]
DENIALS = ["That was cooked up by the press.", "It was cooked up.",
           "The press made that up.", "Reporters cooked that up."]


@pytest.mark.parametrize("denial", DENIALS)
@pytest.mark.parametrize("count", range(3))
@pytest.mark.parametrize("position", ["before", "after"])
def test_pronoun_falsity_refuses(tmp_path: Path, denial: str, count: int, position: str) -> None:
    pieces = [denial, *FILLERS[:count], CLAIM + "."] if position == "before" else [
        CLAIM + ".", *FILLERS[:count], denial]
    report = gate(tmp_path, "The report is published on Mondays. " + " ".join(pieces), DRAFT)
    assert report["per_claim"][0]["verdict"] != "GROUNDED"
    assert report["gate"] != "PASS"


def test_forward_colon(tmp_path: Path) -> None:
    report = gate(tmp_path, "This was made up: " + CLAIM + ".", DRAFT)
    assert report["per_claim"][0]["verdict"] != "GROUNDED"
    assert report["gate"] != "PASS"


@pytest.mark.parametrize("denial", ["This was dreamed up.", "These were whipped up.",
    "Those were conjured up.", "All of it was thought up.",
    "The whole thing was dreamed up.", "The press makes this up.",
    "The press is making all of it up.", "Reporters cooked the story up."])
def test_other_predicates_and_referents(tmp_path: Path, denial: str) -> None:
    report = gate(tmp_path, CLAIM + ". Staff filed records. " + denial, DRAFT)
    assert report["per_claim"][0]["verdict"] != "GROUNDED"
    assert report["gate"] != "PASS"


@pytest.mark.parametrize("source", ["This was cooked up: " + CLAIM + ".",
    CLAIM + ", but reporters cooked that up."])
def test_same_sentence(tmp_path: Path, source: str) -> None:
    report = gate(tmp_path, source, DRAFT)
    assert report["per_claim"][0]["verdict"] != "GROUNDED"
    assert report["gate"] != "PASS"


@pytest.mark.parametrize("continuation", ["It is made up of three parts.",
    "The team made up the shortfall.", "Women make up two thirds of the team.",
    "The team made up the numbers.", "Women make up the bulk of the team."])
def test_constituting_and_shortfall_controls(tmp_path: Path, continuation: str) -> None:
    report = gate(tmp_path, CLAIM + ". " + continuation, DRAFT)
    assert report["per_claim"][0]["verdict"] == "GROUNDED"
    assert report["gate"] == "PASS"
