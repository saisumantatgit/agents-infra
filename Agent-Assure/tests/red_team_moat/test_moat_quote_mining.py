"""Quote-mining — the hole exact containment opens, and its guard.

Demoting T2 (ADR-006) left T1 as the only path to GROUNDED, and T1 needs an
8-token contiguous span. 31 of the 52 calibration claims are shorter than that,
and so was the gate's own end-to-end fixture: source "Redis handles 100K ops per
second", claim quoting it word for word, verdict UNGROUNDED. Exact containment
(the claim IS the span, any length) fixes that soundly — an attacker cannot
fabricate by exact quotation, because doing so means giving up the fabrication.

But it opens ONE new attack that a long span makes impractical: lifting a short
span out of the clause that governs it. "Critics claim Redis is slow" contains
"Redis is slow". "It is not true that the cache loses data" contains "the cache
loses data". The source is REPORTING or DENYING the statement; quoting the span
alone reverses what it said.

_span_is_hedged is the guard. Every test below was written BEFORE it was
trusted, and the guard was mutation-checked by disabling it and watching these
go red. The A-side tests (honest short quotes that must still ground) are as
important as the attacks: a guard that refuses every short quote would "close"
this by reintroducing the bug exact containment exists to fix.
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
STORE = str(Path(__file__).parent / "fixtures" / "store_containment.jsonl")


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


# --- The attacks: a span lifted out of the clause that governs it ------------

MINED = [
    pytest.param("Redis is slow [S2].\n", "attribution: 'Critics claim ...'",
                 id="mined-from-attribution"),
    pytest.param("The cache loses data on restart [S3].\n",
                 "denial: 'It is not true that ...'", id="mined-from-denial"),
    pytest.param("The cluster loses quorum [S5].\n",
                 "conditional: 'If ..., writes are rejected'",
                 id="mined-from-conditional"),
]


@pytest.mark.parametrize("draft,governing", MINED)
def test_quote_mined_span_must_not_ground(
    tmp_path: Path, draft: str, governing: str
) -> None:
    """The source contains these words in this order — and does not say them."""
    report = _gate(tmp_path, draft)
    assert report["gate"] != "PASS", (
        f"quote-mining: gate PASSed a span lifted out of a {governing} clause; "
        f"score={report['grounding_score']}"
    )


# --- The other direction: honest short quotes must still ground --------------

def test_short_exact_quote_still_grounds(tmp_path: Path) -> None:
    """OI-T2-01's case, and the reason exact containment exists. A guard that
    broke this would have 'closed' quote-mining by restoring the bug."""
    report = _gate(tmp_path, "Redis handles 100K ops per second [S1].\n")
    assert report["gate"] == "PASS", (
        f"an exact short quotation was flagged (gate={report['gate']}). "
        f"The hedge guard has over-reached."
    )


def test_hedge_in_a_different_source_does_not_block(tmp_path: Path) -> None:
    """S4 hedges the appliance claim ('According to the vendor'); S6 asserts it
    outright. Citing S6 must ground — the guard is per-span, not per-topic."""
    report = _gate(tmp_path, "The appliance ships with dual power supplies [S6].\n")
    assert report["gate"] == "PASS", (
        f"a hedge in an UNCITED source blocked an asserted claim "
        f"(gate={report['gate']})"
    )
