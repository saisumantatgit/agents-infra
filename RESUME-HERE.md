# RESUME HERE — Agent-Assure Calibration Workspace

**Last session:** 2026-08-30 (autonomous close-out run under Sai's 10M sanction + standing order).
**Authoritative handoff:** `docs/logbook/2026-08-30-autonomous-closeout.md`, then `docs/decisions/RATIFICATION-REGISTER-2026-08-30.md` (every autonomous call + its undo). This file is the quick-start pointer, not the record.
**Branch:** `agent-assure-calibration-run` (this directory is a git **worktree** of agents-infra).

## What changed on 2026-08-30 (read the register before reversing anything)

All three moat holes that had been OPEN since 2026-07-12/14 are **closed**, plus
two hygiene items and the threshold drift. Every call is logged in the
ratification register with a one-step undo, for you to ratify or reverse:

| Was | Now |
|---|---|
| OI-MOAT-03 (T1 span certifies unchecked words) | **FIXED** — residual-coverage check (D-04) |
| OI-MOAT-05 (relation grounded by endpoint co-presence) | **FIXED** — predicate-support check (D-05) |
| OI-MOAT-07 (verbless fabrication escapes the denominator) | **FIXED** — verbless exemption narrowed (D-03) |
| OI-CAL-01 (gate ran 0.65 while docs said 0.71) | **RESOLVED** — 0.71 deployed, `--lex-tau` added (D-06) |
| OI-ENV-01 (global-pytest onboarding trap) | **FIXED** — dev dependency-group + conftest guard (D-07) |
| OI-NUM-02 (trailing-space numeric token) | **FIXED** (D-12) |
| AA-MOAT-* IDs | **renamed** OI-MOAT-{NN} per HQ ADR-039 (D-08) |
| cpc-book ask (open since 07-19) | **answered** + batch ingestion built (D-09) |

## Orientation (5 minutes)

1. `cd Agent-Assure && uv sync && uv run pytest` → 442 passed + 1 skipped + 1 xfailed
   (the xfail is OI-MOAT-20, deliberately open; the skip is an empty parametrize).
   (`--extra dev` is no longer required — OI-ENV-01 fixed.)
2. Read `CLAUDE.md` (root) — the operating manual. Gate semantics: ADR-005
   (PASS = empty retained appendix). **`lex_tau` now RUNS at 0.71.**
3. `docs/decisions/RATIFICATION-REGISTER-2026-08-30.md` — the 12 autonomous calls.
4. `Agent-Assure/docs/plans/reports/RED-TEAM-R3-2026-08-30.md` — round-3 adversary
   run against the new fixes. **Read this before trusting the fixes.**
5. `ls inbox/pending/` — one P1 item still waits on **you**.

## Still waiting on you

| # | Decision | Where | One-line context |
|---|---|---|---|
| 1 | **Ratify gold labels** (30–45 min) | inbox P1 + `calibration/RATIFICATION-BRIEF-v2.md` | STILL THE LONG POLE. Unblocks α2/CR-002 → α3 → α5. **Edit `labels-v2.csv`.** Nothing this session touched your labels; all 52 remain `candidate`, exactly as you left them. |
| 2 | **Ratify or reverse the 12 autonomous calls** | `docs/decisions/RATIFICATION-REGISTER-2026-08-30.md` | Each row carries its undo. D-03/-04/-05 changed moat semantics (all fail-closed); D-06 moved the live operating point (measurement-neutral on both corpora). |
| 3 | **OI-DEC-01** | OPEN-ISSUES | Escalated deliberately: the fix is the first PASS-*enabling* change in the cohort, so it is Escalation-#1 yours. Propagate a sentence-final citation across a conjunction split, or document "cite each clause"? |
| 4 | **ADR-004 / Phase-2b (NLI)** | `docs/plans/ADR-004-DECISION-PACKAGE.md` | Q1–Q4 unchanged and still yours. **Less urgent now:** 2b was carrying the Error-B fix for OI-MOAT-03; that landed deterministically, so 2b's remaining value is Error-A recovery on paraphrase. |
| 5 | **OI-BUILD-01** | OPEN-ISSUES | The two reference worktrees are still on the wrong base; reference material only. |

## State snapshot

| Thing | State |
|---|---|
| Phase 1 (gate + capture + plugin) | COMPLETE |
| Demo | **READY** — re-verified 2026-08-30 post-fixes: honest draft still PASS (100.0), fabricated still FAIL (50.0) |
| α4 second-repo install | READY (with caveats) — `docs/alpha/ALPHA4-INSTALL-VALIDATION-2026-07-14.md` |
| Moat | Rounds 1–2 closed; **round 3 run 2026-08-30 against the new fixes** — see the R3 report for what it found and what was done about it |
| Calibration | CR-001 stands (n=12). Labels: 52 candidate, **untouched**. Batch ingestion for incremental multi-domain corpora is built and tested |
| α2 / CR-002 | **BLOCKED on your ratification** (unchanged) |
| α5 sign-off | Gated on your ratification of the register + gold labels, and on the R3 disposition |

## Already done — do NOT redo

Everything in the 2026-07-16 RESUME-HERE, plus this session: the four moat/threshold
fixes, the ADR-039 rename, OI-ENV-01, OI-NUM-02, batch ingestion + cpc-book ack,
red-team round 3. See the logbook for the full commit list.

## Standing discipline (learned the hard way, three times now)

- **Regenerate the corpus and diff it after ANY classify/tiers/score change** —
  `uv run python -m calibration.build_corpus_v2 --features-only`. It adjudicated
  every fix this session: it confirmed D-05 by flipping exactly the three
  human-labeled-violation rows, and it showed D-04's only drift was in the
  right direction.
- **Never tune a constant to make one corpus row pass.** Change the rule's meaning.
- **Re-run the red-team after every remediation** — round 2 found 14 holes in
  round 1's fixes; round 3 was run against this session's fixes for the same reason.
- **Green-on-first-run is not evidence.** Mutation-check a new guard: disable it
  and watch the test fail. Two tests written this session looked fine and were
  asserting nothing until that check caught them.
