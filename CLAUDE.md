@SOUL.md

# Agents Infra

Six-product CLI plugin suite providing full-lifecycle governance for AI agent workflows.

## Architecture

Six independent plugins that compose but never couple:

```
Before execution:  Agent-PROVE   — Thinking validation (14 frameworks, evidence protocol)
                   Agent-Cite    — Evidence enforcement and citation auditing
During execution:  Agent-Trace   — Dependency-aware blast-radius mapping before edits
                   Agent-Drift   — Intent drift detection and correction
After execution:   Agent-Scribe  — Governance docs (logbook, AAR, PIR, ADR)
                   Agent-Litmus  — Test quality validation and mutation analysis
```

Each plugin follows a layered structure:
- **Prompts** (`prompts/`) — LLM-agnostic core logic, single source of truth
- **Adapters** (`adapters/`) — Platform-specific wrappers (Claude Code, Codex, Cursor, Aider, Generic)
- **Commands** — User-facing slash commands that invoke skills/prompts

PROVE adds: `agents/` (14 framework agents + 2 orchestrators), `skills/` (workflow logic)
Trace adds: `scripts/` (Python scripts for graph ops), `templates/` (curated overlay examples), `specs/` (locked schemas)
Scribe adds: `templates/` (AAR, PIR, ADR, Logbook), `hooks/` (load-context.sh session-start hook)
Cite adds: `evidence-protocol.yaml` (configurable rules), reference docs
Drift adds: `references/` (design references), `templates/` (drift-spec template)
Litmus adds: `references/` (violation taxonomy, mutation patterns), `templates/` (report template)

## Commands

**PROVE** (7): `/brainstorm`, `/validate`, `/consider`, `/think`, `/audit`, `/review`, `/frameworks`
**Scribe** (4 + hook): `/logbook`, `/draft-aar`, `/draft-pir`, `/draft-adr`, `load-context` (session-start)
**Trace** (4): `/trace`, `/map`, `/query`, `/validate-universe`
**Cite** (3): `/cite-audit`, `/cite-fix`, `/cite-report`
**Drift** (5): `/drift-lock`, `/drift-check`, `/drift-fence`, `/drift-status`, `/drift-report`
**Litmus** (5): `/litmus-scan`, `/litmus-edge`, `/litmus-strength`, `/litmus-fix`, `/litmus-report`

## Conventions

- **Independent installability** — Each product has its own `install.sh` or manual setup. Never assume all six are present in a target repo.
- **Prompts are canonical** — Adapter files wrap `prompts/`; never put logic in adapters. Edit prompts first, then update adapters.
- **Each product has its own repo** — This monorepo is the development workspace. Each sub-directory mirrors its standalone GitHub repo exactly.
- **Evidence protocol (PROVE/Cite)** — Every claim cites a source, every number has a derivation, zero uncited inference. Format: `[source: path:line]`, `[derived: computation]`, `[searched: paths]`.
- **Hybrid model (Trace)** — Machine-generated graph + human-curated overlays. Generated vs curated facts always distinguishable via `source` field.
- **Verdict taxonomy is fixed** — PROVE: VALIDATED/REJECTED, CYCLE_APPROVED/CYCLE_FAILED, PASS/FAIL. Cite: COMPLIANT/NON_COMPLIANT. Litmus: EFFECTIVE/WEAK/HOLLOW, STRONG/MODERATE/THEATER, PROTECTED/AT_RISK/EXPOSED. Drift: ON_TARGET/DRIFTING/OFF_COURSE. Do not invent new verdicts.
- **Platform adapters** — All six support Claude Code, Codex, Cursor. PROVE adds OpenCode, Gemini CLI. Scribe, Trace, Cite, Drift, Litmus add Aider.
- **MIT licensed** — All six products.

## Key Files

| Path | Purpose |
|------|---------|
| `SOUL.md` | Persona and domain principles for this repo |
| `Agent-PROVE/CLAUDE.md` | PROVE-specific architecture and protocols |
| `Agent-Trace/CLAUDE.md` | Trace-specific architecture and design decisions |
| `Agent-Cite/CLAUDE.md` | Cite-specific evidence protocol rules |
| `Agent-Drift/CLAUDE.md` | Drift-specific detection methodology |
| `Agent-Litmus/CLAUDE.md` | Litmus-specific test quality criteria |
| `Agent-PROVE/package.json` | PROVE npm metadata (no build scripts) |
| `Agent-Trace/package.json` | Trace npm metadata (no build scripts) |
| `Agent-Cite/package.json` | Cite npm metadata (no build scripts) |
| `Agent-Drift/package.json` | Drift npm metadata (no build scripts) |
| `Agent-Litmus/package.json` | Litmus npm metadata (no build scripts) |
| `Agent-Scribe/install.sh` | Scribe installer (detects CLI, copies adapters) |
| `Agent-Trace/install.sh` | Trace installer (detects CLI, copies scripts + adapters) |
| `Agent-Cite/install.sh` | Cite installer (detects CLI, copies adapters) |
| `Agent-Drift/install.sh` | Drift installer (detects CLI, copies adapters) |
| `Agent-Litmus/install.sh` | Litmus installer (detects CLI, copies adapters) |
| `Agent-PROVE/scripts/validate-structure.sh` | Validates PROVE directory structure |
| `Agent-Trace/scripts/*.py` | Python scripts: build_manifest, query_impact, validate_universe, check_query_schema, common |

## Gotchas

- **No build step** — These are prompt-based plugins, not compiled software. The `package.json` files contain metadata only (no `scripts` block). There are no `npm install`, `npm build`, or `npm test` commands.
- **Trace requires Python** — The `scripts/` directory contains Python files that get copied into target repos by `install.sh`. They must remain valid standalone Python.
- **Scribe has no CLAUDE.md** — Scribe is the simplest product (prompts + templates + adapters). Its README is the primary reference.
- **Sub-project CLAUDEs override this file** — When working inside a sub-project directory, its own CLAUDE.md takes precedence for product-specific rules.
- **Lineage matters for design decisions** — PROVE originated from ProSure Mission 1086. Trace originated from iVal 2.0's `agent-safe-remediation` research. Scribe was built from first principles (US Army AAR, Google SRE PIR, MADR v4.0.0). Cite was extracted from PROVE's evidence protocol. Drift and Litmus are novel designs.
- **install.sh is destructive** — Installers copy files into the target repo's working directory. They will overwrite existing files in `prompts/`, `.claude/commands/`, etc.
- **Shield renamed to Trace** — The original Agent-Shield was renamed to Agent-Trace. If you encounter "Shield" in older docs or lineage references, it refers to what is now Trace.
