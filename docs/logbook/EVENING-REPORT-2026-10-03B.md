# EVENING REPORT — 2026-10-03, afternoon run (D-87)

**Goal:** a draft cannot certify ITSELF, and ordinary prose naming a product or
standard gets a verdict about the CLAIM rather than a refusal about a model
number. **Both met — the first fully, the second within my authority.**

---

## 1. DONE — with the command that proves it

| Job | Commit |
|---|---|
| **J-83** a draft may not certify itself | `d88b9fa` |
| **J-72 display half** figure refusals made diagnosable | `25d3c71` |
| **J-79** shared vocabulary is not a hedge | `8842a84` |
| **J-82** absence figure refusal no longer reads as a search failure | `e7a899a` |
| **Rounds 17 + 18**, four CRITICALs found and fixed | `48e8561`, `754911b` |
| **Cross-kind guard** for the whole placement class | `48e8561` |
| ADR/CR/register/CLAUDE.md corrections | several |

```
suite    822 → 850 passed, 2 skipped, 66 xfailed, exit 0
Error-A  10/25 = 0.400   UNMOVED        Error-B  0/27 = 0.000   UNMOVED
honest   7 passed, 3 xfailed  UNMOVED   gold md5 6215b526…d171f unchanged
```

**The headline finding was yours, not mine.** Your J-54 plugin test captured the
draft as a source; citing it certified the draft against its own text at PASS
100.0. No adversary was involved — an agent reading the draft it is about to
verify is ordinary behaviour.

## 2. NOT DONE — and why

**J-84** (the absence basis rule is a tripwire: one irrelevant real source
licenses an absence the draft argued for itself) and **J-85** (GROWING the query
list is fail-open, where D-54 recorded only SHRINKING). Both CRITICAL, both
reproduced, both registered. They need `check_absence` to separate queries that
may COUNT from queries that may form the DENOMINATOR — the signature change
J-42 has needed since 2026-10-01, in the function that already produced one
self-inflicted Error-B. **Starting that at 17:00 after fixing four criticals is
how today's mistakes were made.** Neither regresses CR-010.

## 3. DENIED

Nothing was denied by a boundary.

## 4. ONE-WAY DOORS QUEUED FOR YOU

| # | Door | Note |
|---|---|---|
| 1 | **The publish** | Approved as D-83; Escalation #5 reserves the act. Not performed. |
| 2 | **J-72's narrowing** | PASS-enabling, Escalation #1. I shipped only the display half. |
| 3 | **J-69, J-70, J-35** | Unchanged, all yours. |
| 4 | **q25** | One gold label. |
| 5 | **J-78** — 1.9 GB of other projects' scratch | Still not mine to delete; iVal messaged. |

## 5. UNKNOWNS

- **Whether a fifth instance of the placement class exists.** Round 18's census
  of all 15 `ground()` returns says every remaining self-citation hole is in the
  ABSENCE branch — but rounds 16, 17 and 18 each said the previous one was the
  last.
- **The 5-user comprehension test.** Still the only thing that can reverse D-83.
- **Real-draft Error-A** (J-66) — unmeasured outside the 7-draft harness.

## 6. BUDGET

**~1.9M new tokens** (output + cache creation) of 2.5M sanctioned, ceiling 3.0M.
Stopped starting new work at ~1.8M per the degradation clause.

## 7. WITHDRAWALS

- **J-72's narrowing**, pulled from the committed set at tick 1 — I had queued a
  PARKED item, and the goal sentence shrank to what my authority allows.
- **A conditional identifier heuristic**, withdrawn in the same sitting it was
  written: it fired on `100K` and missed `iPhone 15`. I was tuning a classifier
  I cannot validate.
- **"Recall unchanged at 7/14"** — true of my set, false as a claim. J-79 does
  lose a denial whose hedge word the claim itself uses.
- **"Proven red against HEAD~1"** — off by one; the red is at HEAD~2.
- **Nearly: "the guard covers R18-01"** — it did not. Running it against the
  known-broken gate is the only reason I found out.

## 8. FRAMEWORKS

**Case-vs-Systemic** — after three rounds found one class, the fourth response
was a cross-product guard rather than a fourth patch. **FMEA detectability** —
"name the SIBLING" is in this run's own instrument, and I still missed the
sibling branch twice; the guard is the structural answer to my failing to do it
by care. **Asymmetry of error cost** — every landed change is fail-closed or
display-only; the one PASS-enabling repair went back to you. **Calibration** —
every number re-derived, and three of my own published numbers corrected within
hours of publishing them. **Via negativa** — two heuristics removed rather than
tuned. **Park list** — honoured twice, once after I had already queued the item.
