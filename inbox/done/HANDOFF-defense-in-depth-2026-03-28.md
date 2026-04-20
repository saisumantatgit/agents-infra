# Handoff: 4-Layer Defense-in-Depth Model for agents-infra

**Source:** Config Management HQ — gold nuggets from Owain Lewis video (2026-03-28)
**Priority:** High — validates and refines the agents-infra architecture
**Memory seed:** `project_defense_in_depth.md` already in this repo's Claude memory

---

## What This Is

A practitioner's 4-layer model for AI code review that maps directly to agents-infra's 6-plugin governance stack:

| Layer | What | agents-infra Plugin |
|-------|------|-------------------|
| 1. Hooks (pre-commit) | Automated linting, formatting, tests | Global hooks (ADR-008) |
| 2. Local AI Review | AI reviews AI in fresh context | PROVE (thinking) + Cite (evidence) |
| 3. CI Platform Review | Automated checks on every PR | Litmus (test quality) + Trace (blast radius) |
| 4. Human Review | Architecture, business logic, judgment | Scribe (governance docs for reviewers) |

## Action Items

- [ ] **PROVE + Litmus outputs must use severity grouping:** must-fix, should-fix, informational. Current verdict taxonomy (VALIDATED/REJECTED etc.) doesn't distinguish severity. Design a severity field alongside the existing verdicts.
- [ ] **Consider a `review.md` template:** A file that tells PROVE/Cite what project-specific concerns to focus on. Like CLAUDE.md but for review priorities. Research says: don't make it a separate file — add a `## Review` section to project CLAUDE.md instead.
- [ ] **Hook self-correction pattern:** PreToolUse hooks can return corrective suggestions (exit 0 + message) instead of just blocking (exit 2). PROVE could use this — instead of "REJECTED: weak thinking", return "SUGGESTION: consider these alternatives..." and let the agent self-correct.
- [ ] **Validate that Drift maps to Layer 2:** Drift detection (is the agent staying on task?) is conceptually a Layer 2 concern — runtime monitoring, not pre-commit. Confirm this mapping holds.

## Reference
- Video: Owain Lewis "How I Use AI To Review AI Code" — full nuggets in HQ `docs/research/gold-nuggets-code-review-agent-sdk-2026-03.md`
- Blueprint plugin (code review skill): https://github.com/owainlewis/blueprint/blob/main/skills/code-review/SKILL.md
- Anthropic security review action: https://github.com/anthropics/claude-code-security-review
