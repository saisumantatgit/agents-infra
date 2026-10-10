# MORNING REPORT — 2026-10-03

**Goal set at §0:** that you could merge PR #7 and launch knowing an adversary
had attacked the code that actually ships.

**The goal was met, and the answer is NO. Do not merge.** Round 14 came back
with **three NEW CRITICAL Error-B shapes plus one re-confirmed finding that I
re-graded to CRITICAL** (see below) against the shipping code. That is the run
working, not the run failing: the whole purpose of making the merge conditional
on round 14 was that the answer might be this one.

---

## 1. DONE — each with the command that proves it

**Round 14 (J-68).** Opus adversary, 35 tool calls, 169k tokens. **The adversary
graded 3 CRITICAL (NEW) + 2 Error-B re-confirmed + 1 doc-defect. I re-graded
R14-04 from "HIGH, re-confirmed" to CRITICAL and am stating that rather than
letting the count drift**: it reproduces at PASS 100.0 / exit 0 on a plain
FACTUAL claim, which meets the adversary's own CRITICAL definition, and it is
the root cause of R14-01. So: 3 CRITICAL
Error-B + 1 HIGH doc-defect. **Every finding reproduced by me from the
adversary's own fixtures before being recorded** — round 13's lesson. 7/7
round-12 relational shapes confirmed REFUSED; positive control still PASS 100.0.

```
a1 (triggered): exit=0 gate=PASS score=100.0 kind=NUMERIC  verdict=GROUNDED
a2 (causes)   : exit=1 gate=FAIL score=0.0   kind=RELATIONAL verdict=UNVERIFIED_RELATION
```

**Baseline re-derived, not quoted:**
```
tp=27 fp=10 tn=15 fn=0
Error-A = 10/25 = 0.400     Error-B = 0/27 = 0.000
```

**Gates, run first-hand:** `uv run pytest -q` → **797 passed · 2 skipped · 66
xfailed · exit 0**. Gold md5 `6215b526d03147295b003d7ccb0d171f` unchanged, zero
labels touched.

**Also landed:** 5 strict-xfail tripwires for round 14; the ADR-007 amendment
correcting my own overclaim; the missing positive control on the corpus/loader
test; J-45's display overclaim; a test docstring that described withdrawn
behaviour; CR-008; register rows J-69…J-72 with owners.

## 2. NOT DONE — and why

**Nothing in the gate was repaired, deliberately.** All three candidate repairs
alter which claims can pass → Escalation #1 → yours. Each is priced below.
`ground_check.py` is byte-identical to last night apart from two comment blocks
and one display string.

## 3. DENIED

Nothing was denied by a boundary tonight.

## 4. ONE-WAY DOORS QUEUED FOR YOU

| # | Door | Command / decision |
|---|---|---|
| 1 | **Merge PR #7** | **Do not, yet.** `gh pr merge 7` only after you rule on J-70. |
| 2 | **J-70** — the root cause | Choose: structural repair (sentence-scoped source text for T1) **or** accept-and-disclose. See §Decisions. |
| 3 | **J-62+J-71** — absence figure checks | The cheap one: closes R14-03a at **Error-A 0.400 unchanged**. Say GO and I land it with a proven-red test. |
| 4 | **J-69** — the causal lexicon | My recommendation: **do not fix this way.** It is the wrong layer. |
| 5 | J-54, J-51, q25 | Unchanged, ~12 min, your terminal. |

## 5. UNKNOWNS — I will not remember these

- Whether an honest absence claim naming a model number differently from its
  source would newly fail under the J-62+J-71 repair. **UNVERIFIED** — I built
  the fixture and it did not isolate the effect, because the baseline already
  refused that draft for an unrelated reason.
- Real-draft Error-A at any operating point (J-66). The honest-draft harness has
  **7 drafts**. That is an instrument, not a sample.
- Whether `_SPAN_HEDGE_TOKENS` has the right members at all. Round 14 attacked
  its SCOPE, never its contents.

## 6. BUDGET

**~1.5M new tokens (output + cache creation)** of 3.5M sanctioned, ceiling 4.2M.
Measure named; derived from the session's own artifacts, not from a run summary.
Under budget because three of the five committed rows turned into measurements
and registrations rather than implementations.

## 7. WITHDRAWALS

**I withdrew my own recommendation, after publishing it.** I priced the J-70
repair on the gold corpus at +0.160 Error-A, recommended it in a PR comment,
then ran the honest-draft harness on the same patch: **7 passing drafts → 5
failing**, one of them a verbatim quotation of the cited source reading
`UNGROUNDED`. Same patch, same hour, two instruments, opposite verdicts. Third
instance in three days (D-68's stem, D-69; D-74's fall-through, D-76) of a
correct measurement from an instrument that could not represent the cost — the
first one caught **before** landing.

**I also wasted a cycle on finished work.** I wrote a complete duplicate test
for J-37 before searching the suite; it had been closed on 2026-10-01. I trusted
the register's stated mechanism instead of deriving it from code — the rule I
had written into the overnight instrument an hour earlier. Duplicate deleted;
the register row corrected; the one real gap it was missing (no `pytest.raises`
anywhere in that file) added and mutation-checked.

## 8. FRAMEWORKS APPLIED

- **Theory of Constraints** — round 14 was the upstream node; everything else was
  sequenced behind it, and it changed the whole queue when it reported.
- **Contradiction-as-locator** — the adversary blamed the classifier; the code
  said the hedge window. Tracing the disputed lines found one mechanism behind
  two findings, and the sharper diagnosis is what makes J-69 the wrong fix.
- **Calibration** — every load-bearing number re-derived, each with a positive
  control; "UNVERIFIED" written where a measurement was missing rather than a
  stronger adjective.
- **Asymmetry of error cost** — nothing fail-OPEN was touched; the three
  candidates were priced rather than landed because each alters which claims pass.
- **Case vs Systemic** — J-69 is the case, J-70 is the system; the register says
  so and recommends against the case fix.
- **Name the CEILING** — R14-02 is a `CEILING:` I wrote during J-43 (`"one"`
  excluded from the spelled-number lexicon) returning as the attack itself.
- **Sunk cost, on my own work** — 54 passing tests deleted the moment the
  original was found; a published recommendation withdrawn within the hour.
- **FMEA detectability** — the loud failures were already covered; the silent
  ones (validation deleted and all green; a display asserting a count the
  verdict never used) were not, and those are what got instruments.
