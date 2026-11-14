# Reasons for refusal: why claims copied word for word come back UNGROUNDED (2026-11-15)

Status: done, not committed. Worktree `ovn1115-q8`, branch `ovn-1115-q8` (= main 7d2da1b).
Source of the problem: `reports/ALPHA-WALKTHROUGH-2-2026-11-15.md`, steps 10-13 and 17 (inputs in `/private/tmp/claude-501/ovn1115-q8/work/`).

## 1. Verdict

**The refusals were the rules working as written. What was missing was the report saying which rule fired.** Every claim the tester copied word for word and got back UNGROUNDED was refused by one named rule reacting to the source's OWN neighbouring words. That covers the 7 reproduced here, and in the Error-A corpus it is 1,126 of 1,258 UNGROUNDED segments. Now `evidence_basis` names the rule and quotes the words, and `support_diagnostic` carries one code per rule. The fix only changes what the report says: verdicts, scores and gates are identical to main on 70,000 fuzzed drafts and on the 336-draft corpus.

- **Main cause:** the 5-word hedge window (`_span_is_hedged`) does not stop at a sentence boundary. "…finished on Monday **without** errors. The migration moved…" refuses the second sentence. This one rule is 682 of the 1,126 corpus segments (61%) and 4 of the tester's 7.
- **"N percent" (separate bug):** the claim-side figure reader has no "percent" alternative and the source-side reader has one, so a copied "3.1 percent" can never match. The engine now says so. The fix itself would let more claims pass, so it is a ruling (section 3).
- **What this does not fix:** no cause was changed (Sai's ruling). Every honest sentence refused on main is still refused. The difference is that the author now learns why, and the fix line stops telling him to copy the sentence again.

## 2. Cause table: the tester's refused copies, traced

Each row was re-run against the tester's saved drafts and stores. "Code" is the new `support_diagnostic`.

| Draft / claim (copied from source) | Verdict | Cause traced in `scripts/ground_check.py` | Rule / function | New code |
|---|---|---|---|---|
| d1 #5 "The default limit for a new group is four jobs [S1]" (piece of "…four jobs, and the limit can be changed without restarting the scheduler") | UNGROUNDED | `_conjunction_split` cut the sentence at " and ". The source sentence (one unit) holds `("without","restarting")` and the piece has no negation, so the two sides negate different words. | B1 `_negation_polarity_matches` via `_contained_with_matching_polarity` (exact path) and `_anchor_sentence_covers` (span path); split by `_conjunction_split` | `verbatim_but_source_sentence_negates_differently` + split note |
| d2 #2 "The migration moved 2.1 million customer records … forty minutes [S1]." | UNGROUNDED | The 5 tokens before the span are "finished on monday **without** errors", the END of the previous sentence. | `_span_is_hedged` (`_SPAN_HEDGE_LOOKBACK`=5, `_SPAN_HEDGE_TOKENS` holds "without") | `verbatim_but_hedge_word_before_it` |
| d2 #5 "the vendor has proposed a renewal at 16,500 dollars [S1]." (piece of "…14,000 dollars per quarter, and the vendor…") | UNGROUNDED | Split at " and ". The piece starts mid-sentence, so the window is "000 dollars **per** quarter and"; "per" is a hedge token (for "per the vendor"). | `_span_is_hedged`; `_conjunction_split` | `verbatim_but_hedge_word_before_it` + split note |
| d6 #5 "A standard card allows up to twenty items at one time [S1]." | UNGROUNDED | The next sentence "Of **these**, **no** more than five may be audio-visual items…" has a denial word plus a back-reference word. | H1 following-sentence rule in `_unit_denied` (now `_unit_denial_reason`) | `verbatim_but_next_sentence_denies` |
| d6 retry "Books may be kept for three weeks [S1]." | UNGROUNDED | The sentence two back is the same "Of these, no more…"; "these" also counts as a forward-pointing word. | RUN-2026-11-04 `previous2` rule in `_unit_denied` | `verbatim_but_sentence_two_back_denies` |
| d6 #10 "Report the loss at any branch or through the app [S1]" (piece) | UNGROUNDED | Window "What **if** I lose my card" (the FAQ question before it). | `_span_is_hedged` ("if"); `_conjunction_split` | `verbatim_but_hedge_word_before_it` + split note |
| d7 #2 "The immediate cause was an expired TLS certificate on the internal payment gateway [S1]." | UNGROUNDED | Window "but **could not** complete purchases" (end of the previous sentence). The previous-sentence rule would also fire ("this" + "not"). The hedge rule runs first and is the one reported. | `_span_is_hedged` | `verbatim_but_hedge_word_before_it` |
| d4 #1, #3 "…an increase of 9 percent…", "Customer churn fell to 3.1 percent from 4.0 percent…" | UNVERIFIED_NUMBER | The claim reads "3.1" as (3.1, absolute) and the source reads "3.1 percent" as (3.1, percent), so they never match (section 3). | `_NUMERIC_RE` vs `_SOURCE_NUMERIC_RE`; `numeric_ok` | (basis note, no code) |
| d2 retry "No rollback was needed [S1]." | UNVERIFIED_ABSENCE | A sentence-initial "No" classifies the claim as ABSENCE, and an absence claim is never certified. T1 alone would ground it. | `_ABSENCE_RE` `^\W*(?:no|…)\b` in `classify`; J-97 / ADR-009 in `ground` | unchanged (designed behaviour, Error-A) |
| d8 #4, #5 (the invented mayor sentence, split in two) | UNGROUNDED | No exact span in S1: correct refusal. | n/a | split note only |
| d4 #4 table, d5 #3 code block, 5 headings | UNGROUNDED / UNCITED | Not verbatim copies: the table is welded into one claim, the code block is one NUMERIC claim, the headings are scored as statements. | `decompose` / `_is_non_claim` | out of scope (walkthrough fixes 3-5) |

**Count:** 7 copied sentences were refused UNGROUNDED by a named context rule. With the 2 percent sentences and the 1 absence sentence, that is 10 refusals of copied text reproduced from the saved files. The tester counted about 14. The rest were edits he made between runs and did not save ("61 percent", and swaps he tried).

**Not the cause in any traced row:** the near-copy rule (`_near_copy_source_ids`), the non-factive "that" rule (it fires only for "X argued that …"), and splitting that changed the text so it was no longer a span. Every piece was still a contiguous span, and splitting mattered by moving the piece's start or dropping a negation.

## 3. "N percent" copied exactly → UNVERIFIED_NUMBER

**Bug, not design.** It fails closed, so it can only refuse more, never pass more.

- **What the matcher does:** the claim figures come from `_NUMERIC_RE` (`%|bytes|million|billion|bn|k|m`), which has **no `percent` alternative**. Source mentions come from `_SOURCE_NUMERIC_RE`, which **has** `percent`. So "3.1 percent" reads (3.1, absolute) in the claim and (3.1, percent) in the source, `numeric_ok` requires the same unit, and the claim is refused however exactly it was copied. "40 per cent" fails the same way.
- **Why it counts as a bug:** `numeric_ok`'s own docstring promises `25% == 25 percent (both map to unit="percent")`. The two readers disagree about a word the source reader already accepts.
- **Writing "%" does not help:** "3.1%" in the claim against "3.1 percent" in the source passes the figure check, then fails T1 as UNGROUNDED (the token runs differ). The engine message therefore suggests no workaround.
- **Fix (a ruling, not made here):** add `percent` (and `per cent`) to `_NUMERIC_RE`. That lets more claims pass, so it needs Sai's ruling and a red-team round. The R38 ruling pack is measuring spelled percentages separately as candidate C2. This pack does not duplicate that work: the digit+"percent" asymmetry here is a sibling input to the same decision.
- **Shipped now (reporting only):** `unread_unit_note` appends to `evidence_basis` of an UNVERIFIED_NUMBER claim: `In this claim "3.1", "4.0" are followed by the word "percent", which the claim's figure reader does not take as a unit …, so the claim's figure … cannot match the source's percentage, even when copied exactly.`

## 4. The fix (reporting only)

Classification: **systemic fix** of the reporting gap: every exact-containment refusal now carries its reason. The causes themselves are **case resolution by direction** (Sai's ruling: fixing them changes verdicts). They stay open in section 7.

- **Verdict-path changes, all behaviour-preserving by construction:**
  - **Hedge window:** `_span_hedge_hits` returns the hedge words; `_span_is_hedged` is now `bool(_span_hedge_hits(...))`.
  - **Denial rules:** `_unit_denied` is now `_unit_denial_reason(...) is not None`. The same checks run in the same order, and the raise for uncomputed strong flags stays where it was. Each `return True` became a named rule code.
  - **Display-only fields:** `_UnitContext` gains `paragraph_denied`, `heading_denied` and `sentence_index`. `Claim` gains `split_from` (`compare=False`, so equality and hash are unchanged). No verdict function reads any of these, enforced by an AST guard.
- **Display:**
  - **`verbatim_refusal`:** replays T1's exact-containment path over the same helpers and returns the first rule that refused each verbatim occurrence, plus the split piece.
  - **When it runs:** `score_report` calls it only when the verdict is already UNGROUNDED, appends its text to `evidence_basis` (the per-claim row and the retained appendix) and sets `support_diagnostic` to the rule's code.
  - **Example (d6 #5):** `Found verbatim in S1, but the sentence after it holds a denial word and points back or is a short reply, so the gate reads it as denying this one: "Of these, no more than five may be audio-visual items such as DVDs." (word "no"), so the match does not count. Copying the sentence again will not change this: the refusal comes from the source's own wording.`
- **Codes (15):** `verbatim_but_hedge_word_before_it`, `_under_non_asserting_verb`, `_under_disowning_label`, `_after_denial_of_what_follows`, `_paragraph_has_falsity_statement`, `_under_denying_heading`, `_denial_earlier_in_sentence`, `_previous_sentence_denies`, `_previous_line_denies`, `_sentence_two_back_denies`, `_next_sentence_says_false`, `_previous_sentence_says_false`, `_next_sentence_denies`, `_source_sentence_negates_differently`, `_negation_limited_in_source`. They appear only on UNGROUNDED rows (checked in the fuzz). All existing codes are unchanged elsewhere.
- **`explain_report.py`:** the new codes needed a different hint. The UNGROUNDED one ("replace the claim with the source's own sentence") is what the tester had already done. `fix_hint` now gives these rows: "Your copy matched the source exactly … Copying it again will not help. Cite a different sentence that states the fact, or leave it out. If the named words plainly do not deny or hedge this sentence, it is a known over-refusal: please report it." Its code set is pinned equal to the engine's.
- **Guide:** `docs/ALPHA-TESTER-GUIDE.md` adds one verdict-table row and one `support_diagnostic` sentence for the `verbatim_but_*` codes.
- **CEILING (in code):** only the exact-containment path is explained. A claim of 8+ tokens refused on the 8-gram span path with no exact occurrence keeps the old text, and at most 2 occurrences are named. Upgrade path: make `t1_verbatim` return its reason once that path is restructured.

## 5. Proof the verdict did not change

| Check | Result |
|---|---|
| New differential fuzzer `reports/refusal_probe/diff_fuzz.py`, branch vs `origin/main` 7d2da1b through each module's `main()`, seeds 101-112 × 5,000 | **60,000 drafts, 206,764 claims: 0 gate, 0 score, 0 verdict, 0 kind, 0 claim-count, 0 appendix differences; 0 crashes.** Gates PASS 5,907 / NEEDS_WORK 3,981 / FAIL 50,112. 39,572 rows carried a new code (all 15 codes except `negation_limited`, which a unit test covers), none on a non-UNGROUNDED row. |
| `reports/r41_probe/diff_fuzz.py` (R41 store-identity grammar), base pointed at main, seeds 201-202 × 5,000 | 10,000 drafts: `verdict_diff {}`, no gate or score difference, 0 branch_better. |
| Error-A corpus `tests/error_a_corpus/run.py --base $PWD` | Gates `FAIL 175 / NEEDS_WORK 156 / PASS 5`, grounded **2044/3990**. The `summary` block is byte-equal to HEAD's. Only the `diagnostic(s)` fields differ (1,126 segments). `results.json` was restored from HEAD afterwards. |
| Tester's fixed drafts f1-f8 | All still PASS 100.0. |

Corpus reason mix (1,126 of 1,258 UNGROUNDED segments):

| Code | Segments |
|---|---|
| hedge word before it | 682 |
| next sentence denies | 193 |
| denial earlier in sentence | 73 |
| source sentence negates differently | 45 |
| under disowning label | 42 |
| sentence two back denies | 38 |
| previous sentence denies | 23 |
| paragraph falsity statement | 18 |
| next sentence says false | 11 |
| previous sentence says false | 1 |

## 6. Gates

- **Full suite:** 1313 passed, 2 skipped, 61 xfailed. That is the 1291 baseline plus 22 new tests.
- **Proven red:** `tests/test_reason_names_denial.py` was run against an archive of `origin/main`. All 22 tests fail there: no codes, no trigger words, no `split_from`, no `VERBATIM_REFUSAL_CODES`. All 22 pass on the branch. Each case asserts the verdict is still UNGROUNDED, the rule code, and the quoted trigger words. An AST guard checks that no verdict function reads the display names.
- **Labels:** `calibration/labels-v2.csv` md5 is `6215b526d03147295b003d7ccb0d171f`, unchanged.
- **`test_measure_rates`:** not edited, and passing. It recomputes Error-A/B from the live gate, so the deployed rates are unchanged.
- **Calibration rerun and new CR:** not needed. No file under `calibration/` reads `evidence_basis` or `support_diagnostic`, and no verdict moved, so the derived corpus is unchanged.
- **Evidence files:** the fuzz outputs are at `/private/tmp/claude-501/ovn1115-q8/fuzz/` (`rf_101`-`rf_112`, `r41_201`-`r41_202`). The main reference copy is `/private/tmp/claude-501/ovn1115-q8/gc_main.py`.

## 7. Open items (causes left as they are; each needs a ruling because fixing it lets more claims pass)

1. **Hedge window crosses sentence boundaries** (61% of corpus verbatim refusals; 4 of 7 here). This is a defect against the rule's own comment ("without reaching back into an unrelated preceding clause"). Candidate fix: clip the lookback at the sentence/unit start. The sentence-level rules (`_unit_denied` previous/previous2) still cover a real denial in the previous sentence. Recommend this as the first ruling because it is the largest Error-A source with a narrow change. It needs a red-team round on "Not true. X"-shaped denials.
2. **Digit + "percent"** (section 3; sibling of R38 C2).
3. **Split pieces lose context:** a piece is checked against the full source sentence's negations (d1) or starts mid-sentence under the first half's words (d2 #5, d6 #10). Candidate: check the unsplit sentence first.
4. **"these" counts as both a forward and a back reference** (d6: one honest "Of these, no more than five…" refused the sentence before it AND the one two after it).
5. **Sentence-initial "No …" is ABSENCE** ("No rollback was needed") and is never certified (J-97 / ADR-009 design; `_ABSENCE_RE` CEILING).
6. **Display gaps not closed here:** reasons for the 8-gram span path when there is no exact occurrence; a "may be invented" line for claims with no shared 8-word run (walkthrough fix 8); `verbatim_but_previous_line_denies` has no fixture (the splitter welds the line into the sentence first).

**Load-bearing assumption:** that the only verdict-path edits, `_unit_denied` → `_unit_denial_reason` and `_span_is_hedged` → `_span_hedge_hits`, are equivalent. This rests on construction (same checks, same order) plus 70,000 fuzzed drafts and the 336-draft corpus with 0 differences. The fuzz grammar does reach the edited code: 39,572 rows went through `_unit_denial_reason` and `_span_hedge_hits` and came out with a code. An input shape the grammar never produces would still not be covered.
