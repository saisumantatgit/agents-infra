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

2026-07-12 update (Sai's ruling): ADR-005 (empty-appendix hard-cap) ACCEPTED;
numeric-unit and absence-anchoring fixes GREENLIT and landed. Their four tests
flipped XPASS and are now permanent green guards (MOAT_GUARDS). AA-MOAT-003
(T1 overreach) and AA-MOAT-005 (relational predicate) remain OPEN by the same
ruling — still strict xfail. Do NOT remove a remaining xfail marker without
the corresponding fix + calibration re-run + new CR (Escalation rule #1).
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


# --- CLOSED violations: permanent green guards -------------------------------
# Each was proven red pre-fix (strict xfail, seen failing on this branch —
# INS-005 satisfied) and flipped to XPASS when its fix landed on 2026-07-12
# under Sai's ruling (ADR-005 accepted; numeric-unit + absence-anchoring
# fixes greenlit). Markers removed per the harness protocol.
# fixture stem -> (open-issue id, fix, one-line original mechanism)
MOAT_GUARDS = [
    pytest.param(
        "numeric-drift-unit_1",
        "AA-MOAT-001",
        "FIXED (rate-qualifier comparison in numeric_ok): 'operations per "
        "minute' no longer grounds against 'per second'.",
        id="AA-MOAT-001-numeric-drift-unit",
    ),
    pytest.param(
        "numeric-drift-decimal_4",
        "AA-MOAT-002",
        "FIXED (ADR-005 empty-appendix hard-cap): a retained "
        "UNVERIFIED_NUMBER can no longer ride inside a >=90% PASS.",
        id="AA-MOAT-002-numeric-drift-decimal-dilution",
    ),
    pytest.param(
        "unsubstantiated-absence_1",
        "AA-MOAT-004",
        "FIXED (discriminating-anchor absence check): entity/numeric anchors "
        "of the negated subject must all appear in the supporting queries.",
        id="AA-MOAT-004-unsubstantiated-absence",
    ),
    pytest.param(
        "letter-suffixed-source-id_5",
        "AA-MOAT-006",
        "FIXED (ADR-005 empty-appendix hard-cap): the retained UNCITED [S1a] "
        "claim blocks PASS regardless of the 90.0 score.",
        id="AA-MOAT-006-letter-suffixed-dilution",
    ),
]

# --- OPEN violations: still xfail, deferred by Sai's 2026-07-12 ruling --------
# fixture stem -> (open-issue id, root cause, one-line mechanism)
MOAT_VIOLATIONS = [
    pytest.param(
        "paraphrase-overreach_1",
        "AA-MOAT-003",
        "Root B: a verbatim >=8-token span short-circuits T1; the surrounding "
        "fabricated superlative ('single fastest database ever engineered') is "
        "never checked.",
        id="AA-MOAT-003-paraphrase-overreach",
    ),
    pytest.param(
        "unsupported-relation_3",
        "AA-MOAT-005",
        "Root B: the two-source relational rule checks endpoint-noun presence, "
        "not support for the relation/predicate ('decisively outperforming').",
        id="AA-MOAT-005-unsupported-relation",
    ),
]


def _assert_not_pass(stem: str, issue_id: str, mechanism: str) -> None:
    draft = str(FIXTURES / f"{stem}.md")
    report = _gate(draft)
    assert report["gate"] != "PASS", (
        f"{issue_id}: gate wrongly returned PASS "
        f"(score={report.get('grounding_score')}, "
        f"retained_appendix={len(report.get('retained_appendix', []))}). "
        f"{mechanism}"
    )


@pytest.mark.parametrize("stem, issue_id, mechanism", MOAT_GUARDS)
def test_fixed_fabrication_stays_blocked(stem: str, issue_id: str, mechanism: str) -> None:
    """Permanent green guard: a CLOSED moat violation must stay closed.
    A failure here is a regression of a fixed Error-B hole — release blocker."""
    _assert_not_pass(stem, issue_id, mechanism)


@pytest.mark.parametrize("stem, issue_id, mechanism", MOAT_VIOLATIONS)
@pytest.mark.xfail(
    strict=True,
    reason="OPEN moat violation (Error-B), deferred by Sai's 2026-07-12 "
    "ruling (T1 residual-coverage interacts with Phase-2b NLI design; "
    "relational predicate check needs its own decision). When this XPASSes, "
    "a fix has landed: remove the marker and move the param to MOAT_GUARDS.",
)
def test_fabrication_must_not_pass(stem: str, issue_id: str, mechanism: str) -> None:
    """The gate MUST NOT certify a draft containing a fabricated/unsupported
    claim as PASS. Reproduced by hand 2026-07-12; see ``mechanism``."""
    _assert_not_pass(stem, issue_id, mechanism)
