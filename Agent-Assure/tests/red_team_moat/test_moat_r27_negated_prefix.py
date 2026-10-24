"""R27-01 (round 27, 2026-10-25): a NEGATED claim matching only the opening of a
source sentence whose next word limits it ("... no known side effects IN MICE")
certified PASS — a regression from B1, which moved negated claims into T1.
Also closes R27-01b's negated pre-existing cases."""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

_AA = Path(__file__).resolve().parents[2]


def _verdict(tmp_path, source, claim):
    rec = {"source_id": "S1", "url": "https://x.example/a", "file_path": None,
           "fetched_at": "1970-01-01T00:00:00Z", "tool": "mcp__exa__web_fetch_exa",
           "content_sha256": "0" * 64,
           "text": source + " The report was published by the national agency.",
           "full_text_source": "verbatim", "captured_via": "inline",
           "query_provenance": "q", "session_id": "s", "retrieval_status": "ok"}
    (tmp_path / "s.jsonl").write_text(json.dumps(rec) + "\n")
    (tmp_path / "d.md").write_text(claim + "\n")
    out = subprocess.run([sys.executable, str(_AA / "scripts/ground_check.py"),
                          "--draft", str(tmp_path / "d.md"), "--store",
                          str(tmp_path / "s.jsonl"), "--json"],
                         capture_output=True, text=True, cwd=str(_AA))
    return json.loads(out.stdout)["per_claim"][0]["verdict"]


CASES = [
    ("Drug X has no known side effects in mice; in humans it causes nausea.",
     "Drug X has no known side effects [S1]."),
    ("The trial caused no deaths among trial participants under 40, while three older participants died.",
     "The trial caused no deaths among trial participants [S1]."),
    ("The refinery no longer emits sulfur at night but still emits it by day.",
     "The refinery no longer emits sulfur [S1]."),
    ("The device was not approved by regulators until 2019.",
     "The device was not approved by regulators [S1]."),
    ("The database cannot lose committed data unless the disk fails.",
     "The database cannot lose committed data [S1]."),
]


@pytest.mark.parametrize("source,claim", CASES)
def test_a_negated_claim_cut_before_a_limiter_does_not_ground(tmp_path, source, claim):
    assert _verdict(tmp_path, source, claim) != "GROUNDED"


def test_POSITIVE_CONTROL_a_complete_negated_quote_still_grounds(tmp_path):
    src = "Drug X has no known side effects."
    assert _verdict(tmp_path, src, "Drug X has no known side effects [S1].") == "GROUNDED"
