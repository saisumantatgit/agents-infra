"""Round-5 red-team regressions — the OTHER branch of a two-branch decision.

Round 5 (2026-08-30, 50 drafts) found 23 wrongful PASSes over 4 mechanisms, and
named the meta-error behind three of them: **a fix applied to one branch of a
two-branch decision.** ``ground()`` grounds on ``t1_verbatim(...) or
t2_lexical(...)``; round 4 hardened T1 with subject anchoring and per-source
coverage and left T2 — which has no subject anchor, no word order, and no
polarity — exactly as it was. The attacker simply took the other branch.

The headline draft attributes Redis's measured throughput to PostgreSQL and
cites S1. The word "postgresql" does not occur ANYWHERE in S1. T2 grounded it
at 100.0 because content-word F1 over the rest of the sentence cleared
lex_tau.

Full report: docs/plans/reports/RED-TEAM-R5-2026-08-30.md
Every draft below was OBSERVED gate=PASS before its fix.
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
STORE = str(Path(__file__).parent / "fixtures" / "store.jsonl")


def _gate(tmp_path: Path, draft_text: str, lex_tau: str | None = None) -> dict:
    draft = tmp_path / "draft.md"
    draft.write_text(draft_text, encoding="utf-8")
    env = {**os.environ, "PYTHONPATH": str(REPO_ROOT)}
    cmd = [sys.executable, GROUND_CHECK, "--draft", str(draft), "--store", STORE, "--json"]
    if lex_tau is not None:
        cmd += ["--lex-tau", lex_tau]
    result = subprocess.run(cmd, capture_output=True, text=True, env=env)
    assert result.stdout, f"gate produced no stdout.\nstderr: {result.stderr}"
    return json.loads(result.stdout)


# --- R5-01: T2 has no subject, so it grounds cross-entity attribution --------

def test_cross_entity_attribution_must_not_ground_via_t2(tmp_path: Path) -> None:
    """The single most important round-5 finding.

    The claim hands Redis's 128000 ops/sec to PostgreSQL and cites [S1].
    "postgresql" does not appear anywhere in S1 — yet T2's content-word F1 over
    the remaining (genuine) words cleared lex_tau and returned GROUNDED at
    100.0. Cross-entity attribution is not a red-team artefact; it is a
    base-rate LLM failure mode, which makes this the most consequential hole
    found in five rounds.
    """
    draft = (
        "In our controlled benchmark on a single node, PostgreSQL sustained "
        "approximately 128000 operations per second, which was about twelve "
        "times the throughput of the disk-backed alternative under the same "
        "workload [S1].\n"
    )
    report = _gate(tmp_path, draft)
    assert report["gate"] != "PASS", (
        f"R5-01: T2 grounded a subject absent from the cited source "
        f"(score={report['grounding_score']})"
    )


@pytest.mark.parametrize("tau", ["0.65", "0.71", "0.99"])
def test_cross_entity_attribution_blocked_at_every_lex_tau(tmp_path: Path, tau: str) -> None:
    """lex_tau cannot fix this and never could.

    F1 is a RATIO whose denominator includes the claim's own length, and the
    attacker writes the claim. Round 5 produced a variant scoring F1=1.000 by
    reciting the source's whole vocabulary in a false order. A threshold on an
    attacker-controlled ratio is not a soundness test at ANY value — which is
    why the fix is a subject/polarity constraint, not a retune.
    """
    draft = (
        "In our controlled benchmark on a single node, PostgreSQL sustained "
        "approximately 128000 operations per second, which was about twelve "
        "times the throughput of the disk-backed alternative under the same "
        "workload [S1].\n"
    )
    assert _gate(tmp_path, draft, lex_tau=tau)["gate"] != "PASS"


def test_polarity_flip_must_not_ground(tmp_path: Path) -> None:
    """A negated restatement shares nearly all its content words with the
    source it contradicts, so a bag-of-words tier scores it as agreement."""
    draft = (
        "Redis never sustained approximately 128000 operations per second in "
        "our controlled benchmark on a single node [S1].\n"
    )
    report = _gate(tmp_path, draft)
    assert report["gate"] != "PASS", (
        f"R5-01b: polarity flip grounded (score={report['grounding_score']})"
    )


# --- R5-03: a two-word absence subject switches both checks off --------------

def test_two_word_absence_subject_must_not_self_certify(tmp_path: Path) -> None:
    """`There are no throughput figures.` — against a store whose every source
    reports throughput figures — returned ABSENCE_SUPPORTED, PASS, exit 0.

    A 2-content-word subject sits in the gap between two rules: it is not
    "specific", so the query side needs only the head noun ("throughput",
    present in both session queries); and the contradiction side DID require a
    corroborator ("figures", absent from every source), so it could never fire.
    The two sides disagreed about what "specific" means, and the attacker stood
    in the disagreement.
    """
    report = _gate(tmp_path, "There are no throughput figures.\n")
    assert report["gate"] != "PASS", (
        f"R5-03: absence of the thing every source reports was certified "
        f"(score={report['grounding_score']})"
    )


# --- R5-04: punctuation defeats the header verb test ------------------------

def test_punctuated_header_assertion_must_not_escape(tmp_path: Path) -> None:
    """`### PostgreSQL Corrupts, Data` escapes while `### PostgreSQL Corrupts
    Data` is caught: the verb-suffix test ran on RAW tokens, so a trailing
    comma made "corrupts," not end in "s"."""
    anchor = (
        "Redis sustained approximately 128000 operations per second, which was "
        "about twelve times the throughput of the disk-backed alternative "
        "under the same workload [S1].\n\n"
    )
    report = _gate(tmp_path, anchor + "### PostgreSQL Corrupts, Data\n")
    scored = report["scored_claims"]
    assert report["gate"] != "PASS" or scored > 1, (
        f"R5-04: punctuated header assertion escaped the denominator "
        f"(scored={scored}, gate={report['gate']})"
    )


# --- OI-MOAT-21: the residue that is NOT mine to close -----------------------

@pytest.mark.xfail(
    strict=True,
    reason="OI-MOAT-21 (OPEN, escalated to Sai 2026-08-30): T2's soundness, "
    "not a T2 bug. `ground()` accepts `t1_verbatim(...) OR t2_lexical(...)`, "
    "so T2 alone is sufficient for GROUNDED — and T2 is a content-word F1 "
    "RATIO whose denominator is the claim's own length, which the author "
    "writes. Round 5 produced a draft scoring F1=1.000 by reciting all of S1's "
    "vocabulary in a false order; no lex_tau rejects it. The misattribution "
    "and polarity constraints added on 2026-08-30 close the cases where the "
    "session retrieved the other entity or the polarity flipped; they do not "
    "make a bag-of-words ratio a soundness test, and cannot. Round 5's "
    "recommendation: DEMOTE T2 from sufficient-for-GROUNDED (e.g. to a "
    "corroborating signal, or gate it behind an order/structure check). That "
    "changes what the gate MEANS and invalidates the calibration lex_tau is "
    "derived from — Escalation #1 and #3, Sai's call, not an agent's. "
    "When this XPASSes, a fix has landed: remove the marker.",
)
def test_reordered_full_vocabulary_recitation_must_not_ground(tmp_path: Path) -> None:
    """The claim uses S1's own words, in an order that reverses its meaning.

    Every content token is covered by the cited source, so the misattribution
    check cannot fire; polarity is unflipped, so that check cannot fire; and
    the F1 ratio is maximal. Word ORDER is the only thing that distinguishes
    this from the truth, and T2 has no model of order at all.
    """
    draft = (
        "In our controlled benchmark on a single node, the disk-backed "
        "alternative sustained approximately 128000 operations per second, "
        "which was about twelve times the throughput of Redis under the same "
        "workload [S1].\n"
    )
    report = _gate(tmp_path, draft)
    assert report["gate"] != "PASS", (
        f"OI-MOAT-21: order-only falsehood grounded (score={report['grounding_score']})"
    )


@pytest.mark.parametrize("tau", ["0.71", "0.76", "0.83"])
def test_oi_moat_21_is_not_closed_by_raising_lex_tau(tmp_path: Path, tau: str) -> None:
    """Guards the CONCLUSION, not just the instance.

    On 2026-09-02 the CR-002 deployment (0.71 -> 0.76) made the previous
    OI-MOAT-21 draft XPASS, because that particular draft scored f1=0.7391 and
    the threshold simply stepped over it. Nothing was fixed. Treating that as
    closure would have been the exact "green test as proof" failure this repo
    bans — a tripwire going quiet for a reason unrelated to the defect.

    This test pins the real claim: the hole is threshold-INDEPENDENT. The
    attacker adds matching vocabulary until the ratio clears whatever bar is
    set, because F1's denominator is the claim's own length and the attacker
    writes the claim. If this ever fails, lex_tau did NOT close OI-MOAT-21 —
    something structural did, and that is worth checking before celebrating.
    """
    draft = (
        "In our controlled benchmark on a single node, the disk-backed "
        "alternative sustained approximately 128000 operations per second, "
        "which was about twelve times the throughput of Redis under the same "
        "workload [S1].\n"
    )
    assert _gate(tmp_path, draft, lex_tau=tau)["gate"] == "PASS", (
        f"OI-MOAT-21 appears closed at lex_tau={tau}. If a STRUCTURAL fix "
        "landed, delete this test and the xfail above. If only the threshold "
        "moved, the hole is still open and this draft needs more vocabulary."
    )
