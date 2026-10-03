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
  REFUSED, not passed. **Roughly two in five** honest claims read `UNGROUNDED` on
  the calibration corpus (**Error-A 0.400, n=52, CR-007** — it rose from 0.320
  when relational grounding was demoted, ADR-007). An `UNGROUNDED` verdict means
  "I could not mechanically trace this", never "this is false".
- **It does not check whether the source is correct**, current, or competent.
- **"We found no evidence of X" is only as good as the searches recorded.** The
  searches behind an absence claim are supplied by the agent, not observed.
- **A multi-line `<!-- ... -->` note is scored as claims** and will fail the
  draft (J-48). Keep authoring notes on one line.
- **In `claude -p` / CI / piped mode the capture hook never runs**, so the store
  is empty and EVERY claim reads `UNCITED`. If you see a draft where nothing is
  cited and the store is missing or empty, suspect this before suspecting the
  draft. Agent-Assure needs an interactive session to capture evidence. Verified
  2026-10-02 across three hook registrations (plugin, project settings, explicit
  `--settings`) — none fired, while the tool call itself ran.
- **The store is not session-bounded unless you ask it to be.** Every captured
  record carries a `session_id`, and passing `--session-id <id>` makes the gate
  REFUSE a store holding any other session's evidence. Without that flag the
  store is appended to and never rotated, so a claim can trace to a source
  captured in an EARLIER session. So: describe evidence as "captured in the
  evidence store" by default, and describe a run as session-scoped ONLY when it
  actually passed `--session-id` (J-38).

These are scope, not bugs — each is pinned by a test in
`tests/test_product_claim.py`, so if one ever stops being true this list is
wrong and must be updated.

## Causal claims are reported, never certified (ADR-007)

A RELATIONAL claim — "X causes Y", "A drives B", "C is responsible for D" — is
grounded by exactly one thing: **a cited source containing that claim
verbatim.** It is NEVER grounded because two sources each mention one end of it.

The old two-source corroboration rule was demoted on 2026-10-02 after a
red-team round demonstrated seven ways to satisfy it with documents that assert
nothing of the kind — a negated endpoint grounded by the positive, a window that
DENIES the relation, the reverse direction, two unrelated pages sharing a common
noun. Seven shapes on one rule is a class, not a backlog.

The rule still RUNS and still reports, as `relation_diagnostic` on each
relational claim:

| value | meaning |
|---|---|
| `corroborated_by_two_sources` | the old rule would have been satisfied |
| `not_corroborated` | it would not |
| `figure_not_in_cited_sources` | a figure in the claim is absent from the cited sources |

**Read it as a lead, never as a verdict.** `corroborated_by_two_sources` with
`UNGROUNDED` is the normal, expected output for an honest causal claim: it means
the sources support the shape of the relation but none of them states it, so the
gate will not certify it and the author must quote a source or soften the claim.

**Tell the user this when it happens.** A draft of causal prose will come back
mostly UNGROUNDED, and that is the gate working, not failing.

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

## Authoring notes: keep them on ONE line

An HTML comment is stripped only when it OPENS AND CLOSES ON THE SAME LINE:
`<!-- check this -->`. A note spread over several lines is NOT stripped — its
inner prose is decomposed and scored as claims, and the draft fails on sentences
nobody meant to publish.

```markdown
<!-- TODO: confirm the replica count with infra -->   <- stripped, invisible to the gate
<!--
TODO: confirm the replica count with infra            <- SCORED. Reads UNCITED, fails the draft.
-->
```

This is deliberate and it is not going to change (J-48). Four designs for a
block-comment stripper have been tried and all four lost: a stripper is an
UNBOUNDED DELETION primitive, and every version found a way to swallow real
claims instead of a note — one of them deleted multi-paragraph prose and
certified the remainder at PASS 100.0 because a CRLF blank line voided its
guard. **Refusing a note is Error-A: loud, recoverable, and the author fixes it
in one keystroke. Deleting a claim is Error-B: silent and unrecoverable.** The
burden stays with the author because only the author can tell a note from a
claim.

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

**What PASS means, and what it does not (ADR-008).** PASS means every claim is
**traceable** to text in a source the run was given — it does **not** mean the
source agrees with the claim. A source reading *"we found no evidence that X"*
can satisfy the check for a draft asserting X (round 14, R14-04), because the
gate matches a contiguous verbatim span and the denial can sit outside it. Every
claim therefore carries a `support_diagnostic`; `cited_sentence_may_not_assert_claim`
means **read that sentence yourself**. It is an advisory and nothing is refused
because of it — **it misses about half the denials we
could construct, and since J-79 fires on none of the claims the gate passes in
the n=52 corpus** (recall 7/14 on our denial set; false alarms
0/15, down from 4/15 — a rate on fifteen rows, not a guarantee). **J-79 trades
recall for precision in one shape**: a denial whose hedge word the CLAIM itself
uses is no longer flagged (`…per the vendor` against a claim saying `per
second`). Our 14-vector set contained none of that shape, so it reported the
trade as free; round 17 found it (recall 7/14 on a named denial set, 2026-10-03: it catches
plain negation, prefix denial, attribution, hearsay and conditionals, and misses
a denial in the next sentence, `retracted`, `erroneous`, `lacks`, `absent`,
`zero`, and a denial after a semicolon). Treat it as a prompt to read the source,
never as a clearance. The word "verified" is deliberately absent from this
tool's output: it checks provenance, not truth.
