"""W2A (2026-10-24) — T1 span coverage must be bound to the anchor's SENTENCE.

T1 certified a claim when an 8-token verbatim span existed and every other
claim content word occurred ANYWHERE in the source. A long subject holds the
whole span, and the predicate is borrowed from a sibling sentence:
entity substitution (W2A-01) and quantifier swap (W2A-02) certified at
PASS 100.0 with no hedge word involved. The fix requires the coverage words to
occur in the same raw-text sentence (`_split_sentences`) as the anchored span.

Driven through the real CLI. See reports/RED-TEAM-W2A-T1-2026-10-24.md.
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts" / "ground_check.py"
SUBJ = "The managed Postgres cluster in the eu-west region"
ENGINE = "The open source orchestration engine for batch workloads"


def _cli(tmp_path: Path, claim: str, source_text: str) -> tuple[int, dict]:
    store = tmp_path / "s.jsonl"
    store.write_text(json.dumps({
        "source_id": "S1", "url": "https://example.com/s1", "file_path": None,
        "fetched_at": "2026-06-28T00:00:00Z", "tool": "mcp__exa__web_fetch_exa",
        "content_sha256": "x", "text": source_text,
        "full_text_source": "verbatim", "captured_via": "inline",
        "query_provenance": "w2a", "session_id": "", "retrieval_status": "ok",
    }) + "\n", encoding="utf-8")
    draft = tmp_path / "d.md"
    draft.write_text(claim + "\n", encoding="utf-8")
    proc = subprocess.run(
        [sys.executable, str(SCRIPT), "--draft", str(draft),
         "--store", str(store), "--json"],
        capture_output=True, text=True, cwd=ROOT)
    return proc.returncode, json.loads(proc.stdout)


def _assert_refused(code: int, rep: dict) -> None:
    assert rep["per_claim"][0]["verdict"] != "GROUNDED", rep["per_claim"][0]
    assert rep["gate"] != "PASS"
    assert code != 0


def test_w2a_01_entity_borrowed_from_sibling_sentence(tmp_path):
    code, rep = _cli(
        tmp_path, f"{SUBJ} was migrated to Spanner in June [S1].",
        f"{SUBJ} was migrated to Aurora in March. "
        "The MySQL fleet was migrated to Spanner in June.")
    _assert_refused(code, rep)


def test_w2a_02_quantifier_borrowed_from_sibling_sentence(tmp_path):
    code, rep = _cli(
        tmp_path, f"{SUBJ} replicated all writes within one second [S1].",
        f"{SUBJ} replicated most writes within one second. "
        "All other regions were offline.")
    _assert_refused(code, rep)


def test_w2a_04_actor_swap_across_sentences(tmp_path):
    """W2A-04 with the borrowed actor in a SIBLING sentence: must refuse."""
    code, rep = _cli(
        tmp_path,
        f"{ENGINE} was maintained by the Apache Foundation until 2019 [S1].",
        f"{ENGINE} was maintained by Google until 2019. "
        "The Apache Foundation took over later.")
    _assert_refused(code, rep)


def test_positive_control_honest_same_sentence_claim_grounds(tmp_path):
    code, rep = _cli(
        tmp_path, f"{SUBJ} was migrated to Aurora in March [S1].",
        f"{SUBJ} was migrated to Aurora in March. "
        "The MySQL fleet was migrated to Spanner in June.")
    assert rep["per_claim"][0]["verdict"] == "GROUNDED", rep["per_claim"][0]
    assert rep["gate"] == "PASS" and code == 0


@pytest.mark.xfail(strict=True, reason=(
    "W2A-04 as reproduced: the swapped actor sits in the SAME raw-text "
    "sentence ('until 2019, when the Apache Foundation took over'), so "
    "sentence-scoped coverage cannot see it. Needs clause/role binding. OPEN."))
def test_w2a_04_actor_swap_within_one_sentence_open(tmp_path):
    code, rep = _cli(
        tmp_path,
        f"{ENGINE} was maintained by the Apache Foundation until 2019 [S1].",
        f"{ENGINE} was maintained by Google until 2019, "
        "when the Apache Foundation took over.")
    _assert_refused(code, rep)


@pytest.mark.xfail(strict=True, reason=(
    "W2A-03: comparative reversal inside ONE sentence; sentence-scoped "
    "coverage cannot close it, only a parser could. OPEN tripwire."))
def test_w2a_03_comparative_reversal_within_one_sentence_open(tmp_path):
    lay = "The new caching layer on the primary storage tier"
    code, rep = _cli(
        tmp_path, f"{lay} is less reliable than the legacy layer and faster [S1].",
        f"{lay} is faster than the legacy layer and less reliable than the "
        "legacy layer.")
    _assert_refused(code, rep)
