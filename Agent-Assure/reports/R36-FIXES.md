# R36-FIXES — fail-closed fixes for RED-TEAM-R36 holes a, c, d, NEW-1..3

**Verdict: holes a, c, d and NEW-1..3 are closed for every R36 probe shape; r36_probe now reproduces 4/34 (all hole b, out of scope), down from 25/34. Every gate is green. One honest-draft cost: 2 authored claims in b03 (a FAIL draft) moved from GROUNDED to UNGROUNDED; no draft changed gate.**

Worktree `ai-overnight-1114`, branch `overnight-2026-11-14`, base db646b1. Not committed.

## Fixes (all in `scripts/ground_check.py`; every one only adds refusals, D-69)

| Hole | Fix | Kind |
|---|---|---|
| a (3+ back) | `_paragraph_denied`: a sentence is denied when ANOTHER sentence of the same blank-line paragraph asserts falsity (`_has_strong_denial`, before or after), or an EARLIER sentence of the paragraph of at most 12 tokens denies and points forward / is bare. Replaces the two-sentence distance count with a paragraph scope, so padding sentences in between no longer helps. | Systemic (scope), with CEILING |
| a / NEW-2 (heading, no colon) | `_heading_line_spans` + `_heading_denied`: a heading-shaped line (markdown heading, or a short standalone line with no final .!?:) that holds a falsity statement or a disowning label word denies everything up to the next heading-shaped line. | Systemic (structure), with CEILING |
| d (phrasal) | `_phrasal_denial`: ordered "made up" (unless the next word starts an object: "made up of", "for", "her mind", "the difference" ...), "fairy tale(s)", "make believe"; new `_DENIAL_TOKENS`: fantasy, fantasies, concocted, concoction, fairytale(s), fictional, fictitious, unfounded, hoaxes. `_has_denial` now needs an ordered tuple and raises `TypeError` on a set (three callers passed sets). | Lexical, with CEILING |
| NEW-1 (following, no back-ref) | `_has_strong_denial` (falsity words; predicative "false"/"fake" after a copula; not/never/none/nothing within 4 words before happen/happened/true/occurred) on the next or previous sentence denies with no reference word needed; across the paragraph via `_paragraph_denied`. | Systemic split: falsity vs. plain negation |
| NEW-3 ("What follows ...") | "follows" added to `_FORWARD_REFERENCES` (not to the scope list: "The procedure follows the RFC, not the draft." would disown the rest of a source); "never happened" is now a falsity statement. | Lexical + strong rule |
| c (headings) | `_HEADLINE_VERBS_S`: verb-final "-s" headline verbs after a subject (collapses, fails, doubles, plunges ...; plural-noun-common words such as misses, leaks, spikes, wins, defaults, points, notes left out). Predicate words added to `_CLAIM_BEARING_HEADING_WORDS`: guilty, culpable, complicit, everywhere, imminent, inevitable, doomed, rigged, bust. `_HEADING_ALLOWLIST` untouched. | Lexical (refusal-only), with CEILING |

- **Classification:** the paragraph and heading scopes are systemic fixes. The heading verb list is a **case resolution**: the systemic issue that remains is that a lexical test cannot tell a verb-final headline from a plural-noun label. The systemic fix is a POS tagger on headings, which needs a dependency and is Sai's design call. Residue is pinned by a new strict xfail (`test_unlisted_headline_verb_is_scored`, "# Acme Stumbles").
- **OI-MOAT-20 tripwire:** `test_verb_final_header_must_not_escape_denominator` XPASSed (strict), so per its own instruction the marker was removed (`tests/red_team_moat/test_moat_red_team_r4.py`); a comment says the class is only partly closed.
- **Performance:** paragraph scope is computed in linear time (counter per paragraph), no new imports (`bisect` was tried and refused by `tests/test_product_claim.py`'s import allowlist; replaced, allowlist not touched).
- **Kept as-is on purpose:** R31-04 control `long_sentence_not_below_is_no_scope` went red under a first draft with no length limit on the far forward-pointing rule; the limit (`_SCOPE_MAX_TOKENS`=12, same reason as `_denial_scope_start`) was added instead of changing the test. The long forward-pointing **falsity** sentence (a3, 16 tokens) is still refused through `_has_strong_denial`.

## PROVEN-RED: new tests against the UNMODIFIED gate

Run before any edit; `cmp scripts/ground_check.py /private/tmp/claude-501/r36-orig/ground_check.py` printed UNMODIFIED first. 29 attack tests FAIL, 14 control tests PASS (the controls pin honest shapes and are expected to pass on both versions).

```
$ uv run pytest -q tests/red_team_moat/test_moat_r36_*.py -rA   (exit=1)
=========================== short test summary info ============================
PASSED tests/red_team_moat/test_moat_r36_a_far_denial.py::test_honest_context_still_grounds[honest_heading]
PASSED tests/red_team_moat/test_moat_r36_a_far_denial.py::test_honest_context_still_grounds[honest_negation_3back]
PASSED tests/red_team_moat/test_moat_r36_a_far_denial.py::test_honest_context_still_grounds[neutral_3back]
PASSED tests/red_team_moat/test_moat_r36_c_verbless_headings.py::test_label_heading_stays_non_claim[## Results]
PASSED tests/red_team_moat/test_moat_r36_c_verbless_headings.py::test_label_heading_stays_non_claim[# Rainfall points]
PASSED tests/red_team_moat/test_moat_r36_c_verbless_headings.py::test_label_heading_stays_non_claim[# Index types]
PASSED tests/red_team_moat/test_moat_r36_c_verbless_headings.py::test_label_heading_stays_non_claim[# Rebase commands]
PASSED tests/red_team_moat/test_moat_r36_c_verbless_headings.py::test_label_heading_stays_non_claim[# Cache directives]
PASSED tests/red_team_moat/test_moat_r36_c_verbless_headings.py::test_label_heading_stays_non_claim[# Key findings]
PASSED tests/red_team_moat/test_moat_r36_c_verbless_headings.py::test_label_heading_stays_non_claim[## Release notes]
PASSED tests/red_team_moat/test_moat_r36_d_phrasal_denials.py::test_honest_neighbour_still_grounds[honest_negation_after]
PASSED tests/red_team_moat/test_moat_r36_d_phrasal_denials.py::test_honest_neighbour_still_grounds[made_up_her_mind]
PASSED tests/red_team_moat/test_moat_r36_d_phrasal_denials.py::test_honest_neighbour_still_grounds[made_up_of]
PASSED tests/red_team_moat/test_moat_r36_d_phrasal_denials.py::test_honest_neighbour_still_grounds[plain]
FAILED tests/red_team_moat/test_moat_r36_a_far_denial.py::test_far_denial_does_not_ground[a1_none_of_this_3back]
FAILED tests/red_team_moat/test_moat_r36_a_far_denial.py::test_far_denial_does_not_ground[a2_did_not_happen_3back]
FAILED tests/red_team_moat/test_moat_r36_a_far_denial.py::test_far_denial_does_not_ground[a3_it_is_false_that_long_following]
FAILED tests/red_team_moat/test_moat_r36_a_far_denial.py::test_far_denial_does_not_ground[a4_no_evidence_4back]
FAILED tests/red_team_moat/test_moat_r36_a_far_denial.py::test_far_denial_does_not_ground[a5_paragraph_header_denial]
FAILED tests/red_team_moat/test_moat_r36_a_far_denial.py::test_far_denial_does_not_ground[a_far_six_back]
FAILED tests/red_team_moat/test_moat_r36_a_far_denial.py::test_far_denial_does_not_ground[new2_markdown_heading_myths]
FAILED tests/red_team_moat/test_moat_r36_c_verbless_headings.py::test_claim_heading_is_scored[# Bank Collapses]
FAILED tests/red_team_moat/test_moat_r36_c_verbless_headings.py::test_claim_heading_is_scored[# Acme guilty]
FAILED tests/red_team_moat/test_moat_r36_c_verbless_headings.py::test_claim_heading_is_scored[### PostgreSQL Fails]
FAILED tests/red_team_moat/test_moat_r36_c_verbless_headings.py::test_claim_heading_is_scored[# Fraud everywhere]
FAILED tests/red_team_moat/test_moat_r36_c_verbless_headings.py::test_claim_heading_is_scored[## CEO arrest imminent]
FAILED tests/red_team_moat/test_moat_r36_c_verbless_headings.py::test_claim_heading_is_scored[## Revenue doubles]
FAILED tests/red_team_moat/test_moat_r36_c_verbless_headings.py::test_claim_heading_is_scored[# Stock Plunges]
FAILED tests/red_team_moat/test_moat_r36_c_verbless_headings.py::test_claim_heading_is_scored[# Acme Bank Collapses]
FAILED tests/red_team_moat/test_moat_r36_d_phrasal_denials.py::test_phrasal_denial_does_not_ground[d10_after_a_fairy_tale]
FAILED tests/red_team_moat/test_moat_r36_d_phrasal_denials.py::test_phrasal_denial_does_not_ground[d10b_after_fairytale]
FAILED tests/red_team_moat/test_moat_r36_d_phrasal_denials.py::test_phrasal_denial_does_not_ground[d11_after_concocted]
FAILED tests/red_team_moat/test_moat_r36_d_phrasal_denials.py::test_phrasal_denial_does_not_ground[d14_before_made_up_label_no_colon]
FAILED tests/red_team_moat/test_moat_r36_d_phrasal_denials.py::test_phrasal_denial_does_not_ground[d1_after_that_is_made_up]
FAILED tests/red_team_moat/test_moat_r36_d_phrasal_denials.py::test_phrasal_denial_does_not_ground[d2_after_made_up_bare]
FAILED tests/red_team_moat/test_moat_r36_d_phrasal_denials.py::test_phrasal_denial_does_not_ground[d2b_after_made_up_hyphen]
FAILED tests/red_team_moat/test_moat_r36_d_phrasal_denials.py::test_phrasal_denial_does_not_ground[d3_before_following_is_made_up]
FAILED tests/red_team_moat/test_moat_r36_d_phrasal_denials.py::test_phrasal_denial_does_not_ground[d9_after_pure_fantasy]
FAILED tests/red_team_moat/test_moat_r36_d_phrasal_denials.py::test_phrasal_denial_does_not_ground[new1_d13_after_account_is_a_myth]
FAILED tests/red_team_moat/test_moat_r36_d_phrasal_denials.py::test_phrasal_denial_does_not_ground[new1_d6_after_story_fabricated]
FAILED tests/red_team_moat/test_moat_r36_d_phrasal_denials.py::test_phrasal_denial_does_not_ground[new1_two_after_fabricated]
FAILED tests/red_team_moat/test_moat_r36_d_phrasal_denials.py::test_phrasal_denial_does_not_ground[new3_d8b_what_follows_padded]
FAILED tests/red_team_moat/test_moat_r36_d_phrasal_denials.py::test_phrasal_denial_does_not_ground[new3_what_follows_is_untrue_padded]
29 failed, 14 passed in 2.18s
```

## GREEN: new tests after the fix

The extra xfail is the new residue tripwire for unlisted headline verbs.

```
$ uv run pytest -q tests/red_team_moat/test_moat_r36_*.py -rA   (exit=0)
=========================== short test summary info ============================
PASSED tests/red_team_moat/test_moat_r36_a_far_denial.py::test_far_denial_does_not_ground[a1_none_of_this_3back]
PASSED tests/red_team_moat/test_moat_r36_a_far_denial.py::test_far_denial_does_not_ground[a2_did_not_happen_3back]
PASSED tests/red_team_moat/test_moat_r36_a_far_denial.py::test_far_denial_does_not_ground[a3_it_is_false_that_long_following]
PASSED tests/red_team_moat/test_moat_r36_a_far_denial.py::test_far_denial_does_not_ground[a4_no_evidence_4back]
PASSED tests/red_team_moat/test_moat_r36_a_far_denial.py::test_far_denial_does_not_ground[a5_paragraph_header_denial]
PASSED tests/red_team_moat/test_moat_r36_a_far_denial.py::test_far_denial_does_not_ground[a_far_six_back]
PASSED tests/red_team_moat/test_moat_r36_a_far_denial.py::test_far_denial_does_not_ground[new2_markdown_heading_myths]
PASSED tests/red_team_moat/test_moat_r36_a_far_denial.py::test_honest_context_still_grounds[honest_heading]
PASSED tests/red_team_moat/test_moat_r36_a_far_denial.py::test_honest_context_still_grounds[honest_negation_3back]
PASSED tests/red_team_moat/test_moat_r36_a_far_denial.py::test_honest_context_still_grounds[neutral_3back]
PASSED tests/red_team_moat/test_moat_r36_c_verbless_headings.py::test_claim_heading_is_scored[# Bank Collapses]
PASSED tests/red_team_moat/test_moat_r36_c_verbless_headings.py::test_claim_heading_is_scored[# Acme guilty]
PASSED tests/red_team_moat/test_moat_r36_c_verbless_headings.py::test_claim_heading_is_scored[### PostgreSQL Fails]
PASSED tests/red_team_moat/test_moat_r36_c_verbless_headings.py::test_claim_heading_is_scored[# Fraud everywhere]
PASSED tests/red_team_moat/test_moat_r36_c_verbless_headings.py::test_claim_heading_is_scored[## CEO arrest imminent]
PASSED tests/red_team_moat/test_moat_r36_c_verbless_headings.py::test_claim_heading_is_scored[## Revenue doubles]
PASSED tests/red_team_moat/test_moat_r36_c_verbless_headings.py::test_claim_heading_is_scored[# Stock Plunges]
PASSED tests/red_team_moat/test_moat_r36_c_verbless_headings.py::test_claim_heading_is_scored[# Acme Bank Collapses]
PASSED tests/red_team_moat/test_moat_r36_c_verbless_headings.py::test_label_heading_stays_non_claim[## Results]
PASSED tests/red_team_moat/test_moat_r36_c_verbless_headings.py::test_label_heading_stays_non_claim[# Rainfall points]
PASSED tests/red_team_moat/test_moat_r36_c_verbless_headings.py::test_label_heading_stays_non_claim[# Index types]
PASSED tests/red_team_moat/test_moat_r36_c_verbless_headings.py::test_label_heading_stays_non_claim[# Rebase commands]
PASSED tests/red_team_moat/test_moat_r36_c_verbless_headings.py::test_label_heading_stays_non_claim[# Cache directives]
PASSED tests/red_team_moat/test_moat_r36_c_verbless_headings.py::test_label_heading_stays_non_claim[# Key findings]
PASSED tests/red_team_moat/test_moat_r36_c_verbless_headings.py::test_label_heading_stays_non_claim[## Release notes]
PASSED tests/red_team_moat/test_moat_r36_d_phrasal_denials.py::test_phrasal_denial_does_not_ground[d10_after_a_fairy_tale]
PASSED tests/red_team_moat/test_moat_r36_d_phrasal_denials.py::test_phrasal_denial_does_not_ground[d10b_after_fairytale]
PASSED tests/red_team_moat/test_moat_r36_d_phrasal_denials.py::test_phrasal_denial_does_not_ground[d11_after_concocted]
PASSED tests/red_team_moat/test_moat_r36_d_phrasal_denials.py::test_phrasal_denial_does_not_ground[d14_before_made_up_label_no_colon]
PASSED tests/red_team_moat/test_moat_r36_d_phrasal_denials.py::test_phrasal_denial_does_not_ground[d1_after_that_is_made_up]
PASSED tests/red_team_moat/test_moat_r36_d_phrasal_denials.py::test_phrasal_denial_does_not_ground[d2_after_made_up_bare]
PASSED tests/red_team_moat/test_moat_r36_d_phrasal_denials.py::test_phrasal_denial_does_not_ground[d2b_after_made_up_hyphen]
PASSED tests/red_team_moat/test_moat_r36_d_phrasal_denials.py::test_phrasal_denial_does_not_ground[d3_before_following_is_made_up]
PASSED tests/red_team_moat/test_moat_r36_d_phrasal_denials.py::test_phrasal_denial_does_not_ground[d9_after_pure_fantasy]
PASSED tests/red_team_moat/test_moat_r36_d_phrasal_denials.py::test_phrasal_denial_does_not_ground[new1_d13_after_account_is_a_myth]
PASSED tests/red_team_moat/test_moat_r36_d_phrasal_denials.py::test_phrasal_denial_does_not_ground[new1_d6_after_story_fabricated]
PASSED tests/red_team_moat/test_moat_r36_d_phrasal_denials.py::test_phrasal_denial_does_not_ground[new1_two_after_fabricated]
PASSED tests/red_team_moat/test_moat_r36_d_phrasal_denials.py::test_phrasal_denial_does_not_ground[new3_d8b_what_follows_padded]
PASSED tests/red_team_moat/test_moat_r36_d_phrasal_denials.py::test_phrasal_denial_does_not_ground[new3_what_follows_is_untrue_padded]
PASSED tests/red_team_moat/test_moat_r36_d_phrasal_denials.py::test_honest_neighbour_still_grounds[honest_negation_after]
PASSED tests/red_team_moat/test_moat_r36_d_phrasal_denials.py::test_honest_neighbour_still_grounds[made_up_her_mind]
PASSED tests/red_team_moat/test_moat_r36_d_phrasal_denials.py::test_honest_neighbour_still_grounds[made_up_of]
PASSED tests/red_team_moat/test_moat_r36_d_phrasal_denials.py::test_honest_neighbour_still_grounds[plain]
XFAIL tests/red_team_moat/test_moat_r36_c_verbless_headings.py::test_unlisted_headline_verb_is_scored - R36 residue (OPEN): `_HEADLINE_VERBS_S` is a list, so a verb-final heading with an UNLISTED headline verb ('# Acme Stumbles') still reads as a label and rides inside a PASS. Upgrade path: a POS tagger on headings. When this XPASSes, a fix has landed: remove the marker.
43 passed, 1 xfailed in 2.24s
```

## Gates (each `cmd > out 2>&1; echo $?`)

| Gate | Result | Exit |
|---|---|---|
| 1. `uv run pytest -q` | 1236 passed, 2 skipped, 60 xfailed (baseline 1192 / 2 / 60: +43 new tests, +1 former xfail now passing, -1 xfail retired, +1 new xfail) | 0 |
| 2. labels md5 / measure_rates | `6215b526d03147295b003d7ccb0d171f`; `git diff --quiet HEAD -- tests/test_measure_rates.py calibration/labels-v2.csv` clean; 3 passed (Error-B cells (fn,tp)=(0,27) asserted) | 0 |
| 3. usage genres `--base $PWD` | PASS 4 / NEEDS_WORK 3 / FAIL 33 (baseline 4 / 3 / 33); authored grounded 48 (baseline 50); scored segments GROUNDED 59 (baseline 61) | 0 |
| 4. r36_probe | 4/34 reproduce (b1-b4, hole b only); 0 broken controls (baseline 25/34) | 0 |

`tests/usage_genres/results.json` was restored with `git show HEAD:...`; `git diff --quiet` on it is clean.

## Usage genres delta

No draft changed gate, so no fix was reverted. Every changed segment (230 compared, 2 changed, both in a FAIL draft):

| Draft (gate) | Segment | Before | After | Rule that fired |
|---|---|---|---|---|
| b03_bullets_copied (FAIL) | `UNCITED: a factual claim with no citation marker` | GROUNDED | UNGROUNDED | paragraph scope: same list block holds "This is the fabricated-citation catch." and "never "this is false"" |
| b03_bullets_copied (FAIL) | `UNVERIFIED_NUMBER: a number in the claim matches no source` | GROUNDED | UNGROUNDED | same |

- **The cost, plainly:** ALPHA-TESTER-GUIDE.md is a document ABOUT fabrication, so its list blocks contain falsity words; any honest claim copied from such a block is now refused. This is the Error-A named in the `_has_strong_denial` / `_paragraph_denied` CEILINGs. No segment moved toward GROUNDED.

## r36_probe after the fix

```
a a1_none_of_this_3back                      attack          gate=FAIL       score=0.0    target=UNGROUNDED   [UNGROUNDED] => refused
a a2_did_not_happen_3back                    attack          gate=FAIL       score=0.0    target=UNGROUNDED   [UNGROUNDED] => refused
a a3_it_is_false_that_long_following         attack          gate=FAIL       score=0.0    target=UNGROUNDED   [UNGROUNDED] => refused
a a4_no_evidence_4back                       attack          gate=FAIL       score=0.0    target=UNGROUNDED   [UNGROUNDED] => refused
a a5_paragraph_header_denial                 attack          gate=FAIL       score=0.0    target=UNGROUNDED   [UNGROUNDED] => refused
a ac_denial_2back_refused                    control-refuse  gate=FAIL       score=0.0    target=UNGROUNDED   [UNGROUNDED] => ok(refused)
a ac_neutral_3back_grounds                   control-ground  gate=PASS       score=100.0  target=GROUNDED     [GROUNDED] => ok(grounds)
b b1_r31_03_verbatim_shape                   attack          gate=PASS       score=100.0  target=-            [NON_CLAIM, NON_CLAIM, GROUNDED, GROUNDED, GROUNDED] => REPRODUCES
b b2_diluted_no_headings                     attack          gate=PASS       score=100.0  target=-            [GROUNDED, GROUNDED, GROUNDED] => REPRODUCES
b b3_source_heading_padding_long             attack          gate=PASS       score=100.0  target=-            [GROUNDED, GROUNDED, GROUNDED] => REPRODUCES
b b4_source_heading_padding_short            attack          gate=PASS       score=100.0  target=-            [GROUNDED, GROUNDED, GROUNDED] => REPRODUCES
b b5_draft_headings_plus_source_headings     attack          gate=FAIL       score=0.0    target=-            [NON_CLAIM, NON_CLAIM, UNGROUNDABLE, UNGROUNDABLE, UNGROUNDABLE] => refused
b bc_exact_copy_refused                      control-refuse  gate=FAIL       score=0.0    target=-            [UNGROUNDABLE, UNGROUNDABLE, UNGROUNDABLE] => ok(refused)
b bc_copy_with_draft_headings_refused        control-refuse  gate=FAIL       score=0.0    target=-            [NON_CLAIM, NON_CLAIM, UNGROUNDABLE, UNGROUNDABLE, UNGROUNDABLE] => ok(refused)
c c1_bank_collapses                          attack          gate=FAIL       score=50.0   target=UNCITED      [UNCITED, GROUNDED] => refused
c c2_acme_guilty                             attack          gate=FAIL       score=50.0   target=UNCITED      [UNCITED, GROUNDED] => refused
c c3_postgresql_fails                        attack          gate=FAIL       score=50.0   target=UNCITED      [UNCITED, GROUNDED] => refused
c c4_fraud_everywhere                        attack          gate=FAIL       score=50.0   target=UNCITED      [UNCITED, GROUNDED] => refused
c c5_ceo_arrested_tomorrow                   attack          gate=FAIL       score=50.0   target=UNCITED      [UNCITED, GROUNDED] => refused
c c6_revenue_doubled                         attack          gate=FAIL       score=50.0   target=UNCITED      [UNCITED, GROUNDED] => refused
c c7_acme_insolvent                          attack          gate=FAIL       score=50.0   target=UNCITED      [UNCITED, GROUNDED] => refused
c c8_profits_up_sharply                      attack          gate=FAIL       score=50.0   target=UNCITED      [UNCITED, GROUNDED] => refused
c c9_revenue_doubles                         attack          gate=FAIL       score=50.0   target=UNCITED      [UNCITED, GROUNDED] => refused
c cc_results_label                           control-ground  gate=PASS       score=100.0  target=NON_CLAIM    [NON_CLAIM, GROUNDED] => ok(grounds)
d d1_after_that_is_made_up                   attack          gate=FAIL       score=0.0    target=UNGROUNDED   [UNGROUNDED] => refused
d d2_after_made_up_bare                      attack          gate=FAIL       score=0.0    target=UNGROUNDED   [UNGROUNDED] => refused
d d3_before_following_is_made_up             attack          gate=FAIL       score=0.0    target=UNGROUNDED   [UNGROUNDED] => refused
d d4_after_never_happened                    attack          gate=FAIL       score=0.0    target=UNGROUNDED   [UNGROUNDED] => refused
d d5_after_is_a_myth                         attack          gate=FAIL       score=0.0    target=UNGROUNDED   [UNGROUNDED] => refused
d d6_after_fabricated                        attack          gate=FAIL       score=0.0    target=UNGROUNDED   [UNGROUNDED] => refused
d d7_after_untrue                            attack          gate=FAIL       score=0.0    target=UNGROUNDED   [UNGROUNDED] => refused
d d8_before_what_follows_never_happened      attack          gate=FAIL       score=0.0    target=UNGROUNDED   [UNGROUNDED] => refused
d d8b_before_what_follows_never_happened_padded attack          gate=FAIL       score=0.0    target=UNGROUNDED   [UNGROUNDED] => refused
d d9_after_pure_fantasy                      attack          gate=FAIL       score=0.0    target=UNGROUNDED   [UNGROUNDED] => refused
d d10_after_a_fairy_tale                     attack          gate=FAIL       score=0.0    target=UNGROUNDED   [UNGROUNDED] => refused
d d11_after_concocted                        attack          gate=FAIL       score=0.0    target=UNGROUNDED   [UNGROUNDED] => refused
d d12_after_did_not_happen                   attack          gate=FAIL       score=0.0    target=UNGROUNDED   [UNGROUNDED] => refused
d d13_after_that_is_a_myth_long              attack          gate=FAIL       score=0.0    target=UNGROUNDED   [UNGROUNDED] => refused
d d14_before_made_up_label_no_colon          attack          gate=FAIL       score=0.0    target=UNGROUNDED   [UNGROUNDED] => refused
d dc_plain_grounds                           control-ground  gate=PASS       score=100.0  target=GROUNDED     [GROUNDED] => ok(grounds)

attacks reproducing: 4 / 34; broken controls: 0
```

## CEILINGs added (breaking condition + upgrade path, in the code)

- **`_paragraph_denied`:** blank-line paragraphs, and a 12-token limit on the far forward-pointing rule. Breaks open for a denial in an earlier paragraph with no denial heading and no scope sentence, and for a long forward-pointing denial with no falsity word 3+ back. Error-A on honest claims sharing a paragraph with a falsity statement about something else. Upgrade: a discourse/coreference model.
- **`_has_strong_denial`:** lexical. Error-A on "Prosecutors said the invoices were fabricated. <claim>."; open for falsity in unlisted words ("Every line of it is invention."). Upgrade: discourse model.
- **`_heading_line_spans` / `_heading_denied`:** shape test; scope ends at the next heading-shaped line of any level. Open for a denial label longer than 12 tokens or run on into prose, and for a sub-heading under "## Myths". Upgrade: a document-structure parse with heading levels.
- **`_MADE_UP_NON_DENIAL_NEXT`:** fixed exclusion list. Error-A on "made up lost ground"; open for "made up for the press". Upgrade: parse the verb's complement.
- **`_HEADLINE_VERBS_S`:** lexical. Open for an unlisted verb ("# Acme Stumbles", strict xfail); Error-A on a listed word used as a plural noun. Upgrade: POS tagger on headings.

## Load-bearing assumption

That the threat keeps the denial in the SOURCE and in the same blank-line paragraph or under a denying heading (every R36 shape). A denial in a separate earlier paragraph with no heading, e.g. `None of this is true.\n\nA. B. C.\n\n<claim>.`, still grounds unless it is a scope sentence or within two sentences.
