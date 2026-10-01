"""J-41r — the comment rule that ended a five-round sequence.

HISTORY, because it is the whole justification. The comment stripper lost rounds
7, 8, 9, 10 AND 11 across three designs:

  1. backtick-only code protection          -> lost r9  (tilde fences, indented code)
  2. `_code_line_spans` region scanner      -> lost r10 (blockquote prefix, space+tab,
                                                        inline opener, code span over \\n)
  3. `_spans_one_block` block-structure rule -> lost r11 (heading, thematic break,
                                                        list marker, <div>, list container)

Each was a BLACKLIST — over "ways to be code", then over "ways to end a block" —
and the attacker writes the document, so each lost the next round.

THE RULE NOW. Strip a comment only when it is unambiguous:

  * SAME LINE: opener and closer on one line; or
  * BLOCK: opener is the first non-whitespace on its line at <=3 COLUMNS of
    indent (tabs to 4, as CommonMark measures), closer is the last non-whitespace
    on its line, and NO blank line sits between them.

...and in both cases: not backslash-escaped, and neither delimiter inside code.

WHY THIS IS NOT DESIGN 3 AGAIN. Design 3's hole was that a MID-LINE opener could
pair with a closer in another block, and every round-11 finding used exactly
that ("See <!-- here." followed by a heading / break / list marker / <div>).
Requiring the opener to START a line kills all of them at once — CommonMark's
HTML-block rule only fires at line start, and when it does fire, everything
through the closing line genuinely IS inside the comment. The no-blank-line
condition then blocks R11A-02, where a container-scoped block is left
unterminated and a later `-->` lives in a different block.

So the rule is renderer-faithful BY CONSTRUCTION rather than by enumeration,
which is why there is nothing left to add to it.

DIRECTION. Stripping REMOVES text from the scored denominator, so stripping too
much is the FAIL-OPEN direction. Every condition above makes the stripper do
LESS than its predecessor on the attack shapes, and the one place it does MORE
(multi-line block comments) is the case CommonMark says really is a comment.
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


# Every shape any round has used to delete reader-visible prose. Each is
# asserted on the DENOMINATOR, not on the gate string: a draft can fail for an
# unrelated reason while the hidden prose is still missing, which is how three
# round-10 findings stayed invisible until that was checked.
ATTACKS = {
    "r9p2-05-tilde-fence":
        f"{GOOD}\n\n~~~\n<!--\n~~~\n\n{FAB}\n\n~~~\n-->\n~~~\n",
    "r9p2-06-indented-code":
        f"{GOOD}\n\n    <!--\n\n{FAB}\n\n    -->\n",
    "r9p2-07-backslash-escape":
        f"{GOOD}\n\n\\<!--\n\n{FAB}\n\n-->\n",
    "r10a-inline-mid-paragraph":
        f"Note <!-- here.\n\n{FAB}\n\n{GOOD}\n\n--> done.\n",
    "r10a-blockquote-tilde-fence":
        f"{GOOD}\n\n> ~~~\n> <!--\n> ~~~\n\n{FAB}\n\n> ~~~\n> -->\n> ~~~\n",
    "r10a-blockquote-indented":
        f"{GOOD}\n\n>     <!--\n\n{FAB}\n\n>     -->\n",
    "r10a-space-plus-tab-indent":
        f"{GOOD}\n\n \t<!--\n\n{FAB}\n\n \t-->\n",
    "r10a-long-tilde-fence":
        f"{GOOD}\n\n~~~~~\n<!--\n~~~~~\n\n{FAB}\n\n~~~~~\n-->\n~~~~~\n",
    "r10a-code-span-across-newline":
        f"{GOOD}\n\n`x\ny <!--`\n\n{FAB}\n\n`-->`\n",
    "r10a-fence-info-string":
        f"{GOOD}\n\n~~~text\n<!--\n~~~\n\n{FAB}\n\n~~~text\n-->\n~~~\n",
    "r11a-01a-atx-heading":
        f"{GOOD}\n\nSee <!-- here.\n# Heading\n{FAB}\n--> end.\n",
    "r11a-01b-thematic-break":
        f"{GOOD}\n\nSee <!-- here.\n***\n{FAB}\n--> end.\n",
    "r11a-01c-list-marker":
        f"{GOOD}\n\nSee <!-- here.\n- item\n{FAB}\n--> end.\n",
    "r11a-01f-html-block-div":
        f"{GOOD}\n\nSee <!-- here.\n<div>\n{FAB}\n--> end.\n",
    "r11a-02-list-container":
        f"{GOOD}\n\n- item\n  <!--\n\n{FAB}\n\n-->\n",
    "j41r-same-line-escaped":
        f"{GOOD}\n\nThe system is safe \\<!-- {FAB} --> really.\n",
    "j41r-block-opener-blank-line":
        f"{GOOD}\n\n<!--\nnote\n\n{FAB}\n\n-->\n",
}


@pytest.mark.parametrize("draft", list(ATTACKS.values()), ids=list(ATTACKS))
def test_no_known_shape_deletes_visible_prose(tmp_path, draft):
    rep = _report(tmp_path, draft)
    scored = [c["text"] for c in rep["per_claim"]]
    assert any("MongoDB" in t for t in scored), (
        f"fabrication deleted from the denominator; scored={scored}")


# --- honest notes: a stripper that never strips is a different bug -----------

@pytest.mark.parametrize("note", [
    "<!-- TODO: check this figure before sending -->",
    "<!-- DRAFT v2 -->",
    "<!-- Reviewer: this came from the Q3 deck -->",
    "<!--\nTODO: check this figure.\nAsk the team.\n-->",
    "   <!--\n   an indented note, 3 columns\n   -->",
    "<!--\nline one\nline two\nline three\n-->",
])
def test_a_genuine_authoring_note_is_still_stripped(tmp_path, note):
    """OI-DEC-03 is an ACCEPTED finding with a real fixture from this project's
    own working drafts: a multi-line note was decomposed into scored FACTUAL
    claims, and 'a gate that flags a writer's own TODO notes as ungrounded
    claims is not measuring the document'. Dropping multi-line support would
    have re-opened it, which is why the block branch exists."""
    rep = _report(tmp_path, f"{GOOD}\n\n{note}\n")
    assert rep["gate"] == "PASS", f"note was scored: {[c['text'] for c in rep['per_claim']]}"


def test_inline_same_line_note_is_stripped(tmp_path):
    rep = _report(tmp_path, f"{GOOD} <!-- verify -->\n")
    assert rep["gate"] == "PASS"


# --- the remaining cost, pinned so it is never a surprise -------------------

def test_multi_PARAGRAPH_note_is_now_scored(tmp_path):
    """THE ONE COST, deliberate. A blank line inside a comment means the
    delimiters may sit in different blocks, which is precisely the condition
    every attack needed. Refusing to strip across it is the fail-closed choice,
    and it is the narrowest version of this cost any of the four designs has had
    (design 3 failed EVERY multi-line note; this fails only ones with a blank
    line in them)."""
    rep = _report(tmp_path, f"{GOOD}\n\n<!--\nnote one.\n\nnote two.\n-->\n")
    assert rep["gate"] == "FAIL"


def test_indent_columns_measures_tabs_as_commonmark_does():
    """Unit-level: ' \\t' is FOUR columns, which is why it is code. Round 10's
    R10A-03 was exactly this off-by-a-tab."""
    assert g._indent_columns(" \t") == 4
    assert g._indent_columns("   ") == 3
    assert g._indent_columns("\t") == 4
    assert g._indent_columns("") == 0


def test_draft_with_no_comments_is_unaffected(tmp_path):
    """THE NULL CASE."""
    rep = _report(tmp_path, f"{GOOD}\n")
    assert rep["gate"] == "PASS"
    assert len(rep["per_claim"]) == 1
