# ADR-005: PASS Requires an Empty Retained Appendix (Gate Score-Bar Semantics)

**Status:** Accepted (Sai, 2026-07-12 — "Accept as proposed").
**Date:** 2026-07-12
**Author:** Claude (autonomous, on delegated authority). Decision is Sai's.
**Context:** The 2026-07-12 red-team sweep proved the gate certifies drafts
containing a known-unsupported claim as PASS whenever that claim is diluted below
the score bar (AA-MOAT-002, AA-MOAT-006 in `docs/open-issues/OPEN-ISSUES.md`).
**Reserves:** ADR-004 is reserved for the local-classifier moat-boundary decision
(Phase-2b NLI tier), drafted Proposed in worktree `wf_f5845e10-a39-17`.

## Decision (proposed)

For any non-vacuous draft, `gate = PASS` **requires that `retained_appendix` be
empty** — i.e. the draft carries **zero** retained violation-class verdicts
(`UNGROUNDED`, `UNCITED`, `UNVERIFIED_CITATION`, `UNVERIFIED_NUMBER`,
`UNVERIFIED_ABSENCE`, `UNVERIFIED_RELATION`, `UNGROUNDABLE`). The `>= 90`
grounding-score threshold is retained as a *secondary* bar but is **no longer
sufficient** for PASS. This generalizes the existing `UNVERIFIED_CITATION`
hard-override (which already caps the gate regardless of score) to the entire
violation class.

Equivalently: **PASS means "every scored factual/numeric claim is grounded,"**
not "at least 90% are."

## Why (the defect this closes)

The score gate is a ratio. A ratio dilutes: 9 grounded claims + 1 fabricated
claim = 90.0%, which clears `>= 90`, so the fabrication rides through inside a
PASS — an **Error-B** event, the unrecoverable class. The gate already *detects*
the bad claim (it lands in `retained_appendix`); it simply does not let that
detection block the verdict. The product's headline promise — "a fabrication
cannot talk its way to PASS" — is false for any fabrication an author is willing
to surround with enough real claims.

This is corroborated, not hypothetical: reproduced by hand at
`score=90.0, retained_appendix=[1], gate=PASS, exit 0`.

## The asymmetric-invariant check (why this is the *permitted* direction)

Under the pinned invariant, Error-B (fabrication → PASS) is unrecoverable;
Error-A (real claim → false alarm) is recoverable. This change **strictly
reduces Error-B** (no diluted fabrication can PASS) at the cost of **raising
Error-A** (a genuinely forgotten citation now flips PASS → NEEDS_WORK instead of
being outvoted 9-to-1). That is the sanctioned trade: "No change may reduce
Error-A by raising Error-B" — the converse, reducing Error-B while accepting
recoverable Error-A, is exactly what the invariant asks for.

## Alternatives Considered

### A. Keep the ratio; raise the threshold (e.g. `>= 99`)
**Rejected.** Still a ratio — dilution just needs a longer draft (1 bad claim in
100 = 99%). Moves the goalpost; does not close the class. A threshold cannot
express "zero fabrications" because it is a proportion, not a predicate.

### B. Per-case patch each red-team draft
**Rejected.** Treats the symptom (these six drafts) not the cause (the ratio).
The attack generalizes to every claim class; case patches leave the vector open.

### C. Hard-cap only on `UNVERIFIED_CITATION` and `UNVERIFIED_NUMBER`
**Rejected as insufficient.** Leaves `UNGROUNDED` (paraphrase-overreach),
`UNVERIFIED_ABSENCE`, `UNVERIFIED_RELATION`, and `UNGROUNDABLE` divertible by
dilution. The clean invariant is "no retained violation of *any* class."

### D. Empty-appendix hard-cap (this ADR)
**Proposed.** One rule, closes Root A entirely, mirrors the existing citation
override, expressible as a predicate not a proportion. Does **not** by itself
close Root B (per-claim over-grounding — AA-MOAT-001/-003/-004/-005), where the
bad claim is marked GROUNDED and never reaches the appendix. Those need
tier-level fixes tracked separately; this ADR scopes Root A only and says so.

## Consequences

**Good:**
- Closes the threshold-dilution vector for all violation classes at once.
- Makes the headline promise literally true for retained (detected) violations.
- Simpler mental model: PASS = zero unsupported claims.

**Bad / to manage:**
- **Error-A rises.** A single forgotten or misplaced citation now blocks PASS.
  This is recoverable (NEEDS_WORK, author fixes) but changes day-to-day feel —
  the score bar was doing real ergonomic work.
- **Calibration goes stale.** `score`/gate semantics change → `calibration/`
  outputs (lex_tau, the score gate itself) must be re-derived → **new ADR-025
  CR** required after the change, on gold labels.
- **`grounding_score` semantics shift** from "pass/fail input" to "informational
  severity signal." Docs and the demo's honesty beat (CR-001 = 90) need updating.

## Blocking questions for Sai

1. Adopt the empty-appendix hard-cap as the PASS rule? (yes/no/modified)
2. Retain `>= 90` as a secondary/informational bar, or drop it entirely?
3. Does any legitimate use case *want* a "mostly grounded" PASS (a soft-gate
   mode)? If so this becomes a policy flag, not a hard rule — but a flag that
   re-opens Error-B must default OFF and be logged.

**How to apply (once accepted):** add the proven-red regressions
(`tests/red_team_moat/` AA-MOAT-002/-006 already staged as strict xfail — they
flip to green guards), implement the appendix hard-cap in `score_report`, re-run
the full suite + the red-team harness (every diluted-fabrication draft must gate
!= PASS), re-run calibration, emit the CR. Then open follow-up ADRs for the Root
B tier fixes.

## Amendments

**2026-07-12 — Accepted and implemented.** Sai ruled "Accept as proposed":
hard-cap adopted, ≥90 retained as a secondary/informational bar (blocking
question 2), no soft-gate flag (question 3). Implemented same day in
`score_report` (`scripts/ground_check.py`); AA-MOAT-002/-006 xfails flipped
XPASS and were converted to permanent green guards
(`tests/red_team_moat/test_moat_red_team.py::test_fixed_fabrication_stays_blocked`).
Calibration impact: corpus v2 feature rows and candidate labels are
byte-identical post-change (verified by regeneration diff) — the lex_tau
inputs are unaffected; `gate` remains `deferred` pending the gold-label run
(CR-002), which will calibrate the secondary score bar under the new
semantics.
