"""W2B-01..05 — a figure's QUALIFIERS are part of the figure.

Red team W2B (reports/RED-TEAM-W2B-NUMERIC-2026-10-24.md): the numeric regexes
start at the first digit, so everything written in front of it was thrown
away. A source's `-12%` grounded a claim of `12%`; `~40%`, `>40%`, `≤4%`
grounded a bare `40%`/`4%`; `¥40M` grounded `$40M`; `.5%` grounded `5%`; `4‰`
grounded a bare `4`. Every one certified PASS 100.0.

The fix parses a figure as VALUE + QUALIFIERS (sign, comparator, currency,
leading decimal point, per-mille) and requires the qualifier sets to be EQUAL
on both sides. Fail-closed: it only adds a condition to a match.

Run through the real CLI, as a user would.
"""

from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
GROUND_CHECK = str(REPO_ROOT / "scripts" / "ground_check.py")

TAIL = " in 2023 according to the annual report"


def _verdict(tmp_path: Path, source_text: str, claim_text: str) -> tuple[int, str]:
    rec = {
        "source_id": "S1",
        "url": "https://example.com/s1",
        "file_path": None,
        "fetched_at": "2026-10-24T00:00:00Z",
        "tool": "mcp__exa__web_fetch_exa",
        "content_sha256": hashlib.sha256(source_text.encode("utf-8")).hexdigest(),
        "text": source_text,
        "full_text_source": "verbatim",
        "captured_via": "inline",
        "query_provenance": "W2B figure-qualifier control",
    }
    store = tmp_path / "store.jsonl"
    store.write_text(json.dumps(rec, ensure_ascii=False) + "\n", encoding="utf-8")
    draft = tmp_path / "draft.md"
    draft.write_text(f"{claim_text} [S1].\n", encoding="utf-8")
    env = {**os.environ, "PYTHONPATH": str(REPO_ROOT)}
    out = subprocess.run(
        [sys.executable, GROUND_CHECK, "--draft", str(draft), "--store", str(store), "--json"],
        capture_output=True, text=True, env=env,
    )
    assert out.stdout, f"gate produced no stdout.\nstderr: {out.stderr}"
    scored = [c for c in json.loads(out.stdout)["per_claim"] if c["kind"] != "NON_CLAIM"]
    assert len(scored) == 1, scored
    return out.returncode, scored[0]["verdict"]


def _pair(src_fig: str, claim_fig: str, frame: str = "Acme posted a net margin of {}") -> tuple[str, str]:
    # The source carries an extra sentence so it is never byte-identical to the
    # draft (J-83 would then refuse it as a self-citation, masking the check).
    return (frame.format(src_fig) + TAIL + ". Figures are unaudited.", frame.format(claim_fig) + TAIL)


ATTACKS = [
    pytest.param(*_pair("-12%", "12%"), id="W2B-01-hyphen-minus"),
    pytest.param(*_pair("−12%", "12%"), id="W2B-01-unicode-minus"),
    pytest.param(*_pair("~40%", "40%"), id="W2B-02-tilde"),
    pytest.param(*_pair(">40%", "40%"), id="W2B-02-greater"),
    pytest.param(*_pair("<4%", "4%"), id="W2B-02-less"),
    pytest.param(*_pair("≈40%", "40%"), id="W2B-02-approx"),
    pytest.param(*_pair("≤4%", "4%"), id="W2B-02-leq"),
    pytest.param(*_pair("±40%", "40%"), id="W2B-02-plusminus"),
    pytest.param(*_pair("¥40M", "$40M", "Acme raised {}"), id="W2B-03-yen-vs-dollar"),
    pytest.param(*_pair("€40M", "$40M", "Acme raised {}"), id="W2B-03-euro-vs-dollar"),
    pytest.param(*_pair("₹40M", "$40M", "Acme raised {}"), id="W2B-03-rupee-vs-dollar"),
    pytest.param(*_pair("£40M", "$40M", "Acme raised {}"), id="W2B-03-pound-vs-dollar"),
    pytest.param(*_pair(".5%", "5%", "Acme said {} of users churned"), id="W2B-04-leading-point"),
    pytest.param(*_pair("4‰", "4", "Acme reported a defect rate of {}"), id="W2B-05-per-mille"),
    pytest.param(*_pair("12%", "-12%"), id="symmetric-claim-adds-sign"),
    pytest.param(*_pair("40%", "~40%"), id="symmetric-claim-adds-comparator"),
]


@pytest.mark.parametrize("source_text,claim_text", ATTACKS)
def test_source_qualifier_dropped_by_claim_is_refused(
    tmp_path: Path, source_text: str, claim_text: str
) -> None:
    code, verdict = _verdict(tmp_path, source_text, claim_text)
    assert verdict != "GROUNDED", (source_text, claim_text, verdict)
    assert code != 0


CONTROLS = [
    pytest.param(*_pair("-12%", "-12%"), id="minus-both-sides"),
    pytest.param(*_pair("~40%", "~40%"), id="tilde-both-sides"),
    pytest.param(*_pair("€40M", "€40M", "Acme raised {}"), id="euro-both-sides"),
    pytest.param(*_pair("$40M", "$40M", "Acme raised {}"), id="dollar-both-sides"),
    pytest.param(*_pair("12%", "12%"), id="no-qualifier-either-side"),
]


@pytest.mark.parametrize("source_text,claim_text", CONTROLS)
def test_same_qualifier_both_sides_still_grounds(
    tmp_path: Path, source_text: str, claim_text: str
) -> None:
    code, verdict = _verdict(tmp_path, source_text, claim_text)
    assert verdict == "GROUNDED", (source_text, claim_text, verdict)
    assert code == 0
