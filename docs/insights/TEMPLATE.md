# Insight Template

> One insight per entry. When an insight graduates, move it to the appropriate target and delete the entry here.

## Entry Format

```markdown
### [YYYY-MM-DD] Title

**Category:** architecture | convention | gotcha | pattern | anti-pattern
**Source:** session observation / code review / incident
**Products affected:** PROVE, Scribe, Trace, Cite, Drift, Litmus (list relevant ones)

**Insight:**
One to three sentences describing what was learned.

**Evidence:**
How this was discovered — file paths, error messages, or observed behavior.

**Graduation target:**
- [ ] Sub-project `docs/adr/` — if it is an architecture decision
- [ ] Root `CLAUDE.md` Conventions or Gotchas — if it is a cross-cutting rule
- [ ] Sub-project `CLAUDE.md` — if it is product-specific
- [ ] `SOUL.md` Anti-Patterns — if it is a recurring mistake
```

## Graduation Criteria

An insight graduates when:
1. It has been validated across at least two sessions or products.
2. The target location is identified (ADR, CLAUDE.md section, or SOUL.md).
3. The insight is rewritten in the voice of the target document and merged there.

Once graduated, delete the entry from the insights log and note the destination in a one-line comment at the bottom of the log.
