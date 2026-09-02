"""Error-A harness — the mirror of tests/red_team_moat/.

WHY THIS EXISTS
---------------
The red-team harness asks one question: *can a fabrication PASS?* Four rounds of
it have found 62 wrongful PASSes and made the gate much stricter. But a gate is
a two-sided instrument, and only one side was ever measured. An adversary hunts
wrongful PASSes, so **no number of red-team rounds can surface a wrongful FAIL
— by construction.**

That blind spot was not theoretical. A deliberate honest-draft sweep on
2026-08-30, run immediately after nine consecutive fail-closed fixes, found
OI-T2-01: a sentence quoted VERBATIM from a source reads `UNGROUNDED`, because
it is 7 tokens (below T1's 8-token floor) and T2's F1 penalises precision
against a long source window. "I quoted your source exactly and it says
ungrounded" is the worst user experience this product can produce, and four
adversarial rounds had walked straight past it.

These tests assert the OTHER direction: honest drafts must not be flagged.
A failure here is Error-A — recoverable, never a release blocker — but a
silent, accumulating Error-A is how a verification tool gets switched off, and
a tool that is switched off has an unbounded Error-B.

Some of these are EXPECTED failures, marked xfail against a named OI. That is
the point: this file makes the false-alarm surface visible and countable
instead of leaving it to be discovered by a user.
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
STORE = str(REPO_ROOT / "tests" / "red_team_moat" / "fixtures" / "store.jsonl")

# A SECOND frozen store, owned by this harness (the adversarial fixture above is
# frozen and must not grow honest-side cases). Its sources are deliberately
# SHORT — one sentence each — because window length is what decides whether the
# T2-only region is reachable at all. Against the long red-team sources, a claim
# with no novel tokens can only clear lex_tau by covering most of the window,
# and covering most of a long window forces a >=8-token contiguous span, which
# T1 catches first. Short sources are therefore the only place a T2-ONLY honest
# claim exists — which is exactly why the harness had no such case (see
# test_t2_only_* below).
#   S1 "The redesigned coolant pump delivers a lower operating temperature than
#       the previous unit in sustained load testing."
#   S2 "In the second quarter, Helios Freight moved 3,100 containers through its
#       northern terminal."
T2_STORE = str(Path(__file__).parent / "fixtures" / "store.jsonl")

# Frozen store (same fixture the adversarial harness uses):
#   S1 "Redis is an in-memory data structure store used as a database and
#       cache. In our controlled benchmark on a single node, Redis sustained
#       approximately 128000 operations per second, which was about twelve
#       times the throughput of the disk-backed alternative under the same
#       workload."
#   S2 "PostgreSQL is a relational database management system. Under the same
#       benchmark load and hardware, PostgreSQL sustained approximately 11000
#       write operations per second with full durability guarantees enabled."


def _gate(tmp_path: Path, draft_text: str, store: str = STORE) -> dict:
    draft = tmp_path / "draft.md"
    draft.write_text(draft_text, encoding="utf-8")
    env = {**os.environ, "PYTHONPATH": str(REPO_ROOT)}
    result = subprocess.run(
        [sys.executable, GROUND_CHECK, "--draft", str(draft), "--store", store, "--json"],
        capture_output=True, text=True, env=env,
    )
    assert result.stdout, f"gate produced no stdout.\nstderr: {result.stderr}"
    return json.loads(result.stdout)


def _assert_clean(report: dict, draft: str) -> None:
    flagged = [
        (c["text"], c["verdict"]) for c in report["per_claim"]
        if c["kind"] != "NON_CLAIM"
        and c["verdict"] not in ("GROUNDED", "ABSENCE_SUPPORTED")
    ]
    assert report["gate"] == "PASS", (
        f"honest draft wrongly flagged (gate={report['gate']}, "
        f"score={report['grounding_score']}): {flagged}\ndraft: {draft!r}"
    )


# --- Drafts that must PASS ---------------------------------------------------

HONEST = [
    pytest.param(
        "Redis is an in-memory data structure store used as a database and "
        "cache [S1].\n",
        id="honest-long-verbatim-quote",
    ),
    pytest.param(
        "PostgreSQL sustained approximately 11000 write operations per second "
        "with full durability guarantees enabled [S2].\n",
        id="honest-numeric-with-rate-and-quantity",
    ),
    pytest.param(
        "Redis sustained approximately 128000 operations per second, which was "
        "about twelve times the throughput of the disk-backed alternative "
        "under the same workload [S1].\n",
        id="honest-full-sentence-with-comparison",
    ),
    pytest.param(
        "# Benchmark Summary\n\n## Methods\n\nRedis is an in-memory data "
        "structure store used as a database and cache [S1].\n\n"
        "## Discussion\n\nPostgreSQL sustained approximately 11000 write "
        "operations per second with full durability guarantees enabled [S2].\n\n"
        "In conclusion.\n",
        id="honest-structured-document-with-headings",
    ),
]


@pytest.mark.parametrize("draft", HONEST)
def test_honest_draft_is_not_flagged(tmp_path: Path, draft: str) -> None:
    """A faithful, correctly-cited draft must reach PASS.

    The structured-document case is the load-bearing one: ordinary markdown
    headings ("## Methods", "## Discussion") and a transition ("In conclusion.")
    must stay NON_CLAIM. Round 4 made header handling stricter to stop
    assertions hiding in headings, and this is the guard that the strictness did
    not spill onto real document furniture.
    """
    _assert_clean(_gate(tmp_path, draft), draft)


# --- Known false alarms: recorded, counted, and tied to an open issue --------

@pytest.mark.xfail(
    strict=True,
    reason="OI-T2-01 (OPEN): a 7-token verbatim sentence quote reads UNGROUNDED "
    "— below T1's 8-token span floor, and T2's F1 penalises precision against "
    "the long source window (f1=0.385). Fails identically at lex_tau 0.65, so "
    "it predates the 2026-08-30 deployment. Fix options are in OPEN-ISSUES and "
    "move the Error-A/Error-B trade-off, so the choice is Sai's. When this "
    "XPASSes, a fix has landed: remove the marker.",
)
def test_short_verbatim_quotation_should_ground(tmp_path: Path) -> None:
    """The user quoted the source exactly, word for word, and was told the
    claim is ungrounded."""
    draft = "PostgreSQL is a relational database management system [S2].\n"
    _assert_clean(_gate(tmp_path, draft), draft)


@pytest.mark.xfail(
    strict=True,
    reason="OI-T2-01 sibling (OPEN): a faithful REORDERING of a source sentence "
    "('... per second in a controlled benchmark on a single node' vs the "
    "source's 'In our controlled benchmark on a single node, Redis sustained "
    "... per second') breaks T1's contiguous span and scores t2_f1=0.513. Also "
    "fails at 0.65. This is the paraphrase class the T3/NLI tier (ADR-004) "
    "exists to recover.",
)
def test_faithful_reordering_should_ground(tmp_path: Path) -> None:
    draft = (
        "Redis sustained approximately 128000 operations per second in a "
        "controlled benchmark on a single node [S1].\n"
    )
    _assert_clean(_gate(tmp_path, draft), draft)


# --- The T2-ONLY region: the blind spot this harness had ---------------------
#
# Found 2026-09-02 by the adversarial challenge on OI-MOAT-21
# (docs/reports/CHALLENGE-2026-09-02-t2-demotion.md, finding (d)). Every honest
# draft above is grounded by T1. So the harness could not observe ANY change to
# T2 — including removing it entirely. An Error-A harness blind to a whole tier
# is not measuring the surface it claims to measure.
#
# Both drafts below are grounded by T2 ALONE (T1 misses, t2_f1 >= lex_tau) and
# contain ZERO novel content tokens — every word is in the cited source, only
# the order and the trimmed material differ. That second property is what makes
# them DISCRIMINATING rather than merely additional:
#
#   * demoting T2 from sufficient-for-GROUNDED turns both RED;
#   * the coverage repair (require the source to contain every claim content
#     token) leaves both GREEN.
#
# The two candidate fixes for OI-MOAT-21 disagree here, so this file now
# separates them. Before it existed, the n=52 corpus scored the coverage repair
# as strictly better while containing no instance of the case it breaks.

T2_ONLY_HONEST = [
    pytest.param(
        "The redesigned coolant pump delivers lower operating temperature than "
        "the previous unit [S1].\n",
        id="t2-only-faithful-trim-factual",
    ),
    pytest.param(
        "Helios Freight moved 3,100 containers in the second quarter [S2].\n",
        id="t2-only-faithful-reorder-numeric",
    ),
]


@pytest.mark.parametrize("draft", T2_ONLY_HONEST)
def test_t2_only_honest_draft_is_not_flagged(tmp_path: Path, draft: str) -> None:
    """An honest claim that only T2 can ground must still reach PASS.

    This is the guard that any change to T2's sufficiency has a visible,
    counted Error-A cost instead of a silent one.
    """
    _assert_clean(_gate(tmp_path, draft, store=T2_STORE), draft)


@pytest.mark.parametrize("draft", T2_ONLY_HONEST)
def test_t2_only_drafts_really_are_t2_only(tmp_path: Path, draft: str) -> None:
    """Assert the MECHANISM, not just the verdict.

    Without this, the tests above would keep passing if a future change made
    these claims T1-grounded — and the T2 blind spot would silently reopen
    while the file that exists to close it stayed green.
    """
    sys.path.insert(0, str(REPO_ROOT))
    from scripts.ground_check import (  # noqa: PLC0415
        _LEX_TAU_DEFAULT,
        _content_words,
        _tokenize,
        classify,
        decompose,
        load_store,
        t1_verbatim,
        t2_lexical_score,
    )

    store = load_store(T2_STORE)
    claim = classify(next(iter(decompose(draft))))
    cited = [store[c.strip("[]")] for c in claim.citations]
    assert cited, "fixture drift: the draft's citation no longer resolves"

    assert not t1_verbatim(claim, cited), (
        "fixture drift: T1 now grounds this claim, so it no longer exercises "
        "the T2-only region this test exists to cover."
    )
    f1 = max(t2_lexical_score(claim.text, s.text) for s in cited)
    assert f1 >= _LEX_TAU_DEFAULT, (
        f"fixture drift: t2_f1={f1:.3f} fell below the deployed lex_tau "
        f"{_LEX_TAU_DEFAULT}; the claim is no longer T2-grounded."
    )

    vocab = {t for s in cited for t in _tokenize(s.text)}
    cite_tokens = {c.strip("[]").casefold() for c in claim.citations}
    novel = [
        t for t in _content_words(_tokenize(claim.text))
        if t not in vocab and t not in cite_tokens
    ]
    assert not novel, (
        f"fixture drift: claim introduces token(s) absent from the source "
        f"{novel!r}. The zero-novel-token property is what makes this case "
        f"distinguish T2-demotion from the coverage repair; without it the "
        f"test no longer separates the two candidate fixes for OI-MOAT-21."
    )
