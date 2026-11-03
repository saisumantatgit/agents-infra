"""fence_unclosed_then_fence (RUN-2026-11-04): the r32 probe shape GROUNDED on
main 41a7e2e. The fence lines weld into the denial sentence ("``` ls That is a
lie"), so it is no longer a short bare denial. Fail-closed (D-69)."""
from __future__ import annotations

from pathlib import Path

import pytest

from tests.red_team_moat._h_helpers import CLAIM, gate

ATTACKS = {
    # r32 probe fence_unclosed_then_fence, verbatim
    "fence_unclosed_then_fence": "```\nls\nThat is a lie. " + CLAIM + ".\n```python\nx\n```\n",
    "fence_closed": "```\nls\nThat is a lie. " + CLAIM + ".\n```\n",
    "no_fence_line_weld": "ls\nThat is a lie. " + CLAIM + ".\n",
    # the root: a 4-token "That is a lie." was under neither bare-denial cut
    "plain_that_is_a_lie": "That is a lie. " + CLAIM + ".",
    # already refused before this fix ("False" is a <= 3-token unit); guard
    "prose_line_weld": "The harbour was busy\nFalse. " + CLAIM + ".\n",
}

CONTROLS = {
    "line_weld_neutral": "```\nls\nThat is documented. " + CLAIM + ".\n```python\nx\n```\n",
}


@pytest.mark.parametrize("name", sorted(ATTACKS))
def test_line_welded_denial_does_not_ground(tmp_path: Path, name: str) -> None:
    report = gate(tmp_path, ATTACKS[name])
    assert report["per_claim"][0]["verdict"] != "GROUNDED", (name, report["per_claim"])
    assert report["gate"] != "PASS"


@pytest.mark.parametrize("name", sorted(CONTROLS))
def test_line_welded_neutral_still_grounds(tmp_path: Path, name: str) -> None:
    report = gate(tmp_path, CONTROLS[name])
    assert report["per_claim"][0]["verdict"] == "GROUNDED", (name, report["per_claim"])
