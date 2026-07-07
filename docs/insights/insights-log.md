# Insights Log — Agents Infra

> Cross-cutting observations captured during development. See TEMPLATE.md for entry format and graduation criteria.

---

### [2026-07-08] Citation regex silently rejects letter-suffixed source IDs

**Category:** gotcha
**Source:** session observation (α1 corpus build)
**Products affected:** Assure

**Insight:**
The claim-decomposition citation regex accepts only `[S\d+]`-shaped markers; a letter-suffixed ID like `[S12a]` is not matched, so the citation silently detaches and the claim is misclassified (e.g. NUMERIC/UNCITED from the bracket digits). A validation gate that silently narrows its input class is a fail-quiet seam in a fail-loud system.

**Evidence:**
α1 corpus build 2026-07-08: an early multi-source relational fixture using `[S12a]`/`[S12b]` lost its citations and misclassified; fixed by numeric-only IDs (see `docs/plans/reports/ALPHA1-EXECUTION-REPORT.md`). Case resolution applied; systemic fix (widen regex or fail loud on near-miss brackets) is an open item in the 2026-07-08 logbook.

**Graduation target:**
- [ ] Sub-project `CLAUDE.md` — if it is product-specific (Assure Gotchas, once the systemic fix lands or is ADR-rejected)

### [2026-07-08] Judgment-in-the-spec lets executors drop a tier without quality loss

**Category:** pattern
**Source:** session observation (Fable→Opus/Sonnet handoff)
**Products affected:** suite-wide (orchestration practice)

**Insight:**
When the spec carries the decisions (failure-mode taxonomy, invariants, escalation triggers, checkable exit criteria) and the executor carries only assembly + verification, agents one tier down produce discipline-conformant work on the first pass. The measurable tell: red-first tests actually proven red, and fail-loud catches surfaced instead of papered over.

**Evidence:**
2026-07-08 session: 4 parallel agents (2 Opus, 2 Sonnet) against Fable-authored specs; zero re-dispatches, zero refutations, 2 unsolicited fail-loud catches (missing `calibration-plan.md`; gitignored `.claude/skills/`). Telemetry in the 2026-07-08 logbook.

**Graduation target:**
- [ ] Root `CLAUDE.md` Conventions or Gotchas — if it is a cross-cutting rule (candidate for the global model-routing table's operating rules after a second validating session)

<!-- Graduated insights log:
     (record destination when an insight is promoted)
-->
