# E2-lite pre-merge adversary review (branch ovn-1121-e2l @ bf48460 vs origin/main 0c0ddc4)

**Verdict: 0 BLOCKERS.** Nothing main refuses passes on the branch. The rule has real honest-label cost beyond what the report lists, a latency cost the report does not mention, and an easy set of evasions.

## 1. Blocker question: does anything main refuses now pass? No.

**Code-path argument (structural):**
- The diff against 0c0ddc4 touches `ground_check.py` with additions only (+83/-0): two new functions plus one loop in `main()`. `classify`, `decompose`, `ground`, `score_report` and the R40/`_header_asserts_*` paths are byte-unchanged.
- The loop rewrites a claim only when `claim.kind == NON_CLAIM and not claim.citations`, and only toward `FACTUAL`. It keeps all `Claim` fields: index, text, citations (empty), numeric_tokens, split_from. A heading main scored is never passed to `_e2_heading_asserts`, so that function (and its `_match_denied` use) cannot return "label" for a heading main scores. Its False return is a no-op.
- A promoted claim with no citations goes `ground` → `UNCITED`, which `_NUMERATOR_VERDICTS` (GROUNDED and ABSENCE_SUPPORTED only) excludes. So the denominator goes up by one, the numerator stays the same, and the retained appendix becomes non-empty. Score can only fall, PASS becomes impossible, and the vacuous NEEDS_WORK case becomes FAIL at 0.0. No claim can gain GROUNDED.
- `self_source_ids` and `inferred_self_ids` come from `draft_text`, not from `claims`, so the rewrite leaves them alone. The only non-CLI entry points (library callers) still run main's code unchanged.

**Empirical comparison, frozen main worktree vs branch, run per draft:**

| Instrument | Drafts | Gate up | Score up | Control gate up | Gate down |
|---|---:|---:|---:|---:|---:|
| Error-B v1 | 280 | 0 | 0 | 0 | 5 (the five `claim_heading` escapes closed) |
| Error-B v2 | 269 | 0 | 0 | 0 | 0 |
| Error-B v3 | 510 | 0 | 0 | 0 | 0 (490 escapes still open) |
| Error-A (`--no-ablate`) | 336 | 0 | 0 (no claim gained grounded) | n/a | 0 |
| Usage genres | 40 | 0 | 0 | n/a | 0 (kinds, gates and scores identical) |
| Differential fuzz (random source-span headings, disowning tails, prefixes, Title Case, setext, trailing punctuation or `[S1]`, 85% cited body) | 600 | 0 | 0 | — | kind changed in 5 |
| Targeted probes of main-scored headings (R40 set, OI-MOAT-19 shapes, cited headings, setext, numeric headings, `Why X collapsed`), plain source and disowned source | 38 | 0 | 0 | — | — |

**Crash check:** `_denial_units` raises `RuntimeError` when its two readings disagree. The branch now calls it on every store source, including uncited ones. I ran it on 1,432 corpus source files plus 11 malformed or odd strings: 0 exceptions. A crash would exit with code 1, which is non-PASS anyway.

## 2. Honest cost beyond the report

**Single-word and noun-compound labels newly scored.** Test setup: a neutral one-sentence source and a fully grounded body. On main every one of these PASSes; on the branch every one FAILs at 50.0. That is 21 of 46 probed labels:
- **Single-word headings (16):** `Charges`, `Charging`, `Finding`, `Found`, `Fail`, `Ban`, `Fines`, `Arrests`, `Suing`, `Crash`, `Fraud`, `Quitting`, `Double`, `Doubling`, `Hacking`. The branch `(i == 0 and len(words) == 1)` scores any one-word heading in the list. The report's `Recent arrests` control survives only because of its premodifier; plain `## Arrests` does not.
- **Compounds ending in a listed word (5):** `Memory leaks`, `Code folding`, `Fast charging`, `Productivity hacks`, `Lost and found`. These are common in developer, billing, EV and compliance docs.
- **Question labels:** `## How the regulator found fraud` is newly scored. It is a label, but `found` is in the always-predicate set.
- **When it fires:** only when the word appears in no store source, which is common when the drafter names a section in its own words.

**Latency.** For every NON_CLAIM heading where rule (b) does not fire, `_e2_heading_asserts` re-tokenises all sources and calls `_denial_units` on every source, before checking whether the heading text even occurs in it.
- **Measured:** with 30 plain headings and 40-sentence sources, main takes 0.19 s at 50 sources and 0.21 s at 200. The branch takes 6.2 s at 50 sources and 24.2 s at 200, growing linearly with headings × sources.
- **Why it matters:** the store is opened `mode="a"` and never rotated (CLAUDE.md gotcha J-38), so the per-run cost only grows.
- **Missing ceiling:** the `CEILING:` comment does not name this. Two cheap fixes: compute `_denial_units` lazily after `normalized.find(body) >= 0`, and compute `source_words` once per run.

**Report accuracy.**
- **Misattributed false alarm:** the round-2 "extra probe" `## Review of where investigators found missing records` is already scored FACTUAL and FAILs on main (verified). The report presents it as an E2 false alarm when it is pre-existing.
- **Real costs missing:** the honest cost that is new is the single-word and compound list above, which the report does not list.

## 3. Evasions of the new rule (not blockers; all PASS on both main and branch)

**Rule (b), the novel-predicate list:**
- **Word anywhere in the store:** any source containing the word disarms the rule. `Origami guide: each sheet folds twice.` makes `## Quay Trust folds` PASS. A captured copy of the draft itself (a self-source) also disarms rule (b) completely, because `source_words` is built from every store record: self-sources, `haiku_summary` and failed retrievals included.
- **Base form in the middle:** `## Police arrest Quay Trust directors` passes. Headline present-tense `-s` forms (`hides`, `fines`, `admits`) are already scored by main, so they are not open.
- **Premodifier prefix:** `## Possible lies` passes.
- **Confusables:** a Cyrillic `і` (`lіed`) or a zero-width space (`li​ed`) passes. E2 does not apply `_confusable_fold`, though E1's `_e1_falsity` does. A soft hyphen is already caught by main.

**Rule (a), the disowned source span:**
- **Short span:** a 5-token span (`regulator found fraud at Quay`) passes.
- **Predicate-first span:** a heading that starts with the predicate (`Found fraud at Quay Trust last spring`) passes, because the predicate is only searched in `words[1:]`.
- **One inserted word:** `The regulator found real fraud at Quay Trust` passes.
- **Markdown emphasis in the source:** `**found**` breaks the `find`.
- **Combined with rule (b):** a predicate present in the disowned source itself disables (b), so every one of these (a) misses leaves the heading NON_CLAIM.
- **Outside the existing denial readings:** inherited and documented. Unlisted verbs (`uncovered`, `defrauded`, `misled`) are already scored by main.

## Method
- **Main side:** a detached worktree of origin/main 0c0ddc4 (removed after the run).
- **Error-B and Error-A:** the four `run.py` runners, with `--base` pointed at each side and output to scratch.
- **Usage genres:** an in-process loop over the `run.py` helpers, so the tracked `results.json` was not written.
- **Probes and fuzz:** a CLI harness that runs both gates' `--json` on identical stores. Scripts are in `probe/`.
- **Repository:** no repo file was modified.
