"""OI-CAL-02 — a corpus rebuild must never destroy human labels.

`build_corpus.py` / `build_corpus_v2.py` regenerate their labeling CSV on every
run, writing a blank (or candidate) `human_label` column. Ratified labels are
AUDIT EVIDENCE and cannot be regenerated: a rebuild after ratification silently
destroys them.

This is not hypothetical. On 2026-07-14 a routine corpus regeneration blanked
the n=12 bootstrap labels that CR-001 was calibrated on; only the fail-loud
label LOADER (which refused to calibrate on empty labels) surfaced it, and the
file was restored from git. Post-ratification the same keystroke would destroy
Sai's n=52 gold labels.

Rule: the writer refuses to overwrite a labeling CSV that carries ANY human
label, and says exactly which file and how many labels it is protecting.
(Fail loud, never fallback — the store and the labels are audit evidence.)

INS-005: proven red against the pre-guard writers (both tests failed — the
writers happily clobbered a labeled file); red output in the 2026-07-14 logbook.
"""

from __future__ import annotations

import csv

import pytest

from calibration.build_corpus import write_enriched_labeling_csv
from calibration.build_corpus_v2 import write_labeling_v2_csv


def _write_labeled_csv(path, header: list[str], label_col: str, label: str) -> None:
    """Write a CSV that already carries a human label in `label_col`."""
    row = {c: f"x-{c}" for c in header}
    row[label_col] = label
    with open(path, "w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=header)
        writer.writeheader()
        writer.writerow(row)


def test_bootstrap_writer_refuses_to_clobber_human_labels(tmp_path):
    """write_enriched_labeling_csv must not overwrite a labeled CSV."""
    target = tmp_path / "labeling.csv"
    _write_labeled_csv(
        target,
        ["claim_id", "query_id", "claim_text", "evidence", "human_label"],
        "human_label",
        "violation",
    )
    before = target.read_text(encoding="utf-8")

    with pytest.raises(ValueError, match="human label"):
        write_enriched_labeling_csv([], {}, str(target))

    assert target.read_text(encoding="utf-8") == before, "labels were destroyed"


def test_v2_writer_refuses_to_clobber_gold_labels(tmp_path):
    """write_labeling_v2_csv must not overwrite Sai's ratified gold labels —
    the exact scenario that would hit the first time anyone regenerates the
    corpus after α1 ratification."""
    target = tmp_path / "labeling-v2.csv"
    _write_labeled_csv(
        target,
        [
            "claim_id", "query_id", "claim_text", "evidence", "human_label",
            "candidate_verdict", "rationale", "label_status",
        ],
        "human_label",
        "grounded",
    )
    before = target.read_text(encoding="utf-8")

    with pytest.raises(ValueError, match="human label"):
        write_labeling_v2_csv([], {}, str(target))

    assert target.read_text(encoding="utf-8") == before, "GOLD labels were destroyed"


def test_writer_still_writes_when_target_absent(tmp_path):
    """The guard must not block a legitimate first write."""
    target = tmp_path / "labeling-v2.csv"
    write_labeling_v2_csv([], {}, str(target))
    assert target.exists()
