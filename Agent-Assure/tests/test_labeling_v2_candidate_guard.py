"""Fail-loud guard: the calibration loader must REFUSE candidate labels.

Phase α1 emits calibration/labeling-v2.csv with label_status=candidate on
every row — a package Sai has not yet ratified. Calibration runs on GOLD
labels only: ingesting candidate labels would tune thresholds on unratified
data, exactly the silent corruption the fail-loud doctrine forbids.

scripts.calibrate.load_labels enforces this: when a labeling CSV carries a
``label_status`` column, every row's value must be ``gold`` (after NFKC
normalization) or load_labels raises ValueError naming the rule. Legacy files
with NO label_status column are unaffected (backward-compatible) — the
original bootstrap labeling.csv still loads.

RED-FIRST: against the pre-change loader (no label_status check), a candidate
CSV whose human_label cells are validly filled loads WITHOUT raising, so both
tests below fail. That failure is the proof the guard did not exist; the
loader change makes them pass.
"""

from __future__ import annotations

import csv
from pathlib import Path

import pytest

from scripts.calibrate import load_labels

_LABELING_V2 = Path(__file__).resolve().parents[1] / "calibration" / "labeling-v2.csv"

_HEADER = [
    "claim_id", "query_id", "claim_text", "evidence",
    "human_label", "candidate_verdict", "rationale", "label_status",
]


def _write(path: Path, rows: list[list[str]]) -> None:
    with open(path, "w", encoding="utf-8", newline="") as fh:
        writer = csv.writer(fh)
        writer.writerow(_HEADER)
        writer.writerows(rows)


def test_load_labels_rejects_candidate_status(tmp_path):
    """A CSV with label_status=candidate is refused, naming the gold rule."""
    csv_path = tmp_path / "candidate.csv"
    _write(csv_path, [
        ["q1#0", "q1", "A claim [S1].", "S1: ...", "grounded", "grounded",
         "looks supported", "candidate"],
        ["q2#0", "q2", "Another [S2].", "S2: ...", "violation", "violation",
         "unsupported", "candidate"],
    ])
    with pytest.raises(ValueError) as exc:
        load_labels(str(csv_path))
    msg = str(exc.value).lower()
    assert "gold" in msg
    assert "label_status" in msg or "candidate" in msg


def test_load_labels_accepts_gold_status(tmp_path):
    """The SAME rows with label_status=gold load cleanly — the guard gates on
    status, not on the mere presence of the column."""
    csv_path = tmp_path / "gold.csv"
    _write(csv_path, [
        ["q1#0", "q1", "A claim [S1].", "S1: ...", "grounded", "grounded",
         "looks supported", "gold"],
        ["q2#0", "q2", "Another [S2].", "S2: ...", "violation", "violation",
         "unsupported", "gold"],
    ])
    labels = load_labels(str(csv_path))
    assert set(labels) == {"q1#0", "q2#0"}
    assert labels["q1#0"].label == "grounded"
    assert labels["q2#0"].label == "violation"


def test_real_labeling_v2_is_rejected_while_candidate():
    """The actual α1 package is refused until ratified.

    Skips (rather than fails) once Sai has flipped every row to gold, so this
    test documents the α1 gate without breaking after ratification.
    """
    assert _LABELING_V2.exists(), f"missing {_LABELING_V2}"
    with open(_LABELING_V2, encoding="utf-8", newline="") as fh:
        statuses = {(r.get("label_status") or "").strip() for r in csv.DictReader(fh)}
    if statuses == {"gold"}:
        pytest.skip("labeling-v2.csv already ratified (all rows gold)")
    with pytest.raises(ValueError) as exc:
        load_labels(str(_LABELING_V2))
    assert "gold" in str(exc.value).lower()
