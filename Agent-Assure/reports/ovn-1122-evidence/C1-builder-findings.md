# OVN-1122-C1 findings — R3 compose-before-grounding

# ROUND 4 (D-147, on top of fe2057e, uncommitted) — CURRENT STATE

## Changes
- BLOCKER fixed: `_predicate_supplier` treats a claim with no word tokens (`---`, `***`, `.`, `…`, `—`, emoji) as
  TRANSPARENT and keeps climbing; nothing left -> None -> refused. The continuation scope test uses the nearest
  worded predecessor (`_nearest_worded`), so `- item / . / 12 million dollars` is still a continuation.
- LATENT fixed: substring table test replaced by POSITIONAL provenance. `gfm_table_cells(draft, claims) ->
  frozenset[int]` aligns claims to draft lines with a forward-only cursor on the comment-stripped NFKC text (same
  stripping as decompose), marks lines of real GFM tables (header + same-width delimiter row; fenced lines
  excluded), and returns the claim indices cut from those lines. Passed as data to `r3_uncomposed`. A list item
  that repeats a table row's text, a table inside an HTML comment, and a table inside a code fence no longer exempt.
  Unalignable claim -> not a cell (stays in scope, fail-closed). Sibling-defect CEILING kept on gfm_table_cells.

## Proven red on fe2057e (fe2057e ground_check.py in a scratch copy, removed after): 13 failed
- test_wordless_line_between_heading_and_item_is_transparent[--- . *** … — ⚠️] (p02, p12, p22, p26, p67-type, p66)
- test_f7_wordless_line_between_lead_in_and_item (p30), test_f8_wordless_lines_around_continuation (p36)
- test_table_text_elsewhere_does_not_exempt_the_item x5 (p42, p43, p45, p48 comment, p49 fence)
All 13 assert the FRAGMENT's own per-claim verdict == UNGROUNDED (plus gate where meaningful).

## Adversary harness (adv/harness.py, all 73 probes, main vs this tree): c1 PASS on 0 probes (main PASS on 29);
51 probes changed; c1 grounding score above main on 0. Output: scratchpad adv_round4.txt.

## Addendum (F3 fab_verdicts GROUNDED) — answered with evidence, no code change needed
v3 manifest `fabricated` for r45_f3 is the HEADING text ("Criminals", "Fraudsters", "Convicted firms"), not the
name. `fab_verdicts` therefore reports the heading's per-claim row, which is NON_CLAIM and, by pre-existing
display convention, carries verdict GROUNDED (ground() returns GROUNDED for NON_CLAIM; it is not scored).
`other_refused 1` is the bare-name item, which R3 demotes: smoke run per_claim
`[('## Criminals','GROUNDED'), ('- Alder Haulage [S1]','UNGROUNDED')]`. The 5/15 non-escaped are the
"Convicted firms" headings that E2 promotes to an uncited FACTUAL claim. Tests assert the item's own verdict
(`_verdict(report, "- <name>") == "UNGROUNDED"`). Open (pre-existing, not R3): a NON_CLAIM heading displays
"GROUNDED" in per_claim, which a tester can misread.

## Measurements (00:00 IST; raw in after5/)
| Measure | Main | Round 4 |
|---|---|---|
| Suite | 1585 / 2 / 88 xfailed | 1636 passed / 2 skipped / 91 xfailed, exit 0 |
| v1 / v2 | 0/280, 0/269 | identical per draft |
| v3 certified | 490/510 | 450/510 (f3 10->0, f7 15->0, f8 15->0, f2 15 open) |
| Error-A | 2044/3990, PASS 5/NW 156/FAIL 175 | identical |
| usage_genres | 61/200, 4/40 PASS | identical |
Diff vs main: more grounded = 0 everywhere; toward refusal = v3 45 drafts (f3/f7/f8) only; honest claims lost 0.
f3 `## Carriers` control 15 -> 0 still disclosed separately. results.json restored via `git show HEAD:`.

## Bare items under a heading, counted on main corpora
- Method: list items, cited, that the R3 lexical test reads as predicate-free, whose supplier is a `#` heading.
- Error-A: 72 such items; 35 GROUNDED on main. By inspection NONE is a bare name: all 72 are full sentences
  whose verb the lexical test cannot see ("Timestamps use…", "Haruto split…", "Revenue rose…", "The study ran…").
  All 35 stay GROUNDED (whole-source-sentence exemption / composition grounds): 0 lost.
- usage_genres: 3 such items (b03 "UNCITED: a factual claim…", b06 "One JSON object per line", b11 "Changes go to…");
  all 3 UNGROUNDED on main already. b06 is the only genuinely verbless one.
- Bare-name shape (`## Company / - Fenton Ltd [S1]`): 0 occurrences in Error-A and usage_genres. The corpora do
  not measure the Error-A cost of refusing honest bare-name lists; that cost is unmeasured, not zero.


# ROUND 3 (D-145) — CURRENT STATE. Round 2 below is superseded only where this section says so.

## Round 3 change
- The round-2 table exemption (`"|" in claim.text`) keyed on an author-controlled character and was evaded
  (orchestrator probe). Replaced by structural GFM provenance, carried as DATA:
  `gfm_table_rows(draft) -> frozenset[str]` = lines of a block whose header line is followed by a delimiter row
  (`|---|`) with the same cell count, plus the following `|` lines. `_is_table_cell(text, table_rows)` exempts a
  claim only if every line of it lies inside such a row. `main()` computes the rows from the draft text and passes
  them to `r3_uncomposed(claims, store, table_rows, ...)`; `_r3_in_scope` and `_reader_text` take them as data.
  No flag parameters. CEILING (in code): line-level GFM only; a table nested in a list/blockquote is not recognised,
  so its cells fall into R3 scope (refusal-side). Upgrade: R1 render step's table nodes.

## Proven red on round-2 code (round-2 rule reconstructed in a scratch copy of scripts/ with `_is_table_cell` returning `"|" in text`, removed after the run; probe store = r45_f3_00 source)
| Probe | Round 2 | Round 3 |
|---|---|---|
| `## Criminals` / `- Alder Haulage \| [S1]` | PASS (item GROUNDED) | FAIL (UNGROUNDED) |
| `## Criminals` / `- Alder \| Haulage [S1]` | PASS (item GROUNDED) | FAIL (UNGROUNDED) |
| f7 lead-in / `- Alder Haulage \| [S1]` | FAIL gate, item GROUNDED | FAIL, item UNGROUNDED |
| `- Alder Haulage [S1]` (original) | FAIL | FAIL |
| real table `\| Firm \|/\|---\|/\| Alder Haulage [S1] \|` | FAIL | FAIL (unchanged) |
Tests added: `test_pipe_inside_a_list_item_does_not_exempt` (3 params), `test_gfm_table_rows_needs_a_delimiter_row`,
`test_real_table_cell_keeps_pre_r3_scope_exemption` (honest twin: a real table cell is not named by R3).

## Own red-team (D-145 item 3), each a test in the file
- REFUSED (test passes): trailing period, citation first (`- [S1] Alder Haulage`), bold, italics, inline code,
  `+` and `*` bullets, `1.` and `1)` numbered, nested indent under a parent item, trailing comma (11 params).
- EVADES -> strict-xfail CEILING tripwires (out of D-144 scope): bare name as a PARAGRAPH under the heading
  (`## Criminals` / `Alder Haulage [S1]`), and as a BLOCKQUOTE under the heading. Upgrade: compose along the real
  Markdown tree (R1). F2 strict-xfail unchanged.
- Real-table variant (`## Records` / `| Status | Firm |` ... `| Convicted | Alder Haulage [S1]. |`): refused today
  (uncited label cell / merged rows), kept as a plain guard test, not an evasion.
- Not probed: setext headings, HTML lists, definition lists (renderer-dependent, R1 territory).

## Round 3 measurements (23:44 IST; raw in scratchpad after4/)
| Measure | Main 5e47ebf | Round 3 |
|---|---|---|
| Suite | 1585 / 2 skipped / 88 xfailed | 1623 passed / 2 skipped / 91 xfailed, exit 0 |
| v1 / v2 certified | 0/280, 0/269 | 0/280, 0/269; every draft record identical to main |
| v3 certified | 490/510 | 450/510: f3 10->0, f7 15->0, f8 15->0, f2 15 (open) |
| Error-A | PASS 5 / NW 156 / FAIL 175, 2044/3990 | identical |
| usage_genres | 4/40 PASS, 61/200 | identical |
Diff of verdicts vs main: MORE grounded than main = 0 on v1, v2, v3, Error-A (claims and gates), usage. Toward
refusal: v3 45 drafts (f3/f7/f8 x15) only. Honest claims lost: 0. Separately disclosed: v3 f3 control
(`## Carriers` over `- Alder Haulage [S1]`) control PASS 15 -> 0 — correct under "traceable", corpus labels it honest.
results.json restored via `git show HEAD:...`; copies in after4/. Nothing committed.


# ROUND 2 (D-144) — CURRENT STATE. Sections below "Round 1 record" describe superseded passes 1-2.

## Round 2 design changes
- SCOPE (`_r3_in_scope`): R3 composes only (a) a list item (governor = heading / lead-in / list parent, nearest
  preceding non-list claim) and (b) a continuation (a non-list claim immediately after a non-table list item).
  Prose after a heading or sentence is out of scope and keeps main's behaviour. CEILING in code: a bare figure in its
  own paragraph directly under a heading still grounds by mention; upgrade = Markdown tree from the R1 render step.
- TABLES OUT (`_is_table_text`, any claim containing `|`): a cell keeps main's verdict exactly. CEILING in code names
  the sibling defect (a cell grounds by mention of its value; an author can move an F3 list into a table) and the
  upgrade (join cell to row label + column header once decomposition keeps table structure).
- SPLIT PIECES (`_predicate_test_text`): the predicate test reads `claim.split_from` when set. Load-bearing, shown
  directly: draft `## Notes / - The meeting was held in the main hall and lasted 28 minutes [S1].` -> with the fix
  `r3_uncomposed` = {}; with the predicate test reading the bare piece it refuses index 2
  ("The meeting was held in the main hall lasted 28 minutes"). Recovered cleanly (0 Error-A loss, below).
- `uncomposed` on score_report KEPT: it is plain data (claim index -> composed reading, used to downgrade that claim
  id and to print the reading), not a mode switch; `None` = empty. No flag parameters.
- Whole-source-sentence exemption kept from pass 2.
- Tests added: `test_split_piece_is_read_as_its_sentence` (honest twin), `test_table_cells_are_out_of_r3_scope`.
  File now 21 passed, 1 xfailed (F2). The 7 attack tests are unchanged from round 1 and were proven red on main.

## Round 2 measurements (first-hand, 23:32 IST; raw in scratchpad/ovn1122/c1/after3/)
| Measure | Main 5e47ebf | Round 2 |
|---|---|---|
| Suite | 1585 passed / 2 skipped / 88 xfailed | 1606 passed / 2 skipped / 89 xfailed, exit 0 |
| v1 certified | 0/280 | 0/280, per-draft records identical to main |
| v2 certified | 0/269 | 0/269, per-draft records identical to main |
| v3 certified | 490/510 | 450/510: f3 10->0, f7 15->0, f8 15->0, f2 15 (open); all other classes identical |
| Error-A | PASS 5 / NW 156 / FAIL 175, grounded 2044/3990 | identical: PASS 5 / NW 156 / FAIL 175, 2044/3990 |
| usage_genres | 4/40 PASS, 61/200 GROUNDED | identical |

Diff of verdicts vs main (scratchpad diffv.py; validated on pass 2 where it found the 136):
- Records MORE grounded than main: v1 0, v2 0, v3 0, Error-A claims 0 (gates up 0), usage claims 0.
- Records changed toward refusal: v1 0, v2 0, v3 45 (= f3 15, f7 15, f8 15 drafts), Error-A 0, usage 0.
- Honest claims still lost: Error-A 0, usage 0, v1/v2 controls 0.
- SEPARATELY DISCLOSED: v3 f3 control `## Carriers` over `- Alder Haulage [S1]` (source "Alder Haulage delivers
  cargo."): control PASS 15 -> 0. Verdict: the refusal is correct under "traceable" (the composed reading
  "Carriers: Alder Haulage" is not in the source), but the corpus labels it honest. It is the only honest loss.
- results.json restored to committed versions (`git show HEAD:...`); copies in after3/.


# Round 1 record (superseded by round 2 above)

## Design
Files: `Agent-Assure/scripts/ground_check.py` (new R3 section before `score_report`; `score_report` gains
`uncomposed: Mapping[int,str]` defaulting to an empty MappingProxy; `main()` computes it), new
`Agent-Assure/tests/test_moat_r3_compose_before_grounding.py`.

Rule. A cited, non-NON_CLAIM claim is a *predicate-free fragment* when `_lacks_predicate` finds no
auxiliary/copula/modal and no verb-suffixed word (`_VERB_SUFFIXES`) in an INNER position (not first, not
last word). Its predicate supplier (`_predicate_supplier`): for a list item, the nearest preceding
non-list claim (heading, lead-in, introducing paragraph; siblings skipped); otherwise the claim right
before it (item it continues / heading over it). `_reader_text` composes supplier reader-text + fragment
body (recursive, so heading > item > continuation chains). `r3_uncomposed` grounds the composition with
the ordinary `ground()` against the FRAGMENT's citations only (T1 per-source law) and returns
index -> composed reading for every fragment whose composition is not in the numerator, or
`no_structure_supplies_a_predicate` when nothing precedes it ("never GROUNDED alone").
`score_report` turns a numerator verdict for those indices into UNGROUNDED (existing verdict) and
appends an R3 sentence to evidence_basis. Refusal-only by construction: it only acts on numerator
verdicts and never on NON_CLAIM; a composed claim that classifies NON_CLAIM is scored as FACTUAL.

Why the predicate test is narrowed vs `_has_finite_verb`: that heuristic errs toward "has a verb"
(right for the denominator), which here is the Error-B direction: it reads "dollars", "companies",
"Holdings", "Haven", "Linden" as verbs, so F8 and several F3/F7 names would escape. Position is
source-fixed (the fragment must be verbatim source text), case is not consulted.

F2 decision. Not covered by R3 and not a sibling patch of `_e2_heading_asserts`: the F2 item has its
own predicate, so no predicate is missing; the heading flips the sense of a complete claim. One
structural rule would have to compose EVERY headed item, which refuses every honest headed list whose
heading is not source text, and telling `## Findings` from `## Myths` needs the heading word's meaning
(an author-controlled lexicon, barred by rule 3). Left as strict-xfail tripwire with a CEILING reason.
`_match_denied` untouched (ordering unchanged).

## Proven-red
New test file copied into a scratch worktree at main 5e47ebf (`/Users/saisumanth/vibe-coding/Agents/ai-ovn1122-c1-main`,
ground_check.py md5 dea0b5be6a334e3f656a07b2a1b94953), run, then removed. Result on main:
`15 failed, 4 passed, 1 xfailed`. The 7 attack tests fail on assertion (gate PASS 100.0 on six, the
seventh gate non-PASS via E2 but the bare name still GROUNDED); the 8 unit tests fail because the R3
functions do not exist on main; the 4 honest twins pass on main (as they must); F2 xfails on both.
```
PASSED tests/test_moat_r3_compose_before_grounding.py::test_f3_honest_heading_whose_composition_is_in_the_source
PASSED tests/test_moat_r3_compose_before_grounding.py::test_honest_heading_over_honest_full_item
PASSED tests/test_moat_r3_compose_before_grounding.py::test_f7_honest_lead_in_whose_composition_is_in_the_source
PASSED tests/test_moat_r3_compose_before_grounding.py::test_f8_honest_full_claims_twin
XFAIL tests/test_moat_r3_compose_before_grounding.py::test_f2_disowning_heading_over_full_claim_is_refused
FAILED tests/test_moat_r3_compose_before_grounding.py::test_f3_heading_over_bare_name_is_refused[Criminals-Alder Haulage]
FAILED tests/test_moat_r3_compose_before_grounding.py::test_f3_heading_over_bare_name_is_refused[Fraudsters-Haven Haulage]
FAILED tests/test_moat_r3_compose_before_grounding.py::test_f3_heading_over_bare_name_is_refused[Sanctioned operators-Alder Holdings]
FAILED tests/test_moat_r3_compose_before_grounding.py::test_f7_lead_in_over_name_from_another_source_is_refused
FAILED tests/test_moat_r3_compose_before_grounding.py::test_f7_lead_in_and_name_citing_the_same_source_is_refused
FAILED tests/test_moat_r3_compose_before_grounding.py::test_f8_continuation_figure_is_refused
FAILED tests/test_moat_r3_compose_before_grounding.py::test_bare_fragment_with_no_structure_is_never_grounded_alone
FAILED tests/test_moat_r3_compose_before_grounding.py::test_uncomposed_mapping_never_lifts_a_verdict
FAILED tests/test_moat_r3_compose_before_grounding.py::test_r3_uncomposed_is_pure
FAILED tests/test_moat_r3_compose_before_grounding.py::test_lacks_predicate[- Alder Haulage [S1]-True]
FAILED tests/test_moat_r3_compose_before_grounding.py::test_lacks_predicate[12 million dollars [S1]-True]
FAILED tests/test_moat_r3_compose_before_grounding.py::test_lacks_predicate[- Haven Haulage [S1]-True]
FAILED tests/test_moat_r3_compose_before_grounding.py::test_lacks_predicate[- other companies [S2]-True]
FAILED tests/test_moat_r3_compose_before_grounding.py::test_lacks_predicate[- Alder Haulage delivers cargo [S1].-False]
FAILED tests/test_moat_r3_compose_before_grounding.py::test_lacks_predicate[- Alder Haulage is a carrier [S1].-False]
15 failed, 4 passed, 1 xfailed in 4.55s
FAILED tests/test_moat_r3_compose_before_grounding.py::test_f3_heading_over_bare_name_is_refused[Criminals-Alder Haulage]
FAILED tests/test_moat_r3_compose_before_grounding.py::test_f3_heading_over_bare_name_is_refused[Fraudsters-Haven Haulage]
FAILED tests/test_moat_r3_compose_before_grounding.py::test_f3_heading_over_bare_name_is_refused[Sanctioned operators-Alder Holdings]
FAILED tests/test_moat_r3_compose_before_grounding.py::test_f7_lead_in_over_name_from_another_source_is_refused
FAILED tests/test_moat_r3_compose_before_grounding.py::test_f7_lead_in_and_name_citing_the_same_source_is_refused
FAILED tests/test_moat_r3_compose_before_grounding.py::test_f8_continuation_figure_is_refused
FAILED tests/test_moat_r3_compose_before_grounding.py::test_bare_fragment_with_no_structure_is_never_grounded_alone
   6 E       assert 'PASS' != 'PASS'
   4 E       AssertionError: {'gate': 'PASS', 'grounding_score': 100.0, 'per_claim': [{'evidence_basis': 'Checked verbatim ag
   2 E       AssertionError: {'gate': 'PASS', 'grounding_score': 100.0, 'per_claim': [{'evidence_basis': 'Not scored: this li
   1 E       AssertionError: assert 'GROUNDED' == 'UNGROUNDED'
```
On the fix: `19 passed, 1 xfailed`.

## Measurements
Baseline re-measured first-hand on main 5e47ebf (scratch worktree): v1 0/280 certified; v2 0/269; v3 490/510
certified (f2 15, f3 10, f7 15, f8 15); Error-A PASS 5 / NW 156 / FAIL 175, grounded 2044/3990; usage_genres
40 drafts PASS 4, 200 scored segments GROUNDED 61. Matches the orchestrator's 22:44 numbers.

### Pass 1 (unnarrowed: lexical predicate test only) — REJECTED, too costly
- v3 certified 490 -> 285; f3 10->0, f7 15->0, f8 15->0, f2 15 (open). BUT controls collapsed: a1..e1c, g1, d11
  control PASS 15 -> 2 each; f3 control 15 -> 0.
- Error-A grounded 2044 -> 1792 (-252); gates FAIL 175->210, NW 156->122, PASS 5->4.
- v1/v2: certified unchanged at 0; control PASS dropped in many classes (e.g. v1 causal_claim 14->0).
- usage_genres GROUNDED 61 -> 60.
- Cause (inspected): honest one-sentence prose with an irregular or phrase-final verb, e.g. v3 control
  `The Dover council held a public meeting [S1].` ("held" has no suffix; "meeting" is phrase-final) read as
  predicate-free, and with no preceding claim it hit the "never GROUNDED alone" branch.
- Narrowed ONCE: exempt a fragment whose words are exactly one whole sentence (or line) of a cited
  verbatim source (`_is_whole_source_sentence`) — a source-side property the draft author cannot set.

### Pass 2 (narrowed once: + whole-source-sentence exemption) — CURRENT CODE, still costly
| Corpus | Before (main) | After |
|---|---|---|
| v1 error_b_corpus certified | 0/280 | 0/280 (no class rises); control PASS drops: causal_claim 14->13, denied_2back 9->8, misattributed_quote 15->14, unsupported_claim 15->14, wrong_unit_rate 14->13 |
| v2 certified | 0/269 | 0/269 (no class rises); control PASS: hedge_dropped 13->12, negation_dropped 12->11, period_shift 12->11 |
| v3 certified | 490/510 | 450/510: f3 10->0, f7 15->0, f8 15->0, f2 15->15 (open, xfail); every other class unchanged; f3 control PASS 15->0 (only control drop) |
| v3 escaped (segment) | 490 | 460 (f7 15->0, f8 15->0; f3 segment-escaped stays 10 because the runner marks the heading span) |
| Error-A | PASS 5 / NW 156 / FAIL 175, grounded 2044/3990 | PASS 5 / NW 135 / FAIL 196, grounded 1908/3990 (-136, 0 gained) |
| usage_genres | PASS 4/40, GROUNDED 61/200 | PASS 4/40, GROUNDED 60/200 (c01_code_copied "directories safely [S1]." — a syntok split fragment of a copied sentence) |

Per the brief (drop > ~20 after one narrowing) I STOPPED here and did not tune further.
Raw outputs: scratchpad/ovn1122/c1/{base,after,after2}/*.out and *.results.json; lost list: error_a_lost.json.

### Suite and latency
- Suite on final code: `1604 passed, 2 skipped, 89 xfailed`, exit 0 (main: 1585/2/88; +19 new passing, +1 F2 xfail).
  An intermediate run failed `test_product_claim::test_the_verdict_path_imports_no_model_and_no_network` because I
  imported `types.MappingProxyType`; replaced with `Mapping[int, str] | None = None`, now green.
- Latency: no 200-source latency/perf check exists in the repo (searched "latency", `perf_counter`/`monotonic`,
  "200 sources"/`range(200)`: no perf test found by those vectors). Ad-hoc harness (scratchpad lat/): 200-source store,
  301-claim draft, CLI wall time, idle machine, 3 interleaved runs: main 1.68 / 2.14 / 2.15 s, fix 1.84 / 2.21 / 2.23 s
  (~+0.07 s, within run noise).

Every Error-A claim that left GROUNDED (136; none entered GROUNDED), with draft ids, and the verdict on each:

Verdict A — 126 table cells (`table_cell` 114 + `table_no_false` 12: "Yes", "False", "Priya", bare figures
like "62", "10%"). The composed reading (row label + column header + cell) IS supported: these drafts copy
the source's own Markdown table. So these are Error-A, honestly. Cause: decompose() splits a table row into
chained claims ("| Yes [S1].", "|\n| Audit export | Yes [S1]."), each cell is predicate-free, and
`_reader_text` chains through the previous cells / heading / bullets into a string that is in no source.
Note the flip side: on main these cells grounded by MENTION — "Yes [S1]" grounds against any source containing
"yes" — so main's GROUNDED was the R3 defect itself, correct only by luck. Proper fix: compose a cell with its
row label and column header (needs table structure from decompose / the R1 render step), not the claim chain.

Verdict B — 10 conjunction-split right halves ("The meeting was held in the main hall and lasted N minutes" x6,
"The new code removes N lines and adds M" x4). Composed reading supported (the whole sentence is verbatim).
Cause: the split piece "lasted 28 minutes" / "adds 42" has its verb as FIRST word, which `_lacks_predicate`
excludes by design, and it then composes with the left piece without the "and". Proper fix: a piece with
`split_from` composes with (i.e. is read as) its `split_from` sentence. Not applied (brief: narrow once).

Full list:
- [number] "The new code removes 5555 lines and adds 42" x1: code_review_000
- [number] "The new code removes 6545 lines and adds 30" x1: code_review_014
- [number] "The new code removes 2099 lines and adds 35" x1: code_review_020
- [number] "The new code removes 5786 lines and adds 47" x1: code_review_021
- [plain] "The meeting was held in the main hall and lasted 28 minutes" x1: news_brief_004
- [plain] "The meeting was held in the main hall and lasted 15 minutes" x1: news_brief_006
- [plain] "The meeting was held in the main hall and lasted 47 minutes" x1: news_brief_014
- [plain] "The meeting was held in the main hall and lasted 25 minutes" x1: news_brief_017
- [plain] "The meeting was held in the main hall and lasted 6 minutes" x1: news_brief_019
- [plain] "The meeting was held in the main hall and lasted 26 minutes" x1: news_brief_022
- [table_cell] "Yes" x48: product_docs_002, product_docs_002, product_docs_002, product_docs_002, product_docs_008, product_docs_008, product_docs_008, product_docs_010, product_docs_010, product_docs_010, product_docs_014, product_docs_014, product_docs_014, product_docs_014, product_docs_018, product_docs_018, product_docs_018, product_docs_018, product_docs_018, product_docs_020, product_docs_020, product_docs_020, meeting_notes_000, meeting_notes_000, meeting_notes_006, meeting_notes_008, meeting_notes_008, meeting_notes_012, meeting_notes_012, meeting_notes_018, financial_report_000, financial_report_000, financial_report_000, financial_report_008, financial_report_008, financial_report_010, financial_report_010, financial_report_012, financial_report_012, financial_report_012, financial_report_020, financial_report_020, financial_report_020, financial_report_022, sales_report_006, sales_report_016, sales_report_020, sales_report_020
- [table_cell] "10%" x3: financial_report_000, financial_report_012, financial_report_012
- [table_cell] "Priya" x2: meeting_notes_000, meeting_notes_012
- [table_cell] "16%" x2: research_summary_008, financial_report_008
- [table_cell] "28%" x2: research_summary_014, financial_report_022
- [table_cell] "62" x1: research_summary_000
- [table_cell] "23%" x1: research_summary_000
- [table_cell] "84" x1: research_summary_000
- [table_cell] "67%" x1: research_summary_000
- [table_cell] "343" x1: research_summary_002
- [table_cell] "190" x1: research_summary_002
- [table_cell] "57%" x1: research_summary_004
- [table_cell] "114" x1: research_summary_004
- [table_cell] "382" x1: research_summary_004
- [table_cell] "11%" x1: research_summary_004
- [table_cell] "87%" x1: research_summary_006
- [table_cell] "97" x1: research_summary_006
- [table_cell] "244" x1: research_summary_006
- [table_cell] "31%" x1: research_summary_008
- [table_cell] "319" x1: research_summary_008
- [table_cell] "394" x1: research_summary_008
- [table_cell] "18%" x1: research_summary_010
- [table_cell] "370" x1: research_summary_010
- [table_cell] "77%" x1: research_summary_010
- [table_cell] "369" x1: research_summary_010
- [table_cell] "21%" x1: research_summary_012
- [table_cell] "45" x1: research_summary_012
- [table_cell] "271" x1: research_summary_012
- [table_cell] "219" x1: research_summary_014
- [table_cell] "336" x1: research_summary_014
- [table_cell] "70%" x1: research_summary_016
- [table_cell] "248" x1: research_summary_016
- [table_cell] "107" x1: research_summary_016
- [table_cell] "365" x1: research_summary_018
- [table_cell] "7%" x1: research_summary_018
- [table_cell] "306" x1: research_summary_018
- [table_cell] "232" x1: research_summary_020
- [table_cell] "15%" x1: research_summary_020
- [table_cell] "61" x1: research_summary_020
- [table_cell] "75" x1: research_summary_022
- [table_cell] "69" x1: research_summary_022
- [table_cell] "625" x1: financial_report_000
- [table_cell] "144" x1: financial_report_000
- [table_cell] "13%" x1: financial_report_008
- [table_cell] "549" x1: financial_report_008
- [table_cell] "60" x1: financial_report_010
- [table_cell] "115" x1: financial_report_012
- [table_cell] "27%" x1: financial_report_020
- [table_cell] "255" x1: financial_report_020
- [table_cell] "1%" x1: financial_report_020
- [table_cell] "507" x1: financial_report_020
- [table_cell] "6%" x1: financial_report_020
- [table_cell] "145" x1: sales_report_002
- [table_cell] "333" x1: sales_report_004
- [table_cell] "329" x1: sales_report_006
- [table_cell] "210" x1: sales_report_008
- [table_cell] "89" x1: sales_report_010
- [table_cell] "358" x1: sales_report_012
- [table_cell] "399" x1: sales_report_014
- [table_cell] "332" x1: sales_report_016
- [table_cell] "307" x1: sales_report_018
- [table_cell] "375" x1: sales_report_020
- [table_no_false] "False" x12: sales_report_002, sales_report_002, sales_report_002, sales_report_004, sales_report_008, sales_report_008, sales_report_010, sales_report_010, sales_report_012, sales_report_012, sales_report_014, sales_report_018

## CEILINGs
1. `_lacks_predicate` — lexical, not a parser. Breaks: a 3+-word name with a suffixed INNER word ("Fenton Holdings
   Group") reads as predicate-bearing, so a bare mention still grounds (Error-B residual). Irregular / phrase-final /
   first-word verbs read as predicate-free (Error-A; the 10 conjunction pieces). Upgrade: pinned offline POS/dependency parse.
2. `_predicate_supplier` — decompose() drops indentation and table structure. Breaks: nested lists compose with the
   outer governor; table cells chain through previous cells (the 126 table Error-A). Upgrade: carry the Markdown tree
   (R1 render) and compose cell = row label + column header, item = parent.
3. `_is_whole_source_sentence` — a predicate-free line in the SOURCE (its heading, list item, caption) exempts a bare
   mention of that line. Upgrade: R1 render step distinguishes source blocks from sentences.
4. F2 (strict xfail in the new test file): disowning heading over a full verbatim claim stays open; needs the E2
   "draft heading not from source is scored" rule or the R2 assertion test (ADR).

## Open
- Error-A cost (-136 grounded, Error-A corpus) exceeds the ~20 budget after one narrowing. I stopped per brief.
  Decision for orchestrator/Sai (Escalation #1 by literal text — it moves the Error-A/Error-B trade): land as-is
  (fail-closed, closes F3/F7/F8), or authorise two structural follow-ups first: (a) split pieces read as their
  `split_from` sentence (expected to recover the 10); (b) table cells composed with row label + column header
  (expected to recover most of the 126; needs table structure). Neither is constant tuning; both are unmeasured.
- f3 corpus control (`## Carriers` over `- Alder Haulage [S1]`, source "Alder Haulage delivers cargo") now refuses:
  correct under "traceable" (the composed reading "Carriers: Alder Haulage" is not in the source), but the corpus
  labels it honest — BASELINE.md / control expectation for f3 needs a ruling.
- Corpus results.json files were restored to the committed versions (after-run copies kept in scratchpad after2/).
  BASELINE.md files not regenerated.
- Scratch worktree ai-ovn1122-c1-main removed. Nothing committed or pushed.
