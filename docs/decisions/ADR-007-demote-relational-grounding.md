# ADR-007 — Demote relational grounding to a diagnostic

- **Status:** Accepted
- **Date:** 2026-10-02
- **Decider:** Sai (Escalation #1 — it moves the Error-A/Error-B trade-off and narrows a shipped product claim)
- **Supersedes:** nothing. **Amends:** the verdict taxonomy's reachability, not its membership.
- **Companion:** `Agent-Assure/calibration/CR-007-relational-demotion.md`, `Agent-Assure/reports/RED-TEAM-R12-2026-10-02.md`

## Context

`ground()` gave RELATIONAL claims a bespoke grounding rule: two distinct
verbatim sources, each carrying one endpoint, plus some ±2-sentence window
asserting a relation between them (OI-MOAT-05), plus a numeric check (R10C-04)
and, from 2026-10-02, a spelled-figure check (J-43).

Round 12 (one Opus adversary, 16 findings, all reproduced) demonstrated **seven
Error-B shapes on that branch, two of them CRITICAL**, every one pre-existing:

| # | Shape | Job |
|---|---|---|
| 1 | A NEGATED endpoint is grounded by sources asserting the positive | J-57 |
| 2 | A trailing clause REPLACES the asserted object (`side_B`'s anchor) | J-58 |
| 3 | A trigger merely CO-LOCATED in the window, not relating the endpoints | J-59 |
| 4 | Direction unchecked — "B because of A" grounds "A causes B" | J-60 |
| 5 | A window that DENIES the relation satisfies it | J-61 |
| 6 | The absence variant of the spelled-figure hole | J-62 |
| 7 | Both endpoints resolving to the SAME phrase | J-64 |

They are not a backlog, they are a **class**. The rule was reconstructing
"this source asserts a relation between A and B" out of token co-occurrence,
against an adversary who writes the document. That is the identical structural
trap the HTML comment stripper lost **five** rounds to (J-41), and the identical
reason T2 was demoted (ADR-006): a surface statistic standing in for a meaning.

Two prior fixes in this area were themselves withdrawn within hours of landing
(D-52 → D-54, and D-68 → D-69), which is the strongest available evidence that
incremental repair here does not converge.

## Decision

**Relational grounding decides nothing.**

1. A RELATIONAL claim **falls through to the ordinary citation/verbatim path**,
   exactly as a FACTUAL claim does. It certifies when a cited source contains
   the claim verbatim (T1) and not otherwise.
2. The entire demoted rule — corroboration, numeric check, spelled-figure
   check — is preserved intact as the pure function `relational_diagnostic`,
   reported per claim as `relation_diagnostic` ∈ {`corroborated_by_two_sources`,
   `not_corroborated`, `figure_not_in_cited_sources`}. **It is information for a
   human, never an input to a verdict**, and an AST guard holds that line.
3. `UNVERIFIED_RELATION` **stays in the taxonomy and becomes unreachable from
   the verdict path.** It is retired, not deleted — the same choice this repo
   made for `tier_sensitive`, for the same reason: a visible no-op cannot
   silently come back to life, whereas a deleted state can be re-added by
   someone who never reads this file.

### Why fall-through rather than a flat refusal

A flat `return UNVERIFIED_RELATION` was the simpler change and was priced at
**Error-A 0.400**. Fall-through measured **0.360** on the same corpus, because
q36's source states the causal sentence outright and therefore still certifies
— through the one guarantee the product actually makes. Fall-through also
**deletes a rule instead of adding one**: a relational claim now has no bespoke
path at all. Four points of Error-A cheaper, and less code in the verdict path.

## The price, measured and not estimated

| | Error-A | Error-B | Open Error-B shapes |
|---|---|---|---|
| Before | 0.320 (8/25) | 0.000 (0/27) | **7, two CRITICAL** |
| After | **0.360** (9/25) | **0.000** (0/27) | **0** |

Across the n=52 gold corpus the relational rule earned exactly **two**
certifications (q12, q36) — five of its seven rows were gold VIOLATIONS it was
already refusing. Verified before landing: **no gold-violation relational row
certifies through the verbatim path.**

Four points of a RECOVERABLE error to close an UNRECOVERABLE class is the trade
the moat invariant exists to make.

## Consequences

- **A draft containing a causal sentence will not PASS unless a cited source
  states that sentence verbatim.** ADR-005 makes a retained violation a hard
  cap, so this is loud and frequent, and it must be said plainly on every
  surface. It is the cost Sai accepted, not a side effect to be discovered.
- **J-43, J-39, J-44 and J-57 … J-61, J-64 become MOOT as verdict defects.**
  Their tripwires are re-pointed at the diagnostic and stay strict, so every
  finding remains measured. J-62 survives: it is the ABSENCE branch.
- The relational machinery (`extract_arguments`, `_endpoint_in_window`,
  `spelled_quantity_ok`, `ground_relational`) is retained and still tested.
- CLAIM-1 narrows. The limitations table gains a row and `test_product_claim.py`
  gains the assertion that keeps it honest.

## Alternatives rejected

- **Fix the seven findings.** Three need design decisions that are Sai's, and
  J-59 cannot be closed without the trigger's ARGUMENTS — i.e. parsing, which
  the moat forbids. Five rounds of evidence say the class survives each fix.
- **Ship with the prose narrowed only.** Leaves Error-B reachable in the
  shipped product, which the invariant calls unrecoverable. Rejected by Sai.
- **Delete the relational path entirely.** Rejected by Sai in favour of keeping
  it as a visible no-op, per the `tier_sensitive` precedent.
