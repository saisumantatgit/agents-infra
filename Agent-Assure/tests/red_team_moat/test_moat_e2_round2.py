"""The 45 v2 honest controls and disowned sentence heading regression."""
import json
import os
from pathlib import Path

import pytest

from tests.red_team_moat import _h_helpers as helpers

CORPUS = Path(__file__).resolve().parents[1] / "error_b_corpus_v2"
CLASSES = {"denied_after", "heading_from_source_words_verbatim",
           "heading_from_source_words_reassembled"}
ROWS = [r for r in json.loads((CORPUS / "manifest.json").read_text())
        if r["class"] in CLASSES]


@pytest.fixture(autouse=True)
def checker_override(monkeypatch):
    if os.environ.get("E2_GATE_PATH"):
        monkeypatch.setattr(helpers, "GATE", Path(os.environ["E2_GATE_PATH"]))


@pytest.mark.parametrize("row", ROWS, ids=lambda row: row["id"])
def test_honest_control(tmp_path, row):
    report = helpers.gate(tmp_path, (CORPUS / row["source"]).read_text(),
                          draft=(CORPUS / "controls" / f"{row['id']}.md").read_text())
    assert report["per_claim"][0]["kind"] == "NON_CLAIM", report
    assert report["gate"] == "PASS", report


def test_disowned_verbatim_sentence(tmp_path):
    body = "The board met in April and published its minutes online"
    source = body + ". The regulator found fraud at Quay Trust. That never happened."
    report = helpers.gate(tmp_path, source, draft="## The regulator found fraud at Quay Trust\n\n" + body + " [S1].\n")
    assert report["per_claim"][0]["kind"] != "NON_CLAIM", report
    assert report["gate"] != "PASS", report
