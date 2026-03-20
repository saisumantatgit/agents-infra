# Test Plan v1 — 9 Claude Code Plugins

**Created:** 2026-03-20
**Scope:** Structural integrity, script validation, installer testing, command/skill coherence, cross-references, and content quality for all 9 products across the Agent Governance Suite and ML Operations Suite.

**Important:** This plan is for test DESIGN only. No tests have been executed.

---

## Priority Order (Highest Risk First)

| Priority | Product | Risk Level | Reason |
|----------|---------|------------|--------|
| 1 | Agent-PROVE | HIGH | Flagship product (v1.2.1), version mismatch already found (package.json=1.2.0 vs plugin.json=1.2.1), most complex (14 agents, 7 commands, 6 skills, 2 orchestrators) |
| 2 | Agent-Trace | HIGH | Python scripts that generate/query dependency graphs, most moving parts (scripts + agents + adapters + templates) |
| 3 | Agent-Scribe | HIGH | Missing package.json, missing .claude-plugin at root, missing CLAUDE.md, missing CONTRIBUTING.md, missing .gitignore — most structural gaps |
| 4 | ml-preflight | MEDIUM | 4 Python scripts, 4 platform snapshots (JSON), 10 case studies, empty .claude/agents/ directory |
| 5 | Agent-Drift | MEDIUM | 5 commands, 5 skills, 4 agents, hooks.json with different schema than PROVE/Trace |
| 6 | Agent-Litmus | MEDIUM | hooks.json uses different schema format (object vs array), plugin.json uses "Agent-Litmus" (capitalized) vs "agent-litmus" pattern |
| 7 | Agent-Cite | MEDIUM | web_verify.py has external dependency (patchright), 3 commands, 3 agents, 3 skills |
| 8 | kaggle-ml-preflight | LOW | Derivative of ml-preflight, Kaggle-native, same structure |
| 9 | colab-ml-preflight | LOW | Derivative of ml-preflight, Colab-native, same structure |

---

## Product 1: Agent-PROVE

### Risk Level: HIGH
### Priority: Test first

**Known Issues Found During Inspection:**
- package.json version is `1.2.0`, plugin.json version is `1.2.1` — version mismatch
- No install.sh (README says "cp -r" manual install only)
- .gitignore exists but is minimal (35 bytes)

### Structural Integrity

- [ ] **SI-01** — Verify all 14 framework agent files exist in `.claude/agents/` — Expected: blind-spot.md, cycle-auditor.md, deep-dive.md, devils-advocate.md, drift-detector.md, first-principles.md, five-whys.md, gap-finder.md, inversion.md, occams-razor.md, one-thing.md, six-thinking-hats.md, t1-validator.md, technical-research.md, tri-strike.md, via-negativa.md (16 files: 14 frameworks + 2 orchestrators) — Expected result: all exist
- [ ] **SI-02** — Verify all 7 command files exist in `.claude/commands/` — Expected: audit.md, brainstorm.md, consider.md, frameworks.md, review.md, think.md, validate.md — Expected result: all 7 exist
- [ ] **SI-03** — Verify all 6 skill directories exist in `.claude/skills/` each with SKILL.md — Expected: brainstorm/, consider/, evidence-audit/, review/, think-cycle/, validate-approach/ — Expected result: 6 dirs, each with SKILL.md
- [ ] **SI-04** — Validate `package.json` is valid JSON — Run: `python3 -c "import json; json.load(open('package.json'))"` — Expected: no error
- [ ] **SI-05** — Validate `package.json` name is `"agent-prove"` — Expected: `"agent-prove"`
- [ ] **SI-06** — Validate `.claude-plugin/plugin.json` is valid JSON — Run: `python3 -c "import json; json.load(open('.claude-plugin/plugin.json'))"` — Expected: no error
- [ ] **SI-07** — Validate plugin.json name is `"agent-prove"` — Expected: `"agent-prove"`
- [ ] **SI-08** — **BUG CHECK:** Verify package.json version matches plugin.json version — Current: package.json=`1.2.0`, plugin.json=`1.2.1` — Expected: both should be `1.2.1` — **KNOWN MISMATCH**
- [ ] **SI-09** — Validate `.claude-plugin/hooks.json` is valid JSON — Expected: valid, has SessionStart hook
- [ ] **SI-10** — Verify hooks.json hook type is `"SessionStart"` — Expected: `"SessionStart"`
- [ ] **SI-11** — Verify `.gitignore` exists and covers `.DS_Store`, `__pycache__`, `node_modules` — Expected: exists (currently 35 bytes — check coverage)
- [ ] **SI-12** — Verify `LICENSE` file exists — Expected: exists, MIT
- [ ] **SI-13** — Verify `CONTRIBUTING.md` exists — Expected: exists
- [ ] **SI-14** — Verify `CHANGELOG.md` exists — Expected: exists
- [ ] **SI-15** — Verify `CLAUDE.md` exists — Expected: exists
- [ ] **SI-16** — Verify `docs/adr/` directory has 5 ADR files (001-005) — Expected: all 5 exist
- [ ] **SI-17** — Verify `gemini-extension.json` is valid JSON — Expected: valid
- [ ] **SI-18** — Verify `GEMINI.md` exists — Expected: exists
- [ ] **SI-19** — Verify platform config dirs exist: `.codex/`, `.cursor-plugin/`, `.opencode/` — Expected: all exist with plugin.json inside
- [ ] **SI-20** — Verify `scripts/validate-structure.sh` referenced in README exists — Expected: exists in `scripts/` directory

### Script Tests

- [ ] **SC-01** — Agent-PROVE has no Python scripts — Expected: N/A (skip)

### install.sh Tests

- [ ] **IN-01** — Agent-PROVE has no install.sh — README provides manual `cp -r` — Expected: N/A, but note the inconsistency with other suite products that have install.sh

### Command/Skill Coherence

- [ ] **CS-01** — Each command file references a skill that exists — Check: audit.md references evidence-audit skill, brainstorm.md references brainstorm skill, consider.md references consider skill, think.md references think-cycle skill, validate.md references validate-approach skill, review.md references review skill, frameworks.md references no skill (informational) — Expected: all referenced skills exist in `.claude/skills/`
- [ ] **CS-02** — Each skill SKILL.md references agents that exist — Check: validate-approach references t1-validator + framework agents, think-cycle references cycle-auditor + framework agents, evidence-audit references framework agents, review references cycle-auditor + framework agents, brainstorm references six-thinking-hats agent, consider references specific framework agents — Expected: all referenced agents exist in `.claude/agents/`
- [ ] **CS-03** — Verify the 2 orchestrator agents (t1-validator, cycle-auditor) reference the correct framework agents — Expected: t1-validator dispatches to the 5 validation-phase frameworks, cycle-auditor dispatches to the 5 verification-phase frameworks
- [ ] **CS-04** — Verify YAML frontmatter in all command .md files is valid — Run: parse the first YAML block of each command — Expected: valid YAML or no YAML (pure markdown commands)

### Cross-References

- [ ] **XR-01** — README badge "Frameworks-14" — Verify there are exactly 14 framework agents (excluding the 2 orchestrators) — Expected: 14
- [ ] **XR-02** — README badge "Commands-7" — Verify there are exactly 7 command files — Expected: 7
- [ ] **XR-03** — README badge "Platforms-5" — Verify 5 platform configs exist — Expected: Claude Code, Cursor, Codex, OpenCode, Gemini CLI
- [ ] **XR-04** — README "Part of the Agent Suite" section does not exist — Compare with newer products that have it — Expected: should list suite products (low priority, PROVE is the oldest)
- [ ] **XR-05** — ADR links in README resolve to actual files — Expected: all 5 ADR paths exist under docs/adr/
- [ ] **XR-06** — CONTRIBUTING.md references correct file paths for agent template — Expected: references `.claude/agents/`

### Content Quality

- [ ] **CQ-01** — README tagline is "Protocol for Real-time Objective Verification & Evidence" or "Prove it or it fails." — Expected: both present
- [ ] **CQ-02** — No stale product references (e.g., "Shield", "Audit", "Agent-Safe-Remediation") — Grep the entire tree for stale names — Expected: no matches
- [ ] **CQ-03** — CLAUDE.md framework taxonomy matches README framework list — Expected: same 14 frameworks, same categories
- [ ] **CQ-04** — Verdict taxonomy in CLAUDE.md matches README — Expected: identical verdict sets

### Estimated Effort: 30 minutes

---

## Product 2: Agent-Trace

### Risk Level: HIGH
### Priority: Test first

**Known Issues Found During Inspection:**
- Has `__pycache__/` in scripts/ (should be gitignored)
- Has both `.claude/` native structure AND `adapters/claude-code/` with duplicate command files

### Structural Integrity

- [ ] **SI-01** — Verify all 3 agent files exist in `.claude/agents/` — Expected: contract-mapper.md, impact-analyzer.md, manifest-builder.md
- [ ] **SI-02** — Verify all 4 command files exist in `.claude/commands/` — Expected: map.md, query.md, trace.md, validate-universe.md
- [ ] **SI-03** — Verify skill directory `.claude/skills/safe-remediation/SKILL.md` exists — Expected: exists
- [ ] **SI-04** — Validate `package.json` is valid JSON with name `"agent-trace"` and version `"1.0.0"` — Expected: valid, correct name and version
- [ ] **SI-05** — Validate `.claude-plugin/plugin.json` is valid JSON with name `"agent-trace"` and version `"1.0.0"` — Expected: valid, matching
- [ ] **SI-06** — Validate `.claude-plugin/hooks.json` is valid JSON with `"SessionStart"` hook — Expected: valid
- [ ] **SI-07** — Verify `install.sh` is executable with `#!/bin/bash` shebang — Expected: executable, correct shebang
- [ ] **SI-08** — Verify `.gitignore` exists — Expected: exists
- [ ] **SI-09** — Verify `__pycache__/` is covered by `.gitignore` — Check: `grep __pycache__ .gitignore` — Expected: present (note: `__pycache__` currently exists in `scripts/` which suggests it may not be properly gitignored)
- [ ] **SI-10** — Verify all 5 Python scripts exist in `scripts/` — Expected: build_manifest.py, query_impact.py, validate_universe.py, check_query_schema.py, common.py
- [ ] **SI-11** — Verify `LICENSE` exists — Expected: exists, MIT
- [ ] **SI-12** — Verify `CONTRIBUTING.md` exists — Expected: exists
- [ ] **SI-13** — Verify `CLAUDE.md` exists — Expected: exists
- [ ] **SI-14** — Verify template files exist — Expected: `templates/invariants.yaml`, `templates/ownership.yaml`, `templates/source_of_truth.yaml`
- [ ] **SI-15** — Verify all template YAML files are valid YAML — Run: `python3 -c "import yaml; yaml.safe_load(open('templates/invariants.yaml'))"` for each — Expected: valid
- [ ] **SI-16** — Verify docs/specs/ has 3 spec files — Expected: curated-overlays.md, manifest-schema.md, query-contract.md
- [ ] **SI-17** — Verify prompts/ has 4 prompt files — Expected: map.md, query.md, trace.md, validate.md
- [ ] **SI-18** — Verify references/ has 5 reference files — Expected: dependency-heuristics.md, evaluation-rubric.md, platform-portability.md, repo-universe-model.md, scenario-walkthroughs.md

### Script Tests

- [ ] **SC-01** — `python3 -c "import py_compile; py_compile.compile('scripts/build_manifest.py')"` — Expected: compiles without error
- [ ] **SC-02** — `python3 -c "import py_compile; py_compile.compile('scripts/query_impact.py')"` — Expected: compiles without error
- [ ] **SC-03** — `python3 -c "import py_compile; py_compile.compile('scripts/validate_universe.py')"` — Expected: compiles without error
- [ ] **SC-04** — `python3 -c "import py_compile; py_compile.compile('scripts/check_query_schema.py')"` — Expected: compiles without error
- [ ] **SC-05** — `python3 -c "import py_compile; py_compile.compile('scripts/common.py')"` — Expected: compiles without error
- [ ] **SC-06** — `python3 scripts/build_manifest.py --help` — Expected: prints help text, exits 0
- [ ] **SC-07** — `python3 scripts/query_impact.py --help` — Expected: prints help text, exits 0
- [ ] **SC-08** — `python3 scripts/validate_universe.py --help` — Expected: prints help text, exits 0
- [ ] **SC-09** — `python3 scripts/check_query_schema.py --help` — Expected: prints help text, exits 0
- [ ] **SC-10** — Run `build_manifest.py` against a simple test repo (create temp dir with 3 Python files) — Expected: generates `nodes.json` and `edges.json` with correct schema
- [ ] **SC-11** — Run `query_impact.py` against the generated manifest from SC-10 — Expected: returns query result with blast radius, tests, confidence fields
- [ ] **SC-12** — Run `validate_universe.py` against the generated manifest — Expected: outputs PASS or FAIL with details
- [ ] **SC-13** — Run `check_query_schema.py` against query output from SC-11 — Expected: validates schema, outputs PASS/FAIL
- [ ] **SC-14** — Run `build_manifest.py` with no arguments (no target repo) — Expected: helpful error message, not a stack trace
- [ ] **SC-15** — Run `query_impact.py` with no manifest present — Expected: helpful error message about missing manifest

### install.sh Tests

- [ ] **IN-01** — Create temp dir with `.claude/` directory, run install.sh — Expected: detects Claude Code, copies commands, agents, skill, hook files
- [ ] **IN-02** — Create temp dir with no CLI marker directories — Expected: falls back to generic or prompts a choice
- [ ] **IN-03** — Grep install.sh for hardcoded absolute paths — Expected: no `/Users/` or `/home/` hardcoded paths
- [ ] **IN-04** — Verify install.sh copies scripts/ directory to target — Expected: Python scripts are copied to target repo
- [ ] **IN-05** — Verify install.sh copies templates/ directory — Expected: curated overlay templates are copied

### Command/Skill Coherence

- [ ] **CS-01** — `.claude/commands/trace.md` references skill `safe-remediation` — Expected: skill exists at `.claude/skills/safe-remediation/SKILL.md`
- [ ] **CS-02** — `.claude/commands/map.md` references manifest-builder agent — Expected: agent exists at `.claude/agents/manifest-builder.md`
- [ ] **CS-03** — `.claude/commands/query.md` references impact-analyzer agent — Expected: agent exists at `.claude/agents/impact-analyzer.md`
- [ ] **CS-04** — Adapter commands in `adapters/claude-code/commands/` match `.claude/commands/` — Expected: same 4 command names in both locations (trace.md, map.md, query.md, validate-universe.md)
- [ ] **CS-05** — Verify no orphan agents (agents referenced nowhere) — Expected: all 3 agents referenced by at least one skill or command

### Cross-References

- [ ] **XR-01** — README badge "Commands-4" — Verify exactly 4 command files — Expected: 4
- [ ] **XR-02** — README badge "Platforms-5" — Verify 5 platform adapters exist — Expected: claude-code, codex, cursor, aider, generic (note: cursor and aider adapter dirs are empty)
- [ ] **XR-03** — README "Part of the Agent Suite" links — Expected: links to Agent-PROVE and Agent-Scribe GitHub repos are valid URLs
- [ ] **XR-04** — README "Part of the Agent Suite" should list all current suite products — Expected: at minimum PROVE, Scribe, Trace (newer products like Cite, Drift, Litmus may not be listed yet)
- [ ] **XR-05** — CLAUDE.md lists the same 4 commands as README — Expected: match
- [ ] **XR-06** — CLAUDE.md lists the same 3 agents as actual `.claude/agents/` — Expected: match
- [ ] **XR-07** — CLAUDE.md lists the same 5 scripts as actual `scripts/` — Expected: match

### Content Quality

- [ ] **CQ-01** — README tagline is "See the ripple effect before it happens." — Expected: present
- [ ] **CQ-02** — No stale product references (grep for "Shield", "Agent-Safe-Remediation", "GordonAI", "iVal", "ProSure") — Expected: no matches
- [ ] **CQ-03** — No stale references from the source material (Agent-Trace was extracted from ival_2.0 agent-safe-remediation research) — Expected: no ival-specific references remain
- [ ] **CQ-04** — Template YAML files have meaningful example content, not lorem ipsum — Expected: real example invariants, ownership, source-of-truth entries

### Estimated Effort: 45 minutes

---

## Product 3: Agent-Scribe

### Risk Level: HIGH
### Priority: Test first

**Known Issues Found During Inspection:**
- Missing `package.json` (every other product has one)
- Missing `.claude-plugin/` directory at root (no plugin.json, no hooks.json at standard location)
- Missing `CLAUDE.md`
- Missing `CONTRIBUTING.md`
- Missing `.gitignore`
- Missing `.claude/` directory at root (commands/agents/skills are only in `adapters/claude-code/`)
- Hooks.json is inside `adapters/claude-code/hooks/hooks.json` instead of `.claude-plugin/hooks.json`
- This is the OLDEST architecture — predates the standardized layout used by Trace, Cite, Drift, Litmus

### Structural Integrity

- [ ] **SI-01** — **BUG:** Verify `package.json` exists — Expected: MISSING — needs to be created
- [ ] **SI-02** — **BUG:** Verify `.claude-plugin/plugin.json` exists — Expected: MISSING — needs to be created
- [ ] **SI-03** — **BUG:** Verify `.claude-plugin/hooks.json` exists at standard location — Expected: MISSING (currently at `adapters/claude-code/hooks/hooks.json`)
- [ ] **SI-04** — **BUG:** Verify `CLAUDE.md` exists — Expected: MISSING
- [ ] **SI-05** — **BUG:** Verify `CONTRIBUTING.md` exists — Expected: MISSING
- [ ] **SI-06** — **BUG:** Verify `.gitignore` exists — Expected: MISSING
- [ ] **SI-07** — **BUG:** Verify `.claude/commands/` exists at root — Expected: MISSING (only at `adapters/claude-code/commands/`)
- [ ] **SI-08** — Verify all 4 command files exist at `adapters/claude-code/commands/` — Expected: draft-aar.md, draft-adr.md, draft-pir.md, logbook.md
- [ ] **SI-09** — Verify hooks file at `adapters/claude-code/hooks/hooks.json` is valid JSON — Expected: valid, has SessionStart hook running `bash hooks/load-context.sh`
- [ ] **SI-10** — Verify `hooks/load-context.sh` exists and is executable — Expected: exists (check executable bit)
- [ ] **SI-11** — Verify `hooks/load-context.sh` has correct shebang — Expected: `#!/bin/bash` or `#!/usr/bin/env bash`
- [ ] **SI-12** — Verify `install.sh` is executable with `#!/bin/bash` shebang — Expected: executable, correct shebang
- [ ] **SI-13** — Verify `LICENSE` exists — Expected: exists, MIT
- [ ] **SI-14** — Verify all 4 prompt files exist in `prompts/` — Expected: draft-aar.md, draft-adr.md, draft-pir.md, logbook.md
- [ ] **SI-15** — Verify all 4 template files exist in `templates/` — Expected: aar-template.md, adr-template-madr-v4.md, logbook-template.md, pir-template.md
- [ ] **SI-16** — Verify `TEMPLATE_CHECKLIST.md` exists — Expected: exists
- [ ] **SI-17** — Verify adapter directories exist — Expected: aider/, claude-code/, codex/, cursor/, generic/ (note: aider/ and cursor/ are empty)

### Script Tests

- [ ] **SC-01** — `hooks/load-context.sh` — Run in a temp dir with no logbook files — Expected: exits cleanly (no crash), ~100ms, no output or a "no context found" message
- [ ] **SC-02** — `hooks/load-context.sh` — Create a fake logbook file in expected location, run the hook — Expected: loads and outputs the handoff notes
- [ ] **SC-03** — `hooks/load-context.sh` — Verify no hardcoded paths — Expected: uses relative paths or environment variables

### install.sh Tests

- [ ] **IN-01** — Create temp dir with `.claude/` directory, run install.sh — Expected: detects Claude Code, copies commands and hook
- [ ] **IN-02** — Verify install.sh copies `hooks/load-context.sh` — Expected: hook script is installed
- [ ] **IN-03** — Verify install.sh handles the 6 CLI types mentioned in README — Expected: Claude Code, Codex, Cursor, Aider, Continue.dev, Generic
- [ ] **IN-04** — Grep install.sh for hardcoded paths — Expected: no `/Users/` or `/home/` paths

### Command/Skill Coherence

- [ ] **CS-01** — Scribe has NO skills directory (uses prompts directly, not the command->skill->agent pattern) — Expected: verify commands reference prompts correctly
- [ ] **CS-02** — Each adapter command references the corresponding prompt — Expected: `adapters/claude-code/commands/logbook.md` references `prompts/logbook.md` or embeds equivalent content
- [ ] **CS-03** — Codex adapter `AGENTS.md` contains equivalent instructions for all 4 commands — Expected: all 4 documented

### Cross-References

- [ ] **XR-01** — README badge "Commands-4" — Verify exactly 4 command files — Expected: 4
- [ ] **XR-02** — README badge "CLI_Support-6" — Verify 6 CLI adapters mentioned — Expected: Claude Code, Codex, Cursor, Aider, Continue.dev, Generic (note: Continue.dev adapter dir does NOT exist — only 5 adapter dirs found)
- [ ] **XR-03** — **BUG CHECK:** README claims 6 CLIs but only 5 adapter directories exist (aider, claude-code, codex, cursor, generic — no continue-dev) — Expected: mismatch should be documented or fixed
- [ ] **XR-04** — README "Part of the Agent Suite" lists only Agent-PROVE — Expected: should also list Trace, Cite, Drift, Litmus (outdated)
- [ ] **XR-05** — README GitHub clone URL is `https://github.com/saisumantatgit/Agent-Scribe.git` — Expected: verify repo exists

### Content Quality

- [ ] **CQ-01** — README tagline is "Nothing is lost." — Expected: present
- [ ] **CQ-02** — No stale product references (grep for "Shield", "GordonAI", "iVal") — Expected: no matches
- [ ] **CQ-03** — Templates follow the documented structure (AAR has Sustain/Improve/Stop, PIR has Five Whys, ADR is MADR v4.0.0) — Expected: all present
- [ ] **CQ-04** — README claims "~100ms" for load-context.sh — Expected: this should be verifiable by timing the hook

### Estimated Effort: 35 minutes

---

## Product 4: ml-preflight

### Risk Level: MEDIUM
### Priority: Test second

**Known Issues Found During Inspection:**
- `.claude/agents/` directory is empty (exists but no files)
- Has a `research/` directory (not listed in CLAUDE.md file structure)
- Has a `docs/` directory with PRODUCT_ARCHITECTURE.md (not mentioned in CLAUDE.md)
- `templates/` only has `known_fixes.yaml` (README mentions `ml-preflight-protocol.yaml` template but it does not exist)

### Structural Integrity

- [ ] **SI-01** — Validate `package.json` is valid JSON with name `"ml-preflight"` and version `"1.0.0"` — Expected: valid
- [ ] **SI-02** — Validate `.claude-plugin/plugin.json` is valid JSON with name `"ml-preflight"` and version `"1.0.0"` — Expected: valid
- [ ] **SI-03** — Validate `.claude-plugin/hooks.json` is valid JSON — Expected: valid, has session_start + before_command hooks
- [ ] **SI-04** — Verify hooks.json uses `"event"` key (not `"type"` like PROVE/Trace) — Note the inconsistency with Agent Suite products. ml-preflight hooks use `{event, action, message}` while Agent Suite uses `{type, command}`. This is a known schema difference between suites.
- [ ] **SI-05** — Verify all 6 command files exist in `.claude/commands/` — Expected: blackbox.md, build.md, check.md, handbook.md, launch.md, monitor.md
- [ ] **SI-06** — Verify all 6 skill directories exist in `.claude/skills/` each with SKILL.md — Expected: blackbox/, build/, check/, handbook/, launch/, monitor/
- [ ] **SI-07** — **BUG CHECK:** `.claude/agents/` directory exists but is EMPTY — Expected: either remove the empty directory or add agent definitions — CLAUDE.md does not mention agents
- [ ] **SI-08** — Verify all 4 Python scripts exist in `scripts/` — Expected: preflight_check.py, env_parity.py, poll_monitor.py, triage.py
- [ ] **SI-09** — Verify `install.sh` is executable with `#!/usr/bin/env bash` shebang — Expected: executable
- [ ] **SI-10** — Verify `.gitignore` exists and covers `__pycache__/` — Expected: exists, `__pycache__` present (note: `__pycache__` directory exists in scripts/)
- [ ] **SI-11** — Verify all 10 case study files exist in `case_studies/` — Expected: cs01 through cs10 markdown files
- [ ] **SI-12** — Verify all 4 platform JSON snapshots exist in `platforms/` — Expected: colab.json, hf_jobs.json, kaggle.json, sagemaker.json
- [ ] **SI-13** — Verify all 4 platform JSON files are valid JSON — Run: `python3 -c "import json; json.load(open('platforms/kaggle.json'))"` for each — Expected: all valid
- [ ] **SI-14** — Verify all 6 reference files exist in `references/` — Expected: cheatsheet.md, error_taxonomy.md, glossary.md, gpu_matrix.md, platform_matrix.md, triage_tree.md
- [ ] **SI-15** — Verify all 6 prompt files exist in `prompts/` — Expected: blackbox.md, build.md, check.md, handbook.md, launch.md, monitor.md
- [ ] **SI-16** — **BUG CHECK:** README says "Copy `templates/ml-preflight-protocol.yaml`" but templates/ only contains `known_fixes.yaml` — Expected: `ml-preflight-protocol.yaml` MISSING
- [ ] **SI-17** — Verify `templates/known_fixes.yaml` is valid YAML — Run: `python3 -c "import yaml; yaml.safe_load(open('templates/known_fixes.yaml'))"` — Expected: valid
- [ ] **SI-18** — Verify `LICENSE` exists — Expected: MIT
- [ ] **SI-19** — Verify `CONTRIBUTING.md` exists — Expected: exists
- [ ] **SI-20** — Verify `CLAUDE.md` exists — Expected: exists
- [ ] **SI-21** — Verify adapter directories: aider/, claude-code/, codex/, cursor/, generic/ — Expected: all exist (aider/ and cursor/ may be empty)

### Script Tests

- [ ] **SC-01** — `python3 -c "import py_compile; py_compile.compile('scripts/preflight_check.py')"` — Expected: compiles
- [ ] **SC-02** — `python3 -c "import py_compile; py_compile.compile('scripts/env_parity.py')"` — Expected: compiles
- [ ] **SC-03** — `python3 -c "import py_compile; py_compile.compile('scripts/poll_monitor.py')"` — Expected: compiles
- [ ] **SC-04** — `python3 -c "import py_compile; py_compile.compile('scripts/triage.py')"` — Expected: compiles
- [ ] **SC-05** — `python3 scripts/preflight_check.py --help` — Expected: prints usage, exits 0
- [ ] **SC-06** — `python3 scripts/env_parity.py --help` — Expected: prints usage, exits 0
- [ ] **SC-07** — `python3 scripts/poll_monitor.py --help` — Expected: prints usage, exits 0
- [ ] **SC-08** — `python3 scripts/triage.py --help` — Expected: prints usage, exits 0
- [ ] **SC-09** — `python3 scripts/preflight_check.py` with no arguments — Expected: helpful error about missing notebook path, not a stack trace
- [ ] **SC-10** — Create a minimal valid .ipynb notebook, run `python3 scripts/preflight_check.py test.ipynb --platform kaggle` — Expected: outputs preflight check results (PASS/FAIL items) with exit code
- [ ] **SC-11** — `python3 scripts/env_parity.py test.ipynb --platform kaggle` with valid notebook — Expected: outputs environment comparison
- [ ] **SC-12** — `python3 scripts/triage.py --error-log /dev/null` (empty log) — Expected: helpful output, not crash
- [ ] **SC-13** — Verify no scripts import external packages not in Python stdlib (except optional ones handled gracefully) — Expected: core functionality works with stdlib only

### install.sh Tests

- [ ] **IN-01** — Create temp dir with `.claude/` directory, run install.sh — Expected: detects Claude Code, copies commands + skills + scripts + references + case studies
- [ ] **IN-02** — Grep install.sh for hardcoded paths — Expected: no absolute paths
- [ ] **IN-03** — Verify install.sh copies `.claude-plugin/` to target — Expected: plugin.json and hooks.json copied

### Command/Skill Coherence

- [ ] **CS-01** — Each of the 6 commands references the corresponding skill — Check: build.md -> build skill, check.md -> check skill, etc. — Expected: all 6 mappings correct
- [ ] **CS-02** — plugin.json `skills` array has 6 entries with correct paths — Expected: all 6 skill paths resolve to existing SKILL.md files
- [ ] **CS-03** — plugin.json `scripts` array lists 4 scripts — Expected: all 4 paths resolve to existing .py files
- [ ] **CS-04** — Adapter commands match `.claude/commands/` — Expected: same 6 command names in `adapters/claude-code/commands/`

### Cross-References

- [ ] **XR-01** — README "Project Structure" section matches actual directory layout — Expected: match (note: `research/` and `docs/` exist but are NOT in the README structure listing)
- [ ] **XR-02** — README "10 case studies" claim — Verify exactly 10 case study files — Expected: 10 files (cs01-cs10)
- [ ] **XR-03** — README "4 platform snapshots" — Verify exactly 4 JSON files in `platforms/` — Expected: 4
- [ ] **XR-04** — README "6 reference documents" — Verify exactly 6 files in `references/` — Expected: 6
- [ ] **XR-05** — CLAUDE.md "5 reference documents" — **MISMATCH CHECK:** actual references/ has 6 files, CLAUDE.md says 6 — Expected: verify CLAUDE.md count matches

### Content Quality

- [ ] **CQ-01** — README tagline is "Pilots don't fly without preflight checks. ML engineers shouldn't push without them." — Expected: present
- [ ] **CQ-02** — No GordonAI-specific references — Grep for "GordonAI", "gordon", "Sandy", "sport psychology" — Expected: no matches
- [ ] **CQ-03** — CLAUDE.md explicitly states "All GordonAI-specific references have been generalized" — Verify this is true in all files — Expected: no GordonAI references anywhere
- [ ] **CQ-04** — Platform JSON snapshots have current data (March 2026 or later) — Expected: check dates or version numbers are current
- [ ] **CQ-05** — Case studies follow a consistent template structure — Expected: each has failure description, root cause, fix, governance rules, triage signature
- [ ] **CQ-06** — `known_fixes.yaml` is valid YAML with meaningful entries — Expected: valid, has at least several fix entries

### Estimated Effort: 40 minutes

---

## Product 5: Agent-Drift

### Risk Level: MEDIUM
### Priority: Test second

### Structural Integrity

- [ ] **SI-01** — Verify all 4 agent files exist in `.claude/agents/` — Expected: compliance-auditor.md, constraint-monitor.md, drift-detector.md, spec-extractor.md
- [ ] **SI-02** — Verify all 5 command files exist in `.claude/commands/` — Expected: drift-check.md, drift-fence.md, drift-lock.md, drift-report.md, drift-status.md
- [ ] **SI-03** — Verify all 5 skill directories exist in `.claude/skills/` each with SKILL.md — Expected: constraint-enforcement/, drift-analysis/, intent-capture/, session-audit/, status-dashboard/
- [ ] **SI-04** — Validate `package.json` is valid JSON with name `"agent-drift"` and version `"1.0.0"` — Expected: valid
- [ ] **SI-05** — Validate `.claude-plugin/plugin.json` is valid JSON with name `"agent-drift"` and version `"1.0.0"` — Expected: valid, matching
- [ ] **SI-06** — Validate `.claude-plugin/hooks.json` is valid JSON — Expected: valid, SessionStart hook
- [ ] **SI-07** — Verify `install.sh` is executable with `#!/bin/bash` shebang — Expected: executable
- [ ] **SI-08** — Verify `.gitignore` exists — Expected: exists
- [ ] **SI-09** — Verify `LICENSE` exists — Expected: MIT
- [ ] **SI-10** — Verify `CONTRIBUTING.md` exists — Expected: exists
- [ ] **SI-11** — Verify `CLAUDE.md` exists — Expected: exists
- [ ] **SI-12** — Verify `templates/drift-protocol.yaml` is valid YAML — Expected: valid
- [ ] **SI-13** — Verify `references/drift-types.md` exists — Expected: exists
- [ ] **SI-14** — Verify `references/spec-schema.md` exists — Expected: exists
- [ ] **SI-15** — Verify `docs/adr/ADR-002-five-commands-not-three.md` exists — Expected: exists
- [ ] **SI-16** — Verify 5 prompt files exist in `prompts/` — Expected: drift-check.md, drift-fence.md, drift-lock.md, drift-report.md, drift-status.md
- [ ] **SI-17** — Verify adapter directories exist — Expected: aider/, claude-code/, codex/, cursor/, generic/ (aider/ and cursor/ may be empty)

### Script Tests

- [ ] **SC-01** — Agent-Drift has no Python scripts — Expected: N/A (skip)

### install.sh Tests

- [ ] **IN-01** — Create temp dir with `.claude/` directory, run install.sh — Expected: detects Claude Code, copies commands, agents, skills, hooks, templates
- [ ] **IN-02** — Verify install.sh copies `drift-protocol.yaml` template — Expected: template installed
- [ ] **IN-03** — Grep install.sh for hardcoded paths — Expected: no absolute paths

### Command/Skill Coherence

- [ ] **CS-01** — CLAUDE.md command-to-skill-to-agent mapping — Verify: drift-lock -> intent-capture -> spec-extractor, drift-check -> drift-analysis -> drift-detector, drift-fence -> constraint-enforcement -> constraint-monitor, drift-status -> status-dashboard -> (no agent), drift-report -> session-audit -> compliance-auditor — Expected: all mappings resolve to existing files
- [ ] **CS-02** — Adapter commands in `adapters/claude-code/commands/` match `.claude/commands/` — Expected: same 5 command names
- [ ] **CS-03** — Each command .md file references the correct skill name — Expected: consistent with CLAUDE.md mapping

### Cross-References

- [ ] **XR-01** — README badge "Commands-5" — Verify exactly 5 command files — Expected: 5
- [ ] **XR-02** — README badge "Platforms-5" — Verify 5 platform adapters — Expected: 5 adapter dirs
- [ ] **XR-03** — README "8 Drift Types" section — Verify all 8 types are defined in `references/drift-types.md` — Expected: all 8 match
- [ ] **XR-04** — README "Part of the Agent Suite" lists PROVE, Trace, Scribe, Cite, Drift — Expected: all URLs are valid
- [ ] **XR-05** — CLAUDE.md 8 drift types match README — Expected: identical sets
- [ ] **XR-06** — CLAUDE.md 5 commands match README — Expected: identical

### Content Quality

- [ ] **CQ-01** — README tagline is "Not on my watch." — Expected: present
- [ ] **CQ-02** — No stale product references — Grep for "Shield", "GordonAI", "iVal", "ProSure" — Expected: no matches
- [ ] **CQ-03** — `drift-protocol.yaml` template has meaningful defaults matching README examples — Expected: severities, monitoring, scoring, verdicts sections all present and match documentation
- [ ] **CQ-04** — Research citations in README are plausible (GitHub Survey 2024, GitClear 2024, etc.) — Expected: citation formats look real (note: cannot verify URLs without execution)

### Estimated Effort: 25 minutes

---

## Product 6: Agent-Litmus

### Risk Level: MEDIUM
### Priority: Test second

**Known Issues Found During Inspection:**
- plugin.json uses `"name": "Agent-Litmus"` (PascalCase) while all other products use lowercase `"agent-*"` — naming inconsistency
- hooks.json uses a different schema format: `{hooks: {SessionStart: {message, display}}}` (nested object) vs all other products which use `{hooks: [{type, command}]}` (array) — schema inconsistency
- plugin.json has a much more detailed structure (commands, agents, suite fields) than other products — possibly a newer format

### Structural Integrity

- [ ] **SI-01** — Verify all 5 agent files exist in `.claude/agents/` — Expected: assertion-analyzer.md, edge-detector.md, mutation-reasoner.md, quality-aggregator.md, test-improver.md
- [ ] **SI-02** — Verify all 5 command files exist in `.claude/commands/` — Expected: litmus-edge.md, litmus-fix.md, litmus-report.md, litmus-scan.md, litmus-strength.md
- [ ] **SI-03** — Verify all 5 skill directories exist in `.claude/skills/` each with SKILL.md — Expected: edge-analysis/, strength-analysis/, test-audit/, test-fix/, test-report/
- [ ] **SI-04** — Validate `package.json` is valid JSON with name `"agent-litmus"` and version `"1.0.0"` — Expected: valid
- [ ] **SI-05** — Validate `.claude-plugin/plugin.json` is valid JSON — Expected: valid
- [ ] **SI-06** — **BUG CHECK:** plugin.json name is `"Agent-Litmus"` (PascalCase) — All other products use lowercase (`"agent-prove"`, `"agent-trace"`, etc.) — Expected: should be `"agent-litmus"` for consistency
- [ ] **SI-07** — **BUG CHECK:** hooks.json uses `{hooks: {SessionStart: {message, display}}}` format — All other Agent Suite products use `{hooks: [{type, command}]}` format — Expected: schema inconsistency should be documented or normalized
- [ ] **SI-08** — Verify `install.sh` is executable with `#!/usr/bin/env bash` shebang — Expected: executable
- [ ] **SI-09** — Verify `.gitignore` exists — Expected: exists
- [ ] **SI-10** — Verify `LICENSE` exists — Expected: MIT
- [ ] **SI-11** — Verify `CONTRIBUTING.md` exists — Expected: exists
- [ ] **SI-12** — Verify `CLAUDE.md` exists — Expected: exists
- [ ] **SI-13** — Verify `templates/litmus-protocol.yaml` is valid YAML — Expected: valid
- [ ] **SI-14** — Verify `references/` has 3 files — Expected: assertion-classification.md, edge-case-taxonomy.md, violation-types.md
- [ ] **SI-15** — Verify 5 prompt files exist in `prompts/` — Expected: litmus-edge.md, litmus-fix.md, litmus-report.md, litmus-scan.md, litmus-strength.md
- [ ] **SI-16** — Verify adapter directories exist — Expected: aider/, claude-code/, codex/, cursor/, generic/ (aider/ and cursor/ may be empty)

### Script Tests

- [ ] **SC-01** — Agent-Litmus has no Python scripts — Expected: N/A (skip)

### install.sh Tests

- [ ] **IN-01** — Create temp dir with `.claude/` directory, run install.sh — Expected: detects Claude Code, copies commands, agents, skills, references, templates
- [ ] **IN-02** — Grep install.sh for hardcoded paths — Expected: no absolute paths
- [ ] **IN-03** — Verify install.sh copies `references/` directory (assertion-classification is needed at runtime) — Expected: references copied

### Command/Skill Coherence

- [ ] **CS-01** — CLAUDE.md command-to-skill-to-agent mapping — Verify: litmus-scan -> test-audit -> assertion-analyzer, litmus-edge -> edge-analysis -> edge-detector, litmus-strength -> strength-analysis -> mutation-reasoner, litmus-fix -> test-fix -> test-improver, litmus-report -> test-report -> quality-aggregator — Expected: all mappings resolve to existing files
- [ ] **CS-02** — plugin.json `commands` array maps command names to skill names — Verify these match the actual files — Expected: all 5 command-to-skill mappings in plugin.json resolve correctly
- [ ] **CS-03** — plugin.json `agents` array lists 5 agents — Verify all exist in `.claude/agents/` — Expected: all 5 exist
- [ ] **CS-04** — Adapter commands in `adapters/claude-code/commands/` match `.claude/commands/` — Expected: same 5 command names

### Cross-References

- [ ] **XR-01** — README states "5 commands, 5 agents, 12 violation types, Test Quality Score 0-100" — Verify: 5 commands, 5 agents, 12 types in reference docs — Expected: all match
- [ ] **XR-02** — CLAUDE.md "12 Violation Types" match README table — Expected: identical 12 types
- [ ] **XR-03** — CLAUDE.md file structure section matches actual layout — Expected: match
- [ ] **XR-04** — README "Part of the Agent Suite" lists 6 products — Verify all 6 listed — Expected: PROVE, Trace, Drift, Litmus, Cite, Scribe

### Content Quality

- [ ] **CQ-01** — README tagline is "The test your tests have to pass." — Expected: present
- [ ] **CQ-02** — No stale product references — Grep for "Shield", "GordonAI", "iVal" — Expected: no matches
- [ ] **CQ-03** — `litmus-protocol.yaml` template has the documented configuration sections — Expected: violations, test_patterns, tqs thresholds, scoring weights, ignore
- [ ] **CQ-04** — TQS formula in CLAUDE.md matches README formula — Expected: `TQS = assertion_strength * 0.40 + violation_penalty * 0.30 + edge_coverage * 0.30` in both

### Estimated Effort: 25 minutes

---

## Product 7: Agent-Cite

### Risk Level: MEDIUM
### Priority: Test second

### Structural Integrity

- [ ] **SI-01** — Verify all 3 agent files exist in `.claude/agents/` — Expected: citation-fixer.md, citation-scanner.md, source-verifier.md
- [ ] **SI-02** — Verify all 3 command files exist in `.claude/commands/` — Expected: cite-audit.md, cite-fix.md, cite-report.md
- [ ] **SI-03** — Verify all 3 skill directories exist in `.claude/skills/` each with SKILL.md — Expected: citation-fix/, evidence-audit/, evidence-report/
- [ ] **SI-04** — Validate `package.json` is valid JSON with name `"agent-cite"` and version `"1.0.0"` — Expected: valid
- [ ] **SI-05** — Validate `.claude-plugin/plugin.json` is valid JSON with name `"agent-cite"` and version `"1.0.0"` — Expected: valid
- [ ] **SI-06** — Validate `.claude-plugin/hooks.json` is valid JSON with SessionStart hook — Expected: valid
- [ ] **SI-07** — Verify `install.sh` is executable with `#!/bin/bash` shebang — Expected: executable
- [ ] **SI-08** — Verify `.gitignore` exists — Expected: exists
- [ ] **SI-09** — Verify `LICENSE` exists — Expected: MIT
- [ ] **SI-10** — Verify `CONTRIBUTING.md` exists — Expected: exists
- [ ] **SI-11** — Verify `CLAUDE.md` exists — Expected: exists
- [ ] **SI-12** — Verify `scripts/web_verify.py` exists — Expected: exists
- [ ] **SI-13** — Verify `templates/evidence-protocol.yaml` is valid YAML — Expected: valid
- [ ] **SI-14** — Verify `references/` has 2 files — Expected: evidence-protocol-spec.md, violation-types.md
- [ ] **SI-15** — Verify 3 prompt files in `prompts/` — Expected: cite-audit.md, cite-fix.md, cite-report.md
- [ ] **SI-16** — Verify `docs/adr/ADR-001-three-tier-citation-model.md` exists — Expected: exists

### Script Tests

- [ ] **SC-01** — `python3 -c "import py_compile; py_compile.compile('scripts/web_verify.py')"` — Expected: compiles without error
- [ ] **SC-02** — `python3 scripts/web_verify.py --help` — Expected: prints help OR prints a helpful error about missing patchright dependency — should NOT crash with unhandled exception
- [ ] **SC-03** — `python3 scripts/web_verify.py` with no arguments — Expected: helpful error message, not a stack trace
- [ ] **SC-04** — Verify web_verify.py handles missing patchright gracefully — Expected: ImportError caught with a message like "pip install patchright" suggestion

### install.sh Tests

- [ ] **IN-01** — Create temp dir with `.claude/` directory, run install.sh — Expected: detects Claude Code, copies commands, agents, skills, hooks, templates, references
- [ ] **IN-02** — Verify install.sh copies `evidence-protocol.yaml` template — Expected: template installed
- [ ] **IN-03** — Grep install.sh for hardcoded paths — Expected: no absolute paths

### Command/Skill Coherence

- [ ] **CS-01** — CLAUDE.md command-to-skill-to-agent mapping — Verify: cite-audit -> evidence-audit -> citation-scanner, cite-fix -> citation-fix -> citation-fixer, cite-report -> evidence-report -> source-verifier — Expected: all mappings resolve to existing files
- [ ] **CS-02** — Adapter commands in `adapters/claude-code/commands/` match `.claude/commands/` — Expected: same 3 command names

### Cross-References

- [ ] **XR-01** — README badge "Commands-3" — Verify exactly 3 command files — Expected: 3
- [ ] **XR-02** — README badge "Platforms-5" — Verify 5 platform adapters — Expected: 5 adapter dirs
- [ ] **XR-03** — README "Violation Types" table lists 6 types — Verify `references/violation-types.md` has the same 6 — Expected: UNCITED_INFERENCE, UNVERIFIED_NUMBER, UNSUPPORTED_ABSENCE, BROKEN_CITATION, FALSE_ABSENCE, UNVERIFIABLE
- [ ] **XR-04** — README "Part of the Agent Suite" lists PROVE, Trace, Scribe, Cite — Expected: all URLs valid
- [ ] **XR-05** — CLAUDE.md violation types match README (note: CLAUDE.md lists 4 types, README lists 6) — Expected: verify which is authoritative

### Content Quality

- [ ] **CQ-01** — README tagline is "Cite it or it's opinion." — Expected: present
- [ ] **CQ-02** — No stale product references — Grep for "Shield", "GordonAI", "iVal" — Expected: no matches
- [ ] **CQ-03** — README correctly explains relationship to Agent-PROVE evidence auditing — Expected: notes that PROVE has basic /audit and Cite goes deeper
- [ ] **CQ-04** — `evidence-protocol.yaml` template matches README configuration example — Expected: severities, include/exclude, thresholds sections present

### Estimated Effort: 25 minutes

---

## Product 8: kaggle-ml-preflight

### Risk Level: LOW
### Priority: Test last

**Derivative of ml-preflight. Same structure, Kaggle-native defaults.**

### Structural Integrity

- [ ] **SI-01** — Validate `package.json` is valid JSON with name `"kaggle-ml-preflight"` and version `"1.0.0"` — Expected: valid
- [ ] **SI-02** — Validate `.claude-plugin/plugin.json` is valid JSON with name `"kaggle-ml-preflight"`, version `"1.0.0"`, platform `"kaggle"` — Expected: valid
- [ ] **SI-03** — Validate `.claude-plugin/hooks.json` is valid JSON — Expected: valid, has session_start + before_command (kaggle push) hooks
- [ ] **SI-04** — Verify all 6 command files exist in `.claude/commands/` — Expected: same 6 as ml-preflight
- [ ] **SI-05** — Verify all 6 skill directories exist in `.claude/skills/` each with SKILL.md — Expected: same 6 as ml-preflight
- [ ] **SI-06** — Verify all 4 Python scripts exist in `scripts/` — Expected: preflight_check.py, env_parity.py, poll_monitor.py, triage.py
- [ ] **SI-07** — Verify `install.sh` is executable with `#!/usr/bin/env bash` shebang — Expected: executable
- [ ] **SI-08** — Verify `.gitignore` exists — Expected: exists
- [ ] **SI-09** — Verify only `platforms/kaggle.json` exists (no colab/sagemaker/hf_jobs) — Expected: only kaggle.json
- [ ] **SI-10** — Verify `platforms/kaggle.json` is valid JSON — Expected: valid
- [ ] **SI-11** — Verify all 10 case study files — Expected: cs01-cs10
- [ ] **SI-12** — Verify references/ has 5 files (no platform_matrix.md — Kaggle only) — Expected: cheatsheet.md, error_taxonomy.md, glossary.md, gpu_matrix.md, triage_tree.md
- [ ] **SI-13** — Verify `templates/kaggle-preflight-protocol.yaml` exists and is valid YAML — Expected: valid (note: this template EXISTS here but is missing from ml-preflight)
- [ ] **SI-14** — Verify `templates/known_fixes.yaml` is valid YAML — Expected: valid
- [ ] **SI-15** — Verify `LICENSE`, `CONTRIBUTING.md`, `CLAUDE.md` exist — Expected: all exist

### Script Tests

- [ ] **SC-01** — All 4 scripts compile — Run: `py_compile.compile()` for each — Expected: all compile
- [ ] **SC-02** — `python3 scripts/preflight_check.py --help` — Expected: help text, NO `--platform` flag required (Kaggle is default)
- [ ] **SC-03** — `python3 scripts/env_parity.py --help` — Expected: help text, no `--platform` flag
- [ ] **SC-04** — `python3 scripts/poll_monitor.py --help` — Expected: help text, `--kernel-id` is the primary argument
- [ ] **SC-05** — `python3 scripts/triage.py --help` — Expected: help text
- [ ] **SC-06** — Verify scripts do NOT require `--platform kaggle` (should be hardcoded default) — Expected: no platform flag needed
- [ ] **SC-07** — `python3 scripts/preflight_check.py` with no args — Expected: helpful error, not crash

### install.sh Tests

- [ ] **IN-01** — Run install.sh in temp dir — Expected: installs Kaggle-specific files
- [ ] **IN-02** — Grep install.sh for hardcoded paths — Expected: none

### Command/Skill Coherence

- [ ] **CS-01** — 6 commands map to 6 skills — Expected: all resolve
- [ ] **CS-02** — Adapter commands match `.claude/commands/` — Expected: same 6

### Cross-References

- [ ] **XR-01** — README references ml-preflight as parent — Expected: link to github.com/saisumantatgit/ml-preflight
- [ ] **XR-02** — README "6-Item Kaggle Checklist" — Verify all 6 items are also in the check skill — Expected: consistent

### Content Quality

- [ ] **CQ-01** — README tagline is "Stop burning your 30hr Kaggle GPU quota on preventable failures." — Expected: present
- [ ] **CQ-02** — No GordonAI references — Expected: none
- [ ] **CQ-03** — No Colab/SageMaker/HF-specific content leaked in — Expected: Kaggle only
- [ ] **CQ-04** — `kaggle.json` platform snapshot has current Kaggle environment data (Python 3.11, CUDA 12.5, etc.) — Expected: matches README table

### Estimated Effort: 20 minutes

---

## Product 9: colab-ml-preflight

### Risk Level: LOW
### Priority: Test last

**Derivative of ml-preflight. Same structure, Colab-native defaults.**

### Structural Integrity

- [ ] **SI-01** — Validate `package.json` is valid JSON with name `"colab-ml-preflight"` and version `"1.0.0"` — Expected: valid
- [ ] **SI-02** — Validate `.claude-plugin/plugin.json` is valid JSON with name `"colab-ml-preflight"` and version `"1.0.0"` — Expected: valid
- [ ] **SI-03** — Validate `.claude-plugin/hooks.json` is valid JSON — Expected: valid, has session_start + before_command (drive.mount) hooks
- [ ] **SI-04** — Verify all 6 command files exist in `.claude/commands/` — Expected: same 6 as ml-preflight
- [ ] **SI-05** — Verify all 6 skill directories exist in `.claude/skills/` each with SKILL.md — Expected: same 6
- [ ] **SI-06** — Verify all 4 Python scripts exist in `scripts/` — Expected: preflight_check.py, env_parity.py, poll_monitor.py, triage.py
- [ ] **SI-07** — Verify `install.sh` is executable with `#!/usr/bin/env bash` shebang — Expected: executable
- [ ] **SI-08** — Verify `.gitignore` exists — Expected: exists
- [ ] **SI-09** — Verify only `platforms/colab.json` exists (no kaggle/sagemaker/hf_jobs) — Expected: only colab.json
- [ ] **SI-10** — Verify `platforms/colab.json` is valid JSON — Expected: valid
- [ ] **SI-11** — Verify all 10 case study files — Expected: cs01-cs10
- [ ] **SI-12** — Verify references/ has 5 files — Expected: cheatsheet.md, error_taxonomy.md, glossary.md, gpu_matrix.md, triage_tree.md
- [ ] **SI-13** — Verify `templates/colab-preflight-protocol.yaml` exists and is valid YAML — Expected: valid
- [ ] **SI-14** — Verify `templates/known_fixes.yaml` is valid YAML — Expected: valid
- [ ] **SI-15** — Verify `LICENSE`, `CONTRIBUTING.md`, `CLAUDE.md` exist — Expected: all exist

### Script Tests

- [ ] **SC-01** — All 4 scripts compile — Run: `py_compile.compile()` for each — Expected: all compile
- [ ] **SC-02** — `python3 scripts/preflight_check.py --help` — Expected: help text, no `--platform` flag required
- [ ] **SC-03** — `python3 scripts/env_parity.py --help` — Expected: help text, no `--platform` flag
- [ ] **SC-04** — `python3 scripts/poll_monitor.py --help` — Expected: help text
- [ ] **SC-05** — `python3 scripts/triage.py --help` — Expected: help text
- [ ] **SC-06** — Verify scripts default to Colab platform — Expected: no `--platform` flag needed
- [ ] **SC-07** — `python3 scripts/preflight_check.py` with no args — Expected: helpful error

### install.sh Tests

- [ ] **IN-01** — Run install.sh in temp dir — Expected: installs Colab-specific files
- [ ] **IN-02** — Grep install.sh for hardcoded paths — Expected: none

### Command/Skill Coherence

- [ ] **CS-01** — 6 commands map to 6 skills — Expected: all resolve
- [ ] **CS-02** — Adapter commands match `.claude/commands/` — Expected: same 6

### Cross-References

- [ ] **XR-01** — README references ml-preflight as parent — Expected: link to github.com/saisumantatgit/ml-preflight
- [ ] **XR-02** — README "Colab Tier Comparison" data is accurate — Expected: Free/Pro/Pro+ tiers with correct GPU options

### Content Quality

- [ ] **CQ-01** — README tagline is "Stop losing training runs to Colab disconnects and silent failures." — Expected: present
- [ ] **CQ-02** — No GordonAI references — Expected: none
- [ ] **CQ-03** — No Kaggle/SageMaker/HF-specific content leaked in — Expected: Colab only
- [ ] **CQ-04** — `colab.json` platform snapshot has current Colab environment data (Python 3.12) — Expected: matches README
- [ ] **CQ-05** — Colab-specific error patterns section in README is Colab-only — Expected: no Kaggle-specific errors

### Estimated Effort: 20 minutes

---

## Cross-Suite Tests (All 9 Products)

### Naming Consistency

- [ ] **XS-01** — All Agent Suite plugin.json files use lowercase `"agent-*"` naming — Known issue: Agent-Litmus uses `"Agent-Litmus"` (PascalCase)
- [ ] **XS-02** — All hooks.json files use the same schema format — Known issue: Agent-Litmus uses object format `{SessionStart: {message}}` while others use array format `[{type: "SessionStart", command: "..."}]`; ml-ops suite uses a different format `[{event, action, message}]`
- [ ] **XS-03** — All package.json version fields match corresponding plugin.json version fields — Known issue: Agent-PROVE has 1.2.0 vs 1.2.1 mismatch

### Suite Link Consistency

- [ ] **XS-04** — Every product's "Part of the Agent Suite" section lists the SAME set of products — Expected: PROVE, Trace, Scribe, Cite, Drift, Litmus (check: Scribe README only lists PROVE; Trace only lists PROVE and Scribe)
- [ ] **XS-05** — All GitHub URLs in suite sections follow `https://github.com/saisumantatgit/Agent-*` pattern — Expected: consistent
- [ ] **XS-06** — ml-preflight variants' "Part of the ml-preflight Family" sections link to each other correctly — Expected: consistent

### Structural Consistency

- [ ] **XS-07** — Agent-Scribe is the only product missing: package.json, .claude-plugin/, CLAUDE.md, CONTRIBUTING.md, .gitignore — Expected: these should be added for consistency
- [ ] **XS-08** — All products with install.sh have executable permission — Expected: all 8 that have install.sh are executable (Agent-PROVE has no install.sh)
- [ ] **XS-09** — All adapter directories follow the same pattern: aider/, claude-code/, codex/, cursor/, generic/ — Expected: consistent across all 8 products with adapters
- [ ] **XS-10** — All products have a LICENSE file — Expected: all 9 have MIT LICENSE

### Estimated Effort: 15 minutes

---

## Summary of Known Issues Found During Inspection

| # | Product | Issue | Severity |
|---|---------|-------|----------|
| 1 | Agent-PROVE | package.json version `1.2.0` != plugin.json version `1.2.1` | error |
| 2 | Agent-PROVE | No install.sh (inconsistent with all other products) | warning |
| 3 | Agent-Scribe | Missing package.json | error |
| 4 | Agent-Scribe | Missing .claude-plugin/ directory (no plugin.json, hooks.json at root) | error |
| 5 | Agent-Scribe | Missing CLAUDE.md | warning |
| 6 | Agent-Scribe | Missing CONTRIBUTING.md | warning |
| 7 | Agent-Scribe | Missing .gitignore | warning |
| 8 | Agent-Scribe | Missing .claude/ directory at root (only in adapters/) | warning |
| 9 | Agent-Scribe | README claims 6 CLIs but only 5 adapter dirs (no continue-dev) | warning |
| 10 | Agent-Litmus | plugin.json name is "Agent-Litmus" not "agent-litmus" | warning |
| 11 | Agent-Litmus | hooks.json uses different schema format than all other products | warning |
| 12 | ml-preflight | .claude/agents/ directory is empty | info |
| 13 | ml-preflight | templates/ml-preflight-protocol.yaml missing (README references it) | error |
| 14 | ml-preflight | research/ and docs/ dirs not in README structure listing | info |
| 15 | All (Trace, ml-ops) | __pycache__/ directories checked into repos | warning |
| 16 | Cross-Suite | hooks.json schema inconsistency across products (3 different formats) | warning |
| 17 | Cross-Suite | "Part of the Agent Suite" sections are stale in older products | info |

---

## Total Estimated Effort

| Product | Minutes |
|---------|---------|
| Agent-PROVE | 30 |
| Agent-Trace | 45 |
| Agent-Scribe | 35 |
| ml-preflight | 40 |
| Agent-Drift | 25 |
| Agent-Litmus | 25 |
| Agent-Cite | 25 |
| kaggle-ml-preflight | 20 |
| colab-ml-preflight | 20 |
| Cross-Suite | 15 |
| **Total** | **280 minutes (~4.7 hours)** |

---

## Execution Order

1. **Wave 1 (HIGH risk):** Agent-PROVE, Agent-Trace, Agent-Scribe — in parallel where possible
2. **Wave 2 (MEDIUM risk):** ml-preflight, Agent-Drift, Agent-Litmus, Agent-Cite — in parallel
3. **Wave 3 (LOW risk):** kaggle-ml-preflight, colab-ml-preflight — in parallel
4. **Wave 4 (Cross-suite):** Cross-Suite consistency tests — after all individual products pass
