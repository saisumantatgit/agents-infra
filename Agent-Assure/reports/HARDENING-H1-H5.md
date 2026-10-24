# Hardening H1-H5 (2026-10-25)

Branch `hardening-2026-10-25`. Five fail-closed fixes to `scripts/ground_check.py` /
`scripts/capture_core.py`: each may only move a claim AWAY from PASS. Baseline before H1:
1045 passed, 2 skipped, 61 xfailed. Gold `calibration/labels-v2.csv` md5
`6215b526d03147295b003d7ccb0d171f` (checked after every fix). Rates are from
`calibration.measure_rates.measure()`; per-row predicted verdicts were diffed against
baseline after every fix.

## H1: far and unlisted denials

- **Hole:** a denial beyond the 5-token hedge lookback, across a `;` / `(` / line split
  inside the same sentence, in a forward-pointing previous sentence, or an unlisted denial
  word, left the grounding sentence free to certify.
- **Red (pre-fix code):** `tests/red_team_moat/test_moat_h1_far_denial.py`: 8 failed,
  2 passed (the 2 are controls). All 8 attacks were GROUNDED / gate PASS:
  `prev_sentence_never_6_back`, `same_sentence_semicolon`, `same_sentence_newline`,
  `same_sentence_paren`, `we_dispute_the_following`, `this_is_false_far`,
  `none_of_that_happened`, `hardly_before`.
- **Fix:** `_source_unit_contexts` + `_unit_denied` + `_DENIAL_TOKENS`, wired into both T1
  paths (`_contained_with_matching_polarity`, `_anchor_sentence_covers`). A match is refused
  when a denial word sits before it in the same sentence, the previous sentence denies and
  points forward (or is ≤3 tokens), or the next sentence denies and points back.
- **Green:** 11 passed. Full suite 1056 passed, 2 skipped, 60 xfailed.
- **Side effect, good:** R8A-05 `nobody-has-established` (a strict xfail, open finding)
  XPASSed, so it was promoted from the xfail list to a passing guard.
- **Design correction during the fix:** the first version refused on ANY denial word in the
  previous sentence. It broke `test_relational_row_is_not_tier_sensitive`: the honest source
  "Insulin resistance occurs when cells do not respond well to insulin. Sustained insulin
  resistance causes type 2 diabetes ..." lost its T1 match. Narrowed to forward-pointing or
  bare-short previous sentences.
- **Rates:** Error-A 12/25, Error-B 0/27 — unchanged; zero gold rows drifted.
- **CEILING (in code):** lexical, not referential. Over-refuses an unrelated same-sentence
  denial; under-refuses a denial two sentences away, an unlisted denial word, or a
  previous-sentence denial with no forward reference.
