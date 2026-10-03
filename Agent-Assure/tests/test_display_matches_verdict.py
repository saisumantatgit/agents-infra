"""J-45 — the report must not announce evidence the verdict did not use.

Round 11-B found `evidence_basis` calling `_session_queries` while the ABSENCE
verdict path had been switched to `_verbatim_session_queries`, so an absence PASS
told the user "Complete record consulted: 4 distinct search queries" while the
verdict had counted only two — and including the other two would have REVERSED
the verdict. Display contradicting the verdict is the D-35 defect class: the gate
lying about its own reasoning.

CLOSED BY D-54, not by a fix aimed at it. Reverting the verbatim-query
restriction (which was my own Error-B) put both paths back on the same function.
Per D-46's standing rule — when a change makes an unrelated finding pass, assume
it MASKED it until proven CLOSED — this is proof by CONSTRUCTION rather than by
coincidence: there is now exactly one query-source function, and both the verdict
and the display call it on the same store, so the count shown IS the count used.

The AST guard below is what keeps that true. It is deliberately NOT a substring
check over source text: D-41 established that a textual guard cannot tell a call
from a comment, and it then failed a commit for writing a function's name in
prose explaining the rule.
"""
from __future__ import annotations

import ast
import inspect
import json
import sys
import textwrap
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

import ground_check as g  # noqa: E402


def _query_sources_called(func) -> set[str]:
    """Names of the query-source FUNCTIONS *func* calls, via the AST.

    Deliberately restricted to ast.Call targets, not every referenced name: the
    first version of this guard compared all names and failed because
    evidence_basis has a LOCAL VARIABLE called `queries`. A guard that fires on a
    variable name is the substring mistake of D-41 wearing an AST costume.
    """
    tree = ast.parse(textwrap.dedent(inspect.getsource(func)))
    called: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            target = node.func
            name = getattr(target, "id", None) or getattr(target, "attr", None)
            if name and "session_queries" in name:
                called.add(name)
    return called


def test_display_and_verdict_use_the_SAME_query_source():
    """THE GUARD. If these two ever consult different functions, the report can
    announce a query set the verdict never counted — which is exactly what round
    11-B found."""
    verdict_sources = _query_sources_called(g.ground)
    display_sources = _query_sources_called(g.evidence_basis)
    assert verdict_sources, "ground() consults no query source — rule has moved"
    assert display_sources, "evidence_basis consults no query source"
    assert verdict_sources == display_sources, (
        f"verdict uses {verdict_sources} but the report shows {display_sources}. "
        f"A report that announces evidence the verdict did not use is the D-35 "
        f"defect class.")


def test_only_one_query_source_function_exists():
    """SIBLING: the divergence was possible because a SECOND query-source
    function existed. Keeping it at one is what makes the guard above
    structural rather than a convention."""
    query_fns = sorted(
        name for name in dir(g)
        if name.startswith("_") and "session_queries" in name
    )
    assert query_fns == ["_session_queries"], (
        f"more than one session-query source exists: {query_fns}. That is how "
        f"the verdict and the display diverged in the first place.")


def test_an_absence_pass_reports_the_query_count_it_actually_used(tmp_path):
    """End-to-end: the number the user reads is the number that decided it."""
    def rec(sid, text, qp):
        return {"source_id": sid, "url": None, "file_path": "/tmp/a",
                "fetched_at": "1970-01-01T00:00:00Z", "tool": "Read",
                "content_sha256": "a" * 64, "text": text,
                "full_text_source": "verbatim", "captured_via": "inline",
                "query_provenance": qp}

    records = [
        rec("SA1", "No recall evidence was found in the manufacturer safety "
                   "bulletin archive for the X200 drone line.",
            "recall evidence search X200 drone"),
        rec("SA2", "The public recall database returned zero results for the "
                   "X200 drone.", "regulatory database evidence query X200"),
    ]
    p = tmp_path / "s.jsonl"
    p.write_text("".join(json.dumps(r) + "\n" for r in records), encoding="utf-8")
    store = g.load_store(str(p))
    claim = "We found no evidence of a safety recall affecting the X200 drone.\n"
    rep = g.score_report([g.classify(c) for c in g.decompose(claim)], store)

    assert rep["gate"] == "PASS"
    basis = rep["per_claim"][0]["evidence_basis"]
    actual = len(g._session_queries(store, frozenset()))
    assert str(actual) in basis, (
        f"the report does not state the {actual} queries the verdict counted: "
        f"{basis!r}")


def test_evidence_basis_never_claims_session_scoping():
    """J-56 — the report must not claim a scope the gate did not enforce.

    `evidence_basis` said a missing citation "was NEVER RETRIEVED this session".
    It cannot know that: the store is session-bounded only when the caller passes
    `--session-id`, and `evidence_basis` is not told whether they did. Without
    the flag, all the gate knows is that the id is not in the store.

    FOUND BY A STRANGER, not by this suite. A real `claude -p` session invoked
    `/assure-verify` on a fabricated draft, got the right verdict, and then said:
    "the engine's message says S3 was 'never retrieved this session', but I
    didn't pass --session-id, so the check wasn't limited to this session."

    It is the SAME overclaim CLAIM-1 retired from all four shipped surfaces,
    surviving one layer down in the engine's runtime output — and my drift guard
    was blind to it because it reads shipped DOCUMENTS, not the strings the
    engine PRINTS. This test is that missing sibling.

    Scoped to `evidence_basis` deliberately: `--session-id`'s help text and
    `assert_single_session`'s error DO legitimately say "this session", because
    they only run when the caller asserted it. The invariant is not "never
    mention sessions"; it is "do not claim a scope you were not given".
    """
    tree = ast.parse(textwrap.dedent(inspect.getsource(g.evidence_basis)))
    literals = [n.value for n in ast.walk(tree)
                if isinstance(n, ast.Constant) and isinstance(n.value, str)]
    offenders = [s for s in literals if "this session" in s.lower()]
    assert not offenders, (
        f"evidence_basis claims session scoping it cannot verify: {offenders}. "
        f"Without --session-id the gate only knows the id is absent from the "
        f"store.")
