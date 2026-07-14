# TDR-001 — graphify Pilot (Pilot B of the Code-Knowledge-Graph Study)

**Status:** Approved (Sai, 2026-07-12 — verbal approval in HQ session; see Approval Block)
**Date:** 2026-07-12
**Owner:** agents-infra (pilot corpus); study governance at HQ
**Prospective:** written before execution, per ADR-024

## Context

HQ's code-knowledge-graph study (`~/vibe-coding/Agents/Claude/docs/research/code-knowledge-graph-tools-comparison-2026-06-19.md`) identified two tool species: deterministic structural indexing vs LLM-enriched semantic indexing. Pilot A (`codebase-memory-mcp`, deterministic) ran on iVal 2.0 and PASSED (iVal TDR-001/CR-001: 17.8× aggregate context reduction, zero-egress verified). Pilot B evaluates the other species: `safishamsi/graphify` — tree-sitter AST for code (local, no LLM) + LLM semantic pass over docs/PDFs/schemas/media + Leiden community detection, one multimodal graph.

Sai's real need is the sensitive repos (iVal 2.0, ProSure). iVal graphify use is **pre-approved contingent on this pilot's gates passing** (2026-07-12). agents-infra is the pilot corpus because it is non-sensitive own IP (~1,900 py/md files, 6 CLI plugins), so the pilot can proceed regardless of how the egress question resolves.

## Decision

Run graphify on agents-infra as a bounded pilot, with a same-corpus A/B against codebase-memory-mcp, gated by an install-time backend/egress verification. Produce CR-001 (agents-infra) with projection-vs-actual.

## Alternatives Considered

1. **Pilot directly on iVal** — rejected: privacy gate unresolved at pilot start; a failed gate would block the whole pilot rather than just the extension.
2. **Install Ollama to unlock iVal immediately** — rejected: measures graphify-with-weak-local-model, not the tool as designed; adds a confound before baseline value is established.
3. **Skip Pilot B, standardize on CMM** — rejected: CMM answers structural questions only; iVal/ProSure value concentrates in docs/spec YAMLs that CMM is blind to. The semantic axis is the whole reason Pilot B exists.

## Rationale

- Contrast axis vs Pilot A is only interpretable on a **same corpus**: CMM indexes agents-infra in seconds, so both tools run against identical gold tasks here.
- Research-doc claims about graphify sit at confidence 50–70 (vendor README, no published benchmark) — the pilot's job is to convert those to measured facts.
- Distribution model (confidence 70): ships as an AI-assistant skill (`/graphify .`) inside Claude Code → semantic pass runs on the session model under Sai's subscription (no API key, no new vendor egress). **If confirmed, the iVal privacy gate collapses to already-accepted Anthropic exposure.** If instead it requires a standalone backend, that mode needs an API key (usage-billed) or Ollama, and iVal extension is re-gated.

## Configuration

- Corpus: `~/vibe-coding/Agents/agents-infra` (main, clean tree at pilot start).
- Baseline: CMM fresh index of the same corpus (user-scope MCP already registered).
- Gold tasks: 6 queries, reused shape from iVal CR-001 — 3 structural ("what calls X", "trace import chain", "where is Y defined") + 3 semantic ("what does plugin Z do and which docs describe it", "which modules implement the PROVE gate concept", "summarize the relationship between TEST_PLAN_v2 and the code it tests"). Structural set scores CMM-vs-graphify head-to-head; semantic set tests graphify's differentiating claim (CMM expected to lose or abstain — that asymmetry is the finding, not a flaw).
- Metrics per task: context bytes consumed, tool calls, wall latency, correctness (hand-adjudicated). Plus: index build time, on-disk size, token cost of the semantic pass, rebuild time after one commit.

## Cost (projection)

- Semantic pass over ~1,900 files (docs subset likely 300–600 files): est. 0.5–2M tokens of subscription usage — **flag: this is a projection with wide error bars; actuals to CR-001**.
- Wall time: est. 30–90 min indexing (LLM-bound). Human time: ~1 session.
- $0 marginal if skill-mode/subscription confirmed; else defer rather than buy an API key mid-pilot.

## Implementation

1. **Gate 0 — provenance & install:** fetch graphify from `github.com/safishamsi/graphify`, pin the version/SHA, read install surface before running (young tool, <5 months old — treat as experimental; skim for anything that executes beyond its stated scope).
2. **Gate 1 — mode & egress verification (BLOCKING for iVal extension):** confirm invocation mode (Claude Code skill vs standalone), and observe actual network behavior during a small-scope index run (e.g., `nettop`/proxy or sandbox-exec deny-test on a toy repo). Record: where does doc content actually go?
3. Decide `graph.json` hygiene BEFORE first run: **gitignore it** for the pilot (do not commit generated artifacts into agents-infra; revisit if adopted).
4. Full index of agents-infra; capture build metrics.
5. Fresh CMM index of agents-infra; run the 6 gold tasks on both; adjudicate.
6. CR-001 (agents-infra) within 24h of the run, ≤80 lines, projection-vs-actual per ADR-025.

## Verification

- Gate 1 evidence recorded (mode + observed egress), not asserted.
- Gold-task table: per-task metrics + correctness verdicts, both tools.
- Pilot PASSES if: graphify materially beats CMM (or answers what CMM cannot) on ≥2 of 3 semantic tasks with acceptable cost, AND Gate 1 shows no non-Anthropic egress in the chosen mode.

## Risks

- **Vendor-README optimism** (confidence 50–60 on capability claims) — mitigated by measuring, not trusting.
- **Young tool** (created 2026, no published benchmark) — pinned version, experimental status, easy rollback.
- **Token burn on subscription** — semantic indexing cost is unmeasured; if the small-scope Gate 1 run projects >5M tokens for the full corpus, pause and reassess scope before the full run.
- **Nondeterministic index** (LLM-enriched) — same query may differ across rebuilds; note reproducibility observations in CR.

## Rollback

Remove graphify install + generated `graph.json`/index artifacts; delete any MCP registration; agents-infra tree untouched (artifact gitignored). CMM baseline index is disposable (`delete_project`).

## Open Questions

1. Exact backend options in standalone mode (Anthropic base URL supported?) — matters only if skill mode disconfirmed.
2. Rebuild cost per commit (full re-enrichment vs incremental?) — decisive for daily-driver adoption.
3. iVal extension TDR (iVal TDR-004) to be written only after this pilot's CR — carries the pre-approval + Gate 1 evidence forward.

## Approval Block

- [x] Approved to execute — Sai, 2026-07-12 ("I am approving the Pilot B as designed, on agents-infra"), including contingent iVal extension ("i am also approving ival_2.0 graphify") gated on Gate 1 + pilot PASS.
- [ ] CR-001 reviewed and closed.
