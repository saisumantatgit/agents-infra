# Agents Infra

> **Think. Record. Shield.**
> A three-product suite of CLI plugins that make AI agents disciplined, accountable, and safe.

Each plugin owns exactly one capability gap in the AI agent workflow. Together, they form a complete governance layer that sits between the agent and the codebase.

---

## The Suite

```
Before execution:    Agent-PROVE   →  "Prove it or it fails."   (thinking validation)
During execution:    Agent-Shield  →  "Shield your code."       (dependency-aware remediation)
After execution:     Agent-Scribe  →  "Nothing is lost."        (governance documentation)
```

| Product | Version | What It Does | GitHub |
|---------|---------|-------------|--------|
| **[Agent-PROVE](Agent-PROVE/)** | v1.2.1 | 14 thinking frameworks, evidence protocol, agentic audit suite. Forces agents to validate approaches before execution. | [saisumantatgit/Agent-PROVE](https://github.com/saisumantatgit/Agent-PROVE) |
| **[Agent-Scribe](Agent-Scribe/)** | v1.0.0 | 4 governance commands (logbook, AAR, PIR, ADR) + session-start hook. Compounds learning across sessions. | [saisumantatgit/Agent-Scribe](https://github.com/saisumantatgit/Agent-Scribe) |
| **[Agent-Shield](Agent-Shield/)** | v1.0.0 | Dependency-aware remediation. Maps blast radius before edits, ties verification to impact surface. | [saisumantatgit/Agent-Shield](https://github.com/saisumantatgit/Agent-Shield) |

---

## Why Three Products, Not One?

Each plugin is **independently installable**. A team that only needs thinking frameworks doesn't get governance commands they won't use. A team that only needs blast-radius mapping doesn't get 14 frameworks they didn't ask for.

The plugins compose but don't couple:
- Use PROVE alone to validate approaches before coding
- Use Shield alone to map dependencies before editing
- Use Scribe alone to capture decisions and handoff context
- Use all three for full pre/during/post governance

---

## Competitive Positioning

No single competitor covers all three gaps. Each plugin occupies an unclaimed niche:

| Capability | Agent-PROVE | Agent-Scribe | Agent-Shield | Nearest Competitor |
|-----------|------------|-------------|-------------|-------------------|
| Multi-framework thinking | 14 frameworks, phase-aware | — | — | None (unique) |
| Evidence protocol enforcement | Zero tolerance for uncited claims | — | — | None (unique) |
| Session-to-session learning | — | Logbook + load-context hook | — | claude-mem (memory only, no governance) |
| Blameless post-incident reviews | — | PIR command (Five Whys) | — | None for AI agents |
| Dependency-aware blast radius | — | — | Repo universe + impact query | None for AI agents |
| Architecture decision records | — | ADR command (MADR v4.0.0) | — | Manual ADR templates |

### Ecosystem Context

| Plugin | What It Owns | Stars |
|--------|-------------|-------|
| Superpowers | Developer discipline — TDD, code review | 95K+ |
| BMAD | Agile lifecycle — personas, phase gates | 41K+ |
| GSD | Context engineering — fresh windows, wave execution | 34K+ |
| claude-mem | Persistent memory | 38K+ |
| **Agent-PROVE** | **Structured evidence-based thinking** | — |
| **Agent-Scribe** | **Governance documentation** | — |
| **Agent-Shield** | **Dependency-aware remediation** | — |

---

## Installation

Each product has its own installation instructions in its README. The general pattern:

```bash
# Clone the suite
git clone https://github.com/saisumantatgit/Agent-PROVE.git
git clone https://github.com/saisumantatgit/Agent-Scribe.git
git clone https://github.com/saisumantatgit/Agent-Shield.git

# Or install individually from any project directory
# See each product's README for platform-specific setup
```

### Platform Support

| Platform | PROVE | Scribe | Shield |
|----------|-------|--------|--------|
| Claude Code | Full | Full | Full |
| Codex | Full | Full | Full |
| Cursor | Full | Full | Full |
| Aider | — | Full | Full |
| OpenCode | Full | — | — |
| Gemini CLI | Full | — | — |

---

## Architecture

### How They Compose

```
Developer Request
    │
    ▼
┌─────────────────────────────────────────────┐
│  Agent-PROVE                                │
│  "Should we do this? How? What could fail?" │
│  /validate → /think → /audit                │
└─────────────────┬───────────────────────────┘
                  │ Approach validated
                  ▼
┌─────────────────────────────────────────────┐
│  Agent-Shield                               │
│  "What breaks if we touch this?"            │
│  /map → /query → /shield                    │
└─────────────────┬───────────────────────────┘
                  │ Blast radius acknowledged
                  ▼
┌─────────────────────────────────────────────┐
│  [ Agent executes the work ]                │
└─────────────────┬───────────────────────────┘
                  │ Work complete
                  ▼
┌─────────────────────────────────────────────┐
│  Agent-Scribe                               │
│  "What happened? What did we learn?"        │
│  /logbook → /draft-aar → /draft-adr         │
└─────────────────────────────────────────────┘
```

### Lineage

Agent-PROVE was extracted from Mission 1086 methodology (ProSure regulatory data classification). The structured thinking approach proved so effective that it was generalized into a standalone plugin.

Agent-Shield originated from `agent-safe-remediation` research conducted during the iVal 2.0 project (`~/vibe-coding/ival_2.0/research/agent-safe-remediation/`). The research was project-specific; Agent-Shield is the project-agnostic extraction. The original research artifacts remain in iVal 2.0 as the authoritative source material.

Agent-Scribe was built from first principles using US Army After Action Review methodology, Google SRE Post-Incident Review practices, MADR v4.0.0 for architecture decisions, and the engineering logbook tradition.

---

## Commands Quick Reference

### Agent-PROVE (7 commands)

| Command | Purpose |
|---------|---------|
| `/brainstorm` | Explore problem space with structured thinking |
| `/validate` | Validate approach before implementation |
| `/consider` | Apply a specific framework to a question |
| `/think` | Deep implementation validation with verification |
| `/audit` | Evidence audit of completed work |
| `/review` | Review against quality criteria |
| `/frameworks` | List all available frameworks |

### Agent-Scribe (4 commands + hook)

| Command | Purpose |
|---------|---------|
| `/logbook` | End-of-session capture (non-negotiable) |
| `/draft-aar` | After Action Review at milestones |
| `/draft-pir` | Post-Incident Review after failures |
| `/draft-adr` | Architecture Decision Record |
| `load-context` | Session-start hook (~100ms) |

### Agent-Shield (4 commands)

| Command | Purpose |
|---------|---------|
| `/shield` | Full 7-step safe remediation workflow |
| `/map` | Build or refresh the repo universe manifest |
| `/query` | Query impact of a proposed change |
| `/validate-universe` | Validate manifest freshness and accuracy |

---

## Repository Structure

```
agents-infra/
├── Agent-PROVE/          # Thinking framework orchestrator
│   ├── README.md         # Full documentation
│   ├── agents/           # 14 framework agents + 2 orchestrators
│   ├── commands/         # 7 slash commands
│   ├── skills/           # 6 skills
│   ├── prompts/          # LLM-agnostic core prompts
│   ├── adapters/         # Platform configs (5 platforms)
│   ├── docs/             # ADRs, research
│   └── LICENSE
├── Agent-Scribe/         # Governance documentation toolkit
│   ├── README.md         # Full documentation
│   ├── prompts/          # 4 command prompts
│   ├── templates/        # AAR, PIR, ADR, Logbook templates
│   ├── adapters/         # CLI adapters (5 CLIs)
│   ├── hooks/            # load-context.sh
│   └── LICENSE
├── Agent-Shield/         # Dependency-aware remediation
│   ├── README.md         # Full documentation
│   ├── commands/         # 4 slash commands
│   ├── agents/           # 3 agents
│   ├── skills/           # safe-remediation skill
│   ├── scripts/          # 5 Python scripts
│   ├── prompts/          # LLM-agnostic core prompts
│   ├── adapters/         # Platform configs (5 CLIs)
│   ├── templates/        # Curated overlay templates
│   ├── specs/            # Schema and contract specs
│   ├── references/       # Design references
│   └── LICENSE
└── README.md             # This file
```

---

## License

All three products are MIT licensed. See individual `LICENSE` files.

## Author

**Sai Sumanth Battepati** — [github.com/saisumantatgit](https://github.com/saisumantatgit)
