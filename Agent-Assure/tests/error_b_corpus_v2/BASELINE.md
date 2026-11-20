# Error-B corpus v2 baseline

Measured on main `aa786830feac1edbb667844cda098ae20223b5d9` (the unchanged gate on this branch). From `Agent-Assure/`:

```sh
.venv/bin/python tests/error_b_corpus_v2/run.py --base .
```

Each of 224 drafts has one labelled unsupported alteration and an honest control; each class occurs twice in each of 14 genres. Sources combine the authored Error-A source with one newly authored fact. The builder asserts the fabricated segment is absent from the source and all other cited segments in both drafts are verbatim. No class requires an exception. These checks do not independently establish that the source entails a claim or that an alteration is false; labels are synthetic and have not been independently reviewed.

Escape means every gate segment overlapping the labelled text is GROUNDED; PASS means the entire fabricated draft is certified. Control PASS measures the honest twin. The results are a fixed set of probes, not a prevalence estimate. Some citations follow the sentence period; the gate may detach them and refuse the honest control, so read the counts alongside control PASS.

| Class | Drafts | Escaped | PASS | Control PASS |
|---|---:|---:|---:|---:|
| comparative_flip | 28 | 0 | 0 | 15 |
| direction_flip | 28 | 0 | 0 | 7 |
| dropped_condition | 28 | 0 | 0 | 11 |
| hedge_dropped | 28 | 0 | 0 | 13 |
| negation_dropped | 28 | 0 | 0 | 12 |
| period_shift | 28 | 0 | 0 | 12 |
| quantifier_inflation | 28 | 0 | 0 | 11 |
| scope_widening | 28 | 0 | 0 | 12 |
| **All** | 224 | 0 | 0 | 93 |

There were no escaped segments in this run; consequently there are no escaped draft IDs to rank. This does not establish that the gate catches other surfaces in these classes.
