# Insights Log — Agents Infra

> Cross-cutting observations captured during development. See TEMPLATE.md for entry format and graduation criteria.

---

### [2026-07-14] Env-var-conditional egress is invisible to document review — only observed runs catch it

**Category:** gotcha
**Source:** session observation (TDR-001 graphify pilot, Gate 1)
**Products affected:** suite-wide (any third-party tool evaluation)

**Insight:**
A tool can be genuinely zero-egress in its documented default AND silently exfiltrating on a given machine, because routing decisions keyed on ambient env vars (`GEMINI_API_KEY`) change behavior without any config file or flag. Reading source/README rates the tool; only checking the *environment it will actually run in* rates the deployment. Egress verification therefore needs two sides: a deny-test (proves no network is needed) plus an env audit + observed run (proves none is attempted *here*).

**Evidence:**
graphify skill.md Step 3 routes semantic extraction to `generativelanguage.googleapis.com` iff `GEMINI_API_KEY`/`GOOGLE_API_KEY` is set — one tip line, no consent gate. The key WAS set on the pilot machine. Caught in Gate 0 env sweep before any doc content was processed; all runs then used `env -u`. See `docs/tdr/evidence/TDR-001-gate-evidence.md`.

**Graduation target:**
- [ ] Root `CLAUDE.md` Conventions or Gotchas — if adopted as a standing third-party-tool gate rule (candidate wording: "egress verification = deny-test + env-key audit + observed run, on the target machine")

### [2026-07-14] Nested git repos silently shrink every indexer's corpus — verify scan scope before comparing tools

**Category:** gotcha
**Source:** session observation (TDR-001 pilot, corpus check)
**Products affected:** suite-wide (this monorepo's workspace layout)

**Insight:**
Both indexers in the A/B (CMM and graphify) independently excluded the six Agent-* sub-directories because they are nested git repos — the "1,900-file monorepo" is an 80-file corpus to any repo-boundary-respecting tool. Any future tool evaluation, index, or search sweep on agents-infra must first break down detected files by top-level directory, or results will quietly describe only Agent-Assure + docs.

**Evidence:**
CMM `index_repository` excluded dirs list; graphify `detect()` per-directory breakdown (80 files: 50 Agent-Assure, 16 docs, 14 other). CR-001 delta #1.

**Graduation target:**
- [ ] Root `CLAUDE.md` Gotchas — workspace-layout consequence, cross-cutting

<!-- Graduated insights log:
     (record destination when an insight is promoted)
-->
