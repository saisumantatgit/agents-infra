# Error-B corpus v2 baseline

Measured on main `d8c2ec0` with `Agent-Assure/.venv/bin/python Agent-Assure/tests/error_b_corpus_v2/run.py --base Agent-Assure`. The 224 original cases and 45 new cases are synthetic; labels have not been independently reviewed. Escaped means the overlapping gate segments are GROUNDED; PASS means the whole draft passes. Control PASS is the honest twin. Class T counts traceability breaks; Class S counts disclosed limitations refused where detectable.

The new heading cases separate verbatim copying (S) from reassembly (T); controls include a source-copied heading. Denied-after covers all twelve v1 denials and three added phrases. These cases cover only a fraction of R45 and R46; they do not measure the remaining families.

| Class | Kind | Drafts | Escaped | PASS | Control PASS |
|---|:---:|---:|---:|---:|---:|
| comparative_flip | T | 28 | 0 | 0 | 15 |
| denied_after | S | 15 | 4 | 4 | 15 |
| direction_flip | T | 28 | 0 | 0 | 7 |
| dropped_condition | T | 28 | 0 | 0 | 11 |
| heading_from_source_words_reassembled | T | 15 | 4 | 4 | 15 |
| heading_from_source_words_verbatim | S | 15 | 4 | 4 | 15 |
| hedge_dropped | T | 28 | 0 | 0 | 13 |
| negation_dropped | T | 28 | 0 | 0 | 12 |
| period_shift | T | 28 | 0 | 0 | 12 |
| quantifier_inflation | T | 28 | 0 | 0 | 11 |
| scope_widening | T | 28 | 0 | 0 | 12 |
| **All** | | 269 | 12 | 12 | 138 |

Class T: 4 certified traceability breaks. Class S: 8 certified disclosed limitations. Results are a fixed set of probes, not a prevalence estimate.
