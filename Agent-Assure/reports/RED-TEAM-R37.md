# RED-TEAM-R37: adversary round on the R36 fixes (branch overnight-2026-11-14 at 9dae061, compared with main 83a5cb9)

**Verdict: 0 BLOCKERS. 14 HOLE classes still pass on the branch (about 55 drafts; every one also passes on main, so none is a regression). Error-A: 14 honest headings and 15 honest source shapes that main grounds are now refused.**

Scope: `git diff 83a5cb9 9dae061 -- Agent-Assure/scripts Agent-Assure/tests`. Read-only on scripts/ and tests/. The worktree tree matches 9dae061 (`git diff --quiet 9dae061 -- Agent-Assure/scripts Agent-Assure/tests` is clean). `uv run pytest -q` on the branch: 1236 passed, 2 skipped, 60 xfailed, exit 0.

## Method

- **Main copy:** `git show 83a5cb9:Agent-Assure/scripts/ground_check.py > /private/tmp/claude-501/r37/gc_main.py`. No stash or checkout was used.
- **Side-by-side harness:** `reports/r37_probe/harness.py <cases.py>` runs each (source, draft) pair through both CLIs with `--json`. Case files: `c1.py` (blocker probes), `c2.py`/`c3.py` (denial holes), `c4.py` (Error-A), `c5.py` (headline holes), `c6.py` (controls). The harness expects the main copy at the path above.
- **Differential fuzzer:** `reports/r37_probe/fuzz.py <seed> <n>` loads both modules in one process. It crosses 19 denial phrasings × positions (before / after / same sentence / none) × separators (space, newline, blank line) × 5 source headings, against 12 draft headings (cited and uncited, from the new word lists) × 5 bodies. It reports any case where the branch gives PASS and main does not.
- **Code read:** every changed hunk was checked against the paths that refused on main.

## BLOCKERS (branch PASS or GROUNDED where main refuses): 0

| Check | Evidence | Result |
|---|---|---|
| Rewritten `_has_denial` (set to ordered tuple) | Same `_folded(tokens) & _DENIAL_TOKENS` test, with `_phrasal_denial` added by OR. All 5 callers pass tuples, so the new `TypeError` cannot fire. | No refusal lost |
| `_unit_denied` | `before`, `previous`, `previous2` and `following` keep main's tests token for token. The new `context_denied` check and the strong-denial check only add `return True`. | No refusal lost |
| `_source_unit_contexts` | Adds `context_denied` only. `_sentence_spans` cannot raise, because every sentence is a substring of the same base text, found in order. | No refusal lost, no crash path |
| `_header_asserts` | One added `return True`, after the allowlist exactly as on main. A heading that becomes scored can only add a numerator verdict or a retained violation. `"# Revenue doubles [S1]"` was already scored GROUNDED on main (c1). | No widening |
| Fuzzer | Seeds 1, 2, 3 at 40,000 cases each (120,000 total): branch-only PASS **0**, crashes 0, both PASS about 1,250 per seed, main-only PASS about 3,400 per seed (the new refusals). | 0 |
| Test changes | The r4 tripwire's strict xfail was removed because the test now passes. Its assertion was not edited. | Not weakened |

## HOLES (near-variants of the R36 attacks that still PASS on the branch)

Every row below is gate=PASS with the copied claim GROUNDED on **both** the branch and main. `C` = "The regional bank collapsed in March after the regulator completed its audit". `F` = " Staff left. Records were filed. ". The draft is `C [S1].` unless stated.

| # | Class | Source draft(s) (shortened) | Branch | Main |
|---|---|---|---|---|
| H1 | Denial after the claim **in the same sentence** (only the prefix and the next sentence are read) | `C, which is a myth.` / `C (fabricated).` / `C - a complete fabrication.` / source `Revenue doubles is a myth.`, draft `Revenue doubles [S1].` | PASS | PASS |
| H2 | Phrasal siblings not listed | `The account was cooked up.`+F+C / `dreamed up` / `trumped up` / `The tabloid makes up stories.` | PASS | PASS |
| H3 | Falsity words not listed, and **inflections of listed ones** | `fabricates`, `fabricating`, `falsified`, `apocryphal`, `invented`, `invention`, `misinformation`, `disinformation`, `inaccurate`, `It was all lies.` (each 3 sentences back) | PASS | PASS |
| H4 | Event negation outside the 4 target words | `The tale I tell did not occur.` / `It never took place.` / `None of it is real.` (3 back) | PASS | PASS |
| H5 | "false" without a copula | `Reporters called it false.`+F+C | PASS | PASS |
| H6 | Next-sentence falsity outside the strong list (NEW-1 sibling) | `C. The story was invented.` / `... was cooked up.` / `... is apocryphal.` / `The event did not occur.` | PASS | PASS |
| H7 | Look-alike and format characters outside the fold | `fɑbricated` (Latin alpha), `fabri​cated` (zero-width space), `fabri­cated` (soft hyphen), `fıctional` (dotless i). The Cyrillic о, full-width, math-bold and `made​ up` forms are refused. | PASS | PASS |
| H8 | Forward-pointing denial of 13+ tokens with no falsity word | `We checked each of the items below and not one of them holds up.` (13 tokens; the 12-token form is refused) / `None of the reports this page collected from the forums last winter is accurate.` / `What follows in the rest of this short note from the forum did not occur.` | PASS | PASS |
| H9 | Denial in the **previous paragraph** (the named load-bearing assumption) | `None of this is true. Use z.\n\nOk then. Fine.\n\nC.` / blockquote `> None of this is true.\n\nStaff left. Records were filed.\n\nC.` / `Rumours we investigated and found to be false.` (ends with a period, so not heading-shaped) + a 3-sentence paragraph + C | PASS | PASS |
| H10 | **Heading scope cut by any short line**, which evades the NEW-2 fix | `## Myths about the bank\n\nPeople talked. Some wrote. Others posted.\n\nMore\n\nC.` (one bare word "More" ends the scope; the control without it is refused) / an `And so` line / a `### The collapse` sub-heading | PASS | PASS |
| H11 | Heading label words that are excluded or not listed | `## Lies the tabloids told` / `## Wrong claims about the bank` / `## Inventions of the press` / `**Lies the tabloids told**` (each + a 3-sentence paragraph + C) | PASS | PASS |
| H12 | Denial label longer than 12 tokens, or run on into prose | `Rumours that we investigated over the summer and found in the end to be false` + paragraph + C / `Rumours we found to be false and the people who spread them. ...` | PASS | PASS |
| H13 | "follows" synonyms | `What comes after is invented. One. Two. Three.` + C | PASS | PASS |
| H14 | Headline verbs and predicates not listed (draft `<heading>\n\nC [S1].`, heading read as NON_CLAIM) | `# Acme Stumbles` (the strict xfail already tracks this one), `# Bank Folds`, `# Stock Drops`, `# Bank Defaults`, `# CEO Lies` (left out on purpose), `# CEO Out`, `# Acme Under Investigation`, `## CEO arrest looming`, `## Revenue Doubling`, `# Acme-guilty` (hyphen-joined), `# Bank Collɑpses` (Latin alpha not folded) | PASS | PASS |

Probes the branch now refuses (these passed on main): bold, HTML `<h2>` and setext denial headings; markdown list items carrying "None of this is true."; `made-up` / `Made Up` / `fairy-tale` / `make-believe` 3 back; `# Bank Collapses!`; `## Revenue doubles.`; `## Bust: Acme`; Cyrillic а and zero-width-space headline verbs.

## ERROR-A (honest drafts that main PASSes and the branch refuses)

**Headings** (draft `<heading>\n\nC [S1].`; branch reads the heading as UNCITED, gate FAIL; main reads it as NON_CLAIM, gate PASS). Plural nouns hit by `_HEADLINE_VERBS_S`: `## Price rises`, `## Market crashes`, `## Server crashes`, `## Account bans`, `## Insider buys`, `## Police raids`, `## Recent arrests`, `## Price jumps`, `## Hospital admits`, `## Compiler warns`. Words newly in `_CLAIM_BEARING_HEADING_WORDS`, with no length guard: `## Guilty pleas`, `## Boom and bust`, `## Imminent deadlines`, and the one-word `## Everywhere`. These headings are unchanged and not refused: `## Results`, `## Key Takeaways`, `# What Matters`, `## Stock splits`. `# Sales Rises` is refused on main as well, so it is not new.

**Source shapes** (honest source + F + C; branch UNGROUNDED, gate FAIL; main GROUNDED, gate PASS):

| Shape | Rule that fires | Named in a CEILING? |
|---|---|---|
| `The board is made up entirely of independent directors.` / `Women made up 40 percent of the workforce.` / `Retail deposits made up two thirds of funding.` | `_phrasal_denial`: "entirely", digits and number words are missing from `_MADE_UP_NON_DENIAL_NEXT`. Because the phrase is strong, it refuses the **whole paragraph**. | No ("made up lost ground" is named; numbers are not) |
| `When the strict flag is false, the parser accepts trailing commas.` | predicative "false" (copula "is"). Common in code docs. | No |
| `The planned merger never happened.` / `The expected rebound did not happen.` | event-negation rule, paragraph-wide | No |
| `Staff ran a fantasy football league.` | "fantasy" is in the strong list | No |
| `The procedure follows the RFC, not the draft.` | "follows" + "not" makes a short pointing sentence, so `_paragraph_denied` refuses the rest of the paragraph. The control in a separate paragraph grounds. The R36-FIXES note kept "follows" out of the scope list to avoid exactly this; the paragraph rule brings it back at paragraph scope. | Partly (the scope list only) |
| `This did not affect depositors.` / `None of this changed the outcome.` (3 back) | far pointing rule. Main reached only 2 back; the branch reaches the whole paragraph. | Yes ("This does not apply ...") |
| `Prosecutors said the invoices were fabricated.` / `The myth that banks never fail persisted for decades.` / `Critics asked whether the rumours were untrue.` / `The claim that the regulator acted late is not true.` | strong denial, paragraph-wide | Yes (the prosecutors example) |
| `## Myths and facts` (a standard FAQ heading) / `Rumours and facts` / `How the committee is made up` (short standalone lines) | `_heading_denied` disowns the whole section | `Rumours and facts` is named; the other two are not |

## Load-bearing assumption

"0 BLOCKERS" rests on two things. The first is the hunk-by-hunk reading that every change only adds refusals. The second is that the fuzzer's grammar is representative: it covers short single-source drafts and does not cover relational, absence, multi-source or self-source (Read-of-draft) paths. Those paths reach the changed code only through `_unit_denied` and `_header_asserts`, both of which were read directly. A blocker would need a path where a heading turning from NON_CLAIM into a scored claim changes how a *different* claim is decomposed or classified. No such coupling was found in `score_report` (each claim is judged on its own), but it was not fuzzed across multi-claim self-copy drafts beyond the existing r36 b-family tests, which are green.
