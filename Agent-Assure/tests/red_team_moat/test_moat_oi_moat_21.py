"""OI-MOAT-21 — argument substitution: the class no lexical tier can catch.

WHAT THIS FILE DOCUMENTS
------------------------
Round 5 established that T2 (content-word F1 over a source window) has no word
order, no subject anchor and no polarity. This file establishes the sharper
consequence found on 2026-09-02 while adjudicating OI-MOAT-21:

**A true claim and a false claim can be the SAME single-token delta against the
same source, and score an IDENTICAL t2_f1.**

Each pair below shares one source. The A-arm swaps a VERB for a synonym, so the
claim stays true. The B-arm swaps a NOUN ARGUMENT, so the claim becomes false —
"winter trial" becomes "summer trial", "eastern corridor" becomes "western",
"hull inspection" becomes "wing". Measured (uv run python -m
calibration.build_batch_t2), all five pairs score t2_f1 identically:

    p01 0.8889/0.8889   p02 0.8889/0.8889   p03 0.8889/0.8889
    p04 0.8750/0.8750   p05 0.8750/0.8750

There is therefore NO threshold on lex_tau that admits the A-arms and rejects
the B-arms, and no ordering of them for a threshold to exploit. This is not a
tuning gap; it is the ceiling of the lexical method, and it is why the T3/NLI
tier (ADR-004) is not optional.

WHY THE B-ARMS ARE XFAIL AND THE A-ARMS ARE NOT
-----------------------------------------------
The B-arms currently reach gate=PASS. They are marked strict-xfail against
OI-MOAT-21 (ADR-039: an INVARIANT open issue carries a citing tripwire) rather
than deleted or silently accepted — a known Error-B that is counted is a debt;
an uncounted one is a lie. When OI-MOAT-21 is fixed they XPASS and the marker
comes off.

The A-arms assert the opposite direction and must stay PASS. They are the
Error-A guard on the same fix: a repair that closes the B-arms by rejecting
every claim carrying a novel token closes the A-arms too, and this file fails
loudly when it does. The two halves together are what make the candidate fixes
distinguishable — see
docs/decisions/ADJUDICATION-2026-09-02-t2-soundness.md.
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
STORE = str(Path(__file__).parent / "fixtures" / "store_argswap.jsonl")


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


# (pair, verb-synonym claim -> TRUE, argument-swap claim -> FALSE, what changed)
PAIRS = [
    ("p01",
     "The Halden reactor maintained a stable output level throughout the winter trial [S1].\n",
     "The Halden reactor sustained a stable output level throughout the summer trial [S1].\n",
     "winter -> summer"),
    ("p02",
     "Orbital Freight lowered its average delivery time across the eastern corridor [S2].\n",
     "Orbital Freight reduced its average delivery time across the western corridor [S2].\n",
     "eastern -> western"),
    ("p03",
     "The Kestrel sensor identifies surface cracks during routine hull inspection [S3].\n",
     "The Kestrel sensor detects surface cracks during routine wing inspection [S3].\n",
     "hull -> wing"),
    ("p04",
     "Revenue grew eleven percent year over year in the logistics division [S4].\n",
     "Revenue expanded eleven percent year over year in the mapping division [S4].\n",
     "logistics -> mapping"),
    ("p05",
     "The Vantis compiler increases build throughput on large monorepo projects [S5].\n",
     "The Vantis compiler improves build throughput on large monolith projects [S5].\n",
     "monorepo -> monolith"),
]

_A_ARMS = [pytest.param(a, id=f"{pid}-verb-synonym-true") for pid, a, _b, _w in PAIRS]
_B_ARMS = [
    pytest.param(b, w, id=f"{pid}-argument-swap-false") for pid, _a, b, w in PAIRS
]


@pytest.mark.parametrize("draft", _A_ARMS)
def test_verb_synonym_claim_must_still_ground(tmp_path: Path, draft: str) -> None:
    """Error-A guard: substituting a verb for a synonym keeps the claim TRUE.

    A fix for the B-arms that also rejects these has not separated true from
    false — it has stopped grounding paraphrase, which is T2's only purpose.
    """
    report = _gate(tmp_path, draft)
    assert report["gate"] == "PASS", (
        f"honest verb-synonym paraphrase was flagged "
        f"(gate={report['gate']}, score={report['grounding_score']}). "
        f"If this broke while closing OI-MOAT-21, the fix rejects novel tokens "
        f"indiscriminately and cannot tell a synonym from a fabrication."
    )


@pytest.mark.xfail(
    strict=True,
    reason="OI-MOAT-21 (OPEN, escalated to Sai): a one-token ARGUMENT "
    "substitution is certified GROUNDED. Its t2_f1 is IDENTICAL to the "
    "verb-synonym arm of the same pair, so no lex_tau separates them. The fix "
    "moves the Error-A/Error-B trade-off and retires lex_tau, so it is "
    "Escalation #1 and #3, not an agent's call. When these XPASS, a fix has "
    "landed: remove the marker and re-run the sweep.",
)
@pytest.mark.parametrize("draft,swapped", _B_ARMS)
def test_argument_swap_must_not_ground(
    tmp_path: Path, draft: str, swapped: str
) -> None:
    """A fabrication produced by changing ONE noun must not reach PASS."""
    report = _gate(tmp_path, draft)
    assert report["gate"] != "PASS", (
        f"OI-MOAT-21: gate PASSed a claim falsified by a single-token "
        f"argument swap ({swapped}); score={report['grounding_score']}"
    )
