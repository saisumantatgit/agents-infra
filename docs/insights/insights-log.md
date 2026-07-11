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

### [2026-07-12] A verification gate's own test suite cannot measure its moat

**Category:** principle
**Source:** session observation (26-agent red-team sweep + hand reproduction)
**Products affected:** Assure (generalizes to any verification/safety gate)

**Insight:**
A gate's test suite encodes its authors' threat model, so it structurally cannot
find the attack the authors never imagined — it verifies that intended mechanisms
behave as intended, which is the authors agreeing with themselves. The moat's
*actual* boundary (as opposed to its advertised one) is found only by an outside
process with no stake in the gate being right: an adversary generating
unanticipated inputs, scored by the gate's own mechanical verdict. Corollary
("audit the article"): "**a** fabricated citation cannot pass" and "**no**
fabrication can pass" are different guarantees; products drift from the first to
the second in the pitch, never in the code. Write down the property the code
actually earns, in its exact words. Fix: the adversary belongs *in* the suite, as
a permanent strict-xfail-to-green tripwire, not as a one-off audit.

**Evidence:**
2026-07-12: 334 tests green throughout while a 12-class adversarial sweep found —
and hand-reproduction confirmed — 6 Error-B moat violations (`gate=PASS` on
unsupported claims). Two independent roots (score-bar dilution; per-claim
over-grounding), where the sweep's synthesis had claimed one — the contradiction
"it's all dilution" vs "two scored a clean 100 with empty appendix" located the
second root. Recorded as `tests/red_team_moat/` (6 strict xfail), AA-MOAT-001..006
in `docs/open-issues/`, ADR-005, CN-ADR005. Sibling to the load-bearing-assumption
rule and INS-098 (adversarial review finds the adjacent hole).

**Graduation target:**
- [ ] Root `CLAUDE.md` Conventions — candidate cross-cutting rule ("ship the
      adversary as a regression tripwire") after a second validating instance.

<!-- Graduated insights log:
     (record destination when an insight is promoted)
-->
