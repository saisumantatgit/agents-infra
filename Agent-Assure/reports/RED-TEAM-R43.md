# RED-TEAM R43: does REASONS-FOR-REFUSAL change any verdict?

Date: 2026-11-15. Status: COMPLETE. Branch `ovn-1115-q8` at `8abe1f1` vs `origin/main` `746f337`.
Reviewer stance: pre-merge adversary, last gate on moat code. Read-only on
`scripts/` and `tests/`.

**Verdict: no input found that changes gate, score, verdict, kind or claim count; one performance regression in the display path, unbounded, which can push a run past the 120 s Bash-tool timeout the verify skill runs under.**

## Question

Does any input give a different gate, grounding score, per-claim verdict, kind,
or claim count on the branch than on `origin/main`? Claim under test
(`reports/REASONS-FOR-REFUSAL.md`): the change is reporting only.

## Line-by-line equivalence

| Change | Verdict-path effect | Finding |
|---|---|---|
| `_unit_denied` -> `_unit_denial_reason(...) is not None` | Rule order kept: disowned, scope, context, same-sentence, previous, previous_line, previous2, ValueError guard on strong flags (same position), following_strong, previous_strong, following rules. Every return value is a non-empty constant string, so `is not None` matches the old `True`; every old `False` is now `None`. `or` split into separate `if`s keeps truthiness. No new exception and no mutation. | Equivalent |
| `_span_is_hedged` -> `bool(_span_hedge_hits(...))` | `any(tok in S for tok in window)` == non-empty filtered tuple | Equivalent |
| `Claim.split_from` (`compare=False`) | Not in `__eq__`/`__hash__`; `decompose` produces the same pieces and the same `index` increments; `classify` copies it. No verdict function reads it; no `asdict`/`repr` of `Claim` anywhere in `scripts/`. | Equivalent |
| `_UnitContext` + 3 defaulted fields | Computed from `para_denied[s]`/`head_denied[s]`/`s`, which were already indexed on the same line; no new IndexError. Not compared or hashed by any rule. | Equivalent |
| `score_report`: `evidence_basis` once instead of twice; `verbatim_refusal` / `unread_unit_note` after `ground` | Gate is computed from `verdict`, `kind`, `retained_appendix` membership and `has_unverified_citation`; none read `basis` or `support_diagnostic`. The only channels left are an exception raised, or a run that takes too long. | Equivalent, with the performance finding below |
| `explain_report.fix_hint` | Rendering only | n/a |

## Differential harness

An independent harness (`/private/tmp/claude-501/ovn1115-r43/harness.py` and `mutfuzz.py`; `refusal_probe/diff_fuzz.py` was not reused) imports both modules in one process and runs `decompose -> classify -> score_report` with the CLI's self-source arguments. It compares the exception, the claim count and fields, the gate, score, scored count, vacuous flag, per-claim (index, text, kind, verdict, relation/absence diagnostic) and the appendix (index, verdict).

The grammar puts hedge words at sentence ends ("He said no.", "Per.", "Contrary.") right before copied facts, and denials 1-3 sentences back. It also covers scope sentences, falsity statements in the same paragraph, denying headings, `Myths:` labels with bullets, tables, fenced bare denials, conjunction and semicolon joins in sources and drafts, figures in `percent`/`%`/`per cent`, 1-3 sources, cross-citations, `[S9]`, uncited lines and self-copy stores. Half the seeds are benign, with plain facts and correct citations, so the PASS/NEEDS_WORK boundary is exercised.

| Run | Drafts | Gate mix (FAIL/NW/PASS) | Differences | Exceptions (either side) |
|---|---|---|---|---|
| Grammar, seeds 0-59,999 | 60,000 | 54,695 / 3,290 / 2,015 | **0** | 0 |
| Unicode/structure mutation layer (ZWSP, CRLF, NBSP, full-width, Cyrillic о, ligature, stray `[S1]`/`#`/`|`/`;`/`Untrue.`) | 12,000 | 11,716 / 192 / 92 | **0** | 0 |
| Targeted repetition probes (`perf.py`, `perf2.py`) | 18 | all FAIL | **0** | 0 |

The fuzz fired 14 of the 15 `verbatim_but_*` codes (about 59k times in total). It never fired `verbatim_but_negation_limited_in_source`, so that branch's exception-freedom is shown by reading the code only.

## Corpus runners

Both runners ran against an extracted `origin/main` tree and against the worktree, with `--out` set to a temp directory so `tests/` was not written.

| Corpus | Drafts | Summary equal | Differing non-display leaves |
|---|---|---|---|
| `tests/error_a_corpus` | 336 (3,990 claims) | yes | 0 (1,117 differences, all in `diagnostics`, the support_diagnostic display codes) |
| `tests/error_b_corpus` (+controls) | 280 | yes | 0 |

## Findings

**F1, performance (display path, unbounded, fail-closed).** `_occurrence_refusal` calls `_source_unit_contexts(source.text)` again for every exact occurrence that is hedge-refused. The call computes `starts_sentence`, which does not depend on `start`. Main short-circuits at the hedge check and never builds the contexts. Cost is roughly claims × hedged occurrences × one context build, about 0.8 s per 100 KB of source.

| Input | main | branch |
|---|---|---|
| 1 claim, 100 KB source, 10 hedged copies | 0.16 s | 8.8 s |
| 5 claims, same source | 0.48 s | 31 s |
| 1 claim, 40 hedged copies | 0.05 s | 20 s |
| 20 claims `"The feature is supported by default [S1]."`, 100 KB source with 10 copies of `"Version 2 does not have this. The feature is supported by default."` (CLI, `slow/`) | 1.38 s, FAIL 0.0 | 87.76 s, FAIL 0.0 (same 20 verdicts) |

The verdict never changes in-process. But `skills/verify-grounding/SKILL.md` runs the gate through the Bash tool, whose default timeout is 120 s, so on large sources the branch can produce no report where main produces one. The measured 20-claim case took 87.8 s, under the 120 s limit. The cost is linear in claims, so about 28+ such claims, or a 150 KB+ source, would cross the limit. That figure is extrapolated, not measured. That points away from PASS (fail-closed), but it is a changed outcome. The fix is display-only: hoist the `starts_sentence` computation, and build `_source_unit_contexts` once per source in `_occurrence_refusal`.

No differences in gate, score, verdict, kind or claim count were found.

## Residual risk

- **Load-bearing assumption:** the `_unit_denial_reason` return codes are all non-empty strings. If a future code is `""`, `_unit_denied` would read it as denied. The values are module constants today.
- **Grammar ceiling:** the generated sources are at most about 5 blocks, so the fuzz does not cover long real pages. Real-page behaviour is covered only by the two corpora (616 drafts).
