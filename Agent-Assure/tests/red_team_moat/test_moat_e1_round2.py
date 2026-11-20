"""Round 2: split-object falsity and honest phrasal idioms."""
from pathlib import Path
import os

import pytest

from tests.red_team_moat import _h_helpers as helpers

CLAIM = "Quay Trust was acquired by a larger rival last spring"


@pytest.fixture(autouse=True)
def baseline_gate(monkeypatch):
    if os.environ.get("E1_GATE_PATH"):
        monkeypatch.setattr(helpers, "GATE", Path(os.environ["E1_GATE_PATH"]))


@pytest.mark.parametrize("denial", [
    "Reporters made it all up.", "The press made up the whole thing.",
    "The press made the whole story up.", "The press made up the story.",
    "Reporters made everything up.", "Reporters made all that up.",
    "Reporters made stuff up.", "Reporters cook it up.",
    "Reporters are cooking it up.", "Reporters dream these up.",
    "Reporters cook it up in 2020.", "Reporters dream these up on Monday.",
    "This has been deliberately cooked up.",
])
def test_new_falsity_shapes(tmp_path, denial):
    report = helpers.gate(tmp_path, CLAIM + ". Staff filed records. " + denial,
                          CLAIM + " [S1].")
    assert report["per_claim"][0]["verdict"] != "GROUNDED"
    assert report["gate"] != "PASS"


@pytest.mark.parametrize("idiom", [
    "The firm promised to make it up to them.",
    "If we miss the target, we make it up with credits.",
    "The convoy made it up the hill.",
    "The share price made it up to a record.",
    "The pharmacist makes it up on request.",
    "This deal conjured up memories of 2008.",
    "This news whipped up support among staff.",
    "The chef cooked it up in ten minutes.",
    "It was thought up by the founders in 2010.",
    "It cooked up a storm in sales.",
    "Analysts said that staff dreamed up a new plan.",
    "Strong sales made the figures up 4 percent.",
    "The head chef cooked it up from an old family recipe.",
    "We will make it up to regular customers with a discount.",
    "Analysts said that the chef cooked up a meal.",
])
def test_honest_idioms(tmp_path, idiom):
    report = helpers.gate(tmp_path, CLAIM + ". Staff filed records. " + idiom,
                          CLAIM + " [S1].")
    assert report["per_claim"][0]["verdict"] == "GROUNDED"
    assert report["gate"] == "PASS"


def test_idiom_does_not_refuse_other_claims_in_paragraph(tmp_path):
    other = "Harbor Bank opened a branch in the city last autumn"
    source = CLAIM + ". " + other + ". The head chef cooked it up from an old family recipe."
    report = helpers.gate(tmp_path, source, CLAIM + " [S1]. " + other + " [S1].")
    assert [claim["verdict"] for claim in report["per_claim"]] == ["GROUNDED", "GROUNDED"]
    assert report["gate"] == "PASS"
