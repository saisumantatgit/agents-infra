# RED-TEAM-R42: final pre-merge adversary on ovn-1115-q1 @ bce1ac7

**Verdict: DO NOT MERGE. 1 BLOCKER class (two mechanisms, B1 and B2): a source that origin/main refuses (FAIL 0.0) certifies PASS 100.0 on bce1ac7. Root cause: one R40 change is not an OR on top of main. Widening `_has_strong_denial` also changes which heading lines `_strong_tokens` cuts out, and main's tests on the cut text are not monotone in it.**

Reference: `git show origin/main:Agent-Assure/scripts/ground_check.py > /private/tmp/claude-501/ovn1115-r42/gc_main.py`. `ground_check.py` is the same at origin/main 7d2da1b and at bb9b024: PR #38 changed only `add_source.py`, `explain_report.py` and docs. Every comparison below runs both modules through their own `main()` with `--json`. Probes are in `/private/tmp/claude-501/ovn1115-r42/probe/` and the reusable harnesses are in `reports/r42_probe/`. No file under scripts/ or tests/ was edited.

## Question
Is there a draft+store that bce1ac7 PASSes/GROUNDs, or scores higher on, where origin/main refuses? **Yes.**

## BLOCKER B1/B2: un-cleared heading lengthens the cut text (`_strong_tokens`)

Mechanism. `_strong_tokens` removes every heading line that `_heading_line_denies` says does NOT deny ("cleared"). It does this so that a FAQ heading welded onto the next sentence is not read as part of it. R40 widened `_has_strong_denial` in place, so `_heading_line_denies` now denies (does not clear) headings that main clears:
- FAQ headings whose remainder holds an R40 shape that is only true at the end of the clause ("we fabricate", "fabricating").
- Topic headings ("## Why the merger did not occur").
- Plain headings ("## The launch never took place", "## The hypothesis was falsified", "## Reporters called it false", "## None of it is real", "## Rivals falsely claimed solvency").

The heading then stays in the welded sentence's `cut_tokens`. Two of main's tests on that text get WEAKER when the text gets longer:

1. **B1, length cap.** In `_paragraph_denied`, the far forward-pointing rule needs `len(t) <= _SCOPE_MAX_TOKENS` (12) for `t` in (full, cut). On main the cut sentence (for example 9 tokens) qualifies. On the branch, cut equals full (14 or more tokens), so the pointing denial is lost for the rest of the paragraph.
2. **B2, code-value exemption.** `_code_value_subject` reads the three words before the copula. Heading words now sit there ("flags we fabricate | is false"), so main's predicative "is false" stops being strong. `following_strong` (the R36 NEW-1 rule) and the paragraph rule are then lost.

The heading's own new denial does not make up for this. Its scope (`_heading_denied`, `_heading_denied_r40`) ends at the next markdown heading of equal or higher level, so text placed after that heading in the same blank-line paragraph keeps only main's (now lost) paragraph rule.

Reproductions. Draft `<claim> [S1].`; one verbatim source S1; claim "Revenue rose to 90000 dollars after the audit". Gate result on origin/main, then on bce1ac7:

| ID | Source text (S1) | origin/main | bce1ac7 |
|---|---|---|---|
| B1a | `## Facts and costs we fabricate\nWe do not believe the next short part.\n# Notes\nStaff left. Records were filed. <claim>. The board met.` | FAIL 0.0 UNGROUNDED | **PASS 100.0 GROUNDED** |
| B1b | `## Fact vs fabricating\nNone of the figures in the next section are accurate.\n## Results\nStaff left. Records were filed. <claim>.` | FAIL 0.0 | **PASS 100.0** |
| B1c | `## Truth or fabricating\nNone of the numbers in the next section are accurate.\n## Results\nThe audit took several months. Staff left. <claim>.` | FAIL 0.0 | **PASS 100.0** |
| B2a | `Staff left. <claim>.\n## Facts and flags we fabricate\nIs false.` | FAIL 0.0 | **PASS 100.0** |
| B2b | `Staff left. <claim>.\n## Facts and flag values we fabricate\nIs fake.` | FAIL 0.0 | **PASS 100.0** |
| ctrl | B1b without its first heading line | FAIL 0.0 | FAIL 0.0 |
| ctrl | B2a with heading `## Facts and flags` | FAIL 0.0 | FAIL 0.0 |

Breadth (`reports/r42_probe/cutseam_fuzz.py`, a targeted grammar of 21 headings × 9 lines × layouts): seed 1 × 3,000 gave **156 branch-better**; seeds 2-5 × 5,000 gave **244 / 262 / 249 / 254** (12 distinct headings each). Total **1,165 branch-better in 23,000** targeted pairs. Those headings include R40b event-negation headings ("## The launch never took place", "## Why the launch never took place", "## Why the merger did not occur"), so the R40b carve-out feeds the same hole. 

Why the R40 gates missed it. `mono.py` checks `main._unit_denied ⇒ R40._match_denied` per position, but its lexicon never puts an R40-only falsity heading in the same paragraph as a pointing line or a code-value copula. Neither does fuzz3, nor the broad R42 grammar below (64,000 pairs, 0 found). This is the R40 load-bearing assumption failing ("every addition is an extra OR"): `_has_strong_denial` is also read as a NEGATIVE input, in the clearing step of `_strong_tokens`. `_heading_line_denies` → `cleared = not denies` → `cut_tokens` → length cap and code-value window.

Fix (recommendation, Systemic). Restore the OR by construction. Compute `cut` with main's clearing rule: a `_heading_line_denies` that uses main's `_has_strong_denial` without `_falsity_construction`. Then evaluate `strong`, `deictic` and `pointing` over the union of alternatives (full, main-cut, R40-cut), so that no R40 change can remove an alternative main had. R40's new heading denials still act through `_heading_denied` / `_heading_denied_r40`, which are OR'd. Add B1a-B2b as red tests; they fail on bce1ac7 today and pass on main's refusal. Why this fix and not one that shrinks the list: any remaining place where a widened predicate feeds a `not` or a length/position test has to be removed, not patched word by word. A word-list narrowing would leave the mechanism open to the next widening.

## Attack 1: merge seam (`_unit_denied` / `_match_denied` / source filter)
- **Textual seam: clean.** Everything after `_anchor_sentence_covers` (ground, evidence_basis, `_self_source_ids`, `_near_copy_of_draft`, score_report, main: all of PR #36's near-copy refactor) is identical between bce1ac7 and origin/main (`diff` of the file tails, 0 lines apart from the offset). None of that code calls `_source_unit_contexts`, `_unit_denied`, `_match_denied` or `_has_strong_denial`. So self-ids and the source filter are the same set on both.
- **`_match_denied` call sites (2): checked, monotone.** `_contained_with_matching_polarity` uses `all(_match_denied)` → continue, and `_anchor_sentence_covers` uses `not _match_denied`. Both are supersets of `_unit_denied` (it is called first, and its result is OR'd).
- **The unit split rewrite (`\n+` first, then `;()`) gives the same units in the same order** as main's single regex (read).
- **The non-monotone input is B1/B2 above.** It is upstream of `_unit_denied` (`context_denied`, `following_strong`), not in the merge.

## Attack 2: multi-source + self-source differential fuzz
`reports/r42_probe/diff_fuzz42.py` extends `reports/r41_probe/diff_fuzz.py`. It reuses all 20 of r41's source kinds: near-copy, path_abs/rel/symlink/hardlink, hash_meta/text, summary, failed, empty, partial/whole_contained. It adds a `denial_ctx` kind (about 60% of sources): the claim set in random R40/R40b structure (FAQ and label headings, 7-24 token pointing lines, event negations, trailing falsity, ZWSP / soft hyphen / alpha / dotless i / Cyrillic). Both modules run through main().

| Seeds | Pairs | Multi-source | branch_better | Claim-count diff | Crashes / non-report diff | Verdict diffs |
|---|---|---|---|---|---|---|
| 1-8 × 8,000 | **64,000** | 38,504 | **0** | 0 | 0 | only GROUNDED→UNGROUNDED (6,415) |

This broad grammar did not reach B1/B2: a markdown heading has to sit inside the paragraph between the pointing line and the claim. Only the targeted grammar found them. The 0 here therefore does not show that the branch is monotone.

## Attack 3: event-negation carve-out ("never took place", "did not occur")
- **The R40b narrowing on its own cannot pass what main refuses.** `_event_negation_points` only narrows a branch of `_falsity_construction` that main does not have (read; and 0 in the fuzz above, with pointing and non-pointing subjects, with and without adjuncts).
- **But the carve-out's STRONG cases feed B1.** A clause-final event-negation heading ("## The launch never took place", "## Why the merger did not occur") is denying on the branch and cleared on main, so it un-clears and opens B1. Found by cutseam_fuzz.

## Attack 4: comparison-copy fold used for a MATCH?
- **No (read).** `_comparison_view` is called in exactly two places: `_header_asserts` (it can only promote a heading to a scored claim) and `_view_unit_contexts`. The latter is read only by `_match_denied`, as an OR'd denial, with a failed alignment read as DENIED.
- **Matching runs only on the original tokens.** `_contained_with_matching_polarity` and `_anchor_sentence_covers` both slice `ctx.tokens`.
- **Heading promotion cannot raise the score.** A promoted heading has no citation (a cited heading is already a claim on main). Its verdict is therefore UNCITED, UNVERIFIED_ABSENCE (ABSENCE is demoted) or UNVERIFIED_RELATION, never a numerator verdict. Probes `heading_promo*.py`: score equal or lower, never higher.

## Regression harnesses (r36, r37, r38, error_a)
| Harness | Result |
|---|---|
| r36_probe | 4/34 attacks reproduce (hole b only), 0 broken controls. Same as R40b. |
| r37 c1-c6 (repointed copies in /private/tmp/claude-501/ovn1115-r42/probe/r37) | 0 BLOCKER, 0 CRASH |
| r38 fuzz3, grammars r37 and r38, seeds 1, 2, 3, 7 × 20,000 = **160,000** (main stands in for both references) | `r38_pass_main_refuses` **0**, crashes 0 |
| error_a corpus (`tests/error_a_corpus/run.py --base <worktree>`) | **PASS 5 / NEEDS_WORK 156 / FAIL 175, 2044/3990 grounded.** The regenerated `results.json` is byte-identical to HEAD's (`cmp`), so no restore was needed. scripts/ and tests/ are clean (`git diff --quiet`). |

The existing harnesses are green **and** B1/B2 exist: none of their grammars has an R40-only falsity heading in the same paragraph as a pointing line.

## Only read, not executed
- The equivalence of the unit-split rewrite.
- The monotonicity of `_paragraph_denied`'s deictic/stem counters under extra strong flags.
- That `_comparison_view` has no match consumer.
- That PR #36's region is untouched (shown by diff, not by running each function).
- The full test suite (`uv run pytest`) was not re-run in R42.
