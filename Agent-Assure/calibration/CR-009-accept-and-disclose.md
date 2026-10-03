# CR-009 — ADR-008 shipped: the claim changed, the engine did not

**Window:** 2026-10-03 09:51 → 12:30 IST (day run, D-80)
**Supersedes:** nothing. **CR-007 remains the DEPLOYED operating point.**
**Deployed rates UNCHANGED: Error-A 0.400 (10/25), Error-B 0.000 (0/27), n=52 gold.**

## Projection vs actual

| Item | Projected | Actual | Δ | Verdict |
|---|---|---|---|---|
| J-73 scope statement | footer on every report | landed; **two variants**, because the research's wording claimed session scope the gate may not claim without `--session-id` (J-56) | +1 variant | done |
| J-74 support diagnostic | deterministic signal, never a verdict | landed; flags **both** round-14 CRITICALs that still certify at PASS 100.0 | — | done |
| J-75 claim surfaces | wording only | wording **+ two stale error rates corrected** (0.320/CR-004 → 0.400/CR-007) | +1 defect found | done |
| ADR-008 | record the decision | written with its evidence and its rejected alternatives | — | done |
| Round 15 | adversary on both new surfaces | dispatched | — | see report |
| Budget | 1.5M new tokens | ~1.1M at time of writing | −27% | under |

## The rates, before and after — this is the gate that mattered

| Measure | Before | After | Moved? |
|---|---|---|---|
| Error-A (n=52 gold) | 0.400 (10/25) | **0.400 (10/25)** | **no** |
| Error-B (n=52 gold) | 0.000 (0/27) | **0.000 (0/27)** | **no** |
| `tests/honest_drafts/` | 7 passed / 3 xfailed | **7 passed / 3 xfailed** | **no** |
| Suite | 797 / 2 / 66 | **815 / 2 / 66** | +18 tests only |
| Gold md5 | `6215b526…d171f` | `6215b526…d171f` | **no** |

**Both deliverables are display-only, so a moved rate would have been proof of a
leak into the verdict path.** Nothing moved. That was the run's primary gate and
it is the reason the rates appear here as a *result* rather than a reassurance.

## The new diagnostic's own error rate — PUBLISHED, NOT TUNED

`support_diagnostic` fires `cited_sentence_may_not_assert_claim` on:

| Population | Fire rate |
|---|---|
| All scored claims (n=52) | 10/52 = **0.192** |
| **Claims the GATE passes** | **4/15 = 0.267** ← the false-alarm rate that matters |
| Claims a human LABELLED grounded | **7/25 = 0.280** |
| **RECALL — denials it CATCHES** | **7/14 = 0.500** (named 14-vector set, 2026-10-03) |

**R15-02, corrected.** This row first read `7/27 = 0.259`, using the labelled-VIOLATION denominator. Gold is **25 grounded / 27 violation**, so the figure is 7/25 = 0.280. Round 15 reproduced the 26.7% headline, the 10/52, Error-A 0.400 and Error-B 0.000 exactly — this one row was wrong, in a CR about a diagnostic's own error rate.

**1 in 4 of its flags is a false alarm; it misses about half the denials we
could construct.** Misses: next-sentence denial, `retracted`, `erroneous`,
`lacks`, `absent`, `zero`, post-semicolon. **One apparent catch is spurious** —
*"a claim since debunked"* fires on `claim`, not `debunked` (same artefact as
`per`, J-79) — **so both headline numbers are wrong in opposite directions.** Tolerable for an advisory that
refuses nothing; intolerable for a gate — which is precisely why ADR-008 ships
it as a measurement. **It is published rather than tuned** because tuning a
signal nobody has re-validated is how 2026-10-02 produced two Error-Bs. The
number appears in the function's docstring, in `README.md`, in `SKILL.md` and in
`commands/assure-verify.md`, so a user meets it in the same breath as the flag.

## Non-measurement, named explicitly

- **The diagnostic's RECALL is unmeasured.** The 26.7% above is its false-alarm
  rate. How often it MISSES a denying source is unknown, and the corpus cannot
  say: no corpus row has a long subject phrase, which is the shape R14-04 needs.
  Round 15 was dispatched to attack exactly this; see its report.
- **The CEILING is in the code:** a token scan cannot distinguish "the study
  found no link" from "no study found a link". Both fire. Upgrade path is J-70,
  which is Sai's (Escalation #1).
- **The load-bearing assumption of the whole decision is untested:** that buyers
  read PASS as "traceable", not "supported". Five buyer interviews would settle
  it. Nothing in this CR substitutes.

## Defects found while doing other work

Two stale error rates on claim surfaces (0.320/CR-004 after ADR-007 had raised
it to 0.400), and a commit made on a RED gate with a message stating a false
result (`3ba4216` → `49d1bfa`). **Narrative extracted per ADR-025's 80-line
ceiling:** `docs/logbook/2026-10-03B-four-censuses-and-the-shapes-they-could-not-see.md`.

## Round 16 correction to this CR's own evidence

**The zero delta is close to NON-MEASUREMENT, not the measurement this CR
claimed.** Rates reproduce (10/25, 0/27) and the corpus does hold 2
figure-bearing ABSENCE rows, but **q22's delta cannot register by construction
(already a violation), so the zero is an n=1 reading on a model number.** A
synthetic sweep flips 6/9 figure-bearing certifiable absences, and the check's
placement has since been corrected (R16-01: 1,904 of 1,910 verdict changes were
relabels of an existing refusal). Detail: `reports/RED-TEAM-R16-2026-10-03.md`.

## Verdict

**No change to the deployed operating point. CR-007 still governs.** What changed
is what the product CLAIMS: every report states its own scope, the contradiction
signal ships as a measurement with its own error rate attached, and no surface
says "verified" unqualified. **PR #7 remains DO-NOT-MERGE** — J-69, J-70 and
J-62+J-71 are open CRITICAL classes, all Escalation #1, all Sai's.
