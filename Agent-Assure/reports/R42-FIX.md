# R42-FIX: main's denial verdict OR'd by construction (ovn-1115-q1 @ bce1ac7 + fix, uncommitted)

**Verdict: the R42 blocker is closed by a systemic fix. Every gate is green: 0 branch-better in 23,000 targeted pairs and in 64,000 broad pairs, and the main-path code is proven AST-identical to origin/main 746f337. The fix is not committed, and it has not yet been re-red-teamed.**

## Fix (Systemic)
- **Root cause (R42):** R40 widened `_has_strong_denial` and `_points_forward` in place. Main's `_strong_tokens` clearing step reads `_heading_line_denies` negatively, so the widening cut fewer headings out of welded sentences. On the longer text, two of main's tests got weaker: the 12-token pointing cap (B1) and the code-value window (B2).
- **Structure now:** `_match_denied(unit, ...)` is `_unit_denied(unit.main, start) or _r40_match_denied(unit.r40, unit.view, ...)`. `unit.main` comes from `_source_unit_contexts`, which is origin/main's code. `unit.r40` comes from `_source_unit_contexts_r40`, which is bce1ac7's R40 reading. So the branch refuses whenever main refuses, for every input. The new code is the bce1ac7 denial reading OR'd with main's.
- **Main path restored:** `_has_strong_denial`, `_points_forward`, `_paragraph_denied` and `_source_unit_contexts` are back to main's bodies.
- **R40 reading:** it lives only in separate names: `_has_strong_denial_r40`, `_points_forward_r40`, `_heading_line_denies_r40`, `_heading_line_spans_r40`, `_strong_tokens_r40`, `_heading_denied_r40_flat`, `_paragraph_denied_r40` / `_pointing_r40`, `_unit_denied_r40` and `_source_unit_contexts_r40`. R40 heading lines, the trailing rule, the long-line rule and the comparison copy now call these. `_unit_denied_r40` and `_paragraph_denied_r40` are main's function OR'd with the R40 extra. This equals bce1ac7, because main reads `_points_forward` only positively.
- **Consumers:** `_contained_with_matching_polarity` and `_anchor_sentence_covers` iterate `_denial_units` and decide only through `_match_denied`. `_denial_units` raises if the two readings split the text into different units.
- **Classification untouched:** the R40 `_header_asserts` widening was left as is. R42 Attack 4: a promoted heading can only lower the score.

## Structural guard: `tests/red_team_moat/test_moat_r42_additive_structure.py` (4 tests)
1. **Digest pin:** the digest covers every function reachable from `_source_unit_contexts` and `_unit_denied` (28 functions, docstrings stripped) and every constant they read, including rebinds (38). It equals the digest of origin/main 746f337's file (`36d4617b…`). bce1ac7 gives a different digest (`136060b8…`).
2. **No R40 names:** the main path reaches no R40 name.
3. **Main first:** `_match_denied` is a single `Or` expression whose first operand is `_unit_denied(<x>.main, …)`.
4. **Single entry:** the R40 reading is entered only through `_denial_units` and `_match_denied`, and the two consumers never call `_unit_denied` directly.

All 4 fail on bce1ac7 and pass after the fix. CEILING: AST-level. A mutation made through a method call on a main-path dict is not seen. Upgrade path: also digest the runtime values.

## Proven red: `tests/red_team_moat/test_moat_r42_heading_seam.py` (8 cases)
- **Cases:** B1a, B1b, B1c, B2a and B2b from R42, plus three event-negation headings from cutseam_fuzz: "## The launch never took place", "## Why the merger did not occur" and "## Why the launch never took place".
- **bce1ac7:** 8 failed. **origin/main gc:** 8 passed. **Fix:** 8 passed.

## Gates
| Gate | Result |
|---|---|
| cutseam_fuzz, seed 1 × 3,000 + seeds 2-5 × 5,000 = 23,000 | branch_better **0** (was 1,165); branch_worse 2,918 |
| diff_fuzz42, seeds 1-8 × 8,000 = 64,000 | branch_better 0, crashes 0, claim-count diff 0; only GROUNDED→UNGROUNDED diffs (6,515) |
| r38 fuzz3, grammars r37 + r38 × seeds 1, 2, 3, 7 × 20,000 = 160,000 | r38_pass_main_refuses **0**, crashes 0 |
| r37 c1-c6 (r42 harness copies) | 0 BLOCKER, 0 CRASH. HOLE rows are pass-on-both (main passes too) |
| r36_probe | 4/34 attacks reproduce, 0 broken controls (same as R42) |
| Full suite | **1403 passed**, 2 skipped, 74 xfailed = 1381 baseline + 10 from main's merge + 12 new |
| labels-v2.csv md5 | 6215b526d03147295b003d7ccb0d171f (unchanged) |
| test_measure_rates | untouched |
| Error-A corpus | PASS 5 / NEEDS_WORK 156 / FAIL 175, 2044/3990 grounded; results.json byte-identical to HEAD |
| Error-B corpus (from main) | **certified PASS 7/280** vs main 20/280. Fabrication escaped 11 vs 36. results.json restored |

Error-B certified PASS by class, branch vs main:

| Class | Branch | Main |
|---|---|---|
| claim_heading | 5 | 6 |
| denied_2back | 1 | 3 |
| denied_3plus_back | 1 | 1 |
| denied_adjacent | 0 | 1 |
| denied_heading | 0 | 6 |
| denied_same_sentence | 0 | 3 |
| Every other class | 0 | 0 |

- **No new PASS:** no draft PASSes on the branch that main refuses, and no control twin either.
- **Error-A cost:** control PASS is 190 vs 195 on main.

## Merge of origin/main
`git merge --no-commit --no-ff origin/main` (746f337) was clean, with no conflicts. `ground_check.py` is identical at the merge base bb9b024 and at 746f337. The merge is staged but NOT committed (MERGE_HEAD is present), and the fix sits unstaged on top of it.

## Load-bearing assumption
The structure guarantees "branch ⊇ main" only for the denial path (`_match_denied` and its two consumers). Anything else R40 changed outside that path relies on R42's read-only argument, not on construction. That includes `_header_asserts` (classification) and the bce1ac7 unit-split rewrite, which is used only by the R40 reading and is checked unit-by-unit by `_denial_units`. Not done: a fresh adversarial round on this fix.
