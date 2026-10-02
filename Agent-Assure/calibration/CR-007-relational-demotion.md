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
| 4 | Round 13 adversary | — | 0.18M | — | 16 findings, **6 NEW Error-B, 5 CRITICAL** |
| — | Error-A, flat refusal (variant A) | **0.400** | **0.400** | **0** | **ADOPTED (D-76)** — priced for Sai, and correct |
| — | Error-A, fall-through (variant B) | — | 0.360 | −0.040 | **WITHDRAWN (D-76): the 4 points bought 6 Error-B shapes** |

**Δ explanation (required):** the projection was RIGHT and my refinement was
wrong. Fall-through measured 0.360 because q36 still certified through the
verbatim path — a correct measurement of an incomplete trade. Round 13 showed
the same path certifying direction reversals, denied relations and negation
flips at PASS 100.0. The flat refusal's 0.400, priced before the ruling, is the
real number.

## Rates

| Metric | CR-006 | **CR-007** | Basis |
|---|---|---|---|
| Error-A | 0.320 (8/25) | **0.400 (10/25)** | n=52 gold, single ratifier |
| Error-B | 0.000 (0/27) | **0.000 (0/27)** | 95% upper bound ~10.5% — never quote as zero |
| Open Error-B shapes, relational | **7 (two CRITICAL)** | **0** | closed by demotion, not by repair |
| Gold md5 | `6215b526…d171f` | **unchanged** | zero labels touched |
| Suite | 789 / 2 / 61 | **793 / 2 / 61** | passed / skipped / xfailed |

Two rows moved, both gold-grounded, both now false alarms: **q12** and **q36**
(`GROUNDED → UNVERIFIED_RELATION`). The five gold-violation relational rows keep
the same refusal and the same label. `UNVERIFIED_RELATION` is reachable again
and means exactly one thing: **this gate does not certify relations.**

## What this corpus does and does not measure

**MEASURED.** The demotion is the best-measured change in this window's history:
all 7 relational rows carry the shape, every verdict was re-derived, and the
critical property was checked directly — no gold-violation relational row
certifies through the verbatim path.

**MEASURED AND REFUTED ONCE.** (a) Whether the demotion OPENED anything: round
13 found that the FIRST implementation did — six shapes — and the corpus could
not have caught any of them, because **no corpus row has a subject phrase of 8+
tokens**, which is what T1's span rule needs. The corpus is not an adversary.
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

**Launch readiness: round 13 is answered, and it cost a withdrawal.** The
relational branch now refuses unconditionally and the figure checks are
kind-independent. What is NOT established: no adversary has yet run against THIS
state of the code — round 13 attacked the fall-through. J-54 (Sai, 2 min)
remains the last human gate, and a round 14 against the flat refusal is the
first item of the next session.
