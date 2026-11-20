# CR-014 — E1 phrasal falsity, 2026-11-21

Fail-closed C1 authority: D-119/D-120. This records the fresh run; CR-007 remains the deployed operating point until the orchestrator decides otherwise.

| Measure | Projection | Actual | Delta |
|---|---|---|---|
| Error-A, 25 grounded gold claims | may rise | 12/25 = 0.480 before and after | 0 |
| Error-B, 27 violation gold claims | cannot rise | 0/27 before and after | 0 |
| Regenerated feature rows vs regenerated main | unknown | byte-identical, md5 `9b2b4e60140dda089a100c89099238eb` | 0 |
| Gold labels md5 | unchanged | `6215b526d03147295b003d7ccb0d171f` | 0 |

Rates are freshly recomputed from each gate (`calibration.measure_rates`), n=52, single ratifier. 0/27 means no known violation in this gold set escaped; its approximate 95% upper bound is 10.5%. These rows do not measure the E1 family; no change is not proof of safety.

The checked-in feature rows were already stale relative to live main. Regenerating main and E1 independently produced identical rows, but two rows differ from the checked-in artifact: q03 changed GROUNDED → UNGROUNDED and q13 ABSENCE_SUPPORTED → UNVERIFIED_ABSENCE. Both are gold `grounded`, hence existing false alarms on main as well as E1; neither drift was caused by E1. The regenerated derived feature file is retained, while authored gold labels are untouched. Honest and fabrication corpus measurements and the one newly lost control claim are in `reports/E1-PRONOUN-MADE-UP.md`.
