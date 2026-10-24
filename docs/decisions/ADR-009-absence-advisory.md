# ADR-009 — Absence claims are reported, never certified

**Status:** PROPOSED — built for Sai's ruling on J-97; NOT accepted until he merges.
**Date:** 2026-10-22 · **Mirrors:** ADR-007 (relational claims, demoted 2026-10-02)

## Context
An absence claim ("there is no X") is supported by the rule that two distinct
searches looked for X and found nothing. Since J-36, no search tool is captured:
the "searches" are `query_provenance` strings — URLs and file paths the drafting
agent chose. Round 20 to round 23 closed the cheapest routes (failed and blank
fetches counted as searches); the class remains: two SUCCESSFUL fetches of pages
the agent picked can still certify that something does not exist.

## Decision
`ground()` never returns `ABSENCE_SUPPORTED`. The full rule chain is kept,
unchanged, as `_absence_chain`; when it would certify, the verdict is
`UNVERIFIED_ABSENCE` and the report carries
`absence_diagnostic: "searches_would_qualify"`. Nothing is deleted.

## Price (measured, `measure_rates`)
Error-A **10/25 → 11/25 (0.400 → 0.440)** — one gold row, q13, the corpus's only
certified gold-grounded absence. Error-B **0/27 unchanged**. Honest-drafts
instrument: no change. **The sample is one row; the usage price is unmeasured.**

## Consequences
Four tripwires close BY DEMOTION, not repair (J-42, R8C-01, R8C-02, R8C-03):
they reopen if absence is ever re-promoted. Upgrade path: capture real search
queries (J-36), then re-promote behind its own adversary round.

## What would reverse it
A customer job where absence is the product ("no adverse event reported",
"no sanction found"): then J-36 is the investment, not this demotion.
