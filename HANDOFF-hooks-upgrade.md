# Handoff: Lifecycle Hooks Upgrade for All 6 Plugins

**Date:** 2026-03-22
**From:** Claude Opus 4.6 session (Config Management HQ — technology scout)
**To:** Next Claude session (agents-infra implementation)
**Repo:** `~/vibe-coding/Agents/agents-infra/`

---

## Origin

Technology Scout Report on Claude Code Hooks (2026-03-22, Config Management HQ).

**Finding:** agents-infra plugins currently use ~5% of the Claude Code hooks API. Only Scribe has a single SessionStart hook (`hooks/load-context.sh`) that loads the last logbook handoff into session context. The other five plugins have zero hooks. The hooks system offers 25 event types and 4 handler types. Upgrading to full lifecycle hooks transforms the plugins from passive prompt-only tools to active autonomous governance agents.

## Source Material

- Scout report: `/tmp/scout_hooks.md` (read this first for full context on the hooks API)
- Claude Code hooks docs: https://docs.anthropic.com/en/docs/claude-code/hooks
- Reference repo: `disler/claude-code-hook-mastery` (3,360 stars)

## Current Hook State (Verified 2026-03-22)

| Plugin | Hooks Today | Location |
|--------|-------------|----------|
| Scribe | 1 SessionStart (`load-context.sh`) | `Agent-Scribe/hooks/load-context.sh`, configured in `Agent-Scribe/adapters/claude-code/hooks/hooks.json` |
| Trace | 0 | — |
| Drift | 0 | — |
| PROVE | 0 | — |
| Cite | 0 | — |
| Litmus | 0 | — |

The existing Scribe hook reads stdin JSON for `cwd`, finds the latest logbook entry, extracts Handoff Notes and Blockers sections, and returns `{"additionalContext": "..."}`. Latency: ~100ms. This is the reference pattern for all new hooks.

---

## What to Upgrade

### P0 — Trace, Drift, Scribe (Week 1)

#### Trace — Real-time tool use logging

| Hook | Event Type | Handler Type | What It Does |
|------|-----------|--------------|--------------|
| NEW | PostToolUse | command (shell) | Log every tool invocation (tool name, args hash, result summary, timestamp) to `.trace/session-log.jsonl`. Structured JSONL, one line per invocation. |
| NEW | Stop | command (shell) | Write session summary to `.trace/session-summary.md` — total tool calls, unique tools used, files modified, duration. |

**Implementation notes:**
- PostToolUse receives `tool_name`, `tool_input`, `tool_output` in stdin JSON. Extract and log.
- Keep the JSONL appender idempotent — if the file does not exist, create it.
- The Stop hook should read the JSONL and compute aggregates.

#### Drift — Configuration drift detection

| Hook | Event Type | Handler Type | What It Does |
|------|-----------|--------------|--------------|
| NEW | PreToolUse | command (shell) | Guard against writes to `CLAUDE.md`, `MEMORY.md`, `SOUL.md` that violate ADR templates. If the tool is a file-write targeting these paths, validate structure against ADR-002/003/005 templates. Return `{"decision": "block", "reason": "..."}` on violation. |
| NEW | SessionStart | command (shell) | Compare current project `CLAUDE.md` against ADR-002 template (5 required sections: Architecture, Commands, Conventions, Key Files, Gotchas). Warn on missing sections or structural drift. Output via `additionalContext`. |

**Implementation notes:**
- PreToolUse must check `tool_name` — only intercept `Write`, `Edit`, or similar file-mutation tools.
- Parse the `file_path` from tool input to determine if it targets a governance file.
- SessionStart hook should be fast (<200ms). A simple section-header grep suffices.

#### Scribe — Context management (upgrade existing)

| Hook | Event Type | Handler Type | What It Does |
|------|-----------|--------------|--------------|
| EXISTS | SessionStart | command (shell) | Loads latest logbook handoff. **No changes needed.** |
| NEW | PostCompact | command (shell) | After context window compression, reload critical context: CLAUDE.md Architecture section, active tasks from logbook, and any build queue items. Return via `additionalContext`. |
| NEW | SessionStart (v2) | command (shell) | Extend existing hook: also load latest logbook entry timestamp and verify it is <24h old. If stale, add warning to context. |

**Implementation notes:**
- PostCompact is critical — context compression silently drops governance context. This hook restores it.
- Merge the SessionStart v2 logic into the existing `load-context.sh` rather than adding a second SessionStart hook.

---

### P1 — PROVE, Cite (Week 2)

#### PROVE — Evidence verification

| Hook | Event Type | Handler Type | What It Does |
|------|-----------|--------------|--------------|
| NEW | PreToolUse | command (shell) | Intercept `git commit` attempts. Check if test/lint commands were run in the current session (scan shell history or a session log). If no evidence of test execution, return `{"decision": "block", "reason": "No test evidence found. Run tests before committing."}`. |
| NEW | Stop | command (shell) | Scan session transcript for "task complete" or "done" claims. Check if corresponding evidence exists (test output, verification commands). Log warnings for uncited completion claims. |

**Implementation notes:**
- The PreToolUse hook needs to detect Bash tool calls containing `git commit`. Check `tool_name == "Bash"` and `tool_input.command` contains `git commit`.
- For Stop hook, the session transcript approach may not be available via hooks — investigate what Stop receives in stdin. May need to maintain a session-level evidence log that other hooks write to.

#### Cite — Source attribution

| Hook | Event Type | Handler Type | What It Does |
|------|-----------|--------------|--------------|
| NEW | PostToolUse | command (shell) | After WebFetch or WebSearch tool calls, auto-log the source URL with timestamp to `.cite/sources.jsonl`. Fields: `url`, `timestamp`, `query` (if search), `title` (if available from response). |

**Implementation notes:**
- PostToolUse receives tool output. For WebFetch, extract URL from input and response metadata.
- The JSONL file serves as an audit trail for citation tracking during `/cite-audit`.

---

### P2 — Litmus (Week 3)

#### Litmus — Quality gates

| Hook | Event Type | Handler Type | What It Does |
|------|-----------|--------------|--------------|
| NEW | PreToolUse | command (shell) | Before file writes (Write/Edit tools), validate against project conventions: file naming patterns, directory structure rules, required file headers. Return block decision on violations. |
| NEW | Stop | command (shell) | Run a lightweight quality checklist before session end: check for uncommitted changes, verify no TODO markers left in modified files, confirm test files exist for new source files. Output summary. |

**Implementation notes:**
- Convention rules should be configurable per project (read from a `.litmus/conventions.yaml` or similar).
- Stop hook should be advisory (warnings), not blocking — sessions should always be allowed to end.

---

## Architecture Decisions

1. **All hooks are shell commands** — Consistent with the existing Scribe pattern. Shell is the lowest-common-denominator handler type, works everywhere.
2. **Each plugin owns its own hooks directory** — `Agent-{Name}/hooks/` contains the scripts. `Agent-{Name}/adapters/claude-code/hooks/hooks.json` declares them.
3. **JSONL for structured logs** — Trace and Cite produce append-only JSONL files. Human-readable, `jq`-queryable, git-diffable.
4. **PreToolUse hooks return decision JSON** — `{"decision": "allow"}` or `{"decision": "block", "reason": "..."}`. This is the hooks API contract.
5. **No hook should exceed 500ms** — Hard latency budget. If a hook needs more time, it should log a warning and allow the action.

## Security Considerations

- **CVE awareness:** Check Point Research (Feb 2026) flagged Claude Code hooks as an attack surface for MCP rug-pull and tool-poisoning attacks. All hooks MUST:
  - Validate stdin JSON structure before parsing (do not blindly eval)
  - Never execute content from tool output as commands
  - Sanitize file paths to prevent directory traversal
  - Use `set -e` and `set -o pipefail` in all shell scripts
- **No secrets in hooks** — Hooks run in the user's shell environment. Never log environment variables or credentials.

## File Structure (Target State)

```
Agent-Trace/
  hooks/
    post-tool-use.sh      # NEW — tool invocation logger
    stop-summary.sh        # NEW — session summary writer
  adapters/claude-code/hooks/
    hooks.json             # NEW — declares PostToolUse + Stop

Agent-Drift/
  hooks/
    pre-tool-use-guard.sh  # NEW — governance file write guard
    session-start-drift.sh # NEW — CLAUDE.md structure checker
  adapters/claude-code/hooks/
    hooks.json             # NEW — declares PreToolUse + SessionStart

Agent-Scribe/
  hooks/
    load-context.sh        # EXISTS — extend with staleness check
    post-compact.sh        # NEW — context restoration after compression
  adapters/claude-code/hooks/
    hooks.json             # UPDATE — add PostCompact entry

Agent-PROVE/
  hooks/
    pre-commit-evidence.sh # NEW — test evidence gate
    stop-evidence-audit.sh # NEW — completion claim checker
  adapters/claude-code/hooks/
    hooks.json             # NEW — declares PreToolUse + Stop

Agent-Cite/
  hooks/
    post-tool-use-cite.sh  # NEW — source URL logger
  adapters/claude-code/hooks/
    hooks.json             # NEW — declares PostToolUse

Agent-Litmus/
  hooks/
    pre-tool-use-lint.sh   # NEW — convention validator
    stop-quality-gate.sh   # NEW — quality checklist
  adapters/claude-code/hooks/
    hooks.json             # NEW — declares PreToolUse + Stop
```

## Estimated Effort

| Phase | Plugins | Effort | Hooks Count |
|-------|---------|--------|-------------|
| P0 | Trace, Drift, Scribe | 1 week | 5 new + 1 update |
| P1 | PROVE, Cite | 1 week | 3 new |
| P2 | Litmus | 3-5 days | 2 new |
| **Total** | **6 plugins** | **~3 weeks** | **10 new + 1 update** |

## Acceptance Criteria

- [ ] Each plugin's `adapters/claude-code/hooks/hooks.json` updated with new hook declarations
- [ ] Each new hook shell script is executable, uses `set -e`, reads stdin JSON correctly
- [ ] Each new hook tested with a dry-run scenario (pipe sample JSON, verify output)
- [ ] Latency verified: no hook exceeds 500ms in testing
- [ ] README updated for each plugin documenting new hooks and their behavior
- [ ] No regression in Scribe's existing SessionStart hook (`load-context.sh`)
- [ ] Security: all hooks validate stdin JSON, sanitize paths, never eval tool output
- [ ] Each plugin's `package.json` version bumped (minor version increment)

## Dependencies

None. This is an upgrade to existing published plugins. The plugins are already on npm. New versions should be published after testing.

## Key Files to Read First

1. `CLAUDE.md` — agents-infra architecture, conventions, verdict taxonomy
2. `SOUL.md` — persona and domain principles
3. `Agent-Scribe/hooks/load-context.sh` — reference implementation for all new hooks
4. `Agent-Scribe/adapters/claude-code/hooks/hooks.json` — reference hook declaration format
5. `/tmp/scout_hooks.md` — technology scout report with full hooks API details
