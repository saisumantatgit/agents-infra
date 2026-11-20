"""R40: RED-TEAM-R37 hole shapes R40 leaves OPEN, each named in a CEILING:
comment in scripts/ground_check.py and in reports/R40-FIXES.md with the reason
no fix was safe against honest text. Strict xfails: each goes RED (XPASS) the
day a change refuses it, so the register cannot silently go stale."""
from __future__ import annotations

from pathlib import Path

import pytest

from tests.red_team_moat._h_helpers import CLAIM, TAIL, gate

S = CLAIM + "." + TAIL

OPEN_SOURCES = {
    # H9: a denial in an EARLIER paragraph (no heading, no scope sentence)
    "h9_previous_paragraph": "None of this is true. Use z.\n\nOk then. Fine.\n\n" + S,
    "h9_blockquote_paragraph": "> None of this is true.\n\nStaff left. Records were filed.\n\n" + S,
    "h9_label_sentence_paragraph": "Rumours we investigated and found to be false.\n\nPeople talked. Some wrote. Others posted.\n\n" + S,
    # R38 referent test (R37 H2/H3 wording): a falsity statement three
    # sentences back whose subject neither points (this, it, the story) nor
    # shares a stem with the claim grounds by design (R38 trade)
    "h2_trumped_up_unrelated_subject": "The charges were trumped up. Staff left. Records were filed. " + S,
    "h3_fabricating_unrelated_subject": "The tabloid is fabricating again. Staff left. Records were filed. " + S,
    # H10 (plain-line denier): a short plain line still ends a NON-markdown denial line's scope
    "h10_plain_label_then_short_line": "Myths about the bank\n\nPeople talked. Some wrote. Others posted.\n\nMore\n\n" + S,
    # H11: "Inventions" is a label word in honest history headings
    "h11_inventions_heading": "## Inventions of the press\n\nPeople talked.\n\n" + S,
    # H12: a denial label that runs on into prose on the same line
    "h12_label_runs_on": "Rumours we found to be false and the people who spread them. People talked. Some wrote. Others posted.\n\n" + S,
}

OPEN_HEADINGS = [
    "# Bank Folds",       # E2-lite closes this when folds is novel
    pytest.param("# Stock Drops", marks=pytest.mark.xfail(strict=True, reason="R40 ceiling")),
    pytest.param("# Bank Defaults", marks=pytest.mark.xfail(strict=True, reason="R40 ceiling")),
    pytest.param("# CEO Out", marks=pytest.mark.xfail(strict=True, reason="R40 ceiling")),
    "# CEO Lies",         # E2-lite closes this when lies is novel
    "## Revenue Doubling",  # E2-lite closes this when doubling is novel
]

HEAD_SOURCE = CLAIM + "."
HEAD_BODY = CLAIM + " [S1].\n"


@pytest.mark.xfail(strict=True, reason="R40 CEILING: open on main ef3ae1f and after R40")
@pytest.mark.parametrize("name", sorted(OPEN_SOURCES))
def test_r40_open_source_shape_is_refused(tmp_path: Path, name: str) -> None:
    report = gate(tmp_path, OPEN_SOURCES[name])
    assert report["gate"] != "PASS", (name, report["gate"])


@pytest.mark.parametrize("heading", OPEN_HEADINGS)
def test_r40_open_heading_shape_is_scored(tmp_path: Path, heading: str) -> None:
    report = gate(tmp_path, HEAD_SOURCE, heading + "\n\n" + HEAD_BODY)
    assert report["per_claim"][0]["kind"] != "NON_CLAIM", (heading, report["per_claim"][0])
