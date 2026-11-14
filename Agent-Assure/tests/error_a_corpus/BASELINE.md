# Error-A corpus baseline

**Verdict: 5 of 336 honest drafts pass the gate; 156 NEEDS_WORK, 175 FAIL. 2044 of 3990 cited claims (51.2%) are GROUNDED.** Every claim is a verbatim sentence or cell of its own source, so every refusal below is a false refusal (Error-A).

Measured on main `ef3ae1f` (worktree ovn1115-q2, no scripts edited). Command, from `Agent-Assure/`:

    uv run python tests/error_a_corpus/run.py --base .
    uv run python tests/error_a_corpus/baseline_md.py --commit ef3ae1f

## What the corpus is, and is not

- **Size:** 336 drafts, 14 genres x 24, each with its own source file written for this corpus (no third-party text), 3990 cited claims. Regenerate with `build_corpus.py` (seed fixed).
- **Honesty by construction:** each cited claim is a verbatim substring of its source (asserted at build time and again by the runner, which raises on any exception). No fabrication is in the corpus.
- **Not a prevalence sample.** Shapes known to be refused (negation next to a claim, made up of, quoted denials, never happened, table No cells, =False, numbers) are deliberately over-represented. Read the per-shape table, not the headline rate, as the measurement. `light` drafts (one third) carry no negation neighbours.
- **Unit of count:** an authored claim is one cited bullet, sentence or table cell. It is GROUNDED only if every checker segment overlapping it is GROUNDED (same rule as `usage_genres`).
- **Refusing cause is an attribution, not the gate's report.** The gate prints a verdict and a `support_diagnostic` but not the refusing token. The runner re-runs each refused claim alone against only its own sentence: grounded alone = context caused it, then the nearest denial word in the 3 sentences before or 1 after is named; refused alone = intrinsic, named by the first feature of the claim. Validation: of 80 sampled `neighbour` attributions, 69 were refused again with only the neighbour and the claim as source, and 68 became GROUNDED when the neighbour was swapped for a neutral sentence (about 85% agreement).

## Per genre

| Genre | Drafts | PASS | NEEDS_WORK | FAIL | Claims | GROUNDED | Rate |
|---|---|---|---|---|---|---|---|
| api_reference | 24 | 0 | 4 | 20 | 325 | 108 | 33.2% |
| changelog | 24 | 1 | 11 | 12 | 246 | 141 | 57.3% |
| code_review | 24 | 0 | 7 | 17 | 248 | 115 | 46.4% |
| faq | 24 | 0 | 6 | 18 | 256 | 120 | 46.9% |
| financial_report | 24 | 1 | 8 | 15 | 370 | 166 | 44.9% |
| howto_code | 24 | 0 | 13 | 11 | 248 | 130 | 52.4% |
| hr_policy | 24 | 0 | 9 | 15 | 273 | 137 | 50.2% |
| incident | 24 | 1 | 21 | 2 | 277 | 194 | 70.0% |
| meeting_notes | 24 | 0 | 8 | 16 | 293 | 134 | 45.7% |
| news_brief | 24 | 0 | 9 | 15 | 226 | 90 | 39.8% |
| product_docs | 24 | 0 | 14 | 10 | 319 | 164 | 51.4% |
| readme | 24 | 0 | 21 | 3 | 246 | 182 | 74.0% |
| research_summary | 24 | 1 | 16 | 7 | 296 | 185 | 62.5% |
| sales_report | 24 | 1 | 9 | 14 | 367 | 178 | 48.5% |
| **All** | 336 | 5 | 156 | 175 | 3990 | 2044 | 51.2% |

## Per density (source length against claims quoted)

| Density | Drafts | PASS | NEEDS_WORK | FAIL | Rate |
|---|---|---|---|---|---|
| dense | 112 | 0 | 45 | 67 | 46.3% |
| normal | 112 | 0 | 48 | 64 | 50.7% |
| light | 112 | 5 | 63 | 44 | 60.5% |

## Per shape (claim level)

| Shape | Claims | GROUNDED | Rate |
|---|---|---|---|
| faq_fact | 36 | 0 | 0.0% |
| table_no_false | 178 | 21 | 11.8% |
| table_cell | 542 | 159 | 29.3% |
| neg_neighbour | 448 | 164 | 36.6% |
| number | 575 | 235 | 40.9% |
| made_up_of | 216 | 103 | 47.7% |
| never_happened | 215 | 106 | 49.3% |
| quoted_denial | 220 | 117 | 53.2% |
| neg_sentence | 232 | 136 | 58.6% |
| plain | 1268 | 944 | 74.4% |
| code_false | 38 | 37 | 97.4% |
| code_span | 22 | 22 | 100.0% |

## Top 15 refusal causes

Counted over 1946 refused claims plus 244 uncited structural segments (headings, fences, table header rows) that the gate scored as claims. Offsets are folded: `neighbour:not` means the nearest denial word in an adjacent sentence was `not`.

| # | Cause | Count | Example segment |
|---|---|---|---|
| 1 | `list_marker:number_of_numbered_list_item` | 406 | product_docs_015: Members open role templates from the toolbar above the project list (UNVERIFIED_NUMBER) |
| 2 | `context:neighbour:not` | 276 | product_docs_001: The Business plan costs 30 dollars per member each month (UNGROUNDED) |
| 3 | `context:neighbour:no` | 253 | product_docs_000: Each project keeps its attachments for 28 days after a member removes them (UNGROUNDED) |
| 4 | `context:neighbour:never` | 210 | product_docs_007: The release notes say the change "does not affect existing comments" (UNGROUNDED) |
| 5 | `intrinsic:negation_in_claim` | 186 | product_docs_000: The free trial lasts 28 days and needs no card (UNGROUNDED) |
| 6 | `uncited:heading` | 172 | product_docs_000: # Quillboard: working with bulk import (UNCITED) |
| 7 | `context:neighbour:cannot` | 133 | product_docs_000: The Starter plan does not include bulk import (UNGROUNDED) |
| 8 | `intrinsic:digits` | 101 | readme_002: Version 3.5 reduced memory use by 6 percent on large inputs (UNVERIFIED_NUMBER) |
| 9 | `context:neighbour:made up` | 84 | product_docs_006: The planned redesign of the folder list never shipped in the 2026 cycle (UNGROUNDED) |
| 10 | `context:table_row_merge` | 73 | product_docs_002: Yes (UNGROUNDED) |
| 11 | `context:neighbour:false` | 55 | code_review_000: A comment above it explains why (UNGROUNDED) |
| 12 | `uncited:fence_or_delimiter` | 48 | readme_000: ```python / from pebblecache import load (UNCITED) |
| 13 | `context:no_denial_word_within_-3..+1` | 45 | product_docs_006: Guests are not counted as members for billing (UNGROUNDED) |
| 14 | `context:neighbour:without` | 37 | product_docs_003: Version 9.8 added offline mode to every plan (UNGROUNDED) |
| 15 | `context:neighbour:myth` | 36 | faq_000: Fact: Every plan can export recipes (UNGROUNDED) |

Refused-claim verdicts: UNGROUNDED 1232, UNVERIFIED_NUMBER 510, UNVERIFIED_ABSENCE 121, UNCITED 99, UNVERIFIED_RELATION 15.

## Readings

- **Numbered lists (largest single cause):** a numbered-list item counts its own list number as an unverified figure. 406 claims (20.9% of all refusals) are refused for this alone, from 55 drafts that use a numbered list. Excluding those drafts, the grounded rate is 60.2%.
- **Structure:** 244 uncited segments (headings, code fences, table header rows) are scored as claims; 11 drafts have every cited claim GROUNDED and still do not PASS.
- **Near-copy rule (UNGROUNDABLE):** 0 claims in this run. The rule treats a source whose word pairs are 80% or more present in the draft as a copy of the draft; this corpus pads each source with uncited sentences, so it rarely fires here. An earlier draft of this corpus with short sources hit it on most dense drafts.
- **Spelled-out percentages:** probe, source sentence copied word for word plus one neutral sentence: `About 85 percent of requests failed at the peak [S1].` gives UNVERIFIED_NUMBER; `About 85% of requests failed at the peak [S1].` gives GROUNDED. Half of the percentage claims here use each form, so the `percent` form feeds the `intrinsic:digits` cause.

## Load-bearing assumption

That my sources and drafts are honest. They are AI-written and the faithfulness check is mechanical (verbatim substring), not independent human labelling; a claim that is verbatim but reads as a different assertion out of context (for example a sentence opening with `It`) still counts as honest here. Second weak seam: cause labels for context refusals are an 85% agreement attribution, not the gate's own report.

