# CR-005 — launch-claim window (J-25…J-41r, J-22, J-38)

**Deployed:** 2026-10-02 · **Supersedes:** CR-004 · **n = 52 gold, single ratifier**

Mandatory per CLAUDE.md failure-mode 9 and ADR-025: `ground()` changed eleven
times across 2026-10-01/02, so a CR is owed. **It is emitted DESPITE an expected
zero delta** — I first recommended annotating CR-004 instead, which was wrong:
exempting a run from calibration because you expect no movement is exactly the
selective calibration ADR-025 exists to prevent.

## What changed since CR-004

| Job | Change | Direction |
|---|---|---|
| J-25 | unresolved-citation check moved ahead of the kind dispatch | fail-closed |
| J-26 | `load_store` refuses a self-contradicting store | fail-closed |
| J-27 → J-41r | comment stripping is SAME-LINE only (4th design; 3 earlier ones lost r9/r10/r11) | fail-closed |
| J-37 | corpus fixtures use real tool names; loader-parity test added | none (fixtures) |
| J-39 | relation endpoints match on word boundaries | fail-closed |
| J-40 | numbers inside RELATIONAL claims are checked, against CITED sources | fail-closed |
| R10C-03 | a summary may refuse an absence, never certify one | fail-closed |
| **J-22** | `conclude*` / `indicate*` added to the factive whitelist | **PASS-ENABLING — Sai-ratified, D-53** |
| J-38 | `session_id` captured; `--session-id` refuses a foreign-session store | fail-closed, opt-in |

## Projection vs actual

Projection = CR-004 actuals. Re-derived through `predicted_is_violation` over
`feature_rows-v2.jsonl` against `labels-v2.csv` on the shipped tree.

| Measure | Projected | Actual | Δ |
|---|---|---|---|
| Error-A | 0.320 | **0.320** (8/25) | 0% |
| Error-B | 0.000 | **0.000** (0/27) | 0% |
| Confusion (tp/fp/tn/fn) | 27/8/17/0 | **27/8/17/0** | 0% |
| Corpus rows whose verdict changes | 0 | **0** | 0% |
| `labeling-v2.csv` bytes | identical | **identical** | 0% |
| `labels-v2.csv` md5 | `6215b526…d171f` | **`6215b526…d171f`** | 0% |
| Suite | 664 | **734** passed | +70 |

Error-A rows, unchanged from CR-004: q05, q08, q09, q16, q27, q31, q35, q47.

## Movement

| | CR-003 | CR-004 | CR-005 |
|---|---|---|---|
| Error-A | 0.320 | 0.320 | **0.320** |
| Error-B | 0.074 | 0.000 | **0.000** |

## THE ZERO DELTA IS NOT A SAFETY RESULT. Read this before quoting it.

A byte-identical corpus means **the 52 rows do not contain the shapes these
changes touch.** It is evidence of *non-measurement*, not of non-regression. The
same inference was drawn wrongly twice on 2026-09-12 and withdrawn both times.

What A=0.320 does **not** bound, by change:

- **J-22** — no row contains `concluded that` / `indicates that`. The class was
  unmeasured when Sai ratified it and is unmeasured now.
- **J-41r** — no row contains an HTML comment. Its known cost (a multi-line note
  is scored, J-48) is bounded by tests, not by this number.
- **J-26 / J-37** — no row exercises a malformed store, and until J-37 the corpus
  **bypassed `load_store` entirely**, so loader changes were invisible to this
  instrument by construction.
- **J-38** — no row carries a `session_id`; enforcement is opt-in and untested
  against the corpus.
- **J-39 / J-40** — no row has a sub-word endpoint collision or a figure inside a
  relational claim.

**Provenance of the rate, unchanged and still the weakest link:** n=52, SINGLE
ratifier (the project owner), and the inter-rater round measured κ 0.54 / 0.16
between independent readers. Quote as *(n=52, single ratifier, CR-005)* and never
quote Error-B as "zero" — on 0/27 the 95% upper bound is ~10.5%. Say "no
remaining Error-B among the 52 ratified rows."

**The open step is unchanged and it is not a code task:** a corpus extension
carrying the shapes above, so the next CR measures something these changes can
move. Authoring rows sits against the gold-label gate, so it is Sai's (J-37).
