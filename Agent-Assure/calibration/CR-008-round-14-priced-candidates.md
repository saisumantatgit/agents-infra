# CR-008 — Round 14, and three priced candidates that did not land

**Window:** 2026-10-02 22:07 → 2026-10-03 (overnight run, D-78)
**Supersedes:** nothing. **CR-007 remains the DEPLOYED operating point.**
**Deployed rates are UNCHANGED: Error-A 0.400 (10/25), Error-B 0.000 (0/27), n=52 gold.**

## Projection vs actual

| Item | Projected | Actual | Δ | Verdict |
|---|---|---|---|---|
| J-68 round 14 | adversary runs; findings reproduced and answered | **3 CRITICAL (NEW) + 2 re-confirmed Error-B + 1 doc-defect** as graded by the adversary; I re-graded R14-04 to CRITICAL (stated, not silent — it PASSes at 100.0 on plain FACTUAL and is R14-01's root cause). **All reproduced from the adversary's own fixtures**; 0 repaired | — | done; the repairs are Sai's |
| J-62 absence spelled figure | fixed by me | **merged with J-71 and priced instead**; became Escalation #1 | scope changed | priced, not landed |
| J-67 T1 span/hedge | characterise only | characterised AND priced; **superseded by J-70** with a sharper mechanism | deeper than projected | priced, not landed |
| J-37 corpus/loader | builder rewrite | **was already closed** (`15baf1e`, 2026-10-01); register row was stale | −1 row of work | closed; added the missing control |
| J-45 evidence_basis | stretch | done — display-only wording | pulled forward | landed |
| Token budget | 3.5M new tokens (output + cache creation) | ~1.5M at the time of writing | −57% | under |

## The three candidates, priced and NOT landed

| Candidate | Closes | Error-A | Error-B | Honest drafts | Landed? |
|---|---|---|---|---|---|
| Baseline (shipped code) | — | **0.400** | **0.000** | 7 pass / 3 xfail | — |
| Whole-source hedge scan (J-70) | R14-01, R14-04 h1+h3 | 0.560 | 0.000 | **5 FAIL / 2 pass** | **NO — withdrawn** |
| Figure checks before the absence verdict (J-62+J-71) | R14-03a | **0.400** | 0.000 | not measured | NO — Escalation #1 |
| Extend `_RELATIONAL_RE` (J-69) | 22 fixtures only | not measured | 0.000 | not measured | NO — wrong layer |

**The baseline row is a re-derivation, not a quotation.** Error-A 10/25 and
Error-B 0/27 were recomputed from the current code through the repo's own
feature-row path, and match CR-007 exactly.

## The delta that matters, explained

**J-70's +0.160 Error-A was a false reassurance, and the corpus produced it.**
Four extra false alarms out of 25 reads as tolerable. The honest-draft harness,
run on the identical patch, takes 7 passing drafts to 5 failing — including a
**verbatim quotation of the cited source** reading `UNGROUNDED`, the exact
defect that harness was built to catch (OI-T2-01). Mechanism: nearly every real
source sentence contains some `_SPAN_HEDGE_TOKENS` member, so scanning the whole
source makes nearly every source look hedged.

Recorded as a **withdrawal**, because I had already published the recommendation
in a PR comment before running the second instrument.

## Non-measurement, named explicitly

- **J-70's class cannot be measured by this corpus at all.** No corpus row has a
  subject phrase of 8+ tokens, which is exactly what T1's span rule needs. A
  zero delta here would have been non-measurement; the +0.160 that appeared is
  measured on rows of the wrong shape.
- **J-62+J-71's zero IS a measurement** — 2 of the corpus's 7 ABSENCE rows carry
  a figure, so rows of this shape exist and did not move. **But** both of those
  "figures" are product model numbers (`X200` → `200`; `X200 manual` → **`200
  m`**, registered J-72), so the check is exercised on an unrepresentative shape.
- **J-69 is unmeasured by design** — it is the wrong layer, so pricing it would
  have priced a repair nobody should make.

## Verdict

**No change to the deployed operating point. CR-007 still governs.** Three
CRITICAL Error-B classes are now demonstrated, tripwired strict-xfail, and
registered to Sai as Escalation #1 (J-69, J-70, J-62+J-71). **PR #7 remains
DO-NOT-MERGE** — round 14 was the gate on merging and it did not come back clean.

Suite at close of this CR: **797 passed · 2 skipped · 66 xfailed · exit 0**.
Gold md5 `6215b526d03147295b003d7ccb0d171f` — never touched; zero labels changed.
