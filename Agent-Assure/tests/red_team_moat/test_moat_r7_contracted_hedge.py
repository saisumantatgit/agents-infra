"""OI-MOAT-25 — an apostrophe defeats the quote-mining guard.

ROUND 7, path C. The single sharpest finding of any round so far, because the
evasion is ONE CHARACTER and the guard it defeats was shipped three days ago.

`_span_is_hedged` refuses a contained span when an attribution or denial token
sits within 5 tokens before it. Its fixture — and every test written for it —
spells the denial "It is not true that ...". `_tokenize` is `\\w+`, so it splits
"isn't" into ["isn", "t"]. Neither piece is in `_SPAN_HEDGE_TOKENS`, which
contains "not" but no contracted form. The denial becomes invisible.

    source "It is not true that the cache loses data on restart."  -> FAIL
    source "It isn't true that the cache loses data on restart."   -> PASS, 100.0

Same denial, same claim, same gate. This is the project's own law firing again:
NEVER key a moat rule on a surface property the author controls. Rounds 3 and 4
killed a token-count rule with a short fabrication and its capitalisation
replacement with the Shift key. This one is the apostrophe.

THE FIX IS SYSTEMIC, NOT A LONGER LIST. Adding "isn", "haven", "doesn" … to
_SPAN_HEDGE_TOKENS closes these fixtures and leaves the class open — which is
what every previous narrow fix did. The root cause is that tokenization
DESTROYS the negation before any guard can see it, so the repair belongs at the
tokenizer: expand the "n't" suffix to " not" before tokenizing, one rule
covering every contracted negation there is, so the existing hedge list and
_ABSENCE_NEGATION_RE both see what the source actually said.

These tests are strict xfails: they are the OPEN Error-B, counted. They XPASS
the moment the tokenizer is repaired — remove the marker then.
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
STORE = str(Path(__file__).parent / "fixtures" / "store_contraction.jsonl")


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


def _verdict(report: dict) -> str:
    scored = [c for c in report["per_claim"] if c["kind"] != "NON_CLAIM"]
    assert len(scored) == 1, f"expected one scored claim, got {scored}"
    return scored[0]["verdict"]


CONTRACTED = [
    pytest.param(
        "The cache loses data on restart [S1].\n",
        id="denial-contracted-isnt",
    ),
    pytest.param(
        "Redis is slow under sustained load [S2].\n",
        id="denial-contracted-havent",
    ),
]

UNCONTRACTED = [
    pytest.param(
        "The cache loses data on restart [S3].\n",
        id="denial-spelled-out-is-not",
    ),
    pytest.param(
        "Redis is slow under sustained load [S4].\n",
        id="denial-spelled-out-have-not",
    ),
]


@pytest.mark.xfail(
    strict=True,
    reason="OI-MOAT-25 OPEN: _tokenize splits \"isn't\" into ['isn','t'], so the "
    "denial is invisible to _span_is_hedged and the mined span grounds. Error-B. "
    "Closes when the n't suffix is expanded before tokenizing.",
)
@pytest.mark.parametrize("draft", CONTRACTED)
def test_contracted_denial_must_not_ground(tmp_path: Path, draft: str) -> None:
    """The source DENIES the claim. Certifying it is the unrecoverable error."""
    assert _verdict(_gate(tmp_path, draft)) != "GROUNDED"


@pytest.mark.parametrize("draft", UNCONTRACTED)
def test_uncontracted_denial_does_not_ground(tmp_path: Path, draft: str) -> None:
    """The control, and the reason the above is a one-character evasion.

    Identical denial, identical claim, apostrophe removed. This one the guard
    catches. If this test ever fails, the guard has regressed outright and the
    xfail above stops being evidence of anything.
    """
    assert _verdict(_gate(tmp_path, draft)) != "GROUNDED"


def test_honest_short_quote_still_grounds(tmp_path: Path) -> None:
    """The mirror, and the reason the fix must not be 'refuse short quotes'.

    S5 asserts the claim plainly, with no hedge anywhere. Exact containment
    exists to ground exactly this, and OI-T2-01 is the bug that appears if a
    guard over-reaches. Any repair to OI-MOAT-25 must leave this green.
    """
    draft = "The appliance ships with dual power supplies [S5].\n"
    assert _verdict(_gate(tmp_path, draft)) == "GROUNDED"
