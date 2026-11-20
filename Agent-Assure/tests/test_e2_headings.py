"""E2: headings cannot disappear merely because they reuse source vocabulary."""
import os
from pathlib import Path
import pytest
from tests.red_team_moat import _h_helpers as h

h.GATE = Path(os.environ.get("E2_GATE", str(h.GATE)))
BODY = "The board published its annual report in June"
SOURCE = BODY + ".\n\nThe regulator found fraud at Quay Trust. That never happened. Quay Trust hid the failures. The council never met."
HEADINGS = ["The regulator found fraud at Quay Trust", "Fraud at Quay Trust",
            "Quay Trust hid the failures", "Regulator: fraud at Quay Trust",
            "The council never met"]

@pytest.mark.parametrize("heading", HEADINGS)
@pytest.mark.parametrize("style", ["#", "##", "###", "####", "#####", "######", "setext1", "setext2", "end"])
def test_heading_is_scored(tmp_path, heading, style):
    if style.startswith("setext"):
        line = heading + "\n" + ("===" if style == "setext1" else "---")
    else:
        line = ("##" if style == "end" else style) + " " + heading
    body = BODY + " [S1]."
    draft = body + "\n\n" + line if style == "end" else line + "\n\n" + body
    report = h.gate(tmp_path, SOURCE, draft=draft)
    assert report["gate"] != "PASS", report
    if style.startswith("setext"):
        assert any(c["text"] == "## " + heading and c["kind"] != "NON_CLAIM" for c in report["per_claim"]), report

@pytest.mark.parametrize("heading,source", [("Overview", SOURCE), ("Next steps", SOURCE),
    ("Project architecture", "## Project architecture\n\n" + SOURCE)])
def test_honest_heading_controls(tmp_path, heading, source):
    report = h.gate(tmp_path, source, draft="## " + heading + "\n\n" + BODY + " [S1].")
    assert report["gate"] == "PASS", report
