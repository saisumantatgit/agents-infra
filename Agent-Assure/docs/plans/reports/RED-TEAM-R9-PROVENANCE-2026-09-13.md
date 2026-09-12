# Red-team round 9 — PROVENANCE ONLY — 2026-09-13

**Status: IN PROGRESS** (started 00:28 IST, adversaries time-boxed to 01:05,
hard close 01:20). Created before the work so an interrupted round still
delivers what it found.

## Scope — the closed class, deliberately

Round 9 attacks **only** the provenance half: does every certified claim cite a
source that was actually retrieved this session, captured verbatim, and is
every uncited assertion actually scored? **Entailment findings are OUT OF
SCOPE** and are discarded — rounds 3–8 already show that class is open.

Why run it before the product call: if provenance ships, the product stakes its
name on this class. A closed class is one a red team can actually exhaust.

| adversary | surface |
|---|---|
| P1 | citation-id resolution: fabricated, lookalike, unicode, zero-width, bracket/case/suffix forms, placement, mixed real+fabricated |
| P2 | source-type and denominator integrity: summary-vs-verbatim spoofing, empty/snippet text, malformed or duplicate store records, claims that escape citation detection or the scored denominator |

## Results

PENDING.
