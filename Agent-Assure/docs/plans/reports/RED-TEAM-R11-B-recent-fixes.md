# Red-Team Round 11, Adversary B — the three fixes of the last two hours

Scope: R10C-03 / D-45 (absence basis must be verbatim), R10C-04 / D-46 (numbers
inside RELATIONAL claims), J-39 / D-48 (word-boundary endpoint matching).
All reproductions run against `29e3087` on `provenance-fix-2026-10-01`.
Working tree clean; nothing under `scripts/`, `calibration/` or `tests/` touched.
Fixtures: `/tmp/claude-501/aa/r11b/`.

## Verdicts

- **CLAIM 1 (R10C-03): REFUTED — 1 ERROR-B**
- **CLAIM 2 (R10C-04): REFUTED — 2 ERROR-B**
- **CLAIM 3 (J-39): UPHELD for Error-B, REFUTED as "strictly fail-closed" — 1 ERROR-A**

Counts: **3 ERROR-B**, **2 ERROR-A**, **1 cosmetic**, 0 unreproduced hypotheses
carried as findings.

---

## R11B-01 — ERROR-B — downgrading evidence to a summary CERTIFIES an absence that the same evidence as verbatim REFUSES

This is the exact inversion of R10C-03's stated invariant ("a summary may REFUSE
an absence claim, never CERTIFY one") and of its stated direction ("Fail-closed").

Draft (`E_draft.md`), one claim:

```
'There is no benchmark for the streaming ingest workload.\n'
```

Store: four records, identical texts and identical `query_provenance` in both
runs. The ONLY difference is that S3/S4 are `verbatim` in one and
`haiku_summary` (tool `WebFetch`) in the other.

```
S1 verbatim q="benchmark streaming ingest workload"  text="The ingest pipeline was rewritten in Rust last quarter. Latency numbers were not published."
S2 verbatim q="benchmark ingest workload latency"    text="Operations moved to a new scheduler. No figures were released."
S3 ???      q="benchmark redis"                      text="Redis remains a popular cache layer for many teams."
S4 ???      q="benchmark postgres"                   text="Postgres is widely deployed for transactional workloads."
```

Commands and actual output:

```
$ uv run python3 scripts/ground_check.py --draft /tmp/claude-501/aa/r11b/E_draft.md \
      --store /tmp/claude-501/aa/r11b/E_verbatim.jsonl --json
{"gate": "FAIL", "grounding_score": 0.0, "per_claim": [{"index": 0, "kind": "ABSENCE",
 "text": "There is no benchmark for the streaming ingest workload.",
 "verdict": "UNVERIFIED_ABSENCE", "evidence_basis": "... 4 distinct search queries ..."}],
 "retained_appendix": [ ...1 row... ], "scored_claims": 1, "vacuous": false}
exit=1

$ uv run python3 scripts/ground_check.py --draft /tmp/claude-501/aa/r11b/E_draft.md \
      --store /tmp/claude-501/aa/r11b/E_summary.jsonl --json
{"gate": "PASS", "grounding_score": 100.0, "per_claim": [{"index": 0, "kind": "ABSENCE",
 "text": "There is no benchmark for the streaming ingest workload.",
 "verdict": "ABSENCE_SUPPORTED", "evidence_basis": "An absence claim is checked against
 what was SEARCHED, not what was cited. Complete record consulted: 4 distinct search
 queries and the text of 4 retrieved sources. The queries were: \"benchmark streaming
 ingest workload\"; \"benchmark ingest workload latency\"; \"benchmark redis\";
 \"benchmark postgres\"."}],
 "retained_appendix": [], "scored_claims": 1, "vacuous": false}
exit=0
```

Got: `ABSENCE_SUPPORTED` / gate PASS 100.0 with empty retained appendix.
Correct: `UNVERIFIED_ABSENCE` / FAIL — strictly no *better* than the all-verbatim
run, since the summary run holds strictly *less* certifiable evidence.

**Mechanism.** `_verbatim_session_queries` (`scripts/ground_check.py:2864`) is fed
to `check_absence` as the whole query universe, so it shrinks not only the
matching set but the *denominator* of the blanket-corpus-word refusal at
`scripts/ground_check.py:2553`:

```
if len(distinct) >= 3 and 2 * len([q for q in distinct if head_noun in q]) > len(distinct):
    return Verdict.UNVERIFIED_ABSENCE
```

With four queries, "benchmark" is in 4/4 → blanket word → refuse. Filtering the
two summary-derived queries out drops `distinct` to 2, the `>= 3` gate switches
the refusal OFF entirely, and the remaining two queries certify. Summary records
used to contribute a REFUSAL; R10C-03 removed them from the refusal as well as
from the certification. The fix was written as though `distinct` only ever feeds
`match_count`; it also feeds a fail-closed guard, and removing inputs from a
fail-closed guard is fail-OPEN.

Sanity check that R10C-03's own fixture class still holds (so this is a new hole,
not the old one): with ALL four records as `haiku_summary`, the verbatim-basis
check at `ground_check.py:2977` fires and the gate returns `UNVERIFIED_ABSENCE`,
FAIL, exit=1. Confirmed.

**Class, not fixture.** Any absence whose head noun is common enough to trip the
majority rule is now certifiable by *degrading* part of the session's capture.
The attacker does not even need to author the degradation: a session that used
native `WebFetch` for two of its four retrievals gets the weaker rule for free.

**Suggested direction (not applied).** Compute the blanket-word denominator over
`_session_queries(store)` (all records) and the `match_count` numerator over
`_verbatim_session_queries(store)`. Refusals read the whole store; certifications
read verbatim only. That is what "may refuse, never approve" actually means, and
it is the asymmetry the docstring already claims.

---

## R11B-02 — ERROR-B — a spelled-out number inside a RELATIONAL claim is never checked

Draft (`A_draft.md`):

```
'Poor indexing causes ninety-seven percent of silent data loss [S1][S2].\n'
```

Control (`A_control.md`), identical but for the surface spelling of the figure:

```
'Poor indexing causes 97% of silent data loss [S1][S2].\n'
```

Store `A_store.jsonl` (both runs), containing no percentage at all:

```
S1 verbatim q="indexing data loss"        text="Poor indexing causes silent data loss in write-heavy clusters. Engineers report that the problem is hard to detect."
S2 verbatim q="silent data loss recovery" text="Silent data loss can persist for months before anyone notices. Recovery is expensive."
```

```
$ uv run python3 scripts/ground_check.py --draft .../A_draft.md --store .../A_store.jsonl --json
{"gate": "PASS", "grounding_score": 100.0, "per_claim": [{"index": 0, "kind": "RELATIONAL",
 "text": "Poor indexing causes ninety-seven percent of silent data loss [S1][S2].",
 "verdict": "GROUNDED",
 "evidence_basis": "Checked verbatim against 2 cited sources: S1 (115 chars), S2 (85 chars)."}],
 "retained_appendix": [], "scored_claims": 1, "vacuous": false}
exit=0

$ uv run python3 scripts/ground_check.py --draft .../A_control.md --store .../A_store.jsonl --json
{"gate": "FAIL", "grounding_score": 0.0, "per_claim": [{"index": 0, "kind": "RELATIONAL",
 "text": "Poor indexing causes 97% of silent data loss [S1][S2].",
 "verdict": "UNVERIFIED_NUMBER", ...}],
 "retained_appendix": [ ...1 row... ], "scored_claims": 1, "vacuous": false}
exit=1
```

Got: GROUNDED / PASS 100.0. Correct: `UNVERIFIED_NUMBER` / FAIL — the store
contains no "ninety-seven percent", no 97, and no percentage.

**Mechanism.** `ground()`'s new guard is `if verdict == Verdict.GROUNDED and
claim.numeric_tokens:` (`scripts/ground_check.py:2957`), and `numeric_tokens` comes
from `_NUMERIC_RE = \$?\d[\d,.]*\s?(?:%|million|billion|k|m|bn)?`
(`scripts/ground_check.py:764`), which **requires a digit**. The check is keyed on
a surface property the author controls — the Shift key of round 4, respelt as the
number row. Measured at `classify()` level, every one of these RELATIONAL claims
yields `numeric_tokens == ()` and therefore skips the new check entirely:

| Draft figure | `numeric_tokens` | checked? |
|---|---|---|
| `ninety-seven percent` | `()` | no |
| `two thirds` | `()` | no |
| `one in three` | `()` | no |
| `a threefold rise` | `()` | no |
| `outages to double` | `()` | no |
| `the third-largest share` | `()` | no |
| `half of all outages` | `()` | no |
| `a majority of outages` | `()` | no |
| `losses of four million dollars` | `()` | no |
| `a 3x rise` | `('3',)` | yes, but as bare absolute `3` |
| `40-60%` | `('40', '60%')` | yes, and wrongly — see R11B-05 |
| `since 2019` | `('2019',)` | yes |

**Same defect on the ABSENCE path, reproduced as instructed.** The brief asks
whether ABSENCE is genuinely protected or only incidentally. It is only
incidentally protected, and the incident is the same digit:

```
F_spelled.md = 'There is no evidence of ninety-seven percent uptime in the status page.\n'
F_digit.md   = 'There is no evidence of 97% uptime in the status page.\n'
F_store.jsonl:
  S1 verbatim q="evidence uptime status page"         text="The status page lists rolling maintenance windows for the last quarter."
  S2 verbatim q="uptime evidence status page archive" text="Operations publishes a weekly note about scheduled downtime."
```

```
F_spelled → {"gate":"PASS","grounding_score":100.0,"verdict":"ABSENCE_SUPPORTED","kind":"ABSENCE"} exit=0
F_digit   → {"gate":"FAIL","grounding_score":0.0,"verdict":"UNVERIFIED_ABSENCE","kind":"ABSENCE"} exit=1
```

The digit version is refused only because `_extract_absence_anchors`
(`scripts/ground_check.py:2233`) promotes any token containing a digit to a strong
anchor; spell the same figure in letters and the anchor disappears with it.
J-40 recorded this as a CEILING. The reproduction shows the ceiling is not a
corner case — it is one keystroke away on every absence claim that carries a
figure.

---

## R11B-03 — ERROR-B — the relational numeric check reads the WHOLE STORE, not the cited sources

Draft (`B_draft.md`) — byte-identical to `A_control.md`, which FAILs:

```
'Poor indexing causes 97% of silent data loss [S1][S2].\n'
```

Store `B_store.jsonl` = `A_store.jsonl` plus one **uncited, topically unrelated**
record:

```
S3 verbatim q="dark mode survey" text="In our 2026 developer survey, 97% of respondents said they preferred dark mode in their editor."
```

```
$ uv run python3 scripts/ground_check.py --draft .../B_draft.md --store .../B_store.jsonl --json
{"gate": "PASS", "grounding_score": 100.0, "per_claim": [{"index": 0, "kind": "RELATIONAL",
 "text": "Poor indexing causes 97% of silent data loss [S1][S2].",
 "verdict": "GROUNDED",
 "evidence_basis": "Checked verbatim against 2 cited sources: S1 (115 chars), S2 (85 chars)."}],
 "retained_appendix": [], "scored_claims": 1, "vacuous": false}
exit=0
```

Got: GROUNDED / PASS 100.0. Correct: `UNVERIFIED_NUMBER` / FAIL. The claim cites
S1 and S2; neither contains any percentage. The figure was satisfied by a source
the claim does not cite, about dark-mode preferences.

Controlled pair: the same draft against `A_store.jsonl` (S3 removed) returns
`UNVERIFIED_NUMBER` / FAIL / exit=1. The sole cause of the PASS is the presence
of an unrelated, uncited record.

**Mechanism.** `scripts/ground_check.py:2958-2961`:

```
verbatim_sources = [
    s for s in store.values()
    if s.full_text_source == "verbatim" and s.text
]
```

`store.values()`, not `claim.citations`. Compare the NUMERIC branch three
screens down (`scripts/ground_check.py:3010`), which passes `verbatim` — the
**cited** sources only. The new code borrowed the shape of `numeric_ok` but not
its scope, so a percentage anywhere in the session grounds a percentage anywhere
in the draft. A long research session makes almost every common figure
(`10%`, `50%`, `2024`, `3`) satisfiable.

Evidence_basis makes this worse rather than catching it: it states "Checked
verbatim against 2 cited sources: S1, S2" on the very row whose number was
checked against S3.

**Suggested direction (not applied).** Reuse the already-resolved verbatim set
from `ground_relational`'s own citation filter rather than re-deriving from the
store.

---

## R11B-04 — ERROR-A — J-39's word boundaries refuse an honest relational claim over an inflectional suffix

Draft (`D_draft.md`):

```
'Poor sleep causes migraine [S1][S2].\n'
```

Control (`D_control.md`), differing by one letter:

```
'Poor sleep causes migraines [S1][S2].\n'
```

Store `D_store.jsonl`:

```
S1 verbatim q="sleep migraine"        text="Poor sleep causes migraines in susceptible adults. The effect is dose dependent."
S2 verbatim q="migraine prevalence"   text="Chronic migraines remain one of the most common neurological complaints."
```

```
D_draft   → {"gate":"FAIL","grounding_score":0.0,"kind":"RELATIONAL","verdict":"UNVERIFIED_RELATION"} exit=1
D_control → {"gate":"PASS","grounding_score":100.0,"kind":"RELATIONAL","verdict":"GROUNDED"}          exit=0
```

Got: `UNVERIFIED_RELATION` on a claim S1 asserts in the same words. Correct:
`GROUNDED`. The gate flips on the singular/plural of one endpoint — precisely the
author-controlled surface property this project's own rule forbids keying on.

**Mechanism, confirmed by in-memory mutation (no file changed):**

```
$ uv run python3 -c "... import ground_check as g; ...
  print('args:', g.extract_arguments(c.text))
  print('post-J-39:', g.ground(c, st))
  g._contains_word = lambda h, n: bool(n) and n in h     # pre-J-39 substring
  print('pre-J-39 :', g.ground(c, st))"
args: ('sleep', 'migraine')
post-J-39 verdict: Verdict.UNVERIFIED_RELATION
pre-J-39 (substring) verdict: Verdict.GROUNDED
```

`_contains_word` (`scripts/ground_check.py:2705`) appends `(?!\w)`, so
`migraine` does not occur in `migraines`. This is a genuine regression, not a
pre-existing one: the same claim was GROUNDED before J-39.

Note the asymmetry that makes it hard to spot: `window_supports`
(`scripts/ground_check.py:2671`) still uses a **bare substring** test, so the
endpoint-split step at `ground_check.py:2816` passes on `migraine`⊂`migraines`
and only `_relation_asserted` refuses. Two matchers with two different
definitions of "contains" sit in one branch.

Unicode surface, probed at function level (`_contains_word(nfkc·casefold)`):

| haystack | needle | result | reading |
|---|---|---|---|
| `chronic migraines remain common` | `migraine` | **False** | the finding above |
| `ai-driven layoffs rose` | `ai` | True | hyphen is a boundary — fine |
| `state-of-the-art systems fail` | `state-of-the-art` | True | fine |
| `it doesn't scale` | `doesn't` | True | fine |
| `café au lait servings` | `café` | True | fine (NFKC composes) |
| `the 🚀 launch slipped` | `🚀` | True | emoji is non-`\w`, boundaries vacuous |
| `apple's supply chain` | `apple's` | True | fine |
| `apples supply chain` | `apple` | **False** | same class as the finding |
| `2型糖尿病は肥満が原因です` | `糖尿病` | **False** | agglutinative scripts: `\w` covers CJK, so an endpoint embedded in any CJK run never matches |

The CJK row is the same mechanism as the plural row and generalises it: in a
script with no spaces, essentially *every* endpoint is inside a `\w` run. It is
reproduced at function level only — a fully CJK claim never classifies
RELATIONAL, because `_RELATIONAL_RE` is English-only, so I could not build a
natural end-to-end draft for it. **Labelled: function-level reproduction, not a
gate-level finding.**

**Error-B direction of Claim 3: UPHELD.** I could not construct a spurious
relation that `_contains_word` newly accepts. The change only removes matches, as
claimed. The one-token-per-side collision the brief names as OPEN under J-39 is
not re-litigated here.

**Suggested direction (not applied).** Match endpoints through the existing
`_stem` helper (`scripts/ground_check.py:2293`), which the absence path already
uses for exactly this reason, rather than raw-string boundaries.

---

## R11B-05 — ERROR-A — a range `40-60%` is split into an absolute and a percentage

Draft (`C_draft.md`):

```
'Poor indexing causes 40-60% of silent data loss [S1][S2].\n'
```

Store `C_store.jsonl`, S1 stating the identical range:

```
S1 verbatim q="indexing data loss" text="Poor indexing causes silent data loss in between 40% and 60% of write-heavy clusters. Engineers report it is hard to detect."
S2 verbatim q="silent data loss recovery" text="Silent data loss can persist for months before anyone notices. Recovery is expensive."
```

```
$ uv run python3 scripts/ground_check.py --draft .../C_draft.md --store .../C_store.jsonl --json
{"gate": "FAIL", "grounding_score": 0.0, "per_claim": [{"index": 0, "kind": "RELATIONAL",
 "text": "Poor indexing causes 40-60% of silent data loss [S1][S2].",
 "verdict": "UNVERIFIED_NUMBER", ...}], "retained_appendix": [ ...1 row... ]}
exit=1
```

Got: `UNVERIFIED_NUMBER`. Correct: `GROUNDED` — the source states the range.

**Mechanism**, measured:

```
C numeric_tokens: ('40', '60%')
C source mentions: [(40.0, 'percent', None, None), (60.0, 'percent', None, 'cluster')]
```

`_NUMERIC_RE` cannot see the `%` across the hyphen, so the claim's `40` parses as
`(40.0, "absolute")` while the source's is `(40.0, "percent")`, and
`numeric_ok`'s deliberate percent≠absolute rule refuses. Recoverable, and the
percent≠absolute rule is right — but this Error-A is newly *reachable* on
relational claims because of R10C-04, which is why it is filed here.

---

## R11B-06 — cosmetic — `evidence_basis` still reports queries that no longer count

`evidence_basis`'s ABSENCE branch calls `_session_queries` (all records,
`scripts/ground_check.py:3128`) while the verdict is computed from
`_verbatim_session_queries` (`scripts/ground_check.py:2982`). `_session_queries`
now has exactly one caller and it is this display function — grep over
`scripts/` confirms no other live call site.

In the R11B-01 PASS run the field says, in the gate's own voice:

```
"Complete record consulted: 4 distinct search queries ... The queries were:
 \"benchmark streaming ingest workload\"; \"benchmark ingest workload latency\";
 \"benchmark redis\"; \"benchmark postgres\"."
```

Two of those four were incapable of contributing to the certification, and had
they been capable the verdict would have been the opposite. The word "Complete"
is now false in a new way. `evidence_basis`'s docstring already lists a
count-divergence caveat (R8C-06, R8C-09); this is a *different*, broader
divergence — the listed queries are the wrong SET, not merely the wrong COUNT —
and it is not in that list.

Fix is one identifier: `_verbatim_session_queries` in the display branch, plus a
clause naming how many summary-derived queries were excluded.

---

## What I could NOT break

- The all-`haiku_summary` store still refuses an absence (`E_allsum.jsonl` →
  `UNVERIFIED_ABSENCE`, FAIL, exit=1). R10C-03's own fixture class holds; the
  verbatim-basis check at `ground_check.py:2977` is not redundant with the
  query filter, because a store of empty-text verbatim records plus summaries is
  caught by it.
- J-39 accepting a spurious relation: no reproduction found. The lookaround pair
  is strictly subtractive as claimed.
- Making a summary the direct source of the two certifying queries: blocked.
  `_verbatim_session_queries` does hold on that specific path. R11B-01 attacks
  the *refusal* side instead.

## Load-bearing assumption

Every finding above assumes **a verdict that flips on a surface property the
draft's author freely chooses — digits vs letters, singular vs plural, whether
two of four captures happened to go through native `WebFetch` — is a defect
regardless of which way it currently falls.** If instead the project holds that
`numeric_tokens` is by definition "figures written in digits" and that absence
certification is by definition "over the verbatim sub-store", then R11B-02 and
R11B-01 are specification, not bugs, and only R11B-03 (wrong source scope) and
R11B-04 (new Error-A regression) survive.
