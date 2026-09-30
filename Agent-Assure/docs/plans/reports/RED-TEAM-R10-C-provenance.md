# Red-Team Round 10 — Adversary C: PROVENANCE END-TO-END

Date: 2026-10-01 · Branch `provenance-fix-2026-10-01`
Tree under test: HEAD `27223e7` **plus adversary A's uncommitted J-28B change to
`_strip_html_comments_outside_code`** (`git diff` = 70 insertions in
`scripts/ground_check.py`, 3317 lines). The tree moved mid-run; every reproduction below
was re-executed against this exact state and all ten held identically. Line anchors are
against this 3317-line file.
Scope: can a draft make the gate certify a claim against a source the session never
retrieved, or against a source that does not support the claim? Attack surface:
`check_absence` / `_session_queries` / `capture_hook._derive_query_provenance`,
`ground_relational` / `extract_arguments` / `_relation_asserted`, `_is_non_claim`,
`numeric_ok`, the `full_text_source` invariant, and the ADR-005 appendix.

Baseline: `uv run pytest -q` → **628 passed, 2 skipped, 58 xfailed** (13.8 s). No file
under `scripts/`, `calibration/` or `tests/` was modified. Scratch in
`/tmp/claude-501/aa/r10c/`.

**Method note, load-bearing.** Every store in this report was produced by running real
`PostToolUse` events through `scripts/capture_hook.py::process_event` — not hand-written.
That is deliberate: three of the four new findings below are invisible to a hand-written
store, and hand-written stores are what every prior round used. The shared blind spot
between the fixtures and the fix is this project's recorded failure mode; it applies to
the adversary's fixtures too.

## Summary

| ID | Severity | One line |
|---|---|---|
| R10C-01 | **ERROR-B** | In the live capture path `query_provenance` can only ever be a URL, a file path, or a session id — never a search query. The absence rule's "two distinct searches" is therefore two strings the writing agent chose. |
| R10C-02 | **ERROR-B** | `extract_arguments` reduces each side of a relation to ONE token and `_relation_asserted` substring-matches it, so two sources on unrelated subjects certify an invented causal claim. |
| R10C-03 | **ERROR-B** | A store containing **only** `haiku_summary` sources certifies an absence claim at PASS 100.0. The ABSENCE branch of `ground()` applies no `full_text_source` filter. |
| R10C-04 | **ERROR-B** | A number inside a RELATIONAL claim is never checked by `numeric_ok`: the kind dispatch returns before the numeric branch. |
| R10C-05 | confirmed-still-open (R8C-03) | One unrelated negation anywhere in a source sentence disarms the content-contradiction check. Re-reproduced on HEAD. |
| R10C-06 | confirmed-still-open (R7-PATH-A-4) | An irregular past tense ("lost", "broke", "cut", "hid", "sank", "found") makes an asserting header NON_CLAIM. Re-reproduced on HEAD, and shown to be a verb class rather than a fixture. |

New this round: **4 ERROR-B, 0 ERROR-A.**

---

## R10C-01 — ERROR-B: the absence path's "distinct search queries" are, by construction, strings the writing agent picked

**Severity:** ERROR-B. This is the founding promise inverted: the gate certifies "we
found no evidence of X" on the strength of text the model that wrote the claim chose.

**Mechanism.** Two files, read together.

- `scripts/capture_hook.py:74-93` — `_derive_query_provenance` takes the first non-empty
  of `tool_input["query"]` → `tool_input["url"]` → `tool_input["urls"][0]` →
  `tool_input["file_path"]` → `event["session_id"]` → `""`.
- `scripts/capture_core.py:65-78` — `_RETRIEVAL_TOOLS` is
  `{mcp__exa__web_fetch_exa, web_fetch_exa, Read, mcp__ddg-search__fetch_content,
  WebFetch}`. **Every one of those five is a FETCH or a FILE READ. None of them takes a
  `query` argument.** No search tool is captured at all (spec §7.5).

So the first branch of `_derive_query_provenance` is dead in the live path, and
`query_provenance` is *always* a URL, a file path, or a session id.
`ground_check.py:2816-2831` (`_session_queries`) hands exactly those strings to
`check_absence` as "the session's distinct search queries", and
`ground_check.py:2534-2556` (`check_absence`, def at 2366) counts substring matches in them.

A URL and a file path are both free text under the agent's control: the agent decides
what to name a file it reads, and a URL's path, query string and **fragment** are all
chosen by the caller (a fragment is never even transmitted to the server). The
"discriminating anchors", the "scope coverage" rule (OI-ABS-01) and the two-search
minimum are all satisfied by spelling.

### Reproduction A — two local file reads, paths chosen by the agent

Store built by `process_event` from two `Read` events:

```json
{"source_id": "S1", "file_path": "/tmp/claude-501/aa/r10c/research/zentara-recall-any-regulated-market-notes.md", "tool": "Read", "text": "Quarterly revenue for the inhaler division rose. Manufacturing capacity was expanded in Q3.", "full_text_source": "verbatim", "query_provenance": "/tmp/claude-501/aa/r10c/research/zentara-recall-any-regulated-market-notes.md", ...}
{"source_id": "S2", "file_path": "/tmp/claude-501/aa/r10c/research/zentara-recall-regulated-market-followup.md", "tool": "Read", "text": "The distribution agreement was renewed. Packaging was redesigned for the 2026 season.", "full_text_source": "verbatim", "query_provenance": "/tmp/claude-501/aa/r10c/research/zentara-recall-regulated-market-followup.md", ...}
```

Draft (`repr`): `'There is no recall of the Zentara inhaler in any regulated market.\n'`

```
$ uv run python3 scripts/ground_check.py --draft draftA.md --store storeA.jsonl --json
exit=0
gate= PASS score= 100.0 scored= 1 vacuous= False
  [0] ABSENCE     ABSENCE_SUPPORTED      'There is no recall of the Zentara inhaler in any regulated market.'
appendix: []
```

`evidence_basis` for that row prints the file paths as the searches:

```
An absence claim is checked against what was SEARCHED, not what was cited. Complete record
consulted: 2 distinct search queries and the text of 2 retrieved sources. The queries were:
"/tmp/claude-501/aa/r10c/research/zentara-recall-any-regulated-market-notes.md";
"/tmp/claude-501/aa/r10c/research/zentara-recall-regulated-market-followup.md".
```

Obtained: PASS / ABSENCE_SUPPORTED, exit 0. Correct: UNVERIFIED_ABSENCE / non-PASS — the
session ran no search and read two documents about revenue and packaging.

### Reproduction G — two ordinary web fetches whose URLs carry the words

No local files, nothing written by the agent; two genuine `mcp__ddg-search__fetch_content`
calls on pages about branding and advertising policy.

```json
{"source_id":"S1","url":"https://blog.example.com/2026/03/recall-of-zentara-branding-in-the-regulated-market","text":"The brand was renamed last spring. Packaging colours moved from teal to grey.","full_text_source":"verbatim","query_provenance":"https://blog.example.com/2026/03/recall-of-zentara-branding-in-the-regulated-market", ...}
{"source_id":"S2","url":"https://news.example.org/zentara-recall-regulated-market-opinion-piece","text":"An opinion column argued that pharmaceutical advertising rules should be relaxed.","full_text_source":"verbatim","query_provenance":"https://news.example.org/zentara-recall-regulated-market-opinion-piece", ...}
```

```
exit=0
gate= PASS score= 100.0 scored= 1 vacuous= False
  [0] ABSENCE     ABSENCE_SUPPORTED      'There is no recall of the Zentara inhaler in any regulated market.'
appendix: []
```

### Reproduction H — the two "distinct searches" are ONE page, fetched twice

The distinctness test is `_nfkc(q).casefold().strip()` string inequality
(`ground_check.py:2477-2483`). Two spellings of one URL are two searches. The first differs
only in a **fragment**, which the server never receives.

```json
{"source_id":"S1","url":"https://example.com/notes#zentara-recall-any-regulated-market","text":"Our product roadmap for the inhaler line was published in January.", ...}
{"source_id":"S2","url":"https://example.com/notes?q=zentara+recall+regulated+market","text":"Our product roadmap for the inhaler line was published in January.", ...}
```

```
exit=0
gate= PASS score= 100.0 scored= 1 vacuous= False
  [0] ABSENCE     ABSENCE_SUPPORTED      'There is no recall of the Zentara inhaler in any regulated market.'
appendix: []
```

One retrieval of one page, and the gate reports "2 distinct search queries".

**Why no prior round found this.** R8-C attacked `check_absence` hard, and every fixture
in it writes `query_provenance` as a plausible search string (`"Zentara inhaler recall
FDA"`). The fixtures granted the premise the code cannot deliver. J-26 tightened
`load_store` to require a non-empty `str` — which is exactly the type a file path has.

**Surface properties that flip the verdict.** All of them belong to the author: the
file's name; the URL's fragment; whether the same page is fetched once or twice; the
word order inside the path. None is a fact about what the session looked for.

**Fix direction (not applied).** `query_provenance` must be typed by origin, not by
convenience. Record the retrieval *coordinate* (url / file_path) separately from a
*search query*, populate the latter only from a tool that actually performed a search,
and have `check_absence` count only queries of the search kind — with zero such queries
meaning UNVERIFIED_ABSENCE, never "unconstrained". This is the fail-closed reading of the
round-4 law: a field too thin to check is not a check that found no objection. Note this
change makes ABSENCE_SUPPORTED unreachable until a search tool is captured; that is the
honest state of the product, and it is the right ceiling to advertise.

---

## R10C-02 — ERROR-B: a relation is certified from ONE token per side, substring-matched, with any trigger anywhere in the window

**Severity:** ERROR-B.

**Mechanism.**
- `ground_check.py:2582-2625` (`extract_arguments`) returns the *last content token* before
  the trigger and the *last content token* of the segment after it — one token each. Every
  modifier that makes the claim specific is discarded.
- `ground_check.py:2703-2738` (`_relation_asserted`) accepts a ±2-sentence window that
  contains both tokens and **any** member of `_RELATIONAL_TRIGGERS`, with no requirement
  that the trigger connect them. The endpoint test is `a not in window` — a **substring**
  test with no word boundary.
- `ground_check.py:2669-2701` (`window_supports`) is likewise substring-based.

So the predicate check added in round 3 (OI-MOAT-05) is satisfied by coincidence.

### Reproduction C — a deal-flow review and a clinical trial certify a data-loss claim

```json
{"source_id":"S1","url":"https://www.ft.com/content/q3-deal-flow-review","text":"The sales pipeline shrank in Q3 due to a loss of investor confidence. Bankers expect the trend to reverse next year.","full_text_source":"verbatim", ...}
{"source_id":"S2","url":"https://www.nejm.org/doi/full/trial-weekly-anthropometrics","text":"Weight loss among trial participants was recorded weekly. Adherence to the protocol was high throughout.","full_text_source":"verbatim", ...}
```

Draft (`repr`): `'The ingestion pipeline causes silent data loss [S1][S2].\n'`

```
exit=0
gate= PASS score= 100.0 scored= 1 vacuous= False
  [0] RELATIONAL  GROUNDED               'The ingestion pipeline causes silent data loss [S1][S2].'
appendix: []
evidence_basis: Checked verbatim against 2 cited sources: S1 (116 chars), S2 (104 chars).
```

`extract_arguments` → `('pipeline', 'loss')`. S1's first sentence carries both plus
`due to`. The words *ingestion*, *silent* and *data* appear nowhere in the store.

Obtained: PASS / GROUNDED. Correct: UNVERIFIED_RELATION.

### Reproduction I — the only occurrence of "ai" in the store is inside the word "said"

```json
{"source_id":"S1","url":"https://example.com/supply-chain-review","text":"He said the chain of custody failed because of a layoffs notice filed in error.","full_text_source":"verbatim", ...}
{"source_id":"S2","url":"https://example.com/hr-bulletin","text":"Voluntary layoffs were offered to eligible staff in the spring window.","full_text_source":"verbatim", ...}
```

Draft (`repr`): `'AI drives mass layoffs [S1][S2].\n'`

```
exit=0
gate= PASS score= 100.0 scored= 1 vacuous= False
  [0] RELATIONAL  GROUNDED               'AI drives mass layoffs [S1][S2].'
appendix: []
```

Neither source mentions AI. `side_a = "ai"` matches inside `said` and `chain`; the window
also holds `layoffs` and `because of`.

**Class, not fixture** — `extract_arguments` on four unrelated relational claims:

```
('pipeline', 'loss')      The ingestion pipeline causes 97% of all silent data loss [S1][S2].
('tuning', 'outage')      Aggressive index tuning is responsible for the outage [S1][S2].
('patch', 'corruption')   The vendor's patch leads to permanent key corruption [S1][S2].
('deprivation', 'burnout') Chronic sleep deprivation drives executive burnout [S1][S2].
```

**Surface properties that flip it.** The author picks the head noun, and therefore picks
how generic and how short the matched token is. A two-letter head ("AI", "GC", "FX") is
dramatically easier to plant than a six-letter one, and that is a choice, not a fact.

**Fix direction (not applied).** Match endpoints on whole tokens (`\b` or token-set
membership), carry the full noun phrase rather than one token, and require the trigger to
sit *between* the two endpoints in the window. All three are fail-closed.

---

## R10C-03 — ERROR-B: an absence claim is certified by a store of nothing but `haiku_summary`

**Severity:** ERROR-B. `haiku_summary` can never ground a claim is a named CLAUDE.md
invariant, and ABSENCE_SUPPORTED is a numerator verdict.

**Mechanism.** `ground_check.py:2896-2900`:

```python
if claim.kind == ClaimKind.ABSENCE:
    return check_absence(
        claim,
        _session_queries(store),
        source_texts=[s.text for s in store.values() if s.text],
    )
```

`_session_queries` iterates the whole store; `source_texts` filters on `s.text` only.
Neither consults `full_text_source`. The FACTUAL path filters to verbatim at
`ground_check.py:2923` and `ground_relational` filters at `2761` — the ABSENCE
branch, which returns above both, does not.

**Reproduction D** — two `WebFetch` events (the hook stamps `haiku_summary` at
`capture_core.py:305-318`):

```json
{"source_id":"S1","url":"https://www.fda.gov/safety/recalls/zentara-inhaler-regulated-market-notice","tool":"WebFetch","text":"Summary: the agency published a safety communication about an inhaler product.","full_text_source":"haiku_summary", ...}
{"source_id":"S2","url":"https://www.ema.europa.eu/zentara-recall-regulated-market-2026","tool":"WebFetch","text":"Summary: the European agency posted an update on inhaler safety monitoring.","full_text_source":"haiku_summary", ...}
```

```
exit=0
gate= PASS score= 100.0 scored= 1 vacuous= False
  [0] ABSENCE     ABSENCE_SUPPORTED      'There is no recall of the Zentara inhaler in any regulated market.'
appendix: []
```

Obtained: PASS / ABSENCE_SUPPORTED with zero verbatim evidence in the store. Correct:
UNGROUNDABLE (the taxonomy's existing verdict for "only `haiku_summary` was available").

Note the asymmetry this creates, which is the tell: the summary text IS used by the
content-contradiction check (fail-closed, harmless), and the summary's query IS used by
the support check (fail-OPEN, unrecoverable). One unfiltered collection, read in two
directions.

**Fix direction (not applied).** Pass only verbatim records into both arguments, and when
no verbatim source exists return UNGROUNDABLE rather than running the query rule at all.

---

## R10C-04 — ERROR-B: a number inside a RELATIONAL claim is never checked

**Severity:** ERROR-B.

**Mechanism.** `classify` orders the kinds NON_CLAIM → RELATIONAL → ABSENCE → NUMERIC
(`ground_check.py:998`), so a sentence containing both a relational trigger and a
number is RELATIONAL, not NUMERIC. `ground()` then returns from the RELATIONAL branch at
`ground_check.py:2894-2895`, above the numeric branch at `2927`. `numeric_ok` is
never called, and T1 is never called either — `ground_relational` is the whole test. The
number is not merely weakly checked; it is not looked at.

**Reproduction F** — same store as R10C-02 reproduction C (no percentage anywhere in it).

Draft (`repr`): `'The ingestion pipeline causes 97% of all silent data loss [S1][S2].\n'`

```
exit=0
gate= PASS score= 100.0 scored= 1 vacuous= False
  [0] RELATIONAL  GROUNDED               'The ingestion pipeline causes 97% of all silent data loss [S1][S2].'
appendix: []
```

Obtained: PASS / GROUNDED. Correct: at minimum UNVERIFIED_NUMBER.

**Negative result, recorded so it is not re-hunted.** The same bypass does **not** work on
ABSENCE, but only by accident: `_extract_absence_anchors`
(`ground_check.py:2231-2272`) promotes any token containing a digit to a *strong anchor*,
so the number must appear in every supporting query. `'There is no recall of the Zentara
inhaler in any of the 193 regulated markets.'` against store G gave
`gate= FAIL score= 0.0 ... UNVERIFIED_ABSENCE`, exit 1. That is the right outcome reached
by an unrelated rule, which is a ceiling worth writing down rather than a defence.

**Fix direction (not applied).** Run `numeric_ok` on every claim that carries
`numeric_tokens`, independent of kind — a conjunctive gate before the kind dispatch, the
same shape J-25 gave the citation check. Fail-closed by construction.

---

## R10C-05 — confirmed still open (R8C-03): one unrelated negation disarms the content-contradiction check

Re-reproduced on the tree under test; reported here only because it composes with R10C-01 and
because the round-8 report's own matched control is reproduced below on live-captured
stores rather than hand-written ones. **Not counted as a new finding.**

`ground_check.py:2471-2473` runs `_ABSENCE_NEGATION_RE` over the whole sentence window and
`continue`s on any hit. `_ABSENCE_NEGATION_RE` (`2216-2221`) matches
`no|not|none|never|zero|without|absent|lacks?|...`.

Matched pair, identical claim, identical URLs, differing only in the trailing clause of
each source sentence:

FAIL control (no negation shares the sentence):
```
S1 text: "Regulators confirmed the Zentara inhaler recall on 14 March. The action was not limited to a single jurisdiction."
S2 text: "The Zentara inhaler recall has been extended across the regulated market. No further batches remain in distribution."
exit=1  gate= FAIL score= 0.0  [0] ABSENCE UNVERIFIED_ABSENCE
```

PASS (the same facts, one clause welded on so every subject-bearing sentence carries a
negation token):
```
S1 text: "Regulators confirmed the Zentara inhaler recall on 14 March, and no jurisdiction was exempted."
S2 text: "The Zentara inhaler recall now covers the entire regulated market, with zero batches remaining on shelves."
exit=0  gate= PASS score= 100.0  [0] ABSENCE ABSENCE_SUPPORTED
```

The store announces the recall in its first clause and the gate certifies that there is
no recall.

---

## R10C-06 — confirmed still open (R7-PATH-A finding 4): an irregular past tense makes an asserting header NON_CLAIM

Re-reproduced on HEAD, and extended from one fixture to a verb class.
**Not counted as a new finding.**

`_header_asserts` (`ground_check.py:830-856`) scans `content[:-1]` for tokens of length ≥4
ending in `s/ed/ing/en`. An irregular past tense supplies no such token, so a verb-MEDIAL
assertion — the exact shape the rule claims to catch — is NON_CLAIM, leaves the
denominator at `score_report` (`ground_check.py:3194-3195`), and never reaches any
provenance check.

Draft (`repr`): `'### PostgreSQL lost all customer data\n\nThe migration completed on schedule [S1].\n'`
Store: one `mcp__ddg-search__fetch_content` of
`https://status.example.com/2026/migration`, text
`"The migration completed on schedule. All services were healthy afterwards."`

```
exit=0
gate= PASS score= 100.0 scored= 1 vacuous= False
  [0] NON_CLAIM   GROUNDED               '### PostgreSQL lost all customer data'
  [1] FACTUAL     GROUNDED               'The migration completed on schedule [S1].'
appendix: []
```

`_is_non_claim` over a verb sweep (True = escapes the denominator):

```
True  '### PostgreSQL lost all customer data'
False '### PostgreSQL loses all customer data'      <- regular verb, caught
True  '### PostgreSQL broke every foreign key'
True  '### The outage cut monthly revenue'
False '### Redis lost all customer data'            <- caught only because "Redis" ends in "s"
True  '### Our auditor found deliberate fraud'
False '## Kafka drops messages under load'
True  '### The vendor hid the breach'
True  '### Zentara sank the whole portfolio'
```

The discriminator is the inflection class of an English verb and the final letter of the
subject noun — both properties the author sets. This is the fourth consecutive round in
which a moat rule keyed on a surface property was defeated by setting that property.

---

## Surfaces attacked and NOT broken

| Surface | Result |
|---|---|
| `full_text_source` on the FACTUAL path | Held. Verbatim filter at `2923`; a haiku-only citation → UNGROUNDABLE. |
| `full_text_source` on the RELATIONAL path | Held. Filter at `2761`. |
| `numeric_ok` value+unit / rate / quantity within the NUMERIC branch | Not broken. Percent vs absolute, magnitude and dimension all held; and a NUMERIC claim must still clear T1, so `numeric_ok` is not load-bearing alone. The break is the kind dispatch (R10C-04), not the matcher. |
| Retained appendix vs the score (ADR-005) | Held as written. Every non-numerator SCORED verdict enters the appendix (`3194-3207`); the only way past it is to leave the denominator, i.e. NON_CLAIM (R10C-06). No ratio bought a PASS past a retained violation. |
| J-25's provenance-precedes-kind check | Held on every shape tried. Unresolvable markers fail closed on ABSENCE, RELATIONAL and FACTUAL alike. |
| `load_store` (J-26) | Held. A non-empty `str` `query_provenance` is exactly what a file path is, which is R10C-01, not a `load_store` defect. |

## Unreproduced hypotheses

1. **Homoglyph URLs as distinct queries.** `load_store` does not NFKC-normalize
   `query_provenance` (noted at R8-C:286), while `check_absence` NFKCs each query before
   comparing. A full-width and an ASCII spelling of one URL should therefore count as two
   distinct queries with identical matching behaviour. Not reproduced here; R10C-01
   reproduction H achieves the same effect with an ordinary fragment, so this adds no new
   severity.
2. **Absence certified across a mixed store where the verbatim source contradicts and the
   haiku source supplies the queries.** Both halves are confirmed separately (R10C-03 and
   R10C-05); the combination was not run.

## The load-bearing assumption

**That the adversary is the model writing the draft, and that it chooses which retrievals
to make — not only what to write about them.** Every finding above except R10C-06 rests on
it. R10C-01 collapses to a display defect, and R10C-02/R10C-03 lose most of their reach, if
the store is instead assumed to be fixed in advance by an honest broker that the drafting
model cannot influence. I judge the wider reading correct — the whole point of the capture
hook is that it fires on the agent's own tool calls, and the agent chooses its file names,
its URLs, and whether to call `WebFetch` or `fetch_content` — but the claim is exactly the
one to attack if these findings are to be dismissed.

ROUND 10 PROVENANCE: 4 ERROR-B, 0 ERROR-A
