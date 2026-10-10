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


def test_cross_entity_attribution_blocked_without_any_threshold(tmp_path: Path) -> None:
    """lex_tau could not fix this, and there is no longer a lex_tau to try.

    This test was parametrized over lex_tau 0.65 / 0.71 / 0.99 to pin the
    conclusion that a threshold on an attacker-controlled RATIO is not a
    soundness test at any value. ADR-006 discharged that conclusion the hard
    way: T2 was demoted from sufficient-for-GROUNDED, so no threshold exists to
    sweep and `--lex-tau` is a hard error.

    The draft is retained unparametrized because the ATTACK is still real —
    cross-entity attribution is a base-rate LLM failure, not a red-team
    artefact — and it must stay blocked under whatever tiers exist.
    """
    draft = (
        "In our controlled benchmark on a single node, PostgreSQL sustained "
        "approximately 128000 operations per second, which was about twelve "
        "times the throughput of the disk-backed alternative under the same "
        "workload [S1].\n"
    )
    assert _gate(tmp_path, draft)["gate"] != "PASS"


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


# test_oi_moat_21_is_not_closed_by_raising_lex_tau — DELETED 2026-09-02.
#
# It asserted that the hole stays open at lex_tau 0.71 / 0.76 / 0.83, pinning
# the CONCLUSION that OI-MOAT-21 was threshold-independent. Its own docstring
# named the condition for removing it: "If a STRUCTURAL fix landed, delete this
# test and the xfail above."
#
# One landed. ADR-006 demoted T2 from sufficient-for-GROUNDED, so lex_tau
# governs no verdict and `--lex-tau` is now a hard error — the test could not
# run even in principle. The conclusion it guarded was right and is now
# discharged: the threshold never could have closed this, and a structural
# change is what did.
