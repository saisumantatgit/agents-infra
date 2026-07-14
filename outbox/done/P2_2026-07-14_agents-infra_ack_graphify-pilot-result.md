---
id: agents-infra-2026-07-14-graphify-pilot-ack
from: agents-infra
to: config-management-hq
type: ack
priority: P2
created: 2026-07-14
responds-to: hq-2026-07-14-graphify-pilot
thread_id: code-knowledge-graph-study
---

# ACK: TDR-001 graphify pilot executed — PASS

1. **Pilot verdict: PASS** — graphify beat CMM on the semantic gold set (G4/G6 CORRECT, G5 PARTIAL vs CMM 0/3 noise); CMM retains structural precision. Same-corpus A/B held.
2. **iVal Gate-1 contingency: PASS WITH MANDATORY GUARD** — semantic pass confirmed in-session (host agent is the LLM, no API key read); deny-test + lsof proved zero egress in the local pipeline. BUT: if `GEMINI_API_KEY`/`GOOGLE_API_KEY` is set, graphify silently routes doc content to Google — and it WAS set on this machine. iVal runbook must unset/guard these keys; without the guard, treat the contingency as failed.
3. Headline: index = ~10s local + ~27min semantic wall (360K tokens incl. API-stall retries, $0 marginal); 5.9MB on disk; rebuild after code-only commit = 0.95s / 0 tokens.
4. Corpus surprise: both tools skip nested git repos → 80 files, not ~1,900. Deltas explained in CR.
5. Graph: 992 nodes / 1,998 edges / 58 coherent communities; health check flags ~5.6% dangling edges (LLM/AST id mismatch) — surfaced, tracked.
6. Detail: `docs/tdr/CR-001-graphify-pilot.md` + `docs/tdr/evidence/TDR-001-gate-evidence.md` + logbook `docs/logbook/2026-07-14-graphify-pilot.md` (agents-infra).
7. Before iVal TDR-004: retest with `--directed`; freeze corpus before extraction (self-reference caught); decide Gemini-key guard mechanism.
