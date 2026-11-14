"""RED-TEAM-R42 B1/B2: sources origin/main refuses (FAIL 0.0) that bce1ac7
certified (PASS 100.0). R40 widened `_has_strong_denial` in place, so
`_heading_line_denies` stopped clearing headings main clears, `_strong_tokens`
kept them in the welded sentence, and two of main's tests got weaker on the
longer text: (B1) the 12-token cap on the far forward-pointing rule, (B2) the
code-value window before a predicative "is false". Event-negation headings
("## The launch never took place", R40b) opened the same seam.

Every case is refused by origin/main 746f337 and certified by bce1ac7
(proven red against bce1ac7). Fixed by computing main's denial verdict with
main's rules exactly and OR-ing the R40 reading onto it
(`_match_denied`, reports/R42-FIX.md)."""
from __future__ import annotations

from pathlib import Path

import pytest

from tests.red_team_moat._h_helpers import gate

CLAIM = "Revenue rose to 90000 dollars after the audit"
DRAFT = CLAIM + " [S1].\n"

SOURCES = {
    # B1: the cleared-on-main heading stays in the welded sentence, which
    # then exceeds the 12-token cap of the far forward-pointing rule.
    "b1a_fabricate_faq": ("## Facts and costs we fabricate\nWe do not believe the next short part.\n"
                          "# Notes\nStaff left. Records were filed. " + CLAIM + ". The board met."),
    "b1b_fabricating_faq": ("## Fact vs fabricating\nNone of the figures in the next section are accurate.\n"
                            "## Results\nStaff left. Records were filed. " + CLAIM + "."),
    "b1c_truth_or_fabricating": ("## Truth or fabricating\nNone of the numbers in the next section are accurate.\n"
                                 "## Results\nThe audit took several months. Staff left. " + CLAIM + "."),
    # B2: heading words enter the three-word code-value window before "is
    # false", cancelling main's predicative reading.
    "b2a_flags_is_false": "Staff left. " + CLAIM + ".\n## Facts and flags we fabricate\nIs false.",
    "b2b_flag_values_is_fake": "Staff left. " + CLAIM + ".\n## Facts and flag values we fabricate\nIs fake.",
    # R40b event-negation headings (clause-final, so strong on the branch,
    # cleared on main) opening B1.
    "event_launch_never_took_place": ("## The launch never took place\nWe do not believe the next short part.\n"
                                      "# Notes\nStaff left. Records were filed. " + CLAIM + "."),
    "event_why_merger_did_not_occur": ("## Why the merger did not occur\nWe could not confirm the next few lines.\n"
                                       "## Results\nThe board met twice. Officials declined to comment. "
                                       "Records were filed. " + CLAIM + "."),
    "event_why_launch_never_took_place": ("## Why the launch never took place\nNone of the figures in the next"
                                          " section are accurate.\n## Results\nRecords were filed. The board met"
                                          " twice. Officials declined to comment. " + CLAIM + "."),
}


@pytest.mark.parametrize("name", sorted(SOURCES))
def test_r42_heading_seam_is_refused(tmp_path: Path, name: str) -> None:
    report = gate(tmp_path, SOURCES[name], draft=DRAFT)
    assert report["per_claim"][0]["verdict"] != "GROUNDED", (name, report["per_claim"])
    assert report["gate"] != "PASS", (name, report["gate"], report.get("score"))
