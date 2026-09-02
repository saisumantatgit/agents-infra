# Base-Rate Probe: Quote vs. Paraphrase in Real Prose (2026-09-02)

**Status:** measurement only. No file under `scripts/` or `tests/` was touched.
**Corpus:** 10 chapters, `cpc-book/manuscript/*.md` (26,592 words) vs. the full
statute text, `cpc-book/reference/cpc-1908-fulltext-layout.txt` (174,259 words).
**Script:** `docs/reports/base_rate_probe.py` (reproducible — reruns to the
same JSON in `docs/reports/base_rate_probe_results.json`).

## BLUF

**Headline paraphrase rate = 8/79 = 10.1%** of source-matched claims (A+B+C+D)
would be wrongly flagged UNGROUNDED by the demoted lex-only gate. Stable at
10.1% at lex_tau 0.60–0.70; rises only to 12.3% at 0.50. **But this number is
not the finding that matters most.** Two facts dominate it:

1. **93.4% of factual/numeric/attribution/relational claims (1118/1197) have
   no plausible match anywhere in the whole statute** (bucket E) — this
   corpus's claims are overwhelmingly commentary, case outcomes, procedural
   narrative and worked illustrations, not restatements of statutory text.
2. Of the 79 claims that DO match, **90% (71/79) are already exact quotes or
   long verbatim spans (A+B)** — because legal-writing convention here is to
   quote the operative statutory language in quotation marks and then
   explain it. Genre-driven quoting, not gate-driven caution.
3. **All 8 of the C-bucket "paraphrases" are decomposition artifacts** —
   rhetorical-question fragments, markdown headers, and conjunction-split
   clause remnants — not substantive paraphrased legal claims. See §5. The
   D bucket is **empty** (0 members at any of the three tested cutoffs
   except 2 at 0.50, both also artifacts).

Read plainly: in a legal-textbook corpus with strong citation discipline,
**honest paraphrase of a genuinely source-backed claim is close to a
non-event** — writers here quote when they cite law. That is a narrow,
genre-specific answer to a genre-general question (see §6, Threats to
Validity) — it does not settle whether AI-agent-drafted research prose,
which this gate actually has to police, paraphrases at the same low rate.

## 1. Method

1. `decompose()` + `classify()` (imported from `scripts/ground_check.py`,
   unmodified) ran on each chapter's raw Markdown, HTML comments and all.
   Kept: FACTUAL, NUMERIC, ATTRIBUTION, RELATIONAL. Discarded: NON_CLAIM
   (190) and ABSENCE (261) — 451 discarded of 1,648 total decomposed
   fragments, 1,197 kept.
2. **Windowing = the gate's own ±2-sentence window**, not a token-count
   slide: reference text was split into sentences with `_split_sentences`
   (11,182 sentences), and for every claim the best-scoring window across
   *all* centers was found by re-deriving `t2_lexical_score`'s exact
   content-word-F1 + numeric-presence-gate formula over those windows
   (`_content_words`, `_tokenize`, `_strip_citations`, `_nfkc` all reused
   verbatim from `ground_check.py`; only the Counter-intersection arithmetic
   — not tokenization — was written locally, and precomputed once for the
   whole reference so every claim reuses the same 11,182 precomputed
   windows). This is simpler than a token-count slide and is exactly what
   `t2_lexical_score` itself does, so the score is provably the gate's own
   number, not an approximation of it.
3. Bucket A (EXACT): claim's whole token sequence (after `_strip_citations`)
   is a contiguous span of the *entire* reference token stream (not just the
   best window — checked against all 178,707 reference tokens via a
   space-delimited substring test, which is a whole-token-boundary-safe
   equivalent of `_claim_contained_verbatim`).
4. Bucket B (LONG-SPAN): not A, but some contiguous ≥8-token span of the
   claim appears anywhere in the reference (checked via a precomputed set of
   all 154,864 distinct 8-grams in the reference — O(1) membership test per
   window, equivalent to `t1_verbatim`'s span-matching but without its
   per-source anchoring/hedge refinements, which the task's bucket
   definition does not require).
5. Buckets C/D/E: per §3–4 of the task spec, using the best window's
   content-word set for the novel-token count and its F1 for the cutoff.

## 2. Per-chapter breakdown

| Chapter | Kept | A | B | C | D | E |
|---|---:|---:|---:|---:|---:|---:|
| execution.md | 137 | 2 | 4 | 0 | 0 | 131 |
| fast-lanes.md | 104 | 0 | 2 | 0 | 0 | 102 |
| first-appeal.md | 108 | 2 | 1 | 1 | 0 | 104 |
| institution.md | 142 | 5 | 9 | 2 | 0 | 126 |
| interim-relief.md | 97 | 0 | 6 | 0 | 0 | 91 |
| issues.md | 113 | 2 | 8 | 1 | 0 | 102 |
| judgment.md | 125 | 3 | 8 | 2 | 0 | 112 |
| narrow-doors.md | 103 | 1 | 4 | 0 | 0 | 98 |
| response.md | 160 | 1 | 8 | 1 | 0 | 150 |
| trial.md | 108 | 0 | 5 | 1 | 0 | 102 |
| **Total** | **1197** | **16** | **55** | **8** | **0** | **1118** |

No single chapter is an outlier: E dominates (89–98% of kept claims) in
every chapter, and B outnumbers A+C combined in 8 of 10 chapters. The
pattern is corpus-wide, not one unrepresentative chapter.

## 3. Sensitivity of the headline number to the E cutoff

| Cutoff | D count | A+B+C+D denom | Headline (C+D)/denom |
|---|---:|---:|---:|
| 0.50 | 2 | 81 | 12.3% |
| 0.60 (spec default) | 0 | 79 | 10.1% |
| 0.70 | 0 | 79 | 10.1% |

Moving the cutoff from 0.70 down to 0.50 moves the headline by 2.2 points
(10.1% → 12.3%) — low sensitivity, because the underlying distribution has
almost nothing sitting in the 0.50–0.70 band (see §5, only 2 rows qualify).
The number is far more sensitive to what counts as "matched" at all (E's
93% share) than to where inside 0.50–0.70 the D/E line is drawn.

## 4. The 16 audited examples (8 from C, 8 from D)

**Bucket D is empty at the spec cutoff (0.60).** At 0.50 it has exactly 2
members. Per the task's own audit requirement — a number nobody can check
is worthless here — both are shown below in full, followed by all 8 members
of C (there are exactly 8, so "8 sampled" is "all of them"), followed by the
next 6 highest-scoring near-misses (novel-count 1–3, any F1) for
transparency about what "almost D" looks like in this corpus.

### C — all 8 members (zero novel content tokens vs. best window)

| # | Chapter | Claim (verbatim) | Best-matching window (truncated) |
|---|---|---|---|
| 1 | first-appeal.md | "Is he wrong?" | "9. Misjoinder and non-joinder. 10. Suit in name of wrong plaintiff. Court may strike out or add parties." |
| 2 | institution.md | "rent for 1905, 1906 and 1907 is unpaid;" | "...The rent for the whole of the years 1905, 1906 and 1907 is due and unpaid. A sues B in 1908 only for the rent due for 1906..." |
| 3 | institution.md | "A sues in 1908 for 1906's rent only." | same window as #2 |
| 4 | issues.md | "The written statement is in," | "Evasive denial. 5. Specific denial. 6. Particulars of set-off to be given in written statement." |
| 5 | judgment.md | "The decree must agree with the judgment: suit number, parties, particulars of the claim —" | "...the decree shall agree with the judgment it shall contain the number of the suit, the names and descriptions of the parties..." |
| 6 | judgment.md | "Can you?" | "No. 8 — NOTICE TO INSPECT DOCUMENTS (O. 11, r. 17.)..." |
| 7 | response.md | "The written statement is in" | same window as #4 |
| 8 | trial.md | "The court may recall" | "17. Court may recall and examine witness. 17A. [Omitted.]. 18." |

**Audit verdict: none of these 8 is a genuine paraphrased legal claim.**
#1 and #6 are rhetorical questions from the manuscript's Socratic-dialogue
style, coincidentally overlapping a table-of-contents fragment on unrelated
content words ("wrong", "can/no"). #2/#3 are a worked numerical illustration
matching the statute's own worked illustration almost by construction — this
is a near-quote that the conjunction-splitter cut mid-sentence, costing it
bucket B only because the split discarded the connecting tokens. #4/#7 are
an identical sentence fragment ("The written statement is in[,]") that reads
as truncated mid-clause — likely a markdown table-cell fragment the sentence
segmenter mis-split. #5 is the closest to a real paraphrase (restates
Order XX Rule 6's decree-contents requirement in the author's own words) and
is the one genuinely interesting finding of the whole sample. #8 is a bare
verb phrase matching a table-of-contents line heading.

### D-cutoff-0.50 — both members (the only two "D" rows found anywhere in 0.50–0.70)

| # | Chapter | Claim (verbatim) | novel tokens | best F1 | Window (truncated) |
|---|---|---|---|---:|---|
| 1 | narrow-doors.md | "O.XLVII r.1(1) grounds;" | grounds, xlvii | 0.533 | "APPOINTMENT OF A RECEIVER (O. 40, r. 1.) (Title) ..." |
| 2 | institution.md | "## QUESTION 2 — Fine." | fine, question | 0.500 | "2 . . . . ." |

**Audit verdict: neither is a real claim.** #1 is a bare cross-reference
label left over after conjunction-splitting; #2 is literally a Markdown
section header ("## QUESTION 2 — Fine.") that `_is_non_claim`'s header
regex should have caught but didn't (it starts with `##` — worth a follow-up
issue against `decompose`/`classify`, filed as an open item below, not fixed
here per the read-only scope of this task). Both are decomposition noise,
not evidence about how a legal author paraphrases a source.

### 6 next-highest near-misses (context only — not bucket D members)

| Chapter | Claim | novel | F1 |
|---|---|---:|---:|
| issues.md | "The High Court, in revision, disagreed" | 1 | 0.462 |
| execution.md | "The executing court treated him as a pendente-lite transferee" | 3 | 0.444 |
| interim-relief.md | 'O.XXXIX r.2(1) has "injury complained, of,".' | 3 | 0.444 |
| issues.md | "A decree follows, dated the day of judgment [S7]." | 3 | 0.444 |
| trial.md | "The trial court dismissed the suit" | 2 | 0.444 |
| institution.md | "5. **Yes — she must.** Rule 11(a) is mandatory," | 2 | 0.429 |

Same pattern continues: every one of these is a sentence fragment (numbered
answer stubs, clause remnants) rather than a complete, self-contained
paraphrase of a specific statutory rule.

## 5. What the buckets actually contain (a second-order finding)

Both C and the near-D population are dominated by **decomposition
artifacts**, not paraphrase. A+B is not immune either: 16 of 79 A+B+C rows
(≈20%) are ≤6 words, mostly bare parenthetical citations like `(Section 47)`
that trivially "exact-match" because the statute literally contains the
string "Section 47" as a heading — these inflate bucket A without being
genuine quoted assertions. Bucket B, by contrast, is overwhelmingly genuine:
its members are long (median well over 20 tokens), sit inside explicit
quotation marks in the manuscript's own prose, and correspond to the
author's stated citation discipline (see manuscript front-matter: "no
arrows in prose, stakes carried by verified law"). B is the trustworthy 70%
of the ABCD population; A and C are the noisy 30%.

## 6. Threats to validity (honest accounting)

1. **Genre bias, not general-writing bias.** This corpus is a legal
   textbook explicitly built to quote a specific statute with citation
   discipline (see manuscript HTML-comment front matter on every chapter:
   "Verification basis: ... re-verification of s.6, s.149, s.9 ... in
   reference/cpc-1908-fulltext-layout.txt"). A textbook author who knows the
   exact section number is quoting will quote; a general non-fiction writer
   summarizing a source under no such discipline paraphrases far more. This
   result is a **lower bound on paraphrase rate for careful, source-checked
   legal writing**, not an estimate for AI-agent-drafted prose in general.
   **Direction: pushes the headline rate DOWN relative to the true rate for
   the gate's actual target population (agent drafts).**
2. **Whole-corpus matching vs. real per-claim citations.** We matched every
   claim against the entire 174K-word statute, not the specific section the
   author actually cited. This lets an unrelated section's vocabulary
   "explain away" a claim's content words purely by coincidence — it is
   strictly easier to find *some* matching window in 174K words than to find
   one in the single cited source. **Direction: this OVERSTATES how much of
   the corpus matches at all (inflates A+B+C+D, deflates E) and, within the
   matched population, makes C/D look more like near-misses than they would
   against the true narrow source — i.e. it UNDERSTATES the flag rate the
   gate would actually produce in production**, where grounding runs
   against the cited source only, not the whole corpus. Both this bias and
   #1 push in the same direction (the true production flag rate is higher
   than 10.1%, not lower), which matters directly for §7.
3. **93% "unrelated" swamps the finding.** Bucket E is excluded from the
   headline by the task's own design, but it is the actual modal outcome
   (93.4% of kept claims). That population is not idle — it is the
   textbook's interpretive commentary, holdings, and worked hypotheticals,
   which a production grounding gate would see cited to case-law or
   secondary sources this measurement did not include. The 79-row ABCD
   population this report analyzes is a small, non-random slice of the
   corpus's claims (the ones that happen to restate the bare statute), and
   generalizing from it to "how often do writers paraphrase" is exactly the
   genre-bias risk in #1 restated at the population level.
4. **The 0.60/0.50/0.70 cutoff is a judgment boundary on an already-tiny
   population** (§3): with only 2 rows total sitting in the sensitive band,
   the reported "stability" of 10.1% is a statement about this corpus
   having almost no borderline cases, not evidence that the gate's behavior
   is robust to the cutoff choice in general.
5. **Decomposition-artifact contamination (new finding, not anticipated by
   the task spec).** §5 shows the small ABCD population itself is diluted
   by non-claims that survived `classify()`'s NON_CLAIM filter (a `##`
   Markdown header, question-mark fragments, conjunction-split remnants).
   This is a **Case Resolution** observation, not a Systemic Fix executed
   here (out of this task's read-only scope) — flagged as an open item
   below per the project's Case-vs-Systemic discipline.

## 7. What this implies for T3 urgency

The number argues for **deferring** T3 on the strength of *this specific
corpus* (10.1% flag rate on already-thin evidence, mostly artifacts) while
simultaneously arguing that **this corpus cannot answer the question T3 was
proposed to fix.** The gate's real workload is AI-drafted prose grounded
against a handful of retrieved web/API sources — a genre with none of this
corpus's built-in quoting discipline and a real (not whole-corpus) source
scope, and per threat #2 above both of those differences push toward a
*higher* production flag rate than the 10.1% measured here, not a lower
one. A number this favorable, resting on a bias-corrected direction that
points the other way, is not evidence that T3 is unnecessary — it is
evidence that the right next measurement is the SAME procedure run against
a corpus that actually represents the gate's production input: AI-drafted
research or report prose grounded against its own real, narrow citations
(not a genre-matched whole-corpus proxy). Until that measurement exists,
the honest position is that T3 urgency is **undetermined by this probe**,
and the single highest-leverage follow-up is repeating §1's method on such
a corpus rather than re-running this one at a different tau.

## Open items (not actioned — read-only task)

- `classify()`'s `_is_non_claim` should catch `## QUESTION 2 — Fine.` as a
  Markdown header but the sample above shows it did not — worth a follow-up
  ticket against the header regex, verified against a live example rather
  than assumed from the regex text.
- The bare-citation short-claim artifact (`(Section 47)` etc.) inflating
  bucket A is a `decompose()`/conjunction-split interaction, not a gate
  scoring issue — separate follow-up, not this task's scope.
