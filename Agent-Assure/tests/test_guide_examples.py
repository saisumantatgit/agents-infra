"""The tester guide's examples are RUN, so the guide cannot give advice the gate refuses.

2026-10-25: the guide shipped a quoting example that FAILED (UNGROUNDED) — written
without being run. Every example tagged `<!-- guide-example: GROUNDED|REFUSED -->`
in docs/ALPHA-TESTER-GUIDE.md is executed here against the stated source.
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

_AA = Path(__file__).resolve().parents[1]
_GUIDE = _AA / "docs" / "ALPHA-TESTER-GUIDE.md"
_SOURCE = ("The 2025 internal audit identified material weaknesses in custodial "
           "reconciliation at the Frankfurt desk during the third quarter. "
           "Remediation is scheduled for the second quarter.")
_TAG = re.compile(r"<!-- guide-example: (GROUNDED|REFUSED) -->\s*\n`([^`]+)`")


def _verdict(tmp_path, claim):
    rec = {"source_id": "S1", "url": "https://x.example/a", "file_path": None,
           "fetched_at": "1970-01-01T00:00:00Z", "tool": "mcp__exa__web_fetch_exa",
           "content_sha256": "0" * 64, "text": _SOURCE,
           "full_text_source": "verbatim", "captured_via": "inline",
           "query_provenance": "q", "session_id": "s", "retrieval_status": "ok"}
    (tmp_path / "s.jsonl").write_text(json.dumps(rec) + "\n")
    (tmp_path / "d.md").write_text(claim + "\n")
    out = subprocess.run([sys.executable, str(_AA / "scripts/ground_check.py"),
                          "--draft", str(tmp_path / "d.md"), "--store",
                          str(tmp_path / "s.jsonl"), "--json"],
                         capture_output=True, text=True, cwd=str(_AA))
    return json.loads(out.stdout)["per_claim"][0]["verdict"]


def test_the_guide_has_examples():
    assert len(_TAG.findall(_GUIDE.read_text())) >= 2


def test_every_guide_example_behaves_as_the_guide_says(tmp_path):
    for expected, claim in _TAG.findall(_GUIDE.read_text()):
        got = _verdict(tmp_path, claim)
        if expected == "GROUNDED":
            assert got == "GROUNDED", f"guide says this passes, gate says {got}: {claim}"
        else:
            assert got != "GROUNDED", f"guide says this is refused, gate grounds it: {claim}"
