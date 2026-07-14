"""OI-CAL-03 — labels are AUTHORED evidence and live apart from the SCAFFOLD.

PIR-002's root cause: one generator-owned file held machine-generated
scaffolding (claim text, evidence) AND irreplaceable human judgment
(`human_label`), so "regenerate the corpus" and "destroy the judgment" were the
same operation. The OI-CAL-02 guard stopped the destruction but froze the
corpus — it could no longer be extended once labeled.

The separation:

  * ``calibration/labeling-v2.csv``  — SCAFFOLD. Generator-owned, freely
    regenerable, carries NO human column. Nothing a human types lives here.
  * ``calibration/labels-v2.csv``    — LABELS. Human-owned. No generator has a
    function that writes it; ``init_labels`` creates it ONCE and refuses to
    overwrite. This is the only file a ratifier edits.

The loader (`load_gold_labels`) joins them on ``claim_id`` and enforces:

  1. every label is ``gold`` (a candidate must never tune a threshold);
  2. every labeled claim still EXISTS in the scaffold;
  3. **every label still matches the claim it was made against** — each row
     carries ``claim_sha``, a hash of the exact claim + evidence the human saw.
     If the corpus is regenerated and a claim's text changes, that label is
     STALE and the loader fails loud rather than silently applying a human's
     judgment to a claim they never read. **This property did not exist before
     OI-CAL-03** — a corpus edit could silently re-point a gold label.
"""

from __future__ import annotations

import csv

import pytest

from calibration.init_labels import claim_sha, init_labels
from scripts.calibrate import load_gold_labels

SCAFFOLD_HEADER = [
    "claim_id", "query_id", "claim_text", "evidence",
    "candidate_verdict", "rationale",
]


def _scaffold(path, rows: list[tuple[str, str, str]]) -> None:
    """rows: (claim_id, claim_text, evidence)"""
    with open(path, "w", encoding="utf-8", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(SCAFFOLD_HEADER)
        for cid, text, ev in rows:
            w.writerow([cid, cid.split("#")[0], text, ev, "grounded", "why"])


def _labels(path, rows: list[tuple[str, str, str, str]]) -> None:
    """rows: (claim_id, human_label, label_status, claim_sha)"""
    with open(path, "w", encoding="utf-8", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["claim_id", "human_label", "label_status", "claim_sha", "note"])
        for cid, label, status, sha in rows:
            w.writerow([cid, label, status, sha, ""])


# --- the scaffold carries no human input, so it is freely regenerable --------

def test_scaffold_has_no_human_column():
    """The generator-owned file must not contain a human_label column at all —
    that co-location is PIR-002's root cause."""
    with open("calibration/labeling-v2.csv", encoding="utf-8", newline="") as fh:
        header = next(csv.reader(fh))
    assert "human_label" not in header, (
        "the scaffold still holds human judgment — OI-CAL-03 regression"
    )
    assert "label_status" not in header


def test_real_labels_file_is_separate_and_complete():
    """Every scaffold claim has exactly one row in the human-owned labels file."""
    with open("calibration/labeling-v2.csv", encoding="utf-8", newline="") as fh:
        scaffold_ids = [r["claim_id"] for r in csv.DictReader(fh)]
    with open("calibration/labels-v2.csv", encoding="utf-8", newline="") as fh:
        label_ids = [r["claim_id"] for r in csv.DictReader(fh)]
    assert sorted(scaffold_ids) == sorted(label_ids)
    assert len(label_ids) == len(set(label_ids)), "duplicate claim_id in labels"


# --- init_labels: creates once, never clobbers ------------------------------

def test_init_labels_refuses_to_overwrite(tmp_path):
    """The one writer that touches the labels file must never overwrite it."""
    scaffold = tmp_path / "scaffold.csv"
    labels = tmp_path / "labels.csv"
    _scaffold(scaffold, [("q1#0", "claim one", "S1: evidence one")])
    init_labels(str(scaffold), str(labels))
    before = labels.read_text(encoding="utf-8")

    with pytest.raises(ValueError, match="already exists"):
        init_labels(str(scaffold), str(labels))

    assert labels.read_text(encoding="utf-8") == before


# --- the loader: gold-only, joined, and STALENESS-CHECKED -------------------

def test_gold_labels_load(tmp_path):
    scaffold = tmp_path / "s.csv"
    labels = tmp_path / "l.csv"
    _scaffold(scaffold, [("q1#0", "claim one", "S1: evidence one")])
    sha = claim_sha("claim one", "S1: evidence one")
    _labels(labels, [("q1#0", "grounded", "gold", sha)])

    out = load_gold_labels(str(labels), str(scaffold))
    assert out["q1#0"].label == "grounded"


def test_candidate_label_is_refused(tmp_path):
    """Calibration runs on gold only — the α1 gate, preserved through the split."""
    scaffold = tmp_path / "s.csv"
    labels = tmp_path / "l.csv"
    _scaffold(scaffold, [("q1#0", "claim one", "S1: evidence one")])
    sha = claim_sha("claim one", "S1: evidence one")
    _labels(labels, [("q1#0", "grounded", "candidate", sha)])

    with pytest.raises(ValueError, match="gold"):
        load_gold_labels(str(labels), str(scaffold))


def test_stale_label_fails_loud(tmp_path):
    """THE new property: the corpus changed under a gold label. The human
    judged a claim that no longer exists in that form — their judgment must
    NOT be silently transferred to the new text."""
    scaffold = tmp_path / "s.csv"
    labels = tmp_path / "l.csv"
    _scaffold(scaffold, [("q1#0", "claim one", "S1: evidence one")])
    sha = claim_sha("claim one", "S1: evidence one")
    _labels(labels, [("q1#0", "grounded", "gold", sha)])

    # Corpus regenerated; this claim's wording changed.
    _scaffold(scaffold, [("q1#0", "claim one, materially reworded", "S1: evidence one")])

    with pytest.raises(ValueError, match="stale"):
        load_gold_labels(str(labels), str(scaffold))


def test_label_for_unknown_claim_fails_loud(tmp_path):
    """A label whose claim vanished from the corpus is an error, not a no-op."""
    scaffold = tmp_path / "s.csv"
    labels = tmp_path / "l.csv"
    _scaffold(scaffold, [("q1#0", "claim one", "S1: evidence one")])
    _labels(labels, [("q9#0", "grounded", "gold", "deadbeef")])

    with pytest.raises(ValueError, match="not in the scaffold"):
        load_gold_labels(str(labels), str(scaffold))


def test_unlabeled_claim_fails_loud(tmp_path):
    """A scaffold claim with no label must not silently drop out of the
    calibration set — that would shrink n without anyone noticing."""
    scaffold = tmp_path / "s.csv"
    labels = tmp_path / "l.csv"
    _scaffold(
        scaffold,
        [("q1#0", "claim one", "S1: ev one"), ("q2#0", "claim two", "S2: ev two")],
    )
    sha = claim_sha("claim one", "S1: ev one")
    _labels(labels, [("q1#0", "grounded", "gold", sha)])

    with pytest.raises(ValueError, match="no label"):
        load_gold_labels(str(labels), str(scaffold))
