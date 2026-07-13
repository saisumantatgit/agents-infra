# RESUME HERE — Agent-Assure Calibration Workspace

**Last session:** 2026-07-14 (autonomous night: red-team round 2 — the 07-12 fixes were evaded 14 ways; 3 closed, 1 escalated; OI-CITE-01 + OI-CAL-02 closed; α4 READY).
**Authoritative handoff:** `docs/logbook/2026-07-14-red-team-round-2.md` — read it first; this file is the quick-start pointer, not the record.
**Branch:** `agent-assure-calibration-run` (pushed; this directory is a git **worktree** of agents-infra). **Tree:** clean at close. **Suite:** 379 passed + 3 xfailed — the 3 xfails are OPEN moat items, deliberately red.

## Orientation (5 minutes)

1. `cd Agent-Assure && uv sync --extra dev && uv run pytest` → expect **379 passed + 3 xfailed**. **`uv sync --extra dev` is not optional** — without it pytest silently resolves to a GLOBAL pytest and shows ~46 bogus failures (OI-ENV-01).
2. Read `CLAUDE.md` (root) — the operating manual. Gate semantics: ADR-005 (PASS = empty retained appendix). `lex_tau` **runs at 0.65**, not CR-001's 0.71 (OI-CAL-01 — your call).
3. Read the latest logbook (above) and `Agent-Assure/docs/open-issues/OPEN-ISSUES.md`.
4. `ls inbox/pending/` — one P1 item still waits on **you**, not on the next session.

## Six decisions waiting for you (nothing below is blocked on anything else)

| # | Decision | Where | One-line context |
|---|---|---|---|
| 1 | **Ratify gold labels** (30–45 min) | inbox P1 + `calibration/RATIFICATION-BRIEF-v2.md` | Unblocks α2/CR-002 → α3 → α5. Package UNCHANGED by all recent work. **Do OI-CAL-02's sibling check first: never run `build_corpus_v2` after ratifying without `--features-only`** (now guarded, but know why). |
| 2 | **AA-MOAT-007** | OPEN-ISSUES | A verbless fabrication ("Redis: unquestionably the fastest datastore in history.") classifies NON_CLAIM → escapes scoring → rides inside a PASS. Score verbless assertions as claims (raises Error-A on headers), or leave it? |
| 3 | **OI-CAL-01** | OPEN-ISSUES | Deploy CR-001's lex_tau=0.71 now, or hold at the shipped 0.65 until CR-002 supersedes it? |
| 4 | **ADR-004 / Phase-2b (NLI)** | `docs/plans/ADR-004-DECISION-PACKAGE.md` | Under ADR-005, a T3 upgrade removes a claim from the appendix and so CAN create a PASS — contradicting "T3 never creates a PASS". 4 options with Error-A/B analysis; recommendation = Option 4. |
| 5 | **AA-MOAT-003 / -005** | OPEN-ISSUES | Still deferred by your 07-12 ruling (T1 overreach → fold into 2b?; relational predicate → own decision). |
| 6 | **OI-ENV-01** | OPEN-ISSUES | Make `install.sh` provision dev deps, or fail loud when pytest resolves outside `.venv`? |

## State snapshot

| Thing | State |
|---|---|
| Phase 1 (gate + capture + plugin) | COMPLETE |
| Demo | **READY** — `Agent-Assure/demo/DEMO-SCRIPT.md`, golden-tested, offline |
| α4 second-repo install | **READY (with caveats)** — `Agent-Assure/docs/alpha/ALPHA4-INSTALL-VALIDATION-2026-07-14.md`; fresh install → real store → genuine draft PASS → fabrication NEEDS_WORK |
| Moat | Round 1 (07-12): 6 holes, 4 fixed. Round 2 (07-14): 14 wrongful PASSes evading those fixes — 3 mechanisms fixed, AA-MOAT-007 open. **Guards permanent** in `tests/red_team_moat/` |
| Calibration | CR-001 (lex_tau 0.71 recommended, n=12) **re-run post-fix, reproduces byte-identically**. Corpus drift after tier changes: 2 rows, both improvements. Labels: 12 + 52, all intact, now **guarded against clobbering** (OI-CAL-02) |
| α2 / CR-002 | **BLOCKED on your ratification** (decision #1) |
| α5 sign-off | Blocked until AA-MOAT-003/-005/-007 close or are explicitly accepted as residual risk |

## Already done — do NOT redo

Demo + golden tests; CLAUDE.md operating manual; 3 skills; corpus v2 + candidate labels; gold-only loader gate; portfolio audit (`26a035a`). Round-1 red-team + 6 findings (`51b3d02`). ADR-005 + numeric-unit + absence fixes (`6624e85`). Round-2 fixes, OI-CITE-01, OI-CAL-02 guard, α4, ADR-004 package, doc conformance (this session). Verification evidence in `docs/plans/reports/`.

## Standing discipline (learned the hard way, twice)

- **Regenerate the calibration corpus and diff it after ANY classify/tiers/score change** — use `uv run python -m calibration.build_corpus_v2 --features-only`. It caught an Error-B leak (q22, round 1) and an Error-A regression (q37, round 2) before either could be committed.
- **Never tune a constant to make one corpus row pass.** Change the rule's meaning. (See the q37 story in the logbook / CN-ADR005.)
- **Re-run the red-team sweep after every remediation** — round 2 found 14 holes in round 1's fixes.
