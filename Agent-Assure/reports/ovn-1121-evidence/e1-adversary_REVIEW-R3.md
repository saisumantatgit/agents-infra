# E1 final pre-merge adversary, round 3

**Verdict: 0 BLOCKERS.** Nothing that main refuses passes on the branch: 0 of 2,494 corpus jobs and 0 of 218 probes.

## Setup
- **Branch:** ovn-1121-e1 at 7bfdb4a (round 4, with main 375c828 merged in).
- **Main gate:** /Users/saisumanth/vibe-coding/Agents/ai-ovn1121-mainchk. Its scripts/ground_check.py has md5 19888bdcd3bb2df9e5bc0dd79ae72c43, the same as `origin/main:Agent-Assure/scripts/ground_check.py`.
- **Runtime diff:** the only runtime file the branch changes is scripts/ground_check.py (+91/-2). `calibration/feature_rows-v2.jsonl` is data and is not loaded by scripts. Its two rows that changed both moved toward refusal.
- **Harness:** r3/cmp.py. This is round 2's cmp.py with `error_b_corpus_v3` added. Both main and branch get the same evidence store, built through capture_hook.py.

## Code path
- **`_match_denied`:** it reads `_unit_denied(unit.main, start) or _r40_match_denied(...) or unit.e1_context or _e1_falsity(prefix) or _e1_falsity(suffix minus own)`. Main's two operands come first and are unchanged, and everything E1 adds is OR'd after them.
- **Callers:** there are two, and each is refusal-only:
  - **`_contained_with_matching_polarity`, line 1885:** `if all(_match_denied...): continue`. More denials only skip more units.
  - **t1 window, line 3957:** `and not _match_denied(...)`. More denials only remove windows.
- **`_denial_units`:** it adds the `e1_context` field and nothing else. Main's units, R40's units, the token-equality RuntimeError and the views are unchanged. Every unit gets `sentence_index=s` from `_source_unit_contexts`, so `e1[m.sentence_index]` indexes the same sentence list.
- **Exceptions:** nothing in this path catches exceptions broadly. Any exception from the new code propagates and refuses loudly; it cannot turn a claim into a pass.
- **The "made up to" exemption:** it sits inside `_e1_falsity`, so it can only drop refusals that E1 added. It cannot reach either of main's operands.

## Empirical
| Set | Jobs | Gate up | Score up | Claims gained (Error-B) | Claims lost (Error-A) |
|---|---|---|---|---|---|
| error_b v1+v2, error_a, usage_genres | 1,474 | 0 | 0 | 0 | 22 |
| error_b_corpus_v3 (510 drafts + 510 controls) | 1,020 | 0 | 0 | 0 | 0 |
| Round 1 and round 2 probes (probes, probes2/3/4) | 173 | 0 | 0 | 0 | 69 |
| New round 3 probes (probes_r3.json) | 45 | 0 | 0 | 0 | 9 |

- **Corpus losses:** the 22 losses are the same IDs round 2 found (r3/lost_ids vs r3/lost_r2, no diff). Each one is a refusal.
- **Repo tests:** the four E1 and R42 moat files give 98 passed and 15 xfailed.

## New probes for round 4's allowances (r3/probes_r3.log)
- **Lead-ins:** `However, that was made up.` and the other lead-in and reporting-frame probes are refused on both main and branch, or refused on the branch only (`In truth`, `Reporters say`).
- **Modals and all/just:** `That would have been cooked up.` is refused on the branch only; the other modal and all/just probes are refused on both.
- **Short adjuncts:** `out of thin air`, `entirely`, `to sell papers` and `last week` are all refused on the branch only.
- **"made up to …" exemption:** combining it with main's refusals (`That was made up to deceive. That claim is false.`, `...made up to deceive, and it is false.`, `...false and made up to sell papers.`) is still refused on the branch, because main's operand fires first.
- **Shapes both still pass:** `That was made up to deceive investors.`, `...to look real`, `...to mislead`, `...to sell papers`, `It was all made up to fool readers.`, the forward `That was made up to deceive: {C}`, and `The following was made up to deceive. {C}`. Each one also passes on main, and the CEILING note names them (passive "made up to deceive" and "the following" remain open).
- **Controls:** the honest `made up of`, `made up to the lender` and `made up the difference` all pass on both.

## Material, non-blocking
- **Exemption is wider than its purpose list:** the passive "made up to …" exemption lets through every purpose verb. The active-split branch, by contrast, refuses `to sell/deceive/mislead/trick/fool`. So `That was made up to mislead.` passes while `Reporters made it up to mislead.` is refused. This is fail-open relative to E1's own intent, but not relative to main, and the CEILING note discloses it. Narrow fix: exempt `made up to` only when the next word is not one of those purpose verbs.

## Load-bearing assumption
The verdict rests on `_match_denied` being the only place where the branch's verdicts differ from main's. That is backed by the diff (one runtime file, two hunks touching only `_denial_units` and `_match_denied`) and by the md5 match. The probe and corpus runs confirm it but do not prove it on their own.
