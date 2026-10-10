# 2026-10-02C — the demotion, and two refinements too many

## What

Sai ruled on the relational branch (demote to a diagnostic, keep the machinery,
ship after the demotion + J-54). ADR-007 was written, implemented, adversary-ed,
**refuted, and re-implemented** — all inside one sitting.

## Why

The delivery queue closed in the morning, and round 12 ended it with seven
demonstrated Error-B shapes on the relational branch. I took the objective back
to Sai rather than closing more jobs: the goal was never "items closed", it was
a product shippable under a claim that is true, and by that measure the morning
had moved backwards.

## Done

| Step | Outcome | Commit |
|---|---|---|
| ADR-007 written | demotion, with the measured price | `c8a233f` |
| Implemented as FALL-THROUGH | Error-A 0.360 | `de0f87b` |
| 33 tests migrated to the diagnostic | delegated, then audited line by line | `de0f87b` |
| CR-007 + 9 jobs closed by demotion | first rate move in three CRs | `4ad1723` |
| **Round 13 REFUTED it** | 6 NEW Error-B, 5 CRITICAL | — |
| **Re-implemented as FLAT REFUSAL** | Error-A 0.400, shapes gone | `fff0514` |
| ADR amended, CR corrected, J-67/J-68 | | `5da240c` |

Suite **793 passed**, 2 skipped, 61 xfailed. Corpus regenerated and stable at
every step; gold md5 `6215b526…d171f` never touched; zero labels.

## Decisions

**D-73 … D-77.** Two are withdrawals of decisions made hours earlier.

- **D-73/D-74** — demote; implement as fall-through, measured at 0.360 against
  the flat refusal's 0.400.
- **D-76 — D-74 WITHDRAWN.** T1 and corroboration are not nested. T1 certifies
  on an 8-token span anchored at the claim's SUBJECT plus set-membership
  coverage, so a causal claim with a long subject had its whole PREDICATE
  checked by "do these words appear anywhere here". Direction reversal, a source
  that explicitly DENIED the relation, and negation reversal all certified PASS
  100.0. **J-57, J-60, J-61 were MOVED ONTO T1, not closed.**
- **D-77 — the figure checks are kind-independent.** R13-01: `PASS` 100.0,
  exit 0, on a fabricated €3.7 million figure, **printing
  `figure_not_in_cited_sources` in the same record**, because `classify` ranks
  RELATIONAL above NUMERIC and the numeric gate read `kind == NUMERIC`.

## Agents

Three. One Opus adversary on the moat (176K tokens, 61 tool calls) — it found
the six shapes. One Opus adversary earlier (round 12, 169K). One Sonnet for the
33-test migration (117K) under a locked spec, audited line by line afterwards.
Routing held: both moat adversaries were Opus and both earned it; the mechanical
migration was Sonnet and its two defects were caught by my audit, not by the
suite.

## Withdrawals

1. **The fall-through implementation (D-74)** — six Error-B shapes.
2. **"No new Error-B; demotion is net-tightening"** — refuted.
3. **J-44's stem (D-68, this morning)** — an Error-B.
4. **"Six pre-existing Error-Bs"** — it was seven.
5. **Two careless edits of my own**, caught by reading not by the suite: a
   first-occurrence replace hit the wrong golden-matrix row, and a blanket
   replace hit four non-relational calibrate rows.

## Reflection

**Two refinements, both inside a ruling, both argued from a correct measurement,
both Error-B.** J-44's stem had a real Error-A behind it; the fall-through
really did measure 0.360 against 0.400. Neither measurement was wrong. What was
wrong was treating one measured quantity as the whole trade while changing
something on the unrecoverable side of the invariant — Error-A is a number you
can read off a corpus, and Error-B is a *space of shapes* that a corpus of 52
rows cannot enumerate. The corpus said fall-through was better and the corpus
was structurally incapable of saying otherwise: **no row has a subject phrase of
8+ tokens, which is exactly what T1's span rule needs.** So the instrument that
justified the refinement could not have detected its cost. That is the real
lesson, and it is sharper than "run an adversary": a measurement is only
evidence about the shapes your instrument can represent, and for Error-B the
instrument is an adversary, never a corpus. Inside a ruling that touches the
moat, a refinement needs its own adversary BEFORE it lands.

## Next

**Sai:** J-54 (2 min, the launch gate) and J-51. Then the new one — **J-66**:
0.400 understates the real-draft Error-A, because ADR-005's hard cap means any
draft with an unquoted causal sentence now fails.

**Claude, next session, in order:** **J-68 — round 14 against the flat refusal**,
which no adversary has seen. Then **J-67** (T1's span+coverage rule and the
hedge check that did not fire — moot for relational, live for FACTUAL, and
invisible to the corpus). Then **J-62** (the absence branch's spelled-figure
hole, the one round-12 Error-B ADR-007 does not close).

**Do not merge PR #7 before round 14.** Two implementations in this area have
now been refuted within hours of landing.
