"""Round 11 — J-28B REFUTED. Tripwires for the residue (J-41).

`_spans_one_block` measures only two things: a blank line, and blockquote depth.
Every OTHER CommonMark paragraph-interrupting block start is invisible to it —
ATX headings, thematic breaks, list markers, fence openers, setext underlines,
other HTML blocks. A mid-paragraph literal `<!--` therefore pairs with a `-->`
across that boundary and deletes the reader-visible prose between them.

Each of these was verified to hide the fabrication on the tree that shipped
J-28B. They are recorded, NOT accepted (Alpha #7).

READ THIS BEFORE FIXING THEM ONE BY ONE. This class has now lost rounds 7, 8, 9,
10 and 11 across three implementations. Adding the missing block starts here
would be the fourth, and the fourth blacklist. The registered recommendation
(J-41) is to DELETE the feature — stop stripping HTML comments — which removes
the class permanently. That call is Sai's because it moves the Error-A/Error-B
trade-off.

If J-41 is taken, this file and most of the stripper's tests go with it. That is
the intended outcome, not a loss.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))

import ground_check as g  # noqa: E402

GOOD = "Redis replicates to three replicas [S1]."
FAB = "MongoDB lost all customer data under sustained write load."


def _report(tmp_path, draft):
    rec = {"source_id": "S1", "url": None, "file_path": "/tmp/a",
           "fetched_at": "2026-09-13T00:00:00Z", "tool": "Read",
           "content_sha256": "a" * 64,
           "text": "Redis replicates to three replicas.",
           "full_text_source": "verbatim", "captured_via": "inline",
           "query_provenance": "q1"}
    p = tmp_path / "s.jsonl"
    p.write_text(json.dumps(rec) + "\n", encoding="utf-8")
    return g.score_report([g.classify(c) for c in g.decompose(draft)],
                          g.load_store(str(p)))


# A fence opener is DELIBERATELY ABSENT from this list: in this draft shape the
# fence makes the following text code, so `_protected` catches it and the
# fabrication is scored. It reproduces in other shapes (see the round-11 report)
# but not here, and a tripwire that passes must not be filed as one.
# (the block start that interrupts the paragraph)
BLOCK_STARTS = [
    pytest.param("# A Heading", id="01a-atx-heading"),
    pytest.param("***", id="01b-thematic-break"),
    pytest.param("- item", id="01c-list-marker"),
    pytest.param("<div>", id="01f-html-block-type-6"),
]


@pytest.mark.parametrize("interrupter", BLOCK_STARTS)
@pytest.mark.xfail(strict=True, reason=(
    "J-41 OPEN (round 11): _spans_one_block measures only a blank line and "
    "blockquote depth, so every other paragraph-interrupting block start is "
    "invisible. A mid-paragraph literal <!-- pairs across the boundary and "
    "deletes the visible fabrication from the scored denominator."))
def test_block_boundary_must_prevent_comment_pairing(tmp_path, interrupter):
    draft = f"{GOOD}\n\nSee the note <!-- here.\n{interrupter}\n{FAB}\n--> end.\n"
    rep = _report(tmp_path, draft)
    scored = [c["text"] for c in rep["per_claim"]]
    assert any("MongoDB" in t for t in scored), (
        f"fabrication deleted from the denominator; scored={scored}")


def test_control_same_shape_without_an_interrupter_really_is_one_comment(tmp_path):
    """Keeps the tripwires honest: with NO block boundary between them, the
    delimiters ARE one comment and stripping is correct. The finding is the
    BOUNDARY being invisible, not the pairing itself.

    Asserted on the DENOMINATOR, not on the gate: the leftover sentence around
    the comment is itself an uncited claim, so this draft fails either way, and
    a `gate == PASS` assertion here would have passed or failed for a reason
    unrelated to what it claims to test."""
    draft = f"{GOOD}\n\nSee the note <!-- {FAB} --> end.\n"
    rep = _report(tmp_path, draft)
    scored = [c["text"] for c in rep["per_claim"]]
    assert not any("MongoDB" in t for t in scored), (
        f"a genuine same-block comment should still be stripped; scored={scored}")
