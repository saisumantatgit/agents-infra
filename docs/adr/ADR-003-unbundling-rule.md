# ADR-003: Unbundling Rule — Only Orthogonal Capabilities

**Status:** Accepted
**Date:** 2026-03-20
**Context:** Deciding which capabilities from Agent-PROVE can be extracted as standalone products.

## Decision

Only extract capabilities that serve a **genuinely different use case** than the parent product. Never extract subsets of the same use case.

## The Rule

A capability is extractable if and only if ALL of these are true:
1. It serves a different buyer persona than the parent
2. It has zero coupling to the parent's core layer (e.g., PROVE's framework agents)
3. The standalone version adds capabilities the parent doesn't have
4. It does not cannibalize the parent's headline feature
5. It can stand alone as a complete product (not a feature pretending)

## Context

Agent-PROVE (v1.2.1) bundles 14 thinking frameworks, 2 orchestrators, evidence auditing, 7 commands, and 6 skills. The question: what can be unbundled?

## Alternatives Considered

### Agent-Plan (extract /validate + 5 frameworks)
**Rejected.** Ships PROVE's headline feature. If Plan has the 5 best frameworks for free, the upgrade to PROVE is "pay for 9 more frameworks" — weak value proposition. Cannibalization score: HIGH.

### Agent-Lens (extract /consider + all 14 frameworks)
**Rejected.** Gives away PROVE's core IP. PROVE's only remaining value would be orchestration. Cannibalization score: VERY HIGH.

### Agent-Cite (extract evidence audit + add /cite-fix, /cite-report)
**Accepted.** Evidence enforcement is orthogonal to thinking validation. Different buyer persona (anyone who wants citation discipline, not just framework users). Zero coupling to framework layer. Adds /cite-fix and /cite-report that PROVE doesn't have. Cannibalization score: LOW.

### Agent-Multithink (lightweight framework access)
**Rejected.** PROVE's `/consider` command already IS the lightweight thinking boost. Same action, same objects, lesser version. Not a different product.

### Agent-ADR (extract /draft-adr from Scribe)
**Rejected.** Single command is a feature, not a product. Too thin to stand alone.

## Consequences

**Good:**
- Each standalone product has clear, defensible identity
- PROVE retains its core value (framework orchestration)
- Agent-Cite acts as top-of-funnel: users who value evidence rigor → discover PROVE

**Bad:**
- Limits the number of extractable products (most of PROVE is inseparable)
- Future product ideas must meet a high bar

**How to apply:** When evaluating any future standalone proposal, run it through the 5-criterion filter above. If ANY criterion fails, the proposal should be killed or redesigned until all pass.
