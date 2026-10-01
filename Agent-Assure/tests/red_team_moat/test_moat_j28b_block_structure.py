"""J-28B — round 10 adversary A's five findings, and the structural rule.

J-27's code-region scanner was a BLACKLIST after all. Every one of round 10's
findings was a NEW WAY TO BE CODE that the scanner had not enumerated: a `>`
blockquote marker in front of a fence, a space-plus-tab indent worth 4 columns,
an inline opener with no code region at all, a code span crossing a newline.
Extending the scanner a fifth time would have been the sixth instance of this
repo's recorded failure mode. The adversary said so explicitly.

The rule that replaces it asks a STRUCTURAL question instead: does this opener
genuinely OPEN AN HTML BLOCK? CommonMark HTML-block type 2 says a `<!--`
beginning a line with at most 3 spaces of indent does; anything else is literal
text, and literal text can only be a comment within its OWN BLOCK.

    strip  <=>  (opener opens an HTML block)  OR
                (opener and closer in the same block: no blank line,
                 no change of blockquote depth)

That keys on document structure, not on a surface character the author picks —
the property this project's own law demands.

All five shapes below were verified to hide a fabrication BEFORE this rule; 3 of
them certified a clean PASS 100.0 with an empty retained appendix.

NOT CLAIMED CLOSED. This rule has not itself faced an adversary. Round 11 owes
it one, and until then no closure claim should be made on its behalf — the last
two such claims in this file's history were both refuted within the hour.
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


def _assert_fabrication_reached_the_denominator(rep):
    """The load-bearing assertion. `gate != PASS` alone is NOT enough: a draft
    can fail for an unrelated reason while the hidden prose is still missing —
    which is how three of these shapes were scored as Error-B in the first
    place."""
    scored = [c["text"] for c in rep["per_claim"]]
    assert any("MongoDB" in t for t in scored), (
        f"fabrication was deleted from the denominator; scored={scored}")


# --- the five findings ------------------------------------------------------

def test_r10a_01_inline_opener_no_code_region(tmp_path):
    """Mid-paragraph `<!--` is literal in commonmark.py AND python-markdown.
    It pairs with a `-->` two paragraphs later. No code region is involved at
    all, so J-27's entire scanner was bypassed."""
    draft = f"Note the marker <!-- inline here.\n\n{FAB}\n\n{GOOD}\n\n--> done.\n"
    _assert_fabrication_reached_the_denominator(_report(tmp_path, draft))


def test_r10a_02a_blockquote_tilde_fence(tmp_path):
    """`_FENCE_RE` anchors at `^`, so a `>` marker hides the fence from it."""
    draft = (f"{GOOD}\n\n> ~~~\n> <!--\n> ~~~\n\n{FAB}\n\n> ~~~\n> -->\n> ~~~\n")
    _assert_fabrication_reached_the_denominator(_report(tmp_path, draft))


def test_r10a_02b_blockquote_indented_code(tmp_path):
    """Same anchoring gap via indented code inside a blockquote."""
    draft = f"{GOOD}\n\n>     <!--\n\n{FAB}\n\n>     -->\n"
    _assert_fabrication_reached_the_denominator(_report(tmp_path, draft))


def test_r10a_03_space_plus_tab_indent(tmp_path):
    """CommonMark measures indent in COLUMNS after 4-column tab expansion, so
    " \\t" is an indented code block. It matched neither `^ {4,}` nor `^\\t`."""
    draft = f"{GOOD}\n\n \t<!--\n\n{FAB}\n\n \t-->\n"
    _assert_fabrication_reached_the_denominator(_report(tmp_path, draft))


def test_r10a_05_code_span_across_a_newline(tmp_path):
    """`_CODE_SPAN_RE`'s `` `[^`\\n]*` `` forbids newlines; CommonMark code
    spans may cross a line ending."""
    draft = f"{GOOD}\n\n`x\ny <!--`\n\n{FAB}\n\n`-->`\n"
    _assert_fabrication_reached_the_denominator(_report(tmp_path, draft))


# --- controls: the rule must not have stopped stripping altogether ----------

@pytest.mark.parametrize("note,label", [
    ("<!-- TODO: check this figure -->", "single line"),
    ("<!--\nTODO: check this figure.\nAsk the team.\n-->", "multi line"),
    ("<!--\nTODO: check this figure.\n\nAnd this one.\n-->", "multi PARAGRAPH"),
])
def test_a_genuine_html_block_comment_is_still_stripped(tmp_path, note, label):
    """A `<!--` at line start really DOES open a CommonMark HTML block, which
    runs to its `-->` however many blank lines it spans. Stripping across them
    is renderer-faithful, which is why the multi-paragraph case must still
    strip — a blank-line rule ALONE would wrongly score an honest note."""
    rep = _report(tmp_path, f"{GOOD}\n\n{note}\n")
    assert rep["gate"] == "PASS", f"{label} note was scored"


def test_the_original_r9p2_attacks_remain_closed(tmp_path):
    """Chesterton's Fence: J-27's own shapes must not have reopened."""
    for draft in (
        f"{GOOD}\n\n~~~\n<!--\n~~~\n\n{FAB}\n\n~~~\n-->\n~~~\n",
        f"{GOOD}\n\n    <!--\n\n{FAB}\n\n    -->\n",
        f"{GOOD}\n\n\\<!--\n\n{FAB}\n\n-->\n",
    ):
        _assert_fabrication_reached_the_denominator(_report(tmp_path, draft))


def test_draft_with_no_comments_is_unaffected(tmp_path):
    """THE NULL CASE."""
    rep = _report(tmp_path, f"{GOOD}\n")
    assert rep["gate"] == "PASS"
    assert len(rep["per_claim"]) == 1
