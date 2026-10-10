# Calibration Record — Agent-Assure Gate (ADR-025)

## Projection vs Actual

| Metric | Projection | Actual | Delta |
|---|---|---|---|
| lex_tau | 0.65 | 0.71 | +9.2% |
| gate | 0.9 | deferred | deferred |
| nli_tau | 0.8 | deferred | deferred |

## Held-Out Error Rates (chosen operating point, leave-one-out)

- n = 12 claims across 12 queries
- Error-A (false alarm, recoverable): 0.2
- Error-B (false negative, UNRECOVERABLE): 0.14285714285714285
- Confusion: tp=6 fp=1 tn=4 fn=1

## Honesty (calibration-plan.md §6)

- n≈12 queries is calibration, not proof — provisional until production data widens it.
- Split method: leave-one-out (per-claim). The Error-A/Error-B rates above are HELD-OUT (not in-sample).
