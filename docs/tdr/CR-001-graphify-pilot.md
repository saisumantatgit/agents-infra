# CR-001 — graphify Pilot (companion to TDR-001)

**Executed:** 2026-07-14 · **Tool:** graphifyy 0.9.15, SHA 961b78e5 pinned · **Corpus:** agents-infra (default scan)
**Evidence:** `evidence/TDR-001-gate-evidence.md` · Gold-task detail: session logbook 2026-07-14.

## Projection vs actual

| Metric | TDR projection | Actual | Δ | Note |
|---|---|---|---|---|
| Corpus size | ~1,900 files | 80 files / 98.6K words | −96% | Both tools skip nested git repos; the six Agent-* dirs are nested repos. Same-corpus A/B preserved. |
| Semantic-pass tokens | 0.5–2M | 360,155 | below band | 42 doc files → 2 subagents; total includes retry inflation from 2 API stalls. |
| Index wall time | 30–90 min | ~27 min semantic (incl. 2 infra stalls + resumes; ~11 min pure agent runtime) + ~10s local (detect 0.25s, AST 3.85s, build+cluster 5.37s) | below band | LLM-bound stage dominated by API instability, not tool. |
| Marginal cost | $0 if skill-mode confirmed | $0 (subscription; no API key read) | 0 | Skill mode CONFIRMED from shipped skill.md. |
| On-disk size | (unprojected) | 5.9MB (graph.json 1.19MB, graph.html 1.07MB, cache) | — | |
| Rebuild after commit (no doc change) | unknown (OQ2) | 0.95s, 0 tokens (warm-cache probe: semantic cache 42/42 hit + AST re-extract + rebuild; no file actually mutated) | — | OQ2 answered for the code-only case; doc-change rebuild cost still unmeasured. |

## Gate results

| Gate | Verdict | One-line basis |
|---|---|---|
| Gate 0 provenance/install | PASS | SHA pinned; PyPI↔repo consistent; install = file copies + CLAUDE.md registration; no telemetry; no startup phone-home. |
| Gate 1 mode/egress | PASS (pilot mode) | Deny-test: pipeline completes under `deny network*`; lsof: 0 sockets. **Guard required: `GEMINI_API_KEY`/`GOOGLE_API_KEY` set ⇒ silent doc egress to Google — was SET on this machine; unset for all runs.** |

## Gold-task A/B (6 tasks; bytes = answer payload; hand-adjudicated)

| Task | graphify | CMM | Verdict pair (graphify / CMM) |
|---|---|---|---|
| G1 callers of `classify` | 6.3KB, 532ms | 0.3KB, <1s | PARTIAL (full recall incl. `emit_claim_features`, buried in 139-node undirected dump) / PARTIAL (precise but missed cross-file caller) |
| G2 importers of `capture_core` | 4.5KB, 654ms | 0.6KB, 117ms | CORRECT (all 9 + true reverse dep; edge direction rendering ambiguous) / CORRECT (exact file list) |
| G3 where is `load_store` | 6.2KB, 334ms | 2.5KB, <1s | CORRECT / CORRECT (richer: signature, docstring, complexity) |
| G4 what is Agent-Assure + docs | 6.2KB, 317ms | — | **CORRECT / WRONG** (BM25 returned unrelated test functions) |
| G5 modules implementing grounding gate | 0.8KB, 318ms | — | **PARTIAL / WRONG** (graphify: concept docs, no module bridge; CMM: cosine noise, scores 0.02–0.04) |
| G6 TEST_PLAN_v2 ↔ code it tests | 6.4KB, 290ms | — | **CORRECT / WRONG** (graphify links plan→PIR-001→AAR-002→test cluster; CMM noise) |

Structural set: CMM wins on precision/answer-shape; graphify recall-complete but low-precision (BFS dumps; undirected graph loses caller/callee direction — `--directed` untested, see OQ). Semantic set: graphify 2 CORRECT + 1 PARTIAL vs CMM 0/3.

## Verdict

**Pilot PASS** per TDR-001 Verification: graphify answers what CMM cannot on ≥2 of 3 semantic tasks (G4, G6 decisively; G5 weakly) at acceptable cost (360K tokens, $0 marginal), and Gate 1 shows no non-Anthropic egress in the pilot mode. **iVal contingency: PASS WITH MANDATORY GUARD** — Gemini env keys must be absent/unset wherever graphify runs on sensitive corpora.

## Sub-run verdicts

| Sub-run | Verdict |
|---|---|
| Toy-repo deny-test (Gate 1) | PASS — zero egress proven two ways |
| Full index build | PASS — 992 nodes / 1,998 edges / 58 communities; health check flagged 111 dangling + 47 collapsed edges (LLM/AST id mismatch; surfaced per honesty rules) |
| Gold-task A/B | PASS — semantic differentiation confirmed |
| Warm-cache rebuild probe | PASS — 0.95s / 0 tokens (code-only path; doc-change path unmeasured) |

## Deltas >20%, explained

1. Corpus −96%: nested-repo exclusion (both tools) — projection assumed monorepo scanned flat.
2. Tokens below band: linear consequence of corpus delta (42 docs vs assumed 300–600).

## Open items carried forward

- `--directed` mode untested — may fix G1/G2 direction ambiguity; retest before iVal TDR-004.
- 111 dangling edges: semantic↔AST node-ID mismatch rate ≈5.6% of edges; check upstream issue tracker before adoption.
- Self-reference: mid-pilot evidence file was swept into chunk 2's extraction (detect ran after it was written). Harmless here; on sensitive repos, freeze corpus before extraction.
- sdist↔repo byte-diff not performed (Gate 0 residual risk, low).
