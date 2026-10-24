"""C2 (2026-10-25): the hedge look-back must not cross a sentence boundary when
the claim is an exact copy of a source sentence. Honest cases were refused
(Error-A) because the previous sentence ended in a negator; the guards below are
Error-B shapes that must stay refused. Run through the real CLI."""
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
           "content_sha256": "0" * 64, "text": source,
           "full_text_source": "verbatim", "captured_via": "inline",
           "query_provenance": "q", "session_id": "s", "retrieval_status": "ok"}
    (tmp_path / "s.jsonl").write_text(json.dumps(rec) + "\n")
    (tmp_path / "d.md").write_text(claim + "\n")
    out = subprocess.run([sys.executable, str(_AA / "scripts/ground_check.py"),
                          "--draft", str(tmp_path / "d.md"), "--store",
                          str(tmp_path / "s.jsonl"), "--json"],
                         capture_output=True, text=True, cwd=str(_AA))
    return json.loads(out.stdout)["per_claim"][0]["verdict"]


HONEST = [
    ("The first rescue plan was not. The bank collapsed in March.",
     "The bank collapsed in March [S1]."),
    ("The drug did not work in mice. It cured most patients in the trial.",
     "It cured most patients in the trial [S1]."),
    ("The audit found no errors. The firm filed its accounts on time.",
     "The firm filed its accounts on time [S1]."),
    ("Long-term data were not available! Mortality fell by a third in 2020.",
     "Mortality fell by a third in 2020 [S1]."),
]

GUARDS = [
    # (1) denial in the same sentence, and a whole-sentence falsity verdict
    ("It is not true that the bank collapsed in March.",
     "The bank collapsed in March [S1]."),
    ("It is not true. The bank collapsed in March.",
     "The bank collapsed in March [S1]."),
    ("It is not true, the bank collapsed in March.",
     "The bank collapsed in March [S1]."),
    ("That is not the case. The bank collapsed in March.",
     "The bank collapsed in March [S1]."),
    ("According to the vendor, the bank collapsed in March.",
     "The bank collapsed in March [S1]."),
    # (2) a colon is not a boundary
    ("The following claim is false: the bank collapsed in March.",
     "The bank collapsed in March [S1]."),
    ("The following claim is false: The bank collapsed in March.",
     "The bank collapsed in March [S1]."),
    # (3) a list item governed by its lead-in line: a newline is not a boundary
    ("These are not facts:\n- The bank collapsed in March",
     "The bank collapsed in March [S1]."),
    ("Not true.\nThe bank collapsed in March.",
     "The bank collapsed in March [S1]."),
    # (4) attribution across the boundary still refuses
    ("Critics claimed collapse. Collapse.", "Collapse [S1]."),
    ("Critics claimed it collapsed. It collapsed.", "It collapsed [S1]."),
    ("That is false. The bank collapsed in March.",
     "The bank collapsed in March [S1]."),
    # mid-sentence span after a boundary keeps today's behaviour
    ("He was not. Then the bank collapsed in March.",
     "The bank collapsed in March [S1]."),
]


@pytest.mark.parametrize("source,claim", HONEST)
def test_exact_sentence_after_negated_sentence_grounds(tmp_path, source, claim):
    assert _verdict(tmp_path, source, claim) == "GROUNDED"


@pytest.mark.parametrize("source,claim", GUARDS)
def test_error_b_guards_still_refuse(tmp_path, source, claim):
    assert _verdict(tmp_path, source, claim) != "GROUNDED"


# (3) PRE-EXISTING HOLE, not created or closed by C2: "myths" (plural) is not in
# _SPAN_HEDGE_TOKENS and the window holds no other hedge, so this grounds on the
# pre-C2 code too. C2 cannot touch it (no sentence boundary is involved). Left
# strict-xfail for Sai's ruling rather than widening the blacklist here.
@pytest.mark.xfail(strict=True, reason="pre-existing: 'myths' not a hedge token")
def test_myths_list_lead_in_refuses(tmp_path):
    assert _verdict(tmp_path, "Myths:\n- the bank collapsed in March",
                    "The bank collapsed in March [S1].") != "GROUNDED"
