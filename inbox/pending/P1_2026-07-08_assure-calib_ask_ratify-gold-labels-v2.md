---
id: P1_2026-07-08_assure-calib_ask_ratify-gold-labels-v2
from: assure-calibration
to: sai
type: ask
priority: P1
created: 2026-07-08
ack_required: true
acceptance_criteria: labels-v2.csv rows corrected/ratified and label_status flipped to gold
updated: 2026-07-14
---

# Ask: Ratify the v2 gold labels (Phase α1 → unblocks α2)

Phase α1 of the Alpha Readiness Plan is done except for the one gate only you
can clear: **ratifying the calibration labels**. This is the Alpha long-pole.

## What I need

Review the 52 candidate labels and mark them gold. Full instructions and the
14 hardest rows are in the brief:

- **Brief:** `Agent-Assure/calibration/RATIFICATION-BRIEF-v2.md` (read first)
- **File you READ:** `Agent-Assure/calibration/labeling-v2.csv` (scaffold — claim,
  evidence, candidate, rationale)
- **File you EDIT:** `Agent-Assure/calibration/labels-v2.csv` ← **the only file you
  touch.** Row-aligned with the scaffold, so the brief's line numbers hold in both.

Three steps: (1) for each row in `labels-v2.csv`, confirm or correct
`human_label` (grounded/violation); (2) leave `claim_sha` alone — it binds your
judgment to the exact text you read; (3) find-and-replace `label_status`
`candidate` → `gold` on every row, and save.

**Changed 2026-07-14 (PIR-002):** your labels used to live in the same file the
corpus generator rewrites — and on 2026-07-14 a routine rebuild blanked the n=12
bootstrap labels (recovered from git). Labels now live in their own file that
**no generator may write**, and a `claim_sha` binds each one to the claim it was
made against, so a later corpus change can never silently re-point your judgment
at a sentence you never read. Nothing for you to do about it; just edit
`labels-v2.csv`, not `labeling-v2.csv`.

Expected effort: **30–45 min**, concentrated on the 14 flagged rows
(over-association relationals, unit/magnitude/decimal numeric drift, faithful
paraphrases below lex_tau, absence head-noun edge cases, and the
plausible-fabricated-citation moat calls q19/q46).

## Why it's blocking

`scripts.calibrate.load_gold_labels` refuses to ingest the labels while any row
is `label_status=candidate` (fail-loud, tested in
`tests/test_labeling_v2_candidate_guard.py` and
`tests/test_gold_labels_separation.py`). Calibration runs on gold labels only —
so α2 (threshold sweep, leave-one-out, CR-002) cannot start until you flip
`labels-v2.csv` to gold.

## Load-bearing check before you start

"Grounded" means **the cited evidence establishes the claim**, not "the claim
is true in the world." q19 and q46 are true-sounding but are violations
because the store link is fabricated/mismatched. If your read of "grounded"
differs, flag that first — it changes every threshold α2 derives.

## Done when

- `labeling-v2.csv` rows ratified/corrected and `label_status` is `gold` on all
  52 rows.
- Ack back (reply here or drop an `ack` in `outbox/`) so α2 kicks off.
