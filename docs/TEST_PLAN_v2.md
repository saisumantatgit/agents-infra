# Test Plan v2 — 9 Claude Code Plugins

**Created:** 2026-03-20
**Revision:** v2 (incorporates Agent-Litmus TQS analysis of v1 — TQS 41 → target TQS 75+)
**Scope:** Structural integrity, script validation (happy + error paths), installer robustness, command/skill coherence, cross-references, content quality, and cross-suite consistency.

**Litmus violations addressed in v2:**
- HOLLOW_ASSERTION → upgraded to content assertions
- WEAK_ASSERTION → upgraded to schema/value assertions
- HAPPY_PATH_ONLY → error-path tests added for every script and installer
- MISSING_EDGE_CASE → null inputs, idempotency, permission, boundary tests added
- DUPLICATE_TEST_LOGIC → parameterized into Wave 0 cross-suite matrix
- FLAKY_INDICATOR → timing assertions removed, deterministic checks only
- HARDCODED_DEPENDENCY → version checks use "contains key" not "equals value"

---

## Execution Order

| Wave | Scope | Tests | Rationale |
|------|-------|-------|-----------|
| 0 | Cross-suite consistency (parameterized) | 56 | Catches systemic issues FIRST — moved from last to first per AAR-002 |
| 1 | HIGH risk products (PROVE, Trace, Scribe) | ~75 | Product-specific tests only (structural covered by Wave 0) |
| 2 | MEDIUM risk products (ml-preflight, Drift, Litmus, Cite) | ~80 | Product-specific tests only |
| 3 | LOW risk derivatives (kaggle, colab) | ~30 | Delta from parent product only |

---

## Wave 0: Cross-Suite Parameterized Tests

> Replaces ~70 duplicate existence checks from v1 with a single parameterized matrix.
> Run for EVERY product. Each cell is one test.

### Matrix A: Structural Files (8 products × 7 checks = 56 tests)

Products: PROVE, Trace, Scribe, Cite, Drift, Litmus, ml-preflight, kaggle-ml-preflight, colab-ml-preflight

| ID | Check | Assertion (STRONG — not just "exists") |
|----|-------|----------------------------------------|
| W0-01 | `package.json` valid | Valid JSON AND `name` field matches lowercase `"agent-{product}"` or `"{product}"` pattern AND `version` field is semver |
| W0-02 | `plugin.json` valid | Valid JSON AND `name` matches package.json `name` exactly AND `version` matches package.json `version` exactly |
| W0-03 | `hooks.json` schema | Valid JSON AND uses array format `{hooks: [{type: "SessionStart", command: "..."}]}` — NOT object format |
| W0-04 | `LICENSE` content | File exists AND first line contains "MIT License" AND file contains "Copyright" |
| W0-05 | `CONTRIBUTING.md` content | File exists AND contains "Contributing" in first 5 lines AND contains "pull request" or "PR" (not a placeholder) |
| W0-06 | `CLAUDE.md` content | File exists AND contains `## Architecture` or `## Commands` (has substance, not empty) |
| W0-07 | `.gitignore` content | File exists AND contains `__pycache__/` AND contains `.DS_Store` |

### Matrix B: Adapter Directories (8 products × 5 checks = 40 tests)

| ID | Check | Assertion |
|----|-------|-----------|
| W0-08 | `adapters/claude-code/` exists | Directory exists AND contains at least 1 `.md` file in `commands/` |
| W0-09 | `adapters/codex/` exists | Directory exists AND contains `AGENTS.md` |
| W0-10 | `adapters/cursor/` exists | Directory exists (may be empty — cursor adapter is optional) |
| W0-11 | `adapters/aider/` exists | Directory exists (may be empty — aider adapter is optional) |
| W0-12 | `adapters/generic/` exists | Directory exists |

### Matrix C: Suite Links (6 Agent products × 3 checks = 18 tests)

Products: PROVE, Trace, Scribe, Cite, Drift, Litmus

| ID | Check | Assertion |
|----|-------|-----------|
| W0-13 | README has "Part of the Agent Suite" | Section heading exists AND contains table or list |
| W0-14 | Suite section lists all 6 products | Contains strings: "Agent-PROVE", "Agent-Trace", "Agent-Scribe", "Agent-Cite", "Agent-Drift", "Agent-Litmus" |
| W0-15 | Suite links are valid URLs | All URLs match pattern `https://github.com/saisumantatgit/Agent-*` |

### Matrix D: No Stale References (9 products × 1 check = 9 tests)

| ID | Check | Assertion |
|----|-------|-----------|
| W0-16 | No stale names in tree | `grep -ri` for "Agent-Safe-Remediation" returns 0 matches. `grep -ri "GordonAI"` returns 0 matches (exclude `docs/logbook/` which is historical). |

### Matrix E: No Committed Artifacts (9 products × 1 check = 9 tests)

| ID | Check | Assertion |
|----|-------|-----------|
| W0-17 | No `__pycache__/` committed | `find . -name __pycache__ -type d` returns 0 results OR all results are in `.gitignore` AND not tracked by git (`git ls-files --cached` returns empty for those paths) |

**Wave 0 Total: 56 + 40 + 18 + 9 + 9 = 132 tests**

---

## Wave 1: HIGH Risk Products (Product-Specific Only)

### Product 1: Agent-PROVE

> Structural checks handled by Wave 0. These are PROVE-specific tests only.

#### Agent Inventory (3 tests)

- [ ] **P1-01** — Verify exactly 16 agent files in `.claude/agents/` — List: blind-spot.md, cycle-auditor.md, deep-dive.md, devils-advocate.md, drift-detector.md, first-principles.md, five-whys.md, gap-finder.md, inversion.md, occams-razor.md, one-thing.md, six-thinking-hats.md, t1-validator.md, technical-research.md, tri-strike.md, via-negativa.md — Assert count = 16 AND each file > 100 bytes (not empty/stub)
- [ ] **P1-02** — Verify exactly 7 command files in `.claude/commands/` — Assert count = 7 AND each has YAML frontmatter (starts with `---`)
- [ ] **P1-03** — Verify exactly 6 skill directories in `.claude/skills/`, each with SKILL.md > 200 bytes — Assert count = 6 AND no SKILL.md is a stub

#### Command→Skill→Agent Coherence (7 tests)

- [ ] **P1-04** — `audit.md` references skill "evidence-audit" — Assert: grep "evidence-audit" returns match
- [ ] **P1-05** — `brainstorm.md` references agent or skill "brainstorm" or "six-thinking-hats" — Assert: match found
- [ ] **P1-06** — `consider.md` references framework agent dispatch — Assert: contains "agent" or "framework"
- [ ] **P1-07** — `think.md` references skill "think-cycle" — Assert: match found
- [ ] **P1-08** — `validate.md` references skill "validate-approach" — Assert: match found
- [ ] **P1-09** — `review.md` references skill "review" or "cycle-auditor" — Assert: match found
- [ ] **P1-10** — `frameworks.md` is display-only (no skill reference) — Assert: does NOT contain "skill:" in frontmatter

#### Orchestrator Wiring (2 tests)

- [ ] **P1-11** — `t1-validator.md` agent file contains references to at least 5 framework agents — Assert: grep for agent names returns ≥5 matches
- [ ] **P1-12** — `cycle-auditor.md` agent file contains references to at least 3 framework agents — Assert: grep returns ≥3

#### Cross-References (5 tests)

- [ ] **P1-13** — README badge "Frameworks-14" — Assert: count of `.md` files in `.claude/agents/` minus 2 (orchestrators) = 14
- [ ] **P1-14** — README badge "Commands-7" — Assert: count of `.md` files in `.claude/commands/` = 7
- [ ] **P1-15** — README badge "Platforms-5" — Assert: 5 platform configs exist (`.claude-plugin/`, `.codex/`, `.cursor-plugin/`, `.opencode/`, `gemini-extension.json`)
- [ ] **P1-16** — All 5 ADR files exist under `docs/adr/` — Assert: ADR-001 through ADR-005 files exist AND each > 500 bytes
- [ ] **P1-17** — CLAUDE.md framework taxonomy lists same 14 frameworks as README — Assert: all 14 names appear in both files

#### Content Quality (2 tests)

- [ ] **P1-18** — README contains "Protocol for Real-time Objective Verification & Evidence" — Assert: exact substring match
- [ ] **P1-19** — Verdict taxonomy consistent — Assert: CLAUDE.md and README both contain "VALIDATED", "REJECTED", "CYCLE_APPROVED", "CYCLE_FAILED"

**PROVE Total: 19 tests**

---

### Product 2: Agent-Trace

#### Agent & Command Inventory (3 tests)

- [ ] **P2-01** — 3 agent files in `.claude/agents/`, each > 100 bytes — contract-mapper.md, impact-analyzer.md, manifest-builder.md
- [ ] **P2-02** — 4 command files in `.claude/commands/`, each with YAML frontmatter — map.md, query.md, trace.md, validate-universe.md
- [ ] **P2-03** — `.claude/skills/safe-remediation/SKILL.md` exists and > 200 bytes

#### Command→Agent Wiring (4 tests)

- [ ] **P2-04** — `map.md` references "manifest-builder" — Assert: grep match
- [ ] **P2-05** — `query.md` references "impact-analyzer" — Assert: grep match
- [ ] **P2-06** — `trace.md` references skill "safe-remediation" — Assert: grep match
- [ ] **P2-07** — `validate-universe.md` references "contract-mapper" — Assert: grep match

#### Script Compilation (5 tests)

- [ ] **P2-08** — All 5 scripts compile: `py_compile.compile()` for build_manifest.py, query_impact.py, validate_universe.py, check_query_schema.py, common.py — Assert: exit 0 for each

#### Script Happy Path (4 tests)

- [ ] **P2-09** — `build_manifest.py --help` — Assert: exit 0 AND stdout contains "usage" or "manifest" (case-insensitive)
- [ ] **P2-10** — `query_impact.py --help` — Assert: exit 0 AND stdout contains "usage" or "target"
- [ ] **P2-11** — `validate_universe.py --help` — Assert: exit 0 AND stdout contains "usage" or "universe"
- [ ] **P2-12** — `check_query_schema.py --help` — Assert: exit 0 AND stdout contains "usage" or "schema"

#### Script Error Path (5 tests)

- [ ] **P2-13** — `query_impact.py` with no args — Assert: exit ≠ 0 AND stderr contains "required" or "error" (not a raw stack trace without message)
- [ ] **P2-14** — `query_impact.py --target /nonexistent/path` — Assert: exit ≠ 0 AND output contains error message (not unhandled FileNotFoundError)
- [ ] **P2-15** — `build_manifest.py --root /nonexistent/path` — Assert: exit ≠ 0 AND output contains error message
- [ ] **P2-16** — `check_query_schema.py` with nonexistent JSON file — Assert: exit ≠ 0 AND helpful error
- [ ] **P2-17** — `build_manifest.py` against directory with 0 Python files — Assert: completes without crash, outputs empty or minimal manifest

#### Installer (3 tests)

- [ ] **P2-18** — `install.sh` contains no hardcoded paths — Assert: `grep -E '/Users/|/home/' install.sh` returns 0 matches
- [ ] **P2-19** — `install.sh` is executable — Assert: `test -x install.sh` passes
- [ ] **P2-20** — `install.sh` run twice in same target (idempotency) — Assert: second run exits 0, no duplicate files created

#### Reference & Template Content (4 tests)

- [ ] **P2-21** — All 3 template YAML files are parseable — Assert: each > 50 bytes AND contains at least 2 distinct top-level keys (lines matching `^[a-z_]+:`) AND no lines with tab indentation (YAML uses spaces)
- [ ] **P2-22** — All 5 reference files exist and > 200 bytes each
- [ ] **P2-23** — All 3 spec files exist in `docs/specs/` and > 200 bytes each
- [ ] **P2-24** — All 4 prompt files exist in `prompts/` and > 200 bytes each

**Trace Total: 28 tests**

---

### Product 3: Agent-Scribe

#### Architecture-Specific (2 tests)

- [ ] **P3-01** — Scribe has NO `.claude/skills/` directory — Assert: directory does not exist (Scribe uses prompts directly)
- [ ] **P3-02** — Scribe has NO `.claude/agents/` directory — Assert: directory does not exist

#### Command→Prompt Coherence (4 tests)

- [ ] **P3-03** — `.claude/commands/logbook.md` references `prompts/logbook.md` — Assert: grep match for "prompts/logbook" or equivalent instruction
- [ ] **P3-04** — `.claude/commands/draft-aar.md` references `prompts/draft-aar.md` — Assert: grep match
- [ ] **P3-05** — `.claude/commands/draft-pir.md` references `prompts/draft-pir.md` — Assert: grep match
- [ ] **P3-06** — `.claude/commands/draft-adr.md` references `prompts/draft-adr.md` — Assert: grep match

#### Template Quality (4 tests)

- [ ] **P3-07** — `templates/aar-template.md` contains "Sustain" AND "Improve" AND "Stop" — Assert: all 3 keywords present
- [ ] **P3-08** — `templates/pir-template.md` contains "Five Whys" AND "Blast Radius" — Assert: both present
- [ ] **P3-09** — `templates/adr-template-madr-v4.md` contains "Decision Drivers" AND "Considered Options" — Assert: both present (MADR v4 structure)
- [ ] **P3-10** — `templates/logbook-template.md` contains "Zone Check" AND "Handoff" — Assert: both present

#### Hook Validation (3 tests)

- [ ] **P3-11** — `hooks/load-context.sh` has no syntax errors — Assert: `bash -n hooks/load-context.sh` exits 0
- [ ] **P3-12** — `hooks/load-context.sh` contains no hardcoded paths — Assert: `grep -E '/Users/|/home/' hooks/load-context.sh` returns 0 matches
- [ ] **P3-13** — `hooks/load-context.sh` exits cleanly when no logbook files exist — Assert: run in empty temp dir, exit 0 (no crash)

#### Installer (3 tests)

- [ ] **P3-14** — `install.sh` contains no hardcoded paths — Assert: grep returns 0 matches
- [ ] **P3-15** — `install.sh` is executable — Assert: `test -x` passes
- [ ] **P3-16** — `install.sh` handles 5 CLI types — Assert: file contains "claude" AND "codex" AND "cursor" AND "aider" AND "generic" (case-insensitive)
- [ ] **P3-17a** — `install.sh` run twice in same target (idempotency) — Assert: second run exits 0

#### Cross-References (2 tests)

- [ ] **P3-17** — README badge "Commands-4" — Assert: 4 files in `.claude/commands/`
- [ ] **P3-18** — README badge "CLI_Support-5" — Assert: 5 adapter directories exist

**Scribe Total: 18 tests**

---

## Wave 2: MEDIUM Risk Products (Product-Specific Only)

### Product 4: ml-preflight

#### Command/Skill Inventory (2 tests)

- [ ] **P4-01** — 6 command files, each with `skill:` in YAML frontmatter — Assert: count = 6 AND all have skill reference
- [ ] **P4-02** — 6 skill directories, each with SKILL.md > 200 bytes — Assert: count = 6

#### Script Compilation (4 tests)

- [ ] **P4-03** — All 4 scripts compile: preflight_check.py, env_parity.py, poll_monitor.py, triage.py — Assert: `py_compile` exit 0 each

#### Script Happy Path (4 tests)

- [ ] **P4-04** — `preflight_check.py --help` — Assert: exit 0, stdout contains "usage" or "notebook"
- [ ] **P4-05** — `env_parity.py --help` — Assert: exit 0, stdout contains "usage"
- [ ] **P4-06** — `poll_monitor.py --help` — Assert: exit 0, stdout contains "usage"
- [ ] **P4-07** — `triage.py --help` — Assert: exit 0, stdout contains "usage"

#### Script Error Path (5 tests)

- [ ] **P4-08** — `preflight_check.py` with no args — Assert: exit ≠ 0, stderr contains "required" (argparse error, not raw traceback)
- [ ] **P4-09** — `preflight_check.py /nonexistent/notebook.ipynb` — Assert: exit ≠ 0, output contains error message (not unhandled exception)
- [ ] **P4-10** — `env_parity.py /nonexistent/notebook.ipynb` — Assert: exit ≠ 0, helpful error
- [ ] **P4-11** — `triage.py --error-log /nonexistent/file` — Assert: exit ≠ 0, helpful error
- [ ] **P4-12** — `preflight_check.py /dev/null` (zero-byte file, not a valid notebook) — Assert: exit ≠ 0, error message about invalid notebook format

#### Script Dependency Isolation (1 test)

- [ ] **P4-13** — All 4 scripts import only stdlib — Assert: grep for `import` lines, all resolve to Python stdlib modules (argparse, ast, json, os, re, sys, pathlib, typing, subprocess, time, datetime, random)

#### Platform Data (2 tests)

- [ ] **P4-14** — All 4 platform JSON files are valid JSON AND each contains `"platform"` key — Assert: parse succeeds AND key exists
- [ ] **P4-15** — All 4 platform JSON files contain `"gpu_options"` array with ≥1 entry — Assert: array exists and is non-empty

#### Case Studies & References (3 tests)

- [ ] **P4-16** — Exactly 10 case study files (cs01-cs10) — Assert: count = 10, each > 200 bytes
- [ ] **P4-17** — Exactly 6 reference files — Assert: count = 6, each > 200 bytes
- [ ] **P4-18** — `templates/known_fixes.yaml` is valid YAML-like AND contains "FIX-" entries — Assert: file contains "FIX-001"

#### Installer (3 tests)

- [ ] **P4-19** — `install.sh` no hardcoded paths — Assert: grep returns 0
- [ ] **P4-20** — `install.sh` is executable — Assert: `test -x`
- [ ] **P4-21** — `install.sh` run twice in same target (idempotency) — Assert: second run exits 0

**ml-preflight Total: 24 tests**

---

### Product 5: Agent-Drift

#### Command/Skill/Agent Inventory (3 tests)

- [ ] **P5-01** — 5 command files, each with YAML frontmatter — Assert: count = 5
- [ ] **P5-02** — 5 skill directories, each with SKILL.md > 200 bytes — Assert: count = 5
- [ ] **P5-03** — 4 agent files, each > 100 bytes — Assert: count = 4

#### Command→Skill→Agent Chain (5 tests)

- [ ] **P5-04** — `drift-lock.md` references "intent-capture" — Assert: grep match
- [ ] **P5-05** — `drift-check.md` references "drift-analysis" — Assert: grep match
- [ ] **P5-06** — `drift-fence.md` references "constraint-enforcement" — Assert: grep match
- [ ] **P5-07** — `drift-status.md` references "status-dashboard" — Assert: grep match
- [ ] **P5-08** — `drift-report.md` references "session-audit" — Assert: grep match

#### Content-Specific (4 tests)

- [ ] **P5-09** — `references/drift-types.md` lists exactly 8 drift types — Assert: count of `##` or numbered headings = 8
- [ ] **P5-10** — CLAUDE.md lists same 8 drift types — Assert: all 8 type names appear
- [ ] **P5-11** — `templates/drift-protocol.yaml` contains keys: "severities", "monitoring", "scoring", "verdicts" — Assert: all 4 present
- [ ] **P5-12** — `docs/adr/ADR-002-five-commands-not-three.md` exists and > 500 bytes

#### Installer (3 tests)

- [ ] **P5-13** — `install.sh` no hardcoded paths, is executable
- [ ] **P5-14** — `install.sh` copies templates/drift-protocol.yaml — Assert: grep "drift-protocol" in install.sh returns match
- [ ] **P5-15** — `install.sh` run twice in same target (idempotency) — Assert: second run exits 0

**Drift Total: 15 tests**

---

### Product 6: Agent-Litmus

#### Command/Skill/Agent Inventory (3 tests)

- [ ] **P6-01** — 5 command files, each with YAML frontmatter — Assert: count = 5
- [ ] **P6-02** — 5 skill directories, each with SKILL.md > 200 bytes — Assert: count = 5
- [ ] **P6-03** — 5 agent files, each > 100 bytes — Assert: count = 5

#### Command→Skill→Agent Chain (5 tests)

- [ ] **P6-04** — `litmus-scan.md` references "test-audit" — Assert: grep match
- [ ] **P6-05** — `litmus-edge.md` references "edge-analysis" — Assert: grep match
- [ ] **P6-06** — `litmus-strength.md` references "strength-analysis" — Assert: grep match
- [ ] **P6-07** — `litmus-fix.md` references "test-fix" — Assert: grep match
- [ ] **P6-08** — `litmus-report.md` references "test-report" — Assert: grep match

#### Content-Specific (4 tests)

- [ ] **P6-09** — `references/violation-types.md` lists exactly 12 violation types — Assert: count = 12
- [ ] **P6-10** — CLAUDE.md lists same 12 violation types — Assert: all 12 type names appear
- [ ] **P6-11** — `templates/litmus-protocol.yaml` contains keys: "violations", "test_patterns", "tqs", "scoring" — Assert: all 4 present
- [ ] **P6-12** — TQS formula in CLAUDE.md AND README both contain "0.40" AND "0.30" — Assert: both files match

#### Installer (3 tests)

- [ ] **P6-13** — `install.sh` no hardcoded paths, is executable
- [ ] **P6-14** — `install.sh` downloads reference files — Assert: grep "violation-types\|assertion-classification\|edge-case-taxonomy" in install.sh returns ≥3 matches
- [ ] **P6-15** — `install.sh` run twice in same target (idempotency) — Assert: second run exits 0

**Litmus Total: 15 tests**

---

### Product 7: Agent-Cite

#### Command/Skill/Agent Inventory (3 tests)

- [ ] **P7-01** — 3 command files, each with YAML frontmatter
- [ ] **P7-02** — 3 skill directories, each with SKILL.md > 200 bytes
- [ ] **P7-03** — 3 agent files, each > 100 bytes

#### Command→Skill→Agent Chain (3 tests)

- [ ] **P7-04** — `cite-audit.md` references "evidence-audit" — Assert: grep match
- [ ] **P7-05** — `cite-fix.md` references "citation-fix" — Assert: grep match
- [ ] **P7-06** — `cite-report.md` references "evidence-report" — Assert: grep match

#### Script Tests (4 tests)

- [ ] **P7-07** — `web_verify.py` compiles — Assert: `py_compile` exit 0
- [ ] **P7-08** — `web_verify.py --help` — Assert: exit 0 OR exit with message containing "patchright" (graceful dependency error)
- [ ] **P7-09** — `web_verify.py` with no args — Assert: exit ≠ 0, output contains usage or error (not raw traceback)
- [ ] **P7-10** — `web_verify.py` handles missing patchright — Assert: source contains `try` and `ImportError` or `check_dependencies` function

#### Content-Specific (4 tests)

- [ ] **P7-11** — `references/violation-types.md` lists exactly 6 violation types — Assert: UNCITED_INFERENCE, UNVERIFIED_NUMBER, UNSUPPORTED_ABSENCE, BROKEN_CITATION, FALSE_ABSENCE, UNVERIFIABLE all present
- [ ] **P7-12** — CLAUDE.md lists same 6 violation types — Assert: all 6 present
- [ ] **P7-13** — `templates/evidence-protocol.yaml` contains keys: "severities", "include", "exclude", "thresholds" — Assert: all 4 present
- [ ] **P7-14** — `docs/adr/ADR-001-three-tier-citation-model.md` exists and > 500 bytes

#### Installer (3 tests)

- [ ] **P7-15** — `install.sh` no hardcoded paths, is executable
- [ ] **P7-16** — `install.sh` copies evidence-protocol.yaml — Assert: grep "evidence-protocol" returns match
- [ ] **P7-17** — `install.sh` run twice in same target (idempotency) — Assert: second run exits 0

**Cite Total: 17 tests**

---

## Wave 3: LOW Risk Derivatives (Delta Tests Only)

> These products share ~90% structure with ml-preflight. Only test what's DIFFERENT.

### Product 8: kaggle-ml-preflight

#### Platform Isolation (3 tests)

- [ ] **P8-01** — `platforms/` contains ONLY `kaggle.json` — Assert: exactly 1 file
- [ ] **P8-02** — `kaggle.json` contains `"platform": "kaggle"` — Assert: exact match
- [ ] **P8-03** — `templates/kaggle-preflight-protocol.yaml` exists and > 100 bytes

#### Script Platform Default (2 tests)

- [ ] **P8-04** — `preflight_check.py --help` — Assert: output contains "kaggle" (case-insensitive)
- [ ] **P8-05** — `preflight_check.py` with no args — Assert: exit ≠ 0, helpful error (not crash)

#### Script Error Path (2 tests)

- [ ] **P8-06** — `preflight_check.py /nonexistent/file.ipynb` — Assert: exit ≠ 0, helpful error
- [ ] **P8-07** — `preflight_check.py /dev/null` — Assert: exit ≠ 0, invalid notebook error

#### Content Isolation (3 tests)

- [ ] **P8-08** — No Colab-specific instructions — Assert: grep for "drive.mount\|Runtime restart\|colab-preflight-protocol" returns 0 matches (comparison context OK, but Colab-specific commands should not appear)
- [ ] **P8-09** — No GordonAI references — Assert: grep -ri "gordonai" returns 0
- [ ] **P8-10** — README references ml-preflight as parent — Assert: contains "github.com/saisumantatgit/ml-preflight"

#### Installer (2 tests)

- [ ] **P8-11** — `install.sh` no hardcoded paths, is executable
- [ ] **P8-12** — `install.sh` run twice (idempotency) — Assert: second run exits 0

**kaggle Total: 12 tests**

---

### Product 9: colab-ml-preflight

#### Platform Isolation (3 tests)

- [ ] **P9-01** — `platforms/` contains ONLY `colab.json` — Assert: exactly 1 file
- [ ] **P9-02** — `colab.json` contains `"platform": "colab"` — Assert: exact match
- [ ] **P9-03** — `templates/colab-preflight-protocol.yaml` exists and > 100 bytes

#### Script Platform Default (2 tests)

- [ ] **P9-04** — `preflight_check.py --help` — Assert: output does NOT contain "--platform" flag (Colab is implicit)
- [ ] **P9-05** — `preflight_check.py` with no args — Assert: exit ≠ 0, helpful error

#### Script Error Path (2 tests)

- [ ] **P9-06** — `preflight_check.py /nonexistent/file.ipynb` — Assert: exit ≠ 0, helpful error
- [ ] **P9-07** — `preflight_check.py /dev/null` — Assert: exit ≠ 0, invalid notebook error

#### Content Isolation (3 tests)

- [ ] **P9-08** — No Kaggle-specific instructions — Assert: grep for "kaggle kernels push\|kaggle-preflight-protocol\|30hr.*quota" returns 0 matches
- [ ] **P9-09** — No GordonAI references — Assert: grep -ri "gordonai" returns 0
- [ ] **P9-10** — README references ml-preflight as parent — Assert: contains "github.com/saisumantatgit/ml-preflight"

#### Installer (2 tests)

- [ ] **P9-11** — `install.sh` no hardcoded paths, is executable
- [ ] **P9-12** — `install.sh` run twice (idempotency) — Assert: second run exits 0

**colab Total: 12 tests**

---

## Summary

| Wave | Tests | v1 Equivalent | Change |
|------|-------|---------------|--------|
| Wave 0 (Cross-Suite) | 132 | ~70 (scattered + Wave 4) | +62 (parameterized, stronger assertions) |
| Wave 1 (HIGH) | 66 | ~105 | -39 (deduped to Wave 0) |
| Wave 2 (MEDIUM) | 71 | ~124 | -53 (deduped to Wave 0, +4 idempotency) |
| Wave 3 (LOW) | 24 | ~53 | -29 (delta-only) |
| **Total** | **293** | **304** | **-11 tests, dramatically stronger assertions, 8/8 installers with idempotency** |

### v1 → v2 Changes by Litmus Violation

| Violation | v1 Status | v2 Fix |
|-----------|-----------|--------|
| HOLLOW_ASSERTION | ~50 bare "exists" checks | All upgraded to content assertions (contains "MIT License", > 200 bytes, etc.) |
| WEAK_ASSERTION | ~25 "valid JSON" checks | Upgraded to "valid JSON AND contains expected keys/values" |
| NO_ASSERTION | ~8 ambiguous tests | All rewritten with deterministic pass/fail criteria |
| MISSING_EDGE_CASE | 0 error-path script tests | 17 error-path tests added (invalid paths, null inputs, missing deps) |
| HAPPY_PATH_ONLY | 85% happy / 15% error | ~65% happy / ~35% error |
| DUPLICATE_TEST_LOGIC | ~70 repeated structural checks | Parameterized into Wave 0 matrix |
| HARDCODED_DEPENDENCY | Platform version pinning | Changed to "contains key" checks, not "equals value" |
| FLAKY_INDICATOR | "~100ms" timing assertion | Removed — replaced with "exits with code 0" |

### Known Limitations

1. **No functional integration tests** — This plan tests structure and script entry points. It does not test whether `/brainstorm` actually produces a brainstorm or `/litmus-scan` actually scans tests. Functional testing requires a Claude Code runtime environment.
2. **No performance tests** — Script execution time under load is not tested.
3. **Installer tests require temp directories** — Each installer idempotency test needs an isolated temp dir. Specify cleanup in agent instructions.
