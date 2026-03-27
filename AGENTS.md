# AGENTS.md

## Commands
- Validate PROVE structure: `bash Agent-PROVE/scripts/validate-structure.sh`
- Install any plugin to a target repo: `bash Agent-<Name>/install.sh`
- Trace scripts require Python 3.12+: `python Agent-Trace/scripts/build_manifest.py`
- No build, test, or lint commands exist — this is a prompt-based plugin suite

## Architecture
Six independent CLI plugins for AI agent governance. Prompt-based (not compiled).

- `Agent-PROVE/` — Thinking validation (14 frameworks, evidence protocol)
- `Agent-Cite/` — Evidence enforcement and citation auditing
- `Agent-Trace/` — Dependency-aware blast-radius mapping (Python scripts)
- `Agent-Drift/` — Intent drift detection and correction
- `Agent-Scribe/` — Governance docs (logbook, AAR, PIR, ADR)
- `Agent-Litmus/` — Test quality validation and mutation analysis

Each plugin has:
- `prompts/` — LLM-agnostic core logic (canonical, single source of truth)
- `adapters/` — Platform wrappers (Claude Code, Codex, Cursor, Aider, Generic)
- `install.sh` — Copies files into target repo (destructive — overwrites existing)

## Boundaries
- Never put logic in adapters — adapters wrap `prompts/`, nothing more
- Never invent new verdict values — taxonomy is fixed (see CLAUDE.md Conventions)
- Never assume all six plugins are installed together — each is independently installable
- Trace `scripts/*.py` must remain valid standalone Python (no project-level imports)
- `install.sh` is destructive — it overwrites files in the target repo's working directory
- MIT licensed — all six products
