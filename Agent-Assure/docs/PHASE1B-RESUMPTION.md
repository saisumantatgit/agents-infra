# Agent-Assure Phase 1b/1c — Resumption State (paused on budget, 2026-06-28)

**Branch:** `agent-assure-phase1b` (pushed to origin). Base: `agents-infra` main (Phase 1a merged). Env: uv (`uv run pytest` from `Agent-Assure/`).

## DONE + committed + pushed (201 tests green)
- **Tasks 1–5 of the capture hook**: `scripts/capture_core.py` (make_record, overflow reconstruct, next_source_id, append_record, atomic source_id, cat-n strip), `scripts/capture_hook.py` (stdin PostToolUse entry), `.claude-plugin/hooks.json`, closed-loop integration test (`tests/test_capture_integration.py`). All per-task reviewed; foundation re-verified "sound".

## NOT done (paused on budget)
- **1c packaging** (none of it): `.claude-plugin/plugin.json`, `.claude/skills/verify-grounding/SKILL.md`, `.claude/commands/assure-verify.md`, `references/grounding-failure-types.md`, `install.sh`, `README.md`. Match the sibling `agents-infra/Agent-Cite` conventions.
- **Phase-1 final adversarial review** (workflow died here).

## PARKED Task-4 findings — adjudicate + fix before the PR (from the completion-workflow verifier panel)
1. **IMPORTANT — silent drop on missing `tool_response`.** `capture_hook.py` `event.get("tool_response")` → None when the key is absent → `make_record`→`_extract_text` raises `TypeError` → caught in `main()`, logged to stderr, exit 0. The retrieval event is LOST with only a stderr line. Fix: explicit guard — if `tool_response` absent, emit a distinct `TASK-4-VALIDATION` message and return early; do not conflate with unknown-shape. (high confidence)
2. **IMPORTANT — silent-drop observability untested.** No test asserts stderr contains `[assure-hook] capture skipped` on an unrecognized-shape valid-JSON event. Add: fire `tool_name=mcp__exa__web_fetch_exa, tool_response=42` → assert exit 0 AND `capture skipped` in stderr. (high)
3. **IMPORTANT — concurrency test is a tautology (TDD gap).** `test_concurrent_appends_unique_ids` passes EVEN WITH `fcntl.flock` removed — 12 subprocesses stagger (~50ms startup) and never contend, so the test never proves the lock is needed. Fix: a real contention test — `threading.Thread` (not subprocess) with `next_source_id` patched to `sleep(0.05)` inside the critical section; assert IDs unique WITH lock, and (as red proof) duplicates WITHOUT it. (high)
4. **MINOR — `hooks.json` uses bare `python3`** which may resolve outside the uv venv (system python3 < 3.11 breaks it). Fix: `"${CLAUDE_PLUGIN_ROOT}/.venv/bin/python"`. (medium)
5. **MINOR — `fcntl` module-level import** is POSIX-only → ImportError on Windows blocks all of `capture_core`. Move import inside the lock function or platform-guard. (high)
6. **MINOR — lock file `<store>.lock` never cleaned up** (harmless 0-byte, but clutters `.assure/`). Document as intentional or clean up. (medium)
- Scope held; cat-n prefix strip correct + tested at 3 levels. Full verifier output: workflow run `wf_b6f460e1-b7a`.

## ALSO parked (from Task-3 second-opinion)
- (Important, low real-world risk) round-trip test uses only NFKC-stable unicode — add a non-NFKC `text` round-trip test (or confirm `make_record` always normalizes upstream — it does via the `_sha256_nfkc` path).
- (Minor) `load_store` NFKCs only `text`, not the other string fields.

## LIVE-VALIDATION (user, needs a real Claude Code session — Claude cannot self-certify)
The hook's assumed `PostToolUse` payload shapes must be confirmed against reality: (a) Exa `web_fetch_exa` response shape (assumed `dict["text"]`/str); (b) the large-result truncation form (assumed `{preview, file_path}`) for overflow reconstruction; (c) `Read` cat-n prefix format; (d) DDG `fetch_content` = verbatim. If a real shape differs, only the detection predicate / extractor changes — the rest is shape-agnostic. Then: run the hook live, confirm `.assure/evidence-store.jsonl` populates, and that `ground_check.py` grounds against it.

## NEXT (resume order, when budget returns)
1. Fix parked Importants 1–3 (TDD) on this branch. 2. Build 1c packaging. 3. Final Phase-1 adversarial review. 4. Open the held PR. 5. User live-validation → merge. **Do NOT merge before live-validation** (packaging wraps the unvalidated hook).
