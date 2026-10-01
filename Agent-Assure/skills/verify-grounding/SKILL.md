---
name: verify-grounding
description: >
  Verify that every factual claim in a draft can be traced, mechanically, to a
  source captured in the evidence store. Runs the deterministic
  Agent-Assure engine (no model, no network) and returns a
  PASS / NEEDS_WORK / FAIL gate with per-claim verdicts. The engine — not your
  reading — decides grounding. It checks the draft against what the session
  READ; it does not judge whether the source is right.
license: MIT
metadata:
  domain: verification-first-research
  maturity: beta
  primary_use: grounding-gate
allowed-tools: Bash Read
---

# Verify Grounding

Show whether an AI-generated draft is **traceable**: every factual claim must be
supported by a source captured verbatim in the evidence store. The verdict is
produced by a deterministic Python engine (`scripts/ground_check.py`) — no model
judges grounding. Your job is to run the engine, surface its verdict, and help
remediate — never to decide grounding yourself.

## What this gate does NOT prove

Say this plainly when you report a PASS. A PASS is not a certificate of truth.

- **It does not verify where the evidence came from.** The gate checks the draft
  against what the session READ. The agent's own tool choices are trusted, so a
  file the agent wrote and then read back counts as a verbatim source.
- **It checks verbatim provenance, not meaning.** A faithful paraphrase is
  REFUSED, not passed. Roughly a third of honest claims read `UNGROUNDED` on the
  calibration corpus (Error-A 0.320, n=52, CR-004). An `UNGROUNDED` verdict means
  "I could not mechanically trace this", never "this is false".
- **It does not check whether the source is correct**, current, or competent.
- **"We found no evidence of X" is only as good as the searches recorded.** The
  searches behind an absence claim are supplied by the agent, not observed.
- **A multi-line `<!-- ... -->` note is scored as claims** and will fail the
  draft (J-48). Keep authoring notes on one line.
- **The store is not session-bounded.** It is appended to and never rotated, and
  no record carries a session id, so a claim can be traced to a source captured
  in an EARLIER session. Say "captured in the evidence store", never "retrieved
  this session" (J-38).

These are scope, not bugs — each is pinned by a test in
`tests/test_product_claim.py`, so if one ever stops being true this list is
wrong and must be updated.

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
- any point where "every claim must trace to a captured source" is
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
was captured, or the hook is not installed/firing. Do not present a
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

**PASS** — "Grounding gate: PASS (score N ≥ threshold, empty retained-violation
appendix). Every scored claim traces to a captured source."

**NEEDS_WORK / FAIL** — present the failing claims as a table (claim, verdict,
why), grouped by verdict. Lead with any `UNVERIFIED_CITATION` — those are
citations to sources that were never retrieved (fabricated), the highest-severity
failure. Under ADR-005 (2026-07-12), ANY retained violation-class verdict —
not just `UNVERIFIED_CITATION` — caps the gate at NEEDS_WORK regardless of
score; PASS requires zero retained violations. See
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

## Verdict → gate summary (ADR-005 semantics, accepted 2026-07-12)

| Gate | Condition |
|---|---|
| PASS | **empty retained-violation appendix** (zero violation-class verdicts) AND score ≥ threshold |
| NEEDS_WORK | score ≥ 60 AND (any retained violation OR below threshold OR vacuous) |
| FAIL | score < 60 — checked FIRST, so a sub-60 score is FAIL even when other overrides apply |

PASS means **every scored claim is grounded**, not "at least threshold% are" —
one retained violation caps the gate at NEEDS_WORK regardless of score. The
score threshold (default 90) is a secondary bar. NON_CLAIM statements (headers,
questions, pure opinion) are excluded from the scored denominator.

## References

- [references/grounding-failure-types.md](../../references/grounding-failure-types.md) — every verdict, what it catches, how to fix
- Engine internals, JSONL format, and grounding tiers: the plugin `README.md`
