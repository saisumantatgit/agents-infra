# Usage genres: honest bullets, code and tables (2026-10-25)

**40 honest drafts, every claim supported by its source, 4 in 40 pass the gate. All 4 are copied-sentence bullet lists.**
Measured on frozen engine commit `385190f` (a detached worktree, so concurrent edits to
`scripts/ground_check.py` do not move the numbers). Stores are built through the real
`scripts/capture_hook.py` (one `Read` event per source); each draft is checked with
`scripts/ground_check.py --json`.

Command (from `Agent-Assure/`; results land in `tests/usage_genres/results.json`):

    .venv/bin/python tests/usage_genres/run.py --base <frozen 385190f checkout>/Agent-Assure

## Corpus
- **Drafts:** 40 in `drafts/`: bullets 14 (7 copied, 7 paraphrased), code write-ups 13 (7 copied, 6 paraphrased), tables 13 (7 copied, 6 paraphrased). `manifest.json` lists each draft's sources.
- **Sources:** 7 text files written for this test in `sources/` (Python `tempfile`, HTTP caching, git rebase, SQLite WAL, PostgreSQL indexes, harbour logbook, rainfall table) plus 2 real repo docs (`README.md`, `docs/ALPHA-TESTER-GUIDE.md`), read from the frozen checkout.
- **Copied** drafts reuse source sentences/cells word for word; `run.py` asserts every copied segment is a verbatim substring of its source (0 exceptions). **Paraphrased** drafts restate the same facts in new words. Faithfulness of paraphrases is my own reading, not an independent label (candidate, not gold).
- **Unit of count:** "authored claim" = one bullet, sentence or table cell carrying a `[Sn]` marker. It is GROUNDED only if every checker segment overlapping it is GROUNDED, because the checker splits some claims (at ", and", "." in code, and merges whole tables into one segment).

## Result 1: pass rate by genre and variant
| Genre | Variant | Drafts PASS | Authored claims GROUNDED |
|---|---|---|---|
| Bullets | copied | 4 of 7 | 26 of 36 (72%) |
| Bullets | paraphrased | 0 of 7 | 0 of 33 (0%) |
| Code | copied | 0 of 7 | 22 of 27 (81%) |
| Code | paraphrased | 0 of 6 | 3 of 23 (13%) |
| Tables | copied | 0 of 7 | 6 of 29 (21%) |
| Tables | paraphrased | 0 of 6 | 0 of 23 (0%) |
| **All** | | **4 of 40** | **57 of 171 (33%)** |

Raw checker segments, for comparison with earlier instruments: 199 scored, 71 GROUNDED.
Gates: 4 PASS, 5 NEEDS_WORK, 31 FAIL.

- **Paraphrase leakage:** 3 of the 3 grounded "paraphrased" code claims (c11, c12, c13) reuse an 8+ word run of the source by accident of my wording. Genuinely reworded claims: 0 grounded in 76 authored claims outside those three.
- **Table drafts barely pass even when copied:** the decomposer merges a pipe table into one or two long segments, so a single cell failing sinks the rest.

## Result 2: refusal reasons (checker-reported, segments)
Cited segments refused, by the verdict and `support_diagnostic` the checker printed:

| Verdict / diagnostic | Copied | Paraphrased |
|---|---|---|
| UNGROUNDED / `no_hedge_in_cited_sentence` | 14 | 59 |
| UNGROUNDED / `cited_sentence_may_not_assert_claim` | 7 | 10 |
| UNVERIFIED_ABSENCE (either diagnostic) | 3 | 3 |
| UNVERIFIED_RELATION | 1 | 0 |
| **Total refused cited segments** | **25** | **72** |

Plus **31 uncited structural segments scored as claims, all UNCITED**: 12 headings (digits in a heading make it read as a claim, e.g. `# Temporary files, part 1`), 9 fenced-code lines, 7 table header/delimiter lines, 3 stray fragments (`with tempfile.` from splitting code at the dot). They are honest text with no claim in it; each one alone blocks a PASS.

Diagnostic label caveat: `no_hedge_in_cited_sentence` is printed on GROUNDED and UNGROUNDED alike; it does not name the cause. Causes below come from isolated re-runs, not from the label.

Feature split of the 92 cited copied segments (GROUNDED / total): plain sentence 34/42; contains a code span 28/36; contains a parenthesis 0/6; table row or multi-line 3/13; label with colon 3/6. A segment can carry several features.

## Result 3: honest claims refused (isolated and traced)
Controlled runs of the same claim against variants of its source (frozen `385190f`):

1. **Word-for-word copy refused because of the sentence before it.** `Only one writer can be active at a time [S1].` is the source sentence exactly. Against the full `sqlite_wal.md` it is UNGROUNDED. With the preceding sentence replaced by a neutral one (`Readers can proceed.`) it is GROUNDED. The neighbour, "...a writer does not block readers.", carries a negation inside the checker's look-back window. Honest rule-following refused.
2. **Inline code span defeats an exact copy.** `An index on an expression such as `lower(email)` speeds up queries that use the same expression [S1].` is UNGROUNDED with a neutral neighbour sentence. The same sentence with `lower(email)` replaced by the plain word `lower` is GROUNDED. The code span (backticks, parenthesis) is the only difference.
3. **A parenthetical figure refuses a copy.** `Optional flag: `--threshold N` sets the score bar (default 90) [S1].` is UNGROUNDED; dropping only `(default 90)` gives GROUNDED. In the corpus, 0 of 6 copied segments containing a parenthesis grounded.
4. **Honest paraphrase of a trivial fact.** `Readers and writers do not block each other [S1].` (source: "Readers do not block writers, and a writer does not block readers") is UNGROUNDED, as are 59+10 other paraphrased segments. This is the guide's own stated design ("paraphrase is refused by design"); it is a reason, not a bug.
5. **A correctly cited table with only a heading above it.** `t02` (PostgreSQL index table, every cell copied and cited) is FAIL: the header block is scored UNCITED, and the merged rows are UNGROUNDED / `cited_sentence_may_not_assert_claim`.

Not diagnosed: `Blank lines are skipped [S1].` (copied; short) is UNGROUNDED against the README but GROUNDED against a neutral three-sentence source; the cause was not isolated.

## Bottom line
- **Copying works for plain prose bullets (72%) and plain code-write-up sentences (81%); it fails for tables (21%).** Paraphrase grounds at 0 of 76 genuine rewordings.
- **Structure is penalised as if it were claims:** 31 uncited headings, fences, table headers and fragments, in 17 of 40 drafts, each enough to stop a PASS.
- **Not touched:** no engine or script was edited; PASS-enabling changes (table-aware decomposition, ignoring fenced code and numeric headings, tolerating code spans/parentheses) remain Sai's call (Escalation #1).

## Caveats
- **Load-bearing assumption:** my sources and drafts are AI-written, and "honest" is my own judgement that each claim restates its source; no human gold labels.
- Seven of nine sources are short single-topic texts I wrote; real retrieved pages are longer and may behave differently (the look-back effect in example 1 depends on neighbour sentences).
- Counts are of one run on `385190f`; `results.json` holds every per-claim verdict and diagnostic.
