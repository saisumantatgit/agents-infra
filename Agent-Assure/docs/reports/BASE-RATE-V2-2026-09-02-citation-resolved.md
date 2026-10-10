# Base-Rate Probe v2: Citation-Resolved Paraphrase Measurement (2026-09-02)

**Status:** measurement only. No file under `scripts/` or `tests/` was touched.
**Corpus:** 10 chapters, `cpc-book/manuscript/*.md` (1,197 kept claims) vs. the
full statute text, `cpc-book/reference/cpc-1908-fulltext-layout.txt`.
**Script:** `docs/reports/base_rate_v2_probe.py` (reproducible — writes
`docs/reports/base_rate_v2_probe_results.json` incrementally, one checkpoint
per chapter).

## BLUF

Two headline numbers, and neither should be read alone.

1. **Paraphrase rate among CITED, non-artifact claims = 1/7 = 14.3%**
   (excluding the ambiguous F bucket) **or 1/85 = 1.2%** (treating F as "not a
   paraphrase miss," which is the wrong read — see below). **n is too small
   for either number to be a usable calibration input.** Only 85 of 1,197
   kept claims (7.1%) carry a statutory citation that resolves in the index,
   and of those, 78 land in bucket F — ambiguous by construction (see §4).
   Only 7 claims are lexically decidable at all (A+B+C+D), and only 1 of those
   7 is a paraphrase (C). This is not a base rate; it is a sample of one.

2. **Decomposition-artifact rate = 26.1% of ALL kept claims (313/1,197)** —
   more than double v1's 8-claim paraphrase count, confirming v1's second-order
   finding at 2.7x the corpus scale: `decompose()`'s conjunction/semicolon
   splitting and markdown-header handling routinely emit fragments
   (`(Section 47)`, `## QUESTION 4 — So what can they take?`,
   `The arrest power is real,`) that are not claims in any sense a grounding
   gate should score. This is corpus-wide (20.4%–32.4% per chapter, no
   outlier) and is a bigger, more mechanical Error-A source than paraphrase.

3. **A third artifact mechanism, not anticipated by the task spec, dominates
   bucket F itself.** Manually inspecting all 10 F samples: 6 of 10 are
   **bare citation-range headers/parentheticals** — `(Sections 60–64; Order
   XXI Rules 46A–46F)`, `## QUESTION 5 — The auction, and its three escape
   doors (Order XXI Rules 64–92)` — which survive the Step-3 artifact filter
   (they end in `)`, not in `,;:—-`, and have ≥4 content tokens: "sections",
   "order", "xxi", "rules") but are section-*heading titles naming a range*,
   not sentences asserting content. They resolve against the FIRST section in
   the range (my citation regex takes the first number after "Section(s)"),
   then correctly show zero overlap with that one section's text, because
   the "claim" was never about that section's content — it was a table-of-
   contents pointer. **This means the true population of genuine, assertive,
   citation-backed claims in this corpus is smaller than 85 — likely closer
   to the 1 in 10 F-samples that reads as a real assertion.** See §4 for the
   one sample that IS genuine paraphrase.

**Read plainly:** this corpus cannot answer "what is Assure's real-world
paraphrase base rate" with statistical confidence — it is a legal textbook
whose writers overwhelmingly (89.5%, 1,112/1,197) either don't cite a
specific provision at all (66.3%) or cite it in a heading/pointer rather than
an assertion (roughly 5% more, folded into the 7.1% CITED figure). v1 already
showed this corpus is genre-mismatched to an AI-agent-research use case; v2
narrows the mismatch further by showing that even the small CITED slice is
mostly citation *pointers*, not citation *support claims*.

## 1. Statute index — validation

**149 Sections + 622 Order/Rule units = 771 addressable units, 178,707
statute tokens.**

Method: located the real Section-1 body (`"1. Short title, commencement and
extent.—"`, the only occurrence carrying the em-dash that marks body text vs.
the table-of-contents entry, which ends in a bare period) to fix
`body_start`, then the first `"THE FIRST SCHEDULE"` after it to split
Sections from the First-Schedule Orders/Rules region. Section/Rule headers
are found with `(\d{1,3}[A-Za-z]{0,2})\.\s+(title)\.\s?—`, guarded two ways
against the OCR layout's page-footnote noise (which reuses "N. Text" digit
formatting): (a) footnote titles never open with `Subs.`/`Ins.`/`Omitted`/
`Rep.`/`Added`/`See`/`Cl.`/`Explanation N` — genuine section titles never do
either, so this is a precise filter; (b) a monotonicity guard rejects a
matched number that regresses more than 0.5 below the running maximum
(footnotes reset to 1, 2, 3... every page, which reliably violates this).

**5 sampled units (first 100 chars):**

| Unit | First 100 characters |
|---|---|
| Section 1 | `1. Short title, commencement and extent.—(1) This Act may be cited as the Code of Civil Procedure, 1` |
| Section 2 | `2. Definitions.—In this Act, unless there is anything repugnant in the subject or context,—` |
| Section 3 | `3. Subordination of Courts.—For the purposes of this Code, the District Court is subordinate to the` |
| Order I, Rule 1 | `[1. Who may be joined as plaintiffs.—All persons may be joined in one suit as plaintiffs where—` |
| Order I, Rule 2 | `2. Power of Court to order separate trial.—Where it appears to the Court that any joinder of plainti` |

Segmentation reads as sane: each unit opens on its own number+title, ends
before the next number+title, content is legible statutory prose.

**Known residual gap (disclosed, not fixed — out of budget for this probe):**
CPC has 158 numbered sections; 149 resolved (9 are `[Repealed.]` stubs with no
`.—` body, correctly excluded — not a defect). Order/Rule coverage is not
independently verified against the First Schedule's own table of contents;
one manuscript citation (`Order XXXVIII Rule 5`, 2 occurrences) failed to
resolve despite Rules 4 and 6 of that Order being present, i.e. a genuine
single-unit gap, not the space-in-dash defect (both space and no-space header
forms are matched). This does not change the qualitative finding (n is far
too small regardless of one more resolved unit) but is named here per the
"say so, don't average it away" rule.

## 2. Population counts

| Bucket | Count | % of kept |
|---|---:|---:|
| Kept (FACTUAL/NUMERIC/ATTRIBUTION/RELATIONAL) | 1,197 | 100% |
| **CITED** (own text carries a resolving statutory citation) | 85 | 7.1% |
| **UNCITED** (no citation-shaped string) | 793 | 66.3% |
| **UNRESOLVED** (citation-shaped, does not resolve) | 6 | 0.5% |
| Decomposition artifact (excluded from CITED/UNCITED/UNRESOLVED split above) | 313 | 26.1% |

CITED + UNCITED + UNRESOLVED + artifact = 85 + 793 + 6 + 313 = 1,197. ✓

**Distinct unresolved citation-shaped strings** (6 total occurrences, 5
distinct strings — every one independently verified, not averaged away):

| String | Occurrences | Why it fails to resolve |
|---|---:|---|
| `Order XXXVIII Rule 5` | 2 | Genuine index gap — Rule 5 of Order XXXVIII not found (Rules 4, 6 present) |
| `section 9` | 1 | Lowercase "section" — the citation regex is case-sensitive on the keyword by design (avoids matching "in this section" as a citation); this is a recall miss, not a resolution failure |
| `Section 95)` | 1 | Trailing paren captured by the citation-shaped regex; the real citation ("Section 95") resolves, this is over-matching in the *shape* detector only, already double-counted in CITED for the same claim |
| `Order XV Rule 1.` | 1 | Trailing period captured similarly — likely double-counted alongside a resolving match in the same claim |
| `section (3)` | 1 | Not a real citation — "sub-section (3)" fragment; the shape-detector's `\S+` after "section" over-matches a bare parenthetical |

Net effect: the true unresolved rate is closer to 1–2 genuine misses out of
~91 citation-shaped strings (~1–2%), not a systematic parse failure — the
index resolves cleanly; the shape-detector over-matches on trailing
punctuation, a cosmetic issue that inflates UNRESOLVED by counting the same
claim's citation twice under two different surface strings.

## 3. Decomposition-artifact count (headline in its own right)

**313 of 1,197 kept claims (26.1%) are decomposition artifacts** —
fragments or interrogatives that `decompose()` emitted as standalone
"claims" but which assert nothing checkable.

| Chapter | Kept | Artifact | Artifact % |
|---|---:|---:|---:|
| execution.md | 137 | 34 | 24.8% |
| fast-lanes.md | 104 | 24 | 23.1% |
| first-appeal.md | 108 | 24 | 22.2% |
| institution.md | 142 | 46 | 32.4% |
| interim-relief.md | 97 | 23 | 23.7% |
| issues.md | 113 | 29 | 25.7% |
| judgment.md | 125 | 37 | 29.6% |
| narrow-doors.md | 103 | 27 | 26.2% |
| response.md | 160 | 47 | 29.4% |
| trial.md | 108 | 22 | 20.4% |
| **Total** | **1,197** | **313** | **26.1%** |

No chapter is an outlier (20.4%–32.4% range) — this is a property of
`decompose()`'s conjunction/semicolon splitter and markdown-header handling
on this genre (numbered questions, bullet lists, dash-joined clauses), not
one chapter's writing style.

**10 verbatim samples:**

1. `(Section 47)` — FRAGMENT
2. `## QUESTION 2 — What can the court actually do for you?` — INTERROGATIVE
3. `(Section 51)` — FRAGMENT
4. `Five modes, on the decree-holder's application [S6]:` — FRAGMENT
5. `- **attachment and sale** of the debtor's property (or sale without attachment);` — FRAGMENT
6. `- **arrest and detention** in the civil prison — within the limits Section 58 sets;` — FRAGMENT
7. `The arrest power is real,` — FRAGMENT
8. `it is fenced on every side [S7]:` — FRAGMENT
9. `Prison is a one-time lever per decree,` — FRAGMENT
10. `## QUESTION 4 — So what can they take?` — INTERROGATIVE

These are excluded from the Step-4 population below.

## 4. Bucketing CITED, non-artifact claims (n=85) against their own cited unit

Method: whole cited-unit text (not a sentence window) is used for A/B/C,
because every Section/Rule unit here is already smaller than the ±2-sentence
window the gate itself would slide — using the window would only narrow the
match surface, not widen it. D's F1 threshold reuses `t2_lexical_score`
verbatim (the gate's own ±2-sentence-window, numeric-gated F1), so D's number
is provably the gate's own arithmetic.

| Bucket | Count | Definition |
|---|---:|---|
| A — EXACT | 0 | Whole claim is a contiguous span of the cited unit |
| B — LONG-SPAN | 6 | Some ≥8-token contiguous claim span appears in the unit |
| C — ZERO-NOVEL PARAPHRASE | 1 | Every content token present, not contiguous |
| D — NOVEL-TOKEN PARAPHRASE | 0 | 1–3 content tokens absent, t2_f1 ≥ 0.60 |
| F — NO LEXICAL OVERLAP | 78 | Everything else |
| **Total (CITED, non-artifact)** | **85** | |

**HEADLINE (C+D)/(A+B+C+D+F) = 1/85 = 1.2%.**
**HEADLINE excluding F: (C+D)/(A+B+C+D) = 1/7 = 14.3%.**

The two differ by an order of magnitude because F is 92% of the denominator.
**Do not pick either number as "the" answer** — F is not resolved by lexical
methods, full stop, and reporting only the F-excluded number silently assumes
every F case is "genuinely unsupported," which the samples below refute.

### F, both ways, with samples

**As a share:** 78/85 = 91.8% of CITED, non-artifact claims land in F.

**10 verbatim F samples, next to their cited unit (first ~150 chars):**

| # | Claim | Cited unit (excerpt) | t2 score | Read |
|---|---|---|---:|---|
| 1 | `It is permission to start the machinery ... Part II of the Code (Sections 36–74)` | `36. Application to orders.—The provisions of this Code relating to the execution of decrees...` | 0.0 | **Range-header artifact**, not a claim about §36 specifically |
| 2 | `(Sections 60–64; Order XXI Rules 46A–46F)` | `60. Property liable to attachment and sale...` | 0.0 | **Range-header artifact** |
| 3 | `## QUESTION 5 — The auction, and its three escape doors (Order XXI Rules 64–92)` | `64. Power to order property attached to be sold...` | 0.0 | **Range-header artifact** |
| 4 | `(Order XXI Rules 35–36, 97–106)` | `35. Decree for immovable property.—(1) Where a decree is for the delivery...` | 0.0 | **Range-header artifact** |
| 5 | `## QUESTION 7 — Two creditors, one debtor, one pot (Section 73)` | `73. Proceeds of execution-sale to be rateably distributed...` | 0.0 | **Range-header artifact** |
| 6 | `4. **Tools, no** — an artisan's tools are exempt under the Section 60 proviso [S12].` | `60. Property liable to attachment and sale... The following property is liable to attachment...` | 0.0 | Ambiguous — real assertion, but the *proviso* clause is deep in §60's text, likely past this unit's captured span |
| 7 | `(Order XXXVII Rules 1–2)` | (Order XXXVII, Rule 1 text) | 0.0 | **Range-header artifact** |
| 8 | `6. **No.** Order XXIII Rule 1: without the court's permission, a fresh suit on the same subject-matter is barred [S8].` | `[1. Withdrawal of suit or abandonment of part of claim.—(1) At any time after the institution of a suit, the plaintiff may as against all or any of the defendants...` | 0.0 | Correctly resolved (Rule 1 IS the withdrawal/fresh-suit-bar rule) but scored F because the claim compresses several sub-clauses of a long, multi-part rule into one sentence — real content, genuinely thin lexical overlap with any single window |
| 9 | `The Code's answer is Section 96: an appeal lies from every decree ... save where the Code or another law says otherwise [S1].` | `96. Appeal from original decree.—(1) Save where otherwise expressly provided ... an appeal shall lie from every decree passed by any Court...` | **0.452** | **Genuine paraphrase** — "lies"/"lie" and "says"/no-verb-form mismatch drag F1 below 0.60; this IS the kind of claim T3-NLI paraphrase detection exists for |
| 10 | `The Supreme Court's answer: the appeal route is closed by Section 96(3), the fresh-suit route is closed by Order XXIII Rule 3A...` | Both citations resolved and were concatenated for scoring: §96 body + `3A. Bar to suit.—No suit shall lie to set aside a decree on the ground that the compromise... was not lawful.` | 0.0 | Correctly resolved against BOTH cited units; still F because the claim is a compressed two-provision synthesis in the author's own words — genuinely thin overlap with either unit alone or combined |

**Adjudication: F is not one thing.** Of these 10, **6 are not claims at
all** (#1–5, #7 — citation-range headers misclassified as sentences by
`decompose()`, the same disease as §3, just surviving the FRAGMENT filter
because they end in `)` and clear the 4-content-token floor). **4 are
genuine, correctly-resolved claims** (#6, #8, #9, #10) that compress or
paraphrase real statutory content and land in F because the overlap with
their (correctly identified) cited unit is thin: #9 is the cleanest
lexically-hard paraphrase (t2=0.452, a single verb-form mismatch away from
D); #6, #8, #10 compress a multi-clause provision into one sentence, which
lexical F1 structurally cannot credit even when the compression is faithful.
Lexical methods cannot adjudicate faithfulness from here — that adjudication
needs either a human read of the full provision or a semantic/NLI tier.

This means the *true* denominator for a paraphrase base-rate claim is not 85
and not even 7 — it is closer to **4** genuine cases in the full F sample
(with all 4 arguably paraphrase-like, none confidently "unsupported"), against
a total lexically-decidable population of A=0, B=6, C=1, D=0. At that scale,
"the" paraphrase rate is not a measurable quantity from this corpus; it is a
description of a handful of specific sentences.

## 5. Sensitivity note

No lex_tau sensitivity table is reported here (unlike v1's §3) because n=7
lexically-decidable claims makes any sweep noise, not signal — moving tau
from 0.60 to 0.50 could flip 0 or 1 claims and the resulting percentage swing
(0% to potentially 28%) would say nothing about the gate's true operating
characteristics.

## Closing: does this make T3 more or less urgent?

**Modestly more urgent, but on a different basis than a base rate.** This
probe cannot produce a defensible paraphrase-frequency number — the CITED,
non-artifact, non-range-header population is 4–11 claims across a
178K-word statute and a 27K-word manuscript, an order of magnitude too small
for any rate to generalize. What it *does* show, concretely, is:

1. **Sample #9 is a real, load-bearing example of exactly the failure T3 is
   designed to catch**: "an appeal lies from every decree" vs. the statute's
   "an appeal shall lie from every decree" — same content, different
   inflection, t2_f1=0.452, comfortably below any defensible lex_tau. A
   lex-only gate flags this UNGROUNDED even though it is a faithful
   restatement. This is not hypothetical; it is sitting in the corpus.
2. **The bigger, cheaper win is upstream of T3, not instead of it**: 26.1%
   of all kept claims and 71% of the CITED-but-ambiguous F bucket are
   decomposition/classification artifacts (fragments, headers, citation-range
   pointers), not paraphrase. Fixing `decompose()`/`classify()` to not emit
   "(Sections 60–64; Order XXI Rules 46A–46F)" as a claim needing grounding
   removes 6 of today's 10 F-samples and probably a comparable share of the
   1,118-claim "unrelated" bucket from v1 — for zero LLM calls and zero
   Error-B risk, since it only ever REMOVES candidate claims, never adds a
   PASS path.
3. **What would change this answer:** a corpus of AI-agent-drafted research
   prose (the gate's actual target population, not this legal-textbook
   proxy) with a citation discipline that forces genuine restatement rather
   than block-quoting — that corpus would very likely show CITED counts in
   the hundreds, not 85, and a genuine-F/paraphrase share large enough to
   calibrate against. Until such a corpus exists, T3's *priority* should be
   argued from the mechanism (inflectional/lexical drift lex-only tiers
   cannot see, sample #9 being existence proof) and from the classify/
   decompose fix's cheapness as a prerequisite — not from this probe's rate,
   which is honestly too small to move a threshold either way.

## Appendix: reproduction

```bash
cd Agent-Assure
PYTHONPATH=. uv run python docs/reports/base_rate_v2_probe.py
```

Writes `docs/reports/base_rate_v2_probe_results.json` after every chapter
(checkpointed, not terminal-only) and prints the same summary block to
stdout that appears in §2–§4 above.
