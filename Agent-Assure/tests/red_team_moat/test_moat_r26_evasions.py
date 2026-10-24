"""Round 26 (2026-10-24): two evasions of tonight's fixes, both closed.

R26-01: a word borrowed from the next LINE / a ";" clause / a "(...)" aside
counted as the same source sentence (W2A's fix). R26-02: a qualifier separated
from its digit by whitespace or a zero-width character was dropped (W2B's fix).
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

_AA = Path(__file__).resolve().parents[2]


def _gate(tmp_path, source, claim):
    rec = {"source_id": "S1", "url": "https://x.example/a", "file_path": None,
           "fetched_at": "1970-01-01T00:00:00Z", "tool": "mcp__exa__web_fetch_exa",
           "content_sha256": "0" * 64, "text": source,
           "full_text_source": "verbatim", "captured_via": "inline",
           "query_provenance": "q", "session_id": "s", "retrieval_status": "ok"}
    (tmp_path / "s.jsonl").write_text(json.dumps(rec) + "\n")
    (tmp_path / "d.md").write_text(claim + "\n")
    out = subprocess.run([sys.executable, str(_AA / "scripts/ground_check.py"),
                          "--draft", str(tmp_path / "d.md"), "--store",
                          str(tmp_path / "s.jsonl"), "--json"],
                         capture_output=True, text=True, cwd=str(_AA))
    return json.loads(out.stdout)


_BASE = ("The managed relational database service operated by the regional "
         "provider recorded the lowest replication lag in the benchmark")


@pytest.mark.parametrize("sep", ["\n", "; ", " ("])
def test_R26_01_a_word_from_the_next_line_or_clause_cannot_cover(tmp_path, sep):
    source = (f"{_BASE} for Aurora{sep}Spanner was also evaluated"
              + (")" if sep == " (" else "") + ".")
    claim = f"{_BASE} for Spanner [S1]."
    assert _gate(tmp_path, source, claim)["gate"] != "PASS"


@pytest.mark.parametrize("q", ["- ", " -", "-​", "~ ", "± "])
def test_R26_02_a_spaced_qualifier_still_counts(tmp_path, q):
    source = f"Quarterly operating margin at the Frankfurt desk moved {q}12% year on year."
    claim = "Quarterly operating margin at the Frankfurt desk moved 12% year on year [S1]."
    assert _gate(tmp_path, source, claim)["gate"] != "PASS"


def test_POSITIVE_CONTROL_same_sentence_same_qualifier_still_grounds(tmp_path):
    # The source must be a real document, not the draft's own sentence: a
    # source identical to the draft is (correctly) refused as the draft itself
    # (J-83). The first version of this control made exactly that mistake.
    source = ("Quarterly operating margin at the Frankfurt desk moved -12% year on "
              "year. The desk's headcount was unchanged over the same period.")
    claim = "Quarterly operating margin at the Frankfurt desk moved -12% year on year [S1]."
    assert _gate(tmp_path, source, claim)["per_claim"][0]["verdict"] == "GROUNDED"
