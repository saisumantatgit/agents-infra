# Phase α1 Execution Report — Gold-Label Ratification Package

**Executor:** Opus 4.8 · **Date:** 2026-07-08 · **Plan:** ALPHA-READINESS-PLAN.md §α1
**Status:** COMPLETE (all deliverables shipped; awaiting Sai ratification to unblock α2)

---

## Deliverables

| # | Deliverable | Path | State |
|---|---|---|---|
| 1 | Widened corpus builder | `Agent-Assure/calibration/build_corpus_v2.py` | new |
| 1 | Feature rows (α2 input) | `Agent-Assure/calibration/feature_rows-v2.jsonl` | new, 52 rows |
| 2 | Candidate labeling package | `Agent-Assure/calibration/labeling-v2.csv` | new, 52 rows |
| 3 | Candidate-guard test | `Agent-Assure/tests/test_labeling_v2_candidate_guard.py` | new, 3 tests |
| 3 | Loader fail-loud gate | `Agent-Assure/scripts/calibrate.py` (`load_labels`) | edited |
| 4 | Ratification brief | `Agent-Assure/calibration/RATIFICATION-BRIEF-v2.md` | new |
| 5 | Inbox ask | `inbox/pending/P1_2026-07-08_assure-calib_ask_ratify-gold-labels-v2.md` | new |

## Corpus statistics

- **n = 52 claims across 52 queries** (each query single-claim by design, so one
  candidate label maps to one decomposed claim unambiguously; builder fails loud
  if any draft decomposes to ≠1 claim). Requirement was n≥50 across ≥25 queries.
- **Class balance: 25 violation / 27 grounded = 48% violation** (positive class
  pinned to violation; requirement ≥30%).
- **Taxonomy coverage** (all classes in `references/grounding-failure-types.md`):
  GROUNDED (T1 verbatim, T2 paraphrase, numeric value+unit), ABSENCE_SUPPORTED,
  relational-grounded; UNVERIFIED_NUMBER, UNVERIFIED_CITATION, UNCITED,
  UNGROUNDED, UNVERIFIED_ABSENCE, UNVERIFIED_RELATION, UNGROUNDABLE.
- **Hardness curation** — 9 divergence rows (gate's mechanical verdict disagrees
  with the human candidate) + 5 aligned-but-subtle traps, all flagged in the
  brief: relational over-association (q25/q26/q48), single-word subject swap with
  matching number (q46), faithful paraphrase below lex_tau (q27/q47), absence
  head-noun edge cases both directions (q30/q49), unit-normalized numeric the gate
  under-grounds (q31), unit/magnitude/decimal numeric drift (q16/q17/q50),
  negation inversion under high lexical overlap (q28), plausible fabricated
  citation on a real-sounding number (q19).

## Schema change (backward-compatible)

Existing `labeling.csv` schema: `claim_id, query_id, claim_text, evidence,
human_label`. `labeling-v2.csv` adds three columns: **`candidate_verdict`**,
**`rationale`**, **`label_status`** (`candidate` on every row). `human_label` is
pre-filled equal to the candidate so a ratifier edits in place;
`candidate_verdict` preserves the original machine-assisted proposal.

Loader gate (`load_labels`): when a CSV carries a `label_status` column, **every
row must be `gold`** or it raises ValueError ("calibration runs on gold labels
only"). Files with **no** `label_status` column are unaffected — the legacy
`labeling.csv` and all existing calibration tests still pass unchanged.

Anchoring-bias note: the bootstrap deliberately hides the gate's verdict from a
blind labeler. α1 is a different workflow (candidate ratification, not blind
labeling), so it surfaces a candidate + rationale by design; the gate's own
mechanical verdict is still withheld from the CSV, and the tradeoff is stated in
the brief.

## Red-test evidence (proven RED before the loader change)

`uv run pytest tests/test_labeling_v2_candidate_guard.py` against the
**pre-change** loader:

```
tests/test_labeling_v2_candidate_guard.py::test_load_labels_rejects_candidate_status
>       with pytest.raises(ValueError) as exc:
E       Failed: DID NOT RAISE ValueError
tests/test_labeling_v2_candidate_guard.py::test_real_labeling_v2_is_rejected_while_candidate
E       Failed: DID NOT RAISE ValueError
========================= 2 failed, 1 passed in 0.05s =========================
```

The two rejection tests fail because the pre-change loader ignores
`label_status` and ingests candidate rows silently — the exact gap. After adding
the gate:

```
tests/test_labeling_v2_candidate_guard.py::test_load_labels_rejects_candidate_status PASSED
tests/test_labeling_v2_candidate_guard.py::test_load_labels_accepts_gold_status PASSED
tests/test_labeling_v2_candidate_guard.py::test_real_labeling_v2_is_rejected_while_candidate PASSED
============================== 3 passed in 0.03s ==============================
```

The third test skips (not fails) once every row is flipped to gold, so it
documents the α1 gate without breaking after ratification.

## Full-suite result

```
uv run pytest  →  334 passed in 2.74s
```

(331 pre-existing + 3 new. No threshold, gate, or tier logic was changed; the
only production edit is the additive `label_status` check in `load_labels`.)

## Exit criteria (plan §α1)

- [x] `labeling-v2.csv` exists (52 rows, ≥25 queries, ≥30% violation).
- [x] Fail-loud loader rejects it while `label_status=candidate` (test proves it,
      red-first evidence above).
- [x] Ratification brief delivered to Sai via inbox item (`inbox/pending/P1_...`).

**Blocked next:** α2 (threshold sweep + CR-002) starts when Sai flips
`labeling-v2.csv` to gold and acks the inbox item.
