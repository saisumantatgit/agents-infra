"""J-50 — a correct refusal must read as a decision, not as a crash.

`install.sh` routes a first-time user straight into the `--session-id ""`
refusal against the shipped demo store, whose records carry no session id. The
refusal is RIGHT and its wording is good; it arrived behind a ten-line
traceback from `<module>`. A stranger's first thirty seconds therefore looked
like a broken tool rather than a gate declining to assert something it cannot
know — and those are opposite verdicts on whether to trust it.

**What is deliberately NOT tested as a property: softness.** The exit code, the
refusal, and the original message text are all unchanged. Only the packaging
moved. Two of these tests exist to pin that: `--debug` must still produce the
traceback, and the verdict path must still be unguarded, so a defect in
scoring surfaces as a bug report instead of being dressed up as a refusal.

**Run against a DIFFERENT build** with `ASSURE_GROUND_CHECK=/path/to/copy.py`
— which is how these were proven red against the pre-fix script.
"""
from __future__ import annotations

import ast
import os
import subprocess
import sys
from pathlib import Path

import pytest

_AGENT_ASSURE = Path(__file__).resolve().parents[1]
GROUND_CHECK = Path(os.environ.get(
    "ASSURE_GROUND_CHECK", _AGENT_ASSURE / "scripts" / "ground_check.py"))
DEMO_STORE = _AGENT_ASSURE / "demo" / "evidence-store.jsonl"
DEMO_DRAFT = _AGENT_ASSURE / "demo" / "draft-grounded.md"
FABRICATED = _AGENT_ASSURE / "demo" / "draft-fabricated.md"


def _run(*argv: str, cwd: Path | None = None) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(GROUND_CHECK), *argv],
        cwd=str(cwd or _AGENT_ASSURE),
        capture_output=True, text=True,
    )


def _assert_legible(result: subprocess.CompletedProcess) -> str:
    assert result.returncode == 1, "a refusal still exits non-zero"
    combined = result.stdout + result.stderr
    assert "Traceback" not in combined, (
        f"the refusal is behind a traceback:\n{combined}")
    assert "REFUSED:" in result.stderr, (
        f"no refusal line on stderr:\n{combined}")
    return result.stderr


def test_the_J50_shape_an_empty_session_id_reads_as_a_refusal():
    """The exact first-run path install.sh routes a user into."""
    stderr = _assert_legible(_run(
        "--draft", str(DEMO_DRAFT), "--store", str(DEMO_STORE),
        "--session-id", ""))
    # The ORIGINAL wording survives — this is a packaging change, not a rewrite.
    assert "UNATTRIBUTABLE" in stderr
    assert "omit --session-id" in stderr


def test_SIBLING_an_unreadable_draft_reads_as_a_refusal():
    """FMEA: name the sibling. The draft open() was unguarded too."""
    stderr = _assert_legible(_run(
        "--draft", "definitely-not-here.md", "--store", str(DEMO_STORE)))
    assert "definitely-not-here.md" in stderr


def test_SIBLING_a_missing_store_keeps_load_stores_own_better_message():
    stderr = _assert_legible(_run(
        "--draft", str(DEMO_DRAFT), "--store", "definitely-not-here.jsonl"))
    # load_store authors this text; the fix must print it, not replace it.
    assert "capture hook" in stderr
    assert "demo/evidence-store.jsonl" in stderr


def test_a_malformed_line_names_the_STORES_line_number_not_jsons(tmp_path):
    """Found while making the refusals legible: the message only became
    misleading once a user could actually read it.

    Every other failure in load_store carries `lineno`; the parse itself did
    not, so json's own "line 1 column 1" — which counts within the fragment —
    sent a reader to the wrong line of a long store.
    """
    good = (
        '{"source_id":"S1","url":null,"file_path":"/tmp/x",'
        '"fetched_at":"1970-01-01T00:00:00Z","tool":"Read",'
        '"content_sha256":"a","text":"hello world there",'
        '"full_text_source":"verbatim","captured_via":"hook",'
        '"query_provenance":"q"}'
    )
    store = tmp_path / "store.jsonl"
    store.write_text(good + "\nBROKEN\n", encoding="utf-8")
    stderr = _assert_legible(_run(
        "--draft", str(DEMO_DRAFT), "--store", str(store)))
    assert "line 2 of the evidence store" in stderr, stderr


def test_debug_still_gives_the_traceback_and_loses_no_wording():
    """The detail MOVES; it does not disappear."""
    result = _run("--draft", str(DEMO_DRAFT), "--store", str(DEMO_STORE),
                  "--session-id", "", "--debug")
    assert result.returncode == 1
    assert "Traceback" in result.stderr
    assert "UNATTRIBUTABLE" in result.stderr


def test_the_VERDICT_path_is_still_unguarded():
    """A traceback out of scoring is a BUG REPORT and must stay loud.

    Checked over the AST rather than by provoking a defect: no `try` block in
    `main` may contain the scoring pipeline. If a later change widens one of
    the input guards to wrap `score_report`, a genuine defect would be printed
    to a user as "REFUSED", which is the silent-fallback failure this codebase
    forbids wearing a different hat.
    """
    tree = ast.parse(GROUND_CHECK.read_text(encoding="utf-8"))
    main = next(n for n in ast.walk(tree)
                if isinstance(n, ast.FunctionDef) and n.name == "main")
    guarded: set[str] = set()
    for node in ast.walk(main):
        if isinstance(node, ast.Try):
            for inner in ast.walk(node):
                if isinstance(inner, ast.Call) and isinstance(
                        inner.func, ast.Name):
                    guarded.add(inner.func.id)
    for forbidden in ("score_report", "classify", "decompose", "ground"):
        assert forbidden not in guarded, (
            f"main() now catches exceptions from {forbidden}() — a defect in "
            "the verdict path would be reported to the user as a refusal")


@pytest.mark.parametrize("draft,gate", [(FABRICATED, "FAIL")])
def test_the_verdicts_themselves_did_not_move(draft, gate):
    result = _run("--draft", str(draft), "--store", str(DEMO_STORE), "--json")
    assert result.returncode == 1
    assert f'"gate": "{gate}"' in result.stdout, result.stdout
