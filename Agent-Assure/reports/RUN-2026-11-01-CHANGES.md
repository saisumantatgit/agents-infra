# RUN-2026-11-01: R31-04 fail-closed denial gaps + D-102 rows 1 and 2

Branch `run-2026-11-01` (worktree ai-run-1101), base main 6eb3d5c (+ d2a3138 register entry). Baseline: 1106 passed, 2 skipped, 60 xfailed.
Gold `calibration/labels-v2.csv` md5 6215b526d03147295b003d7ccb0d171f checked after each item. `tests/test_measure_rates.py` pin untouched.

## Item A: R31-04 denial gaps (refusal only, D-69)

Test: `tests/red_team_moat/test_moat_r31_04_denial_gaps.py` (13 attacks, 4 controls).

**Red (pre-change code, `git checkout scripts/ground_check.py`):** 11 failed, 7 passed. GROUNDED/PASS on main:
denial_6_back, denial_2_back_no_forward_word ("Every word of this page is invented." + 1 filler sentence), trail_that_is_a_lie, trail_lies, trail_bogus, trail_fake, trail_no_not_at_all_sir_never, prose_label_second_item (8-word label ending ":"), label_cyrillic_false ("FАLSE:"), label_cyrillic_myths ("Мyths:"), inline_cyrillic_false ("This is fаlse: ...").
Already refused on main (kept as guards, not claimed as closures): label_7_words_disowning, label_nonsense, denial_2_back_bare. The 4 controls ground on both.

**Green:** 18 passed. Full suite: 1124 passed, 2 skipped, 60 xfailed. measure_rates (fp,tn)=(12,13) unchanged, Error-B 0/27. Gold md5 unchanged.

Changes (`scripts/ground_check.py`):
- `_DENIAL_TOKENS` + lie, lies, bogus, fake(s), invented, fabrication(s), hoax, untruth(s), falsehood(s). `_DISOWNING_LABEL_TOKENS` + nonsense, lie(s), bogus, invented, fabricated, fabrication(s), fiction, baseless, wrong, incorrect.
- `_is_bare_denial`: <= 3 tokens with a denial, or <= 8 tokens at least half denial words. Used for the previous and following sentence.
- `_denial_scope_start`: a sentence that denies and says "following/below/hereafter/hereunder", or names the whole text ("this page", "every ... document"), denies every later sentence.
- `_LONG_LABEL_LINE_RE`: a label line of any length that ENDS with ":" is a list label.
- `_DENIAL_CONFUSABLES` + `_folded`: Cyrillic/Greek look-alikes folded only in the denial and label word checks.

Ceilings (in code as `CEILING:`): "lie(s)" as a verb next to a match refuses (Error-A); the bare-denial ratio cut refuses "Not always." and misses wordier replies; the whole-text scope has no end ("does not apply to the cases below" refuses the rest); the confusables map is a fixed subset, not TR39.
