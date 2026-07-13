"""Round-2 red-team regressions — evasions of the 2026-07-12 moat fixes.

The 2026-07-12 fixes were REAL but NARROW. Round 2 (2026-07-14) found that the
rate-qualifier comparison recognized only ``per <word>`` / ``/<word>`` forms
within a two-word window, and that the absence discriminating-anchor rule
leaked for entity-free subjects in sessions with fewer than 3 distinct queries.
Every draft below was observed gate=PASS against the frozen store BEFORE the
round-2 fix (red evidence in the 2026-07-14 logbook; drafts reproduced from
docs/plans/reports/RED-TEAM-R2-2026-07-14.md).

These are permanent green guards: each asserts the CORRECT behavior
(gate != PASS), each was seen red first (INS-005).

Scope note — these fixes COMPLETE Sai's 2026-07-12 rulings (AA-MOAT-001
"compare value AND dimensional unit; fail-closed on any unit/quantity
mismatch"; AA-MOAT-004 "anchor absence on discriminating tokens; treat
majority-present corpus words as non-discriminating") rather than making a new
Error-A/Error-B decision. The one genuinely NEW class found in round 2 —
verbless NON_CLAIM smuggling (AA-MOAT-007) — is RECORDED, NOT FIXED, and is
covered by a strict-xfail below pending Sai's ruling.
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

# Frozen store (do not restate elsewhere):
#   S1 — "...Redis sustained approximately 128000 operations per second..."
#   S2 — "...PostgreSQL sustained approximately 11000 write operations per second..."
# Every draft below asserts something the store does NOT support.

RATE_EVASIONS = [
    pytest.param(
        "Redis is an in-memory data structure store, sustaining 128000 "
        "operations each minute [S1].",
        id="R2-rate-each-minute",
    ),
    pytest.param(
        "Redis is an in-memory data structure store, sustaining 128000 "
        "operations every minute [S1].",
        id="R2-rate-every-minute",
    ),
    pytest.param(
        "Redis is an in-memory data structure store, sustaining 128000 "
        "operations a minute [S1].",
        id="R2-rate-a-minute",
    ),
    pytest.param(
        "Redis is an in-memory data structure store, at a per-minute rate of "
        "128000 operations [S1].",
        id="R2-rate-qualifier-before-number",
    ),
    pytest.param(
        "Redis is an in-memory data structure store, sustaining 128000 "
        "operations per-minute [S1].",
        id="R2-rate-hyphenated",
    ),
    pytest.param(
        # Cyrillic 'р' (U+0440) in "рer" — NFKC does NOT fold this; the
        # confusables fold in the numeric-context extractor must.
        "Redis is an in-memory data structure store, sustaining 128000 "
        "operations рer minute [S1].",
        id="R2-rate-cyrillic-homoglyph",
    ),
    pytest.param(
        "Redis is an in-memory data structure store, sustaining 128000 "
        "write operations for the cluster per minute [S1].",
        id="R2-rate-qualifier-far-from-number",
    ),
]

QUANTITY_SWAPS = [
    pytest.param(
        "Redis is an in-memory data structure store, sustaining 128000 "
        "gigabytes per second [S1].",
        id="R2-quantity-gigabytes",
    ),
    pytest.param(
        "Redis is an in-memory data structure store, sustaining 128000 "
        "users per second [S1].",
        id="R2-quantity-users",
    ),
]

ABSENCE_LEAKS = [
    pytest.param(
        "There is no benchmark for the streaming ingest workload.",
        id="R2-absence-generic-headnoun",
    ),
    pytest.param(
        "There is no throughput ceiling for the streaming ingest workload.",
        id="R2-absence-generic-headnoun-2",
    ),
]


def _gate(tmp_path: Path, draft_text: str) -> dict:
    draft = tmp_path / "draft.md"
    draft.write_text(draft_text, encoding="utf-8")
    env = {**os.environ, "PYTHONPATH": str(REPO_ROOT)}
    result = subprocess.run(
        [sys.executable, GROUND_CHECK, "--draft", str(draft), "--store", STORE, "--json"],
        capture_output=True,
        text=True,
        env=env,
    )
    assert result.stdout, f"gate produced no stdout.\nstderr: {result.stderr}"
    return json.loads(result.stdout)


@pytest.mark.parametrize("draft_text", RATE_EVASIONS)
def test_rate_qualifier_evasion_must_not_pass(tmp_path: Path, draft_text: str) -> None:
    """A wrong rate denominator, however phrased, must not gate PASS.

    The store says 128000 operations per SECOND. Every phrasing here asserts a
    per-MINUTE rate; the gate must refuse to certify it regardless of the
    surface form (each/every/a/hyphenated/before-the-number/far/homoglyph).
    """
    report = _gate(tmp_path, draft_text)
    assert report["gate"] != "PASS", (
        f"rate evasion wrongly PASSed (score={report['grounding_score']}, "
        f"retained={len(report['retained_appendix'])}): {draft_text!r}"
    )


@pytest.mark.parametrize("draft_text", QUANTITY_SWAPS)
def test_quantity_noun_swap_must_not_pass(tmp_path: Path, draft_text: str) -> None:
    """The measured quantity is part of the dimensional unit: 128000
    GIGABYTES/sec is not grounded by 128000 OPERATIONS/sec."""
    report = _gate(tmp_path, draft_text)
    assert report["gate"] != "PASS", (
        f"quantity swap wrongly PASSed (score={report['grounding_score']}): "
        f"{draft_text!r}"
    )


@pytest.mark.parametrize("draft_text", ABSENCE_LEAKS)
def test_generic_headnoun_absence_must_not_pass(tmp_path: Path, draft_text: str) -> None:
    """An entity-free absence claim whose subject content the session never
    searched must not be ABSENCE_SUPPORTED — the store's two queries mention
    'benchmark'/'throughput' but nothing about a streaming ingest workload."""
    report = _gate(tmp_path, draft_text)
    assert report["gate"] != "PASS", (
        f"generic head-noun absence wrongly PASSed: {draft_text!r}"
    )


# --- OPEN: AA-MOAT-007, recorded not fixed (awaiting Sai) ---------------------

@pytest.mark.xfail(
    strict=True,
    reason="AA-MOAT-007 (OPEN, blocked on Sai): a verbless colon-form "
    "assertion classifies NON_CLAIM, is excluded from the scored denominator, "
    "and rides inside a PASS. Fixing it changes WHAT COUNTS AS A CLAIM — an "
    "Error-A/Error-B decision no existing ruling covers (Escalation rule #1). "
    "When this XPASSes, a fix has landed: remove the marker.",
)
def test_verbless_nonclaim_smuggle_must_not_pass(tmp_path: Path) -> None:
    """A fabricated superlative written verblessly ('Redis: unquestionably the
    fastest datastore in all of human history.') is classified NON_CLAIM and
    therefore never scored — the draft PASSes carrying it."""
    report = _gate(
        tmp_path,
        "Redis is an in-memory data structure store used as a database and "
        "cache [S1].\n\n"
        "Redis: unquestionably the fastest datastore in all of human history.\n",
    )
    assert report["gate"] != "PASS", (
        "AA-MOAT-007: verbless fabrication rode inside a PASS "
        f"(score={report['grounding_score']})"
    )
