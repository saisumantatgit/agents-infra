# Calibration Record — Agent-Assure Gate (ADR-025)

## Projection vs Actual

| Metric | Projection | Actual | Delta |
|---|---|---|---|
| lex_tau | 0.71 | 0.76 | +7.0% |
| gate | 0.9 | deferred | deferred |
| nli_tau | 0.8 | deferred | deferred |

## Held-Out Error Rates (chosen operating point, leave-one-out)

- n = 52 claims across 52 queries
- Error-A (false alarm, recoverable): 0.2
- Error-B (false negative, UNRECOVERABLE): 0.1111111111111111
- Confusion: tp=24 fp=5 tn=20 fn=3

## Honesty (calibration-plan.md §6)

- n≈52 queries is calibration, not proof — provisional until production data widens it.
- Split method: leave-one-out (per-claim). The Error-A/Error-B rates above are HELD-OUT (not in-sample).

## Label provenance (ADR-025 — required for a gold run)

- Ratifier: **Sai Sumanth Battepati**, 2026-09-02. Corpus n=52, 25 grounded / 27 violation (violation class 51%, floor 30%).
- Method: labelled blind via a review page that withheld the candidate verdicts; 14 rows self-flagged; 11 disagreements with the candidate set adjudicated in session.
- Outcome of adjudication: 4 rows ratified AGAINST the candidate (q14, q16, q37, q49); 7 rows corrected toward it on evidence shown (q17, q24, q25, q26, q44, q48, q50).
- `claim_sha` unchanged on all 52 rows; `load_gold_labels` accepted the set (gold-only, no duplicate/orphan/unlabeled/STALE).

## Independence caveat (read before quoting these rates)

**Labeller and candidate-generator were not independent.** The ratifier is the
project owner and had seen 9 candidate verdicts in conversation before
labelling; all 9 are in the agreed set. Final labels differ from the candidates
on **4 of 52 rows**. These rates are therefore materially stronger than
candidate labels but are NOT external ground truth. A second blind labeller on
the same 52 would make the comparison independent and is the recommended next
step; until then, quote these as "n=52, single ratifier, CR-002".

## Corpus defect found during ratification (fixed)

Rows q24/q44 are violations because their sources are `haiku_summary`, and the
scaffold exposed no source type — making them unlabellable by any human from
the sheet. Ratified only after the source type was disclosed. Systemic fix:
`source_type` column added to the scaffold (as a COLUMN, never by editing
`evidence`, which would invalidate every `claim_sha`).

## Supersession

CR-002 supersedes CR-001 (n=12). Error-B monotonicity holds: 0.143 -> 0.111.
