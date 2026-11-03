"""R34-04 (RUN-2026-11-04): the OI-MOAT-19 heading checks (final "-ed"
participle, claim-bearing word list) tested the raw text, so a Cyrillic look-
alike letter or a zero-width character turned "# Bank collapsed" back into a
label and the fabricated headline certified PASS. Fail-closed (D-69): the fold
is used only for the test; the heading text is never rewritten."""
from __future__ import annotations

from pathlib import Path

import pytest

from tests.red_team_moat._h_helpers import CLAIM, DRAFT, TAIL, gate

SOURCE = CLAIM + "." + TAIL

ATTACKS = {
    "cyrillic_e_participle": "# Bank collapsеd",
    "cyrillic_o_claim_word": "# Recоrd profits",
    "zwsp_after_participle": "# Bank collapsed​",
    "zwj_inside_claim_word": "# Rec‍ord profits",
    "soft_hyphen_participle": "# Bank collap­sed",
}


@pytest.mark.parametrize("name", sorted(ATTACKS))
def test_disguised_claim_heading_blocks_pass(tmp_path: Path, name: str) -> None:
    report = gate(tmp_path, SOURCE, ATTACKS[name] + "\n\n" + DRAFT)
    assert report["per_claim"][0]["verdict"] != "GROUNDED", (name, report["per_claim"])
    assert report["gate"] != "PASS", (name, report["gate"])


def test_label_heading_with_zwsp_still_passes(tmp_path: Path) -> None:
    report = gate(tmp_path, SOURCE, "## Results​\n\n" + DRAFT)
    assert report["gate"] == "PASS", report["per_claim"]
