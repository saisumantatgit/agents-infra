# PIR-001: 17 Bugs Shipped to GitHub Untested

## Metadata

| Field | Value |
|-------|-------|
| **PIR ID** | PIR-001 |
| **Date** | 2026-03-20 |
| **Severity** | P2 (Medium — partial failure, no functional impact, workaround exists) |
| **Status** | Final |
| **Incident date** | 2026-03-20 (prior session — build session) |
| **Detection date** | 2026-03-20 (this session — test session) |
| **Resolution date** | 2026-03-20 (same session — fix + push) |

## Zone Check

| Dimension | Status | Notes |
|-----------|--------|-------|
| **Severity** | :yellow_circle: P2 | No functional bugs. All metadata/consistency issues. |
| **Containment** | :green_circle: Contained | All 15 fixable bugs remediated and pushed. |
| **Blast Radius** | Low | No user-facing impact. Products functioned correctly despite bugs. |

## 1. Summary

17 bugs were shipped to GitHub across 9 products during a single high-velocity build session. None were functional — all were metadata inconsistencies, stale references, orphan files, or structural gaps. The bugs went undetected because the session prioritized building and shipping over testing. A comprehensive test plan existed by session end but was never executed. Detection occurred in the next session via a 304-test sweep. All fixable bugs were resolved within 25 minutes.

## 2. Timeline

| Time | Event | Actor |
|------|-------|-------|
| 2026-03-20 (prior session) | 9 products built and pushed to GitHub | Agent + Human |
| 2026-03-20 (prior session) | TEST_PLAN_v1.md written (304 tests designed) | Agent |
| 2026-03-20 (prior session) | Session ends WITHOUT executing the test plan | Human (session fatigue) |
| 2026-03-20 (this session) | "Shall we resume" — testing identified as top priority | Human |
| 2026-03-20 (this session) | 9 QA agents dispatched, 17 bugs found | Agent |
| 2026-03-20 (this session) | 7 fix agents dispatched, 15 bugs fixed | Agent |
| 2026-03-20 (this session) | 7 repos pushed clean to GitHub | Agent |

## 3. Five Whys

1. **Why were 17 bugs shipped?** — Because 9 products were pushed to GitHub without running the test plan.

2. **Why wasn't the test plan executed?** — Because the build session ran long (~9 hours, 460+ files, 30K+ lines) and the test plan was written at the very end as a "next session" item.

3. **Why was testing deferred to the next session?** — Because the session's momentum was heavily weighted toward shipping. Each product build generated excitement for the next one (Cite → Drift → Litmus → ml-preflight variants). Testing felt like a brake on that momentum.

4. **Why was there no quality gate before `git push`?** — Because the workflow had no mandatory pre-push verification step. The logbook handoff noted "TEST all 9 products" as the #1 next action, but there was no hook or process that prevented pushing untested work.

5. **Why?** → **ROOT CAUSE:** The build workflow lacked a mandatory quality gate between "build" and "push." Shipping velocity was treated as the primary metric, with testing documented as a deferred obligation rather than a blocking requirement.

## 4. Blast Radius

| Radius | Affected | How |
|--------|----------|-----|
| **Direct** | 7 GitHub repos | Inconsistent metadata, stale suite links, schema divergence |
| **Adjacent** | Anyone who cloned between build and fix sessions | Would encounter version mismatch (PROVE), wrong naming (Litmus), missing files (Scribe) |
| **Downstream** | None | No downstream consumers yet — products are pre-promotion |
| **Potential (if undetected)** | Suite credibility | A governance tool suite with inconsistencies in its own governance artifacts would undermine trust |

## 5. Prompt Forensics

### Triggering input
The build session was a single, escalating conversation: "Build Agent-Shield" → brand evaluation → 4 new products → 3 ML-Ops products. Each product build was prompted individually, but there was no "stop and verify" checkpoint.

### Expected vs actual
- **Expected**: Build → Test → Fix → Push (for each product)
- **Actual**: Build → Push → Build → Push → ... → Write test plan → End session

The inversion of test-then-push to push-then-test-later was the core process failure.

## 6. What Went Well

1. **The test plan was written** — Even though it wasn't executed, the prior session produced a comprehensive 700-line test plan with numbered items, expected results, and known issues. This made the fix session highly efficient.
2. **Bug severity was low** — All 17 bugs were metadata/consistency issues. Zero functional bugs. Every command worked, every script compiled, every prompt was correctly structured.
3. **Detection-to-resolution was fast** — From "shall we resume" to "all pushed" was under 80 minutes, including drafting the AAR and PIR.
4. **The parallel agent model scaled** — 9 test agents + 7 fix agents = 16 parallel workers. No conflicts, no coordination overhead.

## 7. What Went Wrong

1. **No pre-push quality gate** — The workflow allows `git push` without any verification step. A pre-push hook or checklist would have caught at least the version mismatch (ERROR) and the schema divergence (ERROR).
2. **Consistency wasn't checked during build** — Each product was built independently. The "use Litmus as the template" pattern only emerged by the 6th product. Earlier products (Scribe, Trace) were built with less mature templates.
3. **Session fatigue drove deferred testing** — A 9-product, 460-file, 30K-line session is too much for a single pass without quality checkpoints.

## 8. Where We Got Lucky

1. **No users yet** — The suite is pre-promotion. If these repos had active users, the inconsistencies would have been visible on day one. The window between incident and fix was hours, not days.
2. **All bugs were cosmetic** — The build quality of the actual prompts, commands, skills, agents, scripts, and templates was high. The bugs were all in the wrapper layer (package.json, plugin.json, hooks.json, README badges, suite sections).
3. **The test plan existed** — If the prior session had ended without writing TEST_PLAN_v1.md, this session would have started with "what do we test?" instead of "execute the plan." The plan saved ~2 hours of test design work.

## 9. Remediation

### Immediate fix
- Executed 304-test sweep across all 9 products
- Fixed 15 of 17 bugs (2 intentionally skipped: historical logbook reference, PROVE's deliberate no-installer design)
- Pushed 7 repos clean to GitHub

### Permanent fix
- **Quality gate rule**: No `git push` without evidence of testing. Add to `CLAUDE.md` session hygiene checklist.
- **Template-first building**: When building new suite products, always start from the most recent product's structure (currently Litmus) to inherit consistency.
- **Cross-suite smoke test**: After any product build, run a 10-item cross-suite consistency check (naming, versioning, schema, suite links, structural files) before pushing.

### Detection improvement
- **TEST_PLAN_v2**: Move cross-suite tests to Wave 0 (run first, not last). Add universal `__pycache__` check across all products with Python scripts.
- **Pre-push validation script**: Consider a `scripts/validate-suite.sh` that checks cross-product consistency (version sync, naming, hooks schema) — runnable before any push.

## 10. Action Items

| # | Action | Priority | Owner | Due | Status |
|---|--------|----------|-------|-----|--------|
| 1 | Add "no push without test evidence" to agents-infra CLAUDE.md session hygiene | P1 | Agent | Next session | Open |
| 2 | Create `scripts/validate-suite.sh` for cross-product consistency checks | P2 | Agent | Next session | Open |
| 3 | Update TEST_PLAN to v2 with Wave 0 cross-suite and universal __pycache__ | P2 | Agent | Next session | Open |
| 4 | Adopt "template-first" rule: new products always clone from latest product | P2 | Human | Ongoing | Open |

## 11. Lessons Learned

1. **Velocity without verification is technical debt creation.** The prior session was the most productive ever (~460 files, 9 products), but it traded testing for speed. The debt was repaid quickly — but only because we caught it in the next session. Uncaught, it compounds.

2. **Consistency is a cross-cutting concern, not a per-product concern.** Testing each product independently got 91% pass rate. The failures were all in the spaces *between* products — naming conventions, schema formats, suite links. Cross-suite tests must be a first-class citizen, not an afterthought.

3. **The test plan is the most valuable artifact from a build session.** It outlives the session, enables parallel execution, and turns "we should test this" from a vague intention into an executable checklist. Write it during the build, not after.
