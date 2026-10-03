# MIDDAY REPORT — 2026-10-03

**Goal set at §0:** that when you're back, Agent-Assure's PRODUCT CLAIM matches
what the code actually does. **Met.** The engine is unchanged; what it claims is not.

**ROUND 15: _pending at the time this skeleton was written._ Its findings and my
adjudication are appended below under "ROUND 15". If that section is missing or
says pending, the run died before it reported and nothing in this report should
be read as adversarially reviewed.**

---

## 1. DONE — with the command that proves it

| Job | Commit |
|---|---|
| **J-73** every report states its own scope | `a7c0e62` |
| **J-74** `support_diagnostic` — contradiction as a measurement | `3ba4216` + `49d1bfa` |
| **J-75** claim surfaces + two stale rates corrected | `26bfd0a` |
| **ADR-008**, **CR-009**, register J-76/77/78 | `a7c0e62`, `83774c5` |

**The gate that mattered.** Both deliverables are display-only, so a moved error
rate would have been proof of a leak into the verdict path:

```
Error-A = 10/25 = 0.400     UNMOVED
Error-B = 0/27  = 0.000     UNMOVED
honest_drafts: 7 passed, 3 xfailed    UNMOVED
suite: 815 passed, 2 skipped, 66 xfailed, exit 0   (797 before; +18 new tests)
gold md5 6215b526d03147295b003d7ccb0d171f          unchanged
```

**Each new test PROVEN-RED** against `HEAD`'s `ground_check.py` via `git show`:
J-73 8-of-9 failed pre-fix, J-74 8-of-9 failed pre-fix.

**The best catch of the run.** The research's recommended disclosure wording said
*"retrieved this session"*. Per **J-56** the gate cannot claim session scope
unless `--session-id` was passed — so shipping that unconditionally would have
been **a fresh overclaim inside the fix for overclaiming.** There are two
variants; the unscoped one says "present in the evidence store supplied to this
run" and names the flag.

## 2. NOT DONE — and why

**Nothing in the verdict path was touched, deliberately.** J-69, J-70 and
J-62+J-71 are open CRITICAL classes, all priced, all Escalation #1, all yours.
**PR #7 remains DO-NOT-MERGE.** The STORM snippet check stayed parked (needs a
third-party clone; you didn't call it and I took silence as no).

## 3. DENIED

Nothing was denied by a boundary.

## 4. ONE-WAY DOORS QUEUED FOR YOU

| # | Door | Command / decision |
|---|---|---|
| 1 | **Merge PR #7** | Not yet. `gh pr merge 7` only after you rule on J-70. |
| 2 | **J-70** — the root cause | Structural repair (sentence-scoped source text for T1) **or** accept-and-disclose permanently. The blunt repair is withdrawn: +0.160 Error-A on the corpus, but 5 of 7 honest drafts fail including a verbatim quote. |
| 3 | **J-62+J-71** | The cheap one: closes R14-03a at **Error-A 0.400 unchanged**. Say GO and it lands with a proven-red test. |
| 4 | **J-78 — 1.9 GB of other projects' scratch** | `du -sh /tmp/claude-501/*/ \| sort -rh`, then `rm -rf /tmp/claude-501/-Users-saisumanthbattepati-vibe-coding-ival-2-0` (1.3G) and `…-iPay` (600M) **only when no session is live in those projects.** I did not touch them — destroying another session's working state is a one-way door. |
| 5 | J-54 · J-51 · q25 | Unchanged, ~12 min, your terminal. |

## 5. UNKNOWNS — I will not remember these

- **The support diagnostic's RECALL is unmeasured** (J-76). 26.7% is its
  FALSE-ALARM rate. How often it MISSES a denying source is unknown, and the
  gold corpus cannot say — no corpus row has the long subject phrase R14-04
  needs. **Quote it as reporting what it can detect, never as closing the gap.**
- **Whether buyers read PASS as "traceable" or "supported."** Untested; it is the
  load-bearing assumption under ADR-008. Five buyer interviews settle it.
- **Whether STORM's stored `snippets` are verbatim page text.** If they are
  model-processed, Agent-Assure tags them `haiku_summary` and refuses 100% of
  STORM's output — the integration fails closed. ~30 minutes to settle.

## 6. BUDGET

**~1.3M new tokens** (output + cache creation) of 1.5M sanctioned, ceiling 1.8M.
Measure named, derived from this session's artifacts. Stopped *starting* new work
at ~1.2M per the degradation clause and spent the remainder finishing.

## 7. WITHDRAWALS

- **A commit on a RED gate, with a message stating a false result.** `3ba4216`
  claimed "815 passed, exit 0"; the run said "1 failed, 814 passed". Corrected in
  `49d1bfa`. Cause recorded: I grepped for a TOP-LEVEL report key set and not a
  PER-CLAIM one — **one KIND of search where the standing order requires three** —
  so `test_per_claim_fields` was invisible to my pre-check. The test worked
  exactly as designed; the process around it did not.
- **The progress file's timestamps were forward estimates, not readings**, and by
  the third row the record claimed a time an hour ahead of reality. Corrected
  from `git log`. Same reflex as the "815 passed": asserting a number I had not
  looked at.
- **Nothing was withdrawn from the design** — ADR-008's three parts landed as
  specified.

## 8. FRAMEWORKS APPLIED

- **Jobs to be Done** — the claim IS the product. A gate whose promise exceeds
  its behaviour fails the job even when every verdict is correct.
- **Asymmetry of error cost** — the whole shape of ADR-008: over-flagging in an
  advisory is free, over-certifying in a verdict is unrecoverable. It is why a
  65–75%-accurate signal ships as a measurement and not a gate.
- **Chesterton's Fence / via negativa** — reused `_SPAN_HEDGE_TOKENS` instead of
  writing a lexicon; changed the SCOPE, not the vocabulary.
- **Name the CEILING** — the diagnostic cannot tell "the study found no link"
  from "no study found a link", and that is in the code, not just here.
- **Calibration** — the run's primary gate was that Error-A and Error-B must NOT
  move, because a display change cannot move them; and twice today the discipline
  caught me asserting a number before reading it.
- **FMEA detectability** — named the sibling every time: the no-`--session-id`
  case for J-73, the kind-gating trap for J-74, the per-claim field set for the
  report schema.
