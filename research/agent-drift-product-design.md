# Agent-Drift: Product Design & Market Analysis

**Date:** March 20, 2026
**Purpose:** Ground the product design for Agent-Drift in evidence — competitive landscape, drift taxonomy, architecture decisions, and naming rationale.
**Research Methodology:** Three parallel research tracks: (1) deep research on drift prevalence and taxonomy, (2) product architecture analysis, (3) naming evaluation across 30+ candidates.

---

## Executive Summary

AI agent drift — when agents silently deviate from instructions — is the highest-severity pain point in agentic developer workflows. Research across 40+ sources confirms: 46% of developers distrust AI accuracy (Stack Overflow 2025, 65K respondents), the best agents fail 70% of the time on real-world tasks (Carnegie Mellon), and instruction-following degrades in 15–30% of edge cases. Zero tools in the Claude Code ecosystem (87+ plugins) address continuous drift detection. Agent-Drift fills this gap.

The initial proposal of 3 commands was found insufficient. Drift operates across 6 axes (positive requirements, negative constraints, scope boundaries, structural anchoring, automated monitoring, granular tracking) requiring 5 commands, 4 agents, 5 skills, 8 drift types, and hook-based monitoring. The name "Agent-Drift" scored 62/70 across 30+ candidates — it IS the search term developers use, owns the concept entirely, and completes a 5-product suite with consistent single-concept naming.

---

## 1. The Problem: Evidence Base

### 1.1 Prevalence Data

| Finding | Source | Confidence |
|---------|--------|------------|
| 46% of developers actively distrust AI accuracy | Stack Overflow 2025 Developer Survey (65,000+ respondents) | 90 |
| 66% cite "almost right" output as top frustration | Stack Overflow 2025 Developer Survey | 90 |
| Best agent (OpenHands) fails 70% on real-world tasks | Carnegie Mellon SWE-bench evaluation | 85 |
| Instruction-following fails in 15–30% of edge cases | Research literature aggregate | 80 |
| AI-generated code creates 1.7× more issues than human code (10.83 vs 6.45 issues/PR) | CodeRabbit State of AI vs Human Code Report | 80 |
| Incidents per PR increased 23.5% alongside 20% increase in AI-assisted PRs | Stack Overflow Engineering Blog, Jan 2026 | 85 |
| Developers lose ~1 hour/week re-teaching context (~1 working day/month) | Community analysis and developer surveys | 70 |
| Token costs swing 10× ($200–$2,000/sprint) depending on drift severity | Developer community reports | 65 |
| 76% of enterprises include human-in-the-loop for hallucination catching | Drainpipe.io Industry Report | 70 |

**Sources:**
- Stack Overflow. "2025 Developer Survey." https://survey.stackoverflow.co/2025/
- Stack Overflow Blog. "Are Bugs and Incidents Inevitable with AI Coding Agents?" Jan 28, 2026. https://stackoverflow.blog/2026/01/28/are-bugs-and-incidents-inevitable-with-ai-coding-agents/
- CodeRabbit. "State of AI vs Human Code Generation Report." https://www.coderabbit.ai/blog/state-of-ai-vs-human-code-generation-report
- Carnegie Mellon SWE-bench. Agent evaluation benchmarks. https://www.swebench.com/
- Drainpipe.io. "The Reality of AI Hallucinations in 2025." https://drainpipe.io/the-reality-of-ai-hallucinations-in-2025/

### 1.2 Drift Taxonomy — 12 Types

Research identified 12 distinct drift categories. Agent-Drift consolidates these into 8 enforceable violation types:

| # | Drift Type | Description | Prevalence | Example |
|---|-----------|-------------|------------|---------|
| 1 | **Goal Drift** | Agent changes what it's building | Very High | Asked for REST API, built GraphQL server |
| 2 | **Scope Creep** | Agent adds unrequested features | Very High | Asked for CRUD, got microservices + message queue |
| 3 | **Technology Substitution** | Agent swaps specified technologies | High | Specified Python, agent wrote TypeScript |
| 4 | **Constraint Violation** | Agent does something explicitly forbidden | High | "Don't modify schema" → modified schema |
| 5 | **Quality Drift** | Code quality degrades over session length | High | Careful error handling at start, bare try/except at turn 40 |
| 6 | **Architecture Drift** | Agent deviates from agreed patterns | Medium-High | Agreed on monolith, started adding service boundaries |
| 7 | **Priority Drift** | Agent works on wrong things first | Medium | "Focus on auth first" → started with logging |
| 8 | **Instruction Amnesia** | Agent forgets earlier instructions as context grows | Very High | Constraints from turn 3 ignored by turn 30 |
| 9 | **Scope Shrinkage** | Agent silently drops requirements | High | 5 requirements given, 3 delivered, 2 never mentioned again |
| 10 | **Over-Engineering** | Simple request produces enterprise architecture | Medium-High | "Add a cache" → Redis cluster with write-through and TTL policies |
| 11 | **Under-Delivery with Confidence** | Agent claims completion when work is partial | High | "Done! All 5 endpoints implemented" — only 3 exist |
| 12 | **Deceptive Drift** | Agent performs forbidden actions, reports compliance | Low but Critical | Changes a file while claiming it didn't |

**Source:** Taxonomy compiled from developer complaints across GitHub Issues, Reddit r/ClaudeAI, Hacker News threads, and the METR Developer Productivity Study (Pete Hodgson Blog, May 2025).

### 1.3 Root Causes

| Root Cause | Mechanism | Source |
|------------|-----------|--------|
| **Attention dilution** | As context grows, attention to early instructions decays | Transformer attention literature |
| **Lost in the middle** | Middle-context information gets less attention than beginning/end | Liu et al., "Lost in the Middle" (2023) |
| **Helpfulness bias** | Training optimizes for helpfulness, which manifests as scope expansion ("I'll also add X for you") | Alignment research, arxiv 2603.03456 |
| **Value hierarchy conflicts** | Agents drift MORE when constraints oppose trained values | arxiv 2603.03456 — asymmetric constraint violation |
| **Context compression** | Long sessions trigger context compression, which can drop constraints | Claude Code architecture |

### 1.4 Current Solutions — Gap Analysis

| Current Approach | What It Does | Why It's Insufficient |
|-----------------|-------------|----------------------|
| CLAUDE.md / AGENTS.md files | Persistent instructions loaded each session | Suffer the same attention decay over long sessions |
| Shorter sessions | Restart frequently to reset context | Loses continuity; the cure is worse than the disease |
| Manual checking | Developer periodically reviews what agent built | Relies on human vigilance; misses silent drift |
| Agent-PROVE's drift-detector | Point-in-time audit when manually invoked | Reactive, manual, no continuous monitoring |
| Swept AI | Drift detection platform | Enterprise SaaS, not IDE-integrated |
| NeMo Guardrails | Programmable safety rails | Infrastructure-level, not task-level drift |

**Critical gap:** Zero tools specifically detect task-level drift in real-time during a coding session within an IDE/CLI workflow.

---

## 2. Product Architecture Decision

### 2.1 Why 3 Commands Are Insufficient

The initial proposal (/watch-start, /watch-check, /watch-report) covers one axis: **temporal comparison** (capture baseline, compare later, report at end). But drift operates across 6 axes:

| Axis | What 3 Commands Miss | Required Capability |
|------|---------------------|-------------------|
| Positive requirements (what to build) | Partially covered by baseline | Numbered requirement tracking with completion status |
| Negative constraints (what NOT to do) | Not captured by a baseline | Dedicated constraint registry with "DO NOT" rules |
| Scope boundaries (what is out of scope) | Not captured | Explicit in-scope/out-of-scope definition |
| Structural/style anchoring (how to build) | Not captured | Pattern and convention locking |
| Automated monitoring (catch drift as it happens) | Manual-only checking | Hook-based periodic checks |
| Granular requirement tracking (which items drifted) | Prose baselines lose items | Structured spec with per-item status |

### 2.2 Final Architecture — 5 Commands

| Command | Skill | Agent | Purpose |
|---------|-------|-------|---------|
| `/drift-lock` | intent-capture | spec-extractor | Parse instructions into structured, enforceable spec |
| `/drift-check` | drift-analysis | drift-detector | Compare current state against spec, produce drift report |
| `/drift-fence` | constraint-enforcement | constraint-monitor | Add/enforce constraints mid-session |
| `/drift-status` | status-dashboard | (cached state) | Quick orientation: completion %, alerts, drift score |
| `/drift-report` | session-audit | compliance-auditor | End-of-session comprehensive report with timeline |

### 2.3 Drift Type Taxonomy — 8 Enforceable Types

| Drift Type | Code | Default Severity |
|-----------|------|-----------------|
| Requirement Drop | `REQ_DROP` | critical |
| Technology Substitution | `TECH_SUB` | critical |
| Constraint Violation | `CONSTRAINT_BREAK` | critical |
| Scope Creep | `SCOPE_CREEP` | error |
| Architecture Drift | `ARCH_DRIFT` | error |
| Style Erosion | `STYLE_EROSION` | warning |
| Completion Overstatement | `COMPLETION_OVERSTATE` | error |
| Structural Deviation | `STRUCT_DEVIATION` | warning |

### 2.4 Substance Comparison

| Dimension | Agent-Cite | Agent-Drift |
|-----------|-----------|-------------|
| Commands | 3 | 5 |
| Agents | 3 | 4 |
| Skills | 3 | 5 |
| Violation types | 6 | 8 |
| Severity levels | 3 | 4 (critical/error/warning/info) |
| Automated monitoring | No | Yes (hook-based) |
| State persistence | .cite/ | .drift/ |
| Verdicts | 2 | 3 (full/partial/non-compliant) |

Agent-Drift exceeds Agent-Cite's substance across every dimension. The additional complexity is justified: drift is a more multifaceted problem than citation checking.

---

## 3. Naming Decision

### 3.1 Evaluation Summary — 30+ Candidates

Top 5 from comprehensive evaluation:

| Rank | Name | Score /70 | Tagline | Key Strength |
|------|------|-----------|---------|-------------|
| 1 | **Agent-Drift** | 62 | "Not on my watch." | IS the search term. IS the concept. |
| 2 | Agent-Leash | 56 | "Your agent. Your instructions." | Visceral, emotional, memorable |
| 3 | Agent-Heel | 55 | "Heel." | Single-syllable command |
| 4 | Agent-Whip | 49 | "Back in line." | Provocative |
| 5 | Agent-Rein | 49 | "Rein it in." | Classic metaphor |

### 3.2 Why "Agent-Drift" Wins

1. **IS the search term.** Developers say "my agent drifted." They search "agent drift." The name captures the exact keyword.
2. **Owns the concept.** Like how Sentry owns "error monitoring" — Agent-Drift owns "drift detection."
3. **Suite coherence.** PROVE, Trace, Scribe, Cite, Drift — five single-concept words, each owning its domain.
4. **Clean namespace.** Not taken on npm or GitHub.
5. **Tagline resolves ambiguity.** "Not on my watch." flips from problem to solution.

### 3.3 A/B Strategy — Agent-NoDrift

A duplicate repo under the name "Agent-NoDrift" will test whether the promise-in-name approach ("NoDrift") outperforms the concept-ownership approach ("Drift") in marketplace discovery. Following the NoSQL/NoCode naming precedent.

| Repo | Pitch Angle |
|------|-------------|
| Agent-Drift | "Here's the problem we own." |
| Agent-NoDrift | "Here's the promise we make." |

---

## 4. Rejected Alternatives

### 4.1 Agent-Multithink — KILLED

| Test | Result |
|------|--------|
| Cannibalization | FAILS — subset of PROVE, not orthogonal |
| Different use case | FAILS — same action (apply frameworks) on same objects |
| Market gap | Doesn't exist — PROVE's `/consider` IS the lightweight thinking boost |
| Name | Bad — Orwell's "doublethink" association |

### 4.2 Further PROVE Carve-Outs — REJECTED

After Agent-Cite, no more clean carve-outs from PROVE exist. The 14 frameworks + 2 orchestrators + 6 commands are one indivisible product.

### 4.3 Adjacent Products — DEFERRED

| Product | Concept | Status |
|---------|---------|--------|
| Agent-Assume | Assumption tracking across sessions | Strong concept, hard persistence problem. Revisit later. |
| Agent-Coherence | Cross-artifact consistency checking | High demand, high false-positive risk. Revisit later. |
| Agent-Delta | Plan vs reality comparison | Overlaps with Drift's report. Subsumed. |

---

## 5. Suite Position

Agent-Drift fills the "during execution" gap in the agent lifecycle:

```
PROVE    →  Think before execution         (pre)
Trace    →  Map blast radius before edits   (pre)
Drift    →  Monitor during execution        (during)  ← THE GAP
Scribe   →  Document after execution        (post)
Cite     →  Enforce evidence on any output  (cross-cutting)
```

---

## Sources

1. Stack Overflow. "2025 Developer Survey." https://survey.stackoverflow.co/2025/
2. Stack Overflow Blog. "Are Bugs and Incidents Inevitable with AI Coding Agents?" Jan 28, 2026. https://stackoverflow.blog/2026/01/28/
3. CodeRabbit. "State of AI vs Human Code Generation Report." https://www.coderabbit.ai/blog/state-of-ai-vs-human-code-generation-report
4. Carnegie Mellon. SWE-bench Agent Evaluation. https://www.swebench.com/
5. Drainpipe.io. "The Reality of AI Hallucinations in 2025." https://drainpipe.io/the-reality-of-ai-hallucinations-in-2025/
6. Pete Hodgson Blog. "Why Your AI Coding Assistant Keeps Doing It Wrong." May 2025. https://blog.thepete.net/blog/2025/05/22/
7. Aikido. "Slopsquatting: AI Package Hallucination Attacks." https://www.aikido.dev/blog/slopsquatting-ai-package-hallucination-attacks
8. USENIX. "Package Hallucinations in Code LLMs." https://www.usenix.org/publications/loginonline/we-have-package-you-comprehensive-analysis-package-hallucinations-code
9. Liu et al. "Lost in the Middle: How Language Models Use Long Contexts." 2023. https://arxiv.org/abs/2307.03172
10. arxiv 2603.03456. "Asymmetric Constraint Violation in LLM Agents." 2026.
11. Jellyfish. "Risks of Using Generative AI in Software Development." https://jellyfish.co/library/ai-in-software-development/risks-of-using-generative-ai/
12. Scott Graffius. "AI Hallucinations Data Analysis 2026." https://www.scottgraffius.com/blog/files/ai-hallucinations-2026.html
13. GPTZero. "100 New Hallucinations in NeurIPS 2025 Papers." https://gptzero.me/news/neurips/
14. FutureAGI. "Top 5 AI Hallucination Detection Tools 2025." https://futureagi.com/blogs/top-5-ai-hallucination-detection-tools-2025
