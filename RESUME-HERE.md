# RESUME HERE — Agent-Assure Calibration Workspace

**Last session:** 2026-07-08 (Fable-5 handoff + all-lanes parallel execution).
**Authoritative handoff:** `docs/logbook/2026-07-08-parallel-execution.md` — read it first; this file is the quick-start pointer, not the record.
**Branch:** `agent-assure-calibration-run` (pushed; this directory is a git **worktree** of agents-infra). **Tree:** clean at close. **Suite:** 334 passed (`cd Agent-Assure && uv run pytest`).

## Orientation (5 minutes)

1. Read `CLAUDE.md` (root) — rewritten 2026-07-08 as the operating manual; its Failure Modes and Escalation sections are binding.
2. Read the latest logbook entry (above).
3. `ls inbox/pending/` — one P1 item is waiting on **Sai**, not on you.
4. Verify before trusting: `git status` + `uv run pytest` (expect 334). If either disagrees with this file, the artifacts win — investigate before building.

## State snapshot

| Thing | State |
|---|---|
| Phase 1 (gate + capture hook + plugin) | COMPLETE, merged |
| Demo | **READY** — `Agent-Assure/demo/DEMO-SCRIPT.md`, golden-tested, offline |
| 2c calibration harness | Built; bootstrap CR-001: lex_tau=0.71, held-out Error-B=0.143 (n=12, provisional) |
| α1 ratification package | DELIVERED — `calibration/labeling-v2.csv` (n=52, all `candidate`), brief at `calibration/RATIFICATION-BRIEF-v2.md` |
| α2 calibration v2 (CR-002) | **BLOCKED on Sai** ratifying labels (inbox P1) |
| 2b NLI tier (α3) | Not started; next build slice after CR-002 |
| Skills | `.claude/skills/`: assure-calibrate, assure-red-team, assure-slice (committed, force-added past `.claude/` ignore) |
| Plans | `docs/plans/`: HANDOFF-MASTER-PLAN, ALPHA-READINESS-PLAN (α0–α5), DEMO-READINESS-PLAN, LANE-A spec, LANE-B portfolio audit |

## Decisions awaiting Sai (do NOT decide these yourself)

1. Ratify/correct `labeling-v2.csv`, flip `label_status` → `gold` (inbox P1; 30–45 min with the brief).
2. Does the 2026-07-03 live capture run close the Phase-1b live-validation gate? Do not infer.
3. Error-B monotonicity floor: keep 0.143 (n=12) or re-anchor at first ≥n=50 ratified run.
4. Lane B commercial half: supply `Temp-DDmmm-Consulting.md` (template in `docs/plans/LANE-B-PORTFOLIO-AUDIT.md`, final section).

## Next actions when unblocked

- Labels ratified → invoke skill **`assure-calibrate`** → CR-002 → update stale "provisional" citations repo-wide.
- Then Phase α3 (2b NLI tier) via skill **`assure-slice`** → CR-003 re-calibration after NLI lands.
- Then α4 second-repo install validation, α5 Opus whole-branch sign-off (see ALPHA-READINESS-PLAN).

## Already done — do NOT redo

Demo golden tests + script; CLAUDE.md rewrite; the 3 skills; corpus v2 + candidate labels; gold-only loader gate; portfolio audit. All committed in `26a035a`; verification evidence in `docs/plans/reports/`.

## Open systemic item

Citation regex rejects letter-suffixed source IDs (`[S12a]`) silently — case-resolved with numeric-only IDs; systemic fix (widen regex or fail loud on near-miss brackets) tracked in the 2026-07-08 logbook + insights log. Use `S\d+` IDs in any new fixtures until fixed.
