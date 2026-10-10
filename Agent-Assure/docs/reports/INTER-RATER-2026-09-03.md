# Inter-rater check — the independence test FAILED, informatively

**Date:** 2026-09-03 · **Readers:** Pravallika (52/52), Nandu (50/52, stopped at q30).
**Raw submissions:** `calibration/second-reader/`. **Nothing was written to
`labels-v2.csv`** — these are not gold and no generator may touch that file.

## Headline

| pair | agreement | Cohen's κ |
|---|---|---|
| Pravallika vs Sai | 76.9% | **+0.543** — moderate |
| Nandu vs Sai | 58.0% | **+0.160** — slight |
| **Pravallika vs Nandu** | **54.0%** | **+0.092** — none |

**Two independent readers agree with each other at chance.** The purpose of this
exercise was to show that the 52 gold labels are reproducible by someone other
than their author. **They are not.**

## Two defects in the review page, both mine

**1. The item order leaked the answer.** `labeling-v2.csv` is sorted by label —
the first 22 rows are all `grounded`, then a long violation block (6 alternations
where random would be ~26). My page served items in file order. Pravallika's
opening run of 21 "yes" answers, which I first read as carelessness, was
**correct** and tracked the true structure.

This inflates every agreement figure above. True reproducibility is **worse**
than these numbers.

**2. The AI-summary question was the wrong question.** Both readers marked both
`haiku_summary` rows "supported" — 2/2, both readers, same direction. That is
systematic, not noise. The page asked *"Does this summary support the
statement?"* and the honest answer is **yes**: the summary text matches the claim
exactly. The gold says violation for a different reason — **an AI summary cannot
ground anything, whoever wrote it.** That is a rule about provenance, and I asked
about content. The question should be *"Can this be used as proof?"*

## Disagreement with Sai, by evidence type

| type | n | Pravallika | Nandu |
|---|---|---|---|
| verbatim | 38 | 7/38 (18%) | **18/37 (49%)** |
| absence | 9 | 3/9 | 1/8 |
| haiku_summary | 2 | **2/2** | **2/2** |
| unresolved | 3 | 0/3 | 0/3 |

Nandu is at coin-flip on the main category. Combined with the incomplete
submission, either the task was not engaged with or it was genuinely unclear —
and I cannot distinguish those from the data.

## What survives

**22 of 50 rows are unanimous** across all three people (12 grounded, 10
violation). On that core:

| corpus | n | Error-A | Error-B |
|---|---|---|---|
| all 52 (CR-004) | 52 | 0.320 | 0.000 |
| unanimous core | 22 | **0.417** | **0.000** |

Error-A is **worse** on the rows everyone agrees about. Error-B holds at zero on
every subset — mildly reassuring, and n=10 violations is far too small to lean on.

**The gate's design findings are UNAFFECTED.** The matched-pair result, the
reordering attack, the absence-scope defect and the decomposition faults were all
established by construction and direct trace, not by labels. Nothing in ADR-006,
CR-003 or the OI-DEC/ABS fixes depends on these 52 judgements.

**What is affected is every quoted RATE.** Error-A 0.320 and Error-B 0.000 were
already carrying "(n=52, single ratifier)". They must now carry: *"and two
independent readers reproduced those labels at κ=0.54 and κ=0.16, agreeing with
each other at κ=0.09."*

## The finding that outranks the statistics

If two capable adults, given the same claim and the same source, agree only at
chance on *"does this support this"*, then the gate is automating a judgement
**humans do not reliably share**. That is a product fact, not a calibration
detail, and it cuts both ways:

- It may mean the task needs domain competence, and lay readers were the wrong
  population — in which case the fix is a different second labeller.
- Or it may mean the 52 items include many genuinely ambiguous cases, in which
  case a deterministic gate will disagree with *somebody* no matter what it does,
  and the honest product claim shifts from *"it is correct"* toward *"it is
  consistent, auditable, and shows you its evidence."*

**I cannot tell which from this data**, and I am not going to pick the flattering
one. The next test distinguishes them: re-run with the order shuffled and the
AI-summary question fixed, with one lay reader and one reader who knows the
domain. If the domain reader lands near Sai and the lay reader does not, it is
population. If neither does, it is the corpus.

## Alpha criterion #5

Was *"not attempted"*. It is now **FAILED** — a worse state, honestly recorded.
Fixing the page does not un-fail it; only a passing re-run does.
