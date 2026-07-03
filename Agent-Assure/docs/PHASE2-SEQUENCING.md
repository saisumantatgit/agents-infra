# Agent-Assure Phase 2 — Sequencing Recommendation

**Status: RECOMMENDATION — awaiting your go. No Phase 2 implementation has started (held per the standing gate).**
Author: Claude (autonomous, on Sai's delegated authority, 2026-07-03). Ratify, amend, or reorder before any build.

## Context

Phase 1 is complete and on branch `agent-assure-phase1b` (pushed, **not merged** — awaiting your
live-validation of the capture hook). What exists: the deterministic grounding **gate**
(`ground_check.py`, 134 tests), the `PostToolUse` **capture hook** (Tasks 1–5, +73 tests), Claude
Code **plugin packaging**, and an offline **demo** proving the moat (fabricated `[S3]` → FAIL).

The design spec (`docs/superpowers/specs/2026-06-20-agent-assure-design.md`) already specifies all of
Phase 2 — it does not need re-designing. What it does **not** decide is the **order** to build the
Phase 2 slices. That is this document.

## The four Phase 2 slices

| Slice | What it adds | Size | Depends on | Human gate? |
|---|---|---|---|---|
| **2a Research front-end** | PLAN → PERSPECTIVES (STORM) → GATHER → SYNTHESIZE, feeding the gate | Large (~4–5M) | the gate (done) | no |
| **2b T3 NLI tier** | local DeBERTa-MNLI entailment for paraphrase grounding; fail-closed, optional | Medium (~1–2M) | the gate (done) | no |
| **2c Calibration** | validate the provisional thresholds (score ≥ 90, `lex_tau` 0.65) per `calibration-plan.md` | Medium (~1–2M) | a **labeled** eval corpus | **YES — gold labels** |
| **2d Cross-platform** | Codex / Cursor / OpenCode / Gemini manifests | Small (~0.5M) | validated gate | no |

## Recommendation — build order: **2c-harness → 2b → 2a → 2d**

**Perfect the differentiated core, then build the commodity delivery around it** — the same
gate-first logic the spec used for Phase 1, extended into Phase 2.

1. **2c first, but split it.** The gate's PASS/FAIL bar is admitted-provisional ("no empirical
   basis," spec §12.5). Its *sharpest* catch — `UNVERIFIED_CITATION` (fabricated source) — is
   threshold-independent and already sound; but the **score gate and the T2 lexical boundary are
   not defensible until calibrated.** Building the big research front-end (2a) first would pour
   ~5M into feeding *more* claims through an uncalibrated gate, amplifying any Error-A/B
   miscalibration. So: **build the calibration harness now** (metric computation, threshold sweep,
   the moat-integrity operating-point selection from `calibration-plan.md`) — this is buildable
   without you. **Then the actual calibration run waits on gold labels** (see load-bearing caveat).

2. **2b NLI next.** T1 (verbatim) + T2 (lexical-F1) structurally miss *paraphrased* grounding — a
   real claim restated in the source's own different words reads as UNGROUNDED (Error A). T3 closes
   that gap, reducing false flags, and it is fail-closed so it cannot *create* an Error-B (false
   PASS). Calibrating (2c) *before* NLI would calibrate a gate the NLI tier then changes — so NLI
   before the *final* calibration pass; harness before both.

3. **2a research front-end last of the big three.** It is the spec's own "commodity half"
   (§1.1) — valuable for the full "ask a question → grounded report" product, but the *differentiated*
   value is the gate, which 2c+2b harden. Worth its ~5M only once the gate it feeds is trustworthy.

4. **2d cross-platform** after the vertical is proven — breadth over an unvalidated core is waste.

### Why this inverts the offhand "front-end + NLI → calibration" order

Your one-line framing put the front-end first. On merit I recommend the opposite, because the
front-end builds the *delivery layer* on a gate whose operating point isn't yet validated. If you
still want the front-end first (e.g. to demo the full loop sooner), that's a legitimate
product call — but you'd be shipping a bigger surface on provisional thresholds. Flagging it so the
choice is yours, not silently made.

## The load-bearing caveat (same shape as the live-validation gate)

**Calibration cannot be completed by me alone.** `calibration-plan.md` is explicit that the positive
class must be labeled *first*, and Claude-labeling-Claude's-own-grounding is circular — it would
validate the gate against the same judgment the gate encodes. So:

- **Buildable tonight/next, no gate:** the calibration *harness* (corpus schema, per-claim metric,
  threshold sweep, Error-A/Error-B operating-point selector) + a **candidate** label set I generate,
  clearly marked unvalidated.
- **Needs you (or an external ground truth):** ratifying / correcting the gold labels before the
  thresholds are set on them. Until then, 0.90 stays a flagged provisional default (the spec's
  "ship-flagged → instrument → recalibrate from production" path keeps v1 unblocked).

## Recommended first concrete slice, if you approve

Build **2c-harness** (calibration infrastructure + candidate labels) as the next subagent-driven-
development slice — it is the highest-leverage, lowest-regret step (validates the moat everyone
relies on, unblocks the labeling you'd do, and doesn't commit the big 2a spend). A detailed TDD
plan (writing-plans format, like the Phase 1a/1b plans) is **intentionally not written yet** — it
should target the slice you actually pick, so writing it now would be at-risk. Say go on a slice and
it's the first thing I draft.

## Decision block (for you)

- [ ] Approve order **2c-harness → 2b → 2a → 2d**, OR
- [ ] Reorder (e.g. front-end first — noted trade-off above), OR
- [ ] Adjust scope of any slice.
- [ ] Confirm you'll provide/ratify calibration gold labels (or name an external ground truth).

Until you decide, Phase 2 stays unbuilt. Phase 1 remains held at the live-validation gate.
