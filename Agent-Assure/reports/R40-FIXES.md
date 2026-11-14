# R40-FIXES: fail-closed fixes for the RED-TEAM-R37 hole classes

**Verdict: 11 of the 14 R37 hole classes are fixed and 3 are left open, each named in a CEILING: comment. Partial residues inside four of the fixed classes are also CEILINGed. Nothing passes that main ef3ae1f refuses (0 cases in 160,000 fuzzed drafts and 0 in 11.1M function-level match positions). The usage genres are byte-identical to main. 28 honest probe shapes are newly refused (listed below).**

Worktree `ovn1115-q1`, branch `ovn-1115-q1` (== main ef3ae1f). Not committed. Main reference copy:
`/private/tmp/claude-501/ovn1115-q1/gc_main.py` (`git show HEAD:...`, `cmp`-identical to the worktree file before any edit).
Probe copies (paths repointed to this worktree and the main copy): `/private/tmp/claude-501/ovn1115-q1/probe/`.
Outputs: `/private/tmp/claude-501/ovn1115-q1/out/`.

## Per-class disposition

`C` = the R37 claim. "3 back" = the denial is three sentences before `C` in the same paragraph.

| # | Class | Disposition | Mechanism (all refusal-only, OR'd onto main's tests; D-69) |
|---|---|---|---|
| H1 | Same-sentence trailing denial | **Fixed** | `_trailing_denied`: `_has_strong_denial` applied to the words after the match, plus the later units of the sentence on the same line (new `_UnitContext.suffix`). This is the R36 next-sentence rule moved one boundary closer. On the anchor path the claim's own words are skipped. |
| H2 | cooked/dreamed/trumped up, makes up | **Fixed** | `_falsity_construction`: copula + `cooked/dreamed/dreamt/thought/conjured up` with a content subject; `trumped up` anywhere; `make(s) up` + a content noun, keeping the constituting exemptions. |
| H3 | fabricates, falsified, apocryphal, invented, invention, mis/disinformation, inaccurate, "all lies", falsely | **Fixed** | Unconditional: `apocryphal`, `falsif*`. `fabricate(s)/fabricating` count with no object or with a content object. Copula + `lie(s)/misinformation/disinformation` with any subject. Copula + bare `invention`. Copula + `invented/inaccurate/doctored/...` only with a content subject (`_DISCOURSE_NOUNS`) or a "what follows/comes after" subject, so "The telephone was invented" stays honest. `falsely` + a reporting verb. |
| H4 | did not occur, never took place, not real | **Fixed** | Negator + `occur(s)`; negator + `take/took place`; copula + (`not`) + `real` at the end of a clause (so "not a real number" and "not real-time" stay honest). |
| H5 | "called it false" | **Fixed** | `false/fake` within 3 words after a verdict verb, with the clause ending after it ("found false positives" stays honest). |
| H6 | Next-sentence siblings | **Fixed** | Follows from H2-H4: all of these are strong, so the R36 NEW-1 rule fires. |
| H7 | Latin alpha, ZWSP, soft hyphen, dotless ı | **Fixed** | `_comparison_view` builds a second copy of the text for comparison only. Look-alikes are mapped, combining marks are dropped, and format/filler characters inside a word are removed. Every denial test runs again on this copy and the result is OR'd (`_match_denied`, `_header_asserts`). The view is a copy rather than a wider `_confusable_fold`, because the fold also feeds R38 exemptions, and widening it there would pass text main refuses. Content is never rewritten. |
| H8 | Forward denial of 13+ tokens | **Fixed (one line, up to 24 tokens)** | `_long_line_points`: a one-line sentence (welded tables and code span several lines) with denial + forward reference + falsity or a truth word from a narrow set. CEILING: over 24 tokens, or wrapped across lines. |
| H9 | Previous-paragraph denial | **CEILING** | No safe rule: any distance bound can be padded past, and an unbounded rule lets every FAQ "None of this is true." disown the rest of the document. Recorded in the `_paragraph_denied` docstring; 3 strict xfails. |
| H10 | Heading scope cut by a short line | **Fixed for markdown, CEILING for plain lines** | `_heading_denied_r40`: a markdown denying heading of level L now reaches the next markdown heading of level ≤ L. A deeper sub-heading ends it only when it names the truth ("### The facts"). A non-markdown denying line has no level, so it keeps main's scope (1 strict xfail). |
| H11 | Lies / Wrong claims / Inventions | **Fixed except "Inventions"** | `_r40_heading_label_denies`: a falsity adjective directly before a content noun ("Wrong claims", "False claims"), or "Lies" opening the heading followed by a determiner, preposition or pronoun. "## Lie groups", "## False positives", "## Where the problem lies" and "## What went wrong" stay honest. "Inventions" is CEILINGed because it heads honest history sections. |
| H12 | Long label / run-on label | **Fixed for long standalone lines, CEILING for run-on** | `_heading_lines_r40`: a standalone line of 13-24 tokens that asserts falsity disowns its section. A label that runs on into prose is a sentence (1 strict xfail). |
| H13 | "follows" synonyms | **Fixed** | `_forward_free_relative` covers "what comes after/next/below"; `_points_forward` ORs it in. |
| H14 | Headline verbs / predicates | **Fixed: Stumbles, Falters, looming, Under Investigation, Acme-guilty, Collɑpses. CEILING: Folds, Drops, Defaults, Out, Lies, Doubling** | `_header_asserts_r40` splits hyphenated words, checks `_R40_HEADLINE_VERBS_S`, treats a final `looming` as a predicate, and treats "under investigation/probe/..." as a predicate. All of it runs on the heading and on its comparison copy. The CEILINGed words are routine honest labels ("Training folds", "Packet drops", "Configuration defaults", "Sign out", "Frequency doubling"); 6 strict xfails. |

**Residue reclassified, not a new hole:** R37's "The charges were trumped up." and "The tabloid is fabricating again." are strong after R40. Three sentences back they still ground, because the R38 referent test needs a pointing word or a shared stem, and neither sentence has one (this is the disclosed R38 synonym trade). With a referent ("The whole account was trumped up.") they are refused. Both are pinned as strict xfails.

## PROVEN-RED

The new test files were run against unmodified main. `scripts/ground_check.py` was replaced by the `cmp`-verified main copy, the tests were run, and the R40 file was copied back (`cmp` verified). No git stash or checkout was used.

- `test_moat_r40_fail_closed.py`: **54 FAILED / 0 passed** on main. These are 46 sources, 1 short-claim case and 7 headings. All 54 pass on R40.
- `test_moat_r40_honest_controls.py`: 31 passed on main and 31 on R40. These are Error-A guards, not red tests.
- `test_moat_r40_ceiling_tripwires.py`: 14 xfailed on main and 14 on R40 (strict). These are the CEILINGed shapes.
- One existing tripwire went green: `test_moat_r36_c_verbless_headings.py::test_unlisted_headline_verb_is_scored` ("# Acme Stumbles") XPASSed under strict xfail. Following the marker's own instruction, the marker was removed; **the assertion is unchanged**. This is the only edit to an existing test.

## Gates

| Gate | Result |
|---|---|
| Nothing passes that main refuses | Gate-level: `fuzz3.py` (R38 three-way harness; main stands in for both references) on R37 and R38 grammars, seeds 1, 2, 3 and 7 × 20,000 each = **160,000 drafts**. `r38_pass_main_refuses` = **0**, crashes 0. Function-level: `probe/mono.py` checks, for every unit × every match (start, end), that `main._unit_denied ⇒ R40._match_denied`, that units and tokens are identical, and that `main._header_asserts ⇒ R40._header_asserts` for every line. Seeds 1-4 × 30,000 sources = **11,085,788 positions**: MONO_VIOLATION **0**, HEADER_VIOLATION 0, misalign 0, crash 0. R37 harness c1-c6: 0 BLOCKER, 0 CRASH. |
| Existing tests | `uv run pytest -q`: **1362 passed, 2 skipped, 73 xfailed**, exit 0. That is the 1276 baseline + 85 new passes + 1 former xfail; xfails are 60 − 1 + 14. |
| Calibration | `labels-v2.csv` md5 `6215b526d03147295b003d7ccb0d171f`; `tests/test_measure_rates.py` untouched (`git diff --quiet`). |
| Usage genres | PASS **4** (unchanged); authored grounded **48** (unchanged, vs 48). The generated `results.json` is byte-identical to the one main produces. The committed file was restored from HEAD (`git diff --quiet` clean). |

## Error-A (honest controls)

- **R37 c4 (31 Error-A shapes) and c6 controls:** no verdict changed versus main.
- **R38 fuzz grammar:** every R40-only refusal in the 80,000 classified drafts (seeds 3 and 7, both grammars: 210 + 136 + 236 + 148) is an attack shape. Of the 730, 728 are the H1 "..., which is a myth" form; the other 2 are "C. This is not real." (an H4 denial of C). No honest shape is newly refused.
- **Usage genres:** 0 delta.

## New honest-text refusals (Error-A introduced)

Measured by `probe/erra.py`, main PASS → R40 FAIL, with the shape 3 sentences back and/or adjacent. Narrowed during the round: "fabricating it in-house" (pronoun objects were dropped from `_FABRICATE_OBJECTS`). Still refused, and disclosed in the CEILINGs:

1. **Falsity statements about something else, adjacent or sharing a referent:** "It is a lie that banks never fail." / "Its slogan is a lie." / "That rumour is misinformation." / "The quote is apocryphal." / "The hypothesis was falsified." / "The account is inaccurate in one detail." / "The figures were doctored by the old board." / "The data were manufactured in a lab." / "The legend was invented later." / "Critics called it false." / "Rivals falsely claimed the bank was solvent." / "Teachers make up stories for children." This is the same class as R38's kept "Prosecutors said the invoices were fabricated."
2. **Same sentence:** "C (the rumour that it was fabricated was false)." / "C, dispelling the myth of safety." (`probe/erra2.py`). "C, dispelling the myth that banks never fail." is refused on main as well, by the polarity rule ("never").
3. **One-line pointing negative with a truth word:** "This page does not list every case, and the figures below are not final or verified by anyone."
4. **Markdown denial heading scope:** "## Common myths ... Installation" (plain line) and "## Common myths ... ### Installation" (sub-heading without a truth word) now refuse the honest section after them.
5. **Label headings:** "## False claims" disowns its section. "## Fake news" is refused on main as well.
6. **Long standalone line:** "The myth that banks never fail persisted for decades among savers and regulators alike" (14 tokens, no final period) disowns its section.
7. **Draft headings:** "## Guilty-plea process" (hyphen split, the R38 "Guilty pleas" class) and "## Company concedes". "## Topics under investigation" and "## Areas under scrutiny" are scored on main as well, so they are not new.
8. **Comparison-copy misalignment:** a unit containing a contraction split by an invisible character ("ca​nnot") is refused (fail closed).

## Load-bearing assumption

That `_match_denied` and `_header_asserts` are the only paths by which the R40 diff reaches a verdict, and that every R40 addition is OR'd onto an unchanged main test. `_has_strong_denial` and `_points_forward` were widened in place. Every one of their consumers was checked to use them as a refusal: the R38 FAQ exemption reads `not _has_strong_denial`, so a wider test exempts less. `mono.py` confirms this mechanically at 11.1M positions. Its grammar covers random lexicon words, invisible and look-alike characters, and markdown, list, quote and table separators. It does not cover multi-source drafts or the self-source path; those reach the change only through the same two consumers.
