# C1 ruling pack: heading fabrications and far denials (OVN-1121, 2026-11-21)

**Verdict: main certifies two families of fabrication as PASS 100 today, both reproduced first-hand. The fixes only ever refuse more, so they are inside tonight's C1 authority. They were not built because Codex is out of quota until 26 Nov 13:52 and D-119 bars a Claude build fallback.**

**Later classification (D-129, `R45-R46-CLASSIFICATION.md`):** a family here called Error-B or live fabrication is either Class T (it breaks the written "traceable" promise; a bug) or Class S (traceable text the source disowns; disclosed under ADR-008). E1 and E3 are Class S. E2's reassembled headings are Class T and its verbatim-copy variant is Class S.

- **E1, pronoun-subject "made up" after the claim.** A source sentence such as "Quay Trust was acquired by a larger rival last spring." followed by "That was cooked up by the press.", "It was cooked up." or "The press made that up." gets the claim GROUNDED and the draft certified PASS 100. "That never happened." in the same place is refused.
- **E2, a heading built from source words.** A draft heading is never scored (`NON_CLAIM`) if it passes the existing headline tests. That includes a verbatim copy of a sentence the source denies (`## The regulator found fraud at Quay Trust`, source: "… That never happened.") and reassemblies (`## Fraud at Quay Trust`, `## The council never met`). Each certifies PASS 100.

Measured on main `d8c2ec0`. This pack was challenged by an Opus adversary (prompt: "attack the conclusions… re-derive independently"). Its first version was **corrected**: the Family D diagnosis was refuted and the Family H sibling and cost were corrected. The review is summarised at the end, and the first version is in git history (`c5e64a4`).

## Terms

| Term | Meaning here |
|---|---|
| Error-B | A fabrication certified PASS. Unrecoverable; the moat. |
| Error-A | An honest claim refused. Recoverable. |
| Scored heading | A heading checked as a claim. Uncited, it reads UNCITED, and the draft goes to NEEDS_WORK (FAIL in a short draft). |
| Novel word | A heading word, outside a stop list, found in none of the draft's sources (NFKC, lower-cased). |
| R40 | The 2026-11-15 fail-closed fix that refuses "cooked up" only after a content-noun subject ("The story was cooked up"). |

## E1: pronoun-subject "made up" (was "Family D")

**Cause:** a lexical gap in the R40 fix. `_UP_FALSITY_VERBS` (`ground_check.py:3270`) is read only with a content-noun subject, and `cooked` is not in `_DENIAL_TOKENS` (`ground_check.py:3009`). A pronoun subject (`That`, `It`), or "made that up" with the object in the middle, evades it. This is an evasion of a shipped fix.

**Corpus evidence:**

- All 6 escapes in `denied_2back` and `denied_3plus_back` use "That was cooked up by the press.".
- Swapping in "That never happened." at the same distance gets all 4 tested drafts refused.
- The two PASSes are a special case: there "That was cooked up…" opens a paragraph *before* the claim, so its antecedent is the earlier paragraph. Those two are arguably not fabrications.
- Moved *after* the claim, the same phrase denies it and still certifies PASS 100. That is the live Error-B.

**Fix (fail-closed, build when capacity returns):**

1. Read the `_UP_FALSITY_VERBS` predicates ("cooked up", "dreamed up", "made up", "whipped up", …) with a pronoun or demonstrative subject or object too, in the sentence after the claim and within the paragraph.
2. Use proven-red tests for: `That/It was cooked up.`, `The press made that up.`, `Reporters cooked that up.`, and with 0–2 fillers between.
3. Sibling to check: the same verbs before the claim when the pronoun is forward-pointing ("This was made up: …").
4. Measure on the Error-A corpus. Pronoun-subject "made up" in honest prose ("It was made up of three parts") is the obvious Error-A risk; R38 already exempts the constituting sense "made up of". Measure that it holds.

**Withdrawn from the first version:** "the corpus label is the problem" and "narrow the two-back rule". The two-back rule decides 0 of the 26 refused far-denial drafts. They are refused by the paragraph-falsity rule (15), the hedge rule (5) and other paths (6). So narrowing it changes no Family D outcome. "Do not widen the denial window" stands, for a different reason: the misses are lexical, so widening closes nothing.

**Corpus repair (Codex, tests only):** add the denial-after-claim shape with every DENIALS phrase, so E1 is measured by the corpus and not only by a probe. With the current DENIALS list, that rebuild will show the E1 PASSes.

## E2: headings (was "Family H")

On v1, 10 of the 15 `claim_heading` attacks are already scored by the existing headline tests (`ground_check.py:1093-1150`). 5 reach `NON_CLAIM` and PASS. The reviewer found the worse sibling: headings made only of source words, including a verbatim copy of a denied sentence. No body-path denial rule applies to them, because headings never reach `_unit_denial_reason`.

| Candidate rule | Closes | Leaves open | Honest drafts that PASS today and lose PASS (Error-A corpus 5 + usage_genres 4 = 9) | Honest headings scored |
|---|---|---|---|---|
| H1: score a heading with any novel word | 15/15 v1 attack headings | every source-word heading (E2 siblings) | 6 of 9 (PASS 9→3) | 175 of 532 (33%) |
| S: score every heading that is not a verbatim source heading | all of the above, plus the siblings | a heading copied from a source *heading* that the body denies (not measured) | 7 of 9 (PASS 9→2) | 198 of 532 (37%) |
| S + closed label list: as S, but exempt a heading whose every word is in a short closed list of structural labels (notes, overview, summary, steps, known, issues, …) | as S, except claims spelled only in label words | claims spelled only in label words | not measured; it needs the list written first | not measured |

- **The fabrication-corpus control rows are vacuous.** v1 and v2 control drafts contain no headings (0/280, 0/224), so their "0 lost" proves nothing. The 9 honest PASS drafts above are the only measurement.
- **H1's refusal reason is an oracle.** A reason that names the novel words tells a retrying model which words to swap for source words, which is exactly the E2 sibling. Whatever rule ships, its reason should say "a heading not taken from your sources is checked like a sentence", not list words.
- **A closed label list fails safe.** A word missing from it means the heading is scored (refused), never passed.

**Recommendation: ship S + a closed label list, built by Codex (or Claude, on Sai's word), with these measured before merge:**

- the list's Error-A gain over S on the 9 PASS drafts and all 532 headings;
- the label-word claims it leaves open (for example `## Known issues` claims that issues exist);
- an Opus adversary round.

Why: E2 is a live Error-B on main with no rewording needed, and only S-class rules close it. The list recovers the commonest honest headings without letting entity or predicate words through. H1 alone is rejected because it leaves E2 open and its refusal reason points attackers at the open part.

What would flip it: the measured list recovering too little (PASS stays near 2/9). Then the choice becomes a product one for Sai. Either PASS certifies body claims only and the report lists headings as unchecked text (a verdict-semantics change, ADR first), or the writer cites headings.

## Side finding: next-sentence denial across a paragraph break

`verbatim_but_next_sentence_denies` refuses 183 honest claims on the Error-A corpus. 19 of them cross a paragraph break. **A paragraph cut is not safe:** it would certify `<claim>.` followed in the next paragraph by `Quay Trust denies this.` The reviewer estimates that treating "that" after a reporting verb as not pointing back would free about 91 of 183, with its own attack to measure. Both widen passes, so both are Sai's.

## Adversary review (summary)

| Claim in first version | Verdict |
|---|---|
| Family D is a labelling problem; narrow two-back | REFUTED (lexical R40 gap; two-back decides 0 of 26) |
| H1 sibling = reassembled source words only | CORRECTED (verbatim denied sentence as heading, PASS 100) |
| H1 cost 5→2; controls 0/190, 0/93 | CORRECTED (9→3 incl. usage_genres; controls have no headings) |
| "The gate never reads headings" | CORRECTED (10/15 attack headings already scored) |
| Paragraph-break cut is "more principled" | CORRECTED (has its own attack) |
| Numbers 15/15, 3/5, 175/532, 13/16, 37, 183/193 | UPHELD |

Main-loop re-checks, first-hand on `d8c2ec0` with passing positive controls: E1 (4 phrasings, PASS 100; "That never happened." FAIL) and E2 (5 headings, PASS 100; control PASS). The S-rule cost (7 of 9; 198/532) was measured by the main loop after the review.
