# Fable-5 Handoff Master Plan — Agent-Assure Calibration Workspace

**Author:** Claude Fable 5, 2026-07-07, written under a hard 15-minute access deadline.
**Executor from here:** Opus 4.8 (judgment-bearing tasks) / Sonnet 5 (mechanical tasks). Routing per task below.
**Authority:** Sai's directive this session: "Extend, sharpen my ask, reason and do the needful."

---

## 0. The sharpened ask (what Sai actually requested, restated)

Three lanes, plus a feasibility question:

- **Lane A** — Rewrite this repo's CLAUDE.md as the operating manual a *less capable model* needs to work here at Fable level: conventions (existing + missing), named weak-model failure modes with the rule preventing each, checkable quality bars per deliverable, exact escalation rules. Then the 3 highest-hours-saved skills, written in full.
- **Lane B** — Consultant audit: projects, offers, workflows, pricing, time allocation → ranked roadmap executable by a weaker model, incl. 3 stop-doing items with full reasoning.
- **Lane C** — Alpha readiness plan + Demo readiness plan for Agent-Assure, authored by Fable, executed by Opus/Sonnet.

**Feasibility verdict on "this being a brand-new repo":**

- **Lane A: ~90% executable here.** This repo is NOT thin. It carries: a complete Phase 1 gate (200+ tests), a bootstrapped calibration run (CR-001), 3 AARs, PIR-001 (17 bugs shipped untested — a named failure history), an insights log, ADRs, and a SOUL.md. That is exactly the raw material an operating manual distills. The only gap vs a mature repo: fewer *repeated* mistakes observed, so the weak-model failure list leans on Fable inference from the architecture (flagged as such in the Lane A spec).
- **Lane B: ~40% executable from repos alone.** Workflows and where-time-goes ARE recoverable (git activity + logbooks across `~/vibe-coding`, the HQ logbook, the 12 active projects list). **Offers, pricing, and revenue are in no repo** — those need a user-supplied input (even a 20-line note). Without it, Lane B degrades honestly into a **portfolio audit** (kill / finish / ship ranking across 12 projects from commit-activity and governance evidence), which is still high-value. Do NOT let a weaker model fabricate pricing analysis from nothing.
- **Lane C: 100% executable.** Written in full — see `ALPHA-READINESS-PLAN.md` and `DEMO-READINESS-PLAN.md`.

---

## 1. Current repo state (evidence, verified this session)

- Repo: Agent-Assure calibration workspace, branch `agent-assure-calibration-run`, clean tree.
- Phase 1 (gate + capture hook + plugin packaging): COMPLETE, merged (PR #2, #4).
- Phase 2a calibration bootstrap: DONE — `lex_tau=0.71` (projected 0.65, +9.2%), CR-001 emitted, held-out (leave-one-out) Error-A=0.20, **Error-B=0.143**, n=12 claims. CR-001 self-declares: "calibration, not proof."
- Phase 2 sequencing recommendation exists (`Agent-Assure/docs/PHASE2-SEQUENCING.md`): 2c-harness → 2b NLI → 2a front-end → 2d cross-platform. Harness is now built; **the calibration RUN awaits gold-label ratification by Sai** (Claude-labels-Claude is circular — standing gate).
- Offline demo exists: `Agent-Assure/demo/` — fabricated `[S3]` citation → FAIL (the moat moment).

## 2. Two standing human gates (nothing below overrides these)

1. **Live-validation gate:** capture hook validated by Sai in a real session (partially satisfied 2026-07-03 per README; confirm before Alpha sign-off).
2. **Gold-label gate:** calibration thresholds are provisional until Sai ratifies/corrects labels. n=12 must widen to n≥50 before any threshold is called "validated."

## 3. Lane routing and model assignment

| Lane | Artifact | Executor | Effort |
|---|---|---|---|
| A | Rewrite `CLAUDE.md` per `LANE-A-CLAUDE-MD-REWRITE-SPEC.md` | Opus 4.8 | high |
| A | Write the 3 skills (specs in Lane A doc §5) | Sonnet 5, Opus review | medium |
| B | Portfolio audit (repo-derivable half) | Sonnet 5 sweep agents + Opus synthesis | medium |
| B | Offers/pricing half | **BLOCKED on Sai input** — ask for a `Temp-DDmmm-Consulting.md` note | — |
| C | Execute `ALPHA-READINESS-PLAN.md` | Opus 4.8 (slices), Sonnet 5 (mechanical) | per plan |
| C | Execute `DEMO-READINESS-PLAN.md` | Sonnet 5 | low-medium |

## 4. Execution order for the next session (Opus)

1. Demo readiness first (smallest, de-risks any near-term showing; ~1 hour).
2. Lane A CLAUDE.md rewrite (unblocks every later weaker-model session; ~1 session).
3. Alpha plan Phase α1 (label ratification package for Sai — the human gate long-pole).
4. Lane B portfolio-audit half; request pricing/offers input from Sai in parallel.
5. The 3 skills.

## 5. Verification discipline (binding on all executors)

- Every "done" claim needs command output as evidence (`uv run pytest` from `Agent-Assure/`, demo run transcript).
- Regression tests proven red before claimed (INS-005).
- Any threshold or gate change → new CR per ADR-025, ≤80 lines.
- Post-discontinuity (this handoff IS one): re-verify artifacts from evidence before trusting this document's numbers — re-read CR-001 and rerun the test suite before building on them.
