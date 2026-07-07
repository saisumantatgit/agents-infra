"""Golden test for the Agent-Assure demo (docs/plans/DEMO-READINESS-PLAN.md, D1).

Runs the exact frozen demo path — `demo/build_store.py` then
`scripts/ground_check.py` against both demo drafts — and asserts the gate
verdicts the demo script (demo/DEMO-SCRIPT.md) and README promise:

  draft-grounded.md   -> gate PASS
  draft-fabricated.md -> gate FAIL, with UNVERIFIED_CITATION naming the
                          fabricated source [S3] (never retrieved).

This makes demo breakage a test failure in CI, not a live-audience discovery.

Follows the subprocess convention in tests/test_golden.py: invoke scripts via
sys.executable so they run under the same uv-managed interpreter as pytest.
`demo/build_store.py` is NOT parameterizable (it writes to the real
`demo/evidence-store.jsonl` by design — it simulates the capture hook running
in place); rebuilding it is deterministic (fixed fetched_at, unlink-then-write)
so re-running this test repeatedly is safe and does not require --forked/xdist
isolation.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent
DEMO_DIR = REPO_ROOT / "demo"
GROUND_CHECK = str(REPO_ROOT / "scripts" / "ground_check.py")
BUILD_STORE = str(DEMO_DIR / "build_store.py")

STORE = str(DEMO_DIR / "evidence-store.jsonl")
DRAFT_GROUNDED = str(DEMO_DIR / "draft-grounded.md")
DRAFT_FABRICATED = str(DEMO_DIR / "draft-fabricated.md")

FABRICATED_SOURCE_ID = "S3"


def _run(cmd: list[str], cwd: Path | None = None) -> subprocess.CompletedProcess:
    env = {**os.environ, "PYTHONPATH": str(REPO_ROOT)}
    return subprocess.run(
        cmd, capture_output=True, text=True, cwd=str(cwd) if cwd else None, env=env,
    )


def _rebuild_demo_store() -> None:
    """Rebuild demo/evidence-store.jsonl exactly as demo/build_store.py does —
    the same command the demo script's Step 2 runs. Deterministic (fixed
    fetched_at, unlink-then-rewrite), so re-running is safe."""
    result = _run([sys.executable, BUILD_STORE], cwd=REPO_ROOT)
    assert result.returncode == 0, (
        f"demo/build_store.py failed.\nstdout: {result.stdout}\nstderr: {result.stderr}"
    )


def _run_ground_check(draft: str) -> tuple[subprocess.CompletedProcess, dict]:
    result = _run(
        [sys.executable, GROUND_CHECK, "--draft", draft, "--store", STORE, "--json"],
        cwd=REPO_ROOT,
    )
    report = json.loads(result.stdout)
    return result, report


def test_demo_store_builds_two_sources() -> None:
    """demo/build_store.py (the simulated capture hook) writes exactly S1, S2."""
    _rebuild_demo_store()
    lines = Path(STORE).read_text(encoding="utf-8").strip().splitlines()
    assert len(lines) == 2, f"Expected 2 sources in demo store, got {len(lines)}"
    records = [json.loads(line) for line in lines]
    assert [r["source_id"] for r in records] == ["S1", "S2"]


def test_grounded_draft_gate_pass() -> None:
    """draft-grounded.md against the demo store -> gate PASS, exit 0, score 100.0."""
    _rebuild_demo_store()
    result, report = _run_ground_check(DRAFT_GROUNDED)
    assert result.returncode == 0, (
        f"Expected exit 0 (PASS) but got {result.returncode}.\n"
        f"stdout: {result.stdout}\nstderr: {result.stderr}"
    )
    assert report["gate"] == "PASS", f"Expected gate PASS, got {report['gate']!r}"
    assert report["grounding_score"] == 100.0, (
        f"Expected score 100.0, got {report['grounding_score']!r}"
    )
    verdicts = {c["verdict"] for c in report["per_claim"]}
    assert verdicts == {"GROUNDED"}, f"Expected only GROUNDED verdicts, got {verdicts}"


def test_fabricated_draft_gate_fail_with_unverified_citation() -> None:
    """draft-fabricated.md against the demo store -> gate FAIL, exit 1, and the
    fabricated source-id [S3] is named by an UNVERIFIED_CITATION verdict on the
    per-claim text that cites it."""
    _rebuild_demo_store()
    result, report = _run_ground_check(DRAFT_FABRICATED)
    assert result.returncode == 1, (
        f"Expected exit 1 (non-PASS) but got {result.returncode}.\n"
        f"stdout: {result.stdout}\nstderr: {result.stderr}"
    )
    assert report["gate"] == "FAIL", f"Expected gate FAIL, got {report['gate']!r}"

    unverified_citation_claims = [
        c for c in report["per_claim"] if c["verdict"] == "UNVERIFIED_CITATION"
    ]
    assert unverified_citation_claims, (
        "Expected at least one UNVERIFIED_CITATION verdict in per_claim output, "
        f"got verdicts: {[c['verdict'] for c in report['per_claim']]}"
    )
    assert any(
        f"[{FABRICATED_SOURCE_ID}]" in c["text"] for c in unverified_citation_claims
    ), (
        f"Expected the fabricated source-id [{FABRICATED_SOURCE_ID}] to appear in "
        f"the text of an UNVERIFIED_CITATION claim, got: {unverified_citation_claims}"
    )

    # The draft's real, evidence-backed claims must still be GROUNDED — the
    # gate only flags the fabrication, it does not blanket-fail the draft.
    grounded_claims = [c for c in report["per_claim"] if c["verdict"] == "GROUNDED"]
    assert len(grounded_claims) >= 2, (
        f"Expected the two real (S1/S2-backed) claims to remain GROUNDED, "
        f"got: {report['per_claim']}"
    )


def test_rendered_report_matches_golden_transcript() -> None:
    """demo/show_report.py rendering of both drafts matches the frozen golden
    transcripts in demo/expected/ byte-for-byte (modulo trailing newline)."""
    _rebuild_demo_store()
    show_report = str(DEMO_DIR / "show_report.py")

    for draft, golden_name in (
        (DRAFT_GROUNDED, "grounded-rendered.txt"),
        (DRAFT_FABRICATED, "fabricated-rendered.txt"),
    ):
        ground = _run(
            [sys.executable, GROUND_CHECK, "--draft", draft, "--store", STORE, "--json"],
            cwd=REPO_ROOT,
        )
        rendered = subprocess.run(
            [sys.executable, show_report],
            input=ground.stdout,
            capture_output=True,
            text=True,
            cwd=str(REPO_ROOT),
        )
        golden_path = DEMO_DIR / "expected" / golden_name
        golden_text = golden_path.read_text(encoding="utf-8")
        assert rendered.stdout.strip() == golden_text.strip(), (
            f"Rendered output for {draft} does not match golden transcript "
            f"{golden_path}.\nGot:\n{rendered.stdout}\nExpected:\n{golden_text}"
        )
