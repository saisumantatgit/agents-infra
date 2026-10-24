"""H4 (2026-10-25): a list label that disowns its items ("Fallacies:",
"Debunked:", "False claims:", "Rumours:" / "Rumors:", and "Myths:" for the
second item onward) must make every item under it non-grounding — the same
refusal "Common myths:" already gave its FIRST item through the hedge lookback.
Each ATTACK was seen GROUNDED on the pre-fix code. Refusal only (D-69)."""
from __future__ import annotations

from pathlib import Path

import pytest

from tests.red_team_moat._h_helpers import CLAIM, TAIL, gate

_ITEM = CLAIM[0].lower() + CLAIM[1:]
_OTHER = "- depositors were repaid in full within a week of the closure."

LABELS = ["Fallacies:", "Debunked:", "False claims:", "Rumours:", "Rumors:",
          "Common myths:", "Popular misconceptions:"]


def _first(label: str) -> str:
    return f"{label}\n- {_ITEM}.\n{_OTHER}\n" + TAIL.strip()


def _second(label: str) -> str:
    return f"{label}\n{_OTHER}\n- {_ITEM}.\n" + TAIL.strip()


def _numbered_with_blank(label: str) -> str:
    return f"## {label}\n\n1. depositors were repaid in full within a week.\n2. {_ITEM}.\n\n" + TAIL.strip()


@pytest.mark.parametrize("shape", [_first, _second, _numbered_with_blank],
                         ids=["first_item", "second_item", "numbered_heading"])
@pytest.mark.parametrize("label", LABELS)
def test_h4_items_under_a_disowning_label_do_not_ground(tmp_path: Path, label: str, shape) -> None:
    report = gate(tmp_path, shape(label))
    assert report["per_claim"][0]["verdict"] != "GROUNDED", (label, report["per_claim"])


@pytest.mark.parametrize("label", ["Key facts:", "Timeline:", "Findings:"])
def test_h4_control_neutral_label_still_grounds(tmp_path: Path, label: str) -> None:
    report = gate(tmp_path, _second(label))
    assert report["per_claim"][0]["verdict"] == "GROUNDED", (label, report["per_claim"])


def test_h4_control_list_ends_at_a_plain_paragraph(tmp_path: Path) -> None:
    src = f"Rumours:\n{_OTHER}\n\nThe record is clear.\n{CLAIM}.\n" + TAIL.strip()
    report = gate(tmp_path, src)
    assert report["per_claim"][0]["verdict"] == "GROUNDED", report["per_claim"]
