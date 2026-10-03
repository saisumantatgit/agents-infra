# Agent-Assure

Verification-first grounding gate for AI-generated drafts. Checks every factual claim against a captured evidence store before the draft reaches a human reader. No LLM calls during grounding — the engine is pure Python, deterministic, and audit-defensible.

**Phase 1 scope (built):** a `PostToolUse` capture hook that records retrieved sources verbatim (1b), the deterministic grounding engine — decomposition, classification, two-tier lexical grounding (T1 verbatim + T2 lexical-F1), numeric verification, absence checking, relational two-source rule, score gate, and CLI (1a) — and Claude Code plugin packaging (1c). Phase 2 (research front-end, NLI paraphrase tier, calibration, cross-platform) is future work.

---

## How it works — two halves

1. **Capture (automatic).** A `PostToolUse` hook (`hooks/hooks.json` → `scripts/capture_hook.py`) fires after every retrieval tool call — Exa fetch, `Read`, native `WebFetch`, DDG fetch — and appends a verbatim-tagged record to `.assure/evidence-store.jsonl`. You do nothing; the store is built as you research. All payload shapes are live-validated against a real Claude Code session (2026-07-03): large `Read` results truncate inline (the store holds exactly what the model saw); native `WebFetch` (Haiku-summarized) is tagged `haiku_summary` so the gate refuses to certify against it.
2. **Verify (on demand).** `/assure-verify <draft>` runs `scripts/ground_check.py` against that store and returns a `PASS` / `NEEDS_WORK` / `FAIL` gate with per-claim verdicts. **No LLM judges grounding** — the verdict is a mechanical fact about the store, which is exactly why a fabricated `[S9]` citation cannot talk its way to a pass.

---

## Install & Plugin Usage

```bash
# From the Agent-Assure directory — provisions .venv (Python >=3.11 + deps)
bash install.sh
```

Then register the directory as a Claude Code plugin. Once active:

- the capture hook runs automatically during research;
- after drafting, run `/assure-verify path/to/draft.md` (uses `.assure/evidence-store.jsonl` by default).

The plugin ships one command (`/assure-verify`), one skill (`verify-grounding`), and the capture hook. See [skills/verify-grounding/SKILL.md](skills/verify-grounding/SKILL.md) and [references/grounding-failure-types.md](references/grounding-failure-types.md).

---

## Quick Start (manual CLI)

```bash
uv run python scripts/ground_check.py \
    --draft  DRAFT.md   \
    --store  STORE.jsonl \
    [--threshold 90]    \
    [--json]
```

Exit codes: `0` = gate PASS, `1` = NEEDS_WORK or FAIL.

Without `--json`: writes `grounding-report.yaml` to CWD and prints a one-line summary.

With `--json`: prints the full report as JSON to stdout (no file written).

---

## Drafting conventions (two rules, both fail-safe)

1. **Citation markers go INSIDE the sentence, before the final period** —
   `... 128000 operations per second [S1].`, not `... per second. [S1]`. A marker
   after the period becomes its own segment and detaches from its claim, which
   then reads `UNCITED`.
2. **Keep authoring notes on ONE line** — `<!-- TODO: check this -->`. Only a
   comment that opens and closes on the same line is stripped. A multi-line
   `<!-- ... -->` block is decomposed and SCORED as claims, so the draft fails on
   sentences nobody meant to publish (J-48).

Both rules over-flag rather than under-flag. The second one is permanent: a
block-comment stripper is an unbounded deletion primitive, and four designs for
one have been tried and rejected — one deleted multi-paragraph prose and
certified the remainder at PASS 100.0 when a CRLF blank line voided its guard.
Refusing a note is recoverable in one keystroke; deleting a claim is not.

---

## EvidenceStore JSONL Format

One JSON object per line. Blank lines are skipped.

```jsonc
{
  "source_id":        "S1",                          // required — citation key e.g. "[S1]"
  "url":              "https://example.com/page",    // optional
  "file_path":        null,                          // optional
  "fetched_at":       "2026-06-19T12:00:00Z",       // required — ISO-8601 timestamp
  "tool":             "exa.web_fetch_exa",           // required — capture tool name
  "content_sha256":   "abc123def456...",             // required — hex digest of text
  "text":             "Full retrieved text...",      // required — source body
  "full_text_source": "verbatim",                   // required — see note below
  "captured_via":     "inline",                     // required — "inline" | "overflow-file"
  "query_provenance": "redis performance benchmarks" // required — search query that produced this source
}
```

**`full_text_source` values:**

| Value | Meaning | Grounding tiers run? |
|---|---|---|
| `verbatim` | Full text captured directly from the source | Yes — T1 and T2 run on this text |
| `haiku_summary` | Text is an LLM summary, not the original | No — tiers do NOT run; claim → UNGROUNDABLE |

All text fields are NFKC-normalized before matching.

---

## Verdict Taxonomy

| Verdict | Meaning |
|---|---|
| `GROUNDED` | Claim supported by a verbatim source via T1 or T2 (or is a NON_CLAIM) |
| `ABSENCE_SUPPORTED` | Absence claim backed by ≥2 distinct queries that each carry every strong anchor (capitalized entity / numeric token) of the negated subject plus its head noun — or, for entity-free subjects, a head noun that is not a majority corpus word (2026-07-12 fix) |
| `UNGROUNDED` | Verbatim sources exist but neither T1 nor T2 finds support |
| `UNCITED` | Claim carries no citation markers |
| `UNVERIFIED_CITATION` | Citation marker present but the source_id is absent from the store |
| `UNVERIFIED_NUMBER` | NUMERIC claim whose number does not match any source — value, unit, and (when the claim states one) the rate qualifier ("per second"/"/min" etc.) must all match (2026-07-12 fix) |
| `UNVERIFIED_ABSENCE` | Absence claim where fewer than 2 distinct queries carry every strong anchor + head noun of the subject, or (entity-free subject, ≥3 distinct queries) the head noun is a non-discriminating majority-corpus word (2026-07-12 fix) |
| `UNVERIFIED_RELATION` | Relational claim ("A causes B") without 2 distinct verbatim sources (one per side) |
| `UNGROUNDABLE` | All cited sources have `full_text_source != "verbatim"` (e.g. haiku_summary), or source text is empty |

**Score gate (ADR-005 semantics — accepted 2026-07-12):**

| Gate | Condition |
|---|---|
| `PASS` | **empty retained appendix** (zero violation-class verdicts) AND score ≥ threshold |
| `NEEDS_WORK` | score ≥ 60 AND (any retained violation OR below threshold) |
| `FAIL` | score < 60 — **checked first**, so a sub-60 score is `FAIL` even when other overrides apply |

`PASS` means **every scored claim is grounded**, not "at least 90% are" — one
retained violation caps the gate regardless of score (this closed the
threshold-dilution vector, OI-MOAT-02/-006). The score threshold
(default 90.0) is retained as a secondary bar. NON_CLAIM verdicts are excluded
from the scored denominator.

---

## Grounding Tiers

**T1 — Verbatim:** A contiguous span of ≥8 casefolded NFKC tokens from the claim appears in the source. Citation markers stripped before tokenizing.

**T2 — Lexical-F1: DEMOTED 2026-09-02 (ADR-006). IT DECIDES NOTHING.** It is computed and emitted as a diagnostic (`t2_f1`) and no verdict consults it. **`lex_tau` is RETIRED**, and `--lex-tau` now RAISES rather than silently no-op'ing — passing it exits 2. Why it went: a true and a false claim can differ by one token and score an identical `t2_f1` (5/5 matched pairs), and a bag of words has no order, so a false REORDERING scored 1.000. **This paragraph previously documented T2 as live at `lex_tau` 0.71 with a working `--lex-tau` override — a month after the override began exiting 2** (R15-03, round 15). Current operating point: **Error-A 0.400 / Error-B 0.000, n=52 gold, CR-007.**

Tiers run **only** on sources with `full_text_source == "verbatim"`. NUMERIC claims additionally pass through `numeric_ok()` before T1/T2: the claim's numeric expression must match a source expression in both value and unit (25% ≠ bare 25; $4M ≡ $4,000,000). When the claim states a rate qualifier ("per second", "/min", etc.), the matching source mention must carry the SAME qualifier — a bare or differently-qualified occurrence fails closed (2026-07-12 fix).

---

## Running Tests

```bash
cd Agent-Assure
uv sync               # runtime deps + pytest (dev group, installed by default)
uv run pytest
```

The test suite includes:
- Unit tests for every engine function (decompose, classify, tiers, absence, relational, score)
- Parametrized golden verdict matrix (`tests/test_golden_matrix.py`) — one row per verdict path, each asserting the exact verdict with the exact fixture conditions that cause it
- Determinism assertions — same draft → identical claim set across calls
- CLI smoke tests (end-to-end, YAML + JSON modes, exit codes)
- Capture-hook tests: verbatim tagging, overflow-file reconstruction, `cat -n` stripping, atomic source_id assignment under thread contention (with a red-proof that the same scenario collides when the lock is neutered), and a closed-loop hook→store→engine integration proof

---

## Part of the Agent suite

Agent-Assure is the verification-first research member of the `agents-infra`
suite (PROVE, Cite, Trace, Scribe, Drift, Litmus). Its closest sibling is
**Agent-Cite**, and the boundary is deliberate: Cite does LLM-based citation
*discovery* (does a claim have *a* source somewhere on the web?); Assure does
*mechanical* traceability (does every claim trace to a source *captured in the
evidence store*, proven without a model?). Cite asks a model; Assure asks the
evidence store.

## What Agent-Assure does not prove

A PASS means every claim was mechanically traced to captured evidence. It is not
a certificate of truth, and the boundary is deliberate:

| Not proven | Why |
|---|---|
| Where the evidence came from | The gate checks the draft against what the session READ. The drafting agent's tool choices are trusted, so a file it wrote and read back is a verbatim source. |
| **A causal or correlational claim, unless a source states it** | **ADR-007 (2026-10-02): corroboration no longer certifies anything.** A claim like "X causes Y" is certified only if a cited source contains that claim verbatim — never because two sources each mention one end of it. A red-team round demonstrated seven ways two unrelated documents could satisfy the old rule, so it was demoted to a reported DIAGNOSTIC (`relation_diagnostic`) that decides nothing. **Consequence: a draft containing a causal sentence will usually not PASS.** That is deliberate. |
| That the meaning is supported | Verbatim provenance only. A faithful paraphrase is REFUSED (**Error-A 0.400, n=52, CR-007** — the rate rose when relational grounding was demoted, ADR-007). `UNGROUNDED` means "not mechanically traceable", never "false". |
| **That the source AGREES with the claim** | **No.** The gate checks the claim's words are PRESENT in a cited source, not that the source supports it. A source reading *"we found no evidence that X"* can satisfy the check for a draft asserting X (round 14, R14-04). Every report carries a `support_diagnostic` flagging this where it can detect it — **an advisory, not a verdict: it catches about half the denials we could construct** (recall 7/14) and, since J-79, fires on none of the claims the gate passes in the n=52 corpus (0/15, down from 4/15 — a rate on fifteen rows, not a guarantee). ADR-008. |
| That the source is right | The gate certifies source-support, not truth. |
| That an absence was really searched for | The searches behind "no evidence of X" are supplied by the agent, not observed. |
| **Anything at all in `claude -p` / CI mode** | **The capture hook does NOT run in print mode** (verified 2026-10-02 against a plugin hook, a project `.claude/settings.json` hook and an explicit `--settings` hook — none fired while the tool itself ran). The store stays EMPTY, so every claim reads `UNCITED` and the gate fails everything. Agent-Assure needs an interactive session to capture. |
| That the source was retrieved *this* session — **unless you ask** | `--session-id <id>` makes the gate REFUSE a store containing any other session's evidence. Without that flag there is **no session enforcement**, because the store is appended to and never rotated (J-38), and the report says so in its own scope line. **Correction (R15-04, round 15): this row used to say "every captured record now carries a `session_id`". Records written before that field existed carry a BLANK one, and `--session-id ""` exploited exactly that — it matched the blanks, raised nothing, and printed the SESSION-SCOPED wording over evidence carrying no session data at all. A blank `--session-id` now REFUSES (R15-01).** |

**What PASS means, and what it does not (ADR-008).** PASS means every claim is
**traceable** to text in a source the run was given — it does **not** mean the
source agrees with the claim. A source reading *"we found no evidence that X"*
can satisfy the check for a draft asserting X (round 14, R14-04), because the
gate matches a contiguous verbatim span and the denial can sit outside it. Every
claim therefore carries a `support_diagnostic`; `cited_sentence_may_not_assert_claim`
means **read that sentence yourself**. It is an advisory and nothing is refused
because of it — **it misses about half the denials we
could construct, and since J-79 fires on none of the claims the gate passes in
the n=52 corpus** (recall 7/14; false alarms 0/15, down from 4/15 — a rate on
fifteen rows, not a guarantee) (recall 7/14 on a named denial set, 2026-10-03: it catches
plain negation, prefix denial, attribution, hearsay and conditionals, and misses
a denial in the next sentence, `retracted`, `erroneous`, `lacks`, `absent`,
`zero`, and a denial after a semicolon). Treat it as a prompt to read the source,
never as a clearance. The word "verified" is deliberately absent from this
tool's output: it checks provenance, not truth.


Each row is pinned by a test in `Agent-Assure/tests/test_product_claim.py`. If
one stops being true, that suite fails and this table is what must change.

## License

[MIT](LICENSE)
