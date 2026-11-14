# R38-NARROWING: cut the RED-TEAM-R37 Error-A refusals, keep the R36 fabrication refusals

**Verdict: 17 of the 31 R37 Error-A shapes are restored and 14 are kept as disclosed Error-A. Every gate is green, and nothing passes that main 83a5cb9 refuses (0 in 240,000 fuzzed drafts). The cost is one traded refusal class, listed under "Trades" below.**

Worktree `ai-overnight-1114`, branch `overnight-2026-11-14`, base 2dc776b. Not committed. All changes are in `scripts/ground_check.py`, and each one narrows only a rule R36 added; main's rules are untouched (D-69). Reference copies: `/private/tmp/claude-501/r37/gc_main.py` (83a5cb9, checked with `cmp` against `git show`) and `/private/tmp/claude-501/r38/gc_2dc776b.py`.

## Shapes restored (main PASS, 2dc776b FAIL, R38 PASS)

| R37 shape | Rule change (all positional or structural, none keyed on case or length) |
|---|---|
| `When the strict flag is false, ...` | Predicative "false"/"fake" is not a falsity statement when a code/value noun (flag, option, value, field ...) is its subject (`_CODE_VALUE_NOUNS`). |
| `The planned merger never happened.` / `The expected rebound did not happen.` / `Prosecutors said the invoices were fabricated.` / `Staff ran a fantasy football league.` | **Referent test**: two or more sentences away, a falsity statement disowns a sentence only if it refers to it, either through a deictic/discourse word (this, it, the story, the figures, none of it, a myth ...), a bare denial ("Not true."), or a shared five-letter stem. Adjacent sentences keep the R36 NEW-1 rule unchanged. |
| `made up entirely of ...` / `made up 40 percent` / `made up two thirds` | "made up" + quantity, or + adverb + object, is the constituting sense (`_made_up_takes_object`). `The story is made up entirely.` is still a denial. |
| `The procedure follows the RFC, not the draft.` | "follows" points forward only with a free-relative head ("What follows", "all that follows"): `_points_forward`. |
| `This did not affect depositors.` / `None of this changed the outcome.` (3 back) | The far pointing rule now also needs a veracity word or a falsity statement ("no evidence for any of this", "None of this is accurate"). One or two back, main's rules still refuse it. |
| `## Myths and facts` / `Rumours and facts` (+ `## Fact or fiction`) | A FAQ heading (≤6 tokens, a truth word, a coordinator, no copula/negator, no other falsity word) does not disown its section. It is also cut out of the welded sentence before the strong test (`_strong_tokens`). |
| `How the committee is made up` | A "how/why/..." topic line whose only denial is "made up", and which has no discourse referent, does not disown. |
| `## Recent arrests` (+ `## Two raids`) | A headline "-s" word after **only** closed-class pre-modifiers has no subject. |
| `## Boom and bust`, `## Everywhere` | R36 predicate words (`_PREDICATE_HEADING_WORDS`) need a subject: they do not fire on a one-word heading or on a bare "X and <pred>" heading. |

## Kept as disclosed Error-A (each named in a CEILING: comment)

- **Noun-noun and verb headings (9):** `## Price rises`, `## Market crashes`, `## Server crashes`, `## Account bans`, `## Insider buys`, `## Police raids`, `## Price jumps`, `## Hospital admits`, `## Compiler warns`. A noun before a listed verb has the same shape as `## Revenue doubles`, and capitalisation is set by the author, so no structural signal separates them. Upgrade path: a POS tagger. CEILING is at the `_HEADLINE_VERBS_S` test in `_header_asserts`.
- **Attributive predicate headings (2):** `## Guilty pleas`, `## Imminent deadlines`. These have the same shape as the claim-bearing `# Rigged election`. CEILING is on `_predicate_heading_word`.
- **Source sentences that refer to the claim (3):** `The myth that banks never fail ...` (shares the stem "bank"), `Critics asked whether the rumours were untrue.` ("rumours" is a discourse noun), and `The claim that the regulator acted late is not true.` (shares "regul", and "claim" is a discourse noun). CEILING is in the `_paragraph_denied` docstring.

## Trades (refusals 2dc776b made that R38 gives back; main grounds all of them)

- **Synonym referent (the main cost):** `The meltdown never happened. <padding>. The bank collapsed ...` is now grounded. The denial shares no stem and no deictic word with the claim. Named in the `_paragraph_denied` CEILING.
- **FAQ and topic headings:** `## Myths and facts about the bank` over a section that holds only myths now grounds, as does `How the story was made up` without a discourse noun. A denial sitting in a separate paragraph under a FAQ heading (`## Myths and facts\n\nNone of this is true.\n\n...\n\n<claim>`) now grounds; this is the previous-paragraph hole H9, open on main. Named in the `_heading_line_denies` CEILING.
- **`made up` + number:** `The figures were made up 100 percent.` now grounds. Named in the `_made_up_takes_object` CEILING.
- **Fuzz breakdown of body-level give-backs:** 1,200 across 120k R38-grammar drafts. 688 are the carve-out shapes (honest), 310 are same-sentence denials ("..., which is a myth", hole H1, open on main and on 2dc776b; only the draft heading changed), 183 are FAQ/topic headings, and 19 are unrelated-subject denials (the referent test working as designed). In the R37 grammar, every one of the 40 give-backs is `The procedure follows the RFC, not the draft.`
- **New refusal (fail-closed):** `## How it works\n\nNo.\nPeople talked.\n...<claim>` is now refused. The bare "No." is read with the heading cut out. This is 2 cases in 120k.

## PROVEN-RED: new controls against 2dc776b

`cmp scripts/ground_check.py /private/tmp/claude-501/r38/gc_2dc776b.py` printed UNMODIFIED before the run. `uv run pytest -q tests/red_team_moat/test_moat_r38_error_a_controls.py -rA` gave exit 1: **21 failed, 19 passed**.

- **FAILED (all 21 restored controls):** 17 sources: board_made_up_entirely_of, fact_or_fiction_heading, fantasy_football, flag_is_false, how_committee_made_up, made_up_mostly_of, made_up_two_thirds, merger_never_happened, myths_and_facts_heading, none_of_this_changed, procedure_follows, prosecutors_fabricated, rebound_did_not_happen, rumours_and_facts_line, this_did_not_affect, value_is_false, women_made_up_40. 4 headings: `## Recent arrests`, `## Two raids`, `## Boom and bust`, `## Everywhere`.
- **PASSED (all 19 guards):** these are the nearest fabrication shapes to each carve-out, and they must hold on both versions. 12 sources: collapse_never_happened, everything_here_fabricated, how_heading_fabricated_body, it_is_false, made_up_end, made_up_entirely_bare, myths_heading, no_evidence_this, none_of_this_accurate, story_fabricated_far, that_never_happened, what_follows_untrue. 7 headings: `# Bank Collapses`, `# Acme guilty`, `# Acme guilty and doomed`, `## Fraud everywhere`, `## CEO arrest imminent`, `## Revenue doubles`, `## Acme crashes`.

## GREEN after the change

`uv run pytest -q tests/red_team_moat/test_moat_r38_error_a_controls.py -rA` gave exit 0: **40 passed**. The test file was byte-identical to the one used for the red run (checked with `cmp`).

## Gates

| Gate | Result |
|---|---|
| 1. Nothing passes that main refuses | `reports/r38_probe/fuzz3.py` (three-way, in-process). R37 grammar: seeds 1-3 × 40,000; R38 grammar (adds every carve-out and its nearest denials): seeds 1-3 × 40,000. **r38_pass_main_refuses = 0 in 240,000 drafts**, crashes 0. R37 harness case files c1-c6: 0 BLOCKER. c4 Error-A: 31 → 14. |
| 2. R36 tests and r36_probe | `test_moat_r36_*.py` unchanged (`git diff --quiet` clean): 43 passed, 1 xfailed. r36_probe: **4/34** (b1-b4, hole b only), 0 broken controls. |
| 3. Full suite and calibration | `uv run pytest -q`: **1276 passed, 2 skipped, 60 xfailed** (1236 + 40 new), exit 0. labels md5 `6215b526d03147295b003d7ccb0d171f`; `test_measure_rates.py` untouched, 3 passed. |
| 4. Usage genres | PASS **4** / NEEDS_WORK 3 / FAIL 33. Authored grounded **48** (branch 48, main 50). `results.json` restored from HEAD; `git diff --quiet` is clean. |

## Usage genres

No change from 2dc776b. The two b03 segments (a FAIL draft) stay UNGROUNDED. ALPHA-TESTER-GUIDE line 162, `This is the fabricated-citation catch.`, and line 163, `never "this is false"`, are falsity statements with the deictic "this" in the same list block, so the referent test keeps them. A quoted or negated falsity cannot be separated from a real one without a discourse model; this is disclosed, not fixed.

## CEILINGs added or amended (in the code)

`_paragraph_denied` (referent test: the synonym fail-open, and the shared-stem/discourse-noun Error-A), `_points_forward`, `_made_up_takes_object`, `_CODE_VALUE_NOUNS`, `_heading_line_denies`, the `_HEADLINE_VERBS_S` test in `_header_asserts` (the 9 kept headings), and `_predicate_heading_word` (the 2 kept headings). `_UnitContext.previous_strong` / `following_strong` default to None, and `_unit_denied` raises on None rather than reading it as "no denial".

## Load-bearing assumption

That the referent test's vocabulary (deictic and discourse words plus a five-letter stem) covers how real debunking pages point at what they deny. A debunker who names the claim only by a synonym, three or more sentences away in the same paragraph, now grounds where 2dc776b refused. Main grounds it too, so it is not a gate-1 regression, but it is the one class R36 closed that R38 reopens.
