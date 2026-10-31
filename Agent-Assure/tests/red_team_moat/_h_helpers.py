"""Shared CLI driver for the H1-H5 hardening tests (2026-10-25). Pure helper:
writes a one-record store and a draft under tmp_path and returns the gate's
JSON report from the real CLI."""
from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path

AA = Path(__file__).resolve().parents[2]
GATE = AA / "scripts" / "ground_check.py"

CLAIM = "The regional bank collapsed in March after the regulator completed its audit"
TAIL = " The regulator published its findings in June."
DRAFT = CLAIM + " [S1].\n"


def gate(tmp_path: Path, source_text: str, draft: str = DRAFT) -> dict:
    rec = {
        "source_id": "S1", "url": "https://example.com/s1", "file_path": None,
        "fetched_at": "2026-10-25T00:00:00Z", "tool": "mcp__exa__web_fetch_exa",
        "content_sha256": hashlib.sha256(source_text.encode("utf-8")).hexdigest(),
        "text": source_text, "full_text_source": "verbatim",
        "captured_via": "inline", "query_provenance": "H-hardening",
    }
    store = tmp_path / "store.jsonl"
    store.write_text(json.dumps(rec, ensure_ascii=False) + "\n", encoding="utf-8")
    draft_path = tmp_path / "draft.md"
    draft_path.write_text(draft, encoding="utf-8")
    out = subprocess.run(
        [sys.executable, str(GATE), "--draft", str(draft_path), "--store", str(store), "--json"],
        capture_output=True, text=True, env={**os.environ, "PYTHONPATH": str(AA)},
    )
    assert out.stdout, f"gate produced no stdout.\nstderr: {out.stderr}"
    return json.loads(out.stdout)
