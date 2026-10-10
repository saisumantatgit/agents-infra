# Adjudication — OI-MOAT-21, T2 soundness

**Date:** 2026-09-02 · **Status:** ESCALATED to Sai (Escalation #1 + lex_tau retirement)
**Inputs:** my conclusion (demote T2) vs the commissioned adversarial challenge
(`Agent-Assure/docs/reports/CHALLENGE-2026-09-02-t2-demotion.md`, which recommended
a coverage repair instead). Adjudicated by direct evidence trace, per CLAUDE.md
"contradiction is a locator" — not by averaging or deference.

## Where the challenge was RIGHT (accepted; my claims corrected)

1. **My Error-A figure was wrong.** I said demotion costs 0.200→0.360 by naive
   counting. Independent re-derivation with the project's own machinery:
   **A 0.200→0.320, B 0.111→0.074**. Matches the challenge exactly.
2. **T2 owns only 1 of the 3 deployed false negatives.** q46 is T2's; q14 and q37
   live in `check_absence`. Demoting T2 reduces Error-B, it does not close it.
3. **The misattribution rule cannot fire on q46 by construction** — `elsewhere` is
   built from OTHER store sources and q46's store holds exactly one. 35/52 corpus
   stores are single-source, so that guard is inert on two-thirds of the corpus.
4. **Demotion makes `lex_tau` a dead parameter** (identical rates at 0.50/0.76/0.95),
   which makes CR-002 vacuous. Demotion therefore needs an ADR retiring lex_tau,
   not a CR. I had not seen this.
5. **`tests/honest_drafts/` contains no T2-only draft**, so the Error-A harness is
   structurally blind to exactly this regression.

## Where the challenge was WRONG (its recommendation is rejected)

It recommends the **coverage repair** — require the cited source to contain every
content token of the claim — on the grounds that it measures A 0.240 / B 0.074 and
so dominates demotion (A 0.320 / B 0.074) under minimise-A-subject-to-B.

**Direct trace of the two decisive rows:**

| row | claim token absent from source | truth | coverage-repair verdict |
|---|---|---|---|
| `grounded_t2` (golden matrix, canonical honest T2 row) | `achieves` (source: `delivers`) | HONEST | **REJECT** |
| q46 (the fabrication the repair exists for) | `mapping` (source: `logistics`) | FABRICATION | **REJECT** |

One novel token each. **Lexically identical.** The repair does not separate the
fabrication from the honest paraphrase — it rejects both.

Its measured A=0.240 is an **artifact of a blind corpus**: the 52 rows contain zero
honest synonym-substitution claims, which is the only case the repair breaks. The
challenge observed the consequence (`grounded_t2` turns red) and recorded it as
"only 2 tests failed" rather than as the counterexample. A fixture asserting the
canonical purpose of the tier is not a fixture to update.

This is the SAME defect the challenge itself found in `tests/honest_drafts/`:
**both harnesses are blind to the case that discriminates the options.** The corpus
cannot see the repair fail; honest_drafts cannot see demotion fail.

## What is actually established

**No lexical feature separates argument-substitution from synonym-substitution.**
Both are one-token deltas against the cited source. This is not a gap in T2's
implementation; it is the ceiling of the lexical method. Therefore:

- T2 cannot be repaired into soundness by any further lexical rule.
- T3 (semantic entailment) is **not optional** — it is the only mechanism that can
  distinguish these two, whichever lexical option is chosen.
- **The n=52 corpus cannot adjudicate this decision**, and no honest CR can be
  emitted from it for either option.

## Recommendation to Sai

1. **Deploy neither option yet.** Both are currently unmeasurable.
2. **Extend the corpus first** with the two missing classes — honest synonym
   paraphrase, and argument-substitution fabrication — then label them. Cheap, and
   it converts a preference argument into a measurement. This makes the second
   blind labeller (J-06) load-bearing rather than a nice-to-have.
3. **Fix both harness blind spots now** (test-only, fail-closed, my authority):
   add a T2-only honest draft to `tests/honest_drafts/`.
4. **My standing lean, to be confirmed by the extended corpus:** demote T2, accept
   A≈0.32, retire `lex_tau` by ADR, and let T3 buy the Error-A back. Demotion is
   honest about the ceiling; the coverage repair conceals it behind a corpus that
   cannot see its cost.

## Load-bearing assumption

That `grounded_t2` (`achieves`/`delivers`) represents a class users actually write.
If honest drafts in practice never substitute a synonym for a source's verb, the
repair's cost is near zero and it wins. **That is an empirical question about real
user drafts that nobody here has measured** — and it is exactly what the corpus
extension in (2) exists to answer.
