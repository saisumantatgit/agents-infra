---
id: hq-2026-07-14-graphify-pilot
from: config-management-hq
to: agents-infra
type: brief
priority: P2
created: 2026-07-14
ack_required: true
thread_id: code-knowledge-graph-study
acceptance_criteria:
  - Gate 0 evidence recorded (version/SHA pinned, install surface inspected)
  - Gate 1 evidence recorded (invocation mode confirmed + OBSERVED network egress on a toy-repo run, not asserted)
  - Full pilot run per TDR-001 (6 gold tasks, CMM same-corpus A/B, all metrics captured)
  - CR-001 written within 24h of run, ≤80 lines, projection-vs-actual (ADR-025)
  - agents-infra logbook entry
  - Outbox ack to HQ with ≤10-line result summary + verdict on the iVal Gate-1 contingency
---

# Execute TDR-001: graphify pilot (Pilot B, code-knowledge-graph study)

**Everything you need is in `docs/tdr/TDR-001-graphify-pilot.md`** — approved by Sai 2026-07-12, written before execution per ADR-024. Read it in full before touching the tool; this brief only adds cross-repo context the TDR doesn't carry.

## Context you need from HQ's side

- This is Pilot B of a two-pilot study. Pilot A (`codebase-memory-mcp`, deterministic/local) already PASSED on iVal 2.0 (iVal TDR-001/CR-001: 17.8× aggregate context reduction). Your job is the contrast axis: LLM-enriched semantic indexing vs Pilot A's structural indexing, measured on THIS repo with a same-corpus CMM A/B (CMM is already registered as a user-scope MCP server — `mcp__codebase-memory-mcp__*`).
- Research basis (per-claim confidence ratings): HQ `docs/research/code-knowledge-graph-tools-comparison-2026-06-19.md`. Key unverified claims you are converting to facts: skill-mode distribution (`/graphify .`, confidence 70), semantic-pass egress destination (confidence 60), all capability claims (50–65).

## The one thing that must not be shortcut

**Gate 1 is blocking for a downstream decision bigger than this pilot:** Sai has pre-approved graphify on iVal 2.0 (payroll data) *contingent on Gate 1 showing the semantic pass runs in-session under the subscription with no non-Anthropic egress*. Observe actual network behavior on a toy repo (nettop / proxy / sandbox-exec deny-test) before the real run. If you find any egress to a non-Anthropic endpoint, the pilot may still proceed on this repo (it's non-sensitive) but the ack MUST flag the iVal contingency as FAILED.

## Operating notes

- `graph.json` and any generated index artifacts: gitignore BEFORE first run (TDR Implementation step 3).
- Token circuit breaker: if the toy-repo run projects >5M tokens for the full corpus, STOP and report back instead of running the full index.
- Treat the tool as experimental (created 2026, no published benchmark): pin the SHA, skim the install surface for anything executing beyond stated scope.
- Discontinuity rule applies: if your session gets interrupted mid-run, verify artifacts from evidence before trusting any prior report of progress.

## Reporting

Outbox ack (`responds-to: hq-2026-07-14-graphify-pilot`) with: pilot verdict (PASS/FAIL per TDR Verification), the iVal Gate-1 contingency verdict, headline numbers (index time / size / token cost / gold-task A/B), and pointers to CR-001 + logbook. Keep the ack ≤10 lines; full detail lives in the CR.
