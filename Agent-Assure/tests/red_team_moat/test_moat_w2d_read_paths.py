"""W2D-01 / W2D-02 — a relative or `~` Read path plus a PARTIAL Read let the
draft certify itself (reports/RED-TEAM-W2D-CAPTURE-2026-10-24.md).

The capture hook stored `tool_input["file_path"]` verbatim; the gate resolved
it against ITS OWN cwd. Run the gate from anywhere else and the path test
missed; a partial Read (offset/limit) defeated the whole-draft digest. Both
J-83 tests missed and the draft scored PASS 100.0.

These tests go through the REAL hook (`process_event`) and the REAL gate CLI,
with the gate run from a directory that is NOT the agent's cwd.
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

from scripts.capture_hook import process_event

_ROOT = Path(__file__).resolve().parents[2]
_GATE = _ROOT / "scripts" / "ground_check.py"

_CLAIM = ("The install script provisions a runtime virtual environment "
          "with Python 3.11 or newer.")
_DRAFT = f"# Notes\n\n{_CLAIM[:-1]} [S1].\n"


def _read_event(file_path: str, content: str, *, cwd: str | None,
                harness_path: str | None, start_line: int, num_lines: int,
                total_lines: int, offset: int | None = None,
                limit: int | None = None) -> dict:
    tool_input: dict = {"file_path": file_path}
    if offset is not None:
        tool_input["offset"] = offset
    if limit is not None:
        tool_input["limit"] = limit
    file_obj: dict = {"content": content, "numLines": num_lines,
                      "startLine": start_line, "totalLines": total_lines}
    if harness_path is not None:
        file_obj["filePath"] = harness_path
    event: dict = {"tool_name": "Read", "tool_input": tool_input,
                   "tool_response": {"type": "text", "file": file_obj},
                   "session_id": "sess-A"}
    if cwd is not None:
        event["cwd"] = cwd
    return event


def _gate(draft: Path, store: Path, gate_cwd: Path) -> tuple[dict, int]:
    proc = subprocess.run(
        [sys.executable, str(_GATE), "--draft", str(draft), "--store",
         str(store), "--json", "--session-id", "sess-A"],
        capture_output=True, text=True, cwd=str(gate_cwd), check=False)
    return json.loads(proc.stdout), proc.returncode


def _setup(tmp_path: Path) -> tuple[Path, Path, Path, Path]:
    agent = tmp_path / "p2"
    agent.mkdir()
    elsewhere = tmp_path / "elsewhere"
    elsewhere.mkdir()
    draft = agent / "d.md"
    draft.write_text(_DRAFT, encoding="utf-8")
    return agent, elsewhere, draft, tmp_path / "store.jsonl"


@pytest.mark.parametrize("harness_path", [True, False],
                         ids=["harness-filePath", "event-cwd-only"])
def test_w2d01_relative_partial_read_does_not_pass(tmp_path, harness_path):
    agent, elsewhere, draft, store = _setup(tmp_path)
    process_event(_read_event(
        "d.md", _CLAIM, cwd=str(agent),
        harness_path=str(draft) if harness_path else None,
        start_line=3, num_lines=1, total_lines=3, offset=3, limit=1),
        str(store))
    report, code = _gate(draft, store, elsewhere)
    assert report["gate"] != "PASS" and code != 0, report


def test_w2d01_relative_partial_read_no_cwd_no_harness_path(tmp_path):
    """No signal to resolve the path: stored as-is, the gate must still treat
    an unresolvable path with the draft's basename as the draft."""
    agent, elsewhere, draft, store = _setup(tmp_path)
    process_event(_read_event(
        "d.md", _CLAIM, cwd=None, harness_path=None,
        start_line=3, num_lines=1, total_lines=3, offset=3, limit=1),
        str(store))
    report, code = _gate(draft, store, elsewhere)
    assert report["gate"] != "PASS" and code != 0, report


def test_w2d01_tilde_partial_read_does_not_pass(tmp_path, monkeypatch):
    agent, elsewhere, draft, store = _setup(tmp_path)
    monkeypatch.setenv("HOME", str(agent))
    process_event(_read_event(
        "~/d.md", _CLAIM, cwd=str(elsewhere), harness_path=None,
        start_line=3, num_lines=1, total_lines=3, offset=3, limit=1),
        str(store))
    report, code = _gate(draft, store, elsewhere)
    assert report["gate"] != "PASS" and code != 0, report


def test_w2d02_partial_read_of_draft_under_another_name_does_not_pass(tmp_path):
    """W2D-02: a partial Read whose text sits inside the draft is the draft,
    whatever path it was recorded under (fail-closed)."""
    agent, elsewhere, draft, store = _setup(tmp_path)
    copy = agent / "copy.md"
    copy.write_text(_DRAFT, encoding="utf-8")
    process_event(_read_event(
        str(copy), _CLAIM, cwd=str(agent), harness_path=str(copy),
        start_line=3, num_lines=1, total_lines=3), str(store))
    report, code = _gate(draft, store, elsewhere)
    assert report["gate"] != "PASS" and code != 0, report


def test_w2d_capture_records_absolute_path_and_partial_extent(tmp_path):
    agent, _elsewhere, draft, store = _setup(tmp_path)
    process_event(_read_event(
        "d.md", _CLAIM, cwd=str(agent), harness_path=None,
        start_line=3, num_lines=1, total_lines=3), str(store))
    row = json.loads(store.read_text(encoding="utf-8").splitlines()[0])
    assert row["file_path"] == str(draft.resolve())
    assert row["read_extent"] == "partial"


def test_positive_control_genuine_source_read_still_grounds(tmp_path):
    """A genuine, non-draft source, read relatively and partially, still
    grounds the claim — the fix must not refuse real evidence."""
    agent, elsewhere, draft, store = _setup(tmp_path)
    source = agent / "INSTALL.md"
    source_text = f"Intro line.\n{_CLAIM} It also pins the lockfile.\nEnd.\n"
    source.write_text(source_text, encoding="utf-8")
    process_event(_read_event(
        "INSTALL.md", source_text, cwd=str(agent), harness_path=str(source),
        start_line=1, num_lines=4, total_lines=4), str(store))
    report, code = _gate(draft, store, elsewhere)
    assert report["gate"] == "PASS" and code == 0, report
