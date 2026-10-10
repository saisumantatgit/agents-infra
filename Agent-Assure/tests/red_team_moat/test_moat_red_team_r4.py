"""Round-4 red-team regressions — evasions of the round-3 fixes.

Round 4 (2026-08-30) ran 41 drafts against the tree round 3 had just hardened
and found 25 wrongful PASSes over 4 mechanisms — **every one an evasion of a
fix landed the same day.** Rounds 1->2->3->4 have now each broken the previous
round's work, which is why "a fix to the moat gets red-teamed too" is a law
here and not a suggestion.

Round 4's cross-cutting diagnosis is the important part, and it is recorded in
CLAUDE.md as a convention: **three of the four findings are one anti-pattern —
an absent or unreadable field read as "unconstrained" by a gate whose entire
job is to constrain.** `NON_CLAIM` and `None` were both catch-alls pointing
toward PASS. Every "I could not tell" must point AWAY from PASS.

Full report: docs/plans/reports/RED-TEAM-R4-2026-08-30.md
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
FIXTURES = Path(__file__).parent / "fixtures"
STORE = str(FIXTURES / "store.jsonl")

_ANCHOR = (
    "Redis sustained approximately 128000 operations per second, which was "
    "about twelve times the throughput of the disk-backed alternative under "
    "the same workload [S1].\n\n"
)


def _gate(tmp_path: Path, draft_text: str) -> dict:
    draft = tmp_path / "draft.md"
    draft.write_text(draft_text, encoding="utf-8")
    env = {**os.environ, "PYTHONPATH": str(REPO_ROOT)}
    result = subprocess.run(
        [sys.executable, GROUND_CHECK, "--draft", str(draft), "--store", STORE, "--json"],
        capture_output=True, text=True, env=env,
    )
    assert result.stdout, f"gate produced no stdout.\nstderr: {result.stderr}"
    return json.loads(result.stdout)


# --- RT4-01: case is an attacker-controlled bit ------------------------------

RT4_01_CASE_SMUGGLES = [
    pytest.param("PostgreSQL Fails.", id="RT4-01-title-case-body"),
    pytest.param("### Redis Loses Data", id="RT4-01-title-case-header"),
    pytest.param("REDIS CORRUPTS WRITES.", id="RT4-01-all-caps"),
    pytest.param("PostgreSQL: Catastrophic Data Loss.", id="RT4-01-title-case-colon"),
]


@pytest.mark.parametrize("smuggle", RT4_01_CASE_SMUGGLES)
def test_capitalisation_must_not_buy_a_denominator_exit(tmp_path: Path, smuggle: str) -> None:
    """Round 3 replaced a token COUNT with a proper-noun test, and round 4
    beat it with the Shift key.

    `_has_finite_verb` skipped capitalised tokens (a proper-noun heuristic), so
    "PostgreSQL Fails." had no detectable verb; the verbless branch then asked
    whether all content words were capitalised, which Title Case guarantees.
    Both of round 3's structural tests keyed on case, and case is one bit per
    word that the attacker owns outright.
    """
    report = _gate(tmp_path, _ANCHOR + smuggle + "\n")
    assert report["gate"] != "PASS", (
        f"RT4-01: capitalisation bought a denominator exit "
        f"(score={report['grounding_score']}, scored={report['scored_claims']}): {smuggle!r}"
    )


# --- RT4-02: the thinnest possible absence -----------------------------------

RT4_02_THIN_ABSENCES = [
    pytest.param("No benchmark.", id="RT4-02-two-word-document"),
    pytest.param("There is no throughput.", id="RT4-02-single-content-word"),
]


@pytest.mark.parametrize("draft", RT4_02_THIN_ABSENCES)
def test_subject_too_thin_to_check_must_not_be_supported(tmp_path: Path, draft: str) -> None:
    """`No benchmark.` — the ENTIRE document — returned ABSENCE_SUPPORTED,
    gate PASS, exit 0, against a store consisting of nothing but benchmarks.

    Round 3's content-contradiction check requires the head noun AND one other
    subject content word in a source sentence. With a one-content-word subject
    there IS no other word, so `any(...)` over an empty set is vacuously False
    and the check silently declines to run — the failure mode being an absent
    field read as "no objection" instead of "cannot verify".
    """
    report = _gate(tmp_path, draft + "\n")
    assert report["gate"] != "PASS", (
        f"RT4-02: unverifiable absence certified (score={report['grounding_score']}): {draft!r}"
    )


# --- RT4-03: subject swap inside one source ----------------------------------

def test_subject_swap_within_one_source_must_not_ground(tmp_path: Path) -> None:
    """Round 3 made coverage per-source, which killed the union-widening
    attack but left the residue: coverage is still SET MEMBERSHIP, and a set
    has no notion of who did what to whom.

    Every content token below is in S1, and an 8-token span is verbatim — but
    the claim reverses the subjects, attributing Redis's throughput to the
    disk-backed alternative it actually beat.
    """
    draft = (
        "The disk-backed alternative sustained approximately 128000 operations "
        "per second, which was about twelve times the throughput of Redis [S1].\n"
    )
    report = _gate(tmp_path, draft)
    assert report["gate"] != "PASS", (
        f"RT4-03: subject swap grounded (score={report['grounding_score']})"
    )


def test_honest_quote_still_grounds_after_subject_anchoring(tmp_path: Path) -> None:
    """Error-A boundary for RT4-03: the honest quotation must survive."""
    report = _gate(tmp_path, _ANCHOR)
    assert report["gate"] == "PASS", (
        f"honest verbatim quote no longer grounds: {report['per_claim']}"
    )


# --- RT4-04: deleting the rate deletes the check -----------------------------

def test_rate_free_restatement_of_a_rate_must_not_ground(tmp_path: Path) -> None:
    """S1 reports 128000 operations PER SECOND. The draft restates it as a
    total for the benchmark — a throughput misreported as a count, understating
    the measurement by the run's duration.

    `claim_rate=None` was read as "the claim asserts no rate, so impose no
    constraint". Omitting the rate therefore DELETED the dimensional check that
    OI-MOAT-01/-09/-15 exist to enforce: the third instance of absent-field-as-
    permission in one round.
    """
    draft = (
        "Redis sustained approximately 128000 operations in our controlled "
        "benchmark on a single node under the same workload [S1].\n"
    )
    report = _gate(tmp_path, draft)
    assert report["gate"] != "PASS", (
        f"RT4-04: rate-free restatement of a rate grounded "
        f"(score={report['grounding_score']})"
    )


# --- OI-MOAT-20: KNOWN OPEN residue, recorded not hidden ---------------------

@pytest.mark.xfail(
    strict=True,
    reason="OI-MOAT-20 (OPEN, 2026-08-30): a verb-FINAL header "
    "('### PostgreSQL Fails') still reads structural. The header rule scores a "
    "header whose verb-like token is not its final content token — the "
    "positional signal that separates an assertion ('Redis LOSES Data') from a "
    "heading ('Key Findings') without keying on case or on a token count. A "
    "verb-final header defeats it. Closing it means either scoring every "
    "multi-word heading (Error-A on ordinary documents, which gets the tool "
    "switched off — itself a moat failure) or a real POS tagger, which is a "
    "dependency and a design decision. Recorded with this tripwire rather than "
    "left silent. When this XPASSes, a fix has landed: remove the marker.",
)
def test_verb_final_header_must_not_escape_denominator(tmp_path: Path) -> None:
    """The documented residue of the RT4-01 header rule."""
    report = _gate(tmp_path, _ANCHOR + "### PostgreSQL Fails\n")
    assert report["gate"] != "PASS", (
        f"OI-MOAT-20: verb-final header rode inside a PASS "
        f"(score={report['grounding_score']})"
    )
