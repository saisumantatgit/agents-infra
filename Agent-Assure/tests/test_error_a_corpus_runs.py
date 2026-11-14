"""The Error-A corpus loads and its runner executes. Pins NO rates: the corpus measures the
gate, it does not assert how the gate scores (see tests/error_a_corpus/BASELINE.md)."""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]
CORPUS = BASE / "tests" / "error_a_corpus"


def _manifest() -> list[dict]:
    return json.loads((CORPUS / "manifest.json").read_text())


def test_corpus_loads() -> None:
    entries = _manifest()
    assert len(entries) >= 300
    assert len({e["genre"] for e in entries}) >= 10
    assert len({e["id"] for e in entries}) == len(entries)
    for e in entries:
        assert (CORPUS / "drafts" / f"{e['id']}.md").is_file(), e["id"]
        assert e["sources"], e["id"]
        for s in e["sources"]:
            assert (CORPUS / s).is_file(), s


def test_every_claim_is_verbatim_in_its_own_source() -> None:
    for e in _manifest():
        source = " ".join(" ".join((CORPUS / s).read_text().split()) for s in e["sources"])
        for c in e["claims"]:
            assert " ".join(c["text"].split()) in source, (e["id"], c["text"])


def test_runner_executes_on_a_subset(tmp_path: Path) -> None:
    out = tmp_path / "results.json"
    proc = subprocess.run(
        [sys.executable, str(CORPUS / "run.py"), "--base", str(BASE), "--limit", "14",
         "--no-ablate", "--work", str(tmp_path / "work"), "--out", str(out)],
        capture_output=True, text=True, cwd=str(BASE))
    assert proc.returncode == 0, proc.stderr
    data = json.loads(out.read_text())
    assert data["summary"]["drafts"] == len(data["drafts"]) >= 14
    assert set(data["summary"]["gates"]) <= {"PASS", "NEEDS_WORK", "FAIL"}
    assert all("claims" in d and "gate" in d for d in data["drafts"])
