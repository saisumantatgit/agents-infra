# TDR-001 Gate Evidence — graphify pilot

Recorded during execution, 2026-07-14. Companion to `../TDR-001-graphify-pilot.md` and CR-001.

## Gate 0 — Provenance & install surface

- **Repo transferred:** `safishamsi/graphify` → `Graphify-Labs/graphify` (GitHub 301, repository id 1200597263). Individual → org, created 2026-04-03, 85,369 stars / 8,424 forks as of today, last push 2026-07-13, default branch `v8`.
- **SHA pinned:** `961b78e57a10e9c5bb98421ff3e45b40be73542b` (2026-07-13 18:49:25 +0100, author safishamsi).
- **PyPI provenance:** package `graphifyy` v0.9.15; `project_urls` point to `github.com/safishamsi/graphify` (redirects to canonical org repo); version matches repo `pyproject.toml` (0.9.15). Names consistent — the double-y is the official package name, not a squat. Residual risk: sdist↔repo byte-level diff not performed (noted in CR).
- **Install surface (`graphify install claude`):** copies `SKILL.md` → `~/.claude/skills/graphify/` (or `<project>/.claude/skills/graphify/` with `--project`); appends a registration block to `~/.claude/CLAUDE.md` (global mutation — pilot uses `--project` scope to avoid it). No curl-pipe-bash, no post-install code execution.
- **Source sweep:** network code confined to `llm.py` (explicit backends), `security.py` (SSRF-guarded fetch for `/graphify add <url>`, opt-in), `serve.py` (MCP server, opt-in), `google_workspace.py`/`transcribe.py`/`wiki.py` (feature-gated). No telemetry: `querylog.py` states no-telemetry posture, OFF unless enabled; no analytics/sentry/posthog imports. Git hooks (`hooks.py`) are opt-in via `graphify hook install`. `__main__.py` has no startup update-check.
- **Verdict: Gate 0 PASS** — install surface matches stated scope.

## Gate 1 — Invocation mode & egress (evidence below added during Gate 1 run)

- **Mode CONFIRMED from source (`graphify/skill.md`, shipped skill):** ships as an AI-assistant skill (`/graphify .`). Code files: tree-sitter AST extraction, fully local, no LLM. Semantic pass (docs/papers/images only): "the host agent itself is the LLM" — host dispatches in-session subagents (general-purpose) that write chunk JSONs. No API key read for Anthropic; skill explicitly forbids prompting for one.
- **⚠ Environment-conditional egress path (found in Gate 0, verified in skill.md Step 3):** if `GEMINI_API_KEY` or `GOOGLE_API_KEY` is set, graphify routes semantic extraction to `generativelanguage.googleapis.com` instead of the host session — silently (one tip line, no consent gate). **`GEMINI_API_KEY` IS SET on this machine.** Pilot runs with the key explicitly unset for every graphify invocation. For iVal: this is a standing footgun — any operator machine with a Gemini key set would send payroll-doc content to Google. Mitigation required before iVal use (unset in wrapper, or `GRAPHIFY_*` guard).
- **Observed egress evidence (toy repo, 4 files, 2026-07-14):**
  1. **Deny-test:** full local pipeline (detect → AST extract → build → cluster → export) run under `sandbox-exec -p '(version 1)(allow default)(deny network*)'` with `env -u GEMINI_API_KEY -u GOOGLE_API_KEY` — completed successfully in 2.24s. The pipeline requires zero network.
  2. **Socket observation:** same pipeline unrestricted, `lsof -a -p <pid> -i` polled 40× at 100ms — **zero sockets opened** for the process lifetime.
  3. Semantic pass in skill mode dispatches host-session subagents — egress is session traffic to `api.anthropic.com` by construction (already-accepted exposure); graphify's own code performs no LLM network calls in this mode.
- **Verdict: Gate 1 PASS (in pilot mode: Gemini keys unset).** iVal contingency: PASS **with mandatory guard** — any wrapper/runbook for iVal must unset `GEMINI_API_KEY`/`GOOGLE_API_KEY` (or gate on their absence), else doc content silently routes to Google.
