# Agent-Assure

Verification-first grounding gate for AI-generated drafts. Checks every factual claim against a captured evidence store before the draft reaches a human reader. No LLM calls during grounding — the engine is pure Python, deterministic, and audit-defensible.

**Phase 1a scope:** decomposition, classification, two-tier lexical grounding (T1 verbatim + T2 lexical-F1), numeric verification, absence checking, relational two-source rule, score gate, and CLI. Phases 1b/1c add the PostToolUse capture hook and plugin packaging.

---

## Quick Start

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
| `ABSENCE_SUPPORTED` | Absence claim backed by ≥2 distinct queries targeting the subject |
| `UNGROUNDED` | Verbatim sources exist but neither T1 nor T2 finds support |
| `UNCITED` | Claim carries no citation markers |
| `UNVERIFIED_CITATION` | Citation marker present but the source_id is absent from the store |
| `UNVERIFIED_NUMBER` | NUMERIC claim whose number does not match any source (value + unit both checked) |
| `UNVERIFIED_ABSENCE` | Absence claim with fewer than 2 distinct queries mentioning the subject |
| `UNVERIFIED_RELATION` | Relational claim ("A causes B") without 2 distinct verbatim sources (one per side) |
| `UNGROUNDABLE` | All cited sources have `full_text_source != "verbatim"` (e.g. haiku_summary), or source text is empty |

**Score gate:**

| Gate | Condition |
|---|---|
| `PASS` | score ≥ threshold AND no `UNVERIFIED_CITATION` |
| `NEEDS_WORK` | score ≥ 60 but below threshold, OR any `UNVERIFIED_CITATION` |
| `FAIL` | score < 60 |

Default threshold = 90.0. NON_CLAIM verdicts are excluded from the scored denominator.

---

## Grounding Tiers

**T1 — Verbatim:** A contiguous span of ≥8 casefolded NFKC tokens from the claim appears in the source. Citation markers stripped before tokenizing.

**T2 — Lexical-F1:** Content-word F1 between the claim and the best ±2-sentence window of a source is ≥ 0.65, AND every numeric token in the claim is present in that window. Stop words excluded from F1 computation.

Tiers run **only** on sources with `full_text_source == "verbatim"`. NUMERIC claims additionally pass through `numeric_ok()` before T1/T2: the claim's numeric expression must match a source expression in both value and unit (25% ≠ bare 25; $4M ≡ $4,000,000).

---

## Running Tests

```bash
cd Agent-Assure
uv run pytest
```

The test suite includes:
- Unit tests for every engine function (decompose, classify, tiers, absence, relational, score)
- Parametrized golden verdict matrix (`tests/test_golden_matrix.py`) — one row per verdict path, each asserting the exact verdict with the exact fixture conditions that cause it
- Determinism assertions — same draft → identical claim set across calls
- CLI smoke tests (end-to-end, YAML + JSON modes, exit codes)
