# R8-A — Red team: J-19 (factive whitelist) and J-20 (contracted negation)

Date: 2026-09-12 · Adversary round 8, lane A · Target: `scripts/ground_check.py`
(`_span_under_nonfactive_complement`, `_FACTIVE_VERBS`, `_NEGATION_TOKENS`,
`_expand_negation_contractions`, `_NEGATION_CONTRACTION_RE`).

**Result: 7 ERROR-B findings, 1 ERROR-A finding.** Every one reproduced on the
live gate; actual JSON pasted below. Scratch fixtures live in
`/private/tmp/claude-501/.../scratchpad/r8a/` (`<name>.draft.md`,
`<name>.store.jsonl`, built by `mk.py`).

Reproduction command for every finding (from `Agent-Assure/`):

```
uv run python scripts/ground_check.py --draft <name>.draft.md --store <name>.store.jsonl --json
```

Every store record is a single `verbatim` source `S1`; every draft is a single
sentence citing `[S1]`. Only the source sentence and the claim sentence differ
between findings, so they are quoted inline rather than as file dumps.

---

## R8A-01 — ERROR-B — J-19 and `_span_is_hedged` are both bypassed by writing a claim of ≥8 tokens

**Mechanism.** `_span_under_nonfactive_complement` and `_span_is_hedged` are
called from exactly one place — `_claim_contained_verbatim` (the exact-containment
path). The ≥`min_quote_len` contiguous-span path in `t1_verbatim` (the `for source
in sources:` loop) applies **neither** guard, so quote-mining is refused only for
claims shorter than 8 tokens and permitted for longer ones.

**Repro (`A01`).**
Source: `Critics argued that the Redis cache silently loses acknowledged writes on restart under default settings.`
Claim: `The Redis cache silently loses acknowledged writes on restart under default settings [S1].`

```json
{"gate": "PASS", "grounding_score": 100.0, "per_claim": [{"evidence_basis": "Checked verbatim against 1 cited source: S1 (105 chars).", "index": 0, "kind": "FACTUAL", "text": "The Redis cache silently loses acknowledged writes on restart under default settings [S1].", "verdict": "GROUNDED"}], "retained_appendix": [], "scored_claims": 1, "vacuous": false}
```

**Length control (`A01ctl`)** — identical shape, claim shortened below the floor:
Source: `Critics argued that Redis loses acknowledged writes on restart.`
Claim: `Redis loses acknowledged writes on restart [S1].`

```json
{"gate": "FAIL", "grounding_score": 0.0, "per_claim": [{"verdict": "UNGROUNDED", ...}], "retained_appendix": [{"verdict": "UNGROUNDED", ...}], "scored_claims": 1}
```

The guard fires at 6 tokens and is silent at 13. Claim length is set entirely by
the draft author — the exact "surface property the author controls" the J-19
design comment says it escaped.

**Honest mirror** (`base`): the same source with the claim retaining its
attribution (`Critics argued that the Redis cache silently loses ... [S1].`)
returns `PASS / GROUNDED`, correctly. So this is a pure false negative on the
violation class, not a symptom of an over-tight tier.

---

## R8A-02 — ERROR-B — the same ≥8-token bypass turns an explicit DENIAL into GROUNDED

**Mechanism.** Same call-site gap as R8A-01, exercised against the denial half of
`_SPAN_HEDGE_TOKENS` rather than the attribution half. This is the round-7
quote-mining finding reopened by length alone.

**Repro (`A02`).**
Source: `It is not true that the Redis cache silently loses acknowledged writes on restart under default settings.`
Claim: `The Redis cache silently loses acknowledged writes on restart under default settings [S1].`

```json
{"gate": "PASS", "grounding_score": 100.0, "per_claim": [{"evidence_basis": "Checked verbatim against 1 cited source: S1 (105 chars).", "index": 0, "kind": "FACTUAL", "text": "The Redis cache silently loses acknowledged writes on restart under default settings [S1].", "verdict": "GROUNDED"}], "retained_appendix": [], "scored_claims": 1, "vacuous": false}
```

The gate asserts the exact opposite of what the cited source says.

---

## R8A-03 — ERROR-B — the factive prefix window is the WHOLE document, so one factive verb anywhere licenses every later non-factive complement

**Mechanism.** `prefix = source_tokens[:start - 1]` is unbounded to the left;
`return not any(tok in _FACTIVE_VERBS for tok in prefix)` therefore asks "does
this document contain a factive verb *anywhere* before the complementizer", not
"is this complement governed by a factive verb".

**Repro (`A03`).**
Source: `Our benchmark showed that the cluster stayed stable. A blogger speculated that Redis loses data.`
Claim: `Redis loses data [S1].`

```json
{"gate": "PASS", "grounding_score": 100.0, "per_claim": [{"evidence_basis": "Checked verbatim against 1 cited source: S1 (96 chars).", "index": 0, "kind": "FACTUAL", "text": "Redis loses data [S1].", "verdict": "GROUNDED"}], "retained_appendix": [], "scored_claims": 1, "vacuous": false}
```

**Control (`A03c`)** — delete the unrelated first sentence and nothing else:
Source: `A blogger speculated that Redis loses data.`

```json
{"gate": "FAIL", "grounding_score": 0.0, "per_claim": [{"verdict": "UNGROUNDED", ...}], "retained_appendix": [{"verdict": "UNGROUNDED", ...}]}
```

One unrelated sentence of the *source* — not the claim — flips the verdict. Any
real retrieved page of more than a paragraph will contain `shows`, `found`,
`revealed` or `confirmed` somewhere, so on real evidence J-19's whitelist is
satisfied by default.

**Nested instance (`F_nested`)**, same root cause, the shape named in the brief:
Source: `Smith showed that one blogger posits that Redis loses acknowledged data.`
Claim: `Redis loses acknowledged data [S1].`

```json
{"gate": "PASS", "grounding_score": 100.0, "per_claim": [{"evidence_basis": "Checked verbatim against 1 cited source: S1 (72 chars).", "index": 0, "kind": "FACTUAL", "text": "Redis loses acknowledged data [S1].", "verdict": "GROUNDED"}], "retained_appendix": [], "scored_claims": 1, "vacuous": false}
```

`showed` governs the outer clause; the span sits under `posits` in the inner one.
The whitelist reads the outer verb and endorses the inner complement.

**Honest mirror** (`mirror_est`): `Researchers have established that Redis loses
acknowledged data.` → `PASS / GROUNDED`, correct.

---

## R8A-04 — ERROR-B — nouns homographic with whitelisted verbs satisfy the factive test

**Mechanism.** The whitelist is matched on bare token identity with no
positional or part-of-speech constraint, and `documents`, `measures`, `finds`,
`shows`, `proves` are ordinary English nouns.

**Repro (`A04`).**
Source: `Internal documents circulated widely. One blogger posits that Redis loses data.`
Claim: `Redis loses data [S1].`

```json
{"gate": "PASS", "grounding_score": 100.0, "per_claim": [{"evidence_basis": "Checked verbatim against 1 cited source: S1 (79 chars).", "index": 0, "kind": "FACTUAL", "text": "Redis loses data [S1].", "verdict": "GROUNDED"}], "retained_appendix": [], "scored_claims": 1, "vacuous": false}
```

**Second instance (`A05`).** Source: `Security measures were tightened. One
blogger posits that Redis loses data.` → identical `PASS / GROUNDED` output.

No verb in either source is factive. The gate grounded the complement of
`posits` because the document mentioned paperwork, and because it mentioned
precautions.

---

## R8A-05 — ERROR-B — the negation conjunct is a 6-token blacklist; `failed to`, `unable to`, `nobody`, `declined to` walk through a whitelisted factive verb

**Mechanism.** `_NEGATION_TOKENS = {not, no, never, nor, neither, without}`.
English expresses the same negation lexically (`failed`, `unable`, `nobody`,
`declined`, `refused`, `stops short of`), and those frames combine with a
whitelisted factive verb to produce an explicit *non*-endorsement that J-19 reads
as endorsement. Four independent reproductions, all `Claim: Redis loses
acknowledged data [S1].`:

| Source sentence | gate | verdict |
|---|---|---|
| `The team failed to show that Redis loses acknowledged data.` | PASS | GROUNDED |
| `Researchers were unable to demonstrate that Redis loses acknowledged data.` | PASS | GROUNDED |
| `Nobody has established that Redis loses acknowledged data.` | PASS | GROUNDED |
| `The lab declined to confirm that Redis loses acknowledged data.` | PASS | GROUNDED |
| `No one has established that Redis loses acknowledged data.` | FAIL | UNGROUNDED |

The last row is the diagnostic: `No one` fails and `Nobody` passes, on the same
proposition, because the blacklist happens to contain the token `no`. Full JSON
for two of them:

```json
# F_failedto
{"gate": "PASS", "grounding_score": 100.0, "per_claim": [{"evidence_basis": "Checked verbatim against 1 cited source: S1 (59 chars).", "index": 0, "kind": "FACTUAL", "text": "Redis loses acknowledged data [S1].", "verdict": "GROUNDED"}], "retained_appendix": [], "scored_claims": 1, "vacuous": false}

# F_nobody
{"gate": "PASS", "grounding_score": 100.0, "per_claim": [{"evidence_basis": "Checked verbatim against 1 cited source: S1 (58 chars).", "index": 0, "kind": "FACTUAL", "text": "Redis loses acknowledged data [S1].", "verdict": "GROUNDED"}], "retained_appendix": [], "scored_claims": 1, "vacuous": false}
```

**Honest mirror** (`mirror_show`): `The team did show that Redis loses
acknowledged data.` → `PASS / GROUNDED`, correct. The gate cannot tell `did
show` from `failed to show`.

---

## R8A-06 — ERROR-B — J-20 covers two apostrophes; four more hide the negation and invert the verdict

**Mechanism.** `_NEGATION_CONTRACTION_RE = r"n['’]t\b"` enumerates U+0027 and
U+2019. NFKC folds U+FF07 into U+0027 (so that one is covered for free) but
leaves U+2018, U+02BC, U+02B9 and U+05F3 alone. U+02BC/U+02B9 are `\w`, so
`doesnʼt` survives as one token; U+2018 is not `\w`, so `doesn‘t` splits into
`doesn` + `t` — the exact pre-J-20 failure. Either way the token `not` never
appears and `_span_is_hedged` sees an unhedged span.

One source shape, seven apostrophes, claim constant
(`Redis loses acknowledged data [S1].`):

| Source: `The audit doesnXt show Redis loses acknowledged data.` | gate | verdict |
|---|---|---|
| X = U+0027 `'` | FAIL | UNGROUNDED |
| X = U+2019 `’` | FAIL | UNGROUNDED |
| X = U+FF07 `＇` | FAIL | UNGROUNDED |
| X = U+2018 `‘` | **PASS** | **GROUNDED** |
| X = U+02BC `ʼ` | **PASS** | **GROUNDED** |
| X = U+02B9 `ʹ` | **PASS** | **GROUNDED** |
| X = U+05F3 `׳` | **PASS** | **GROUNDED** |

```json
# F_u2018 — source "The audit doesn‘t show Redis loses acknowledged data."
{"gate": "PASS", "grounding_score": 100.0, "per_claim": [{"evidence_basis": "Checked verbatim against 1 cited source: S1 (53 chars).", "index": 0, "kind": "FACTUAL", "text": "Redis loses acknowledged data [S1].", "verdict": "GROUNDED"}], "retained_appendix": [], "scored_claims": 1, "vacuous": false}
```

U+2018 is not exotic: it is the left single quotation mark that word processors
and CMSes emit, and it appears in captured web text without anyone attacking.
The J-20 comment's claim — "BOTH APOSTROPHES … both are matched explicitly" —
assumes the class has two members. It has at least seven.

**Honest mirror** (`mirror6`): `The audit does show Redis loses acknowledged
data.` → `PASS / GROUNDED`, correct. The four passing rows above therefore
assert the opposite of their source.

---

## R8A-07 — ERROR-B — zero-complementizer and `how`-complement frames ground unhedged (confirmed open, as J-19's comment states)

**Mechanism.** `_COMPLEMENTIZERS = {"that"}`, so a complement introduced by
nothing at all, or by `how`, never reaches the factivity test; if the reporting
verb is also outside `_SPAN_HEDGE_TOKENS`, nothing refuses. Claim constant
(`Redis loses acknowledged data [S1].`):

| Source | gate | verdict |
|---|---|---|
| `One blogger posits Redis loses acknowledged data.` (`zeroComp`) | PASS | GROUNDED |
| `One blogger theorised how Redis loses acknowledged data.` (`howComp`) | PASS | GROUNDED |

Listed for completeness and severity accounting, not as a surprise: the J-19
design comment explicitly scopes the fix to the `that`-complement family and
declares the zero-complementizer case open. It is reported here because the
verdict is still a wrongful `PASS` on a non-endorsing source, and because R8A-03
and R8A-04 show that the `that`-family it *did* claim is also not closed.

---

## R8A-08 — ERROR-A — contracted `can't` no longer matches an uncontracted `cannot` source

**Mechanism.** `_expand_negation_contractions` rewrites `can't` to `ca not`
(deliberately, per the design comment), but `cannot` contains no `n't` and stays
`cannot`. The two spellings of the same word therefore tokenize differently and
an otherwise verbatim claim fails.

**Repro (`refuted_cannot`).**
Source: `Our benchmark showed that the cluster cannot lose acknowledged writes on restart under sustained load.`
Claim: `The cluster can't lose acknowledged writes on restart under sustained load [S1].` → `FAIL / UNGROUNDED`

**Honest mirror (`refuted_cannot_mirror`).** Same source, claim spelled
`cannot` → `PASS / GROUNDED`.

The comment argues the irregular expansion is safe because "claim and source
pass through the same function". That holds for `can't`/`can't`, not for
`can't`/`cannot`, which is the common real pairing. Recoverable, low priority
relative to the seven above.

---

## ATTACKS THAT FAILED

Each of these was built, run, and did **not** reproduce. Listed so the next
round does not re-spend the budget.

1. **Passive attribution — `It was argued that P`** → `FAIL / UNGROUNDED`.
   `argued` is in `_SPAN_HEDGE_TOKENS` and inside the 5-token lookback, so the
   older blacklist catches it before J-19 is consulted.
2. **Nominalised attribution — `The claim that P was widely repeated`** →
   `FAIL / UNGROUNDED`. `claim` is a hedge token.
3. **Counterfactual factive — `A replication would have proven that P`** →
   `FAIL / UNGROUNDED`. Not because `would have proven` is understood, but
   because `would` is a hedge token in the lookback window. The negation
   blacklist itself does not contain a counterfactual marker — this passes only
   by luck of the older rule, and a counterfactual phrased without `would`
   (`a replication ought to have proven that P`) should be retested.
4. **`No one has established that P`** → `FAIL / UNGROUNDED`. The tokenizer
   splits it and `no` is in `_NEGATION_TOKENS`. The `Nobody` spelling is R8A-05.
5. **U+FF07 fullwidth apostrophe** → `FAIL / UNGROUNDED`. NFKC folds it to
   U+0027 before `_NEGATION_CONTRACTION_RE` runs, so J-20's ordering
   (`_expand_negation_contractions(_nfkc(text))`) is correct here. The four
   apostrophes in R8A-06 are the ones NFKC does not touch.
6. **U+2019 curly apostrophe** → `FAIL / UNGROUNDED`. J-20's explicit second
   alternative works as designed.
7. **Creating a FALSE negation by expansion.** `_NEGATION_CONTRACTION_RE` has no
   left word boundary, so I looked for a non-contraction ending in `n't` that
   would inject a spurious `not` into the absence-contradiction check at
   `ground_check.py:2114` (where a negation in the body *suppresses* the
   contradiction and so points toward `ABSENCE_SUPPORTED`). I could not
   construct a natural English or transliterated string ending in `n't` that is
   not already a negation. Hypothesis not refuted in principle, but no
   reproduction — do not treat it as closed.
8. **Hiding a negation in an absence source body** (U+02BC inside the body at
   the same 2114 site) points the wrong way for an attacker: suppressing the
   negation makes the body read as an affirmative mention, the contradiction
   fires, and the verdict moves to `UNVERIFIED_ABSENCE`. Fail-closed; no finding.
9. **Breaking an ≥8-token span with an `n't` expansion** to let a fabrication
   match. Expansion is applied symmetrically to claim and source by `_tokenize`,
   so no asymmetry is available except the `cannot`/`can't` spelling difference,
   which is R8A-08 and points to refusal, not to a wrongful pass.

---

## Load-bearing assumption

These reproductions all use a single-sentence draft and a single-source store,
so `grounding_score` is 100.0 and the gate verdict is decided by one claim. The
finding being asserted is about the **per-claim verdict** (`GROUNDED` where the
source does not assert the claim); the `gate: PASS` follows from ADR-005's rule
that an empty retained appendix plus a passing score is a PASS. If any of these
claims appeared alongside other claims that failed, the gate would be `FAIL`
while the fabricated claim still read `GROUNDED` — the Error-B is in the verdict,
and the gate result is its consequence in the single-claim case.

## Recommendation

The single highest-value fix is **R8A-01**: move the `_span_is_hedged` /
`_span_under_nonfactive_complement` pair into the ≥`min_quote_len` span path as
well as the exact-containment path. Without it, R8A-03 through R8A-07 are
academic — an attacker does not need any of them, only a longer sentence. It is
also a fail-closed change (it can only move claims away from PASS), so on the
2026-08-30 unratified reading of escalation rule #1 it sits inside agent
authority; the J-19 rewrite implied by R8A-03/04/05 (bounding the prefix window,
part-of-speech constraint, negation as an open class) does not, because any
whitelist widening is PASS-enabling.
