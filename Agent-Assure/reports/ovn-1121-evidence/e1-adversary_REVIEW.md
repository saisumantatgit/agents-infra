# E1 pre-merge adversary review: branch ovn-1121-e1 @ 00d01f9 vs main d8c2ec0

**Verdict: 0 blockers.** No claim passes on the branch that main refuses. There are 18 evasions (fail-open, known kind), one dead code branch, and 12 new Error-A refusals of honest prose, plus 1 corpus Error-A the report does not disclose.

## Method
- Harness `cmp.py` (in this folder) loads both `ground_check.py` modules in one process. It builds each store through the real `capture_hook.py` and replays `main()`'s `score_report` call, then compares gate, score and the verdict of every claim.
- Corpus run: 1384 jobs covering error_b v1 (drafts + controls, 560), error_b v2 (drafts + controls, 448), error_a (336) and usage_genres (40). Probe run: 87 handmade probes (`mkprobes.py`, `probes.json`), with the claim taken from the R45 E1 family.
- Raw output: `corpus.log`, `corpus_diff.json`, `probes_diff.json`.
- I also ran the E1 test file plus the R42 guard on the branch: 44 passed.

## Q1: Error-B regression (branch passes what main refuses)
- **Code path:** `_match_denied` returns `main OR r40 OR e1_context OR e1(prefix) OR e1(suffix minus own)`. The function has only two callers (lines 1885 and 3924), and both treat True as a refusal (`all(...) -> continue`, `not _match_denied`). So the change can only add refusals.
- **No silent failure path:** `_e1_falsity` and `_e1_contexts` have no early return that yields "not denied" in place of main's verdict. The `own` filter and `_made_up_takes_object` only narrow the new OR term and cannot touch the first two operands. `_e1_contexts` reuses `_sentence_spans`, which raises if a sentence cannot be located. A gate error is not a PASS: `main()` leaves the verdict path unguarded, so it raises and exits non-zero.
- **Measured:** 1471 jobs (corpus plus probes). 0 claims went from refused to GROUNDED, 0 gates went up, 0 scores went up, 0 claim-count differences, 0 exceptions.
- **Result: 0 blockers.**

## Q2: Evasions (fail-open; findings, not blockers)
Each of these passes on BOTH main and the branch (PASS 100):
1. **Close to the tested shapes:**
   - `Reporters made it all up.` The tests cover `made that up` and `making all of it up`; "made it all up" is the most common English form of this phrase.
   - `The press made up the whole thing.` This is a code bug: the post-particle `("the","whole","thing")` check can never run for make-verbs, because `_made_up_takes_object` reads the leading "the" as an object and `continue`s first. `cooked up the whole thing` is caught.
   - `made the whole story up`: the split-object window only looks 1 to 2 words ahead.
   - `made up the story`, `made up the acquisition`: the "the" exemption swallows them.
   - `made everything up`, `made all that up`, `made stuff up`.
2. **Inflections:** `cook it up`, `cooking it up`, `dream these up`. Only `cooked`, `dreamed`, `dreamt`, `thought`, `conjured`, `whipped` and the make forms are listed.
3. **Obfuscation:** a zero-width space or a soft hyphen inside "cooked" evades (the CEILING note discloses this). Cyrillic look-alikes, full-width letters, line breaks, both kinds of quotes, the hyphenated `cooked-up tale` and intervening adverbs are all caught.
4. **Distance:** the denial in a later paragraph (blank line between) evades; so does the same paragraph at 3+ sentences when the subject is not a pronoun. A long relative clause between subject and verb also evades (`That claim, which ran ... week before, was cooked up.`), because the referent sits more than 6 tokens back.
5. **Forward-pointing sibling:** `The following was cooked up: {C}` evades ("following" is not a referent). `This one was cooked up: {C}` is newly caught. The make-up forms (`What follows was made up`, `The claim below is made up`, `Here is what the press made up:`) were already refused on main.
6. **Out of family, for the record:** `whipped together` evades. `invented`, `concocted`, `trumped up`, `That's made up`, `It's all made up` and `made-up story` were already refused on main.

## Q3: Error-A (honest prose newly refused; main PASS 100, branch FAIL 0)
- **Probes, 12 newly refused:**
  - `The firm promised to make it up to them.`
  - `If we miss the target, we make it up with credits.` (support or SLA docs)
  - `The convoy made it up the hill.`
  - `The share price made it up to a record.`
  - `The pharmacist makes it up on request.`
  - `This deal conjured up memories of 2008.`
  - `This news whipped up support among staff.`
  - `The chef cooked it up in ten minutes.`
  - `It was thought up by the founders in 2010.`
  - `It cooked up a storm in sales.`
  - `Analysts said that staff dreamed up a new plan.` ("that" as a conjunction is read as a referent)
  - `Strong sales made the figures up 4 percent.`
- **Root cause:** any of that/this/it/these/those within 6 tokens BEFORE `<verb> up` fires, whether or not it is the subject. "Make it up" (reconcile, compensate, reach) is read as fabrication.
- **Reach:** a single idiom refuses every claim in its paragraph. 6 of 6 reach probes (sentence before, or 3 sentences after in the same paragraph) were newly refused.
- **Correctly unchanged:** `made up of`, `made up the shortfall`, `It's made up of`, `make-up artist`, `made up its mind`, `made up for`, `made up the majority`, `make up ground`, `made up to look`. `deficit was made up by`, `made up from`, `made up entirely by`, `not made up`, `made it up` (reconcile) and `made up` (kiss and make up) were already refused on main.
- **Corpora:** the error_a corpus (336 drafts) and usage_genres (40) show 0 changes, matching the report. That is because neither corpus contains up-idioms, so a zero there measures nothing for this rule.
- **Undisclosed corpus Error-A:** in the v1 control `hr_policy_11_denied_2back`, the honest claim "Managers respond to a request within 37 working days" goes GROUNDED to UNGROUNDED (gate NEEDS_WORK to FAIL). It is the sentence right before a blank line and "That was cooked up by the press." The report lists only `howto_code_14`, because it counts PASS losses, not claim losses. In fairness, "That" can grammatically point back at this exact claim, so refusing it is defensible.
- **Wanted losses on fabrication drafts:** 6 fabricated segments are now refused, in changelog_04, faq_17, howto_code_14, hr_policy_11, news_brief_05 and news_brief_06.

## Load-bearing assumption
"Additive" holds only while both callers keep reading `_match_denied` as refusal-only. If anyone later reuses `_denial_units` / `_match_denied` as positive evidence (for example, a denial supporting a negated or absence claim), the paragraph-wide `e1_context` would turn into an Error-B source.
