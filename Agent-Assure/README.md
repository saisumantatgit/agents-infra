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
threshold-dilution vector, AA-MOAT-002/-006). The score threshold
(default 90.0) is retained as a secondary bar. NON_CLAIM verdicts are excluded
from the scored denominator.

---

## Grounding Tiers

**T1 — Verbatim:** A contiguous span of ≥8 casefolded NFKC tokens from the claim appears in the source. Citation markers stripped before tokenizing.

**T2 — Lexical-F1:** Content-word F1 between the claim and the best ±2-sentence window of a source is ≥ `lex_tau`, AND every numeric token in the claim is present in that window. Stop words excluded from F1 computation. **`lex_tau` ships at 0.65**; CR-001 calibrated 0.71 on n=12 but that value is not yet deployed (OI-CAL-01 — pending ratification of the n=52 gold labels, which supersede it).

Tiers run **only** on sources with `full_text_source == "verbatim"`. NUMERIC claims additionally pass through `numeric_ok()` before T1/T2: the claim's numeric expression must match a source expression in both value and unit (25% ≠ bare 25; $4M ≡ $4,000,000). When the claim states a rate qualifier ("per second", "/min", etc.), the matching source mention must carry the SAME qualifier — a bare or differently-qualified occurrence fails closed (2026-07-12 fix).

---

## Running Tests

```bash
cd Agent-Assure
uv sync --extra dev   # one-time: adds pytest (install.sh installs runtime deps only)
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
*mechanical* grounding (does every claim trace to a source *actually retrieved
this session*, proven without a model?). Cite asks a model; Assure asks the
evidence store.

## License

[MIT](LICENSE)
