# Logbook — 2026-07-14 — TDR-001 graphify pilot (Pilot B, code-knowledge-graph study)

## What

Executed TDR-001 end-to-end per HQ brief `hq-2026-07-14-graphify-pilot`: Gate 0 (provenance/install surface), Gate 1 (mode + observed egress), full graphify index of agents-infra, same-corpus gold-task A/B vs codebase-memory-mcp, CR-001, outbox ack. **Pilot PASS; iVal contingency PASS WITH MANDATORY GUARD.**

## Why

Pilot B of HQ's two-pilot study: convert graphify's confidence-50–70 research claims into measured facts on non-sensitive own IP, gating the pre-approved iVal 2.0 extension on observed (not asserted) egress behavior.

## Done

- Gate 0 PASS: repo transferred `safishamsi/graphify` → `Graphify-Labs/graphify`; SHA pinned `961b78e5`; PyPI `graphifyy` 0.9.15 provenance consistent; install = file copies + CLAUDE.md registration; no telemetry; opt-in hooks. Evidence: `docs/tdr/evidence/TDR-001-gate-evidence.md`.
- Gate 1 PASS (pilot mode): local pipeline completed under `sandbox-exec deny network*` (2.24s) AND opened zero sockets across 40 lsof polls. Skill mode confirmed from shipped `skill.md`: host agent IS the semantic LLM; no Anthropic API key read.
- **Critical catch: `GEMINI_API_KEY` was set in the environment; graphify silently routes doc extraction to Google when present.** All pilot runs used `env -u GEMINI_API_KEY -u GOOGLE_API_KEY`. iVal use requires this guard permanently.
- Full index: 992 nodes / 1,998 edges / 58 communities; detect 0.25s + AST 3.85s + build 5.37s local; semantic pass 2 subagents, 360,155 tokens, ~27min wall including two API stream stalls (watchdog kills) recovered via SendMessage resume with artifacts verified absent before each retry.
- A/B: CMM precise on structural (G2, G3 CORRECT; G1 PARTIAL — missed cross-file caller `emit_claim_features`); graphify recall-complete structural but undirected dumps; semantic set graphify 2 CORRECT + 1 PARTIAL vs CMM 0/3 (BM25/cosine noise). Full table in CR-001.
- CR-001 written (≤80 lines, ADR-025); gitignore for `graphify-out/` added BEFORE first run; inbox brief moved to done; ack in outbox/pending.

## How (methods worth reusing)

- Egress proof = deny-test (proves no network *needed*) + lsof polling (proves none *attempted*). Two-sided evidence, ~3 minutes of work.
- Dead-run proof before resume: chunk file absent on disk + watchdog-failed status → resume via SendMessage (agents kept their 21-file read context; retry cost ≈ one write).
- Corpus parity check before A/B: both tools independently skip nested git repos → 80-file shared corpus, comparison stays fair (found by breaking down detect output by top-level dir, not by assuming).

## Decisions

- D1: Run pilot on default-scan corpus (80 files) rather than force-including nested repos — both tools' defaults agree; forcing would add confounds. Recorded as CR delta, not a deviation.
- D2: Gold tasks adapted to in-corpus anchors (classify/capture_core/load_store; Agent-Assure semantics), preserving TDR's 3+3 shape — original examples referenced excluded plugin internals.
- D3: iVal contingency reported as PASS-with-guard, not bare PASS — the Gemini key path is documented tool behavior we avoided, and the machine had the key set; a bare PASS would have shipped a footgun.
- D4 (case resolution): subagent token split (in/out) unavailable from Agent tool usage — recorded total as input_tokens in cost.json with note. Systemic fix would be harness-side usage split exposure; carried as known limitation, not worth an issue.

## Agents (telemetry)

| Agent | Model | Tokens | Tools | Outcome |
|---|---|---|---|---|
| Semantic chunk 1/2 | session (Fable) | 183,354 | 1 | 68n/94e/3h after 1 API-error death + 1 stall; resumed twice |
| Semantic chunk 2/2 | session (Fable) | 176,801 | 1 | 53n/87e/3h after 1 stall; resumed once |

Total 360K subagent tokens (includes retry inflation). Both outputs validated (JSON parse + ID-format check) before merge. API instability also hit the main loop (2 classifier outages, 1 clone timeout) — all recovered.

## Reflection

The pilot's most valuable finding was not in the measurement plan. The TDR asked "does the semantic pass egress?"; the answer was "no — unless an unrelated env var is set, in which case silently yes." No amount of reading the tool's README would have weighted that correctly: the skill file buries the Gemini routing in a tip about API keys, and the machine happened to have the key. The gate design (observe on a toy repo first) did exactly what gates are for — it turned a latent environmental hazard into a written guard condition before any sensitive byte was at stake. Also instructive: graphify's semantic win is real but its structural answers are recall-dumps, not answers — the two tools are complements, not competitors, which reframes the "standardize on one" question the study started with.

## Next

- HQ: consume ack (outbox/pending → their inbox), review CR-001, decide iVal TDR-004 authoring.
- Before iVal TDR-004: `--directed` retest; corpus freeze protocol; Gemini-key guard mechanism (wrapper vs hook).
- Housekeeping: `P2_2026-07-04` calibration handoff still in inbox/pending — appears superseded by 07-08→07-14 calibration logbooks in the worktree; confirm and move to done next calibration session.
- TDR-001 Approval Block: CR-001 awaits Sai's review-and-close checkbox.
