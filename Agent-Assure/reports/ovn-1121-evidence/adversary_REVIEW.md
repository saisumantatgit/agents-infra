# Adversarial review: C1 ruling pack (OVN-1121, 2026-11-21)

Target: `/Users/saisumanth/vibe-coding/Agents/ai-overnight-1121/Agent-Assure/reports/C1-RULING-PACK-2026-11-21.md`
Repo: agents-infra main `d8c2ec0`, read-only. All scripts are in this folder; gate runs used the real
capture hook + `ground_check.py --json` through `tests/usage_genres/run.py` helpers
(`cd Agent-Assure && uv run python <script>`).

**Verdict: the numbers reproduce; the Family D diagnosis does not.** The two Family D PASSes come from a
lexical gap in a fix that has already shipped (R40). They are not caused by distance or by wrong labels, and
the same gap certifies an unambiguous fabrication on main today. The report's recommendation 2 targets a
rule that decides none of the 32 Family D drafts.

Format: claim | verdict | evidence. Ordered by severity.

## 1. Family D: what causes the escapes (highest severity)

**1a.** Claim: the 2 PASSes are a labelling problem (denial before the claim, pointing back), so "probably
not fabrications"; fix by relabelling + narrowing two-back (report l.6, l.56, l.60-63).
| **REFUTED as a diagnosis** (the narrow label reading of those 2 drafts holds, see 2b) |
Evidence (`famD.py`): all 6 escapes in the two classes (escaped=True; 2 of them PASS) use the same denial,
`That was cooked up by the press.` Every other DENIALS phrase is refused at 1 to 4 fillers.
`swap.py`: put `That never happened.` or `That is made up.` in its place, at the same distance in the same
4 drafts, and all 4 are refused (paragraph_has_falsity / hedge_word_before_it). `The press made that up.`
and `Reporters cooked that up.` still PASS. So the cause is a lexical gap, not distance or label.

**1b.** Implied claim: with the labels corrected, Family D has no Error-B.
| **REFUTED** |
Evidence (`after.py`, `cooked.py`; news_brief_05 source with the block replaced). Each of these certifies
**PASS 100**, claim GROUNDED, on main:
- `Quay Trust was acquired by a larger rival last spring. That was cooked up.`
- `... last spring. It was cooked up.`
- `... last spring. That was cooked up by the press.`
- `... last spring. Staff left early. That was cooked up by the press.`
- `... last spring. The press made that up.`

These are the "denial after the claim, points back" shape that the report itself calls the true fabrication.
Controls: `The story was cooked up.` is refused, and so is `That never happened.` at 1 to 2 fillers.

Mechanism: R40 (`tests/red_team_moat/test_moat_r40_fail_closed.py:28,52`; `reports/RED-TEAM-R37.md:32,36`
H2/H6) closed "cooked up" only when the subject is a content noun ("The story/account was cooked up").
A pronoun subject (`That`/`It`) evades it. `_UP_FALSITY_VERBS` (`ground_check.py:3270`) feeds only the R40
reading, and `cooked` is not in `_DENIAL_TOKENS` (`ground_check.py:3009-3027`). This is an evasion of a
shipped fix, the case CLAUDE.md's "three-round law" describes. If Codex relabels as recommendation 1 says,
with the current DENIALS list, these PASSes appear as Error-B.

**1c.** Claim: "The gate already refuses 13 of 16 in each class. That is the same refusal rule that costs
honest claims below" (`verbatim_but_sentence_two_back_denies`) (l.57).
| 13/16 **UPHELD**; "same rule" **REFUTED** |
Evidence (`famD.py`, fabricated segment's `support_diagnostic` for all 32 drafts): of the 26 refusals,
`verbatim_but_paragraph_has_falsity_statement` = 15, `verbatim_but_hedge_word_before_it` = 5, UNGROUNDED via
another path (`no_hedge_in_cited_sentence`) = 6, and **two_back = 0**. Recommendation 2 ("narrow the two-back
rule") therefore changes no Family D outcome. If the report's label reading is right, the honest cost in
these classes comes from the PARAGRAPH rule, which the report never names.

**1d.** Claim: "do not widen the denial window (C1-D as planned)" (l.60).
| **UPHELD on the conclusion, CORRECTED on the why** |
The paragraph rule already reaches 3 to 5 sentences back (3plus drafts refused by it, 1c). Widening the
window would close nothing because the misses are lexical (1a). The reason not to widen is that it does
nothing, not only that it costs honest claims.

## 2. Family D: the label argument

**2a.** Claim: "In both classes the denial comes before the claim and points backward" (l.6).
| **CORRECTED** |
Evidence: `fabrications.py:78-84`. DENIALS carries its own `has_back_reference` flag: 6 True, 6 False
(`The story was fabricated.`, `Officials said the whole account is a myth.`, `It was all lies.`,
`Pure fantasy.`, `The event did not occur.`, `Untrue.`). Across the 32 drafts, 22 use a back-reference
phrase and 10 do not. 7 of the 22 use "this" (`This is a myth.`, `None of this is true.`), and the gate
itself lists "this" as a FORWARD reference (`_FORWARD_REFERENCES`, `ground_check.py:3487`). Read as
paragraph-opening topic sentences followed by the account, the 10 unflagged phrases support the corpus
label. The report's "six of twelve" (l.56) is accurate; the headline generalises it to all.

**2b.** Claim: the two PASSes are probably not fabrications.
| **UPHELD (narrowly)** |
Both PASSes (news_brief_05, howto_code_14) use the anaphoric `That was cooked up by the press.` at the start
of a paragraph. Its antecedent is the previous paragraph, so the source does not deny the claim. Point 1b
still stands: the same phrase put after the claim is a live Error-B.

## 3. Family H

**3a.** Claim: the named sibling (a heading built only from source words that reverses the source) is the
hole H1 leaves.
| **CORRECTED: a worse sibling exists** |
Evidence (`sibling2.py`): the source holds `The regulator found fraud at Quay Trust. That never happened.
Quay Trust hid the failures of the bus route. None of this is true.` Prepend a heading to the PASSing
control draft and each of these certifies **PASS 100.0** (heading NON_CLAIM) on main:
- `## The regulator found fraud at Quay Trust` (a verbatim copy of an explicitly denied sentence)
- `## Quay Trust hid the failures`
- `## Fraud at Quay Trust`
- `## Regulator: fraud at Quay Trust`

Every word is in the source, so H1 leaves all of them unscored. This sibling needs no rewording. It defeats
every body-path denial rule, because headings never reach `_unit_denial_reason`. The denied-rumour sources
it needs are the shape of 7 corpus classes.

Second problem: H1's refusal reason names the novel words. A drafting model that sees that reason and
retries is told exactly which words to swap for source words, which leads it to this sibling. The report's
first "why" (l.43, "the refusal says exactly which words to change") is also an oracle for the attacker.

**3b.** Claim: "A heading is a free text channel the gate never reads" (l.42); the gate "classifies it as a
label, never scores it" (l.21).
| **CORRECTED** |
Evidence: `error_b_corpus/results.json`. 10 of 15 claim_heading drafts are already scored FACTUAL/UNCITED by
the existing headline tests (`_header_asserts_main` / `_header_asserts_r40`, `ground_check.py:1093-1150`).
Only 5 reach NON_CLAIM. l.21 is correct for those 5; l.42 is false as written.

**3c.** Claim: H1 cost on fabrication-corpus controls is 0 of 190 (v1) and 0 of 93 (v2).
| **CORRECTED (vacuous)** |
Evidence: `grep -lE '^\s{0,3}#{1,6}\s'` finds headings in **0/280** v1 control files and **0/224** v2
control files. H1 cannot touch them by construction. These rows measure nothing and should not appear as
cost evidence.

**3d.** Claim: honest PASS drafts that lose PASS: Error-A 3 of 5.
| **UPHELD, but incomplete** |
Evidence (`famH.py`): Error-A loses changelog_011 "Known issues", financial_report_011 "Cost pressures" and
sales_report_005 "Regional targets". The report leaves out usage_genres, whose headings it does count in
the 175/532: **3 of its 4 PASS drafts also lose PASS** (b02 "Harbour facts", b04 "Rebase cheat sheet",
b07 "Rainfall points"). Honest PASS falls from **9 to 3** across both honest corpora, not from 5 to 2.

**3e.** Claims: 15/15 attack headings have a novel word; 175/532 (33%) honest headings do; top words
rises 17, limits 16, price 14 ...; "Price rises" is honest 15 times; an exemption list needs "60 or more".
| **UPHELD** (one caveat on what 15/15 shows) |
Evidence (`famH.py`, my own 38/42-word stop list; adding or removing negations changes nothing):
15/15, 175/532 = 32.9%, identical top-word counts, "Price rises" ×15 plus "Pay rises" ×2, 95 distinct novel
words over 80 distinct headings. Caveat: the attack headings come from a fixed 12-template list
(`fabrications.py:72-76`) whose claim words are absent from the sources by construction, so 15/15 is close
to guaranteed. It is not evidence against an adaptive attacker, and 3a shows the adaptation works. The 33%
is also a property of the generator's ~80 heading strings, not of real drafts.

**3f.** Claim: a scored heading has no citation, so the draft becomes NEEDS_WORK.
| **UPHELD, with a qualifier** |
Evidence: the 10 scored attack headings read UNCITED. 9 drafts are NEEDS_WORK at score 75; hr_policy_16 is
**FAIL** at 50.0. A short draft can fall to FAIL, not only to NEEDS_WORK.

**3g.** Question: is there a cheaper rule the report missed?
| **Not found by 2 vectors** (no counter-claim) |
Evidence (`famH_alt.py`): inflection-tolerant matching (s/es/ies/ed/ing) cuts honest cost only from 175 to
167, still catches 15/15, and is an acceptance-licensing lexicon, the D-69 hazard. Allowing words from the
draft body changes nothing (175). I found no cheaper rule that closes the class.

## 4. Two-back honest cost

**4a.** Claim: `verbatim_but_sentence_two_back_denies` refuses 37 honest claims; typical case is a negation
about a different subject.
| **UPHELD; the weight is CORRECTED** |
Evidence (`side.py`): 37 claims (38 segments), every claim found once in its source. All 37 trigger
sentences negate a different subject. They come from about 5 generator templates whose "forward" word is a
deictic determiner or adverb, not a discourse pointer:
- `... filter never left preview and is not documented here` (14)
- `... dark theme ... never made it into this release` (8)
- `The planned rewrite ... never landed in this pull request` (10)
- `Screenshots are not needed for this guide` (2)
- `It has not drawn on the credit line this year` (3)

So 37 measures how often those templates occur, not an independent rate. The report's remedy ("resolve the
denial's subject to the claim's subject", l.63) needs a coreference model; that is the CEILING upgrade path,
not a near-term change. Narrowing "this"/"here" to pronoun use (or to "this" + a `_DISCOURSE_NOUNS` noun)
is cheaper and is the change to measure. It still lets claims pass, so it is still Escalation #1.

## 5. Side finding: next-sentence denials across a paragraph break

**5a.** Claim: 183 claims (193 segments) are refused by `verbatim_but_next_sentence_denies`; 19 cross a
paragraph break.
| **UPHELD** |
Evidence (`side.py`, `side2.py`): 183/193 and 19, reproduced. All 19 next sentences negate a different
subject (listed in `side2.py` output).

**5b.** Claim: a stop at paragraph breaks is "a smaller, more principled cut" (l.69).
| **CORRECTED** |
Evidence (`crosspara2.py`): today the next-sentence rule refuses each of these, which a paragraph stop
would certify:
- `<claim>.\n\nQuay Trust denies this.`
- `<claim>.\n\nNobody at Quay Trust confirms that.`
- `<claim>.\n\nWe dispute this.`

A rebuttal paragraph is a common real-world shape, so the paragraph cut has a named Error-B. Its cost needs
to go to Sai along with its saving.

There is also a larger cut the report missed (`backref.py`, a rough lexical classification). The
back-reference word that licenses each of the 183 refusals is:
- complementizer "that" after a reporting verb ("wrote that", "said that", "noted that"): about **91**
- determiner "this": about 17
- pronoun "it": about 82

Excluding complementizer "that" would release about 5 times what the paragraph cut does. It has its own
attack ("Officials said that never happened."), so it is also Escalation #1 and needs to be measured first.

## 6. Reproducibility

**6a.** Claim: the measurement scripts are reproducible from the description (l.73-76).
| **UPHELD in practice** |
The scripts were deleted and the 40-word stop list is unpublished, so the report's exact run cannot be
replayed. My independent scripts reproduce every number regardless of stop-list choice. Future packs should
keep the scripts, not delete them at teardown.

## Load-bearing assumption of this review

Point 1b depends on news_brief_05 standing for the general case: a single-source store, a claim cited
`[S1]`, and the denial in the same or the next paragraph. It does: the R37 fixtures use the same
`CLAIM + ". The story was cooked up."` shape, and only the subject differs.
