"""Round 8, lane B — the preprocessing chain
`_nfkc(_break_after_headers(_strip_html_comments_outside_code(text)))`.

R8B-04 (ERROR-A: a genuine authoring TODO containing a backtick survives
stripping and gets a false-alarm UNCITED) is deliberately NOT tripwired here —
it is recoverable, it is the safe direction (a false alarm, not a wrongful
PASS), and the task scope for this file is Error-B / denominator-escape only.

Every draft/store pair is copied verbatim from
docs/plans/reports/R8-B-preprocessing.md.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
GROUND_CHECK = str(REPO_ROOT / "scripts" / "ground_check.py")

STORE_RECORD = {
    "source_id": "S1", "url": "https://example.invalid/db-notes", "file_path": None,
    "fetched_at": "2026-09-12T00:00:00Z", "tool": "WebFetch",
    "content_sha256": "a" * 64,
    "text": ("Redis is an in-memory data structure store. Redis supports "
             "replication and persistence. The default port for Redis is 6379."),
    "full_text_source": "verbatim", "captured_via": "exa",
    "query_provenance": "redis overview",
}


def _gate(tmp_path: Path, draft_text: str) -> dict:
    store = tmp_path / "s.jsonl"
    store.write_text(json.dumps(STORE_RECORD) + "\n", encoding="utf-8")
    draft = tmp_path / "d.md"
    draft.write_text(draft_text, encoding="utf-8")
    env = {**os.environ, "PYTHONPATH": str(REPO_ROOT)}
    result = subprocess.run(
        [sys.executable, GROUND_CHECK, "--draft", str(draft), "--store", str(store), "--json"],
        capture_output=True, text=True, env=env,
    )
    assert result.stdout, f"gate produced no stdout.\nstderr: {result.stderr}"
    return json.loads(result.stdout)


def _scored_texts(report: dict) -> list[str]:
    return [c["text"] for c in report["per_claim"] if c["kind"] != "NON_CLAIM"]


# ---------------------------------------------------------------------------
# R8B-01 — comment delimiters inside code constructs the gate does not
# recognise as code (tilde fences, indented code blocks) delete reader-visible
# prose between them.
# ---------------------------------------------------------------------------

@pytest.mark.xfail(
    strict=True,
    reason="R8B-01 OPEN (tilde fence): _CODE_SPAN_RE only knows backtick "
    "spans. A CommonMark tilde fence (~~~) is code to every renderer but "
    "plain text to _strip_html_comments_outside_code, so a `<!--` shown "
    "inside one fence pairs with a `-->` inside another and deletes the "
    "reader-visible sentence between them — it does not even reach the "
    "scored denominator.",
)
def test_tilde_fenced_comment_delimiters_must_not_delete_visible_prose(tmp_path: Path) -> None:
    draft = (
        "Redis is an in-memory data structure store [S1].\n\n"
        "~~~\n<!-- example opener\n~~~\n\n"
        "MongoDB lost all data under load.\n\n"
        "~~~\n-->\n~~~\n"
    )
    scored = " ".join(_scored_texts(_gate(tmp_path, draft)))
    assert "MongoDB" in scored, (
        "the MongoDB sentence was not SCORED at all — it disappeared between "
        "the tilde-fenced comment delimiters instead of being flagged"
    )


@pytest.mark.xfail(
    strict=True,
    reason="R8B-01 OPEN (indented code block): the same delimiter-hiding "
    "mechanism via a 4-space indented code block, which CommonMark treats as "
    "code and the comment stripper does not.",
)
def test_indented_code_block_comment_delimiters_must_not_delete_visible_prose(tmp_path: Path) -> None:
    draft = (
        "Redis is an in-memory data structure store [S1].\n\n"
        "    <!-- example opener\n\n"
        "MongoDB lost all data under load.\n\n"
        "    -->\n"
    )
    scored = " ".join(_scored_texts(_gate(tmp_path, draft)))
    assert "MongoDB" in scored, (
        "the MongoDB sentence disappeared entirely; scored_claims stayed at 1 "
        "with no hint that text was removed"
    )


@pytest.mark.xfail(
    strict=True,
    reason="R8B-01 OPEN (opposite-meaning variant): the same indented-code-"
    "block mechanism used to delete a NEGATION, so the gate certifies at "
    "PASS/100.0 a document whose visible prose asserts the opposite of the "
    "cited claim ('Redis does not support replication').",
)
def test_indented_code_block_must_not_delete_a_negation_and_certify_the_opposite(tmp_path: Path) -> None:
    draft = (
        "Redis is an in-memory data structure store [S1].\n\n"
        "    <!-- x\n\n"
        "Redis does not support replication [S1].\n\n"
        "    -->\n\n"
        "Redis supports replication and persistence [S1].\n"
    )
    report = _gate(tmp_path, draft)
    scored = " ".join(_scored_texts(report))
    assert "does not support replication" in scored, (
        "the negated sentence was deleted by the comment stripper; the gate "
        "certified a document containing only its negation at "
        f"{report['gate']}/{report['grounding_score']}"
    )


# ---------------------------------------------------------------------------
# R8B-02 — backslash-escaped comment delimiters (\<!-- ... \-->) are literal
# visible text to every CommonMark renderer but a well-formed pair to the
# comment stripper, which has no notion of escaping.
# ---------------------------------------------------------------------------

@pytest.mark.xfail(
    strict=True,
    reason="R8B-02 OPEN (whole-sentence deletion): CommonMark backslash "
    "escapes (\\<!-- , \\-->) render as literal visible text; the stripper "
    "has no escaping awareness, sees a well-formed delimiter pair, and "
    "deletes the visible prose between them, which never reaches the scored "
    "denominator.",
)
def test_escaped_comment_delimiters_must_not_delete_visible_prose(tmp_path: Path) -> None:
    draft = (
        "Redis is an in-memory data structure store [S1].\n\n"
        "\\<!--\n\nMongoDB lost all data under load.\n\n\\-->\n"
    )
    scored = " ".join(_scored_texts(_gate(tmp_path, draft)))
    assert "MongoDB" in scored, (
        "the MongoDB sentence disappeared between escaped comment delimiters "
        "that every CommonMark renderer shows as literal text"
    )


@pytest.mark.xfail(
    strict=True,
    reason="R8B-02 OPEN (mid-sentence reversal): the same escaping gap welds "
    "a claim into a sentence the author never wrote, and the gate certifies "
    "the fabricated sentence GROUNDED at 100.0 — OI-MOAT-26's shape "
    "(weld a delimiter pair into a sentence and reverse it) reopened via "
    "backslash escaping instead of NFKC.",
)
def test_escaped_delimiters_must_not_fabricate_a_reversed_sentence(tmp_path: Path) -> None:
    draft = "Redis is an \\<!--on-disk relational, never an\\--> in-memory data structure store [S1].\n"
    report = _gate(tmp_path, draft)
    scored = " ".join(_scored_texts(report))
    assert "on-disk relational" in scored or report["gate"] != "PASS", (
        "the gate judged and certified a sentence the author did not write: "
        f"{scored!r}"
    )


# ---------------------------------------------------------------------------
# R8B-03 — header weld: the paragraph-break repair (_HEADER_LINE_RE, strict:
# 1-6 hashes + one ASCII space, pre-NFKC) is narrower than the NON_CLAIM
# header exemption (_NO_FINITE_VERB_RE, ^#+\s, post-NFKC). Anything inside the
# second and outside the first gets no paragraph break inserted but is still
# treated as a header, welding an uncited fabrication out of the denominator.
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("header_line", [
    pytest.param("#\tTODO", id="a6-hash-tab-not-space"),
    pytest.param("####### TODO", id="a5-seven-hashes-over-max"),
    pytest.param("#\u00a0TODO", id="a8-hash-nbsp-not-ascii-space"),
    pytest.param("\uff03 TODO", id="a4-fullwidth-hash-pre-nfkc"),
])
@pytest.mark.xfail(
    strict=True,
    reason="R8B-03 OPEN: _HEADER_LINE_RE (paragraph-break repair) is "
    "strictly narrower than the ^#+\\s header exemption that removes a line "
    "from the scored denominator. A header shape inside the exemption but "
    "outside the repair gets no paragraph break, so syntok welds the "
    "following uncited fabrication into the 'header', and the NON_CLAIM "
    "exemption carries the whole welded body out of scoring.",
)
def test_header_shape_outside_the_break_repair_must_not_hide_a_welded_fabrication(
    tmp_path: Path, header_line: str
) -> None:
    draft = f"Redis is an in-memory data structure store [S1].\n\n{header_line}\nMongoDB lost all data under load.\n"
    scored = " ".join(_scored_texts(_gate(tmp_path, draft)))
    assert "MongoDB" in scored, (
        f"the welded fabrication under header line {header_line!r} was not "
        "scored at all"
    )


def test_control_plain_header_is_correctly_caught(tmp_path: Path) -> None:
    """Control from the report: a standard '### TODO' header IS caught (FAIL, 50.0)."""
    draft = "Redis is an in-memory data structure store [S1].\n\n### TODO\nMongoDB lost all data under load.\n"
    report = _gate(tmp_path, draft)
    assert report["gate"] == "FAIL"
    scored = " ".join(_scored_texts(report))
    assert "MongoDB" in scored
