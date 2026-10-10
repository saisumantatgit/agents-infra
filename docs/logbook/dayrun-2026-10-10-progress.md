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
