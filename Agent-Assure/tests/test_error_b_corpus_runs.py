"""The Error-B corpus loads and its runner executes. Pins NO rates: the corpus measures the
gate, it does not assert how the gate scores (see tests/error_b_corpus/BASELINE.md)."""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]
CORPUS = BASE / "tests" / "error_b_corpus"


def _manifest() -> list[dict]:
    return json.loads((CORPUS / "manifest.json").read_text())


def test_corpus_loads() -> None:
    entries = _manifest()
    assert len(entries) >= 280
    assert len({e["genre"] for e in entries}) == 14
    assert len({e["class"] for e in entries}) >= 18
    assert len({e["id"] for e in entries}) == len(entries)
    for e in entries:
        assert (CORPUS / "drafts" / f"{e['id']}.md").is_file(), e["id"]
        assert (CORPUS / "controls" / f"{e['id']}.md").is_file(), e["id"]
        assert (CORPUS / e["source"]).is_file(), e["id"]


def test_each_draft_carries_its_labelled_fabrication_once_at_its_offset() -> None:
    for e in _manifest():
        text = (CORPUS / "drafts" / f"{e['id']}.md").read_text()
        a = e["offset"]
        assert text[a:a + len(e["fabricated"])] == e["fabricated"], e["id"]
        control = (CORPUS / "controls" / f"{e['id']}.md").read_text()
        assert control.count(e["fabricated"]) == text.count(e["fabricated"]) - 1, e["id"]


def test_fabrication_is_absent_from_source_unless_denied() -> None:
    for e in _manifest():
        source = " ".join((CORPUS / e["source"]).read_text().split())
        present = " ".join(e["fabricated"].split()) in source
        moved_cell = e["class"] == "table_cell" and e["variant"] == "moved_from_other_row"
        assert present == (e["fabricated_in_source"] or moved_cell), e["id"]
        assert e["fabricated_in_source"] == e["class"].startswith("denied_"), e["id"]


def test_runner_executes_on_a_subset(tmp_path: Path) -> None:
    out = tmp_path / "results.json"
    proc = subprocess.run(
        [sys.executable, str(CORPUS / "run.py"), "--base", str(BASE), "--limit", "18",
         "--work", str(tmp_path / "work"), "--out", str(out)],
        capture_output=True, text=True, cwd=str(BASE))
    assert proc.returncode == 0, proc.stderr
    data = json.loads(out.read_text())
    assert data["summary"]["all"]["drafts"] == len(data["drafts"]) >= 18
    assert all(d["gate"] in {"PASS", "NEEDS_WORK", "FAIL"} and isinstance(d["escaped"], bool) for d in data["drafts"])
