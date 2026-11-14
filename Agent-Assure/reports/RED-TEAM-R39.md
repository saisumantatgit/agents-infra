# RED-TEAM-R39 — final pre-merge adversary (0d10d83 vs main 83a5cb9)

**Verdict: 0 BLOCKERS. No draft found that 0d10d83 PASSes or GROUNDs and main 83a5cb9 refuses: by code reading (every main test survives as a disjunct), by a function-level monotonicity fuzz (33,805,032 match positions), and by gate-level fuzz (160k drafts).**

Worktree `ai-overnight-1114`, branch `overnight-2026-11-14` at 0d10d83. Read-only on scripts/ and tests/ (`git diff --quiet 0d10d83 -- Agent-Assure/scripts Agent-Assure/tests` clean; `git status` shows only this file). Main copy: `/private/tmp/claude-501/r39/main/ground_check.py` from `git show 83a5cb9:...`, `cmp`-identical to `/private/tmp/claude-501/r37/gc_main.py` used by the harnesses.

## Question
Is there a draft that 0d10d83 PASSes/GROUNDs and main 83a5cb9 refuses?

## Blockers: 0

## Structural read (what can move a verdict toward PASS)

| Check | Evidence | Result |
|---|---|---|
| Which main objects changed | `inspect.getsource` / value comparison of every module-level object, main vs branch | Only 4 functions: `_has_denial`, `_header_asserts`, `_unit_denied`, `_source_unit_contexts`; only 3 objects: `_DENIAL_TOKENS` (+10 words, none removed), `_FORWARD_REFERENCES` (+`follows`), `_UnitContext` (+3 fields). `ground`, `score_report`, `classify`, `decompose`, `_is_bare_denial`, `_denial_scope_start`, `_disowned_lines`, polarity checks: byte-identical. |
| `_has_denial` | Main test `_folded(tokens) & _DENIAL_TOKENS` kept as first disjunct; set only grew; `or _phrasal_denial` | Superset of main on every input |
| `_unit_denied` | `disowned/scope_denied` kept (+`context_denied`); `before` same tokens; `previous`/`previous2`: main `raw_set & _FORWARD_REFERENCES` vs branch `_points_forward` = folded set & (FORWARD − {follows}). FORWARD words are ASCII lowercase, `_confusable_fold` is identity on them, and main never had `follows`, so main's hits are kept. `previous_line`, `following` unchanged; strong check only adds `return True`. | Superset of main |
| Carve-outs (`made up 40 percent`, `entirely of`, FAQ headings, `flag is false`, `follows`, wh-topic headings, shared stem, referent test) | All live inside NEW predicates (`_phrasal_denial`, `_has_strong_denial`, `_heading_line_denies`, `_paragraph_denied`, `_points_forward`'s follows clause) that are OR'd onto main's tests | Can only withdraw R36/R38 refusals, never a main one |
| `_header_asserts` | Main's three tests unchanged and first; additions only `return True` | Heading NON_CLAIM → scored only (fail-closed) |
| Heading turned into a scored claim as an escape | Uncited → UNCITED; ABSENCE is demoted (`ground` maps ABSENCE_SUPPORTED → UNVERIFIED_ABSENCE); RELATIONAL never certified; vacuous drafts are NEEDS_WORK. A newly scored heading cannot enter the numerator unless it is cited, and cited headings are already scored on main. | No path |
| New crash paths | `_sentence_spans` RuntimeError: sentences are `strip()`ed substrings of the same `_nfkc(text).strip()` base, found in order — unreachable. `_has_denial` TypeError: all callers pass tuples. Strong-flag None → ValueError: the single `_UnitContext(` construction site sets both. Any raise is a CLI error, not a PASS. | 0 crashes in all fuzzing |

## Harness runs

- **r37_probe** `harness.py` c1–c6: 0 BLOCKER lines, 0 CRASH (outputs `/private/tmp/claude-501/r39/out/c*.out`).
- **r38_probe** `fuzz3.py` (three-way, in-process), new seeds 11 and 12 × 40,000 × both grammars = 160,000 drafts: `r38_pass_main_refuses` absent (0) in all four, crashes 0. r37 grammar: 1,372 / 1,269 PASS; r38 grammar: 789 / 824 PASS, 564 / 565 refusals given back vs 2dc776b (the disclosed R38 trades), 1 new refusal vs 2dc776b.
- **c7 targeted attacks** (24 cases, `/private/tmp/claude-501/r39/c7.py`): a main-caught denial plus a carve-out shape next to it — `None of this is true. Women made up 40 percent of staff. C.`, `Not true. The flag is false. C.`, `## Myths and facts\n\nNone of this is true. C.` (also welded and same-line), `None of the following is true.\n\n## Myths and facts\n\nC.`, `None of the following is true. The procedure follows the RFC, not the draft. C.`, `Myths and facts:\n- C`, `No. The value is false. C.`, `How the committee is made up\n\nNone of this is true. C.`, Cyrillic `Nоne of this is true. C.`. All 22 refused on both. 2 PASS on both (holes main also has, out of scope): `C. That was made up 40 percent.` and `Made up 40 percent: C.` — main has no "made up" rule at all; on 2dc776b these were refused, so they are R38 carve-out trades, already named in the `_made_up_takes_object` CEILING.

## Fuzzing (R39's own, function level)

`/private/tmp/claude-501/r39/mono.py`: for each generated source, asserts units align between main and branch, then for EVERY unit × EVERY match position asserts `main._unit_denied ⇒ branch._unit_denied`; also asserts main non-NON_CLAIM ⇒ branch non-NON_CLAIM for every source line read as a draft. This removes fuzz3's blind spots (fixed claim, fixed draft shapes, fixed denial list) because it tests the predicate itself at every offset.

- **Grammars:** `words` (random 1–14-token sentences drawn 50/50 from the union of every denial/forward/back/scope/strong/code-noun/FAQ/truth/coordinator/veracity/copula/made-up-adverb/relative-head lexicon and filler, random end punctuation incl. none and ":"), `sent` (62 crafted sentences: every carve-out, its nearest denial, main denials, headings, list/quote/label lines), `mix` (both). Separators: space, `\n`, `\n\n`, `\n\n\n`, `; `, `\n- `, `\n\n## `, ` (`, `) `, `\n> `, `: `; optional leading `#`/`##`/`**` heading.
- **Volume:** 3 grammars × seeds 1–3 × 100,000 = 900,000 sources, 33,805,032 match positions.
- **Result:** MONO_VIOLATION 0, CLASSIFY_VIOLATION 0, unit misalignment 0, branch crashes 0. Branch-only denials 5,864,013 positions (the R36/R38 refusals). Kind differences (~770 per 100k) are all NON_CLAIM → FACTUAL/ABSENCE headings (fail-closed).

## Suite

`uv run pytest -q`: 1276 passed, 2 skipped, 60 xfailed, exit 0.

## Read only, not fuzzed

Multi-claim and multi-source drafts and the self-source (Read-of-draft) path at gate level. They reach the changed code only through the two `_unit_denied` call sites (`_contained_with_matching_polarity`, `_anchor_sentence_covers`), which use it only as a refusal (`continue` / `and not`), and through `classify`; `score_report` and `ground` are byte-identical, so the function-level monotonicity result carries to them.

## Load-bearing assumption

That `_unit_denied` and `_header_asserts` are the only channels by which the diff can reach a verdict. This was checked mechanically (source comparison of every module object), not only by reading; if a future change adds a third consumer of `_points_forward` or the strong flags that EXEMPTS rather than refuses, this result no longer holds.
