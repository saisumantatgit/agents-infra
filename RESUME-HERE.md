# RESUME HERE — Agent-Assure Calibration Workspace

**Last session:** 2026-07-12 (moat red-team adjudication: ADR-005 accepted + 4 of 6 Error-B holes fixed).
**Authoritative handoff:** `docs/logbook/2026-07-12-moat-remediation.md` — read it first; this file is the quick-start pointer, not the record. (The red-team *discovery* record is `docs/logbook/2026-07-12-moat-red-team-sweep.md`.)
**Branch:** `agent-assure-calibration-run` (pushed; this directory is a git **worktree** of agents-infra). **Tree:** clean at close. **Suite:** 351 passed + 2 xfailed (`cd Agent-Assure && uv run pytest`) — the 2 xfails are OPEN moat items, deliberately red.

## Orientation (5 minutes)

1. Read `CLAUDE.md` (root) — the operating manual; Failure Modes and Escalation sections are binding. Gate semantics changed 2026-07-12 (ADR-005): PASS = empty retained appendix; score ≥90 is a secondary bar.
2. Read the latest logbook entry (above).
3. `ls inbox/pending/` — one P1 item is waiting on **Sai**, not on you.
4. Verify before trusting: `git status` + `uv run pytest` (expect 351 passed + 2 xfailed). If either disagrees with this file, the artifacts win — investigate before building.

## State snapshot

| Thing | State |
|---|---|
| Phase 1 (gate + capture hook + plugin) | COMPLETE, merged |
| Demo | **READY** — `Agent-Assure/demo/DEMO-SCRIPT.md`, golden-tested, offline |
| 2c calibration harness | Built; bootstrap CR-001: lex_tau=0.71, held-out Error-B=0.143 (n=12, provisional). Corpus-v2 verified byte-identical post-moat-fixes — CR-001 stands |
| Moat (red-team cohort) | 6 Error-B holes found 2026-07-12; **4 FIXED** (ADR-005 dilution ×2, numeric unit, absence anchoring) with permanent green guards; **2 OPEN by Sai's ruling** (AA-MOAT-003 T1 overreach, AA-MOAT-005 relational predicate) as strict xfails. See `Agent-Assure/docs/open-issues/OPEN-ISSUES.md` |
| α1 ratification package | DELIVERED — `calibration/labeling-v2.csv` (n=52, all `candidate`, UNCHANGED by the fixes), brief at `calibration/RATIFICATION-BRIEF-v2.md` |
| α2 calibration v2 (CR-002) | **BLOCKED on Sai** ratifying labels (inbox P1). CR-002 will also calibrate the ADR-005 secondary score bar |
| 2b NLI tier (α3) | Not started; AA-MOAT-003 (+ absence-stemming / quantity-noun residuals) should ride with its design |
| α5 sign-off | Blocked until AA-MOAT-003/-005 close (or Sai explicitly accepts them as documented residual risk) |
| Skills | `.claude/skills/`: assure-calibrate, assure-red-team, assure-slice |
| Plans | `docs/plans/`: HANDOFF-MASTER-PLAN, ALPHA-READINESS-PLAN (α0–α5), DEMO-READINESS-PLAN, LANE-A spec, LANE-B portfolio audit |

## Decisions awaiting Sai (do NOT decide these yourself)

1. Ratify/correct `labeling-v2.csv`, flip `label_status` → `gold` (inbox P1; 30–45 min with the brief; package unchanged by the moat fixes).
2. AA-MOAT-003 (T1 verbatim overreach) — fix now, or fold into Phase-2b NLI design? AA-MOAT-005 (relational predicate) — needs its own decision; softest fixture, probe `unsupported-relation_3` first.
3. Does the 2026-07-03 live capture run close the Phase-1b live-validation gate? Do not infer.
4. Error-B monotonicity floor: keep 0.143 (n=12) or re-anchor at first ≥n=50 ratified run.
5. Lane B commercial half: supply `Temp-DDmmm-Consulting.md` (template in `docs/plans/LANE-B-PORTFOLIO-AUDIT.md`, final section).

## Next actions when unblocked

- Labels ratified → invoke skill **`assure-calibrate`** → CR-002 (lex_tau + the ADR-005 secondary bar) → update stale "provisional" citations repo-wide.
- Then Phase α3 (2b NLI tier) via skill **`assure-slice`**, folding in the AA-MOAT-003 decision → CR-003 re-calibration after NLI lands.
- Then α4 second-repo install validation, α5 Opus whole-branch sign-off (needs the 2 open moat items closed or accepted).

## Already done — do NOT redo

Demo golden tests + script; CLAUDE.md rewrite; the 3 skills; corpus v2 + candidate labels; gold-only loader gate; portfolio audit (all `26a035a`). Red-team sweep + 6 findings recorded/hardened (`51b3d02`). ADR-005 implementation + numeric-unit + absence-anchoring fixes, guards, doc sync (this session — see latest logbook for commit).

## Open systemic items

- Citation regex rejects letter-suffixed source IDs (`[S12a]`) silently — the *dilution* half is closed by ADR-005 (AA-MOAT-006 guard); the *classification* half (regex widening, OI-CITE-01) still open; reference build exists on the wrong base (OI-BUILD-01: rebase before trusting). Use `S\d+` IDs in new fixtures until fixed.
- Absence anchors don't stem ("docs" ≠ "documentation"); numeric quantity-nouns not compared ("operations" vs "gigabytes") — recorded residuals in OPEN-ISSUES, ride with Phase-2b.
