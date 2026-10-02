"""CLAIM-1 — every sentence of the product claim, pinned to behaviour.

WHY THIS FILE EXISTS. On 2026-10-01 a red-team round found that the shipped
surfaces (`plugin.json`, `README.md`, `commands/`, `skills/`) promised a claim is
"grounded in a source actually retrieved **this session**" while the code had no
session boundary at all. The tin and the code had drifted, and nothing could
detect that, because a product claim written in Markdown is not executable.

Worse, a three-kind search found that **"no LLM calls during grounding" — the
project's loudest claim, which CLAUDE.md calls "the product, not a style choice"
— was asserted on four surfaces and enforced by ZERO tests.** Its only appearance
in the suite was as prose inside a determinism fixture's draft text.

So this file is the executable version of the claim. Two halves, and the second
is the unusual one:

  1. WHAT WE PROMISE — each guarantee has a test. If a guarantee breaks, the
     suite fails before the claim becomes a lie.
  2. WHAT WE DO NOT PROMISE — each DISCLOSED LIMITATION also has a test,
     asserting the limitation is still real. If someone later closes one, THIS
     FILE FAILS, and whoever closed it must update the claim text to match.

That second half is what keeps the tin honest in both directions. A claim can
drift from the code by the code getting worse OR by the code getting better
while the documentation stays timid.
"""
from __future__ import annotations

import ast
import json
import sys
import tempfile
from pathlib import Path

import pytest

_SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(_SCRIPTS))

import ground_check as g  # noqa: E402


# ===========================================================================
# 1. WHAT WE PROMISE
# ===========================================================================

# Every module the verdict path is allowed to import. stdlib + syntok only.
# syntok is a deterministic sentence segmenter, not a model.
_ALLOWED_IMPORTS = frozenset({
    "__future__", "collections", "collections.abc", "dataclasses", "enum",
    "json", "re", "typing", "unicodedata", "argparse", "sys", "yaml",
    "syntok", "syntok.segmenter", "hashlib", "pathlib", "os", "itertools",
    "functools", "math", "string", "textwrap",
})

# Anything here in the verdict path would make the central claim false.
_FORBIDDEN_SUBSTRINGS = (
    "anthropic", "openai", "cohere", "mistral", "google.generativeai", "genai",
    "transformers", "torch", "tensorflow", "sentence_transformers", "litellm",
    "langchain", "requests", "httpx", "urllib", "http.client", "socket",
    "aiohttp", "subprocess", "random",
)


def _imported_modules(path: Path) -> set[str]:
    """Every module name imported anywhere in *path*, including lazily."""
    tree = ast.parse(path.read_text(encoding="utf-8"))
    names: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            names.update(a.name for a in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            names.add(node.module)
    return names


def test_the_verdict_path_imports_no_model_and_no_network():
    """THE CENTRAL CLAIM: "proven by a deterministic gate, not asserted by the
    model that wrote the claim."

    Checked over the AST so a LAZY import inside a function is caught too — the
    `syntok` import is lazy, which proves lazy imports are a real pattern here.
    """
    imported = _imported_modules(_SCRIPTS / "ground_check.py")
    for name in sorted(imported):
        for forbidden in _FORBIDDEN_SUBSTRINGS:
            assert forbidden not in name.lower(), (
                f"ground_check.py imports {name!r}, which contains {forbidden!r}. "
                f"The verdict path must not reach a model, the network, a "
                f"subprocess, or a random source — that is the product claim."
            )
        assert name in _ALLOWED_IMPORTS, (
            f"ground_check.py imports {name!r}, which is not on the verdict "
            f"path allowlist. If it is genuinely deterministic and local, add "
            f"it to _ALLOWED_IMPORTS in this test ON PURPOSE, with a reason."
        )


def test_the_no_model_guard_can_actually_fail():
    """Proves the guard above is not a tautology, by running its own logic over
    a synthetic module that imports a model client. A guard nobody has seen fail
    is a guard nobody can trust."""
    with tempfile.TemporaryDirectory() as d:
        bad = Path(d) / "bad.py"
        bad.write_text("import anthropic\n", encoding="utf-8")
        assert "anthropic" in _imported_modules(bad)


def _store(tmp_path, records):
    p = tmp_path / "s.jsonl"
    p.write_text("".join(json.dumps(r) + "\n" for r in records), encoding="utf-8")
    return g.load_store(str(p))


def _rec(sid="S1", text="Redis replicates to three replicas.",
         fts="verbatim", tool="Read", qp="q1"):
    return {"source_id": sid, "url": None, "file_path": "/tmp/a",
            "fetched_at": "2026-09-13T00:00:00Z", "tool": tool,
            "content_sha256": "a" * 64, "text": text,
            "full_text_source": fts, "captured_via": "inline",
            "query_provenance": qp}


def _verdicts(tmp_path, draft, records):
    rep = g.score_report([g.classify(c) for c in g.decompose(draft)],
                         _store(tmp_path, records))
    return rep


def test_a_cited_marker_that_names_nothing_is_refused(tmp_path):
    """PROMISE: a citation must resolve to a source in the store."""
    rep = _verdicts(tmp_path,
                    "Redis replicates to three replicas [S1][S99].\n", [_rec()])
    assert rep["gate"] != "PASS"
    assert "UNVERIFIED_CITATION" in [c["verdict"] for c in rep["per_claim"]]


def test_a_summarised_source_can_never_ground_a_claim(tmp_path):
    """PROMISE: native WebFetch is Haiku-summarised, so it is not evidence of
    what a page said. The gate refuses to certify against it."""
    rep = _verdicts(tmp_path, "Redis replicates to three replicas [S1].\n",
                    [_rec(fts="haiku_summary", tool="WebFetch")])
    assert rep["gate"] != "PASS"
    assert rep["per_claim"][0]["verdict"] == "UNGROUNDABLE"


def test_a_figure_not_in_the_cited_source_is_refused(tmp_path):
    """PROMISE: numbers are checked against the cited source, value AND unit."""
    rep = _verdicts(tmp_path, "Redis handles 250K ops per second [S1].\n",
                    [_rec(text="Redis handles 100K ops per second.")])
    assert rep["gate"] != "PASS"


def test_a_pass_requires_an_empty_retained_appendix(tmp_path):
    """PROMISE (ADR-005): a ratio can never buy a PASS past a retained
    violation. Any violation-class verdict blocks PASS outright."""
    rep = _verdicts(
        tmp_path,
        "Redis replicates to three replicas [S1]. MongoDB lost all data.\n",
        [_rec()])
    assert rep["retained_appendix"], "expected a retained violation"
    assert rep["gate"] != "PASS"


def test_the_same_draft_and_store_always_give_the_same_verdict(tmp_path):
    """PROMISE: deterministic. An audit artifact that changes between runs is
    not an audit artifact."""
    draft = "Redis replicates to three replicas [S1].\n"
    first = _verdicts(tmp_path, draft, [_rec()])
    second = _verdicts(tmp_path, draft, [_rec()])
    assert first == second


# ===========================================================================
# 2. WHAT WE DO NOT PROMISE — limitations, pinned so the tin cannot overclaim
#
# Each test below asserts a LIMITATION IS STILL REAL. If one fails, the code
# improved and the claim text in README.md / plugin.json / commands/ / skills/
# must be updated in the same commit.
# ===========================================================================

def test_LIMITATION_paraphrase_is_not_verified(tmp_path):
    """NOT PROMISED: that an honest paraphrase passes. The gate certifies
    VERBATIM provenance, not meaning. T2 was demoted (ADR-006) and no NLI tier
    exists, so a faithful restatement reads UNGROUNDED. This is the measured
    Error-A of 0.320 (n=52, CR-004) and it is a FEATURE of the claim's scope,
    not a defect to hide: the gate says "I could not mechanically trace this",
    which is true."""
    rep = _verdicts(tmp_path,
                    "Redis keeps three copies of the data [S1].\n",
                    [_rec(text="Redis replicates to three replicas.")])
    assert rep["per_claim"][0]["verdict"] == "UNGROUNDED", (
        "paraphrase now grounds — the claim text may now promise more")


def test_LIMITATION_a_file_the_agent_wrote_itself_is_trusted(tmp_path):
    """NOT PROMISED: that the agent cannot manufacture its own evidence.

    ACCEPTED DESIGN, ruled by Sai 2026-10-01: the drafting agent's TOOL CHOICES
    are trusted. `Read` is mapped to `verbatim` unconditionally and no field
    records a file's ORIGIN, so an agent that writes a file and reads it back
    produces a verbatim source. The gate verifies that the draft matches what
    the session READ; it does not verify where what it read came from.

    This test exists so the claim can never quietly imply otherwise."""
    rep = _verdicts(tmp_path,
                    "The Zentara trial reported a 62% response rate [S1].\n",
                    [_rec(text="The Zentara trial reported a 62% response "
                               "rate.", tool="Read")])
    assert rep["gate"] == "PASS", (
        "agent-authored evidence is no longer trusted — if this was fixed "
        "deliberately, update the product claim and this docstring")


def test_LIMITATION_absence_queries_are_chosen_by_the_agent(tmp_path):
    """NOT PROMISED: that "we found no evidence of X" was checked against a real
    search. ACCEPTED DESIGN (Sai, 2026-10-01): no search tool is captured, so
    the "distinct searches" behind an absence claim are strings the agent
    supplied as `query_provenance`."""
    recs = [_rec("SA1", "Nothing was found in the recall archive for the X200.",
                 qp="recall evidence search X200 drone"),
            _rec("SA2", "The recall database returned zero results for X200.",
                 qp="regulatory database evidence query X200")]
    rep = _verdicts(tmp_path,
                    "We found no evidence of a safety recall affecting the "
                    "X200 drone.\n", recs)
    assert rep["gate"] == "PASS", (
        "absence certification changed — update the claim text")


def test_LIMITATION_a_multi_line_authoring_note_is_scored(tmp_path):
    """NOT PROMISED: that authoring comments are ignored. J-48: the comment rule
    strips SAME-LINE comments only, so a multi-line note is scored as claims and
    fails the draft. Keep notes on one line."""
    rep = _verdicts(tmp_path,
                    "Redis replicates to three replicas [S1].\n\n<!--\nTODO: "
                    "check this.\nAsk the team.\n-->\n", [_rec()])
    assert rep["gate"] == "FAIL", "J-48 was fixed — update the claim text"


def test_LIMITATION_a_relational_claim_is_never_certified_by_corroboration(tmp_path):
    """NOT PROMISED, since ADR-007: that a causal or correlational claim is
    certified because two sources corroborate it.

    Round 12 demonstrated seven Error-B shapes on that rule, so it was demoted:
    a RELATIONAL claim now reaches the ordinary verbatim path, and certifies
    only when a cited source contains the claim itself. The corroboration
    result is still computed and REPORTED — as information, never a verdict.

    This store corroborates the relation across two sources as strongly as the
    old rule ever required. The claim must still be refused.
    """
    recs = [
        _rec(sid="S1", qp="q1",
             text="Insulin resistance impairs glucose uptake and is a central "
                  "mechanism that causes type 2 diabetes to develop."),
        _rec(sid="S2", qp="q2",
             text="Type 2 diabetes develops when insulin resistance "
                  "progresses and the pancreas cannot compensate."),
    ]
    rep = _verdicts(tmp_path, "Insulin resistance causes type 2 diabetes "
                              "[S1][S2].\n", recs)
    pc = rep["per_claim"][0]
    assert pc["kind"] == "RELATIONAL"
    assert pc["relation_diagnostic"] == g.RELATION_CORROBORATED, (
        "the diagnostic must still measure corroboration — a demotion that "
        "stops computing the thing is a deletion, not a demotion")
    assert pc["verdict"] == "UNGROUNDED", (
        "ADR-007 was reverted — update the claim text before this test"
    )
    assert rep["gate"] == "FAIL"


def test_the_verdict_path_does_not_consult_the_RELATIONAL_DIAGNOSTIC():
    """ADR-007's load-bearing guard, checked over the AST.

    A diagnostic that creeps back into the verdict path is how a demotion
    silently un-demotes itself — and this repo has the scar: ADR-006 demoted T2
    and kept `tier_sensitive` precisely so a future change could not quietly
    re-threshold verdicts that are supposed to be unable to move.

    `ground` must reference NONE of the demoted machinery, and
    `UNVERIFIED_RELATION` must no longer be reachable from it.
    """
    import ast
    import inspect
    import textwrap

    tree = ast.parse(textwrap.dedent(inspect.getsource(g.ground)))
    referenced = {n.id for n in ast.walk(tree) if isinstance(n, ast.Name)} | {
        n.attr for n in ast.walk(tree) if isinstance(n, ast.Attribute)}
    for name in ("relational_diagnostic", "ground_relational",
                 "extract_arguments", "spelled_quantity_ok",
                 "_endpoint_in_window", "UNVERIFIED_RELATION"):
        assert name not in referenced, (
            f"ground() references {name!r} — ADR-007 demoted it to a "
            f"diagnostic, so the verdict path must not read it")


def test_the_demoted_machinery_is_KEPT_not_deleted():
    """The other half of ADR-007, and the one a cleanup would quietly undo.

    The repo's standing rule is that a demoted computation stays a VISIBLE
    no-op (the `tier_sensitive` precedent). If someone deletes these in a
    tidy-up, every round-10 and round-12 tripwire written against the
    diagnostic disappears with them, and the record of seven findings goes too.
    """
    for name in ("relational_diagnostic", "ground_relational",
                 "extract_arguments", "spelled_quantity_ok",
                 "_endpoint_in_window", "RELATION_CORROBORATED",
                 "RELATION_NOT_CORROBORATED", "RELATION_FIGURE_ABSENT"):
        assert hasattr(g, name), (
            f"{name} was deleted. ADR-007 says KEPT as a visible no-op — "
            f"deleting it takes the tripwires and the findings record with it")
    assert g.Verdict.UNVERIFIED_RELATION, (
        "UNVERIFIED_RELATION must stay in the taxonomy: retired, not deleted")


# ===========================================================================
# 3. THE SHIPPED SURFACES must not re-acquire a claim the code cannot keep
# ===========================================================================

_SURFACES = (
    ".claude-plugin/plugin.json",
    "README.md",
    "commands/assure-verify.md",
    "skills/verify-grounding/SKILL.md",
)

# Phrases that assert something the gate does NOT enforce. Each was on a shipped
# surface until 2026-10-01 and each was false.
_RETIRED_CLAIMS = (
    "actually retrieved this session",
    "retrieved this session",
    "proves every factual claim",
    "this session's evidence store",
)

_ROOT = Path(__file__).resolve().parents[1]


@pytest.mark.parametrize("surface", _SURFACES)
def test_no_shipped_surface_overclaims(surface):
    """A product claim written in Markdown is not executable, so it drifts.

    This is the cheap half of keeping the tin honest: the expensive half is the
    behaviour tests above. Together they catch drift in both directions — the
    code getting worse, and the prose getting braver.

    If a phrase here becomes TRUE (e.g. J-38 lands a real session boundary),
    delete it from _RETIRED_CLAIMS in the same commit that makes it true. Do not
    delete it to make this test pass.
    """
    text = (_ROOT / surface).read_text(encoding="utf-8").lower()
    for phrase in _RETIRED_CLAIMS:
        # The skill is allowed to QUOTE a retired phrase in order to forbid it.
        if phrase in text and 'never "retrieved this session"' not in text:
            pytest.fail(
                f"{surface} contains the retired claim {phrase!r}. The gate does "
                f"not enforce it — see the limitations block on that surface."
            )


@pytest.mark.parametrize("surface", _SURFACES)
def test_every_surface_states_a_limitation(surface):
    """An honest claim names its boundary. A surface that promises without
    disclosing is how the 2026-10-01 drift happened in the first place."""
    text = (_ROOT / surface).read_text(encoding="utf-8").lower()
    assert any(k in text for k in ("does not", "not prove", "refuses")), (
        f"{surface} makes a promise but discloses no boundary")


# The two drafting rules J-48 and the citation-placement finding resolved to.
# Both are DOCUMENTATION fixes, which is the weakest kind of fix there is: prose
# has no runtime, so nothing fails when it is deleted. These two guards give the
# prose a runtime.
_MARKDOWN_SURFACES = ("README.md", "commands/assure-verify.md",
                      "skills/verify-grounding/SKILL.md")


@pytest.mark.parametrize("surface", _MARKDOWN_SURFACES)
def test_every_markdown_surface_tells_authors_to_keep_notes_on_one_line(surface):
    """J-48's ruling was documentation, not code — so the documentation is the fix.

    `test_LIMITATION_a_multi_line_authoring_note_is_scored` pins the BEHAVIOUR
    (a multi-line note fails the draft). This pins the only MITIGATION that
    exists: the author must be told, on every surface they might read, that a
    note has to fit on one line. If the guidance is deleted the limitation stops
    being disclosed and starts being a trap, and nothing else in the suite
    notices — prose has no runtime of its own.
    """
    text = (_ROOT / surface).read_text(encoding="utf-8").lower()
    assert "one line" in text, (
        f"{surface} does not tell authors to keep authoring notes on one line "
        f"(J-48). The gate strips SAME-LINE comments only; an undisclosed "
        f"multi-line note is scored as claims.")
    assert "<!--" in text, f"{surface} states the rule without showing the syntax"


@pytest.mark.parametrize("surface", _MARKDOWN_SURFACES)
def test_every_markdown_surface_states_the_citation_placement_rule(surface):
    """The sibling convention, pinned for the same reason.

    A marker after the sentence-final period detaches and reads UNCITED. That is
    fail-safe, so it will never show up as a test failure anywhere else — it only
    ever shows up as a confused author.
    """
    text = (_ROOT / surface).read_text(encoding="utf-8").lower()
    assert "final period" in text, (
        f"{surface} does not state where citation markers go")


def test_a_missing_store_says_what_to_do(tmp_path):
    """α4 friction 1: the first command the installer prints points at a store
    that does not exist on a fresh install (no research has happened yet). A raw
    FileNotFoundError traceback was the first thing a new user saw. Still an
    exception, still exit 1 — but it must now name the cause and a remedy."""
    with pytest.raises(FileNotFoundError) as exc:
        g.load_store(str(tmp_path / "nope.jsonl"))
    message = str(exc.value)
    assert "capture hook" in message, "does not explain WHY it is missing"
    assert "demo/evidence-store.jsonl" in message, "offers no working remedy"


def test_LIMITATION_the_capture_hook_does_not_run_in_print_mode():
    """NOT PROMISED: that Agent-Assure works in `claude -p` / CI mode.

    Verified 2026-10-02 with a three-way control: a plugin hook via
    `--plugin-dir`, a project-local `.claude/settings.json` hook, and an explicit
    `--settings` hook. NONE fired, while the `Read` tool itself demonstrably ran
    (the model answered from the file each time). So print mode does not execute
    PostToolUse hooks however they are registered.

    Consequence: the store stays EMPTY and every claim reads UNCITED, so the gate
    fails everything for a reason unrelated to the draft.

    This test asserts the LIMITATION IS DOCUMENTED, because the behaviour itself
    belongs to Claude Code and cannot be asserted from pytest. If print mode ever
    starts running hooks, delete this test AND the caveat it guards — together.
    """
    readme = (_ROOT / "README.md").read_text(encoding="utf-8")
    skill = (_ROOT / "skills" / "verify-grounding" / "SKILL.md").read_text(encoding="utf-8")
    for surface, text in (("README.md", readme), ("SKILL.md", skill)):
        assert "print mode" in text.lower() or "claude -p" in text.lower(), (
            f"{surface} does not warn that the capture hook never runs in "
            f"print mode — a user wiring this into CI gets a gate that fails "
            f"everything with no explanation")
