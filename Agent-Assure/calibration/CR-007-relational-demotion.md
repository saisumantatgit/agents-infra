# CR-007 — relational demotion (ADR-007)

Window: 2026-10-02, branch `delivery-queue-2026-10-02`. Ratifications D-73…D-75.
**Supersedes CR-005 as the deployed operating point** — this is the first change
in three CRs that moves a rate.

## Projection vs actual

| # | Step | Projected | Actual | Δ | Note |
|---|---|---|---|---|---|
| 1 | ADR-007 written | — | — | — | `c8a233f` |
| 2 | Demotion implemented + measured | — | — | — | `de0f87b` |
| 3 | 33-test migration | — | 0.12M | — | delegated (Sonnet), then audited line by line |
| 4 | Round 13 adversary | — | **IN FLIGHT** | — | **verdict UNKNOWN at close** |
| — | Error-A, flat refusal (variant A) | **0.400** | — | — | priced for Sai before the ruling |
| — | Error-A, fall-through (variant B) | — | **0.360** | **−0.040** | adopted (D-74) |

**Δ explanation (>20% of the delta, required):** the projection assumed every
relational claim would be refused. One (q36) still certifies, because its cited
source states the causal sentence outright and the ordinary verbatim path grounds
it. The projection priced the capability as all-or-nothing when the verbatim path
already covered part of it.

## Rates

| Metric | CR-006 | **CR-007** | Basis |
|---|---|---|---|
| Error-A | 0.320 (8/25) | **0.360 (9/25)** | n=52 gold, single ratifier |
| Error-B | 0.000 (0/27) | **0.000 (0/27)** | 95% upper bound ~10.5% — never quote as zero |
| Open Error-B shapes, relational | **7 (two CRITICAL)** | **0** | closed by demotion, not by repair |
| Gold md5 | `6215b526…d171f` | **unchanged** | zero labels touched |
| Suite | 789 / 2 / 61 | **793 / 2 / 61** | passed / skipped / xfailed |

One row moved: **q12** `GROUNDED → UNGROUNDED` (gold: grounded) — the single new
false alarm. Five gold-violation relational rows moved
`UNVERIFIED_RELATION → UNGROUNDED`: same refusal, different label. `q36` still
certifies. **`UNVERIFIED_RELATION` is now produced by ZERO of the 52 rows** —
retired from the verdict path, retained in the taxonomy.

## What this corpus does and does not measure

**MEASURED.** The demotion is the best-measured change in this window's history:
all 7 relational rows carry the shape, every verdict was re-derived, and the
critical property was checked directly — no gold-violation relational row
certifies through the verbatim path.

**NOT MEASURED.** (a) Whether the demotion OPENED anything on the verbatim or
absence path — that is round 13's job and its verdict is UNKNOWN at close.
(b) The real-draft Error-A. One false alarm in 52 rows understates it badly:
ADR-005 makes a retained violation a hard cap, so **any** draft containing an
unquoted causal sentence now fails, and causal sentences are common. The corpus
has 7 relational rows; a research draft can be half relational. **This is the
number to watch after launch, and it is not 0.360.**

## The lesson

Seven Error-B shapes on one rule is not a backlog, it is a **class**, and the
cheapest way to close a class is to stop asserting the thing. Two prior fixes in
this area were withdrawn within hours of landing (D-52→D-54, D-68→D-69) — that
is the convergence evidence, and it pointed at demotion long before anyone
counted the shapes.

## Launch claim

Narrowed on all four shipped surfaces, with the consequence stated as a
consequence: *a draft containing a causal sentence will usually not PASS.*
Pinned by `test_LIMITATION_a_relational_claim_is_never_certified_by_corroboration`
and by two guards — `ground()` references none of the demoted machinery (AST),
and the machinery is KEPT rather than deleted.

**Launch readiness: NOT ESTABLISHED at the time of writing.** Round 13 has not
reported. J-54 (Sai, 2 min) remains the last human gate.
