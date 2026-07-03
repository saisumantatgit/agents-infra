# Agent-Assure Phase 1 — Status & Live-Validation Gate

**Branch:** `agent-assure-phase1b` (pushed). **PR:** [#2](https://github.com/saisumantatgit/agents-infra/pull/2) — OPEN. Base: `agents-infra` main (Phase 1a merged). Env: uv (`uv sync --extra dev`, then `uv run pytest`).

## Status: Phase 1 COMPLETE. **LIVE-VALIDATION GATE PASSED (2026-07-03).** 222 tests pass. Merge decision is Sai's.

### DONE + committed + pushed
- **1b capture hook** (Tasks 1–5): `capture_core.py`, `capture_hook.py`, `hooks/hooks.json`, closed-loop integration test.
- **1b parked findings** (from the completion-workflow panel) — all fixed (`aba7c7c`): distinct missing-`tool_response` diagnostic, deterministic thread-contention proof **with a red-proof**, fcntl fail-closed guard, non-NFKC round-trip coverage.
- **1c packaging** (`2dc08b2`): `plugin.json`, `/assure-verify` command, `verify-grounding` skill, `references/`, `install.sh`, LICENSE, README; plugin-root layout (verified vs the shipped superpowers plugin).
- **Demo** (`2dc08b2` + `2e07f94`): `demo/` — `build_store.py` + `draft-grounded`(PASS) + `draft-fabricated`(FAIL) + `show_report.py`; proven end-to-end through the installed `.venv` python.
- **Final adversarial review** (whole-branch, 5 lenses, each finding independently verified — 5 confirmed, ALL FIXED):
  - 🔴 **CRITICAL** (`e01c58e`): a fabricated claim wrapped in a markdown header (`# … [S9]`) was classified `NON_CLAIM` → dropped from the denominator → **gate=PASS**. Pre-existing bug in merged `ground_check.py` (same class as the Phase-1a verbless hole). Closed systemically, proven-red regression. **Hook-independent — can be fast-tracked to `main` ahead of hook validation.**
  - Fixed (`2e07f94`): MCP content-block shape fail-loud; cross-process lock test; demo-output accuracy; score-gate doc precedence.

### LIVE-VALIDATION — EXECUTED 2026-07-03 ✅ (real headless Claude Code sessions, raw PostToolUse payloads captured via a tap hook; regression fixtures in `tests/test_live_shapes.py`)

Method: scratch project + `claude -p` with the hook registered; a parallel tap hook dumped every raw stdin payload; each assumed shape was compared to ground truth, deviations fixed TDD (proven-red first), then re-fired live until all four tools captured. Finally the FULL plugin path was exercised via `claude -p --plugin-dir` (plugin's own `hooks/hooks.json` → `${CLAUDE_PLUGIN_ROOT}/.venv/bin/python`).

Checklist outcomes — every assumed shape differed from reality except DDG; all fixed in `capture_core.py`/`capture_hook.py` per the "only the extractor predicate changes" plan:
- (a) Exa `web_fetch_exa` — **DIFFERED**: TOP-LEVEL MCP content-block list `[{"type":"text","text":…,"_meta":…}]`; tool_input uses PLURAL `{"urls": [...]}`. Fixed (list normalization + urls[0] for url/provenance).
- (b) truncation — **DIFFERED**: no `{preview, file_path}` offload exists. `Read` truncates INLINE (`truncatedByTokenCap: true`, `numLines` < `totalLines`); store holds exactly what the model saw. Overflow path retained as defensive fail-loud guard.
- (c) `Read` — **DIFFERED**: payload is `{"type":"text","file":{"filePath","content",…}}` with RAW file text — NO cat-n prefixes (those exist only in the model-rendered view). `strip_cat_n_prefix` REMOVED (it would corrupt TSV-like content).
- (d) DDG `fetch_content` — **CONFIRMED**: plain verbatim str (the only assumption that survived contact with reality).
- WebFetch (bonus) — **DIFFERED**: `{"result": str, "code", "bytes", …}` envelope. Fixed; `haiku_summary` hard-spec preserved.
- 🔴 **Packaging fix**: hooks lived at `.claude-plugin/hooks.json` — **silently ignored by the plugin loader**. Moved to `hooks/hooks.json` (the real convention); proven live via `--plugin-dir` (plugin would otherwise have shipped installable-but-inert).
- Capture→ground loop CLOSED live: 5-source store built by real sessions; grounded claims → `GROUNDED`, fabricated facts → `UNGROUNDED`, fabricated `[S9]` → `UNVERIFIED_CITATION`, gate `FAIL` at 0.0.

Residual (non-blocking): (i) harness-level truncation of a HUGE MCP result unprobed — Exa/DDG cap content server-side before Claude Code would need to truncate; extractor fails loud if a new shape ever appears. (ii) Calibration observation for Phase 2a: compound source sentences ground poorly when cited as fragments/prefixes (T1 misses on sentence-boundary punctuation, T2 Jaccard ~0.54 < τ=0.65) — recoverable Error A, consistent with moat-integrity bias, but will inflate NEEDS_WORK on real drafts; feed to the calibration harness.

### NEXT
1. **Sai: merge PR #2** — the live-validation hold is satisfied.
2. **Phase 2**: decide sequencing (`docs/PHASE2-SEQUENCING.md` — recommends calibration-harness first, inverting a front-end-first order) + provide/ratify gold labels. Then build the chosen slice via subagent-driven TDD.
