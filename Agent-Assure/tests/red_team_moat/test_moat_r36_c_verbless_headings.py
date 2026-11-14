"""RED-TEAM-R36 hole c: verbless / verb-final-"-s" claim headings over a body
that does not support them were NON_CLAIM and certified PASS 100.0 on main
83a5cb9. Shapes are reports/r36_probe.py verbatim. The new heading lists drive
refusals only (D-69); _HEADING_ALLOWLIST is untouched."""
from __future__ import annotations

from pathlib import Path

import pytest

from tests.red_team_moat._h_helpers import gate

TRUE_LINE = "The regulator published its findings in June"
SOURCE = TRUE_LINE + "."
BODY = TRUE_LINE + " [S1].\n"

ATTACKS = [
    "# Bank Collapses",
    "# Acme guilty",
    "### PostgreSQL Fails",
    "# Fraud everywhere",
    "## CEO arrest imminent",
    "## Revenue doubles",
    "# Stock Plunges",
    "# Acme Bank Collapses",
]

# Honest label headings (several taken from tests/usage_genres/drafts) that
# must stay NON_CLAIM.
CONTROLS = [
    "## Results",
    "# Rainfall points",
    "# Index types",
    "# Rebase commands",
    "# Cache directives",
    "# Key findings",
    "## Release notes",
]


@pytest.mark.parametrize("heading", ATTACKS)
def test_claim_heading_is_scored(tmp_path: Path, heading: str) -> None:
    report = gate(tmp_path, SOURCE, heading + "\n\n" + BODY)
    head = report["per_claim"][0]
    assert head["kind"] != "NON_CLAIM", (heading, head)
    assert head["verdict"] != "GROUNDED", (heading, head)
    assert report["gate"] != "PASS", (heading, report["gate"])


@pytest.mark.parametrize("heading", CONTROLS)
def test_label_heading_stays_non_claim(tmp_path: Path, heading: str) -> None:
    report = gate(tmp_path, SOURCE, heading + "\n\n" + BODY)
    assert report["per_claim"][0]["kind"] == "NON_CLAIM", (heading, report["per_claim"][0])
    assert report["gate"] == "PASS", (heading, report["gate"])


# R40: "stumbles" is now a listed headline verb (`_R40_HEADLINE_VERBS_S`), so
# the strict xfail XPASSed and its marker was removed (assertion unchanged).
# The class stays open for other unlisted verbs: see
# test_moat_r40_ceiling_tripwires.py ("# Bank Folds", "# Stock Drops", ...).
def test_unlisted_headline_verb_is_scored(tmp_path: Path) -> None:
    report = gate(tmp_path, SOURCE, "# Acme Stumbles\n\n" + BODY)
    assert report["gate"] != "PASS", report["per_claim"][0]
