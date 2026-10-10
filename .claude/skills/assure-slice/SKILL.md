---
name: assure-slice
description: >
  Execute one Phase-2 Agent-Assure slice end to end — read the sequencing
  recommendation, draft a TDD plan in the writing-plans format used for Phase
  1a/1b, then run subagent-driven development with per-task Sonnet review and a
  whole-branch Opus gate. Use when starting or resuming a Phase-2 slice
  (2c-harness, 2b NLI, 2a research front-end, 2d cross-platform). Honors the
  gold-label human gate on 2c and the moat invariants. Commands run from
  Agent-Assure/.
license: MIT
allowed-tools: Bash Read Write Edit
---

# assure-slice

Phase 1 (capture hook + deterministic gate) is done and live-validated. Phase 2
is four slices whose order is already decided. This skill turns a chosen slice
into a written TDD plan and drives it through subagent execution with tiered
review — so the moat invariants and the standing human gates are enforced by
process, not memory.

## Slice order (from PHASE2-SEQUENCING.md — do not reorder without Sai)

Recommended build order: **2c-harness → 2b → 2a → 2d.** "Perfect the
differentiated core, then build the commodity delivery around it."

| Slice | Adds | Human gate? |
|---|---|---|
| **2c** Calibration | metric computation, threshold sweep, moat-integrity operating-point selection | **YES — gold labels.** Harness is buildable now; the calibration RUN waits on Sai-ratified labels. |
| **2b** T3 NLI tier | local DeBERTa-MNLI entailment for paraphrase grounding; fail-closed | no — but it changes the gate, so it precedes the FINAL calibration pass |
| **2a** Research front-end | PLAN → PERSPECTIVES → GATHER → SYNTHESIZE feeding the gate | no |
| **2d** Cross-platform | Codex / Cursor / OpenCode / Gemini manifests | no |

The 2c-harness is the recommended first concrete slice: highest-leverage,
lowest-regret. Note the 2c-harness is buildable, but the calibration RUN is
gated on gold labels — see `assure-calibrate`.

## Non-negotiable invariants every slice inherits

- **No LLM in the grounding path.** 2b's NLI tier is fail-closed and Phase-2b
  local (DeBERTa); it may reduce Error-A but must NEVER create a PASS (Error-B).
- **Moat asymmetry.** No change reduces Error-A by raising Error-B. Positive
  class stays pinned to VIOLATION.
- **Closed verdict taxonomy.** A new state requires an ADR first.
- **NFKC before any new text match; fail loud on any new error path.**
- **New verdict paths declare their `tier_sensitive` / lex_tau-invariant tag.**

## Procedure

1. **Pick the slice** (default 2c-harness) and read
   `docs/PHASE2-SEQUENCING.md` in full. It names the design spec that already
   specifies every Phase-2 slice; if that spec file is present in the repo, read
   it too. (As of this branch it is referenced but not vendored here — do not
   block on it; PHASE2-SEQUENCING.md carries the decided scope and order.) The
   design is already decided; you sequence and implement, not re-design.
2. **Confirm the human gate.** If the slice is 2c and reaching a *calibrated
   threshold*, confirm Sai-ratified gold labels exist. If not, scope this slice
   to the HARNESS only and STOP before the calibration run (Escalation rule 2).
3. **Draft the TDD plan** in the writing-plans format used for Phase 1a/1b
   (see the `PHASE1B-RESUMPTION.md` structure: numbered tasks, each with its
   red-first test, the exact fixture/assertion, and a done-criterion). Write it
   to `docs/plans/` and get it reviewed before code. Do not write the plan for a
   slice you have not committed to — a plan for an unpicked slice is at-risk work.
4. **Execute via subagent-driven development.** One task per subagent against the
   locked plan. Every task is TDD: the regression test is run against pre-change
   code and SEEN RED (INS-005) before the fix is claimed.
5. **Tiered review (model-routing rule):**
   - **Per-task review → Sonnet-class.** Well-specified mechanical diffs; a miss
     is recoverable under the whole-branch backstop.
   - **Whole-branch / cross-artefact gate → Opus-class.** This gate never
     downgrades — a miss here ships. Moat-integrity and any safety-critical math
     get Opus.
   - Multi-file TDD execution against the locked spec → Opus-class.
   - Escalate a task refuted twice one tier up; do not iterate at the failing tier.
6. **Close out.** Run `uv run pytest` (all green; paste the count). If the slice
   changed classify/tiers/score, its calibration outputs are stale → run
   `assure-calibrate` and emit a CR. Write the logbook entry; mark Case vs
   Systemic.

## Verification gates (per slice)

1. TDD honored: every new test was seen RED against pre-change code.
2. `uv run pytest` fully green; count pasted (327 baseline on this branch — a
   passing slice only adds tests).
3. No new verdict without an ADR; no LLM introduced into the grounding path.
4. NFKC + fail-loud present on every new text/error path.
5. Per-task Sonnet review done; whole-branch Opus gate passed before merge.
6. If thresholds/features moved: CR emitted via `assure-calibrate`.
7. Human gates honored (gold labels for 2c; nothing published externally without
   Sai — Escalation rules 2, 5).

## Red flags → required response

| You observe / are tempted to | Required response |
|---|---|
| Building 2a (front-end) before the gate is calibrated | That pours spend through an uncalibrated gate. Follow 2c→2b→2a→2d unless Sai reorders. |
| 2b NLI tier would let a paraphrase CREATE a PASS | Forbidden. NLI is fail-closed; it may only reduce Error-A, never manufacture Error-B. |
| Writing the TDD plan for a slice not yet chosen | Stop. Plan the slice actually picked; a speculative plan is at-risk. |
| Downgrading the whole-branch review to save time | The Opus whole-branch gate never downgrades — a miss there ships. |
| 2c calibration run on Claude-generated labels | Those are `candidate`. STOP; ask Sai to ratify (rule 2). |

## References

- `Agent-Assure/docs/PHASE2-SEQUENCING.md` — slice order and rationale.
- `Agent-Assure/docs/PHASE1B-RESUMPTION.md` — the plan/TDD format to mirror.
- `.claude/skills/assure-calibrate/SKILL.md` — the calibration cycle a threshold-touching slice must run.
- CLAUDE.md → Conventions, Failure Modes, Escalation; global model-routing table.
