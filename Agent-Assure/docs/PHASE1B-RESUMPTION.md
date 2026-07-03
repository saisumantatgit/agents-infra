# Agent-Assure Phase 1 — Status & Live-Validation Gate

**Branch:** `agent-assure-phase1b` (pushed). **PR:** [#2](https://github.com/saisumantatgit/agents-infra/pull/2) — OPEN, **HELD** (do not merge before live-validation). Base: `agents-infra` main (Phase 1a merged). Env: uv (`uv sync --extra dev`, then `uv run pytest`).

## Status: Phase 1 COMPLETE, held at the live-validation gate. **216 tests pass.**

### DONE + committed + pushed
- **1b capture hook** (Tasks 1–5): `capture_core.py`, `capture_hook.py`, `.claude-plugin/hooks.json`, closed-loop integration test.
- **1b parked findings** (from the completion-workflow panel) — all fixed (`aba7c7c`): distinct missing-`tool_response` diagnostic, deterministic thread-contention proof **with a red-proof**, fcntl fail-closed guard, non-NFKC round-trip coverage.
- **1c packaging** (`2dc08b2`): `plugin.json`, `/assure-verify` command, `verify-grounding` skill, `references/`, `install.sh`, LICENSE, README; plugin-root layout (verified vs the shipped superpowers plugin).
- **Demo** (`2dc08b2` + `2e07f94`): `demo/` — `build_store.py` + `draft-grounded`(PASS) + `draft-fabricated`(FAIL) + `show_report.py`; proven end-to-end through the installed `.venv` python.
- **Final adversarial review** (whole-branch, 5 lenses, each finding independently verified — 5 confirmed, ALL FIXED):
  - 🔴 **CRITICAL** (`e01c58e`): a fabricated claim wrapped in a markdown header (`# … [S9]`) was classified `NON_CLAIM` → dropped from the denominator → **gate=PASS**. Pre-existing bug in merged `ground_check.py` (same class as the Phase-1a verbless hole). Closed systemically, proven-red regression. **Hook-independent — can be fast-tracked to `main` ahead of hook validation.**
  - Fixed (`2e07f94`): MCP content-block shape fail-loud; cross-process lock test; demo-output accuracy; score-gate doc precedence.

### The ONLY remaining gate: LIVE-VALIDATION (user — needs a real Claude Code session)
Claude cannot self-certify that Claude Code actually FIRES the `PostToolUse` hook, nor the exact live payload shapes. Confirm against reality:
- (a) Exa `web_fetch_exa` response — assumed `str` OR `{"text": str | [content-blocks]}` (content-block list now normalized).
- (b) large-result truncation form — assumed `{preview, file_path}` for overflow reconstruction.
- (c) `Read` cat-n line-number prefix format.
- (d) DDG `fetch_content` = verbatim.

Then: run the hook live, confirm `.assure/evidence-store.jsonl` populates, and that `ground_check.py` grounds against it. If a shape differs, **only** the extractor predicate changes (see the `TASK-4-VALIDATION` notes in `capture_core.py` / `capture_hook.py`). **Do NOT merge PR #2 before this.**

### NEXT (once live-validation passes)
1. Merge PR #2. *(Optional now: cherry-pick the CRITICAL gate fix `e01c58e` to `main` sooner — it is hook-independent.)*
2. **Phase 2**: decide sequencing (`docs/PHASE2-SEQUENCING.md` — recommends calibration-harness first, inverting a front-end-first order) + provide/ratify gold labels. Then build the chosen slice via subagent-driven TDD.
