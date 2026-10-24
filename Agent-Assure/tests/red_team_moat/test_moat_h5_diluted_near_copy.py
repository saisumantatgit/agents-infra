"""H5 (2026-10-25): a near-copy of the draft DILUTED with unrelated lines, so
that under 80% of the SOURCE's bigrams occur in the draft, escaped R26-04's
whole-record share test and the draft certified itself. The ATTACKS were seen
PASS on the pre-fix code. Real hook (`process_event`) -> real gate CLI.

Controls: the R26-04 long-source and short-source positives live in
test_moat_s2_near_copy.py; here, a draft that quotes TWO sentences of a long
genuine file under its own title must still PASS."""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from scripts.capture_hook import process_event

_ROOT = Path(__file__).resolve().parents[2]
_GATE = _ROOT / "scripts" / "ground_check.py"

_CLAIMS = [
    "The install script provisions a runtime virtual environment with Python 3.11 or newer",
    "The lockfile pins every transitive dependency to an exact version for reproducible builds",
    "Network access is required only during the first provisioning step of the toolkit",
]
_FILLER = [
    "Weather in the northern valley was mild for most of the spring season.",
    "The museum reopened its east wing after a long period of restoration work.",
    "Local bakeries reported strong demand for rye bread during the festival week.",
    "A new ferry timetable takes effect on the first Monday of next month.",
    "The choir rehearses on Thursday evenings in the old parish hall downtown.",
    "Volunteers planted two hundred oak saplings along the river embankment.",
    "The library extended its weekend opening hours through the winter months.",
    "Cyclists are asked to use the marked lane on the harbour bridge at night.",
]


def _draft() -> str:
    return "# Toolkit setup notes\n\n" + "".join(f"{c} [S1].\n" for c in _CLAIMS)


def _read(path: Path, content: str) -> dict:
    n = len(content.splitlines())
    return {"tool_name": "Read", "tool_input": {"file_path": str(path)},
            "tool_response": {"type": "text", "file": {
                "content": content, "numLines": n, "startLine": 1,
                "totalLines": n, "filePath": str(path)}},
            "session_id": "sess-A", "cwd": str(path.parent)}


def _run(tmp_path: Path, content: str, draft: str) -> tuple[dict, int]:
    d = tmp_path / "d.md"
    d.write_text(draft, encoding="utf-8")
    other = tmp_path / "notes-copy.md"
    other.write_text(content, encoding="utf-8")
    store = tmp_path / "store.jsonl"
    process_event(_read(other, content), str(store))
    proc = subprocess.run(
        [sys.executable, str(_GATE), "--draft", str(d), "--store", str(store),
         "--json", "--session-id", "sess-A"],
        capture_output=True, text=True, cwd=str(tmp_path), check=False)
    return json.loads(proc.stdout), proc.returncode


def _interleave(lines: list[str], per_gap: int) -> str:
    out: list[str] = []
    filler = iter(_FILLER * 4)
    for line in lines:
        out.append(line)
        out.extend(next(filler) for _ in range(per_gap))
    return "\n".join(out) + "\n"


def test_h5_copy_diluted_with_filler_lines_does_not_pass(tmp_path: Path) -> None:
    copy = ["# Toolkit setup notes"] + [c + "." for c in _CLAIMS]
    report, code = _run(tmp_path, _interleave(copy, 2), _draft())
    assert report["gate"] != "PASS" and code != 0, report


def test_h5_copy_diluted_and_one_word_off_per_line_does_not_pass(tmp_path: Path) -> None:
    copy = ["# Toolkit setup guide"] + [c.replace("The ", "Our ", 1) + "." for c in _CLAIMS]
    report, code = _run(tmp_path, _interleave(copy, 3), _draft())
    assert report["gate"] != "PASS" and code != 0, report


def test_h5_control_draft_quoting_two_sentences_of_long_genuine_file_passes(tmp_path: Path) -> None:
    genuine = _interleave([c + "." for c in _CLAIMS[:2]], 3)
    draft = "# My own summary of the toolkit\n\n" + "".join(f"{c} [S1].\n" for c in _CLAIMS[:2])
    report, code = _run(tmp_path, genuine, draft)
    assert report["gate"] == "PASS" and code == 0, report
