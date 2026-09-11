"""OI-MOAT-26 — comment stripping must run BEFORE NFKC, and stay there.

The fix is a two-line reorder, which is exactly the kind of change a later
refactor undoes without noticing. These tests pin the PROPERTY, not the line.

The attack it closes (round 7, 2026-09-12): NFKC folds the full-width forms
"＜！－－" and "－－＞" into "<!--" and "-->". With stripping running after
NFKC, an author could manufacture a comment delimiter out of characters that no
Markdown renderer hides, weld a pair into mid-sentence, and delete the part of
their own sentence that reversed it:

    draft   "The appliance ships with ＜！－－at most one, and never
             with－－＞ dual power supplies [S6]."
    judged  "The appliance ships with   dual power supplies [S6]."
    verdict GROUNDED, gate PASS, score 100.0

The gate certified the opposite of the sentence the author wrote and printed the
rewritten sentence back as theirs. CLAUDE.md bars NFKC from content paths
precisely because it silently rewrites authored characters; here that rewrite
was load-bearing for a moat rule.

PROVEN RED: under the old order every `manufactured` case below strips to
"A   B" — the pipeline's own output, enumerated in the session log before the
fix landed. Under the new order they survive as visible text and get scored.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))

from scripts.ground_check import _nfkc, _strip_html_comments  # noqa: E402


def _pipeline(text: str) -> str:
    """The ingestion order as `_iter_raw_sentences` applies it."""
    return _nfkc(_strip_html_comments(text))


MANUFACTURED = [
    pytest.param("A ＜！－－note－－＞ B", id="fullwidth-angle-bang-dash"),
    pytest.param("A <!－－note－－> B", id="fullwidth-dashes-only"),
]

GENUINE = [
    pytest.param("A <!-- note --> B", "A   B", id="ordinary-comment"),
    pytest.param("A <!----> B", "A   B", id="empty-comment"),
    pytest.param("A <!--x--><!--y--> B", "A    B", id="adjacent-comments"),
    pytest.param("A <!-- x <!-- y --> B", "A   B", id="nested-looking-opener"),
    pytest.param("A <!-- ﬁle Ａ --> B", "A   B", id="comment-holding-foldables"),
    pytest.param("A <!-- note B", "A <!-- note B", id="unterminated-opener-survives"),
]


@pytest.mark.parametrize("text", MANUFACTURED)
def test_nfkc_cannot_manufacture_a_comment_delimiter(text: str) -> None:
    """Full-width lookalikes are VISIBLE prose and must survive into scoring."""
    out = _pipeline(text)
    assert "note" in out, (
        f"NFKC manufactured a comment delimiter and deleted reader-visible "
        f"prose: {text!r} -> {out!r}"
    )


@pytest.mark.parametrize("text,expected", GENUINE)
def test_genuine_ascii_comments_still_strip(text: str, expected: str) -> None:
    """D-17 must be intact: the fix must not stop stripping real comments.

    The unterminated-opener row is D-17's own load-bearing restriction — one
    stray "<!--" must NOT silently delete every claim below it.
    """
    assert _pipeline(text) == expected


MIXED_DELIMITERS = [
    pytest.param(
        "A <!-- note －－＞ FABRICATED --> B",
        id="ascii-opener-fullwidth-then-ascii-closer",
    ),
]


@pytest.mark.xfail(
    strict=True,
    reason="OI-MOAT-33 OPEN: the reorder is NOT strictly conservative. With an "
    "ASCII opener, a full-width closer and then a real ASCII closer, the OLD "
    "order stripped to the full-width closer and left 'FABRICATED' scored; the "
    "NEW order strips to the ASCII closer and deletes it from the denominator. "
    "Text leaving scoring points TOWARD PASS. Found by the round-7 solo gate, "
    "against my own claim that D-24 was fail-closed.",
)
@pytest.mark.parametrize("text", MIXED_DELIMITERS)
def test_reorder_does_not_delete_more_than_it_used_to(text: str) -> None:
    """The claim D-24 was justified on, stated honestly and failing.

    D-24 was taken as an agent-authority change because a reorder that only ever
    removes LESS text cannot shrink the denominator, and a change that cannot
    shrink the denominator cannot manufacture a PASS. **That reasoning was wrong,
    and this test is the evidence.** The enumeration behind it covered eight
    comment shapes and no MIXED-delimiter shape, so it confirmed exactly what it
    was built to confirm — the standing trap, in my own test file.

    The change stays in place regardless, because reverting it reinstates
    OI-MOAT-26, which is strictly worse: that one certified the OPPOSITE of the
    author's sentence. But the justification is not fail-closure. It is
    **renderer-faithfulness** — a Markdown renderer treats the ASCII "-->" as
    the closer and really does hide "FABRICATED", so the new order judges what
    the reader sees. That is a sound defence and a DIFFERENT one, and it holds
    only while OI-MOAT-29 is closed, which it is not: a "<!--" sitting in
    visible text (inside a code span, say) is not a comment to any renderer, yet
    still pairs with a real closer here.

    So D-24 is correct on its merits and its recorded basis was wrong, which
    moves it out of settled agent authority and into Sai's ratification queue.
    """
    assert "FABRICATED" in _pipeline(text), (
        f"the new order deleted text the old order scored: {text!r} -> "
        f"{_pipeline(text)!r}"
    )


@pytest.mark.parametrize("text", [p.values[0] for p in MANUFACTURED]
                                 + [p.values[0] for p in GENUINE])
def test_reorder_is_conservative_on_uniform_delimiters(text: str) -> None:
    """Narrowed to what is actually true: uniform-delimiter shapes.

    Was `test_reorder_is_strictly_conservative` and asserted the property over
    all inputs. It never covered a mixed-delimiter shape, so it passed while the
    general claim was false. Kept, narrowed, and renamed to say what it checks.
    """
    old_order = _strip_html_comments(_nfkc(text))
    new_order = _pipeline(text)
    assert len(new_order.replace(" ", "")) >= len(old_order.replace(" ", "")), (
        f"the new order removed MORE text than the old on {text!r}: "
        f"{old_order!r} -> {new_order!r}"
    )
