"""D-102 row 2 (Sai, 2026-11-01): H1 denial words count only in PROSE, not
inside inline code spans or closed fenced code. `delete=False` next to a
claim is not a denial of it (R31-02's python_tempfile.md case).

PASS cases were seen refused on the pre-change code (red evidence in
reports/RUN-2026-11-01-CHANGES.md)."""
from __future__ import annotations

from pathlib import Path

import pytest

from tests.red_team_moat._h_helpers import CLAIM, TAIL, gate

CODE_ONLY = {
    "inline_delete_false": CLAIM + ". It was opened with `delete=False` so that it stays." + TAIL,
    "inline_not_none": CLAIM + ". It checks `x is not None` before that step." + TAIL,
    "fenced_delete_false": (CLAIM + ".\n\n```python\nwith tempfile.NamedTemporaryFile(delete=False) as it:\n"
                            "    pass\n```\n" + TAIL),
}


@pytest.mark.parametrize("name", sorted(CODE_ONLY))
def test_d102_denial_word_inside_code_does_not_deny(tmp_path: Path, name: str) -> None:
    report = gate(tmp_path, CODE_ONLY[name])
    assert report["per_claim"][0]["verdict"] == "GROUNDED", (name, report["per_claim"])


PROSE_DENIALS = {
    "prose_denial_before_code": CLAIM + ". That is false, see `audit.log`." + TAIL,
    "prose_denial_after_code": CLAIM + ". See `audit.log`: that is false." + TAIL,
    "prose_bare_denial_then_fence": CLAIM + ". Untrue.\n\n```\nprint(1)\n```\n" + TAIL,
    "prose_denial_same_sentence_as_code": ("It is not the case, says `report.txt`, that "
                                           + CLAIM[0].lower() + CLAIM[1:] + "." + TAIL),
    "unclosed_fence_is_prose": CLAIM + ".\n```\nNone of that happened.\n" + TAIL,
    "stray_backtick_not_a_span": CLAIM + ". That is ` false." + TAIL,
}


@pytest.mark.parametrize("name", sorted(PROSE_DENIALS))
def test_d102_prose_denial_next_to_code_still_denies(tmp_path: Path, name: str) -> None:
    report = gate(tmp_path, PROSE_DENIALS[name])
    assert report["per_claim"][0]["verdict"] != "GROUNDED", (name, report["per_claim"])
    assert report["gate"] != "PASS"


def test_d102_ceiling_denial_hidden_in_backticks_grounds(tmp_path: Path) -> None:
    """ACCEPTED COST, recorded (Sai, D-102 row 2): a denial the source author
    wraps in backticks is read as code, so it no longer denies the claim next
    to it. Pinned so the cost is visible, not discovered."""
    report = gate(tmp_path, CLAIM + ". `That is false.`" + TAIL)
    assert report["per_claim"][0]["verdict"] == "GROUNDED", report["per_claim"]
