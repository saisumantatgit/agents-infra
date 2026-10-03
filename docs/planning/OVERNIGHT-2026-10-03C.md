# OVERNIGHT INSTRUMENT — 2026-10-03C, 21:44 → 06:00 IST

**HOW TO DERIVE the work each cycle. No list of answers.** A wrong fact baked
into a recurring tick executes every tick; a wrong fact here is correctable
between ticks. If this file and the tick disagree, this file wins.

**GOAL (business terms):** tomorrow an honest draft that quotes its source
verbatim is no longer refused as a self-citation, the absence path cannot be
bought with the draft's own queries, and Sai has a runner that can tell him
whether ANY candidate feature separates the cases his gate actually fails on.

---

## §1 THE FOUR RULINGS THIS RUN EXECUTES (Sai, 2026-10-03, "all approved")

1. **PASS-enabling relaxation: NO**, and not "not yet" — the basis is wrong, not
   the timing. Record it; do not implement anything toward it.
2. **`P(grounded)` in the gate: NO. Published bin × outcome counts: YES.** A
   measurement artifact anyone can re-derive by integer counting; the verdict
   stays binary.
3. **The design split: RATIFIED.** HQ designs the matched-pair shapes, Sai
   ratifies the labels, this repo runs candidates and reports.
4. **J-93: DROP the content-digest identity test, KEEP path + `samefile`.**
   Path identity is a FACT; content identity is an INFERENCE, and three
   different things share one content signature.

## §2 THE DIFF RULE — recompute every cycle

A row is IN THE DIFF unless **BUILT** (gated green, committed by explicit path,
pushed) or **OWNED BY A NAMED HUMAN** with the blocking reason stated.

Order: **code → register → scoreboard.** Register rows have been stale or wrong
**five times in two days** (J-37 closed-but-open; J-33's mechanism false; J-80's
census twice; J-81's census twice; J-87's mechanism, corrected by HQ).
**Re-derive any row's mechanism from code before acting on it.**

## §3 GATES — the commit is downstream of the tests

```
cd Agent-Assure && uv run pytest -q > /tmp/suite.txt 2>&1; echo $?
```
Baseline at §0: **848 passed · 2 skipped · 68 xfailed · exit 0.**

Before any commit touching `ground_check.py`:
- **GOLD** `md5 -q Agent-Assure/calibration/labels-v2.csv` =
  `6215b526d03147295b003d7ccb0d171f`. A change is a HALT.
- **RATES** Error-A `10/25 = 0.400`, Error-B `0/27 = 0.000`. **J-93 should LOWER
  Error-A or leave it; if it RAISES it, the ruling has been misread — stop.**
  **Error-B moving at all is wrong.**
- **THREE INSTRUMENTS.** Gold corpus = LABEL. `tests/honest_drafts/` = USAGE.
  An adversary = HOSTILITY. **Tonight the usage instrument is the one that
  matters**: it caught the J-93 Error-A that the corpus could not see.
- **A POSITIVE CONTROL ON EVERY CENSUS AND EVERY GUARD.** Six instruments
  under-reported in two days. **A guard must be run against a gate known to be
  broken before it is trusted** — the cross-kind guard stayed GREEN against the
  bug it was written for.

## §4 EACH TICK

1. Duplicate check — `git worktree list`; one orchestrator per branch.
2. Re-derive state per §2. Recompute the diff from scratch.
3. Append to `docs/logbook/overnight-2026-10-03C-progress.md`: UTC · diff · what
   changed · new tokens (output + cache creation) · frameworks.
4. Next row by §5. Gates FIRST-HAND, commit by explicit path, push. Subagent
   reports are TESTIMONY; the diff and a fresh run are EVIDENCE.
5. **CIRCUIT BREAKER** — two cycles, unchanged diff, no in-flight growth ⇒ HALT,
   name the class, disarm. Same for two failures of one terminal class.
6. **DISARM in the same turn** at diff zero · breaker · hard stop · ceiling.
   **§6 runs BEFORE the disarm.**

## §5 PRIORITY

1. **J-93** — his ruling, and it REVERSES part of tonight's work. Drop the
   content digest, keep path + `samefile`, un-xfail the two honest tests, and
   re-measure. Smallest, highest-confidence, and it removes a live Error-A.
2. **J-84 + J-85** — the two CRITICALs deferred this afternoon. `check_absence`
   must separate queries that may COUNT from queries that may form the
   blanket-corpus-word DENOMINATOR. **This is the function that produced D-54,
   a self-inflicted Error-B withdrawn the same day it landed, and BOTH
   directions are fail-open.** Extend the cross-kind guard FIRST, then change
   the signature, then round 19 against it. If the guard cannot be made to go
   red against the current hole, do not proceed — that is the §3 rule.
3. **The matched-pair RUNNER** (ruling 3). Scores a candidate feature on HQ's
   ten shapes, reports pairwise accuracy with an exact binomial interval, and
   **self-checks on shape 5**: direction reversal is an identical multiset, so a
   bag-of-words feature MUST score ~0.5 — anything else means the harness is
   wrong, not the feature. **Authors no labels**; it consumes shapes and emits
   separation. Sai's ratification is a separate, later act.
4. **Bin × outcome counts** (ruling 2's constructive half) — a measurement
   artifact, integer-countable, no probability in the verdict.
5. CR-011, the close, §6.

## §6 DISK HYGIENE — BEFORE THE DISARM (standing directive)

Measured at §0, not assumed: **repo 18M, no file >1MB — nothing to move to drive
or cloud.** If this run creates a large artifact it moves off local.
- Every scratch harness, fixture and backup this run creates is deleted.
- `grep -c "PRICING PATCH" Agent-Assure/scripts/ground_check.py` must be 0.
- `caffeinate` released; **READ `pgrep` output, never echo a fallback** — that
  mistake was made today.
- **Other projects' scratch is NOT mine.** Re-measure rather than quoting a
  remembered breakdown: at 14:16 the top consumer was `ival_2.0` at 1.3G; by
  17:15 iVal had acted (228K) and `iSuite` held 1.3G instead. **The finding
  moves between sessions; the list goes stale within hours.**

## §7 PARK LIST — pre-ruled; honouring it obeys his decision

Merging to `main` · publishing (D-83 approved, Escalation #5 reserves the act) ·
**J-69, J-70** (Escalation #1) · **J-35's capture-side fix** (Escalation #4) ·
**any gold-label change, including the matched-pair labels** (Escalation #2) ·
q25 · `~/.claude` or the global plugin registry · T3/NLI · J-55/CI ·
anything outward-facing · **any change that could move a claim TOWARD pass** ·
**anything toward the PASS-enabling relaxation, which he has now REFUSED.**

## §8 COMPETENCE BOUNDARY — named before the night

**I assert states I have not measured, and I trust instruments I have not tested
against a known failure.** Today: a commit message claiming a green suite that
was red; a trim claimed under 80 lines at 92 and again at 85; "no caffeinate"
while three ran; "created where none existed" with no prior check; a census
wrong twice, then another wrong twice more; a guard that stayed GREEN against
the bug it was written for; and a mechanism I published that HQ had to correct.
**Every claim tonight gets its measurement in the same command that makes it,
and every guard gets run against a broken gate before it is trusted.**

---

## §9 ARMING RECORD — written at the arm, not claimed before it

**2026-10-03 22:11 local — job `bb24422b`, `13,43 * * * *`, recurring,
session-only. Verified by `CronList` AFTER the create, not asserted before it.**

The first attempt to arm this run **did not happen**. At 21:44 I told Sai
"arming now" and never called `CronCreate`; `CronList` at the close returned
*No scheduled jobs*, which is how it was caught — by a measurement, not by
memory. That is §8's failure mode exactly: **a state asserted without being
measured.** The remedy is the same one that worked all day — the claim and its
measurement in the same breath, which is why the create above is followed by a
list and why this paragraph was written after reading that list.

Hard stop 06:00 local, carried in the tick prompt itself rather than here, so a
tick that never re-reads this file still stops. §6 runs before the disarm.
