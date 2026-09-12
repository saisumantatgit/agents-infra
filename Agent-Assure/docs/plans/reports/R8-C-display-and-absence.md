# R8-C — Red team: `evidence_basis` display surface + the absence path

Date: 2026-09-12 · Target: `Agent-Assure/scripts/ground_check.py` (2902 lines, commit `67b179f`)
Scope: (1) `evidence_basis` (added 2026-09-12, OI-UX-01, never attacked); (2) `check_absence`,
`_extract_absence_anchors`, `_absence_scope_terms`, `_session_queries`, `_ABSENCE_NEGATION_RE`.

All reproductions were RUN. Scratch fixtures live in
`/private/tmp/claude-501/-Users-saisumanthbattepati-vibe-coding-Agents-agent-assure-calibration/d2b27b1f-f3bd-4dea-8c6a-e58508ad626d/scratchpad/r8c/`
and are reproduced inline below so the report stands alone. Every command is run from `Agent-Assure/`:

```
uv run python scripts/ground_check.py --draft D.md --store S.jsonl --json
```

Store rows below are abbreviated; every row in the actual fixtures carried the full key set
(`source_id, url, file_path, fetched_at, tool, content_sha256, text, full_text_source,
captured_via, query_provenance`), with `full_text_source: "verbatim"` unless stated.

## Summary

| id | severity | one-line mechanism |
|---|---|---|
| R8C-01 | **ERROR-B** | An ADVERBIAL scope (`worldwide`) is invisible to `_absence_scope_terms`, which only reads prepositional phrases — two FDA-only searches certify a worldwide absence at 100.0 / PASS. |
| R8C-02 | **ERROR-B** | `_absence_scope_terms` takes the LAST scope preposition, so appending a narrow trailing PP (`…in FDA filings`) shadows the broad scope the claim actually asserts. |
| R8C-03 | **ERROR-B** | The contradiction check skips any source window containing ANY negation token, so a source that ANNOUNCES the recall escapes refutation if the same sentence carries an unrelated "not". |
| R8C-04 | lying-display | `query_provenance` is interpolated raw into the basis prose; a query string can impersonate the gate's own voice ("the gate verified this claim against 4 corroborating sources"). |
| R8C-05 | lying-display | Duplicate citations are counted as distinct sources — `[S1][S1]` renders "Checked verbatim against 2 cited sources", and on a RELATIONAL claim it asserts 2 sources in the very report whose verdict exists *because* there was only 1. |
| R8C-06 | lying-display | "Complete record consulted: N distinct search queries" uses `_session_queries` (raw-string distinct, unfiltered) while the verdict used a DIFFERENT set (NFKC+casefold distinct, non-empty, scope-filtered). Three demonstrated divergences. |
| R8C-07 | lying-display | "…and the text of N retrieved sources" is asserted on a path where `check_absence` returns before reading a single source text. |
| R8C-08 | lying-display | "…so nothing exists to check the claim against" is emitted when a cited source WAS retrieved, holds text, and (for RELATIONAL) was actually consulted. |
| R8C-09 | lying-display | An empty `query_provenance` is rendered as `""` and counted — the literal "absence rendered as a blank/internal token" defect OI-UX-01 was written to close. |
| R8C-10 | robustness | Store-controlled strings enter the basis with no length cap and no control-character sanitisation (ANSI clear-screen + colour sequences survive into the human-facing sentence; a 50 KB `source_id` yields a 50 KB basis). |
| R8C-11 | lying-display (structural root cause) | `evidence_basis` has NO `RELATIONAL` branch, so its documented contract "branch order mirrors `ground()`'s exactly" is false; every RELATIONAL claim is described by a branch the verdict did not take. Root cause of R8C-05 (acute form) and R8C-08. |

ERROR-B findings: **3**. Lying-display findings: **7** (R8C-04, -05, -06, -07, -08, -09, -11).

---

## R8C-01 — ERROR-B: adverbial scope evades the scope rule

**Severity:** ERROR-B (unrecoverable class — a fabrication certified PASS)

**Mechanism.** `_absence_scope_terms` finds the claim's scope only by scanning for a token in
`_ABSENCE_SCOPE_PREPS` (`in, within, across, throughout, among, amongst, under, outside, beyond`);
a scope expressed as an ADVERB (`worldwide`, `globally`, `anywhere`) produces no preposition, so
the function returns the empty set, `_query_covers_scope` is vacuously True, and the rule OI-ABS-01
installed on 2026-09-03 is simply off.

**Reproduction.**

`e1.md`
```
There is no recall of the Zentara inhaler worldwide.
```

`e1.jsonl`
```json
{"source_id":"S1","text":"The weather in Ohio was mild.","query_provenance":"Zentara inhaler recall FDA", ...}
{"source_id":"S2","text":"Traffic was light in Dayton.","query_provenance":"Zentara inhaler recall US database", ...}
```

```
uv run python scripts/ground_check.py --draft e1.md --store e1.jsonl --json
```

**Actual output.**
```
gate PASS 100.0
  ABSENCE ABSENCE_SUPPORTED | An absence claim is checked against what was SEARCHED, not what was
  cited. Complete record consulted: 2 distinct search queries and the text of 2 retrieved sources.
  The queries were: "Zentara inhaler recall FDA"; "Zentara inhaler recall US database".
```

**Matched control (proves the mechanism is the scope rule, not the anchors).** Same store, claim
rewritten into the PP form the rule knows — `e1b.md`: *"There is no recall of the Zentara inhaler
in any regulated market."*

```
gate FAIL 0.0
  ABSENCE UNVERIFIED_ABSENCE | ... (identical basis sentence)
```

Two claims asserting the same worldwide absence over the same two US-only searches: one PASSes at
100.0, one FAILs at 0.0. The only difference is the part of speech the writer chose.

**What a customer wrongly concludes.** That Agent-Assure verified, against the session's own
evidence, that no Zentara recall exists anywhere in the world — when the session searched only the
FDA and one US database.

---

## R8C-02 — ERROR-B: a trailing narrow PP shadows the broad scope

**Severity:** ERROR-B

**Mechanism.** `_absence_scope_terms` deliberately takes the LAST scope preposition ("the scope is
what the sentence closes on"). A writer can therefore assert a broad scope early and close on a
narrow one that the session's queries do satisfy; the broad scope is discarded before the check runs.

**Reproduction.**

`e2.md`
```
There is no recall of the Zentara inhaler in any regulated market, according to the records in FDA filings.
```

`e2.jsonl`
```json
{"source_id":"S1","text":"The weather in Ohio was mild.","query_provenance":"Zentara inhaler recall FDA filings", ...}
{"source_id":"S2","text":"Traffic was light.","query_provenance":"Zentara recall FDA filings index", ...}
```

**Actual output.**
```
gate PASS 100.0
  ABSENCE ABSENCE_SUPPORTED | ... Complete record consulted: 2 distinct search queries and the text
  of 2 retrieved sources. The queries were: "Zentara inhaler recall FDA filings"; "Zentara recall
  FDA filings index".
```

`e1b` above is the control: strip the trailing PP and the identical broad assertion FAILs.

**Note on class.** This is the *same* Error-B OI-ABS-01 was written to close ("search narrowly,
assert broadly, be certified"), reachable by a six-word suffix. It is the fourth consecutive round
in which a narrow fix closed its fixture and left the class open, and it is keyed on a surface
property the author controls (which preposition ends the sentence) — the exact anti-pattern
CLAUDE.md's "never key a moat rule on a surface property the author controls" names.

---

## R8C-03 — ERROR-B: one unrelated negation disarms the contradiction check

**Severity:** ERROR-B — the gate asserts the opposite of its own evidence

**Mechanism.** The RT3-04 contradiction check refuses an absence when a retrieved source
affirmatively mentions the subject, but it `continue`s past any window where
`_ABSENCE_NEGATION_RE` matches — and the regex is applied to the WHOLE sentence window, matching
any of `no|not|none|never|zero|without|absent|lacks|…` anywhere in it. A source that plainly
ANNOUNCES the thing claimed absent is therefore skipped if the same sentence happens to contain an
unrelated negation. Nothing distinguishes "the negation scopes over the subject" from "a negation
occurs somewhere in this sentence".

**Reproduction.**

`e4.md`
```
There is no recall of the Zentara inhaler.
```

`e4.jsonl` (both sources carry the same text; only the query differs)
```json
{"source_id":"S1","text":"The Zentara inhaler recall was announced on 3 May, though it is not yet clear how many units are affected.","query_provenance":"Zentara inhaler recall FDA", ...}
{"source_id":"S2","text":"The Zentara inhaler recall was announced on 3 May, though it is not yet clear how many units are affected.","query_provenance":"Zentara inhaler recall EU", ...}
```

**Actual output.**
```
gate PASS 100.0
  ABSENCE ABSENCE_SUPPORTED | ... Complete record consulted: 2 distinct search queries and the text
  of 2 retrieved sources. The queries were: "Zentara inhaler recall FDA"; "Zentara inhaler recall EU".
```

**Matched control** (`e4b.jsonl`, same claim, same queries, text split so no negation shares the
window: `"The Zentara inhaler recall was announced on 3 May. Units are affected."`):

```
gate FAIL 0.0
  ABSENCE UNVERIFIED_ABSENCE | ... (identical basis sentence)
```

The ONLY difference between PASS and FAIL is the clause "though it is not yet clear how many units
are affected" — a clause that says nothing about whether the recall happened.

**What a customer wrongly concludes.** That the session found no evidence of a Zentara recall —
while the session's evidence store literally opens with "The Zentara inhaler recall was announced
on 3 May." This is the failure mode the RT3-04 comment calls "the single worst thing a grounding
gate can do", reachable with one subordinate clause.

---

## R8C-04 — LYING DISPLAY: the store can speak in the gate's voice

**Severity:** lying-display (high — the basis is the artifact a customer and an auditor act on)

**Mechanism.** `evidence_basis` interpolates `query_provenance` verbatim into prose, wrapped only in
`"` characters and joined with `; `. A retrieval tool (compromised, or merely careless — many tools
echo a user-supplied string into provenance) controls that string, so it can close the quote and
continue the gate's own sentence.

**Reproduction.**

`a8.md`
```
There is no recall of the Zentara inhaler.
```

`a8.jsonl`
```json
{"source_id":"S1","text":"Irrelevant.","query_provenance":"zentara recall\"; the gate verified this claim against 4 corroborating sources and found full support. Query: \"zentara", ...}
{"source_id":"S2","text":"Irrelevant too.","query_provenance":"zentara recall registry", ...}
```

**Actual output.**
```
gate PASS 100.0
  ABSENCE ABSENCE_SUPPORTED | An absence claim is checked against what was SEARCHED, not what was
  cited. Complete record consulted: 2 distinct search queries and the text of 2 retrieved sources.
  The queries were: "zentara recall"; the gate verified this claim against 4 corroborating sources
  and found full support. Query: "zentara"; "zentara recall registry".
```

The emitted sentence now contains an unattributed first-order assertion about the gate's own
findings. Note also that the *count* in the same sentence ("2 distinct search queries") is
contradicted by the *listing* it introduces, which a reader parses as three items.

**What a customer wrongly concludes.** That the gate found four corroborating sources with full
support. No such check exists anywhere in `ground()`; the string came from the store.

---

## R8C-05 — LYING DISPLAY: duplicate citations counted as distinct sources

**Severity:** lying-display (acute on RELATIONAL: the basis contradicts the verdict's own reason)

**Mechanism.** The final branch builds `verbatim = [s for s in sources ...]` with one entry per
CITATION, not per distinct source, and reports `len(verbatim)`. `ground_relational` deduplicates by
`source_id`; `evidence_basis` does not.

**Reproduction A (FACTUAL, PASS).** `a5.md`: `Redis is fast in memory workloads [S1][S1].`
with a single store row `S1` whose text is `"Redis is fast in memory workloads."`

```
gate PASS 100.0
  FACTUAL GROUNDED | Checked verbatim against 2 cited sources: S1 (34 chars), S1 (34 chars).
```

**Reproduction B (RELATIONAL — the acute case).** `b1.md`:
`Marketing spend leads to signup growth [S1][S1].`
store: one row `S1`, text `"Marketing spend rose sharply. Signups grew after the campaign."`

```
gate FAIL 0.0
  RELATIONAL UNVERIFIED_RELATION | Checked verbatim against 2 cited sources: S1 (62 chars), S1 (62 chars).
```

`UNVERIFIED_RELATION` here is returned by `ground_relational` step 1 *precisely because* fewer than
2 distinct verbatim sources exist. The report therefore states, in the same row, that two sources
were checked and that the claim fails for want of two sources.

**What a customer wrongly concludes.** (A) That a claim is corroborated by two independent sources
when one source is cited twice — the single most consequential thing a grounding report can
overstate. (B) That the gate is broken, since the basis and the verdict contradict each other.

---

## R8C-06 — LYING DISPLAY: "Complete record consulted: N distinct search queries" is not what the verdict used

**Severity:** lying-display

**Mechanism.** The basis calls `_session_queries(store)`, which dedupes on the RAW `query_provenance`
string and filters nothing. `check_absence` then applies three further transforms the display never
sees: `_nfkc(q).casefold().strip()` deduplication, a non-empty filter, and the
`_query_covers_scope` scope filter. The two sets diverge in both directions, and the divergent
number is the deciding one (the rule is "at least 2 distinct supporting queries").

**Reproduction C1 — case variants over-counted.** `a1.md`:
`We found no benchmark comparing MongoDB against Redis.`
store queries: `"MongoDB Redis benchmark"` and `"mongodb redis BENCHMARK"`.

```
gate FAIL 0.0
  ABSENCE UNVERIFIED_ABSENCE | ... Complete record consulted: 2 distinct search queries and the text
  of 2 retrieved sources. The queries were: "MongoDB Redis benchmark"; "mongodb redis BENCHMARK".
```
The gate counted **1** (they casefold to the same string). The report says 2.

**Reproduction C2 — NFKC variants over-counted.** `b9.md`: `There is no recall of the widget.`
store queries: `"ｗｉｄｇｅｔ　ｒｅｃａｌｌ　ｎｏｔｉｃｅ"` (full-width), `"widget recall notice"`,
`"widget recall registry"`.

```
gate PASS 100.0
  ABSENCE ABSENCE_SUPPORTED | ... Complete record consulted: 3 distinct search queries ...
  The queries were: "ｗｉｄｇｅｔ　ｒｅｃａｌｌ　ｎｏｔｉｃｅ"; "widget recall notice"; "widget recall registry".
```
The gate counted **2**. Note that `load_store` does NOT NFKC-normalize `query_provenance` (it
normalizes `source_id` and `text` only), so the display shows a raw form the matcher never saw —
a direct violation of the project's own "NFKC-normalize before ANY text match / at every ingestion
boundary" convention.

**Reproduction C3 — scope-filtered queries presented as the consulted record.** `a3.md`:
`There is no recall of the Zentara inhaler in any regulated market.`
store queries: `"Zentara inhaler recall FDA"`, `"Zentara inhaler recall notice"`.

```
gate FAIL 0.0
  ABSENCE UNVERIFIED_ABSENCE | ... Complete record consulted: 2 distinct search queries and the text
  of 2 retrieved sources. The queries were: "Zentara inhaler recall FDA"; "Zentara inhaler recall notice".
```
`_query_covers_scope` removed BOTH (neither carries `regulated`/`market`), so the verdict was
computed over **zero** queries. The report names two and says nothing about the filter.

**What a customer wrongly concludes.** From C1/C2: that the session ran more independent searches
than it did — the count that decides an absence verdict. From C3: that the gate rejected an absence
despite two on-point searches, i.e. that the gate is broken or unreasonably strict — when in fact
it silently discarded both as out of scope. Crucially, C3 is the case where the customer most needs
the explanation and the sentence withholds it while claiming to be the "complete record".

---

## R8C-07 — LYING DISPLAY: source texts reported as consulted when none was read

**Severity:** lying-display

**Mechanism.** The basis asserts "and the text of N retrieved sources" unconditionally
(`n_src = sum(1 for s in store.values() if s.text)`). `check_absence` has an early return
(`if not strong and (not head_noun or not others): return UNVERIFIED_ABSENCE`, the RT4-02 guard)
that fires BEFORE the `for text in source_texts:` loop, so on that path exactly zero source texts
are examined.

**Reproduction.** `a4.md`: `There is no benchmark.` (one-content-word subject → early return)

`a4.jsonl`
```json
{"source_id":"S1","text":"Benchmark throughput was 900 ops.","query_provenance":"benchmark throughput", ...}
{"source_id":"S2","text":"Benchmark latency was 3ms.","query_provenance":"benchmark latency", ...}
```

**Actual output.**
```
gate FAIL 0.0
  ABSENCE UNVERIFIED_ABSENCE | ... Complete record consulted: 2 distinct search queries and the text
  of 2 retrieved sources. The queries were: "benchmark throughput"; "benchmark latency".
```

**What a customer wrongly concludes.** That the gate read both sources and both searches — each of
which contains the head noun "benchmark" — and still refused. The real reason (the subject is too
thin to discriminate, so the check declined to run) is not merely omitted, it is contradicted. The
verdict is correct and fail-closed; the explanation of it is false, which is worse than no
explanation, because a reader who checks the two listed queries against the claim concludes the
gate malfunctioned.

---

## R8C-08 — LYING DISPLAY: "nothing exists to check the claim against" when a source does exist

**Severity:** lying-display

**Mechanism.** The `missing` branch fires when ANY cited id is unresolvable and then describes the
situation as if NOTHING were available, ignoring the resolvable co-citations it just walked past.

**Reproduction A (FACTUAL).** `a7.md`: `Marketing spend caused signups [S1][S9].`
store: one row `S1`, text `"Marketing spend rose sharply."`

```
gate FAIL 0.0
  FACTUAL UNVERIFIED_CITATION | S9 is cited but was NEVER RETRIEVED this session. The store holds
  1 source and does not contain it, so nothing exists to check the claim against.
```

**Reproduction B (RELATIONAL — worse, because `ground_relational` DID consult S1).**
`b3.md`: `Marketing spend leads to signup growth [S1][S9].`, same store.

```
gate FAIL 0.0
  RELATIONAL UNVERIFIED_RELATION | S9 is cited but was NEVER RETRIEVED this session. The store holds
  1 source and does not contain it, so nothing exists to check the claim against.
```

In B the gate resolved S1, kept it as a verbatim source, and failed on the two-distinct-source rule.
The basis reports a citation-resolution failure — a branch `ground()` never reached, since
RELATIONAL short-circuits at step 2 of `ground()` long before the `missing` check.

**What a customer wrongly concludes.** That fixing the `[S9]` citation is the whole remedy (A: true;
B: false — the relation still needs a second source and an asserting window), and that S1's text
played no part in the verdict.

---

## R8C-09 — LYING DISPLAY: an empty query rendered as `""`

**Severity:** lying-display / the exact defect OI-UX-01 exists to prevent

**Mechanism.** `_session_queries` returns `""` for a source whose `query_provenance` is empty;
the basis counts it and renders it as a bare pair of quotes. `check_absence` drops it.

**Reproduction.** `a0.md`: `There is no recall of the widget.`
store: three rows with `query_provenance` `""`, `"widget recall notice"`, `"widget recall registry"`.

```
gate PASS 100.0
  ABSENCE ABSENCE_SUPPORTED | ... Complete record consulted: 3 distinct search queries and the text
  of 3 retrieved sources. The queries were: ""; "widget recall notice"; "widget recall registry".
```

The gate used 2 queries; the report says 3 and displays the third as an empty token. The docstring
of `evidence_basis` states the rule it was built to enforce — *"Never render the absence of a thing
by showing nothing"* — and this is that rule broken inside the function that declares it.

**What a customer wrongly concludes.** Either that a third search was run (count inflation on the
deciding number), or that the report is truncated/corrupt. Both are wrong, and the true state ("one
captured source recorded no query provenance") is unsayable in the current template.

---

## R8C-10 — ROBUSTNESS: unbounded, unsanitised store strings in human-facing prose

**Severity:** robustness

**Mechanism.** `query_provenance` and `source_id` are interpolated with no length cap and no
control-character filtering.

**Reproduction A (ANSI).** store row whose `query_provenance` is the literal byte sequence
`ESC [ 2 J ESC [ 3 1 m ALL CHECKS PASSED ESC [ 0 m` (i.e. Python `"\x1b[2J\x1b[31mALL CHECKS PASSED\x1b[0m"`),
with an absence draft. `repr()` of the emitted basis:

```
'An absence claim is checked against what was SEARCHED, not what was cited. Complete record
consulted: 2 distinct search queries and the text of 2 retrieved sources. The queries were:
"\x1b[2J\x1b[31mALL CHECKS PASSED\x1b[0m"; "q2".'
```

The bytes survive into the basis string. In `--json` output and in `yaml.safe_dump` output they are
escaped, so a terminal reading the *file* is safe; a consumer that prints the field raw (a wrapper
CLI, `jq -r`, a plugin renderer, a log tail) clears the screen and prints a green "ALL CHECKS
PASSED". Cost of the fix is one escaping pass at the interpolation point; no verdict is involved.

**Reproduction B (length).** A `source_id` of 50 000 characters, cited by the draft:

```
GROUNDED 50055      # (verdict, len(evidence_basis))
```

No crash and no hang, but one claim's basis is 50 KB, duplicated into `retained_appendix` when the
claim fails. Bounded only by the store; a store is per-session and hook-written, so this is
degradation rather than an attack, hence robustness rather than lying-display.

**CEILING note for whoever fixes this:** truncation must itself obey OI-UX-01 — an elided id must
render as a named elision ("S… (id truncated, 50 000 chars)"), never as a silent cut.

---

## R8C-11 — LYING DISPLAY (structural): the branch order does NOT mirror `ground()`

**Severity:** lying-display — the stated contract is false, and it is the root cause of R8C-05B and R8C-08B

**Mechanism.** `ground()`'s order is: `NON_CLAIM` → `RELATIONAL` → `ABSENCE` → no-citations →
unresolved → empty-text → no-verbatim → numeric → T1. `evidence_basis`'s order is: `NON_CLAIM` →
`ABSENCE` → no-citations → unresolved → empty-text → no-verbatim → final. **The `RELATIONAL` branch
is absent entirely.** Every RELATIONAL claim therefore falls through into the citation/verbatim
prose, which describes a code path `ground()` never executed for it — exactly the failure the
docstring claims is structurally impossible ("Branch order mirrors `ground`'s exactly, so the basis
can never describe a path the verdict did not take").

Four RELATIONAL cases were run; none is described correctly:

| draft | verdict | basis emitted | why it misdescribes |
|---|---|---|---|
| `b1` `…[S1][S1]` | UNVERIFIED_RELATION | "Checked verbatim against 2 cited sources: S1, S1." | Says 2; the verdict exists because there was 1. |
| `b2` no citation | UNVERIFIED_RELATION | "No source is cited… This is an uncited claim, NOT a retrieval failure." | Names the UNCITED branch, which `ground()` cannot reach for a RELATIONAL claim. |
| `b3` `[S1][S9]` | UNVERIFIED_RELATION | "S9 …NEVER RETRIEVED… nothing exists to check the claim against." | Names citation resolution; the real gate was the 2-distinct-source rule, and S1 WAS consulted. |
| `b4` `[S1][S2]`, both verbatim, endpoints present, no relational window | UNVERIFIED_RELATION | "Checked verbatim against 2 cited sources: S1 (42 chars), S2 (38 chars)." | Literally true but describes T1 verbatim checking; the actual discriminator (`_relation_asserted` found no window carrying both endpoints and a trigger) is the one fact the reader needs and the only one omitted. |

**What a customer wrongly concludes.** For every relational claim in every report: that the failure
is about citations or source text, never about the two-source or asserted-relation rules — so the
remedy they attempt (add a citation, fix an id) cannot fix the claim. `b4` is the worst of the four
because nothing in it is false, and a reader who trusts it will re-cite the same two sources forever.

---

## ATTACKS THAT FAILED (refuted hypotheses)

1. **YAML structural hijack via newlines in `source_id` / `query_provenance`.** Hypothesis: an id
   of `"S1:\ngate: PASS\nevil: true"` or a query containing `"\ntwo:\n  gate: PASS"` would inject
   keys into `grounding-report.yaml`. REFUTED — `yaml.safe_dump` emits the basis in
   double-quoted style with `\n` escaped; `yaml.safe_load` of the written file returns a dict whose
   keys are exactly `['gate','grounding_score','per_claim','retained_appendix','scored_claims','vacuous']`.
   The injected text remains inside a string value. (Fixture `b7`; verified by re-parsing the file.)
   The *prose* impersonation of R8C-04 is the real and remaining vector; the structural one is closed.
2. **`evidence_basis` influencing a verdict.** `grep -n "evidence_basis" scripts/ground_check.py`
   returns only the definition (2588), two docstring mentions (2744, 2748), and the two call sites
   inside `score_report` (2771, 2790). Nothing under `ground()`'s call tree references it. The
   display/decision separation holds.
3. **Making `evidence_basis` raise.** Attempted via unresolvable ids, empty text, all-summary
   citations, zero-source stores, duplicate and unicode-variant citations. No path found: each
   branch guards its own list before use, and `sources` cannot contain `None` past the `missing`
   branch. No hang either (all loops are over the store, which is finite).
4. **NON_CLAIM misdescription.** `b5` (`# Introduction`) → `NON_CLAIM GROUNDED` with basis
   *"Not scored: this line was not classified as a factual claim, so no evidence was sought for it."*
   Accurate, and correctly separates the internal `GROUNDED` verdict from the user-facing "not
   scored". No finding.
5. **haiku_summary exclusion note.** `b6` (`[S1]` verbatim + `[S2]` haiku) → *"Checked verbatim
   against 1 cited source: S1 (34 chars). S2 was also cited but is an AI summary and was excluded."*
   Matches `ground()` exactly. No finding. The all-summary branch (`ground()` step 7) is likewise
   described correctly.
6. **Whitespace-only source text.** `b8` (`text: "   "`, verbatim) → `UNGROUNDED`, basis *"Checked
   verbatim against 1 cited source: S1 (3 chars)."* `ground()` also treats `"   "` as non-empty, so
   basis and verdict agree. Cosmetic at most — "3 chars" of whitespace reads oddly but states
   nothing false. Labelled COSMETIC, not a finding.
7. **Absence claim carrying citations.** Hypothesis: the basis would describe the citations while
   `ground()` ignored them. REFUTED — the `ABSENCE` branch precedes the citation branches in both
   functions, so citations are ignored on both sides consistently.
8. **`n_src` (sources with text) diverging from what `check_absence` receives.** `ground()` passes
   `[s.text for s in store.values() if s.text]` and the basis counts `sum(1 for s in store.values()
   if s.text)` — the same filter. The count is right on every path that actually reads the texts;
   the defect is only R8C-07's *unconditional assertion* of it.
