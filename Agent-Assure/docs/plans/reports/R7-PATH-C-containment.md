# R7 PATH C — Exact containment and its hedge guard

Round 7 adversarial run, 2026-09-12. Surface: `scripts/ground_check.py`
`_SPAN_HEDGE_TOKENS` / `_SPAN_HEDGE_LOOKBACK` (=5) / `_span_is_hedged` /
`_claim_contained_verbatim` / `t1_verbatim`.

**Result: 13 confirmed Error-B (fabrication certified PASS), across 5 mechanisms.**
No file under `scripts/` or `tests/` was modified. All drafts/stores in the
session scratchpad; both stores are reproduced verbatim below.

## Root cause, one sentence

`_span_is_hedged` is a **bag-of-tokens test over a fixed 5-token window placed
immediately before the span**, and the ATTACKER writes the source: he chooses
the distance between the hedge and the span, the spelling of the hedge, its
part of speech, and whether it sits before or after the span. Every one of
those four degrees of freedom defeats the guard, and the guard has no way to
see any of them.

## Stores used

`storeC.jsonl` (findings C-1 … C-8), one JSONL record per source, field shape
copied exactly from `tests/red_team_moat/fixtures/store_containment.jsonl`
(`source_id,url,file_path,fetched_at,tool,content_sha256,text,full_text_source,
captured_via,query_provenance`; `full_text_source":"verbatim"`):

| id | source text (realistic prose the attacker retrieved) |
|----|------|
| S1 | `Critics have argued for many years now that Redis loses data on restart.` |
| S2 | `The appliance survives a total power loss, a marketing line the vendor later withdrew.` |
| S3 | `Is it true that the database replicates synchronously across regions? The evidence says otherwise.` |
| S4 | `Several vendors have spread a persistent myth for more than a decade. The firewall blocks all zero-day exploits.` |
| S5 | `Imagine for a moment that the gateway drops every packet.` |
| S6 | `Should the primary fail, the replica takes over automatically.` |
| S7 | `The proxy terminates TLS at the edge, which is simply not the case in production.` |
| S8 | `Sceptics maintain, and have done so in print since 2019, that the scheduler starves low-priority jobs.` |

`storeD.jsonl` (C-9 … C-12 and the honest mirror M-1):

| id | source text |
|----|------|
| S11 | `Sceptics maintain that the scheduler starves low-priority jobs.` |
| S12 | `The vendor сlaims the array rebuilds in place without downtime.`  ← Cyrillic `с` (U+0441) in "claims" |
| S13 | `This is the so-called finding that the compiler removes bounds checks.` |
| S14 | `Our own benchmark has shown repeatedly over the past year that Redis loses data on restart.`  (HONEST mirror) |
| S15 | `The report debunks the idea that the agent phones home every hour.` |

`storeE.jsonl` (C-13 and two unbroken controls): S21 =
`Critics have argued for many years now that Redis handles 500K ops per second.`,
S22 = `Critics claim the queue drops messages.`

## Findings

Every draft below is the FULL file (one line + newline). Command in all cases:

```
uv run python scripts/ground_check.py --draft <draft> --store <store> --json
```

### Mechanism 1 — the hedge sits more than 5 tokens before the span

`_SPAN_HEDGE_LOOKBACK = 5`. The attacker pads the attributing clause with
ordinary adverbial filler ("for many years now", "and have done so in print
since 2019") until the hedge verb falls out of the window. Nothing about the
padding looks adversarial — it is how journalism is written.

**C-1** draft: `Redis loses data on restart [S1].`
```json
{"gate": "PASS", "grounding_score": 100.0, "per_claim": [{"index": 0, "kind": "FACTUAL", "text": "Redis loses data on restart [S1].", "verdict": "GROUNDED"}], "retained_appendix": [], "scored_claims": 1, "vacuous": false}
```
Unsupported because S1 attributes the statement to critics and does not make it.
Window inspected is `for many years now that` — tokens 3-7; `argued` is token 2.

**C-8** draft: `The scheduler starves low-priority jobs [S8].`
```json
{"gate": "PASS", "grounding_score": 100.0, "per_claim": [{"index": 0, "kind": "FACTUAL", "text": "The scheduler starves low-priority jobs [S8].", "verdict": "GROUNDED"}], "retained_appendix": [], "scored_claims": 1, "vacuous": false}
```
Same mechanism with a parenthetical instead of an adverbial.

**C-13** (storeE) draft: `Redis handles 500K ops per second [S21].`
```json
{"gate": "PASS", "grounding_score": 100.0, "per_claim": [{"index": 0, "kind": "NUMERIC", "text": "Redis handles 500K ops per second [S21].", "verdict": "GROUNDED"}], "retained_appendix": [], "scored_claims": 1, "vacuous": false}
```
The numeric tier does NOT backstop this: `numeric_ok` runs first and passes,
because the number really is in the source — it is the *attribution* that was
stripped, not the magnitude. So the lookback hole reaches NUMERIC claims too.

### Mechanism 2 — hedge expressed by a verb that is not in `_SPAN_HEDGE_TOKENS`

The set lists ~25 attribution verbs. English has hundreds. Adjacency does not
help when the token is simply absent from the set.

**C-9** (storeD) draft: `The scheduler starves low-priority jobs [S11].`
```json
{"gate": "PASS", "grounding_score": 100.0, "per_claim": [{"index": 0, "kind": "FACTUAL", "text": "The scheduler starves low-priority jobs [S11].", "verdict": "GROUNDED"}], "retained_appendix": [], "scored_claims": 1, "vacuous": false}
```
`maintain` sits *immediately* before the span (window = `sceptics maintain that`)
and is not in the set. Cheap unlisted synonyms: maintain, insist, hold, posit,
speculate, imply, "so-called", "the idea that", "on this view".

**C-11** (storeD) draft: `The compiler removes bounds checks [S13].`
```json
{"gate": "PASS", "grounding_score": 100.0, "per_claim": [{"index": 0, "kind": "FACTUAL", "text": "The compiler removes bounds checks [S13].", "verdict": "GROUNDED"}], "retained_appendix": [], "scored_claims": 1, "vacuous": false}
```
`so-called` tokenizes to `so`,`called` — neither listed.

**C-12** (storeD) draft: `The agent phones home every hour [S15].`
```json
{"gate": "PASS", "grounding_score": 100.0, "per_claim": [{"index": 0, "kind": "FACTUAL", "text": "The agent phones home every hour [S15].", "verdict": "GROUNDED"}], "retained_appendix": [], "scored_claims": 1, "vacuous": false}
```
`debunks` is a *denial* verb — the strongest possible hedge in the language —
and it is absent from the denial list, which contains only `denies/disputes/refutes`.

### Mechanism 3 — a hedge token spelled so NFKC cannot fold it

`_tokenize` = NFKC + casefold. NFKC does **not** map Cyrillic `с` (U+0441) to
Latin `c` — exactly the limitation the global rule about confusables names, and
exactly what `_CONFUSABLES` already fixes **but only inside the numeric-context
window** (`_fold`, ~line 1330). The containment path never folds.

**C-10** (storeD) draft: `The array rebuilds in place without downtime [S12].`
```json
{"gate": "PASS", "grounding_score": 100.0, "per_claim": [{"index": 0, "kind": "FACTUAL", "text": "The array rebuilds in place without downtime [S12].", "verdict": "GROUNDED"}], "retained_appendix": [], "scored_claims": 1, "vacuous": false}
```
Source reads `The vendor сlaims …`. A human reader sees "claims"; `_span_is_hedged`
sees the token `сlaims` (Cyrillic с) which is not in the frozenset. NOTE the
claim's own `without` IS a listed hedge token — it did not matter, because the
guard only reads *source* tokens *before* the span.

### Mechanism 4 — hedge carried by structure, not by a token before the span

**C-3** draft: `The database replicates synchronously across regions [S3].`
```json
{"gate": "PASS", "grounding_score": 100.0, "per_claim": [{"index": 0, "kind": "FACTUAL", "text": "The database replicates synchronously across regions [S3].", "verdict": "GROUNDED"}], "retained_appendix": [], "scored_claims": 1, "vacuous": false}
```
Interrogative: `Is it true that …? The evidence says otherwise.` The question
mark and the following sentence carry the whole force; the window is
`is it true that`, none of which is listed. A question is not an assertion,
and the guard has no notion of sentence mood.

**C-5** draft: `The gateway drops every packet [S5].`
```json
{"gate": "PASS", "grounding_score": 100.0, "per_claim": [{"index": 0, "kind": "FACTUAL", "text": "The gateway drops every packet [S5].", "verdict": "GROUNDED"}], "retained_appendix": [], "scored_claims": 1, "vacuous": false}
```
Imperative-hypothetical `Imagine for a moment that …`. The set has
`suppose/assume/hypothetically` but not `imagine` — and even a complete verb
list would still miss "Picture a world in which …", "Consider the case where …".

**C-6** draft: `The replica takes over automatically [S6].`
```json
{"gate": "PASS", "grounding_score": 100.0, "per_claim": [{"index": 0, "kind": "FACTUAL", "text": "The replica takes over automatically [S6].", "verdict": "GROUNDED"}], "retained_appendix": [], "scored_claims": 1, "vacuous": false}
```
Subject-auxiliary-inversion conditional: `Should the primary fail, X`. Exactly
the class the existing `if`-conditional tripwire
(`test_moat_quote_mining.py::mined-from-conditional`) was written to catch —
`should` is a conditional marker here but is not in the set, and `if` is.
Sibling forms all work: `Were the region to fail, X`, `Had the disk filled, X`.

**C-4** draft: `The firewall blocks all zero-day exploits [S4].`
```json
{"gate": "PASS", "grounding_score": 100.0, "per_claim": [{"index": 0, "kind": "FACTUAL", "text": "The firewall blocks all zero-day exploits [S4].", "verdict": "GROUNDED"}], "retained_appendix": [], "scored_claims": 1, "vacuous": false}
```
The hedge (`myth`) is in the PREVIOUS sentence — it is in `_SPAN_HEDGE_TOKENS`,
and it is 7 tokens away, so the fixed window never reaches it. The window
straddles a sentence boundary without noticing, which is the mirror-image of
the bug: the guard is simultaneously too short to see the governing clause and
structurally willing to read across a full stop.

### Mechanism 5 — the hedge sits AFTER the span

`_span_is_hedged` inspects `source_tokens[start-5:start]` only. Nothing to the
right of the span is ever read, so a trailing retraction is invisible.

**C-2** draft: `The appliance survives a total power loss [S2].`
```json
{"gate": "PASS", "grounding_score": 100.0, "per_claim": [{"index": 0, "kind": "FACTUAL", "text": "The appliance survives a total power loss [S2].", "verdict": "GROUNDED"}], "retained_appendix": [], "scored_claims": 1, "vacuous": false}
```
Source: `…, a marketing line the vendor later withdrew.` The span starts at
token 0, so the window is EMPTY — a maximally strong "I don't know" that points
straight at PASS, which is the exact `None`/empty-collection failure the
CLAUDE.md rule "every 'I don't know' must point AWAY from PASS" names.

**C-7** draft: `The proxy terminates TLS at the edge [S7].`
```json
{"gate": "PASS", "grounding_score": 100.0, "per_claim": [{"index": 0, "kind": "FACTUAL", "text": "The proxy terminates TLS at the edge [S7].", "verdict": "GROUNDED"}], "retained_appendix": [], "scored_claims": 1, "vacuous": false}
```
Source: `…, which is simply not the case in production.` The token `not` — a
listed hedge — is four tokens after the span's end and is never looked at.
Note the asymmetry: the SAME token four tokens *before* the span blocks
(mechanism-control c3 below), four tokens *after* does not.

## The mirror — what a naive fix would wrongly reject

Required by the brief, and it is the binding constraint on any repair.

**M-1** draft `Redis loses data on restart [S14].` against S14
(`Our own benchmark has shown repeatedly over the past year that Redis loses
data on restart.`) → `PASS / GROUNDED / 100.0`. This is **correct**: the source
asserts the claim in its own voice.

S14 and S1 are **structurally identical** — `<subject> <reporting-verb>
<6 tokens of adverbial padding> that <SPAN>`. They differ only in whether the
matrix subject is the source itself or a third party. Therefore:

- **Widening `_SPAN_HEDGE_LOOKBACK` to cover C-1 also rejects M-1** (`shown` /
  `benchmark` would have to be treated as hedges, or the window would have to
  reach `our own benchmark has shown`, whose verb is an assertion). Widening to
  the sentence start rejects every honest quotation embedded in any complement
  clause — which is most technical prose.
- **Extending the window to the right (C-2/C-7) rejects** honest
  `X, and our measurements confirm it.` if the trailing scan is token-set based,
  because `confirm`-class sentences routinely contain `no`, `not`, `without`
  ("X, with no caveats").
- **Enlarging `_SPAN_HEDGE_TOKENS` (C-9/C-11/C-12) cannot terminate.** It is an
  open lexical class, and each addition costs honest quotations: adding
  `maintain` breaks `The controller maintains quorum`; adding `holds` breaks
  `The lock holds for the duration`.

So the shape of any real fix is NOT a bigger window or a longer list — both are
"key a moat rule on a surface property the author controls", the failure the
project already recorded twice (round 3 token-count, round 4 Title Case). The
only properties the attacker cannot set without abandoning the attack are
**positional and grammatical**: whether the span is the source sentence's own
matrix clause (rather than a complement of some other verb), and whether the
span's sentence is declarative. A candidate that is fail-closed and cheap:
*refuse containment unless the matched span begins at the start of a source
SENTENCE and that sentence ends in a full stop* — C-2, C-3, C-5, C-6, C-7 die
(span is a complement or the sentence is interrogative), C-1/C-8/C-9/C-13 die
(span is inside a `that`-complement), and M-1 dies too. That last one is the
price, and it is Error-A, i.e. recoverable — but it must be measured on the
n=52 gold set before adoption, not asserted. **Escalation note:** every repair
sketched here moves claims only AWAY from PASS, so on the 2026-08-30 reading of
escalation rule #1 it is inside agent authority; the *choice among* them
changes the Error-A/Error-B trade-off and is Sai's.

**Load-bearing assumption of this whole report:** that a source may legitimately
contain any sentence the attacker wants, i.e. that the attacker controls the
retrieved text. That is stated in the brief and is realistic (an adversary picks
which pages to fetch), but if the threat model were instead "trusted corpus,
untrusted draft", mechanisms 1-4 weaken considerably and only C-2/C-7 (hedge
after the span, in ordinary journalistic prose the attacker did not author)
survive unconditionally.

## Families tried and unbroken

1. **Numeric fabrication through the containment path.** `numeric_ok` runs
   BEFORE `t1_verbatim` in `ground()`, so a contained span does not bypass the
   value+unit check. Control c2 — draft `Redis handles 900K ops per second [S21].`
   against S21 (which says 500K): `{"gate": "FAIL", "grounding_score": 0.0,
   "per_claim": [{"index": 0, "kind": "NUMERIC", "verdict": "UNVERIFIED_NUMBER"}]}`.
   Containment only launders the *attribution*, never the magnitude.
2. **Hedge immediately before the span, listed token.** The guard works exactly
   as designed. Control c3 — draft `The queue drops messages [S22].` against
   `Critics claim the queue drops messages.`: `{"gate": "FAIL",
   "grounding_score": 0.0, "per_claim": [{"verdict": "UNGROUNDED"}]}`. Likewise
   the three existing `test_moat_quote_mining.py` attacks still fail correctly.
3. **Hedge in an uncited source.** Per-span/per-source scoping holds; no
   cross-source leakage found (the existing S4/S6 test is sound).
4. **Citation-marker smuggling into the span.** `_strip_citations` removes the
   marker before tokenizing, so `[S1]` cannot be made to supply span tokens; no
   variant found where the bracket text participated in a match.
5. **Whitespace / punctuation splitting of the claim to shorten the required
   span.** `_tokenize` discards punctuation on both sides symmetrically, so the
   claim's token sequence is what it looks like; no asymmetry found to exploit.

## Reproduction

Stores and drafts are in the session scratchpad
(`storeC.jsonl`, `storeD.jsonl`, `storeE.jsonl`, `a1..a8.md`, `b1..b5.md`,
`c1..c3.md`). All source texts are reproduced in full in the tables above, so
the fixtures can be regenerated from this document alone.
