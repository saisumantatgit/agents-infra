"""OI-MOAT-19 (RUN-2026-11-04): a verbless or verb-final heading that ASSERTS
something ("# Record profits", "# Fraud widespread", "# Acme fraud confirmed")
was NON_CLAIM on main 41a7e2e, so a draft of that heading over one cited true
claim certified PASS. Fail-closed: the fix only adds refusals (D-69)."""
from __future__ import annotations

from pathlib import Path

import pytest

from tests.red_team_moat._h_helpers import CLAIM, DRAFT, TAIL, gate

SOURCE = CLAIM + "." + TAIL

ATTACKS = {
    "record_profits": "# Record profits",
    "fraud_widespread": "# Fraud widespread",
    "fraud_rampant": "## Fraud rampant at Acme",
    # already refused on main (non-final -ed token); kept as a guard
    "unprecedented_losses": "### Unprecedented losses",
    "acme_fraud_confirmed": "# Acme fraud confirmed",
    "trial_failed": "## Trial failed",
    "bank_collapsed_title_case": "# Bank Collapsed",
}


@pytest.mark.parametrize("name", sorted(ATTACKS))
def test_claim_bearing_verbless_heading_blocks_pass(tmp_path: Path, name: str) -> None:
    report = gate(tmp_path, SOURCE, ATTACKS[name] + "\n\n" + DRAFT)
    heading = report["per_claim"][0]
    assert heading["verdict"] != "GROUNDED", (name, report["per_claim"])
    assert report["gate"] != "PASS", (name, report["gate"])


# Label headings main passes and must keep passing.
CONTROLS = {
    "results": "## Results",
    "key_findings": "## Key Findings",
    "harbour_summary": "# Harbour summary",
    "single_participle": "## Related",
    "index_types": "# Index types",
}


@pytest.mark.parametrize("name", sorted(CONTROLS))
def test_label_heading_still_passes(tmp_path: Path, name: str) -> None:
    report = gate(tmp_path, SOURCE, CONTROLS[name] + "\n\n" + DRAFT)
    assert report["gate"] == "PASS", (name, report["per_claim"])
