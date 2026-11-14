# Error-A ruling pack: five pass-widening candidates, measured on both sides

**Verdict: ship C2 as stated, ship C1 only in its narrowed upper-case form with a ceiling, do not ship C3, C4 or C5.** C1u + C2 together win back 358 of 1946 false refusals (2044 -> 2402 of 3990 cited claims grounded, 5 -> 8 drafts PASS) with gold Error-B still 0/27, the whole suite green, and zero new passes in the R36/R37/R38 probes and 6000 fuzz cases. The price is 4 of my 12 targeted list-number fabrications reaching PASS (named below). C3, C4 and C5 each let realistic fabrications through.

Measure only: nothing in any repo was changed except this file. Sai rules (Escalation #1).

## Method

- **Code measured:** main `10373da`, taken with `git archive 10373da Agent-Assure` into `/private/tmp/claude-501/ovn1115-q4/`, one full copy per variant. This report's worktree (`overnight-2026-11-15`, `a0bf080`) does not contain `10373da` (the corpus arrived in PR #35 on main), so nothing was measured here.
- **Patches:** `/private/tmp/claude-501/ovn1115-q4/tools/patch.py` (each candidate is a function that applies one exact-match edit to `scripts/ground_check.py`, and raises if its anchor is not found exactly once). The diff sizes are 11 to 43 lines.
- **Error-A:** `tests/error_a_corpus/run.py` (336 honest drafts, 3990 cited claims) and `tests/usage_genres/run.py` (40 drafts, 171 authored claims), each pointed at the variant with `--base`. The baseline reproduced BASELINE.md exactly (5 PASS / 156 NEEDS_WORK / 175 FAIL, 2044/3990).
- **Error-B, five layers:**
  1. Gold cells from `calibration.measure_rates.measure()`, the function `tests/test_measure_rates.py` pins.
  2. The full pytest suite (1341 collected, including `tests/red_team_moat/`).
  3. `reports/r36_probe.py` (40 cases, run from each variant's copy).
  4. All 152 cases from `reports/r37_probe/c1..c6.py`.
  5. The R38 `fuzz3.py` grammar, run as a differential fuzz (variant against main) for 3000 cases each on the r37 and r38 grammars.

  On top of those, 10 to 13 targeted fabrications per candidate, each aimed at exactly the relaxation (`tools/attacks*.py`). A **slip** is an attack whose gate moves to PASS on the variant while main refuses it.
- **Refinements measured (not in the brief):** C1u (upper-case-start ordinals only), C3b (`that`/`which` count as back-references only in the first two tokens), C4w (three or more columns only), and `rec` = C1u + C2. I added them because the candidates as stated failed on Error-B, and Sai needs to know whether a narrower version survives.

## Results table

Corpus = 336 honest drafts. Grounded = cited claims fully GROUNDED out of 3990. UG = usage_genres authored claims grounded out of 171 (drafts PASS/NW/FAIL). Gold = Error-B cells (fn, tp) from `measure()`. Lost = honest claims grounded on main that the variant refuses.

| Variant | PASS | NW | FAIL | Grounded | Gain | Lost | UG | Gold fn/tp | Suite | R36/R37/fuzz new PASS | Targeted slips |
|---|---|---|---|---|---|---|---|---|---|---|---|
| main | 5 | 156 | 175 | 2044 | - | - | 51 (4/3/33) | 0/27 | 1279 pass | - | - |
| C1 as stated | 5 | 175 | 156 | 2336 | +292 | 0 | 51 | 0/27 | green | 0/0/0 | **8 of 12** |
| C1u (upper-case start) | 5 | 174 | 157 | 2330 | +286 | 0 | 51 | 0/27 | green | 0/0/0 | **4 of 12** |
| C2 | 8 | 159 | 169 | 2113 | +69 | 0 | 51 | 0/27 | green | 0/0/0 | 0 of 11 |
| C3 as stated | 11 | 171 | 154 | 2153 | +109 | 0 | 55 | 0/27 | green | 0/0/0 | **11 of 12** |
| C3b (narrower) | 9 | 168 | 159 | 2134 | +90 | 0 | 53 | 0/27 | green | 0/0/0 | **2 of 12** |
| C4 as stated | 5 | 160 | 171 | 2089 | +45 | 0 | 52 | 0/27 | green | 0/0/0 | **8 of 31** |
| C4w (3+ columns) | 5 | 159 | 172 | 2086 | +42 | 0 | not run | 0/27 not run | not run | 0/0/0 | **5 of 31** |
| C5 (title heading) | 9 | 156 | 171 | 2044 | +0 (80 fewer structural refusals) | 0 | 51 | 0/27 | **36 red** | **4/7/60** | **9 of 11** |
| C1-C4 as stated | 16 | 197 | 123 | 2593 | +549 | 0 | 56 | 0/27 | green | 0/0/0 | union of the above |
| C1-C5 | 22 | 199 | 115 | 2593 | +549 | 0 | 56 | 0/27 | 36 red | 4/7/60 | union |
| **rec = C1u + C2** | **8** | **179** | **149** | **2402** | **+358** | **0** | **51** | **0/27** | **green** | **0/0/0** | **4 (all C1u)** |

Gold Error-A cells stayed at (fp 12, tn 13) for every variant, so the 52-row gold set does not see any of these changes in either direction. Every variant except C5 passes the existing suite, so the existing tests do not cover these relaxations, and the targeted attacks are the only Error-B evidence that does.

## C1 numbered-list ordinal

- **Today:** `_claim_figures` reads the `1` of `1. Members open ...` as a figure, and T1 also needs the token `1` in the source sentence. Removing the figure alone gained **0** claims (they turned UNVERIFIED_NUMBER -> UNGROUNDED). The ordinal has to be dropped on the matching side too (`_strip_citations`), which gained 292.
- **Error-A:** +292 claims (262 of them had the list number as their only cause). PASS drafts do not move (5), because these drafts also have uncited headings. usage_genres: 0.
- **Error-B, as stated:** gold, suite, R36, R37 and fuzz all unchanged. **8 of 12 targeted fabrications PASS:** `12) people died in the fire at the depot [S1].`, `40. people died ...`, `12)<tab>people died ...`, the full-width `１２. people died ...` (each reads as a count; the source gives no count), `9. People died ...`, and three ranked-list items such as `1. Acme Bank reported losses this year [S1].` where the source ranks Acme last. Four are refused: a bare `7. [S1]`, a paragraph-continuation `reached\n12. People died` (the splitter keeps `12.` with the previous sentence), `250. People ...`, and `1. 6 banks failed` (the `6` is still checked).
- **C1u (the item must start with a capital letter):** it closes the four lower-case "count" forms. It keeps 286 of the 292 claims. **4 of 12 still PASS:** `9. People died ...`, `1. Acme Bank ...` (rank), the same rank with a `1` elsewhere in the source, and `9. People died` with `Engine 9` in the source.
- **Conflict with a repo rule:** C1u's capital-letter test is case, a surface property the author controls, and the repo CLAUDE.md says never to key a moat rule on such a property. The test makes nothing pass that C1 as stated would refuse. It only removes the lower-case shapes, which read as a count in rendered text. An attacker who writes `9. People died` gets exactly the C1 slip, which is why the CEILING below is stated for the whole C1 family, not for C1u. A positional test (a blank line or list context) does not close it either: CommonMark renders `9. People died` after a blank line as list item 9.
- **Recommendation: SHIP-WITH-CEILING (C1u form, not as stated).** Main refuses every honest numbered list, so its rank check protects mostly by accident, and C1u wins back 286 claims for 4 rank/count slips.
- **CEILING text:** `CEILING: a list ordinal is never verified, so a rank or count carried only by the list number ("1. Acme had the largest losses", "9. People died") grounds; upgrade path: in decompose, keep the line context and treat an ordinal as furniture only after a blank line, a list item, or the start of the draft, and refuse items under a ranking label ("ranked", "top N").`

## C2 spelled percentages

- **What the figure matcher does today:** it is asymmetric. The claim-side `_NUMERIC_RE` has no `percent` suffix (the source-side `_SOURCE_NUMERIC_RE` has one). So the claim `85 percent` parses as (85, absolute), the verbatim source `85 percent` parses as (85, percent), and the result is UNVERIFIED_NUMBER. The same claim would match any bare `85` in the source (`85 employees`). The docstring of `numeric_ok` already promises `25% == 25 percent`.
- **Patch:** add `percent` to the claim-side suffix list (2 lines).
- **Error-A:** +69 claims (67 had `intrinsic:digits` as their cause), 5 -> 8 drafts PASS. usage_genres: 0.
- **Error-B:** gold, suite, R36, R37 and fuzz all unchanged. **0 of 11 targeted attacks PASS:** percent against a count of the same value, against `$12`, against `85 percentile`, against `percentage points`, a decimal shift, a wrong value, rise vs fall, another subject, and a denied source. Several moved from UNGROUNDED to UNVERIFIED_NUMBER, because the claim `85 percent` no longer matches a bare `85`.
- **Recommendation: SHIP.** It makes the code do what its docstring already promises, and no attack found a new pass.
- **Not covered:** a claim `85 percent` against a source `85%` is still refused (the number gate passes, T1 verbatim fails). That is a separate, wider relaxation and is not measured here.

## C3 next-sentence denial, clause-adjacent to the back-reference

- **Patch as stated:** the next sentence denies the claim only when a denial word sits within 2 tokens before or 3 tokens after a back-reference word (`that/this/it/these/those/which/above/foregoing`).
- **Error-A:** +109 claims, 5 -> 11 drafts PASS. usage_genres +4 (51 -> 55). It recovers 4 of the 7 S1 class-(iii) losses (c02 x3, c07) plus c01.
- **Error-B, as stated: 11 of 12 targeted denials PASS.** Each source is the claim followed by one of these sentences:
  - `Officials later said that the account, as told by the bank, was not accurate.`
  - `That account, according to two officials who reviewed the filings, was not accurate.`
  - `This, the auditors told reporters on Friday, did not take place.`
  - `None of the officials we asked could confirm it.`
  - `Those reports, the bank insists, are wrong.`
  - `It did, according to the bank, not take place.`
  - `Nothing in the filings supports it.`
  - `Which, the regulator noted in its statement, never took place.`
  - `Reporters cannot independently verify any of it.`
  - `We found no evidence in the public filings for that.`
  - `It is a version of events the bank has denied.`

  Any adjacency window passes a denial that is written with a parenthetical between its two halves, and that is ordinary news prose. The two near controls (`that is not what happened`, `this was simply not the case`) stay refused.
- **C3b (narrower: only `that`/`which` must be sentence-initial):** +90 claims, 9 PASS drafts, usage_genres +2. **2 of 12 still PASS:** `Officials later said that the account ... was not accurate.` and `We found no evidence in the public filings for that.`
- **Recommendation: DO-NOT-SHIP, either form.** Both pass realistic denials of the cited sentence, and a miss here ships a claim its own source denies.
- **Systemic fix:** a clause/coreference reading of what the next sentence denies. S1 already named it as the upgrade path. No lexical window separates `a rebase that goes wrong` from `said that the account ... was not accurate`.

## C4 table cells No / False not denying neighbours

- **Patch as stated:** a cell that is exactly `No`/`False`/`None` is replaced by a same-length non-denial word, but only in the denial context drawn from earlier units, rows and sentences. A cell in the claim's own row still denies. Matching text is unchanged. The patch raises if the mask changes the sentence, unit or token split.
- **Error-A:** +45 claims (feature-matrix `Yes` cells after a `No` row), PASS drafts unchanged (5), usage_genres +1 (c05's two segments, the S1 #6/#7 losses).
- **Error-B, as stated: 8 of 31 targeted table attacks PASS.** They are key/value records (`| Confirmed by | None |` above `| Report | <claim> |`), ditto rows (an empty or `"` cell under `False`), an `Events below ... None` row, and a `False` status row above the claim row.
- **C4w (tables of three or more columns only):** +42 claims. It closes the two-column cases. **5 of 31 still PASS**, all of them the same shapes written with three columns.
- **Recommendation: DO-NOT-SHIP, either form.** The gain is 45 claims and 0 PASS drafts, at the price of fact-check and status tables passing. The real defect is that the gate has no idea of rows and columns.
- **Systemic fix:** parse markdown tables into rows and columns, so a `No` in column X of row R qualifies only row R's claim cell under the matching header. That fix would also close the main holes listed below.

## C5 uncited headings and fences that read as labels

- **Safe structural signal: none found.** The most plausible one is the document title (a level-1 heading as the first segment, with no citation and no figure, which becomes NON_CLAIM). I measured it:
  - **Error-A:** structural refusals 244 -> 164, PASS drafts 5 -> 9, grounded claims unchanged.
  - **Error-B:** **36 moat tests turn red** (OI-MOAT-19 verbless headings, R34-02, R34-04 confusables, R35-01 allow-list neighbours, R36-c, R38 guards). It also reopens **4 R36 holes** (`c1_bank_collapses`, `c2_acme_guilty`, `c4_fraud_everywhere`, `c7_acme_insolvent`) and **7 R37 heading attacks** (`HH_profits_rise`, `HH_banks_fail`, the Cyrillic and zero-width-space disguises, and others), and gives **60 fuzz slips** (23 r38 + 37 r37). Of my 11 targeted titles, **9 PASS** (`# Bank Collapses`, `# Acme committed fraud`, `# Fraud confirmed by regulator` and others).
- **Fences:** the refused segments are `` ```python `` welded to its first code line, plus code lines such as `rows = load('data.log', dry_run=False)`. Uncited code asserts an API, and a fabricated API is exactly what the gate exists to catch, so I found no structural reason to exempt it.
- **Recommendation: DO-NOT-SHIP.** The title is the most-read line of a draft, and exempting it re-opens every headline attack of R34-R38.
- **Systemic fix:** the POS-tagger upgrade path already named in the OI-MOAT-19 and R36 CEILINGs. A recoverable workaround for authors is to cite the heading or remove it.

## Holes on main found along the way (not caused by any candidate)

- **Predicating headings with irregular or short verbs:** `# The regulator found fraud at Acme` and `# Regulator: the bank lied` over one honest cited sentence both PASS on main. `found` has no `-ed` ending, and `lied` is under the suffix length cut.
- **Denials after the claim in a table:** a key/value denial row below the claim (`| Event | <claim> |` then `| Happened | No |`), a same-row verdict cell after the claim (`| <claim> | March | False |`), and an `| All rows above | | No |` summary row all PASS on main. The prefix-only rule reads only what comes before the match.
- **R36 holes still open on main:** the 4 known ones (`b1_r31_03_verbatim_shape`, `b2_diluted_no_headings`, `b3`/`b4_source_heading_padding`) still reproduce, unchanged by every variant.

## Load-bearing assumption

That the targeted attacks represent what the relaxation exposes. They are my own designs, 10 to 13 per candidate, not an independent red team. "0 of 11" for C2 means "not found by these 11 attacks", not "no hole". The R36/R37/R38 probes and the fuzz grammar never contain numbered lists, spelled percentages or tables, so for C1, C2 and C4 they are a no-regression check, not an attack. A second weak seam: the C1u ruling depends on judging that rank or count via a list number is a less likely fabrication than the 286 honest claims it frees; Sai can reverse that call on the same numbers.
