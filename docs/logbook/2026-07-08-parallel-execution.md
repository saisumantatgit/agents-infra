# Logbook — 2026-07-08 — Fable handoff + all-lanes parallel execution

**Branch:** `agent-assure-calibration-run` · **Commits:** `e2ec446` (handoff plans), `26a035a` (execution batch) · **Suite:** 334 passed (was 327)

## What happened

Two-stage session across the Fable-5 access deadline (2026-07-07 → 08):

1. **Fable stage (15-min window):** wrote 4 handoff artifacts to `docs/plans/` — HANDOFF-MASTER-PLAN, LANE-A-CLAUDE-MD-REWRITE-SPEC (judgment content: 10 failure modes, 5 escalation triggers, 3 skill specs), ALPHA-READINESS-PLAN (α0–α5), DEMO-READINESS-PLAN (D1–D4).
2. **Execution stage ("GO all in parallel"):** α0 trust verification (clean tree, 327 green), then 4 agents dispatched concurrently (2 Opus, 2 Sonnet per routing table), all completed, all artifacts verified from evidence before commit.

## Delivered (verified, committed, pushed)

- **Demo READY:** golden transcripts (`demo/expected/`), 4 red-first golden tests, `demo/DEMO-SCRIPT.md` (6-beat, ~8 min), offline confirmed by static import check, reset command live-exercised post-commit.
- **CLAUDE.md** rewritten as the weaker-model operating manual (140 lines, 7 sections); every fact live-verified by the agent, not copied from spec.
- **3 skills** (`.claude/skills/`): assure-calibrate, assure-red-team, assure-slice. Force-added past the `.claude/` gitignore — deliberate: deliverables, not settings.
- **α1 ratification package:** corpus v2 n=52/52 queries, 48% violation class, `labeling-v2.csv` (all `label_status=candidate`), gold-only loader gate in `scripts/calibrate.py` (red-first proven: "2 failed DID NOT RAISE → green"), `RATIFICATION-BRIEF-v2.md` (30–45 min, 14 hardest rows), inbox ask `P1_2026-07-08_...ratify-gold-labels-v2.md`.
- **Lane B portfolio audit** (`docs/plans/LANE-B-PORTFOLIO-AUDIT.md`): evidence-only; pricing/offers fenced as NEEDS-SAI-INPUT.

## Open items (blocked on Sai)

1. **α2 calibration v2** — blocked until labels ratified (`label_status` → `gold`). Inbox item P1 pending.
2. **Phase-1b live-validation gate** — confirm whether 2026-07-03 live capture run closes it (α0 open question; do not infer).
3. **Error-B floor anchor** — manual pins monotonicity floor at 0.143 (n=12); decide whether to re-anchor at first ≥n=50 run (direction of invariant unconditional either way).
4. **Lane B commercial half** — needs `Temp-DDmmm-Consulting.md` note (template in audit §5).

## Findings worth keeping

- **Citation regex rejects letter-suffixed IDs** (`[S12a]` fails `S\d+`) — silently declassifies multi-source relational fixtures. Future fixtures: numeric-only source IDs. Candidate systemic fix: widen regex or fail loud on near-miss brackets (carry as open issue).
- `calibration-plan.md` and the design-spec path are cited in docstrings/docs but absent from this worktree — documented as Gotcha; live sources are CR-001 + `scripts/calibrate.py`.
- This workspace is a git worktree of agents-infra, not a standalone repo (Lane B evidence table).

**Reflection:** The Fable window forced an unusually clean separation of judgment from assembly — the spec files carried the decisions, and all four executor agents (two of them a tier down) produced verifiable, discipline-conformant work on the first pass. The measurable signal: both red-first tests were actually proven red, and both fail-loud catches (missing calibration-plan.md, gitignored skills) were surfaced rather than papered over. Evidence that the "judgment in the spec, execution anywhere" pattern holds at tier boundaries.

**Next action:** Sai ratifies labels (inbox P1) → run `assure-calibrate` for CR-002 → Phase α3 (NLI tier) via `assure-slice`.
