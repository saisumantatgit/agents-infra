"""B2 (D-97, 2026-10-25): figures vs identifiers, storage units, punctuation.

Honest claims were refused UNVERIFIED_NUMBER because the figure extractor read
digits inside identifiers as quantities ("X200 manual" -> "200 m", J-72) and a
storage unit as a magnitude ("16 MB" -> "16 M"). The fix treats an identifier
as ONE token matched exactly (whole word) and a byte unit as a unit.

Authorised PASS-enabling change; Error-B must not rise. So every honest case
below was RED before the fix, and every attack is refused before AND after.
All through the real CLI.
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

_AA = Path(__file__).resolve().parents[2]
_TAIL = " Afterwards the operator confirmed the workspace was clean and logged the result."


def _verdict(tmp_path, source, claim):
    rec = {"source_id": "S1", "url": "https://x.example/a", "file_path": None,
           "fetched_at": "1970-01-01T00:00:00Z", "tool": "mcp__exa__web_fetch_exa",
           "content_sha256": "0" * 64, "text": source + _TAIL,
           "full_text_source": "verbatim", "captured_via": "inline",
           "query_provenance": "q", "session_id": "s", "retrieval_status": "ok"}
    (tmp_path / "s.jsonl").write_text(json.dumps(rec) + "\n")
    (tmp_path / "d.md").write_text(claim + "\n")
    out = subprocess.run([sys.executable, str(_AA / "scripts/ground_check.py"),
                          "--draft", str(tmp_path / "d.md"), "--store",
                          str(tmp_path / "s.jsonl"), "--json"],
                         capture_output=True, text=True, cwd=str(_AA))
    return json.loads(out.stdout)["per_claim"][0]["verdict"]


# --- honest: RED before the fix (UNVERIFIED_NUMBER), GROUNDED after ---------

def test_HONEST_identifier_followed_by_a_word_is_not_a_quantity(tmp_path):
    # Pre-fix: "X200 manual" -> "200 m" (200 million) vs the source's 200.
    src = ("The field team flew the survey with the X200 and its manual mode "
           "enabled over the quarry.")
    claim = "The field team flew the survey with the X200 manual mode enabled over the quarry [S1]."
    assert _verdict(tmp_path, src, claim) == "GROUNDED"


def test_CONTROL_storage_unit_in_words_is_not_refused_as_a_figure(tmp_path):
    # NOT a red-before case: pre-fix the lexical tier already refused it
    # UNGROUNDED before the figure check ran. Post-fix the figure verifies (MB == megabytes); the
    # claim is still refused UNGROUNDED by the lexical tier ("mb" is not
    # "megabytes"), so this pins only that the FIGURE is no longer the refusal.
    src = "The release notes say the cache was capped at 16 megabytes on every worker node in the fleet."
    claim = "The release notes say the cache was capped at 16 MB on every worker node in the fleet [S1]."
    assert _verdict(tmp_path, src, claim) not in ("GROUNDED", "UNVERIFIED_NUMBER")


# --- Error-B guard: refused before AND after --------------------------------

@pytest.mark.parametrize("source_id,claim_id", [
    ("X200", "X300"), ("GPT-4", "GPT-5"), ("ac77b8e", "ac77b8f"),
    ("ISO-27001", "ISO-27002"), ("T5", "T6"),
])
def test_ATTACK_a_wrong_identifier_is_refused(tmp_path, source_id, claim_id):
    src = f"The C1 change to the capture layer was validated against {source_id} on the main branch."
    claim = f"The C1 change to the capture layer was validated against {claim_id} on the main branch [S1]."
    assert _verdict(tmp_path, src, claim) != "GROUNDED"


@pytest.mark.parametrize("source_id", ["GPT-4o", "X2000"])
def test_ATTACK_an_identifier_is_matched_whole_word(tmp_path, source_id):
    claim_id = source_id[:-1]
    src = f"The C1 change to the capture layer was validated against {source_id} on the main branch."
    claim = f"The C1 change to the capture layer was validated against {claim_id} on the main branch [S1]."
    assert _verdict(tmp_path, src, claim) != "GROUNDED"


@pytest.mark.parametrize("source_fig", ["16 GB", "16 million", "16M", "16 KiB", "16"])
def test_ATTACK_16_MB_does_not_ground_another_unit(tmp_path, source_fig):
    src = f"The release notes say the cache was capped at {source_fig} on every worker node in the fleet."
    claim = "The release notes say the cache was capped at 16 MB on every worker node in the fleet [S1]."
    assert _verdict(tmp_path, src, claim) != "GROUNDED"


def test_ATTACK_identifier_digits_in_a_source_do_not_ground_a_bare_figure(tmp_path):
    src = "The field team flew the X200 over the quarry and logged every survey pass."
    claim = "The field team flew 200 drones over the quarry and logged every survey pass [S1]."
    assert _verdict(tmp_path, src, claim) != "GROUNDED"


# --- controls ---------------------------------------------------------------

def test_CONTROL_trailing_punctuation_is_not_part_of_a_figure(tmp_path):
    src = "The audit team filed 20 findings and 1 waiver across the three review rounds of the capture layer."
    claim = "The audit team filed 20, findings and 1 waiver across the three review rounds of the capture layer [S1]."
    assert _verdict(tmp_path, src, claim) == "GROUNDED"


def test_CONTROL_right_identifier_and_figure_still_ground(tmp_path):
    src = "Used as a zero-shot judge on the benchmark, GPT-4 reaches 75.3% balanced accuracy on held-out data."
    claim = "Used as a zero-shot judge on the benchmark, GPT-4 reaches 75.3% balanced accuracy on held-out data [S1]."
    assert _verdict(tmp_path, src, claim) == "GROUNDED"
