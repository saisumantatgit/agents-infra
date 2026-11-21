"""Round 4: recovered denials, honest controls, and open tripwires."""
import os
from pathlib import Path

import pytest

from tests.red_team_moat import _h_helpers as helpers

CLAIM = "Quay Trust was acquired by a larger rival last spring"


@pytest.fixture(autouse=True)
def baseline_gate(monkeypatch):
    if os.environ.get("E1_GATE_PATH"):
        monkeypatch.setattr(helpers, "GATE", Path(os.environ["E1_GATE_PATH"]))


@pytest.mark.parametrize("denial", [
    "However, that was cooked up.", "Officials said that was cooked up.",
    "Frankly, it was cooked up.", "In truth, it was dreamed up.",
    "This one was cooked up.", "That one was cooked up.",
    "That was all cooked up.", "That was just cooked up.",
    "That was entirely cooked up.", "That was completely cooked up.",
    "That was simply cooked up.", "It all was cooked up.",
    "That may have been cooked up.", "That might have been cooked up.",
    "That must have been cooked up.", "That could have been cooked up.",
    "It got cooked up.", "Reporters made it up out of thin air.",
    "Reporters made it up out of whole cloth.", "Reporters made it up to sell papers.",
    "Reporters made it up entirely.", "Reporters made that up wholesale.",
    "Reporters cooked that up as a joke.",
])
def test_denials(tmp_path, denial):
    report = helpers.gate(tmp_path, CLAIM + ". Staff filed records. " + denial, CLAIM + " [S1].")
    assert report["per_claim"][0]["verdict"] != "GROUNDED"
    assert report["gate"] != "PASS"


@pytest.mark.parametrize("idiom", ["It was made up to order.", "It was made up to size.",
    "It was made up to look like a merger.", "The firm promised to make it up to them.",
    "It was thought up by the founders in 2010."])
def test_honest_controls(tmp_path, idiom):
    report = helpers.gate(tmp_path, CLAIM + ". Staff filed records. " + idiom, CLAIM + " [S1].")
    assert report["per_claim"][0]["verdict"] == "GROUNDED"
    assert report["gate"] == "PASS"


@pytest.mark.parametrize("source", [
    CLAIM + ". It was co\u200boked up.",
    CLAIM + ". It was co\u00adoked up.",
    CLAIM + ". That claim, which ran in the paper and caused great concern, was cooked up.",
    CLAIM + ". They made up the acquisition.",
    CLAIM + ". It was whipped together.",
    CLAIM + ".\n\nStaff filed records. The meeting ended. It was cooked up.",
    "The following was cooked up: " + CLAIM + ".",
    CLAIM + ". It was conjured up.",
    CLAIM + ". It was thought up.",
    CLAIM + ". It was made up to deceive readers.",
    CLAIM + ". Reporters made it up, they admitted.",
    CLAIM + ". Reporters made it up to increase circulation.",
])
@pytest.mark.xfail(strict=True, reason="CEILING: unrecognized denial form or distant referent requires richer discourse analysis")
def test_open_evasions(tmp_path, source):
    report = helpers.gate(tmp_path, source, CLAIM + " [S1].")
    assert report["per_claim"][0]["verdict"] != "GROUNDED"
    assert report["gate"] != "PASS"
