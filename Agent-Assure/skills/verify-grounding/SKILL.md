---
name: verify-grounding
description: >
  Verify that every factual claim in a draft is grounded in a source actually
  retrieved this session. Runs the deterministic Agent-Assure grounding engine
  (no LLM judgment) against the captured evidence store and returns a
  PASS / NEEDS_WORK / FAIL gate with per-claim verdicts. The engine — not your
  reading — decides grounding.
license: MIT
metadata:
  domain: verification-first-research
  maturity: beta
  primary_use: grounding-gate
allowed-tools: Bash Read
---

# Verify Grounding

Prove that an AI-generated draft is grounded: every factual claim must be
supported by a source that was **actually retrieved this session** and captured
verbatim in the evidence store. The verdict is produced by a deterministic
Python engine (`scripts/ground_check.py`) — no model judges grounding. Your job
is to run the engine, surface its verdict, and help remediate — never to decide
grounding yourself.

## The moat: mechanical, not model-judged

Deep-research agents hallucinate citations 11–57% of the time in production. The
failure is invisible precisely because the citation *looks* real. Agent-Assure
closes this by making grounding a **mechanical** check:

- A `PostToolUse` capture hook records every retrieved source (Exa fetch, Read,
  WebFetch, DDG fetch) verbatim into `.assure/evidence-store.jsonl` as it
  happens — you do nothing.
- The engine decomposes the draft into atomic claims, classifies each, and
  checks each against the store using string / lexical / numeric tests. A cited
  `[S9]` whose source_id is not in the store is caught as `UNVERIFIED_CITATION`
  — the fabricated-citation failure — deterministically.

Because the check is mechanical, it cannot be talked out of a verdict. Do not
supplement or override it with your own reading. That independence IS the value.

## Trigger

Activate this skill when:

- verifying an AI-generated research report, analysis, or memo BEFORE it reaches
  a human reader
- the user runs `/assure-verify <draft>`
- any point where "every claim must trace to a source retrieved this session" is
  the standard

Do NOT activate when:

- the output is pure code, formatting, or scaffolding (no factual claims)
- the draft cites sources from PRIOR sessions not in the current evidence store
  (the store is per-session; grounding is against THIS session's retrievals)

## Arguments

- **DRAFT** (required): path to the draft file to verify.
- `--store PATH`: evidence store JSONL (default `.assure/evidence-store.jsonl`).
- `--threshold FLOAT`: grounding score threshold 0–100 (default 90).

## Workflow

### 1. Locate the evidence store

Default is `.assure/evidence-store.jsonl` in the project root (populated by the
capture hook during this session's research). If it is missing or empty, STOP
and tell the user: the gate has nothing to ground against — either no research
was captured this session, or the hook is not installed/firing. Do not present a
verdict against an empty store as meaningful (the engine correctly reports
NEEDS_WORK + `vacuous: true` there — surface that, do not spin it as a pass).

### 2. Run the engine (do NOT judge grounding yourself)

```bash
"${CLAUDE_PLUGIN_ROOT}/.venv/bin/python" "${CLAUDE_PLUGIN_ROOT}/scripts/ground_check.py" \
    --draft "<DRAFT>" \
    --store "<STORE>" \
    --threshold <THRESHOLD> \
    --json
```

- If `${CLAUDE_PLUGIN_ROOT}` is not set in this context, use the plugin's install
  directory (where `scripts/ground_check.py` lives) and its `.venv/bin/python`.
- Prefer `--json` for the full structured report on stdout.
- Exit code: `0` = PASS, `1` = NEEDS_WORK or FAIL.
- Without `--json`, the engine writes `grounding-report.yaml` to CWD and prints a
  one-line summary.

### 3. Read the report

The JSON report carries:
- `gate`: `PASS` | `NEEDS_WORK` | `FAIL`
- `grounding_score`: 0–100 (GROUNDED + ABSENCE_SUPPORTED over scored claims)
- `vacuous`: `true` when no scored claims exist (empty denominator → NEEDS_WORK)
- per-claim verdicts (`GROUNDED`, `UNVERIFIED_CITATION`, `UNGROUNDED`, …)

### 4. Present the result

**PASS** — "Grounding gate: PASS (score N ≥ threshold, no fabricated citations).
Every scored claim traces to a captured source."

**NEEDS_WORK / FAIL** — present the failing claims as a table (claim, verdict,
why), grouped by verdict. Lead with any `UNVERIFIED_CITATION` — those are
citations to sources that were never retrieved (fabricated), the highest-severity
failure; they cap the gate at NEEDS_WORK regardless of score. See
[references/grounding-failure-types.md](../../references/grounding-failure-types.md)
for what each verdict means and how to remediate.

### 5. Remediate (optional, user-directed)

For each failing claim, the fix is one of:
- add or repair a citation to a source that IS in the store,
- retrieve the missing source (re-run the research so the hook captures it), then
  re-verify,
- or remove / soften the claim if no retrieved source supports it.

**Never** "fix" a claim by editing the evidence store. The store is the record of
what was actually retrieved; editing it to pass the gate defeats the entire point
and is the one action this tool exists to make impossible.

## Citation convention

Place citation markers **inside** the sentence, before the final period:
`... 128000 operations per second [S1].` — not `... per second. [S1]`. A citation
after the sentence-final period is parsed as its own segment and detaches from its
claim (which then reads as UNCITED). This is fail-safe (it over-flags, never
under-flags), but note it when a draft's claims come back UNCITED unexpectedly.

## Verdict → gate summary

| Gate | Condition |
|---|---|
| PASS | score ≥ threshold AND zero `UNVERIFIED_CITATION` |
| NEEDS_WORK | 60 ≤ score < threshold, OR any `UNVERIFIED_CITATION`, OR vacuous (no scored claims) |
| FAIL | score < 60 |

NON_CLAIM statements (headers, questions, pure opinion) are excluded from the
scored denominator.

## References

- [references/grounding-failure-types.md](../../references/grounding-failure-types.md) — every verdict, what it catches, how to fix
- Engine internals, JSONL format, and grounding tiers: the plugin `README.md`
