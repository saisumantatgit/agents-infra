# HANDOFF: Docker Audit Plugin Feasibility Assessment

**From:** Config Management HQ (session 2026-03-26)
**Date:** 2026-03-26
**Priority:** P2 (evaluate when planning next plugin)
**Action:** Assess whether HQ's docker-audit.sh script should become an agents-infra plugin

## Background

HQ built a Docker hygiene audit script (`~/vibe-coding/Agents/Claude/tools/docker-audit.sh`) that checks Dockerfiles and docker-compose files for 4 common mistakes:
1. Wrong layer order (COPY . . before dependency install)
2. Running as root (no USER before CMD)
3. Missing/inadequate health checks
4. Unpinned base images (mutable tags without @sha256: digest)

It was run across 6 projects — all passed on checks 1-3, all had unpinned base images (check 4). The script is ~150 lines of bash, pattern-matching only, no auto-fix.

## What to Evaluate

### 1. Fit with agents-infra architecture
- Does a Docker audit plugin align with the PROVE/Scribe/Trace/Cite/Drift/Litmus suite?
- The existing 6 plugins govern agent behavior. This would govern agent infrastructure. Is that scope expansion desirable?

### 2. Competitive landscape
- **Hadolint** — established Dockerfile linter (Haskell, 10K+ stars). Covers most of what docker-audit.sh does and more.
- **Docker Scout** — Docker's own vulnerability scanner. Built into Docker Desktop.
- **Trivy** — Aqua Security's scanner. Images + filesystems + IaC.
- **Dockle** — container image linter focused on CIS benchmarks.

**Key question:** Can agents-infra differentiate from these? Possible angle: "AI-agent-specific Docker auditing" — does your agent container run as root? Does your MCP server container pin images? Are agent sandboxes properly isolated? None of the above tools have agent-awareness.

### 3. Build effort
- Script → CLI plugin: add argument parsing, JSON output, configurable severity, tests (~2-3 days)
- Script → full plugin with auto-fix: add Dockerfile rewriting, compose patching, CI integration (~1-2 weeks)
- Script → marketplace-ready: add documentation, cross-platform testing, versioning, README (~additional 1 week)

### 4. Market signal
- Docker at 92% adoption among engineers
- "AI agent in container" is the 2026 deployment pattern (NanoClaw, ZeroClaw, OpenClaw all use Docker)
- Docker Sandboxes specifically targets AI agents
- Nobody is doing agent-specific container auditing

## The Script

Location: `~/vibe-coding/Agents/Claude/tools/docker-audit.sh`
Run: `bash <path> --all` (scans all projects) or `bash <path> <Dockerfile>`
Also audits docker-compose files for unpinned images.

## Recommendation from HQ

Evaluate, don't build yet. The competitive landscape (Hadolint, Scout, Trivy) is crowded for generic Docker linting. The differentiation opportunity is agent-specific auditing, which requires defining what "agent-specific" means for Docker containers. That definition work is more valuable than the code right now.

If the assessment is positive, the build order would be:
1. Define "agent-specific Docker checks" (what do PROVE/Scribe care about in containers?)
2. Extend docker-audit.sh with agent-aware checks
3. Package as agents-infra CLI plugin
4. Marketplace listing

## References
- HQ Tool: `~/vibe-coding/Agents/Claude/tools/docker-audit.sh`
- Video source: "Docker in 2026: What Changed (And What You're Still Doing Wrong)"
- Docker audit results: 6 Dockerfiles audited, 0 FAILs, 9 WARNINGs (all unpinned images)
- ADR-009: HQ Handoff Convention
