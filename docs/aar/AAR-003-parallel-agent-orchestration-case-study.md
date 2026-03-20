# AAR-003: Parallel Agent Orchestration at Scale — A Case Study

## Metadata

| Field | Value |
|-------|-------|
| **AAR ID** | AAR-003 |
| **Date** | 2026-03-20 |
| **Milestone** | Full lifecycle quality gate — test, review, remediate, govern — across 9 products |
| **Duration** | ~3 hours (Sessions 2 + 3 combined) |
| **Agents dispatched** | 37+ parallel agents across 5 waves |
| **Products covered** | 9 (6 Agent Suite + 3 ML-Ops) |
| **Findings** | 114 code findings fixed, 9 PIRs written, 2 products APPROVED on second review |

---

## Executive Summary

A single human operator and one AI orchestrator executed a full quality lifecycle — structural testing, code review, remediation, governance documentation, and re-review — across a 9-product software suite in under 3 hours. The work involved 37+ parallel agent dispatches across 5 waves, producing 304 test executions, 114 bug fixes, 9 Post-Incident Reviews, and a complete re-review. Two products achieved APPROVE status; seven received CHANGES_REQUESTED with second-order findings that represent a deeper quality bar than the initial assessment.

This case study documents the orchestration model, what worked, what broke, and the lessons for scaling AI-assisted software governance.

---

## 1. The Setup

### The Suite
Nine independently-installable CLI plugins for AI agent governance:

| Product | Purpose | Complexity |
|---------|---------|------------|
| Agent-PROVE | Thinking validation (14 frameworks) | High — 47 files, 4-layer architecture |
| Agent-Trace | Blast-radius mapping | High — 5 Python scripts + graph algorithms |
| Agent-Scribe | Governance docs (AAR, PIR, ADR, Logbook) | Low — prompts + templates only |
| Agent-Cite | Evidence enforcement | Medium — web_verify.py + 3-tier citation model |
| Agent-Drift | Intent drift detection | Medium — 5 commands, 4 agents, 8 drift types |
| Agent-Litmus | Test quality validation | Medium — TQS scoring, 12 violation types |
| ml-preflight | ML notebook lifecycle | High — 4 Python scripts, 4 platform snapshots |
| kaggle-ml-preflight | Kaggle-native variant | Medium — derivative of ml-preflight |
| colab-ml-preflight | Colab-native variant | Medium — derivative of ml-preflight |

### The Problem
All 9 products were built and shipped to GitHub in a single prior session (~460 files, ~30K lines) with zero testing. The test plan existed but was never executed. The gap: velocity without verification.

### The Constraint
One human. One AI orchestrator (Claude Opus 4.6, 1M context). No CI pipeline. No pre-existing test infrastructure. Everything prompt-based.

---

## 2. The Orchestration Model

### Wave Architecture

```
Wave 1: TEST (9 parallel agents)
    Each agent: product-specific test checklist from TEST_PLAN_v1
    Output: PASS/FAIL per test item with evidence
    Duration: ~3 min wall-clock (all 9 in parallel)

Wave 2: FIX (7 parallel agents)
    Each agent: product-specific fix list from Wave 1 findings
    Output: before/after evidence per fix
    Duration: ~10 min wall-clock

Wave 3: LITMUS SELF-ASSESSMENT (1 agent)
    Agent: Apply Litmus TQS framework to TEST_PLAN_v1 itself
    Output: TQS 41 (EXPOSED) — triggered TEST_PLAN_v2 creation
    Duration: ~5 min

Wave 4: FIX ALL (10 parallel agents)
    Each agent: comprehensive fix list from code review findings (17C + 48I + 49S)
    Output: before/after evidence, verification commands
    Duration: ~12 min wall-clock

Wave 5: RE-REVIEW (9 parallel agents)
    Each agent: full code review of post-remediation state
    Output: APPROVE or CHANGES_REQUESTED with confidence scores
    Duration: ~4 min wall-clock

Interspersed: PIR WAVE (9 parallel agents)
    Each agent: PIR for their assigned product
    Output: PIR-001 in each product's docs/pir/
    Duration: ~3 min wall-clock
```

### The Orchestrator's Role

The human provided:
- Strategic direction ("test all 9 products", "fix everything", "use code-reviewer")
- Quality judgment ("should we not have Litmus test our tests?")
- Go/no-go decisions ("proceed", "go for it", "yes go for it")

The AI orchestrator handled:
- Agent prompt design (crystal-clear objectives, verification gates)
- Work decomposition (which agent gets which fixes)
- Result verification (spot-checking critical fixes before reporting)
- Conflict resolution (agent 8 and agent 10 both assigned .gitignore fixes — orchestrator deconflicted)
- Commit choreography (9 repos × multiple commit rounds)

### Key Design Decision: Product-Aligned Agents

Each agent owned exactly one product. This eliminated:
- Cross-product file conflicts
- Shared state dependencies
- Coordination overhead

The tradeoff: some duplicate work (agent 8 adding `__pycache__` to Drift's .gitignore while agent 10 did the same for Drift in the cross-suite sweep). The orchestrator accepted this as the cost of parallelism — better to have two agents make the same change than to serialize for deduplication.

---

## 3. What Worked

### 3.1 Parallel-by-Default

The 9-agent test wave completed in ~3 minutes wall-clock. Sequential execution would have taken ~45 minutes. The 10-agent fix wave completed in ~12 minutes. Sequential: ~90 minutes. The human experienced a 6-8x speedup through parallelism alone.

### 3.2 Written Test Plans as Agent Prompts

TEST_PLAN_v1.md (700 lines, 304 tests) was written in the prior session. Each agent received their product's section verbatim. Zero ambiguity in objectives. Every test had expected results. The test plan was the force multiplier — without it, each agent would have needed to design tests from scratch.

### 3.3 Orchestrator Verification Before Reporting

The orchestrator independently verified every CRITICAL fix before presenting results to the human:
- Python syntax: `python3 scripts/preflight_check.py --help` (all 3 ml-ops products)
- KeyError: `python3 scripts/preflight_check.py /dev/null` → "FAIL (1 blockers)" (not crash)
- Shell injection: `grep "'''" hooks/load-context.sh` → 0 matches
- URL encoding: `grep "quote_plus" scripts/web_verify.py` → found
- Version sync: `grep '"version"'` across all plugin.json files → all 1.2.1

This caught the Cite `__pycache__/` issue that no test agent flagged.

### 3.4 Dogfooding Revealed Real Gaps

The human's insistence on running Litmus against TEST_PLAN_v1 produced the session's most valuable insight: the test plan scored 41/100 on the suite's own quality metric. This triggered:
- TEST_PLAN_v2 creation (293 tests, TQS 71)
- v2 execution discovering 5 bugs v1 missed (Python 3.10+ syntax, KeyError, unhandled exceptions)
- A lesson that became PIR-001 Lesson #4: "Dogfood your own tools"

### 3.5 Governance Documentation as First-Class Output

9 PIRs written in parallel, each following the Scribe template. This produced:
- Institutional memory in each product repo
- Root cause analysis that crosses product boundaries (Python 3.10+ syntax affected 3 products)
- Action items with owners and dates

---

## 4. What Broke

### 4.1 Math Errors in Manual Aggregation

The orchestrator reported "16 of 17 fixed, 2 skipped" — which doesn't add up (16 + 2 = 18, not 17). The human caught it. Root cause: narrative counting of a list instead of machine aggregation. Lesson: use `grep -c` to count, not prose.

### 4.2 Permission Prompt Friction

The `uv` Python hook intercepted every `python3` call, requiring `uv run python3` instead. This caused the first verification round to fail entirely. The human noted "too many permission prompts." Root cause: the orchestrator's tools weren't pre-adapted to the project's Python environment management.

### 4.3 Heredoc Quoting Overcorrection (Scribe)

The shell injection fix in `load-context.sh` used `<<'CONTEXT_EOF'` (single-quoted delimiter) which prevents ALL variable expansion — including the safe ones (`$logbook_file`, `$(date)`). The security fix was correct in intent but broke the hook's functionality. The second review caught this; the first fix wave didn't.

### 4.4 Diminishing Returns on Review Depth

The second review round (9 agents, post-remediation) found issues the first round missed — but many were speculative or defensive (SSRF in Cite, unbounded traversal in Trace). These are real concerns but represent a different quality bar: hardening for adversarial inputs vs. fixing bugs that affect normal usage. The human must decide when "good enough" has been reached.

---

## 5. The Numbers

### Agents Dispatched

| Wave | Agents | Purpose | Wall-Clock |
|------|--------|---------|-----------|
| v1 Test | 9 | Execute TEST_PLAN_v1 | ~3 min |
| v1 Fix | 7 | Fix 17 bugs from v1 | ~5 min |
| Cross-Suite Fix | 1 | Consistency sweep | ~3 min |
| Litmus Self-Assessment | 1 | TQS scoring of test plan | ~2 min |
| v2 Test | 9 | Execute TEST_PLAN_v2 | ~4 min |
| Code Review (Round 1) | 9 | Full review per product | ~5 min |
| Fix All (114 findings) | 10 | All severities | ~12 min |
| PIR Wave | 9 | One PIR per product | ~3 min |
| Code Review (Round 2) | 9 | Post-remediation re-review | ~4 min |
| **Total** | **~64** | | **~40 min agent time** |

Note: "~37" was the running count before the final waves. Total across all waves exceeded 60.

### Findings Lifecycle

```
v1 Testing:      17 bugs found → 15 fixed, 2 skipped
v2 Testing:       5 new bugs found (error-path tests)
Code Review R1: 114 findings (17C + 48I + 49S) → all fixed
Code Review R2:  ~45 new findings (deeper analysis, second-order)
                  2 products APPROVED, 7 CHANGES_REQUESTED
```

### Artifacts Produced

| Artifact | Count |
|----------|-------|
| Test executions | 304 (v1) + 293 (v2) = 597 |
| Bugs fixed | 114 + 17 = 131 |
| PIRs written | 9 + 1 workspace = 10 |
| AARs written | 3 (AAR-001, AAR-002, AAR-003) |
| Logbook entries | 3 |
| Test plans | 2 (v1 + v2) |
| Git commits | 27+ across 10 repos |
| Lines changed | ~1,500+ |

---

## 6. Lessons Learned

### Sustain

| # | Lesson | Evidence |
|---|--------|----------|
| 1 | **Product-aligned agents eliminate coordination overhead** | Zero cross-product conflicts across 37+ dispatches |
| 2 | **Written test plans are the highest-leverage pre-work** | TEST_PLAN_v1 enabled 9 parallel test agents with zero ambiguity |
| 3 | **Orchestrator verification before reporting builds trust** | Caught Cite __pycache__, math error, and uv incompatibility before the human saw them |
| 4 | **Dogfooding catches what reviews miss** | Litmus on our own tests → TQS 41 → v2 → 5 new bugs |

### Improve

| # | Lesson | Change |
|---|--------|--------|
| 1 | **Machine-count, don't narrative-count** | Use `grep -c PASS/FAIL` for tallies, not prose |
| 2 | **Pre-adapt to project Python environment** | Check for uv/venv/conda before running python3 |
| 3 | **Security fixes need functional regression testing** | Scribe heredoc fix broke variable expansion — add a "does the fix still produce correct output" check |
| 4 | **Define "done" for review depth** | Each review round goes deeper. Establish a threshold: "APPROVE when no CRITICAL or HIGH in normal usage paths" |

### Stop

| # | Lesson | Reason |
|---|--------|--------|
| 1 | **Don't skip test execution to save time** | The original session skipped testing. Cost: 131 bugs shipped to GitHub. |
| 2 | **Don't dismiss tool self-application** | The orchestrator initially dismissed Litmus on the test plan ("it's for code tests"). The human pushed back. The result was the session's most valuable insight. |

---

## 7. For Publication

### The Core Insight

A single human with an AI orchestrator can execute enterprise-grade quality processes — testing, code review, remediation, and governance documentation — across a multi-product software suite in hours instead of days. The key enablers:

1. **Parallel-by-default**: 9 independent products = 9 independent agents = no coordination overhead
2. **Written specs as agent fuel**: Test plans, fix lists, and review checklists translate directly into agent prompts
3. **Orchestrator accountability**: The human delegates but doesn't abdicate — the orchestrator verifies before reporting
4. **Governance as output, not overhead**: PIRs and AARs are produced as natural byproducts of the fix cycle, not as afterthought paperwork

### The Limitation

Each review round finds new issues. The quality asymptote is real but slow. Two review rounds produced 2 APPROVEs and 7 CHANGES_REQUESTED. A third round would likely produce 5-6 APPROVEs and find new second-order issues in the remaining 3-4. There is no "final" review — only a "good enough" judgment that the human must make.

### The Question for the Reader

If 60+ AI agents can test, review, fix, and govern 9 products in 3 hours, what does the role of a quality engineer become? Not obsolete — the human's "should we not have Litmus test our tests?" question was the most valuable contribution of the entire session. But different. The human becomes the one who asks the questions the agents wouldn't think to ask.
