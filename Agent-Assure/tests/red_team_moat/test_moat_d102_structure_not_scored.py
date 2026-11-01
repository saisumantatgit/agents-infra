"""D-102 row 1 (Sai, 2026-11-01): headings, fenced-code lines and table
header/separator rows are not scored as claims. PASS-widening, so every exempt
shape has a smuggling guard: a structural-looking line that carries a citation
marker, a claim-shaped figure or a verb-medial assertion is still scored.

EXEMPT cases were seen non-PASS on the pre-change code (red evidence in
reports/RUN-2026-11-01-CHANGES.md)."""
from __future__ import annotations

from pathlib import Path

import pytest

from scripts import ground_check as g
from tests.red_team_moat._h_helpers import CLAIM, DRAFT, TAIL, gate

SOURCE = CLAIM + "." + TAIL
_CODE = ("```python\nimport tempfile\nwith tempfile.TemporaryDirectory() as d:\n"
         "    print(d)\n```\n\n")

EXEMPT = {
    "heading_section_number": "# Part 1\n\n" + DRAFT,
    "heading_plain_and_fence": "# Results\n\n" + _CODE + DRAFT,
    "fence_with_info_string": _CODE + DRAFT,
    "subheading_step": "## Step 2\n\n" + DRAFT,
}


@pytest.mark.parametrize("name", sorted(EXEMPT))
def test_d102_structure_alone_does_not_block_pass(tmp_path: Path, name: str) -> None:
    report = gate(tmp_path, SOURCE, EXEMPT[name])
    assert report["gate"] == "PASS", (name, report["per_claim"])


SMUGGLE = {
    # a real sentence under a heading still needs a citation
    "uncited_sentence_under_heading": "# Results\n\nThe minister resigned after the audit.\n\n" + DRAFT,
    # a heading that asserts (verb-medial) or carries a claim-shaped figure
    "heading_found_40pct": "# The audit found 40% fraud\n\n" + DRAFT,
    "heading_bare_percent": "# 40% fraud\n\n" + DRAFT,
    "heading_money": "# $4 million in losses\n\n" + DRAFT,
    "heading_year": "# Fraud in 2019\n\n" + DRAFT,
    "heading_verb_medial": "### Redis silently drops writes above ten thousand clients\n\n" + DRAFT,
    # a heading carrying a citation marker is scored (and here is ungrounded)
    "heading_cited_fabrication": "# The bank was rescued by the state [S1]\n\n" + DRAFT,
    "heading_fullwidth_citation": "# The bank was rescued by the state \uff3bS1\uff3d\n\n" + DRAFT,
    # code fence: a cited line inside is scored; an unclosed fence is not code
    "fence_cited_fabrication": "```\nThe bank was rescued by the state [S1].\n```\n\n" + DRAFT,
    "fence_unclosed": DRAFT + "\n```\nThe minister resigned after the audit.\n",
    "fence_info_is_prose": "```The minister resigned after the audit\n```\n\n" + DRAFT,
    # table header rows that assert or carry a figure are scored
    "table_header_figure": "| 40% of loans failed | Year |\n|---|---|\n\n" + DRAFT,
    "table_header_asserts": "| Redis loses acknowledged writes | Yes |\n|---|---|\n\n" + DRAFT,
    "table_header_cited": "| The bank was rescued [S1] | Yes |\n|---|---|\n\n" + DRAFT,
    # R32-02: header + separator with no body row is not a real table
    "table_header_without_body": "| Bank | Month |\n|---|---|\n\n" + DRAFT,
    "fake_separator_with_prose": "|---| The minister resigned after the audit |\n\n" + DRAFT,
    # a body row of a table is still scored
    "table_body_row_uncited": "| Bank | Month |\n|---|---|\n| Northbank | collapsed in May |\n\n" + DRAFT,
}


@pytest.mark.parametrize("name", sorted(SMUGGLE))
def test_d102_structure_cannot_smuggle_a_claim(tmp_path: Path, name: str) -> None:
    report = gate(tmp_path, SOURCE, SMUGGLE[name])
    assert report["gate"] != "PASS", (name, report["per_claim"])


def test_d102_exempt_lines_leave_no_segment() -> None:
    claims = [g.classify(c) for c in g.decompose(
        "# Part 1\n\n" + _CODE + "| A | B |\n|---|---|\n| x | y |\n\n" + DRAFT)]
    scored = [c.text for c in claims if c.kind is not g.ClaimKind.NON_CLAIM]
    assert scored == ["| x | y |", CLAIM + " [S1]."], [(c.kind, c.text) for c in claims]
    # fence and table header/separator leave no segment at all; the table body
    # row is still scored; the heading stays a visible NON_CLAIM row
    assert [c.text for c in claims] == ["# Part 1", "| x | y |", CLAIM + " [S1]."]


def test_d102_residue_plural_heading_still_scored(tmp_path: Path) -> None:
    """Recorded residue, not a goal: RT3-02's verb-medial heading rule cannot
    tell the plural "files" from the verb "drops", so "# Temporary files,
    part 1" is still scored UNCITED (Error-A). Kept deliberately: loosening it
    reopens "### Redis silently drops writes ..." (RT3-02 Error-B)."""
    report = gate(tmp_path, SOURCE, "# Temporary files, part 1\n\n" + DRAFT)
    assert report["gate"] != "PASS", report["per_claim"]


def test_d102_unlabelled_fence_prose_is_scored(tmp_path: Path) -> None:
    """R32-03: a fence with no code-language label is not code; the prose in
    it is scored (here UNCITED), so it blocks PASS."""
    draft = "```\nThe minister resigned after the audit.\n```\n\n" + DRAFT
    report = gate(tmp_path, SOURCE, draft)
    assert report["gate"] != "PASS", report["per_claim"]


def test_d102_ceiling_uncited_prose_inside_code_labelled_fence_is_not_scored(tmp_path: Path) -> None:
    """Recorded CEILING (see `_blank_structural_lines`): uncited prose typed
    inside a CLOSED fence labelled with a code language is not scored. It can
    never be GROUNDED (it carries no citation), and any line with a
    citation-shaped bracket inside a fence IS scored (fence_cited_fabrication)."""
    draft = "```python\nThe minister resigned after the audit.\n```\n\n" + DRAFT
    report = gate(tmp_path, SOURCE, draft)
    assert report["gate"] == "PASS", report["per_claim"]
    assert all("minister" not in c["text"] for c in report["per_claim"])
