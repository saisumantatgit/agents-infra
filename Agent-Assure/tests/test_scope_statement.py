"""J-73 — every report states its own scope, in the product, not the README.

WHY THIS IS A PRODUCT FEATURE AND NOT DOCUMENTATION. Ding et al. (AAAI 2025)
measured that user trust RISES when output carries citations **even when the
citations are random**, and falls only when users actually check them. A PASS
verdict therefore buys unearned trust by default, and a disclosure the reader
never opens does not spend it back. Magesh et al. (Stanford, JELS) shows the
alternative: it quotes a vendor's "100% hallucination-free" marketing beside a
measured 17-33% hallucination rate.

THE PROPERTY UNDER TEST is not "a string exists" — that a `return ""` would
satisfy. It is: **every report tells the reader what PASS does and does not
mean, the statement matches the scope this run can actually claim, and no
verdict path can see it.**

THE SIBLING, named per FMEA (and the reason there are two variants). "retrieved
this session" is a claim about SCOPE. The gate can only make it when
`--session-id` was passed; J-56 was exactly this overclaim in `evidence_basis`,
which said "NEVER RETRIEVED this session" about a store it had no session
information for. So the unscoped variant must NOT say "this session", and must
say how to get session scope.
"""
from __future__ import annotations

import ast
import inspect
import json
import subprocess
import sys
import textwrap
from pathlib import Path

import pytest

_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_ROOT / "scripts"))

import ground_check as g  # noqa: E402


def _src(source_id: str, text: str) -> g.RetrievedSource:
    return g.RetrievedSource(
        source_id=source_id, url=None, file_path="/tmp/x",
        fetched_at="2026-10-03T00:00:00Z", tool="Read", content_sha256="sha",
        text=text, full_text_source="verbatim", captured_via="hook",
        query_provenance="a search",
    )


STORE = {"S1": _src("S1", "Redis handles 100K ops per second in sustained testing.")}


def _report(draft: str, *, session_scoped: bool = False) -> dict:
    claims = [g.classify(c) for c in g.decompose(draft)]
    return g.score_report(claims, STORE, session_scoped=session_scoped)


@pytest.mark.parametrize("draft", [
    "Redis handles 100K ops per second [S1].",                 # PASS
    "The device sold 250,000 units in its first month.",        # UNCITED
    "The trial reported a 62% response rate [S19].",            # fabricated
])
def test_every_report_carries_a_scope_statement(draft):
    """On every verdict, not just PASS — a reader weighing a FAIL needs it too."""
    scope = _report(draft)["scope"]
    assert scope.strip(), "empty scope statement"
    assert scope.endswith("."), "not a sentence"
    assert len(scope.split()) >= 25, f"too terse to disclose anything: {scope}"
    assert "does not mean the source agrees" in scope
    assert "denies or hedges" in scope


def test_the_statement_never_uses_the_word_verified():
    """'Verified' is the word Magesh et al. punished. It must not appear."""
    for scoped in (True, False):
        scope = g.scope_statement(scoped)
        assert "verified" not in scope.lower(), scope
        assert "verify" not in scope.lower(), scope


def test_the_UNSCOPED_statement_does_not_claim_session_scope():
    """THE J-56 SIBLING. Without --session-id the gate cannot say 'this session'."""
    scope = g.scope_statement(False)
    assert "this session" not in scope.lower().replace(
        "retrieved this session", ""), scope
    assert "evidence store supplied to this run" in scope
    assert "--session-id" in scope, "must say how to obtain session scope"


def test_the_SCOPED_statement_does_claim_session_scope():
    """The positive control: without it, the test above is satisfied by a stub."""
    scope = g.scope_statement(True)
    assert "retrieved this session" in scope, scope
    assert "--session-id" not in scope, "scoped run should not advertise the flag"


def test_the_two_variants_are_different():
    assert g.scope_statement(True) != g.scope_statement(False)


def test_the_human_CLI_path_prints_the_statement(tmp_path):
    """The one-line summary is what a person reads; the file is not."""
    draft = tmp_path / "d.md"
    draft.write_text("Redis handles 100K ops per second [S1].\n", encoding="utf-8")
    store = tmp_path / "s.jsonl"
    store.write_text(json.dumps({
        "source_id": "S1", "url": None, "file_path": "/tmp/x",
        "fetched_at": "2026-10-03T00:00:00Z", "tool": "Read",
        "content_sha256": "sha",
        "text": "Redis handles 100K ops per second in sustained testing.",
        "full_text_source": "verbatim", "captured_via": "hook",
        "query_provenance": "q",
    }) + "\n", encoding="utf-8")
    proc = subprocess.run(
        [sys.executable, str(_ROOT / "scripts" / "ground_check.py"),
         "--draft", str(draft), "--store", str(store)],
        capture_output=True, text=True, cwd=str(tmp_path), check=False)
    assert "does not mean the source agrees" in proc.stdout, proc.stdout


def test_no_verdict_path_consults_the_scope_statement():
    """Display must never become decision (D-34). Checked over the AST."""
    for name in ("ground", "check_absence", "ground_relational", "classify"):
        tree = ast.parse(textwrap.dedent(inspect.getsource(getattr(g, name))))
        referenced = {n.id for n in ast.walk(tree) if isinstance(n, ast.Name)} | {
            n.attr for n in ast.walk(tree) if isinstance(n, ast.Attribute)}
        assert "scope_statement" not in referenced, f"{name} consults the display layer"
        assert "_SCOPE_SESSION" not in referenced, f"{name} consults the display layer"
        assert "_SCOPE_STORE" not in referenced, f"{name} consults the display layer"


# ---------------------------------------------------------------------------
# R15-01 — round 15 found J-56's overclaim reproduced BY the J-73 disclosure.
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("blank", ["", " ", "\t", "   \n "])
def test_an_empty_session_id_REFUSES_rather_than_claiming_session_scope(blank):
    """`--session-id ""` scored the demo store at PASS 100.0 and printed
    "retrieved this session" over records carrying no session id at all.

    `assert_single_session`'s docstring already promised that an empty id
    raises. It did not: the test is `source.session_id != session_id`, so a
    blank expected id against blank record ids evaluates `"" != ""`, finds
    nothing foreign and returns. The emptiness of the expected id is a fact
    about the REQUEST, so no comparison against the store can establish it —
    the guard has to be explicit and first.
    """
    store = {"S1": _src("S1", "Redis handles 100K ops per second.")}
    with pytest.raises(ValueError, match="UNATTRIBUTABLE"):
        g.assert_single_session(store, blank)


def test_a_REAL_session_id_still_enforces_normally(tmp_path):
    """POSITIVE CONTROL — the guard must not have broken real enforcement."""
    foreign = g.RetrievedSource(
        source_id="S1", url=None, file_path="/tmp/x",
        fetched_at="2026-10-03T00:00:00Z", tool="Read", content_sha256="sha",
        text="t", full_text_source="verbatim", captured_via="hook",
        query_provenance="q", session_id="OTHER",
    )
    with pytest.raises(ValueError, match="outside this session"):
        g.assert_single_session({"S1": foreign}, "MINE")
