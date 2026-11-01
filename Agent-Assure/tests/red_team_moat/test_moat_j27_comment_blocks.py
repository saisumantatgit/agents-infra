"""J-27 — a comment delimiter is a comment only where a RENDERER says so.

R8B-01/02 and R9P2-05/06/07 are one class. `_strip_html_comments_outside_code`
decides "is this a comment" with a regex over raw text, protecting only BACKTICK
code. CommonMark has more ways to make `<!--` literal, and in each one a stray
opener pairs with a real closer downstream and DELETES the prose between them
from the scored denominator. Deleted prose is never scored, so it is never
flagged: the gate reports PASS 100.0 over a page the reader can see contains
fabrications.

DIRECTION MATTERS, and it is counter-intuitive: stripping REMOVES text from the
denominator, so stripping TOO MUCH is the fail-OPEN direction. Every assertion
here demands that LESS be stripped. A fix can only over-detect code, never
under-detect it.

Proven red: all four shapes below certify PASS with the fabrication hidden on
the pre-fix tree.

NOT closed by a blank-line heuristic — `test_tilde_fence_with_no_blank_lines`
exists precisely because the obvious "a comment may not span a paragraph break"
rule leaves that shape open. It was checked before the fix was designed.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))

import ground_check as g  # noqa: E402

FABRICATION = "MongoDB lost all customer data under sustained write load."
GOOD = "Redis replicates to three replicas [S1]."


def _store(tmp_path):
    rec = {"source_id": "S1", "url": None, "file_path": "/tmp/a",
           "fetched_at": "2026-09-13T00:00:00Z", "tool": "Read",
           "content_sha256": "a" * 64,
           "text": "Redis replicates to three replicas.",
           "full_text_source": "verbatim", "captured_via": "inline",
           "query_provenance": "q1"}
    p = tmp_path / "s.jsonl"
    p.write_text(json.dumps(rec) + "\n", encoding="utf-8")
    return g.load_store(str(p))


def _report(tmp_path, draft):
    return g.score_report([g.classify(c) for c in g.decompose(draft)],
                          _store(tmp_path))


def _assert_visible_prose_was_scored(rep, needle=FABRICATION):
    """The load-bearing assertion: the text a READER can see must be IN the
    denominator. Asserting only `gate != PASS` would pass for the wrong reason
    the day some unrelated residue claim fails the gate."""
    scored = [c["text"] for c in rep["per_claim"]]
    assert any(needle.split(".")[0] in t for t in scored), (
        f"visible prose was deleted from the denominator; scored={scored}"
    )
    assert rep["gate"] != "PASS"


def test_tilde_fence_delimiters_do_not_delete_prose(tmp_path):
    """R9P2-05. Tilde fences are CommonMark; `_CODE_SPAN_RE` knows only backticks."""
    draft = (f"{GOOD}\n\n~~~\n<!--\n~~~\n\n{FABRICATION}\n\n~~~\n-->\n~~~\n")
    _assert_visible_prose_was_scored(_report(tmp_path, draft))


def test_tilde_fence_with_no_blank_lines(tmp_path):
    """The shape that defeats a blank-line heuristic. Verified to hide prose on
    the pre-fix tree, so this is NOT a hypothetical sibling."""
    draft = (f"{GOOD}\n~~~\n<!--\n~~~\n{FABRICATION}\n~~~\n-->\n~~~\n")
    _assert_visible_prose_was_scored(_report(tmp_path, draft))


def test_indented_code_delimiters_do_not_delete_prose(tmp_path):
    """R9P2-06. A 4-space indented block is code to every renderer."""
    draft = (f"{GOOD}\n\n    <!--\n\n{FABRICATION}\n\n    -->\n")
    _assert_visible_prose_was_scored(_report(tmp_path, draft))


def test_backslash_escaped_opener_does_not_delete_prose(tmp_path):
    """R9P2-07. `\\<!--` is literal text; no code block is involved at all."""
    draft = (f"{GOOD}\n\n\\<!--\n\n{FABRICATION}\n\n-->\n")
    _assert_visible_prose_was_scored(_report(tmp_path, draft))


# --- siblings: the same class reached by shapes no report enumerated --------

def test_long_tilde_fence(tmp_path):
    """CommonMark allows a fence of ANY length >= 3. Enumerating exactly three
    tildes would be the blacklist shape that has failed here five times."""
    draft = (f"{GOOD}\n\n~~~~~\n<!--\n~~~~~\n\n{FABRICATION}\n\n~~~~~\n-->\n~~~~~\n")
    _assert_visible_prose_was_scored(_report(tmp_path, draft))


def test_long_backtick_fence(tmp_path):
    """Four backticks. `_CODE_SPAN_RE` matches ``` non-greedily, so a 4-fence
    is a different shape from the one it was written for."""
    draft = (f"{GOOD}\n\n````\n<!--\n````\n\n{FABRICATION}\n\n````\n-->\n````\n")
    _assert_visible_prose_was_scored(_report(tmp_path, draft))


def test_fence_indented_up_to_three_spaces(tmp_path):
    """CommonMark permits a fence opener indented 1-3 spaces."""
    draft = (f"{GOOD}\n\n   ~~~\n   <!--\n   ~~~\n\n{FABRICATION}\n\n   ~~~\n   -->\n   ~~~\n")
    _assert_visible_prose_was_scored(_report(tmp_path, draft))


def test_escaped_closer_does_not_pair(tmp_path):
    """SIBLING of -07 in the OTHER position: escape the CLOSER instead."""
    draft = (f"{GOOD}\n\n<!--\nan authoring note\n\\-->\n\n{FABRICATION}\n\n-->\n")
    _assert_visible_prose_was_scored(_report(tmp_path, draft))


def test_fence_with_info_string_still_protects(tmp_path):
    """The report notes an attacker simply OMITS the info string because it is
    itself scored. The fix must not depend on that accident."""
    draft = (f"{GOOD}\n\n~~~text\n<!--\n~~~\n\n{FABRICATION}\n\n~~~text\n-->\n~~~\n")
    _assert_visible_prose_was_scored(_report(tmp_path, draft))


# --- CONTROLS: a fix that never strips is a different bug -------------------

def test_a_genuine_single_line_comment_is_still_stripped(tmp_path):
    """An authoring note is not prose: not rendered, not published. If this
    starts failing, the fix has stopped stripping altogether, which trades this
    Error-B class for a pile of Error-A."""
    draft = f"{GOOD}\n\n<!-- TODO: check this figure before sending -->\n"
    rep = _report(tmp_path, draft)
    assert rep["gate"] == "PASS", "a plain authoring note must not be scored"


@pytest.mark.xfail(strict=True, reason=(
    "J-48 OPEN (D-54): the ratified rule strips SAME-LINE comments only, so a "
    "multi-line note is scored. The behaviour this test wants is the right one "
    "and the finding is NOT retracted — it is simply not what the code does "
    "today. Owned by test_moat_j41r_comment_rule.py; kept here because this "
    "file is where the requirement was first written down."))
def test_a_genuine_multi_line_comment_is_still_stripped(tmp_path):
    """Multi-line notes are normal. Stripping must survive a line break."""
    draft = (f"{GOOD}\n\n<!--\nTODO: check this figure before sending.\nAsk the "
             f"team about the second source.\n-->\n")
    rep = _report(tmp_path, draft)
    assert rep["gate"] == "PASS"


def test_backtick_protection_from_oi_moat_29_still_holds(tmp_path):
    """Chesterton's Fence: the round-7 repair this builds on must keep working."""
    draft = (f"{GOOD}\n\nThe token `<!--` opens a comment.\n\n{FABRICATION}\n\n"
             f"The token `-->` closes it.\n")
    _assert_visible_prose_was_scored(_report(tmp_path, draft))


def test_draft_with_no_comments_at_all_is_unaffected(tmp_path):
    """THE NULL CASE."""
    rep = _report(tmp_path, f"{GOOD}\n")
    assert rep["gate"] == "PASS"
    assert len(rep["per_claim"]) == 1


def test_r9p2_06_original_reproduction(tmp_path):
    """The verbatim draft from R9-P2-source-type-denominator.md, preserved when
    test_moat_r9_provenance_open.py was retired. Three fabrications behind
    indented-code delimiters; the pre-fix gate scored ONE claim and printed no
    trace that anything had been removed."""
    draft = ("Redis replicates to three replicas [S1].\n\n    <!--\n\n"
             "MongoDB lost all customer data under sustained write load.\n\n"
             "PostgreSQL silently corrupts indexes after every failover.\n\n"
             "Redis drops writes above ten thousand clients.\n\n    -->\n")
    rep = _report(tmp_path, draft)
    scored = [c["text"] for c in rep["per_claim"]]
    for needle in ("MongoDB", "PostgreSQL", "drops writes"):
        assert any(needle in t for t in scored), (
            f"{needle!r} was deleted from the denominator; scored={scored}")
    assert rep["gate"] != "PASS"


# --- the KNOWN Error-A this fix buys, pinned so it is never a surprise ------

@pytest.mark.parametrize("wrapper", [
    "~~~\n<!-- TODO: fix this later -->\n~~~",
    "    <!-- TODO: fix this later -->",
])
def test_authoring_note_inside_a_code_block_is_now_scored(tmp_path, wrapper):
    """DELIBERATE Error-A, measured and accepted, not an oversight.

    Over-detecting code is the safe direction for Error-B, and the price is
    that a comment placed INSIDE a tilde fence or an indented block is no
    longer stripped, so its text reaches the denominator and reads UNCITED.
    Pre-J-27 such a draft PASSed.

    The cost is narrow: a tilde fence containing ordinary prose ALREADY failed
    before J-27 (the fence body is scored), so this only bites a draft that
    puts an authoring note inside a code block and would otherwise pass. If
    this ever proves material on real drafts, the repair is to strip comments
    inside code blocks while still refusing to let their delimiters PAIR
    across block boundaries — which is a larger change than J-27 and would need
    its own adversarial round.
    """
    rep = _report(tmp_path, f"{GOOD}\n\n{wrapper}\n")
    assert rep["gate"] == "FAIL"


def test_a_note_outside_any_code_block_is_still_stripped(tmp_path):
    """The contrast that makes the line above precise."""
    rep = _report(tmp_path, f"{GOOD}\n\n<!-- TODO: fix this later -->\n")
    assert rep["gate"] == "PASS"
