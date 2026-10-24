"""C3 residue — five fail-closed repairs, each driven through the real CLI.

Every repair here may only move a claim AWAY from PASS. Each attack was seen
RED (PASS) on the unfixed code before its repair landed; each has a positive
control — an honest equivalent that must still ground — whose source is a real
two-sentence document, never byte-identical to the draft (J-83 would refuse it
as a self-citation and mask the check).

* R27-02  "16 MB" grounded on "16 Mb" — byte (B) vs bit (b) folded by case.
* R26-03  an accounting negative "(12%)" grounded a claim of "12%".
* R26-05  DDG failures not shaped "Error:" stayed retrieval_status "ok".
* W2C-01  an HTML comment inside <textarea>/<xmp> was stripped though visible.
* R7      a stop-word-only negation/comparison next to a grounded claim PASSed.
"""
from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

_AGENT_ASSURE = Path(__file__).resolve().parents[2]
_GATE = _AGENT_ASSURE / "scripts" / "ground_check.py"
_HOOK = _AGENT_ASSURE / "scripts" / "capture_hook.py"


def _gate(tmp_path: Path, source_text: str, draft: str) -> dict:
    rec = {
        "source_id": "S1",
        "url": "https://example.com/s1",
        "file_path": None,
        "fetched_at": "2026-10-25T00:00:00Z",
        "tool": "mcp__exa__web_fetch_exa",
        "content_sha256": hashlib.sha256(source_text.encode("utf-8")).hexdigest(),
        "text": source_text,
        "full_text_source": "verbatim",
        "captured_via": "inline",
        "query_provenance": "C3 residue control",
    }
    store = tmp_path / "store.jsonl"
    store.write_text(json.dumps(rec, ensure_ascii=False) + "\n", encoding="utf-8")
    draft_path = tmp_path / "draft.md"
    draft_path.write_text(draft, encoding="utf-8")
    out = subprocess.run(
        [sys.executable, str(_GATE), "--draft", str(draft_path), "--store", str(store), "--json"],
        capture_output=True, text=True,
        env={**os.environ, "PYTHONPATH": str(_AGENT_ASSURE)},
    )
    assert out.stdout, f"gate produced no stdout.\nstderr: {out.stderr}"
    return json.loads(out.stdout)


# ---------------------------------------------------------------- R27-02
_SIZE_FRAME = "The model weights occupy 16 {} on disk"
_SIZE_TAIL = ". The checkpoint ships with the release."


@pytest.mark.parametrize("src_unit,claim_unit", [("Mb", "MB"), ("MB", "Mb"), ("Gb", "GB"), ("kb", "KB")])
def test_r27_02_bits_never_ground_bytes(tmp_path: Path, src_unit: str, claim_unit: str) -> None:
    report = _gate(tmp_path, _SIZE_FRAME.format(src_unit) + _SIZE_TAIL,
                   _SIZE_FRAME.format(claim_unit) + " [S1].\n")
    assert report["gate"] != "PASS", report["per_claim"]


@pytest.mark.parametrize("unit", ["MB", "Mb", "GB"])
def test_r27_02_control_same_unit_grounds(tmp_path: Path, unit: str) -> None:
    report = _gate(tmp_path, _SIZE_FRAME.format(unit) + _SIZE_TAIL,
                   _SIZE_FRAME.format(unit) + " [S1].\n")
    assert report["gate"] == "PASS", report["per_claim"]
