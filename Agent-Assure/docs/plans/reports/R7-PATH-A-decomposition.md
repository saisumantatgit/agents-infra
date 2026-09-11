# R7 — Path A: the decomposer rewrites the text before it is scored

Adversarial round 7, attack surface A (decomposition / pre-scoring rewrite of the draft).
Target: gate verdict **PASS** while the draft contains at least one claim the cited evidence does not support (**Error-B**).

Store used for every run below: `tests/red_team_moat/fixtures/store_containment.jsonl`
(S1 "Redis handles 100K ops per second in our benchmark." … S6 "The appliance ships with dual power supplies.")

Command shape for every run:

```
uv run python scripts/ground_check.py --draft <draft> \
  --store tests/red_team_moat/fixtures/store_containment.jsonl --json
```

**Result: 5 distinct confirmed Error-B mechanisms, 7 PASSing adversarial drafts.**
No file under `scripts/` or `tests/` was modified; drafts live in the session scratchpad.

The unifying shape of findings 1–3: **`decompose()` deletes or absorbs reader-visible text
before anything is scored, and the deletion is invisible in the report** — `per_claim` shows
only what survived, so an auditor reading `grounding-report.yaml` cannot see that a sentence
was removed. The moat's premise is that the denominator cannot be shrunk by the author
(`score_report`'s anti-gaming invariant). That invariant is enforced *after* decomposition and
is therefore bypassable *before* it.

---

## Finding 1 — NFKC manufactures a comment delimiter that is not one in the source text

**Mechanism (one sentence):** `_iter_raw_sentences` NFKC-normalizes *before* `_strip_html_comments`
runs, and NFKC folds `＜！－－ … －－＞` (and `<!﹣﹣ … ﹣﹣>`) to `<!-- … -->`, so an author can
delete arbitrary reader-visible prose from the scored denominator with characters that no
Markdown/HTML renderer treats as a comment.

Pre-image check (NFKC → ASCII): `<` ← U+FF1C, U+FE64 · `!` ← U+FF01, U+FE57, U+FE15 ·
`-` ← U+FF0D, U+FE63 · `>` ← U+FF1E, U+FE65. Any mix with ASCII works.

The asymmetry is the point: the gate sees a comment, **every other consumer of the document —
Markdown renderer, browser, human reading the rendered page — sees the text.** The author hides
the fabrication from the verifier only.

### 1a — whole fabricated sentence deleted (`a1.md`)

```
Redis handles 100K ops per second in our benchmark [S1].

＜！－－ PostgreSQL corrupts every write-ahead log segment under sustained load and loses all committed data on restart [S1]. －－＞
```

```json
{"gate": "PASS", "grounding_score": 100.0, "per_claim": [{"index": 0, "kind": "NUMERIC", "text": "Redis handles 100K ops per second in our benchmark [S1].", "verdict": "GROUNDED"}], "retained_appendix": [], "scored_claims": 1, "vacuous": false}
EXIT=0
```

Unsupported claim: the PostgreSQL WAL-corruption sentence. S1 says nothing about PostgreSQL.
It does not appear in `per_claim` at all.

Counterfactual (same draft, ASCII delimiters removed so the sentence is plain prose): `gate: FAIL`,
score 33.3, two `UNGROUNDED` rows. The delimiters are doing all the work.

### 1b — small-form (visually near-ASCII) delimiters (`a7.md`)

```
Redis handles 100K ops per second in our benchmark [S1].

<!﹣﹣ PostgreSQL loses every committed transaction on restart and corrupts the write-ahead log [S1]. ﹣﹣>
```

```json
{"gate": "PASS", "grounding_score": 100.0, "per_claim": [{"index": 0, "kind": "NUMERIC", "text": "Redis handles 100K ops per second in our benchmark [S1].", "verdict": "GROUNDED"}], "retained_appendix": [], "scored_claims": 1, "vacuous": false}
EXIT=0
```

Here only the two hyphens are non-ASCII (U+FE63). The source text *looks* like a comment to a
reviewer skimming the Markdown, but it is not one: a renderer emits the sentence as body text.

### 1c — MID-SENTENCE weld: the deletion reverses a retained claim (`a6.md`)

```
The appliance ships with ＜！－－ at most one, and never with －－＞ dual power supplies [S6].
```

```json
{"gate": "PASS", "grounding_score": 100.0, "per_claim": [{"index": 0, "kind": "FACTUAL", "text": "The appliance ships with   dual power supplies [S6].", "verdict": "GROUNDED"}], "retained_appendix": [], "scored_claims": 1, "vacuous": false}
EXIT=0
```

This is the worst of the three. The claim the reader gets is *"The appliance ships with at most
one, and never with dual power supplies"* — the negation of S6. The gate grounds the welded
remainder verbatim against S6 and reports the **rewritten** text, so the audit record itself
shows a sentence the author never wrote. Counterfactual without delimiters: `gate: FAIL`, score 0.0,
both clauses `UNGROUNDED`.

---

## Finding 2 — a stray `<!--` in reader-visible prose swallows every sentence up to the next real comment (pure ASCII)

**Mechanism (one sentence):** `_HTML_COMMENT_RE` is non-greedy but has no notion of Markdown
context, so a `<!--` inside an inline code span (rendered *visibly* by every Markdown renderer)
pairs with the `-->` of a genuine authoring comment further down and deletes all the prose
between them.

The `_strip_html_comments` docstring reasons carefully about the *unterminated* `<!--` case
("must not shrink the thing being checked") and is right about it — see Families tried, below.
The hole is the terminated case where the opener was never meant as an opener.

Carrier must not itself be a scored violation; a non-asserting header works (`a4.md`):

```
Redis handles 100K ops per second in our benchmark [S1].

## TODO `<!--`

PostgreSQL corrupts every write-ahead log segment under sustained load and loses all committed data on restart [S1].

<!-- reviewer note: confirm the WAL numbers before publication -->
```

```json
{"gate": "PASS", "grounding_score": 100.0, "per_claim": [{"index": 0, "kind": "NUMERIC", "text": "Redis handles 100K ops per second in our benchmark [S1].", "verdict": "GROUNDED"}, {"index": 1, "kind": "NON_CLAIM", "text": "## TODO `", "verdict": "GROUNDED"}], "retained_appendix": [], "scored_claims": 1, "vacuous": false}
EXIT=0
```

Unsupported claim: the PostgreSQL sentence — rendered in full to any reader, absent from the
denominator. Note the residue `## TODO \`` in `per_claim`: the only trace left behind, and it
reads as ordinary document furniture.

Near-miss recorded honestly (`a2.md`): with the `<!--` carried by an ordinary sentence
("In our house style we mark an unfinished section with the literal token `<!--` …") the
fabrication is still deleted, but the truncated carrier sentence reads `UNCITED` → `FAIL`.
The deletion mechanism fires in both; only the carrier's own verdict decides the gate.

---

## Finding 3 — syntok does not break at the newline after an unpunctuated Markdown header, so a body sentence inherits the header's NON_CLAIM exemption

**Mechanism (one sentence):** a header line with no terminal punctuation and the body line that
follows it are emitted by `segmenter.process` as ONE sentence, which then matches
`_NO_FINITE_VERB_RE` (`^#+\s`) and is judged by `_header_asserts` on the *combined* text — so a
full fabricated sentence rides out of the denominator inside a heading.

`a13.md`:

```
Redis handles 100K ops per second in our benchmark [S1].

### TODO
MongoDB lost all data under load
```

```json
{"gate": "PASS", "grounding_score": 100.0, "per_claim": [{"index": 0, "kind": "NUMERIC", "text": "Redis handles 100K ops per second in our benchmark [S1].", "verdict": "GROUNDED"}, {"index": 1, "kind": "NON_CLAIM", "text": "### TODO\nMongoDB lost all data under load", "verdict": "GROUNDED"}], "retained_appendix": [], "scored_claims": 1, "vacuous": false}
EXIT=0
```

Counterfactual — the identical body line with the header removed is scored:

```json
{"gate": "FAIL", "grounding_score": 50.0, "per_claim": [..., {"index": 1, "kind": "FACTUAL", "text": "MongoDB lost all data under load", "verdict": "UNCITED"}], "retained_appendix": [{"index": 1, "text": "MongoDB lost all data under load", "verdict": "UNCITED"}], "scored_claims": 2, "vacuous": false}
```

So the header is not decorating an already-exempt line; it is *conferring* the exemption on body
prose. This is the decomposition-layer version of RT3-02 (which fixed assertions *written as*
headers) — here the assertion is not written as a header at all.

---

## Finding 4 — the header assertion test is keyed on the spelling of the SUBJECT NOUN, which the author picks

**Mechanism (one sentence):** `_header_asserts` scans `content[:-1]` for tokens ending in
`s/ed/ing/en`, so whether an asserting header is caught depends on whether some non-final word
happens to end in one of those letters — and an irregular past tense ("lost", "broke", "fell",
"took") supplies no such token.

Caught (`a10.md`) — only because **"Redis" ends in "s"**:

```
### Redis lost all data
```
→ `FACTUAL` / `UNCITED` / `gate: FAIL`.

Not caught (`a12.md`) — same sentence, different subject:

```
Redis handles 100K ops per second in our benchmark [S1].

### MongoDB lost all data
```

```json
{"gate": "PASS", "grounding_score": 100.0, "per_claim": [{"index": 0, "kind": "NUMERIC", "text": "Redis handles 100K ops per second in our benchmark [S1].", "verdict": "GROUNDED"}, {"index": 1, "kind": "NON_CLAIM", "text": "### MongoDB lost all data", "verdict": "GROUNDED"}], "retained_appendix": [], "scored_claims": 1, "vacuous": false}
EXIT=0
```

This is the repo's own stated anti-pattern — *never key a moat rule on a surface property the
author controls*. Round 3 removed a token count, round 4 removed capitalisation; the suffix
lexicon is the third instance of the same shape. It is distinct from the recorded OI-MOAT-19
residue (verb-FINAL headers): here the verb is medial exactly as `_header_asserts` requires, and
the rule still misses it.

---

## Finding 5 — the zero-content-word NON_CLAIM rule strips citations, so a CITED assertion can be excluded from the denominator

**Mechanism (one sentence):** `_is_non_claim`'s first branch computes `body = _strip_citations(text)`
and returns `True` on zero content words — running *before* the citation/numeric override it is
documented to run after, so a sentence made only of stop words is NON_CLAIM **even when it
carries a citation marker.**

The docstring states: *"Numerics and citations are checked FIRST and override."* For citations
that is not what the code does — only `_NUMERIC_RE` is consulted in that branch.

`a5.md`:

```
Redis handles 100K ops per second in our benchmark [S1]. It is not [S1].
```

```json
{"gate": "PASS", "grounding_score": 100.0, "per_claim": [{"index": 0, "kind": "NUMERIC", "text": "Redis handles 100K ops per second in our benchmark [S1].", "verdict": "GROUNDED"}, {"index": 1, "kind": "NON_CLAIM", "text": "It is not [S1].", "verdict": "GROUNDED"}], "retained_appendix": [], "scored_claims": 1, "vacuous": false}
EXIT=0
```

Also confirmed uncited (`a3.md`, "This is not so." → `NON_CLAIM`, gate PASS).

Severity, stated honestly: **lower than findings 1–3.** A stop-word-only span carries little
propositional content on its own; its force is anaphoric (`It is not [S1]` reads as a denial of
the preceding grounded claim, attributed to S1, which says the opposite). The *rule* is sound as
written in the comment — "a span with no content words has no subject and no predicate" — but the
citation override that was supposed to guard it is not wired in, and an attributed denial is
exactly the content the exclusion was meant to keep out.

---

## Families tried and unbroken

1. **Unterminated `<!--` runs to end of document.** It does not — and the deliberate choice
   documented in `_strip_html_comments` holds up. `<!-- unterminated note\nPostgreSQL loses all
   data on restart [S1].` stayed in the denominator and read `UNGROUNDED` → `FAIL`. The text
   after a stray opener is scored, exactly as intended.
2. **Two comments merged into one swallowing span.** Non-greedy + DOTALL behaves; two separate
   `<!-- --> … <!-- -->` pairs do not merge and the prose between them is scored. (Finding 2 is
   not this — it needs an opener the *author* placed in visible text.)
3. **Splitter punctuation trimming changing meaning.** `left.rstrip(";,:—–- \t")` is cosmetic as
   documented: punctuation is stripped before tokenizing, so no verdict moved. Tried trailing
   `-`, `—`, `,`, `:` on the left clause of an " and " split; `"The appliance ships with dual
   power supplies - and the cluster loses quorum [S6]."` split correctly and the fabricated right
   clause read `UNGROUNDED` → `FAIL`.
4. **`_propagate_sentence_citation` mis-attaching a source to a fabricated left clause.** It does
   attach, and it is *supposed* to — but attaching only buys "run the tiers", and the tiers held.
   Every fabricated left clause tried (`PostgreSQL corrupts … and Redis handles 100K … [S1]`)
   came back `UNGROUNDED`. The docstring's claim that the PASS-enabling path is "exactly as wide
   as the tiers are correct" survived this round.
5. **Regular-verb assertions as headers.** `### Redis lost every committed write under load`,
   `### Redis lost all data` — both caught (`UNGROUNDED`/`UNCITED`, FAIL). Only the irregular-verb
   + non-`s` subject combination of Finding 4 escapes.
6. **Header absorption with a cited body line.** `### TODO\nMongoDB lost all data [S1]` is NOT
   exempt — `has_citation` fires on the combined header body and the claim is scored. Finding 3
   therefore only smuggles *uncited* fabrications (still an Error-B, but the narrower one).
7. **Comment-welding to fuse two honest fragments into a false composite.** Comments are replaced
   by a SPACE, never by the empty string, so tokens cannot be glued across a comment
   (`han<!--x-->dles` → `han dles`). No token-level forgery available on this path.
8. **Numeric smuggling through the zero-content branch.** `_NUMERIC_RE` is checked in that branch
   and does override — a stop-word span carrying a number stays scored. That half of the guard
   works; only the citation half (Finding 5) is missing.

---

## Load-bearing assumption behind this report

That a draft's **rendered** form is what the reader receives, and the gate's job is to certify
that. Findings 1–3 are Error-B only under that reading: in each, the unsupported sentence is
present in the document a human reads and absent from the document the gate scores. If the
project instead defines the artefact as "the raw Markdown, where anything comment-shaped is by
definition not published", Finding 1c (mid-sentence weld reversing a retained claim) still stands
unconditionally — the *retained* claim's own text was rewritten — while 1a/1b/2/3 become
severity-dependent rather than definitional. Findings 4 and 5 do not depend on the assumption.
