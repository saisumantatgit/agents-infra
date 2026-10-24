"""S1 — W2C-01 fixed without reopening R29-01, driven through the real CLI.

* W2C-01: a comment inside a closed <textarea>/<xmp> under a heading renders
  visibly; it must be SCORED, not stripped.
* R29-01: a citation marker inside ANY <!-- --> must never count — not after an
  unclosed <title>, not inside a closed <textarea>, not in a multi-line comment.
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

_SRC = ("In 2025 Acme reported revenue of 40 million dollars for the fiscal year. "
        "The company is headquartered in Ohio.")
_CLAIM = "In 2025 Acme reported revenue of 40 million dollars"


def _gate(tmp_path: Path, draft: str) -> dict:
    rec = {
        "source_id": "S1", "url": "https://example.com/s1", "file_path": None,
        "fetched_at": "2026-10-25T00:00:00Z", "tool": "mcp__exa__web_fetch_exa",
        "content_sha256": hashlib.sha256(_SRC.encode("utf-8")).hexdigest(),
        "text": _SRC, "full_text_source": "verbatim", "captured_via": "inline",
        "query_provenance": "S1 comment citations",
    }
    store = tmp_path / "store.jsonl"
    store.write_text(json.dumps(rec) + "\n", encoding="utf-8")
    draft_path = tmp_path / "draft.md"
    draft_path.write_text(draft, encoding="utf-8")
    out = subprocess.run(
        [sys.executable, str(_GATE), "--draft", str(draft_path), "--store", str(store), "--json"],
        capture_output=True, text=True, env={**os.environ, "PYTHONPATH": str(_AGENT_ASSURE)},
    )
    assert out.stdout, out.stderr
    return json.loads(out.stdout)


@pytest.mark.parametrize("element", ["textarea readonly", "xmp", "TEXTAREA"])
def test_w2c_01_comment_inside_raw_text_element_is_scored(tmp_path: Path, element: str) -> None:
    tag = element.split()[0]
    draft = (_CLAIM + " [S1].\n\n## Key Data <" + element
             + "><!-- PostgreSQL loses all committed data on restart. --></" + tag + ">\n")
    report = _gate(tmp_path, draft)
    assert report["gate"] != "PASS", report["per_claim"]
    assert any("PostgreSQL" in c["text"] and c["kind"] != "NON_CLAIM"
               for c in report["per_claim"]), report["per_claim"]


@pytest.mark.parametrize("draft", [
    # R29-01 exact: unclosed <title>, later hidden citation.
    "The annual report carried the <title> Freight Outlook [S1].\n\n"
    + _CLAIM + " <!-- [S1] -->.\n",
    # R29 d4a: closed textarea around the hidden citation.
    _CLAIM + " <textarea><!-- [S1] --></textarea>.\n",
    # multi-line comment (never stripped) carrying a citation.
    _CLAIM + " <!--\n[S1]\n-->.\n",
    # full-width marker that NFKC folds to [S1].
    _CLAIM + " <!--\n［S1］\n-->.\n",
], ids=["r29-01-unclosed-title", "closed-textarea", "multi-line", "full-width"])
def test_citation_inside_comment_never_counts(tmp_path: Path, draft: str) -> None:
    report = _gate(tmp_path, draft)
    assert report["gate"] != "PASS", report["per_claim"]
    rev = [c for c in report["per_claim"] if "revenue" in c["text"]]
    assert rev and all(not c.get("citations") for c in rev), report["per_claim"]


def test_control_visible_citation_still_grounds(tmp_path: Path) -> None:
    report = _gate(tmp_path, _CLAIM + " [S1].\n\n<!-- editor note: check later -->\n")
    assert report["gate"] == "PASS", report["per_claim"]


def test_R30_a_citation_after_a_bang_closed_comment_stays_visible(tmp_path):
    """Round 30: `<!-- a --!> [S1].` — browsers end the comment at `--!>`, so the
    [S1] is visible and must count. The scrubber used to read on and delete it."""
    import json, subprocess, sys
    from pathlib import Path
    aa = Path(__file__).resolve().parents[2]
    src = ("Redis sustained approximately 128000 operations per second in the "
           "benchmark. The test ran on a single node.")
    rec = {"source_id": "S1", "url": "https://x.example/a", "file_path": None,
           "fetched_at": "1970-01-01T00:00:00Z", "tool": "mcp__exa__web_fetch_exa",
           "content_sha256": "0" * 64, "text": src, "full_text_source": "verbatim",
           "captured_via": "inline", "query_provenance": "q", "session_id": "s",
           "retrieval_status": "ok"}
    (tmp_path / "s.jsonl").write_text(json.dumps(rec) + "\n")
    (tmp_path / "d.md").write_text("Redis sustained approximately 128000 operations "
                                   "per second <!-- a --!> [S1].\n")
    out = subprocess.run([sys.executable, str(aa / "scripts/ground_check.py"), "--draft",
                          str(tmp_path / "d.md"), "--store", str(tmp_path / "s.jsonl"),
                          "--json"], capture_output=True, text=True, cwd=str(aa))
    assert json.loads(out.stdout)["per_claim"][0]["verdict"] != "UNCITED"
