"""Tester-experience tools: scripts/add_source.py and scripts/explain_report.py.

Neither tool may change a verdict. add_source only WRITES a store line (and
proves it loads with ground_check.load_store); explain_report only RENDERS a
ground_check --json report.
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from scripts.ground_check import load_store

_AA = Path(__file__).resolve().parents[1]
_ADD = _AA / "scripts" / "add_source.py"
_EXPLAIN = _AA / "scripts" / "explain_report.py"
_GROUND = _AA / "scripts" / "ground_check.py"
_SENTENCE = ("The 2025 internal audit identified material weaknesses in "
             "custodial reconciliation at the Frankfurt desk during the third quarter.")


def _run(script: Path, *args: str, stdin: str | None = None
         ) -> subprocess.CompletedProcess[str]:
    return subprocess.run([sys.executable, str(script), *args], input=stdin,
                          capture_output=True, text=True, cwd=_AA)


def _ground_json(draft: Path, store: Path, *extra: str) -> str:
    return _run(_GROUND, "--draft", str(draft), "--store", str(store),
                "--json", *extra).stdout


_SOURCE = (_SENTENCE + " Remediation is scheduled for the second quarter, and the "
           "board will review progress at each quarterly meeting thereafter.")


def test_added_source_loads_and_verbatim_claim_passes(tmp_path: Path) -> None:
    src = tmp_path / "my-source.txt"
    src.write_text(_SOURCE + "\n", encoding="utf-8")
    store = tmp_path / "store.jsonl"
    r = _run(_ADD, str(src), "--id", "S1", "--store", str(store),
             "--session-id", "sess-1")
    assert r.returncode == 0, r.stderr
    assert "S1" in load_store(str(store))
    draft = tmp_path / "draft.md"
    draft.write_text(_SENTENCE[:-1] + " [S1].\n", encoding="utf-8")
    g = _run(_GROUND, "--draft", str(draft), "--store", str(store),
             "--session-id", "sess-1", "--json")
    assert g.returncode == 0, g.stdout
    assert json.loads(g.stdout)["gate"] == "PASS"


def test_second_source_appends_and_duplicate_id_is_refused(tmp_path: Path) -> None:
    src = tmp_path / "a.txt"
    src.write_text(_SENTENCE, encoding="utf-8")
    store = tmp_path / "store.jsonl"
    assert _run(_ADD, str(src), "--id", "S1", "--store", str(store)).returncode == 0
    assert _run(_ADD, str(src), "--id", "S2", "--store", str(store)).returncode == 0
    before = store.read_text(encoding="utf-8")
    r = _run(_ADD, str(src), "--id", "S1", "--store", str(store))
    assert r.returncode == 1
    assert "S1" in r.stderr and "already" in r.stderr
    assert store.read_text(encoding="utf-8") == before
    assert sorted(load_store(str(store))) == ["S1", "S2"]


def test_missing_and_empty_file_refused(tmp_path: Path) -> None:
    store = tmp_path / "store.jsonl"
    r = _run(_ADD, str(tmp_path / "nope.txt"), "--id", "S1", "--store", str(store))
    assert r.returncode == 1 and "nope.txt" in r.stderr
    empty = tmp_path / "empty.txt"
    empty.write_text("  \n", encoding="utf-8")
    r = _run(_ADD, str(empty), "--id", "S1", "--store", str(store))
    assert r.returncode == 1 and "empty" in r.stderr
    assert not store.exists()


def test_explain_report_renders_every_claim_reason_and_hint(tmp_path: Path) -> None:
    demo = _AA / "demo"
    report = _ground_json(demo / "draft-fabricated.md", demo / "evidence-store.jsonl")
    parsed = json.loads(report)
    r = _run(_EXPLAIN, stdin=report)
    assert r.returncode == 1  # gate FAIL
    assert "FAIL" in r.stdout and str(parsed["grounding_score"]) in r.stdout
    assert parsed["scope"] in r.stdout.replace("\n", " ") or "PASS means" in r.stdout
    scored = [c for c in parsed["per_claim"] if c["kind"] != "NON_CLAIM"]
    non = [c for c in parsed["per_claim"] if c["kind"] == "NON_CLAIM"]
    assert scored and non
    for c in scored:
        assert c["verdict"] in r.stdout
        assert " ".join(c["evidence_basis"].split()) in " ".join(r.stdout.split())
        assert " ".join(c["text"].split()) in " ".join(r.stdout.split())
    assert "not scored" in r.stdout.lower()
    for c in non:
        assert c["text"] in r.stdout
    assert "fix:" in r.stdout
    # the hint for UNVERIFIED_CITATION (from the guide table)
    assert "Retrieve the source in-session, or fix the id" in r.stdout


def test_explain_report_pass_exit_zero_from_file(tmp_path: Path) -> None:
    demo = _AA / "demo"
    report = _ground_json(demo / "draft-grounded.md", demo / "evidence-store.jsonl")
    f = tmp_path / "r.json"
    f.write_text(report, encoding="utf-8")
    r = _run(_EXPLAIN, str(f))
    assert r.returncode == 0
    assert "PASS" in r.stdout


def test_explain_report_rejects_non_report_input() -> None:
    r = _run(_EXPLAIN, stdin="not json")
    assert r.returncode not in (0,) and "not a ground_check" in r.stderr
