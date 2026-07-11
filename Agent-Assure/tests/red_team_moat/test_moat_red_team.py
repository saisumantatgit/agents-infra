"""Proven-red regression harness — the six confirmed moat violations.

Source: the 2026-07-12 adversarial red-team sweep (26-agent workflow), every
finding independently reproduced by hand against this branch's gate. Full
narrative in ``docs/case-narratives/CN-ADR005-The-Ninety-Percent-Moat.md``;
per-finding detail and fix sketches in ``docs/open-issues/OPEN-ISSUES.md``.

Each fixture draft below gate-**PASSes today when it MUST NOT** — a fabrication
certified as PASS, i.e. an Error-B event, the unrecoverable class under the
pinned asymmetric invariant (CLAUDE.md "Moat-integrity is an INVARIANT").

Why ``strict xfail`` and not a plain failing test:
  * The assertion states the CORRECT behavior (``gate != "PASS"``).
  * It FAILS against current code — that is the proof the hole is real
    (INS-005: a regression test must be seen red before it is coverage).
  * ``strict=True`` means the day a fix lands, the test XPASSes and pytest
    reports that XPASS as a FAILURE — forcing whoever fixes the gate to come
    here, delete the marker, and turn this into a permanent green guard.
  * Marking them xfail (not fail) keeps the main suite green while the fixes
    remain blocked on Sai — the findings are recorded, not papered over.

This file RECORDS. It does not fix. Every fix alters the Error-A/Error-B
trade-off or the gate score bar => Escalation rule #1 => Sai adjudication
(see docs/adr/ADR-005-gate-retained-appendix-hard-cap.md). Do NOT remove an
xfail marker without the corresponding fix + calibration re-run + new CR.
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


def _gate(draft: str) -> dict:
    """Invoke the deterministic gate exactly as the CLI does, under the same
    uv-managed interpreter as pytest (mirrors tests/test_demo_golden.py)."""
    env = {**os.environ, "PYTHONPATH": str(REPO_ROOT)}
    result = subprocess.run(
        [sys.executable, GROUND_CHECK, "--draft", draft, "--store", STORE, "--json"],
        capture_output=True,
        text=True,
        env=env,
    )
    assert result.stdout, f"gate produced no stdout.\nstderr: {result.stderr}"
    return json.loads(result.stdout)


# fixture stem -> (open-issue id, root cause, one-line mechanism)
MOAT_VIOLATIONS = [
    pytest.param(
        "numeric-drift-unit_1",
        "AA-MOAT-001",
        "Root B: numeric token compares magnitude, not the dimensional unit; "
        "'operations per minute' grounds against 'per second'.",
        id="AA-MOAT-001-numeric-drift-unit",
    ),
    pytest.param(
        "numeric-drift-decimal_4",
        "AA-MOAT-002",
        "Root A: 9 grounded + 1 drifted-number claim = score 90.0 >= 90; the "
        "retained UNVERIFIED_NUMBER rides inside a PASS (threshold-dilution).",
        id="AA-MOAT-002-numeric-drift-decimal-dilution",
    ),
    pytest.param(
        "paraphrase-overreach_1",
        "AA-MOAT-003",
        "Root B: a verbatim >=8-token span short-circuits T1; the surrounding "
        "fabricated superlative ('single fastest database ever engineered') is "
        "never checked.",
        id="AA-MOAT-003-paraphrase-overreach",
    ),
    pytest.param(
        "unsubstantiated-absence_1",
        "AA-MOAT-004",
        "Root B: absence grounding anchors on the head noun / generic corpus "
        "words present in query_provenance, not the negated proposition's "
        "discriminating tokens.",
        id="AA-MOAT-004-unsubstantiated-absence",
    ),
    pytest.param(
        "unsupported-relation_3",
        "AA-MOAT-005",
        "Root B: the two-source relational rule checks endpoint-noun presence, "
        "not support for the relation/predicate ('decisively outperforming').",
        id="AA-MOAT-005-unsupported-relation",
    ),
    pytest.param(
        "letter-suffixed-source-id_5",
        "AA-MOAT-006",
        "Root A: 9 grounded + 1 fabricated [S1a] claim = score exactly 90.0; "
        "correctly classified as a violation, still cleared the score bar.",
        id="AA-MOAT-006-letter-suffixed-dilution",
    ),
]


@pytest.mark.parametrize("stem, issue_id, mechanism", MOAT_VIOLATIONS)
@pytest.mark.xfail(
    strict=True,
    reason="OPEN moat violation (Error-B), blocked on Sai gate-bar decision "
    "(ADR-005). When this XPASSes, a fix has landed: remove the marker and "
    "make it a permanent green guard.",
)
def test_fabrication_must_not_pass(stem: str, issue_id: str, mechanism: str) -> None:
    """The gate MUST NOT certify a draft containing a fabricated/unsupported
    claim as PASS. Reproduced by hand 2026-07-12; see ``mechanism``."""
    draft = str(FIXTURES / f"{stem}.md")
    report = _gate(draft)
    assert report["gate"] != "PASS", (
        f"{issue_id}: gate wrongly returned PASS "
        f"(score={report.get('grounding_score')}, "
        f"retained_appendix={len(report.get('retained_appendix', []))}). "
        f"{mechanism}"
    )
