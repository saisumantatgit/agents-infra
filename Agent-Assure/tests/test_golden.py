"""Task 10: CLI-level golden + determinism tests.

Tests invoke scripts/ground_check.py as a subprocess using sys.executable
so they run under the same uv-managed interpreter as pytest.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

SCRIPTS_DIR = Path(__file__).parent.parent / "scripts"
GROUND_CHECK = str(SCRIPTS_DIR / "ground_check.py")

# Fixture paths for the simple end-to-end case.
FIXTURES = Path(__file__).parent / "fixtures"
STORE_BASIC = str(FIXTURES / "store_basic.jsonl")
DRAFT_BASIC = str(FIXTURES / "draft_basic.md")


def _run_cli(*args: str, cwd: Path | None = None) -> subprocess.CompletedProcess:
    """Run the CLI under sys.executable and return the CompletedProcess."""
    cmd = [sys.executable, GROUND_CHECK, *args]
    env_extra = {"PYTHONPATH": str(Path(GROUND_CHECK).parent.parent)}
    import os
    env = {**os.environ, **env_extra}
    return subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        cwd=str(cwd) if cwd else None,
        env=env,
    )


# ---------------------------------------------------------------------------
# Test 1: end-to-end PASS — store fully supports the single draft claim
# ---------------------------------------------------------------------------

def test_end_to_end_pass_json(tmp_path: Path) -> None:
    """Store S1 fully supports the one claim in draft_basic.md → PASS, score 100.0, exit 0."""
    result = _run_cli(
        "--draft", DRAFT_BASIC,
        "--store", STORE_BASIC,
        "--json",
        cwd=tmp_path,
    )
    assert result.returncode == 0, (
        f"Expected exit 0 (PASS) but got {result.returncode}.\n"
        f"stdout: {result.stdout}\nstderr: {result.stderr}"
    )
    report = json.loads(result.stdout)
    assert report["gate"] == "PASS", f"Expected gate PASS, got {report['gate']}"
    assert report["grounding_score"] == 100.0, (
        f"Expected score 100.0, got {report['grounding_score']}"
    )
    # Verdict strings must be plain strings, not enum repr.
    for pc in report["per_claim"]:
        assert not pc["verdict"].startswith("<"), (
            f"Verdict serialized as enum repr: {pc['verdict']}"
        )


def test_end_to_end_pass_yaml(tmp_path: Path) -> None:
    """Without --json, grounding-report.yaml is written and one-line summary printed."""
    result = _run_cli(
        "--draft", DRAFT_BASIC,
        "--store", STORE_BASIC,
        cwd=tmp_path,
    )
    assert result.returncode == 0, (
        f"Expected exit 0 (PASS) but got {result.returncode}.\n"
        f"stdout: {result.stdout}\nstderr: {result.stderr}"
    )
    yaml_path = tmp_path / "grounding-report.yaml"
    assert yaml_path.exists(), "grounding-report.yaml not written to CWD"

    import yaml
    report = yaml.safe_load(yaml_path.read_text())
    assert report["gate"] == "PASS"
    assert report["grounding_score"] == 100.0

    # One-line summary must contain gate and score.
    summary = result.stdout.strip()
    assert "PASS" in summary, f"One-line summary missing 'PASS': {summary!r}"
    assert "100" in summary or "100.0" in summary, (
        f"One-line summary missing score: {summary!r}"
    )


# ---------------------------------------------------------------------------
# Test 2: NEEDS_WORK / FAIL case → exit code 1
# ---------------------------------------------------------------------------

def test_fail_case_exit_1(tmp_path: Path) -> None:
    """Draft with an unsupported claim (UNCITED) → gate != PASS → exit 1."""
    # Draft with a claim that has no citation and nothing in the store to match it.
    draft = tmp_path / "draft_fail.md"
    draft.write_text(
        "The sky is made of cheese with no supporting evidence.\n",
        encoding="utf-8",
    )
    # Use an empty store.
    empty_store = tmp_path / "empty.jsonl"
    empty_store.write_text("", encoding="utf-8")

    result = _run_cli(
        "--draft", str(draft),
        "--store", str(empty_store),
        "--json",
        cwd=tmp_path,
    )
    assert result.returncode == 1, (
        f"Expected exit 1 (non-PASS) but got {result.returncode}.\n"
        f"stdout: {result.stdout}\nstderr: {result.stderr}"
    )
    report = json.loads(result.stdout)
    assert report["gate"] != "PASS", f"Expected non-PASS gate, got {report['gate']}"


# ---------------------------------------------------------------------------
# Test 3: determinism — byte-identical JSON across two runs
# ---------------------------------------------------------------------------

def test_determinism_identical_across_runs(tmp_path: Path) -> None:
    """Same inputs → byte-identical JSON stdout across two runs."""
    run_a = _run_cli(
        "--draft", DRAFT_BASIC,
        "--store", STORE_BASIC,
        "--json",
        cwd=tmp_path,
    )
    run_b = _run_cli(
        "--draft", DRAFT_BASIC,
        "--store", STORE_BASIC,
        "--json",
        cwd=tmp_path,
    )
    assert run_a.returncode == run_b.returncode, "Return codes differ across runs"
    assert run_a.stdout == run_b.stdout, (
        "JSON output is NOT byte-identical across two runs (non-deterministic).\n"
        f"Run A: {run_a.stdout!r}\nRun B: {run_b.stdout!r}"
    )
