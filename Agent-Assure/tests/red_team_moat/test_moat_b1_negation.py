"""B1 (D-97) — negated predicates on a definite subject are FACTUAL, and
grounding is negation-aware.

Before B1, classify() routed any sentence containing "no " / "not " to ABSENCE,
so honest claims such as "R20-02 and R20-03 were not reproduced" were refused
UNVERIFIED_ABSENCE (23 of 177 honest claims, tests/honest_drafts_v2). B1 makes
them FACTUAL, which sends them through T1 — where "not"/"no"/"never" are stop
words. THE GUARD: a claim grounds only against a source sentence whose
negations match the claim's (same negator followed by the same word), in both
directions. Every test runs the real CLI.
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
STORE = str(Path(__file__).parent / "fixtures" / "store_b1_negation.jsonl")


def _claim(tmp_path: Path, draft_text: str) -> dict:
    draft = tmp_path / "draft.md"
    draft.write_text(draft_text, encoding="utf-8")
    env = {**os.environ, "PYTHONPATH": str(REPO_ROOT)}
    result = subprocess.run(
        [sys.executable, GROUND_CHECK, "--draft", str(draft), "--store", STORE, "--json"],
        capture_output=True, text=True, env=env,
    )
    assert result.stdout, f"gate produced no stdout.\nstderr: {result.stderr}"
    report = json.loads(result.stdout)
    scored = [c for c in report["per_claim"] if c["kind"] != "NON_CLAIM"]
    assert len(scored) == 1, f"expected one scored claim, got {scored}"
    return {**scored[0], "_gate": report.get("gate")}


# (a) Honest negations (shapes from tests/honest_drafts_v2 LABELS.md) ground
# when the cited source states the same negation.
HONEST = [
    pytest.param("R20-02 and R20-03 were not reproduced [S8].\n", id="not-reproduced-short"),
    pytest.param("The overflow regression in the parser module of release twelve was not reproduced [S1].\n", id="not-reproduced-long"),
    pytest.param("The scheduled merge of the documentation branch into main deletes no files [S3].\n", id="deletes-no-files"),
    pytest.param("The hardening fix for the cache eviction path was never attacked [S5].\n", id="never-attacked"),
    # A contracted CLAIM ("wasn't") is not listed: _reconstruct_sentence renders
    # it "wasnot" before grounding (the separate PASS-enabling display defect
    # noted at _NEGATION_CONTRACTION_RE, Sai's call), so it reads UNGROUNDED.
    pytest.param("The hardening fix for the cache eviction path was not attacked [S7].\n", id="spelled-matches-contracted"),
]


@pytest.mark.parametrize("draft", HONEST)
def test_honest_negation_grounds(tmp_path: Path, draft: str) -> None:
    c = _claim(tmp_path, draft)
    assert c["kind"] != "ABSENCE", c
    assert c["verdict"] == "GROUNDED", c


# (b) Negation-flip attacks — must NOT ground.
FLIPS = [
    pytest.param("R20-02 and R20-03 were not reproduced [S9].\n", id="neg-claim-aff-source-short"),
    pytest.param("R20-02 and R20-03 were reproduced [S8].\n", id="aff-claim-neg-source-short"),
    pytest.param("The overflow regression in the parser module of release twelve was not reproduced [S2].\n", id="not-claim-aff-source"),
    pytest.param("The overflow regression in the parser module of release twelve was reproduced [S1].\n", id="aff-claim-not-source"),
    pytest.param("The scheduled merge of the documentation branch into main deletes no files [S4].\n", id="no-claim-aff-source"),
    pytest.param("The scheduled merge of the documentation branch into main deletes files [S3].\n", id="aff-claim-no-source"),
    pytest.param("The hardening fix for the cache eviction path was never attacked [S6].\n", id="never-claim-aff-source"),
    pytest.param("The hardening fix for the cache eviction path was attacked [S5].\n", id="aff-claim-never-source"),
    pytest.param("The hardening fix for the cache eviction path wasn't attacked [S6].\n", id="nt-claim-aff-source"),
    pytest.param("The hardening fix for the cache eviction path was attacked [S7].\n", id="aff-claim-nt-source"),
    pytest.param("The hardening fix for the cache eviction path was not attacked [S10].\n", id="negation-elsewhere-in-sentence"),
]


@pytest.mark.parametrize("draft", FLIPS)
def test_negation_flip_does_not_ground(tmp_path: Path, draft: str) -> None:
    c = _claim(tmp_path, draft)
    assert c["verdict"] != "GROUNDED", c
    assert c["_gate"] != "PASS", c


# (c) Real absence claims still classify ABSENCE.
ABSENCE = [
    "There is no recall of the Zentara inhaler in any regulated market.\n",
    "We found no evidence of a safety recall affecting the X200 drone.\n",
    "No independent replication of the result exists.\n",
    "The defect has never been reported in the field.\n",
    "The note found no study that reports verdict agreement [S8].\n",
    "A vendor figure with no independent replication found [S8].\n",
    "The audit did not find any fraud in the accounts.\n",
    "The cited module does not exist.\n",
]


@pytest.mark.parametrize("draft", ABSENCE)
def test_real_absence_still_absence(tmp_path: Path, draft: str) -> None:
    c = _claim(tmp_path, draft)
    assert c["kind"] == "ABSENCE", c
