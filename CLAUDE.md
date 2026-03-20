# Agents Infra

Three-product CLI plugin suite providing pre/during/post governance for AI agent workflows.

## Architecture

Three independent plugins that compose but never couple:

```
Before execution:  Agent-PROVE   — Thinking validation (14 frameworks, evidence protocol)
During execution:  Agent-Shield  — Dependency-aware blast-radius mapping before edits
After execution:   Agent-Scribe  — Governance docs (logbook, AAR, PIR, ADR)
```

Each plugin follows a layered structure:
- **Prompts** (`prompts/`) — LLM-agnostic core logic, single source of truth
- **Adapters** (`adapters/`) — Platform-specific wrappers (Claude Code, Codex, Cursor, Aider, Generic)
- **Commands** — User-facing slash commands that invoke skills/prompts

PROVE adds: `agents/` (14 framework agents + 2 orchestrators), `skills/` (workflow logic)
Shield adds: `scripts/` (5 Python scripts for graph ops), `templates/` (curated overlay examples), `specs/` (locked schemas)
Scribe adds: `templates/` (AAR, PIR, ADR, Logbook), `hooks/` (load-context.sh session-start hook)

## Commands

**PROVE** (7): `/brainstorm`, `/validate`, `/consider`, `/think`, `/audit`, `/review`, `/frameworks`
**Scribe** (4 + hook): `/logbook`, `/draft-aar`, `/draft-pir`, `/draft-adr`, `load-context` (session-start)
**Shield** (4): `/shield`, `/map`, `/query`, `/validate-universe`

## Conventions

- **Independent installability** — Each product has its own `install.sh` (Scribe, Shield) or manual setup. Never assume all three are present in a target repo.
- **Prompts are canonical** — Adapter files wrap `prompts/`; never put logic in adapters. Edit prompts first, then update adapters.
- **Each product has its own repo** — This monorepo is the development workspace. Each sub-directory mirrors its standalone GitHub repo exactly.
- **Evidence protocol (PROVE)** — Every claim cites a source, every number has a derivation, zero uncited inference. Format: `[source: path:line]`, `[derived: computation]`, `[searched: paths]`.
- **Hybrid model (Shield)** — Machine-generated graph + human-curated overlays. Generated vs curated facts always distinguishable via `source` field.
- **Verdict taxonomy is fixed** — PROVE uses VALIDATED/REJECTED (T1), CYCLE_APPROVED/CYCLE_FAILED (Auditor), PASS/FAIL (framework agents). Do not invent new verdicts.
- **Platform adapters** — PROVE supports Claude Code, Codex, Cursor, OpenCode, Gemini CLI. Scribe supports Claude Code, Codex, Cursor, Aider. Shield supports Claude Code, Codex, Cursor, Aider.
- **MIT licensed** — All three products.

## Key Files

| Path | Purpose |
|------|---------|
| `Agent-PROVE/CLAUDE.md` | PROVE-specific architecture and protocols |
| `Agent-Shield/CLAUDE.md` | Shield-specific architecture and design decisions |
| `Agent-PROVE/package.json` | PROVE npm metadata (no build scripts) |
| `Agent-Shield/package.json` | Shield npm metadata (no build scripts) |
| `Agent-Scribe/install.sh` | Scribe installer (detects CLI, copies adapters) |
| `Agent-Shield/install.sh` | Shield installer (detects CLI, copies scripts + adapters) |
| `Agent-PROVE/scripts/validate-structure.sh` | Validates PROVE directory structure |
| `Agent-Shield/scripts/*.py` | Python scripts: build_manifest, query_impact, validate_universe, check_query_schema, common |

## Gotchas

- **No build step** — These are prompt-based plugins, not compiled software. The `package.json` files contain metadata only (no `scripts` block). There are no `npm install`, `npm build`, or `npm test` commands.
- **Shield requires Python** — The `scripts/` directory contains Python files that get copied into target repos by `install.sh`. They must remain valid standalone Python.
- **Scribe has no CLAUDE.md** — Scribe is the simplest product (prompts + templates + adapters). Its README is the primary reference.
- **Sub-project CLAUDEs override this file** — When working inside `Agent-PROVE/` or `Agent-Shield/`, their own CLAUDE.md files take precedence for product-specific rules.
- **Lineage matters for design decisions** — PROVE originated from ProSure Mission 1086. Shield originated from iVal 2.0's `agent-safe-remediation` research. Scribe was built from first principles (US Army AAR, Google SRE PIR, MADR v4.0.0).
- **install.sh is destructive** — Both installers copy files into the target repo's working directory. They will overwrite existing files in `prompts/`, `.claude/commands/`, etc.
