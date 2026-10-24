"""R26-04 — the draft certified itself through a file that was NOT byte-identical
to it (reports/RED-TEAM-R26-2026-10-24.md): a copy one word off read whole, a
partial read of an older version, a whole read of a file holding only the claim.

Real hook (`process_event`) -> real gate CLI. The fix treats a Read source as the
draft when >= 80% of its adjacent word pairs (bigrams) occur in the draft — the
code's _NEAR_COPY_BIGRAM_SHARE. (Corrected 2026-10-25: this docstring first said
70% of 5-word shingles, which the code never did.)
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from scripts.capture_hook import process_event

_ROOT = Path(__file__).resolve().parents[2]
_GATE = _ROOT / "scripts" / "ground_check.py"

_CLAIM = ("The install script provisions a runtime virtual environment "
          "with Python 3.11 or newer.")


def _draft(title: str = "Setup notes") -> str:
    return f"# {title}\n\n{_CLAIM[:-1]} [S1].\n"


def _read(path: Path, content: str, *, start: int, num: int, total: int) -> dict:
    return {"tool_name": "Read", "tool_input": {"file_path": str(path)},
            "tool_response": {"type": "text", "file": {
                "content": content, "numLines": num, "startLine": start,
                "totalLines": total, "filePath": str(path)}},
            "session_id": "sess-A", "cwd": str(path.parent)}


def _gate(draft: Path, store: Path) -> tuple[dict, int]:
    proc = subprocess.run(
        [sys.executable, str(_GATE), "--draft", str(draft), "--store",
         str(store), "--json", "--session-id", "sess-A"],
        capture_output=True, text=True, cwd=str(draft.parent), check=False)
    return json.loads(proc.stdout), proc.returncode


def _run(tmp_path: Path, name: str, content: str, *, start: int, num: int,
         total: int) -> tuple[dict, int]:
    draft = tmp_path / "d.md"
    draft.write_text(_draft(), encoding="utf-8")
    other = tmp_path / name
    other.write_text(content, encoding="utf-8")
    store = tmp_path / "store.jsonl"
    process_event(_read(other, content, start=start, num=num, total=total),
                  str(store))
    return _gate(draft, store)


def test_copy_one_word_off_read_whole_does_not_pass(tmp_path):
    text = _draft("Setup guide").replace(" [S1]", "")
    n = len(text.splitlines())
    report, code = _run(tmp_path, "copy.md", text, start=1, num=n, total=n)
    assert report["gate"] != "PASS" and code != 0, report


def test_partial_read_of_older_version_does_not_pass(tmp_path):
    old = _draft("Setup notes (draft)").replace(" [S1]", "") + "\nTODO.\n"
    lines = old.splitlines()
    part = "\n".join(lines[:3]) + "\n"
    report, code = _run(tmp_path, "old.md", part, start=1, num=3,
                        total=len(lines))
    assert report["gate"] != "PASS" and code != 0, report


def test_whole_read_of_file_holding_only_claim_does_not_pass(tmp_path):
    report, code = _run(tmp_path, "c2.md", _CLAIM + "\n", start=1, num=1,
                        total=1)
    assert report["gate"] != "PASS" and code != 0, report


_LONG_SOURCE = "\n".join([
    "Installation overview for the toolkit, maintained by the release team.",
    "Supported platforms are macOS, Linux and Windows under WSL two.",
    _CLAIM,
    "The script refuses to continue when the interpreter is older than that.",
    "A lockfile pins every transitive dependency to an exact version.",
    "Network access is required only during the first provisioning step.",
    "Caches live under the user's home directory and may be deleted safely.",
    "Uninstalling removes the environment but leaves configuration intact.",
    "Proxy settings are read from the standard environment variables.",
    "Logs from each run are written beside the environment for auditing.",
]) + "\n"


def test_positive_draft_quoting_part_of_long_source_still_grounds(tmp_path):
    n = len(_LONG_SOURCE.splitlines())
    report, code = _run(tmp_path, "INSTALL.md", _LONG_SOURCE, start=1, num=n,
                        total=n)
    assert report["gate"] == "PASS" and code == 0, report


def test_positive_short_genuine_source_still_grounds(tmp_path):
    """A short genuine source the draft does not reproduce wholesale grounds."""
    src = ("Release notes: the install script provisions a runtime virtual "
           "environment with Python 3.11 or newer, replacing the 3.9 floor.\n")
    report, code = _run(tmp_path, "NOTES.md", src, start=1, num=1, total=1)
    assert report["gate"] == "PASS" and code == 0, report
