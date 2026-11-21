# E1 pre-merge adversary, round 2: branch ovn-1121-e1 @ a0f4c21 vs main 00becee

**Verdict: 0 blockers.** Nothing main refuses passes on the branch. All 12 honest idioms from round 1 are GROUNDED again. Of the 18 round-1 evasions, 10 are closed and 8 remain. The cost: the narrowing reopened 36 denial shapes that round 1 caught. 7 of them are the disclosed whipped/conjured/thought class and 29 are not disclosed. It also adds one small new Error-A family ("made up to ...").

## Method
- **Harness:** `r2/cmp3.py`, a 3-way version of round-1 `cmp.py`. It loads main (mainchk), round-1 code (`git show 00d01f9:.../ground_check.py` written to `r2/r1code/`) and the branch, all in one process. It builds each store through the real `capture_hook.py` and replays `main()`'s `score_report`.
- **Main baseline check:** the mainchk HEAD is d8c2ec0, not 00becee. But its `ground_check.py` is byte-identical to `git show 00becee:` (checked with diff -q), and d8c2ec0..00becee touches no `scripts/` file. So the comparison holds. The mainchk tree also has unrelated dirty files (a modified `calibration/feature_rows-v2.jsonl` and two untracked E1 test files). They do not affect the gate.
- **Corpus:** 1474 jobs. error_b v1 drafts and controls (560), error_b v2 drafts and controls (538, which includes the 15 `denied_after` drafts), error_a (336) and usage_genres (40).
- **Probes:** 87 round-1 probes (`r2/probes.json`), 65 new probes (`r2/mkprobes2.py`), 18 new probes (`r2/mkprobes3.py`) and 3 "made up of" probes (`r2/probes4.json`), 173 in all.
- **Branch tests:** `test_moat_e1_pronoun_made_up.py`, `test_moat_e1_round2.py` and `test_moat_r42_additive_structure.py`: 70 passed, 3 xfailed (strict).
- **Raw output:** `r2/corpus.log`, `r2/corpus3.log`, `r2/corpus_diff3.json`, `r2/probes*_3.log` and `r2/probes*_diff3.json`.

## Q1: Blockers (branch passes what main refuses)
- **Structure:** `_match_denied` is still `main OR r40 OR e1_context OR e1(prefix) OR e1(suffix minus own)`, and the first two operands are unchanged. It has two callers (lines 1885 and 3947), and both read True as refusal. `_e1_contexts` and `_e1_falsity` can only add a True. An index mismatch raises; it does not pass.
- **Corpus, main vs branch:** 1474 jobs, 0 errors, 0 claims gained, 0 gates up, 0 scores up, 0 claim-count differences. 22 claims were lost (refusal direction) across 20 gate-downs:
  - 12 are v2 drafts, all fabricated: `denied_after_10/12/13/14`, `heading_from_source_words_verbatim_10/12/13/14` and `heading_from_source_words_reassembled_10/12/13/14`. This matches the commit's "12 -> 0 certified".
  - 8 are v1 items, the same ones round 1 reported: the 6 fabricated drafts, plus the controls `howto_code_14` and `hr_policy_11`.
- **Corpus, round 1 vs branch:** identical on all 1474 jobs. The corpora cannot tell the two rounds apart, so every round-to-round difference below comes from probes only.
- **Probes, main vs branch:** 173 probes, 0 gained, 0 gates up, 0 scores up.
- **Result: 0 blockers.**

## Q2: The 12 round-1 honest idioms
- **Recovered: 12/12 GROUNDED / PASS** (round 1 had refused all 12):
  - make it up to them
  - SLA credits
  - made it up the hill
  - share price made it up to a record
  - pharmacist makes it up
  - conjured up memories
  - whipped up support
  - chef cooked it up in ten minutes
  - thought up by the founders
  - cooked up a storm
  - said that staff dreamed up
  - made the figures up 4 percent
- **Reach probes:** all 6 recovered (the idiom placed in the same paragraph, or in the sentence before).
- **New Error-A relative to round 1:** main PASS and round 1 PASS, but the branch refuses:
  - `It was made up to look like a merger.` (both placements)
  - `It was made up to order.`
  - `These were made up to size by the tailor.`
  - **Cause:** in the passive pronoun branch, only `of` is exempt after `up`, so `up to` falls through and fires.
- **Still refused, same as round 1 (main PASS):**
  - made it up by noon / by Friday / by two o'clock
  - made it up last week / today / again (both reconcile and reach senses)
  - chef cooked it up yesterday
  - It was cooked up fresh for guests
  - It was cooked up by the chef
  - It was dreamed up by the founders in 2010
  - It was dreamed up as a slogan
- **Inconsistency:** the strict-xfail reason drops `thought up` because it "is indistinguishable from honest 'It was thought up by the founders'". The same sentence with `dreamed` is still refused. Either the rationale or the verb list is inconsistent.

## Q3: Evasions
### Round-1 evasions: 10 of 18 closed
- **Closed:**
  - made it all up
  - made up the whole thing (the dead branch is fixed)
  - made the whole story up
  - made up the story
  - made everything up
  - made all that up
  - made stuff up
  - cook it up
  - cooking it up
  - dream these up
- **Remain (8):**
  - zero-width space inside the verb
  - soft hyphen inside the verb
  - long relative clause between subject and verb ("That claim, which ran ..., was cooked up")
  - `They made up the acquisition.` ("acquisition" and "deal" are not discourse nouns)
  - whipped together
  - denial in a later paragraph
  - denial 3 or more sentences away across a paragraph break
  - `The following was cooked up: {C}`

### New evasions relative to round 1 (round 1 FAIL, branch PASS, main PASS): 36 probes
- **(A) Clause-start rule, 13 probes:** the passive pronoun must start the clause or follow but/and, so any lead-in word disables it:
  - `Officials said that was cooked up.`
  - `Officials say it was dreamed up.`
  - `However, that was cooked up.` (before and after placements)
  - `Frankly, it was cooked up.`
  - `In truth, it was dreamed up.`
  - `..., yet that was cooked up.`
  - `Although ..., that was cooked up.`
  - `... - that was cooked up.`
  - `...: that was cooked up.`
  - `This one was cooked up.` (before and after placements), and the forward-colon `This one was cooked up: {C}`, which round 1 caught and which reopened.
  - **Note:** the honest idiom this rule was meant to protect, `said that staff dreamed up`, is already excluded by the auxiliary check, because `staff` is not an auxiliary. The rule actually protects relative clauses (`The plan that was dreamed up by staff worked`, which is GROUNDED). A narrower guard is possible: exempt a `that`/`which` that directly follows a noun, rather than requiring clause start.
- **(B) Tail filter, 8 probes:** only auxiliaries and -ly words may sit between pronoun and participle:
  - `That was all cooked up.`
  - `That was just cooked up.`
  - `That was then cooked up.`
  - `That may have been cooked up.`
  - `That would have been dreamed up.`
  - `That must be cooked up.`
  - `It all was cooked up.`
  - `It got cooked up by reporters.` (no `got` passive)
  - **Fix:** add modals (may, might, must, would, could, should, can), `got`, and the adverbs all, just, then, simply, really, totally.
- **(C) Terminal-adjunct rule on the active split object, 8 probes:** anything after `up` other than a listed time or by-phrase disables it:
  - `Reporters made it up out of thin air.`
  - `... out of whole cloth.`
  - `The press cooked it up to sell papers.`
  - `Reporters cooked that up as a joke.`
  - `Reporters made it up, they admitted.`
  - `Reporters made it up entirely.`
  - `Reporters made that up entirely.`
  - `Reporters made it up wholesale.`
  - **Severity:** "made it up out of thin air" is arguably the most common fabrication phrasing in English.
  - **Fix:** allow -ly adverbs, `wholesale`, `out of (thin air|whole cloth|nothing)`, `as a`, `to <verb>`, and a comma-terminated clause. Keep the `to them`, `to a`, `the hill` and `with` exclusions that protect the idioms.
- **(D) Disclosed, 7 probes:** whipped/conjured/thought up with a pronoun (passive x3, active x3, plus before-placement x1). This matches the 3 strict xfails and the CEILING text.
- **Severity:** all 36 pass on main too, so none is a blocker. They are fail-open regressions against round 1's coverage, and no test or CEILING note records classes A, B or C. The commit and report describe the change as narrowing "for cooked/made/dreamed up only". They do not say that the clause-start and terminal rules also drop common forms of those same verbs.

## Recommendation
**Merge-safe on the moat** (0 blockers, 1474 corpus jobs plus 173 probes). Before merging, I recommend either adding xfail(strict) tests plus a CEILING line for classes A, B and C, or applying the narrow fixes above. The reason: the tests now pin only the shapes that were closed. Without a disclosure, a later reader will take "pronoun made/cooked/dreamed up is refused" at face value, and `However, that was cooked up.` passes. The `made up to` Error-A is minor and can be fixed by adding `to` to the post-particle exemption on the passive branch, behind a guard so that `made up to deceive` still fires.

## Load-bearing assumption
The verdict rests on the probe set being representative. The corpora are identical between round 1 and the branch, so every round-to-round claim here depends on 173 handmade probes. Natural denials in real sources (lead-in adverbs, reported speech) are plausibly more common than the bare `That was cooked up.` that the tests use.
