# Handoff: Hook Lint — Drift Subcommand

**From:** Config Management HQ
**Date:** 2026-03-29
**Priority:** Medium (backlog — build after Drift MVP exists)
**Source:** INS-005 in HQ insights log (hook pipeline race condition fix)

---

## Context

A race condition was discovered in HQ's PreCompact/PostCompact hook pipeline. PreCompact asked Claude to write a file, but hooks are fire-and-forget shell commands — the model gets no execution turn between pipeline stages. The file was never written. PostCompact always fell through to its fallback.

This is a general class of bug in hook-based governance: **pipeline stages that silently depend on actor coordination that can't happen.**

## Proposal

Add a `hook-lint` subcommand to **Drift** (config drift detection). Static analysis of hook configurations to catch:

| Bug Class | Detection Method | Example |
|-----------|-----------------|---------|
| **Race condition** | Hook outputs instructions to model ("IMPORTANT: write/do/create") but no stage writes the artifact mechanically | PreCompact asks Claude to write session-summary.md — impossible |
| **Missing file dependency** | Stage reads a file (`cat`, `[ -f ]`) that no prior stage writes | PostCompact reads session-summary.md but nothing creates it |
| **Dead output** | Hook echoes instructions nobody can act on | Notification to void |
| **Ordering violation** | Stage depends on state from a later stage | PreToolUse depends on PostToolUse output |

## Input

```bash
# Parse hook config from settings.json
agents-infra drift hook-lint ~/.claude/settings.json

# Or point at a hooks directory
agents-infra drift hook-lint ~/.claude/hooks/
```

## Analysis Approach

For each hook shell script:
1. Extract **file writes** (`>`, `>>`, `tee`) — these are outputs
2. Extract **file reads** (`cat`, `[ -f ]`, `source`, `.`) — these are inputs
3. Extract **model instructions** (echo patterns containing imperative verbs: "write", "create", "update", "save") — these are unenforceable
4. Map the pipeline order (PreCompact → Compaction → PostCompact; PreToolUse → Tool → PostToolUse)
5. Verify: every file read has a file write in a prior stage
6. Flag: any instruction to the model between stages (can't be enforced)

## Output Format

```
PASS: PostCompact reads ~/.claude/session-summary.md — PreCompact writes it (line 60)
WARN: PreCompact outputs "write your session state" (line 9) — model cannot act between stages
FAIL: PostCompact reads config.cache but no prior stage creates it
INFO: 3 hooks analyzed, 1 warning, 0 failures
```

## Why Drift (not standalone)

- Drift already analyzes configuration files for correctness
- Hook lint is configuration validation — same domain
- Too narrow for its own CLI tool (would be a 200-line analyzer)
- If it generalizes to CI pipelines / agent orchestration chains later, extract to standalone

## Action Items

- [ ] Add to Drift backlog (after Drift MVP)
- [ ] Design the shell script parser (regex-based is sufficient — hooks are simple bash)
- [ ] Consider: should this also lint GitHub Actions workflows? (same pipeline-stage pattern)
- [ ] Reference: INS-005 in HQ `docs/insights/insights-log.md` for the full race condition analysis

## Cross-Domain Applicability

The same pattern appears in:
- **CI/CD pipelines:** Stages that depend on human approval without an explicit gate
- **Unix pipes:** Each stage must be self-contained (read stdin, write stdout)
- **Middleware chains:** Express/Koa `next()` — can't pause for external input mid-chain
- **Agent orchestration:** Any multi-agent pipeline where Agent B depends on Agent A acting on a side-channel instruction

If hook-lint proves useful, the analyzer generalizes to a **Pipeline Lint** tool for any sequential stage-based system.
