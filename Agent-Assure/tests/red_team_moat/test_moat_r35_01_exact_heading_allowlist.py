"""R35-01 (RUN-2026-11-04b): the a4bc1f8 heading exemptions were pattern rules
(label-final noun, "Record of X", "X, not Y-ed", "record cannot tell") and
re-opened OI-MOAT-19 attacks. The exemption is now an exact whole-heading allow
list; each heading below sits over one cited, grounded sentence and must NOT
PASS."""
from __future__ import annotations

from pathlib import Path

import pytest

from tests.red_team_moat._h_helpers import CLAIM, DRAFT, TAIL, gate

SOURCE = CLAIM + "." + TAIL

ATTACKS = [
    "# Record of fraud",
    "# Scandal notes",
    "# Insolvent overview",
    "# Bankrupt sections",
    "# Massive fraud notes",
    "# Bank solvent, not fraud-tainted",
    "# Acme, not bankrupt-declared",
    "# This record cannot tell lies",
    "# Widespread fraud notes",
    "# Historic fraud overview",
]


@pytest.mark.parametrize("heading", ATTACKS)
def test_pattern_neighbour_of_allowlisted_heading_refused(tmp_path: Path, heading: str) -> None:
    report = gate(tmp_path, SOURCE, heading + "\n\n" + DRAFT)
    assert report["gate"] != "PASS", (heading, report["per_claim"])


@pytest.mark.parametrize("heading", ["## TRACK RECORD", "## Track Record.", "##  track   record"])
def test_track_record_casing_variants_pass(tmp_path: Path, heading: str) -> None:
    report = gate(tmp_path, SOURCE, heading + "\n\n" + DRAFT)
    assert report["gate"] == "PASS", (heading, report["per_claim"])
