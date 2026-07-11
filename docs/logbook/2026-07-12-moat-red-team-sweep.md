# Logbook — 2026-07-12 — Moat red-team sweep: six confirmed Error-B violations

**Branch:** `agent-assure-calibration-run` · **Suite:** 334 passed + 6 xfailed
(new proven-red harness) · **Workflow:** `wf_f5845e10-a39` (26 agents, 1.68M
subagent tokens, 343 tool calls, 0 errors, ~37 min)

## What

A token-window "full steam" session that could NOT touch the Alpha critical path
(α2 blocked on gold-label ratification — labels still 52/52 `candidate`, verified)
spent the budget on the highest-value unblocked work: a 12-class adversarial
red-team sweep against the grounding moat, plus ratification-day prep and two
reference builds. The sweep found **6 confirmed moat violations** (Error-B —
fabrication certified PASS, the unrecoverable class). **All six were reproduced by
hand** on this branch before being recorded.

## Why it matters

The product's headline property is "a fabricated citation cannot talk its way to
PASS." That *narrow* property holds (fabricated-citation class clean, 4/4). The
*broad* property everyone had drifted into believing — "no fabrication can PASS" —
is false six ways. This reshapes Alpha: α5 sign-off cannot proceed until these
close.

## Done (verified, committed)

- **6 Error-B findings, hand-reproduced** (`gate=PASS, exit 0` on unsupported
  drafts): numeric-drift-unit, numeric-drift-decimal(dilution), paraphrase-
  overreach, unsubstantiated-absence, unsupported-relation, letter-suffixed(dilution).
- **`tests/red_team_moat/`** — 6 drafts + frozen store + strict-xfail harness.
  Proven red (6 xfailed); suite stays green (334 passed). XPASS→fail tripwire on
  any future fix.
- **`docs/open-issues/OPEN-ISSUES.md`** — AA-MOAT-001..006 with reproduced
  verdicts, mechanisms, roots, systemic fix sketches; + OI-BUILD-01, OI-CITE-01.
- **`docs/adr/ADR-005`** (Proposed) — PASS requires empty `retained_appendix`
  (closes Root A / dilution). Blocked on Sai (gate-bar change).
- **`docs/case-narratives/CN-ADR005-The-Ninety-Percent-Moat.md`** — detailed CN.
- **INS [2026-07-12]** — "a gate's own suite cannot measure its moat."
- **Ratification-day prep** (workflow recon): `docs/alpha/PHASE1B-VALIDATION-
  EVIDENCE.md`, `docs/plans/reports/THRESHOLD-STALENESS-MAP.md`,
  `docs/plans/PHASE2B-NLI-TDD-PLAN.md`, `docs/alpha/READINESS-SWEEP.md`.

## How / key decisions

- **Two roots, not one (correction of the sweep's synthesis).** Root A: score-bar
  dilution (`>=90` ratio admits a retained violation ≤10% of the draft). Root B:
  per-claim over-grounding (T1 verbatim short-circuit; relational endpoint-noun
  check; numeric unit-blindness; absence head-noun anchoring) — scores 100 with
  empty appendix, so no score-bar fix touches it. The synthesis said "one thread";
  two drafts scoring a clean 100 located the second root (contradiction-as-locator).
- **Recorded, not patched.** All six alter the Error-A/Error-B trade-off or the
  gate bar → Escalation rule #1 → Sai. This session hardened the regression net
  and drafted the decision (ADR-005); it did not move the dial.
- **Builds are reference-only.** The two worktree builds (citation-regex `9d14ff1`,
  NLI-tier `d859e09`) were cut from `agents-infra` **main** (`fef21e4`, 326-test
  base), NOT this branch — diffs don't transfer; rebase + re-verify before any
  merge (OI-BUILD-01). Neither merged.
- **Discontinuity distrust applied.** The 6-violation headline was treated as
  testimony and reproduced from artifacts (gate exit codes) before entering any
  doc or decision.

## Agents (telemetry)

| Phase | Agents | Model | Notes |
|---|---|---|---|
| Recon+RedTeam | 3 + 12 | Sonnet (+1 Opus recon) | 3 prep docs; 12-class sweep, 49 drafts |
| Build | 2 | Opus | worktree-isolated, red-first; on wrong base (see OI-BUILD-01) |
| Verify | 8 | Opus | per-build audit + per-blocker reproduction; all red_first_credible |
| Synthesize | 1 | Opus | READINESS-SWEEP.md dossier |

Workflow total: 26 agents, 1.68M tokens, 343 tool calls, 0 errors. Main-loop
hand-reproduction of all 6 findings + governance authoring done in-session.

**Reflection:** The instructive moment was not the six holes — it was the
synthesis agent's tidy "one root" story colliding with two drafts that scored a
clean 100. A single-root theory cannot explain a fabrication that was marked
GROUNDED (nothing to dilute). Averaging the contradiction would have shipped a
fix that closed a third of the surface and called it done. The contradiction was
the map to the second defect. The other keeper: 334 tests passed through the
entire discovery and never twitched — a gate's suite measures its authors
agreeing with themselves, and the moat's real edge is only ever drawn by an
adversary. That is why the adversary is now *in* the suite.

## Next

1. **Sai decisions (all Escalation #1):** ADR-005 (empty-appendix hard-cap? keep
   `>=90` as secondary?); the four Root-B tier fixes; the Error-B floor anchor.
2. **Gold-label ratification (inbox P1)** still gates α2/CR-002 — unchanged.
3. On any fix: proven-red first (the xfail harness flips to green guard) → re-run
   red-team → re-run calibration → new ADR-025 CR (classify/tiers/score all move).
4. Phase-1b gate decision — evidence dossier now in `docs/alpha/`.
