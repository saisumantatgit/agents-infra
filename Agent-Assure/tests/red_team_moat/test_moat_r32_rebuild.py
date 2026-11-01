"""RED-TEAM-R32 rebuild of D-102 (Sai, 2026-11-01): lines that MAKE NO CLAIM
are not scored, and denial words inside code do not deny. R32 showed the first
attempt also unscored lines that DO make a claim (R32-01..03), masked prose as
code (R32-04), and let code ground what it could not deny (R32-05).

Every REFUSED case below was seen PASS on the first attempt (commits a3846f3 +
ca866f6, cherry-picked); red evidence in reports/RUN-2026-11-01-CHANGES.md."""
from __future__ import annotations

from pathlib import Path

import pytest

from scripts import ground_check as g
from tests.red_team_moat._h_helpers import CLAIM, DRAFT, TAIL, gate

SOURCE = CLAIM + "." + TAIL

# --- draft-side: a line that makes a claim stays scored ---------------------
DRAFT_REFUSED = {
    # R32-01: a leading count is a figure, not a section label
    "h_300_died": "# 300 people died\n\n" + DRAFT,
    "h_40_percent_word": "# 40 percent fraud rate\n\n" + DRAFT,
    "h_per_cent": "# 40 per cent fraud\n\n" + DRAFT,
    "h_12_dead": "## 12 dead in bank riot\n\n" + DRAFT,
    "h_999_fired": "# 999 staff fired\n\n" + DRAFT,
    "h_number_word": "# 1. Twelve banks\n\n" + DRAFT,
    "h_part_then_count": "# Part 1: 300 dead\n\n" + DRAFT,
    # R32-02: a header row is unscored only in a real table, never a list item
    "tbl_record_no_body": "| Record profits | Fraud widespread |\n|---|---|\n\n" + DRAFT,
    "tbl_300_no_body": "| 300 dead | 12 banks |\n|---|---|\n\n" + DRAFT,
    "tbl_300_with_body": "| 300 dead | 12 banks |\n|---|---|\n| a | b |\n\n" + DRAFT,
    "tbl_40_percent_word": "| Fraud rate 40 percent | CEO jailed |\n|---|---|\n| a | b |\n\n" + DRAFT,
    "tbl_one_cell_noleading": "Minister resigned |\n|---|\n\n" + DRAFT,
    "tbl_list_item": "- The minister resigned |\n|---|\n\n" + DRAFT,
    "tbl_list_item_with_body": "- Minister resigned |\n|---|\n| x |\n\n" + DRAFT,
    "tbl_cell_count_mismatch": "| Minister resigned | x |\n|---|\n| y |\n\n" + DRAFT,
    # R32-03: only a code-language fence is unscored
    "fence_prose": "```prose\nThe minister resigned after the audit.\n```\n\n" + DRAFT,
    "fence_text": ("```text\nThe central bank secretly printed 4 trillion dollars in 2019.\n```\n\n"
                   + DRAFT),
    "fence_markdown": "```markdown\nThe minister resigned after the audit.\n```\n\n" + DRAFT,
    "fence_no_label": "```\nThe minister resigned after the audit.\n```\n\n" + DRAFT,
    "fence_tilde": "~~~\nThe minister resigned after the audit.\n~~~\n\n" + DRAFT,
    "fence_wraps_all": "```\nThe minister resigned after the audit.\n" + DRAFT + "```\n",
    "fence_indented3": "   ```\nThe minister resigned after the audit.\n   ```\n\n" + DRAFT,
    "fence_closer_longer": "```\nThe minister resigned after the audit.\n`````\n\n" + DRAFT,
    "fence_unclosed_then_closed": "```\n" + DRAFT + "The minister resigned after the audit.\n```\n",
}


@pytest.mark.parametrize("name", sorted(DRAFT_REFUSED))
def test_r32_claim_shaped_structure_stays_scored(tmp_path: Path, name: str) -> None:
    report = gate(tmp_path, SOURCE, DRAFT_REFUSED[name])
    assert report["gate"] != "PASS", (name, report["per_claim"])


# --- the intended relief survives -------------------------------------------
_PY = "```python\nimport tempfile\nprint(tempfile.gettempdir())\n```\n\n"
DRAFT_EXEMPT = {
    "h_part_1": "# Part 1\n\n" + DRAFT,
    "h_step_2": "## Step 2\n\n" + DRAFT,
    "h_ordinal_paren": "## 2) Setup\n\n" + DRAFT,
    "h_ordinal_dotted": "### 1.2 Setup\n\n" + DRAFT,
    "h_appendix_stage": "# Appendix 3: Stage 2\n\n" + DRAFT,
    "fence_python": _PY + DRAFT,
    "fence_bash_tilde": "~~~bash\nls -la /tmp\n~~~\n\n" + DRAFT,
    "real_table_label_header": "| Bank | Month |\n|---|---|\n| Northbank | May |\n\n" + DRAFT,
}


@pytest.mark.parametrize("name", sorted(DRAFT_EXEMPT))
def test_r32_label_structure_still_not_scored(tmp_path: Path, name: str) -> None:
    claims = [g.classify(c) for c in g.decompose(DRAFT_EXEMPT[name])]
    scored = [c.text for c in claims if c.kind is not g.ClaimKind.NON_CLAIM]
    if name == "real_table_label_header":
        # the header and separator leave; the body row is still scored
        assert scored == ["| Northbank | May |", CLAIM + " [S1]."], scored
        return
    assert scored == [CLAIM + " [S1]."], (name, scored)
    assert gate(tmp_path, SOURCE, DRAFT_EXEMPT[name])["gate"] == "PASS"


# --- source-side: a prose denial is never read as code (R32-04), and code
# --- cannot ground what it cannot deny (R32-05) ------------------------------
SOURCE_REFUSED = {
    "stray_bt_before": "The flag ` is odd. " + CLAIM + ". That is false. Use `x`.",
    "fullwidth_bt": "Use ｀x. " + CLAIM + ". That is false. y｀ ok.",
    "unlabelled_fence_denial": "```\n" + CLAIM + ". That is false.\n```\ncode\n",
    "unlabelled_fence_swallow": "```\nls\n" + CLAIM + ".\nThat is false.\n```\n",
    "unclosed_python_fence": "```python\n" + CLAIM + ". That is false.\n",
    "python_fence_claim_and_denial": "```python\n" + CLAIM + ". That is false.\n```\n",
    "python_fence_claim_only": "```python\n" + CLAIM + ".\n```\n" + TAIL,
    "inline_span_claim": "`" + CLAIM + "`" + TAIL,
}


@pytest.mark.parametrize("name", sorted(SOURCE_REFUSED))
def test_r32_source_code_neither_hides_a_denial_nor_grounds(tmp_path: Path, name: str) -> None:
    report = gate(tmp_path, SOURCE_REFUSED[name])
    assert report["per_claim"][0]["verdict"] != "GROUNDED", (name, report["per_claim"])
    assert report["gate"] != "PASS"


def test_r32_prose_claim_beside_python_fence_still_grounds(tmp_path: Path) -> None:
    """The relief D-102 row 2 exists for: code next to a prose claim, carrying
    a denial word, neither denies nor blocks it."""
    src = CLAIM + ".\n\n```python\nx = None if not ok else 1\n```\n" + TAIL
    assert gate(tmp_path, src)["per_claim"][0]["verdict"] == "GROUNDED"
