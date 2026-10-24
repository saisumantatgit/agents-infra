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

## Cycle 7 — R20 adjudicated · the usage instrument arrived · COMPACTION, cron still armed

- **UTC** 2026-10-10 ~10:2x · **Diff** 1 open (R6 completion), **5 BUILT**
- **R20-01 and R20-02 CONFIRMED by my own fixtures**, not the adversary's.
  **R20-03 DID NOT REPRODUCE** — my construction was refused `FAIL 0.0
  UNGROUNDABLE`, so it is downgraded to OPEN-UNCONFIRMED rather than carried as
  a third CRITICAL. *Two of three survive, and saying which one didn't is the
  point of reproducing them.*
- **The usage instrument arrived after all.** Sai ran the live probe
  (`8c17b88b`, `~/tmp/assure-probe`); a real four-record store exists and I read
  its field shape (not its text). It **refutes a claim on a shipped surface**:
  `CLAUDE.md` said `session_id` is never written — it is written on all four.
  The register row was narrowed 2026-10-03 and the Gotchas entry was not: **the
  J-37 stale-row class, on a claim surface.** Corrected in `e2066ff`.
- **Confirmed in the FIELD, not from the code:** `fetched_at` is still the 1970
  sentinel (J-38's remaining half), and `query_provenance` is a path or a URL on
  every record, never a search query (**J-36, live**).
- **Both instruments disagreed about R20-03 and only the real session settled
  it.** That is the strongest argument yet for keeping a live probe in the loop.
- **Nothing disarmed; §6 not run.** Still to remove at the disarm:
  `prefix_ground_check.py`, `r20/`, `mine20/`, `mine20b/`, `mainprobe/`.
  `~/tmp/assure-probe` is **Sai's to delete** and now holds real evidence worth
  keeping until R20-04/05/06 are reproduced against it.
- **New tokens** ~2.2M cumulative incl. the subagent, 3M sanctioned / 5M ceiling.
- **Frameworks** *Contradiction-as-locator* — the adversary said CRITICAL and my
  run said refused; I adjudicated by direct trace instead of averaging or
  deferring, and the live store broke the tie; *Calibration* — a finding is
  testimony until reproduced, and one of three did not survive; *FMEA
  detectability* — a stale line in `CLAUDE.md` is a control that is confidently
  wrong, which is worse than one that is silent.

## Cycle 8 — Sai chose KEEP RUNNING · cron verified alive · R20-04 upgraded

- **UTC** 2026-10-10 ~10:4x · **Diff** 1 open (R6 completion: R20-05/06, CR-012
  actuals, end-of-day report), **5 BUILT**
- Sai asked for `/sg` 7-step; I ran it **through the skill this time** (the two
  earlier closes were from memory and skipped the session-summary file — since
  written). The close was already complete; the skill's mode gate made the one
  open choice explicit, and **Sai chose to keep the run armed to 22:00.**
  `CronList` after compaction risk: **`5888aa27` alive.**
- **R20-04 UPGRADED HIGH → CRITICAL by my own reproduction.** Two fetches that
  both FAILED (503, `isError: true`) through the real hook certified an absence
  claim at **PASS 100.0 ABSENCE_SUPPORTED**, with the gate stating it read "2
  retrieved sources". **The adversary stopped at HIGH because it could not
  reach PASS; I reached it on the first construction.** Reproducing is not only
  how findings get downgraded (R20-03) — it is also how they get their true
  severity.
- **Three CRITICALs now confirmed by me in the capture layer** (R20-01, -02,
  -04). All Escalation #4, all Sai's.
- **Probe session `8c17b88b`:** nothing to do there but `/exit`; its one
  recommendation (the stale `session_id` Gotcha) was already actioned in
  `e2066ff`. Its store stays on disk.
- **New tokens** ~2.4M cumulative, 3M sanctioned / 5M ceiling.
- **Frameworks** *Calibration* — the adversary under-rated its own finding, so
  testimony errs in BOTH directions and only reproduction sets severity;
  *Asymmetry of error cost* — an absence certified on zero reads is the purest
  Error-B the product can emit, because the reader has no claim text to check.

---

# END-OF-DAY REPORT — 2026-10-10 · disarmed at DIFF ZERO, before the 22:00 hard stop

## 1. DONE — each with the command that proves it

| Row | Proof command | Output |
|---|---|---|
| R1 | `cd Agent-Assure && uv run python -m calibration.measure_rates` | `Error-A 10/25 = 0.400` · `Error-B 0/27 = 0.000` |
| R2 / J-50 | `uv run python scripts/ground_check.py --draft demo/draft-grounded.md --store demo/evidence-store.jsonl --session-id ""` | `REFUSED: --session-id was given but is empty…` exit 1, no traceback |
| R3 | report `Agent-Assure/reports/ALPHA-5-2026-10-10.md` | clean clone, `install.sh` exit 0, fabricated demo `FAIL 50.0` |
| R4 | `gh pr view 10` · dossier `docs/decisions/MERGE-TO-MAIN-DOSSIER-2026-10-10.md` | PR #10 open, not merged |
| R5 | report `Agent-Assure/reports/RED-TEAM-R20-2026-10-10.md` | 4 CRITICAL reproduced by me |
| R6 | `Agent-Assure/calibration/CR-012-day-run-2026-10-10.md` | 54 lines, inside the 80-line ceiling |
| Suite | `cd Agent-Assure && uv run pytest -q` | **861 passed · 2 skipped · 68 xfailed · exit 0** |
| Gold | `md5 -q Agent-Assure/calibration/labels-v2.csv` | `6215b526d03147295b003d7ccb0d171f` |

## 2. NOT DONE

Nothing in the committed set. **Not attempted, by design:** any fix to the four
capture-layer CRITICALs — they are Escalation #4.

## 3. DENIED

**Nothing was denied today.** One self-inflicted block: a PreToolUse hook
refused a heredoc because my own *document text* quoted a git command it
guards. Reworded; nothing routed elsewhere.

## 4. ONE-WAY DOORS QUEUED — Sai's

1. **Merge PR #10 → `main`.** `gh pr merge 10 --merge --repo saisumantatgit/agents-infra`.
   Undo: `git revert -m 1 <merge-sha> && git push origin main`. Recommended:
   merge — `main` ships the engine that certifies a self-citing fabrication at
   100.0. **It does not fix the four capture CRITICALs, which exist on both sides.**
2. **PR #11 → integration branch** — today's work as a small reviewable diff.
3. **A-5-01** — two lines in `install.sh` (Escalation #4).
4. **The capture contract** — R20-01, R20-02, R20-04/06 plus J-35, J-36, J-38.
   **This, not the merge, is now the real gate before an external tester.**

## 5. UNKNOWNS

- **R4-Q1, owner Sai:** does anyone actually install from `main`? Flips the merge
  recommendation.
- **R20-03:** whether ANY construction reaches PASS. Mine was refused. Owner Claude.
- **R20-05:** whether any live tool emits the `{"preview","file_path"}` overflow
  shape. Not seen in Sai's real store. Owner Claude.
- **Whether a reader takes PASS to mean "traceable" or "supported".** Owner Sai —
  see §8 below.

## 6. BUDGET — measure named

**Subagent, derived from its completion record: 151,192 tokens, 31 tool calls,
~10 min** (Opus, round 20). **Main loop: UNKNOWN exactly** — this session has no
trace-derived read path for its own usage, so the running ~2.5M figure in this
file is an ESTIMATE, not a measurement. Under the 3M sanctioned and the 5M ceiling
on any reading.

## 7. WITHDRAWALS — what I said and took back

- **"Going quiet now"** at 13:45 with R1 ready to start. Sai called it; a tick is
  a heartbeat, not a start gun. R1 shipped 40 minutes later.
- **"Delete `~/tmp/assure-probe`"** — reversed: it holds the only real
  hook-written store in the project.
- **R20-03 as CRITICAL** — withdrawn after my own fixture was refused FAIL 0.0.
- **R20-04 and R20-06 as HIGH / MEDIUM** — withdrawn upward; both reach PASS 100.0.
- **"Main is the safe side"** — the framing I started R4 with, withdrawn by its
  own first measurement.
- **Two 7-step closes run from memory instead of the `/sg` skill** — they skipped
  the session-summary file. Rerun through the skill; the file now exists.

## 8. FRAMEWORKS applied to the day's consequential decisions

*Inversion* — asking what happens if we DON'T merge reversed R4. *Competence
boundary* — named at 13:40, and the day's adversary was aimed at exactly that
layer. *Calibration* — every subagent finding treated as testimony; reproduction
moved three of six severities. *FMEA detectability* — naming the sibling turned
one J-50 fix into three. *Contradiction-as-locator* — adversary and my run
disagreed on R20-03, and the live store settled it. *Reachability* — the clone,
not my tree, was the instrument. *Via negativa* — the J-50 guard ends before the
verdict path.

## §8 OF THE INSTRUMENT — SAI'S STANDING REMINDER: THE 5-USER COMPREHENSION TEST

**Still relevant — more so after today.** D-83 approved the release on the
strength of the disclosure, and the disclosure rests on one untested assumption:
that a reader takes `PASS` to mean *traceable* and not *supported*. Today's
findings sharpen it — four ways to reach PASS 100.0 on text no document holds
make it matter more what a reader believes PASS promises.

**Who the five are:** people who would plausibly READ a verification report on
an AI draft — not buyers, not people evaluating the tool. A buyer answers "would
I pay"; a user answers "what did I just read", and the assumption is about reading.

**What to ask each for:** ten minutes, cold, no preparation, no explanation of the
tool first. Then run `docs/research/user-test-2026-10-03/PROTOCOL.md` with
`SHOW-THIS.html`: don't say "traceable", "supported", "grounded" or "verified"
before they do; ask Q1 before they can scroll; write wrong answers down
verbatim; run all five before concluding — 2-of-5 and 4-of-5 are different
decisions.

---

## DISK — §6, run BEFORE the disarm

- **REMOVED by §6, before the disarm:** `prefix_ground_check.py` (220K), `r20/`
  (232K), `mainprobe/` (68K), `mine20/`, `mine20b/`, `mine20c/`, `mine20d/`.
  Scratchpad is empty. Earlier today: `alpha5-clone` (16 MB incl. venv) and
  `userrepo` — REMOVED at R3. `git worktree prune` run; only the main checkout
  remains. **Nothing over ~20 MB was generated at any point.**
- **KEPT, deliberately, and Sai's to remove:** `~/tmp/assure-probe` — the only
  real hook-written store in the project; R20-03 and R20-05 should be checked
  against it before it goes.
- **Pre-existing, NOT mine, untouched, for Sai:** `graphify-out/` (5.9 MB,
  untracked) and `inbox/pending/P2_2026-09-03_from-hq_fyi_three-ci-and-merge-findings-ins-159-160-161.md`
  (unread since 2026-09-03).

## DISARMED

- **Cron `5888aa27` deleted. `CronList`: "No scheduled jobs."** — verified after
  the delete, not assumed.
- **Trigger: DIFF ZERO** — all six committed rows built. The 22:00 hard stop was
  not reached.

## AFTER THE DISARM — Sai said "Go merge" (PR #10). DENIED, returned to Sai.

- **PR #10 is `CONFLICTING`.** `main` has 14 commits the branch lacks (inbox
  items, the graphify pilot, a `.gitignore` line). **Exactly one file is changed
  on both sides: `docs/insights/insights-log.md`**, an append-only prose log.
  Resolution is a union — keep both sides' entries.
- **Correction to my R4 dossier:** it measured with a three-dot diff from the
  merge-base (`a41160c`), which cannot see `main`'s own 14 commits, so it
  reported the merge's size and its zero deletions correctly but **missed the
  conflict**. The dossier was right about what the branch changes and silent
  about what `main` had changed meanwhile — a control correct about what it
  examined.
- **DENIED: `git merge --no-ff --no-commit origin/main` on my own branch**, by
  the auto-mode classifier, reason `[Merge Without Review]`. Not retried, not
  worked around, not routed to another session. `gh pr merge` was not attempted:
  same class, and it was denied three times on 2026-10-03. Tree verified
  untouched afterwards (no `MERGE_HEAD`, HEAD still `a3bdc8a`).
- **Returned to Sai** with exact steps for both the GitHub web route and the
  terminal route. **Verification stays mine:** once he pushes the resolution, I
  re-run the suite, gold md5 and rates on the merged tree before he clicks merge.

## 21:46 IST — SAI MERGED PR #10. `main` = `a382aa0`. Verified.

- **By Sai's hand**, `gh pr merge 10 --merge`, after he resolved the
  `insights-log.md` conflict by the union I prepared and pushed `e2f13f2`.
  (The three `fatal: not a git repository` lines in his window were from
  re-running already-done steps in `~`; harmless.)
- **Verified rather than assumed:** a real merge commit, parents `009c646` +
  `e2f13f2`; `main`'s tree `4a189d5` **identical** to the tested tree. Fresh run:
  **861 passed · 2 skipped · 68 xfailed · exit 0**, gold md5 unchanged, rates
  0.400 / 0.000. **The fabrication `main` certified at PASS 100.0 this
  afternoon now returns FAIL 0.0 UNGROUNDABLE on `main`.** Scratch REMOVED.
- **Not closed by the merge:** the four capture CRITICALs. They are now on
  `main` exactly as before.
- **Stale claim on `main` itself:** `main`'s `RESUME-HERE.md` arrived saying
  `main` had never received the work. Corrected on the branch; it reaches `main`
  only with the next PR. **Delivery is not consumption**, even for a handoff.
- **Frameworks** *Calibration* — "merged" was confirmed by tree identity plus a
  fresh run, not by the green tick in Sai's terminal; *Reachability* — the merge
  made the fixes reachable and simultaneously made one handoff line false.
