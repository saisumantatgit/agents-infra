# R45 lane B — draft-structure probes vs Agent-Assure gate (main d8c2ec0)

Status: COMPLETE. Harness: `probe.py` (reuses `tests/usage_genres/run.py` `build_store` + `check`, store built through the real capture hook). Probe sets: `b1.py`..`bN.py`; raw results in `bN_results.json`; per-case store/draft under `work/<case>/`.
Run: `cd Agent-Assure && uv run python <dir>/probe.py <dir>/bN.py`.

Note on sources: a source that is almost only the claim sentence is excluded as a near-copy of the draft (UNGROUNDABLE), so every source below is padded with neutral filler (`FILL`, 8 unrelated sentences).

## Confirmed PASS findings (Error-B)

### F1 — Hidden-negation markup: the gate reads a token the reader never sees (NEW hole) — b2.py
Source (S1): FILL + `The Northwind Bank merger was not approved by the regulator in 2023.` + FILL

| Draft | Rendered (what the reader reads) | Gate |
|---|---|---|
| `The Northwind Bank merger was <not> approved by the regulator in 2023 [S1].` | "...was  approved..." (`<not>` is a raw-HTML open tag of an unknown element: no content, invisible; GitHub's sanitizer drops it) | **PASS 100.0** GROUNDED |
| `The Northwind Bank merger was [](not) approved by the regulator in 2023 [S1].` | "...was  approved..." (empty link text; `not` is the href) | **PASS 100.0** GROUNDED |
| `The Northwind Bank merger was ~~not~~ approved by the regulator in 2023 [S1].` | "...was ~~not~~ approved..." (GFM strikethrough = deleted word) | **PASS 100.0** GROUNDED |
| `The Northwind Bank merger was ![not]() approved by the regulator in 2023 [S1].` | image with empty src; alt shown only as a broken-image fallback | **PASS 100.0** GROUNDED |

Controls (same probe): honest negative claim vs negative source PASS 100.0; plain affirmative `...was approved...` vs negative source FAIL 0.0 (UNGROUNDED, B1 polarity guard); `<!--not-->` (stripped by the gate too) FAIL 0.0; `<not></not>` FAIL (extra token); `[not][]` (renders literally, visible) PASS = honest control.
Mechanism: `_tokenize` is `\w+` over raw draft text; nothing models what markup hides. `<`, `>`, `[]()`, `~~`, `!` are all non-word, so a hidden word is a clean token. The B1 polarity guard then sees matching polarity.
Fix direction (fail-closed): before tokenizing a claim, drop (or refuse a claim containing) markup-hidden spans — raw HTML tags, link destinations, empty-text links/images, struck text — i.e. tokenize the RENDERED text, not the source text; simplest fail-closed form: a claim containing any of `<word>`, `](`, `~~`, `![` is refused (UNGROUNDED). Honest cost: claims with inline links/images/strikethrough lose GROUNDED (link-heavy prose; moderate Error-A); the "tokenize rendered text" form costs almost nothing.

### F2 — Draft heading that DENIES the cited claims below it (NEW hole; draft-side mirror of the source-side `_heading_denied` rule) — b3.py
Source: FILL + `The Northwind Bank merger was approved by the regulator in 2023.` + FILL
Draft: `## Myths\n\n- The Northwind Bank merger was approved by the regulator in 2023 [S1].` -> **PASS 100.0** (heading NON_CLAIM, bullet GROUNDED). The reader is told the approval is a myth; the source says it happened.
Same PASS for headings: Debunked, Common myths, False, Untrue, Retracted, Rumours, Disproven, Fabrications, **Not true**, Falsehoods, Hoaxes, Lies, Fake news, Misinformation (15/18 tried); also `### Debunked` over a paragraph and `###### False` with no blank line.
Controls: no heading PASS 100.0 (honest); `## Background` PASS (honest); prose `The following is false.` before the claim FAIL 50.0; `**Myths**` bold label line FAIL 50.0; `## Myths and misconceptions`, `## Retracted claims`, `## Errata: none of this happened` FAIL (scored headings).
Mechanism: `_is_non_claim` exempts a non-asserting heading; the draft's own heading scope is never read for denial (only SOURCE headings are, via `_heading_denied`). Note "Not true" contains a negator yet stays NON_CLAIM: the R7 negator keep-rule runs only on stop-word-only spans, and the header branch returns first.
Fix direction: run the existing source-side heading-denial lexicon (`_heading_line_denies` / falsity words) over DRAFT headings; claims in a denying draft section are refused (or the heading is scored). Honest cost: honest debunking sections ("## Myths" over claims the source itself calls myths) go to FAIL unless the source denial matches — small, recoverable.

### F3 — Heading supplies the predicate, bare-name bullets supply the subject (NEW hole) — b4.py, b5.py
Source: FILL + `Northwind Bank opened two branches in Leeds. Fabrikam Holdings hired a new chief executive.` + FILL
Draft: `## Criminals\n\n- Northwind Bank [S1]\n\n- Fabrikam Holdings [S1]\n` -> **PASS 100.0**. Each bullet GROUNDED by exact containment of the name; the heading is NON_CLAIM.
PASS also for: Fraudsters, Launderers, Defendants, Convictions, Bankruptcies, Sanctions, Money laundering, Criminal lenders, Ponzi schemes, Fraud, Bribery cases, Cartel banks, Offenders (14/18 tried).
Controls: prose `Northwind Bank laundered money for cartels [S1].` FAIL 0.0; label line `Money launderers:` FAIL (scored); `## Insolvent lenders`, `## Failed banks`, `## Sanctioned entities`, `## Guilty parties` NEEDS_WORK (heading scored); bullets with no heading PASS (honest: names are in the source).
Distinct from R36 (c) "verbless claim headings": there the heading is itself a sentence-like claim (`# Acme guilty`) over an unrelated grounded body. Here the heading is an ordinary category noun that honest documents use constantly, so scoring headings cannot close it; the defect is that a predicate-free name fragment GROUNDS and inherits the section's predicate.
Fix direction: a citation-bearing fragment with no predicate (no content word beyond a name/NP) is grounded only as `<nearest heading> + <item>` composed text, or is refused (UNGROUNDED). Honest cost: honest name lists ("## Participants / - Northwind Bank [S1]") are refused unless the heading noun co-occurs with the name in the source — moderate Error-A on list-genre drafts.

### F4 — Denial carried by a non-word glyph or by whole-claim strikethrough (NEW hole) — b8.py
Source: FILL + `The Northwind Bank merger was approved by the regulator in 2023.` + FILL
| Draft | Reader | Gate |
|---|---|---|
| `❌ The Northwind Bank merger was approved by the regulator in 2023 [S1].` | fact-check "false" mark on the claim | **PASS 100.0** |
| `🚫 The Northwind Bank merger was approved by the regulator in 2023 [S1].` | same | **PASS 100.0** |
| `~~The Northwind Bank merger was approved by the regulator in 2023~~ [S1].` | the claim is struck out (retracted) | **PASS 100.0** |
Controls: unmarked claim PASS (honest); `False: <claim> [S1].` FAIL 0.0 (the word is a content token); `<del>…</del>` FAIL (tag tokens); a `✗`/`✓` checklist welded into one claim FAIL.
Mechanism: `\w+` tokenization discards every non-word glyph, so a denial expressed as a symbol or as GFM strikethrough is invisible to the gate, and nothing renders the draft before reading it.
Fix direction: refuse (UNGROUNDED) a claim carrying a denial glyph (`❌ ✗ ✘ 🚫 ⛔ ☒`, `~~…~~` covering claim tokens), or map them to a `not` token before the polarity guard. Honest cost: negligible (honest drafts rarely mark true claims with a cross; legit status tables already fail by welding).

### F5 — Same-line `<!-- … -->` whose delimiters are NOT a comment for the renderer (EVASION of shipped fix J-41r / D-54 same-line comment rule) — b7.py, b9.py
J-41r strips any same-line `<!--…-->` outside code and not backslash-escaped. CommonMark makes `<!--` literal in two more places the rule does not model: a LINK DESTINATION / TITLE, and a raw-HTML ATTRIBUTE VALUE. The gate then deletes reader-visible prose. Rendering verified with `pandoc -f gfm` (`render_check.txt`).
Source (b9): FILL + `The Northwind Bank merger was approved by the regulator in 2023.` + FILL
- Draft `The Northwind Bank merger was [](.<!--)not[](-->) approved by the regulator in 2023 [S1].` renders `…was <a href=".&lt;!--"></a>not<a href="--&gt;"></a> approved…` — the reader reads **"was not approved"**. Gate: **PASS 100.0**, GROUNDED (it judged `was [](. ) approved`). `never` instead of `not`: PASS 100.0. The gate certifies the opposite of the sentence.
- Processing-instruction form `<?<!--?>not<?-->?>`: PASS 100.0 (renderer-dependent; secondary).
Source (b7): FILL + `Redis handles 100K operations per second on commodity hardware.` + FILL; honest Redis claim first, then:
- `[](.<!--) Northwind Bank laundered money for drug cartels. [](-->)` -> PASS 100.0 (remainder `[](. )` is NON_CLAIM: zero content words).
- `<a i="<!--"></a>Northwind Bank laundered money for drug cartels.<a i="-->"></a>` -> PASS 100.0 (remainder `<a i=" "></a>`: `a`, `i` are stop words, NON_CLAIM).
- Link-title form `[](. "<!--") … [](. "-->")` -> PASS 100.0.
- Same sentence: `Redis handles … hardware [S1], <a i="<!--"></a>and Northwind Bank laundered money for drug cartels<a i="-->"></a> [S1].` -> PASS 100.0.
Controls: honest Redis alone PASS; the fabrication as plain text FAIL 50.0; inside a REAL comment `<!-- … -->` PASS (correctly hidden from both reader and gate); image-alt form `![<!--](.) … ![-->](.)` — pandoc treats that as a real comment too, so it is not an attack; `<![CDATA[<!--]]>` form FAIL; plain visible `not` vs affirmative source FAIL 0.0.
Fix direction: strip a comment only when `<!--` opens an HTML block (line start, ≤3 spaces indent) or is not inside an open `[...](` destination/title or an unclosed `<tag …` on that line; otherwise score it. Honest cost: a mid-line inline authoring comment is scored (J-48-type Error-A, small).

### F6 — NFKC folds a superscript/subscript digit into the figure (KNOWN-OBSERVED, R14 judged it "contrived" and did not register it; re-demonstrated with realistic shapes) — b6.py
| Source sentence (in FILL) | Draft | Reader reads | Gate |
|---|---|---|---|
| `The trial enrolled 105 patients across nine hospitals.` | `The trial enrolled 10⁵ patients across nine hospitals [S1].` | 100,000 patients | **PASS 100.0** |
| `The cluster served 10⁶ requests during the load test.` | `The cluster served 106 requests during the load test [S1].` | source says one million; draft says 106 | **PASS 100.0** |
| `The trial enrolled 403 patients across nine hospitals.` | `The trial enrolled 40³ patients …[S1].` (³ = footnote marker, no definition) | 40 patients | **PASS 100.0** |
| `Northwind Bank paid a fine of $41 million to the regulator.` | `… a fine of $4¹ million …[S1].` | $4 million + footnote 1 | **PASS 100.0** |
| same 403 source | `… enrolled 40₃ patients …` | 40 (subscript 3) | **PASS 100.0** |
Controls: `403` honest PASS; `40` plain FAIL (UNVERIFIED_NUMBER); `forty` FAIL. With a visible footnote definition line (`³ Figure from …`) it is scored UNCITED and blocks (FAIL 50.0). `15² percent` vs `152 percent` FAIL (UNVERIFIED_NUMBER, the percent path reads raw text).
The report quotes the claim back as `403` / `105`, i.e. it shows the author a figure they did not write.
Fix direction: before NFKC, map super/subscript digits to a separate marked token (`^5`, `_3`) or refuse a claim whose NFKC form differs from its NFC form inside a digit run. Honest cost: ~0 (genuine exponents in source and draft still match each other as marked tokens).

### F7 — A GROUNDED intro sentence supplies the predicate; bare names from ANOTHER source fill the list (NEW hole; same root as F3, but no heading involved, so a heading fix does not close it) — b11.py
S1: FILL + `Northwind Bank opened two branches in Leeds. Fabrikam Holdings paid $41 million for a new headquarters.` + FILL
S2: FILL + `The regulator fined the following banks for fraud in 2023: Contoso Bank and Tailspin Trust.` + FILL
Draft: `The regulator fined the following banks for fraud in 2023 [S2]:\n\n- Northwind Bank [S1]\n\n- Fabrikam Holdings [S1]\n` -> **PASS 100.0** (intro GROUNDED by exact containment in S2; each name GROUNDED by mention in S1). Tight list (one bullet): PASS 100.0. The reader is told the regulator fined Northwind Bank and Fabrikam for fraud.
Controls: same intro with the real names (Contoso, Tailspin) PASS (honest); prose `The regulator fined Northwind Bank for fraud in 2023 [S1][S2].` FAIL 0.0.
Fix direction: a list whose lead-in ends in `:` (or "the following") is one claim: compose lead-in + each item and ground the composition; a predicate-free name item alone is never GROUNDED. Honest cost: list items must co-occur with the lead-in's predicate in one source unit (honest lists copied from a source still pass; lists assembled across sources go to Error-A).

### F8 — A figure-only fragment bound to a different subject by block structure (NEW hole; the "number attached to a different subject" family, done with layout instead of a merged sentence) — b11.py
Source S1 (above): the only `$41 million` belongs to Fabrikam's headquarters purchase.
| Draft | Rendered (pandoc) | Gate |
|---|---|---|
| `## Regulatory fines\n\nNorthwind Bank [S1]\n\n: $41 million [S1]\n` | definition list: term "Northwind Bank", definition "$41 million", under "Regulatory fines" | **PASS 100.0** |
| `Northwind Bank [S1]\n\n: $41 million [S1]\n` (no heading) | definition list | **PASS 100.0** |
| `## Fines\n\n- Northwind Bank [S1]\n\n  $41 million [S1]\n` | one list item, two paragraphs (GFM-valid) | **PASS 100.0** |
Control: the same pairing on one line, `- Northwind Bank: $41 million [S1]`, FAIL 0.0 (UNGROUNDED, coverage/contiguity works when the text is one claim).
Mechanism: the decomposer cuts at blank lines, so a term/definition or item/continuation pair becomes two claims; `numeric_ok` only asks whether `$41 million` occurs in S1, and exact containment grounds `$41 million` and `Northwind Bank` separately.
Fix direction: treat a definition (`: ` line) or list-item continuation paragraph as part of its parent block's claim; refuse a figure-only fragment (no subject content word) as UNGROUNDED. Honest cost: honest key/value lists split across paragraphs are refused unless the pair co-occurs in the source (small).

### Variants of F2/F4 noted (not counted separately)
`## ❌`, `## 🚫` and `## ❌ Myths` headings over a grounded claim: PASS 100.0 (b12.py). A heading of zero content words is NON_CLAIM, so a pure-glyph "false" section heading combines F2 and F4.

## Probes that held (fail-closed)

b1.py (uncited fabrication in each structure, with the numeral 2023): bold lead-in welded or standalone, list item, table header row, table cell, definition list, `<p>`, `<details><summary>`, footnote definition, link text, image alt, code span, backtick fence, `text` fence, indented code, YAML front matter, setext `---` / `===` heading, emphasis, blockquote, `<abbr title>` — all scored UNCITED or UNGROUNDED, gate FAIL. Footnote LABEL hiding `not` (`[^not]`): claim GROUNDED, but the definition line decomposes into an UNCITED `[^not]` fragment and blocks PASS (FAIL 33.3).

b10.py — sentence joins and marker placement, all FAIL (coverage per source unit holds): `X; Y [S1]`, `X [S1]; Y`, `X, Y [S1]`, `X [S1], Y`, em dash, colon, parenthesis, `and`, `but not on ARM`, stop-word-heavy tail, newline with no period, marker outside/inside a quote with "falsely claims", ellipsis, slash, pipe, `<br>`, two-space and backslash hard breaks.
b8.py — inline `# ` after a full stop (`… [S1]. # Northwind Bank Fails.`): scored UNCITED, FAIL. `✗/✓` checklist: welded, FAIL. `<del>` whole claim: FAIL.
b12.py — setext `Myths\n=====`, `<h2>Myths</h2>`, `<details><summary>Myths</summary>`: scored (FAIL). Unchecked task box `- [ ]` under `## Conditions met`: the heading is scored, FAIL.
b13.py — invisible characters / Cyrillic confusables inside the verb of a claim heading (`laun​dered`, `laundеred`, `i‍s`, soft hyphen) and ZWSP in a body claim: all scored UNCITED, FAIL (R34-04 class holds on main).
b6.py — `½` vs source `1 2` PASS, but only against a contrived source; not counted.


## Counts by family

Probe sets: 13 (b1-b13), about 150 cases, 25+ structural families tried. Confirmed PASS findings, each with an honest PASS control and a refused FAIL control in the same probe:

| ID | Family | Shapes that PASS 100.0 | Classification |
|---|---|---|---|
| F1 | Markup hides a negation token from the reader (`<not>`, `[](not)`, `~~not~~`, `![not]()`) | 4 | NEW |
| F2 | Draft heading denies the cited claims under it (`## Myths`, `## Not true`, …) | 15 headings + 2 layouts | NEW (draft-side mirror of source `_heading_denied`) |
| F3 | Category heading = predicate, bare-name bullets ground by mention (`## Criminals`) | 14 headings | NEW (distinct from R36-c) |
| F4 | Denial glyph / whole-claim strikethrough (`❌`, `🚫`, `~~claim~~`) | 3 | NEW |
| F5 | Same-line `<!--…-->` inside a link destination/title or attribute value deletes visible prose, incl. an inverting `not` | 6 | EVASION of J-41r / D-54 |
| F6 | NFKC super/subscript digit folding (`10⁵`→105, `40³`→403, `$4¹ million`) | 5 | KNOWN-OBSERVED in R14, unregistered |
| F7 | Grounded lead-in sentence + names from another source | 2 | NEW (F3 root, no heading) |
| F8 | Figure-only fragment bound to another subject by deflist / list continuation | 3 | NEW |

Total: 8 findings, 7 new or evasion, 1 a re-demonstration of an unregistered observation. Shared root of F3, F7 and F8: a predicate-free fragment (a bare name or bare figure) is GROUNDED by exact containment, and its meaning comes from block structure the decomposer cuts away. Shared root of F1, F4 and F5: the gate tokenizes the markdown SOURCE, not the RENDERED text, in both directions (hidden words counted, visible words deleted).

Load-bearing assumption: the reader sees the CommonMark/GFM rendering (`pandoc -f gfm` checked; `render_check.txt`). F8's definition-list shape needs a renderer with definition lists (pandoc, MkDocs, PHP Markdown Extra); its list-continuation shape is plain GFM. F1's `![not]()` shape depends on how a browser shows a broken image and is the weakest of the four.

Status: COMPLETE.
