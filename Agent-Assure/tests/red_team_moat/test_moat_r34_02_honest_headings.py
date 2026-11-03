"""R34-02 (D-104, RUN-2026-11-04b): the OI-MOAT-19 heading rules (claim-word
list, final "-ed" participle) refused honest label headings that main 41a7e2e
passed. Each heading below sits over one cited, grounded sentence and must
PASS. The attacks in test_moat_oi_moat_19_verbless_headings.py and
test_moat_r34_04_heading_confusables.py stay refused."""
from __future__ import annotations

from pathlib import Path

import pytest

from tests.red_team_moat._h_helpers import CLAIM, DRAFT, TAIL, gate

SOURCE = CLAIM + "." + TAIL

HONEST = [
    "## Record of decisions",
    "## Track record",
    "# Widespread adoption notes",
    "# Historic overview",
    "# Dramatic irony",
    "# Huge pages",
    "## Collapse sections",
    "## Work completed",
    "## What this record cannot tell you",
    "## What changed",
    "## The moat: mechanical, not model-judged",
]


@pytest.mark.parametrize("heading", HONEST)
def test_honest_label_heading_passes(tmp_path: Path, heading: str) -> None:
    report = gate(tmp_path, SOURCE, heading + "\n\n" + DRAFT)
    assert report["gate"] == "PASS", (heading, report["per_claim"])


# Near neighbours of the honest idioms that still predicate: must stay refused.
NEIGHBOURS = [
    "# The record profits",
    "# Record losses",
    "# Record of fraud at Acme confirmed",
    "# Work stopped",
    "# What changed: bank collapsed",
    "# Bank, not collapsed",
    "# Dramatic collapse",
    "# Huge losses",
    "# Widespread fraud",
]


@pytest.mark.parametrize("heading", NEIGHBOURS)
def test_predicating_neighbour_still_refused(tmp_path: Path, heading: str) -> None:
    report = gate(tmp_path, SOURCE, heading + "\n\n" + DRAFT)
    assert report["gate"] != "PASS", (heading, report["per_claim"])
