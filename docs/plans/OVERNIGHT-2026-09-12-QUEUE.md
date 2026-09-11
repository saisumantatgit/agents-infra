# Overnight queue — 2026-09-12 (budget 10M, planned ~3.5M)

Cron-advanced. This file is the DURABLE queue; the cron job itself is in-memory
and dies with the session. A tick that finds this file finishes the first
unchecked item, updates the checkbox + note, commits, and stops.

**Standing order applies.** Park list holds: applying bindings, the gross_wages
adjudication, anything outward-facing. Autonomous calls go in the ratification
register (D-21…) with their undo.

## Not doing tonight, deliberately

- **T3 / NLI (J-02, 3.6–6.1M).** It buys down Error-A 0.320 — a number whose
  labels are not established reproducible (kappa 0.09 between readers). Spending
  the night improving an unmeasurable metric is the Goodhart move.
- **Any new Error-A measurement on this corpus.** Base rate 0/2. RESUME-HERE
  already says a third attempt fails the same way.
- **J-15, J-05, D-01, D-07** — Sai's rulings. Brief prepared, ruling untouched.

## Queue

- [x] **1. Intra-rater instrument** — **DONE.** Page:
      https://claude.ai/code/artifact/170c9801-14fa-4231-9468-1fa2371f5319
      `Agent-Assure/calibration/intra-rater/` holds the items, the withheld key
      and `score.py`. The first plain-random draw of 20 contained NONE of the 4
      rows where Sai overruled the machine (p=0.133), so it could not have
      detected the anchoring branch: sample is now STRATIFIED (D-21), strata are
      never pooled (D-22), and a fourth INDETERMINATE branch was added (D-23).
      All four branches dry-run verified end to end.

**PUSH DENIED** by the permission classifier on this tick (same boundary as the
2026-08-30 session). Commits are local on `agent-assure-calibration-run`.
Not routed to another session — that would launder the denial. Sai must push or
grant the permission.
- [ ] **2. Red-team round 7 — STPA-targeted.** Hazard: a fabrication certified
      PASS. Three NEW PASS-enabling control paths have never been attacked:
      (a) decomposition rewrites the claim text (D-17..D-20),
      (b) citation propagation attaches a citation the author never wrote (OI-DEC-01),
      (c) exact containment grounds a claim whose hedge was stripped upstream.
      Attack those three by name, not by imagination. ~1.5M incl. fixes
- [ ] **3. Corpus regenerate + byte-diff** after any round-7 fix; adjudicate every
      drifted row against its label; CR-005 only if a rate actually moves. ~0.4M
- [ ] **4. Round-7 re-attack on the fixed tree.** Alpha #7 requires a clean round
      AFTER the last moat change; a round that found and fixed does not satisfy
      it. ~0.5M
- [ ] **5. J-15 decision brief** — the counts that make Sai's ruling one word. ~0.2M
- [ ] **6. Close** — register D-21+, logbook, RESUME-HERE, push. ~0.3M

## Stop conditions

- Round 7 finds an Error-B that is NOT fail-closed to repair -> stop, escalate,
  move to the next item. A blocker on one item is not a blocker on all.
- Any change that would be PASS-enabling -> tripwire it, do not fix it.
- 8M consumed -> skip to item 6 and close cleanly.
