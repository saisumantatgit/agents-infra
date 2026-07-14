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


def test_v2_writer_cannot_destroy_labels_because_it_holds_none(tmp_path):
    """OI-CAL-03 supersedes the v2 half of the guard by REMOVING the hazard
    rather than blocking it: the v2 writer emits a derived SCAFFOLD with no
    human column, so a rebuild has nothing of the ratifier's to destroy — and
    the corpus stays extensible after ratification (which the guard alone had
    made impossible).

    The protection that used to live here now lives in two stronger places:
      * `calibration.init_labels` refuses to overwrite the labels file
        (tests/test_gold_labels_separation.py::test_init_labels_refuses_to_overwrite);
      * `load_gold_labels` fails loud on a STALE label — a judgment made
        against a claim whose text has since changed
        (…::test_stale_label_fails_loud).

    Here we assert the structural invariant that makes that safe: the writer
    emits no human column, so a rebuild is non-destructive by construction.
    """
    target = tmp_path / "labeling-v2.csv"
    write_labeling_v2_csv([], {}, str(target))

    with open(target, encoding="utf-8", newline="") as fh:
        header = next(csv.reader(fh))
    assert "human_label" not in header, (
        "the scaffold writer emits a human column again — PIR-002 regression: "
        "a rebuild could destroy ratified judgment"
    )
    assert "label_status" not in header


def test_bootstrap_writer_still_writes_when_target_absent(tmp_path):
    """The legacy guard must not block a legitimate first write."""
    target = tmp_path / "labeling.csv"
    write_enriched_labeling_csv([], {}, str(target))
    assert target.exists()
