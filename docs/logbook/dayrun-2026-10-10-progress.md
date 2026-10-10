# DAYRUN 2026-10-10 — progress (checkpointed each cycle)

Instrument: `docs/planning/DAYRUN-2026-10-10.md`. Skeleton written at §0 so that
a death at 95% still delivers the record. **Nothing below is armed yet — §0.5
says WAIT for AGREED.**

## Cycle 0 — handshake, state derived from code

- **UTC** 2026-10-10 (pre-arm)
- **Diff** not yet computed under §1; the nine-item reply carries the proposal.
- **What changed** instrument file + this skeleton. No code touched.
- **New tokens (output + cache creation)** ~0.1M so far this handshake.
- **Frameworks** *Theory of Constraints* — the bottleneck is reachability and the
  capture layer, not the gate; *Calibration* — the suite, both md5s and the
  branch tip were re-run rather than inherited from a summary, on a machine whose
  home directory had changed underneath the old paths.
- **Verified from code, not register:** 851/2/68 exit 0 · gold md5 matches ·
  corpus md5 matches · 0 open PRs · `main` still `009c646`.
- **Two handshake findings** recorded in the instrument §0: the bootstrap
  calibration runner has a **write side effect** (`CR-001`), and the deployed
  `0.400 / 0.000` pair is **NOT_LOCATED_UNDER** three kinds of search as a
  single re-derivable command.

## Cycle 1 — ARMED

- **UTC** 2026-10-10 08:11 (13:41 IST)
- **Cron job id** `5888aa27` — `11,41 14-21 * * *`, recurring, session-only.
  **Verified by `CronList` AFTER the create**, because on 2026-10-03 an "arming
  now" was announced for a call that had never been made, and only the close
  caught it. First tick **14:11 IST**, last **21:41**, hard stop **22:00**.
- **Ratification** D-93 in `docs/decisions/RATIFICATION-REGISTER-2026-08-30.md`,
  with its UNDO: `CronDelete 5888aa27`, then delete branch
  `testing-live-2026-10-10` local and remote. Every commit of the run lands on
  that branch alone, so the undo needs no history rewrite.
- **Budget** 3M new tokens sanctioned, **ceiling 5M** (Sai raised it from 3.6M
  at 13:40 IST). At 4M — 80% — the run stops STARTING work and spends the
  remainder finishing and reporting.
- **Diff under §1** 6 committed rows open (R1…R6), 0 built, 0 in flight.
- **Frameworks** *Reversibility* — the entire run is scoped to one deletable
  branch, which puts every one-way door (the merge, the publish, the capture
  contract) outside it by construction rather than by my restraint.

## Cycle 2 — R1 BUILT (ahead of the first tick; a tick is a heartbeat, not a start gun)

- **UTC** 2026-10-10 08:2x · **Diff** 5 open (R2…R6), **1 BUILT**, 0 in flight
- **What changed** `calibration/measure_rates.py` + `tests/test_measure_rates.py`,
  commit `5189477`, pushed. **It reproduces the quoted pair exactly:**
  `n=52 (25 grounded, 27 violation) · tp=27 fp=10 tn=15 fn=0 · Error-A 10/25 =
  0.400 · Error-B 0/27 = 0.000`, recomputed from the live gate.
- **Suite** 851 → **854 passed**, 2 skipped, 68 xfailed, exit 0. Gold md5
  unchanged and not in the diff.
- **PROVEN-RED, both directions.** The read-only guard's positive control passes
  when pointed at `run_calibration` (a known writer) and FAILS with
  `changed == set()` when pointed at `measure_rates` — so the detector is not
  blind, and `measure_rates` writes nothing, by two independent routes.
- **A number I checked instead of accepting:** the control's subprocess reported
  0.03s, which looked impossible for a Python spawn. Timed it directly — 0.025s,
  rc 0, 626 bytes of output. The suspicion was right to have and the number was
  real; a plausible-looking duration is not evidence either way.
- **New tokens** ~0.35M cumulative (output + cache creation), 3M sanctioned /
  5M ceiling.
- **Frameworks** *Calibration* — the rate quoted in seven CRs, CLAUDE.md and the
  launch claim had no located re-derivation, so confidence was running ahead of
  checkability; *FMEA detectability* — a docstring promising read-only is the
  R15-01 class, so the promise got a detector and the detector got a positive
  control; *Name the CEILING* — the lex_tau 0.0-vs-1.0 equality probe raises if a
  threshold re-enters the verdict path, instead of silently reporting one tau.

## Cycle 3 — tick 1 · R2 BUILT

- **UTC** 2026-10-10 08:4x · **Diff** 4 open (R3…R6), **2 BUILT**, 0 in flight
- **R2 / J-50** commit `90e129d`, pushed. All three first-run refusals now read
  `REFUSED: <the original message>` at exit 1, with no traceback.
- **Suite** 854 → **861 passed**, 2 skipped, 68 xfailed, exit 0. Gold md5
  unchanged. **Rates re-derived AFTER the change** with R1's new command and
  unmoved at 0.400 / 0.000 — a legibility change must not touch a verdict, and
  that is now checked rather than assumed. R1 paid for itself inside one cycle.
- **PROVEN-RED 5/7** against HEAD's pre-fix script via `ASSURE_GROUND_CHECK`.
  The two passing both sides are the two that must: the AST guard on the verdict
  path (a property the pre-fix code already had — a guard, not a fix) and the
  control asserting the demo verdicts did not move.
- **Naming the sibling found two more defects.** The draft's `open()` was
  unguarded on the same path. And `load_store`'s convention is "raise with the
  offending line", honoured by `_validate_record` and the duplicate check and
  **not by the parse itself** — a corrupt line in a 300-line store reported
  json's "line 1 column 1", which counts within the fragment. Now "line 2 of
  the evidence store". **That message was always wrong; it only became
  misleading once a user could read it.**
- **A bug of mine, caught by running it rather than reading it:** the first
  version of the refusal helper used `_sys`, which is a function-LOCAL import
  inside `main`, so every refusal died with `NameError` instead of printing.
  Three of three manual cases showed it immediately. Fixed with a local import
  rather than hoisting one to module scope — *Chesterton's Fence*: that local
  import is deliberate and I do not know why.
- **New tokens** ~0.75M cumulative, 3M sanctioned / 5M ceiling.
- **Frameworks** *Jobs to be Done* — the job is "tell me whether I can trust
  this draft", and a crash answers a different question; *FMEA detectability* —
  named the sibling and it yielded two further defects, one of which my own fix
  had just made visible; *Via negativa* — the guard catches two named exception
  types at three named sites and ENDS before the verdict path, rather than one
  broad try that would dress a defect as a refusal.

## Cycle 4 — tick 2 · R3 BUILT · clone REMOVED

- **UTC** 2026-10-10 09:1x · **Diff** 3 open (R4, R5, R6), **3 BUILT**, 0 in flight
- **R3 / ALPHA-5** commit `cacc9f0`. `install.sh` exit 0 on a clean `--depth 1`
  clone with no `.venv` and no `.assure`; fabricated `[S3]` refused **FAIL 50.0
  exit 1**; grounded 100.0; J-73 scope line on every verdict; this morning's
  J-50 refusals arrive as sentences in the stranger build too.
  **Reachability is established WITHOUT touching `main`** — a fact R4 needs and
  did not have.
- **A-5-01 found, and it is SAI'S.** `install.sh`'s own session-id snippet
  crashes in a fresh install: the `SID=$(...)` subshell opens a store that
  **cannot exist** before the hook has fired. J-50's sibling one layer out, and
  today's CLI fix cannot reach it — the subshell dies first. Registered with the
  two-line change and with **why the obvious repair is a trap** (defaulting to
  `""` turns a missing file into an unattributable id and reproduces today's
  refusal for a second, unrelated reason). **Not fixed: Escalation #4, park list.**
- **§6 DISK, done now rather than at the disarm:** `alpha5-clone` (**16 MB**
  incl. its venv) and `userrepo` — **REMOVED**. Scratchpad holds only
  `prefix_ground_check.py` (0.2 MB), the proven-red reference for R2; removed at
  the disarm. Nothing was written into the repo from the clone.
  **Pre-existing and NOT mine, untouched:** `graphify-out/` (5.9 MB) and one
  unread HQ inbox item — both for Sai.
- **New tokens** ~1.1M cumulative, 3M sanctioned / 5M ceiling.
- **Frameworks** *Reachability* — "done" is where the next reader will look, and
  a rehearsal in my own tree measures my own tree, so the instrument had to be a
  clone; *Delivery-is-not-consumption* — the installer's last printed line is
  the product's first consumed line, and it was broken; *Via negativa* — the
  report states what it did NOT establish so it cannot be mistaken for coverage.

## Cycle 5 — tick 2 · R4 BUILT · two PRs open, neither merged

- **UTC** 2026-10-10 09:3x · **Diff** 2 open (R5, R6), **4 BUILT**, 0 in flight
- **R4** commit `583d98b`, dossier at
  `docs/decisions/MERGE-TO-MAIN-DOSSIER-2026-10-10.md`.
- **PR #10** → `main` (the big decision). **PR #11** → `agent-assure-calibration-run`
  (today's 11 commits, small and reviewable). **Neither merged. `gh pr merge` was
  not attempted.**
- **THE FINDING, and it inverts the decision.** `main` is not the safe side. It
  already ships Agent-Assure, at the **Phase-1 engine: 1,388 lines, before all
  nineteen red-team rounds** (branch: 4,657). Demonstrated rather than argued —
  one draft citing only itself, one store, two engines:
  **`main` → PASS 100.0 GROUNDED exit 0; branch → FAIL 0.0 UNGROUNDABLE exit 1.**
  `main` certifies a self-citing fabrication, and it is what a stranger installs
  by default. `main`'s README also still documents T2 lexical-F1 grounding,
  which ADR-006 demoted as insufficient.
- **Facts the decision needs, all re-derived today:** 279 commits, 275 files,
  +50,511/−422, **zero deletions**. The gold labels are **`A` (added)**, not
  `M` — `main` has never held them — so **this merge contains no gold-label
  change** and Escalation #2 is not engaged by it. That single `--name-status`
  check removed the scariest-sounding part of the merge.
- **Recommendation made, and what would flip it named:** merge, on the
  asymmetry — a wrong merge costs one `git revert -m 1` (clean *because* nothing
  is deleted); the fabrication `main` certifies today is not reversible. It
  flips if nobody actually installs from `main`, which is a fact about
  distribution that I do not have.
- **New tokens** ~1.5M cumulative, 3M sanctioned / 5M ceiling.
- **Frameworks** *Inversion* — asking what happens if we DON'T merge turned the
  risk around and was the whole finding; *Asymmetry of error cost* — the
  recommendation rests on reversibility, not on the work's merits;
  *Contradiction-as-locator* — "main is the safe side" vs "main is nineteen
  rounds old" could not both be true, and the disputed line was one command away.

## Cycle 6 — R5 reported · COMPACTION, not a close · cron still armed

- **UTC** 2026-10-10 ~10:0x · **Diff** 1.5 open (R5 verification, R6), **4 BUILT**
- **R20: 3 CRITICAL, 2 HIGH, 1 MEDIUM, 3 speculative.** None overlaps
  J-35/J-36/J-38. Report committed.
- **R20-01 REPRODUCED BY ME** with my own fixture, not the adversary's: a claim
  present in **neither** fetched document certifies **PASS 100.0**, and also
  **PASS 100.0 under `--session-id`** with the "retrieved this session" line
  printed over it. `_coerce_text_value` joins MCP blocks with `"\n"` and
  `_tokenize` is `re.findall(r"\w+")`, so the seam is invisible to T1.
- **R20-02 and R20-03 are NOT yet reproduced by me** and are recorded as
  testimony, not fact, in both the logbook and the handoff. The next session
  reproduces them first.
- **The adversary logged its own protocol deviation unprompted** (one read-only
  `git status` against instruction). Recorded rather than dropped.
- **Nothing disarmed, §6 not run.** Clone and `userrepo` already REMOVED;
  four scratch paths remain and are named in the handoff.
- **New tokens** ~1.9M cumulative incl. the subagent's 151K, 3M / 5M ceiling.
- **Frameworks** *Competence boundary* — I named "auditing the layer where the
  measurement lives rather than where the work lives" as my failure mode at
  13:40 and aimed the day's adversary at exactly that layer; *FMEA
  detectability* — the capture layer is the least detectable place in the
  system because the lie becomes evidence before any check runs; *Calibration* —
  the subagent's three CRITICALs are testimony until reproduced, and one of
  three now is.
