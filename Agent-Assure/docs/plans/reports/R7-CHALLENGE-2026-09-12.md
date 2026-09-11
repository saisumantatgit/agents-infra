# R7 CHALLENGE — adversarial review of RED-TEAM-R7-2026-09-12.md

Reviewer: independent adversarial agent, 2026-09-12. The conclusion under review was
committed (`54502e5`) before this review began, so nothing here could be absorbed into it.
No repo file was modified except this one. All experiments ran in the session scratchpad
against the committed tree.

**Summary:** 2 CONFIRMED, 3 OVERSTATED, 1 WRONG. The WRONG one is claim 3, and it is the
report's central recommendation.

| # | Claim | Verdict |
|---|---|---|
| 1 | OI-MOAT-26 is fixed and fail-closed | **OVERSTATED** — fixed, but not fail-closed; two FAIL→PASS inputs, one of which composes with OI-MOAT-29 |
| 2 | Propagation moves no Error-B; the hole is T1 set-membership | **CONFIRMED** — I could not break it, and I say so explicitly |
| 3 | Attack and honest case are syntactically identical; no deterministic rule separates them | **WRONG** — verb factivity separates them, and the report's own recommendation is dominated |
| 4 | 22 wrongful PASSes over 11 mechanisms | **OVERSTATED** — total arithmetic holds; "found 22 and closed 2 … other 20" does not; one counted PASS is not a PASS |
| 5 | 494 / 2 / 21 and corpus byte-identical | **CONFIRMED** — reproduced exactly |
| 6 | The 10 new strict xfails assert their named property | **OVERSTATED** — 9 of 10 are sound; OI-MOAT-29's test mis-asserts and would XPASS with the hole open |

---

## Claim 1 — "OI-MOAT-26 is fixed and fail-closed." → OVERSTATED

**The fix works on its own attack.** Reproduced:

```
draft   The appliance ships with ＜！－－at most one, and never with－－＞ dual power supplies [S6].
verdict FAIL 0.0 — both clauses UNGROUNDED, both retained
```
`a1.md` and `a7.md` (the whole-sentence full-width and small-form variants) also now
`FAIL 33.3`. D-24's behavioural claim is real.

**But "fail-closed" is false as stated.** Stripping BEFORE NFKC removes *more* text than
stripping after whenever a full-width `-->` lookalike sits **inside** a genuine ASCII
comment: the lookalike used to fold into a real closer and terminate the non-greedy match
early, so the tail was scored. It no longer does, so the whole span is deleted.

```
draft (t2.md)
  Redis handles 100K ops per second in our benchmark [S1].

  <!-- reviewer note －－＞ PostgreSQL corrupts every write-ahead log segment and
       loses all committed data on restart [S1]. -->

PRE-FIX  judged text : '… [S1].\n\n  PostgreSQL corrupts … on restart [S1]. -->\n'   → FAIL
POST-FIX judged text : '… [S1].\n\n \n'                                              → PASS 100.0
```

For *this* input the new behaviour is nonetheless **correct**, and the right justification
is not "fail-closed" but **renderer-faithfulness**: a Markdown/HTML renderer terminates the
comment at the first ASCII `-->` and hides exactly what `_strip_html_comments` now deletes.
Post-fix, the gate's deletion is provably ⊆ what the renderer hides (equal for well-formed
pairs, strictly smaller for unterminated openers, which the gate deliberately keeps). That
is a *stronger* and *checkable* invariant than "fail-closed" — and it is the one the
docstring should assert, because "fail-closed" is falsifiable by the case above.

### The OI-MOAT-29 interaction the report misses

The renderer-faithfulness invariant has a precondition the report never states: **that a
well-formed ASCII `<!-- … -->` pair in the raw text really is a comment to the renderer.**
OI-MOAT-29 is precisely the case where it is not — a `<!--` inside an inline code span is
rendered visibly. The two holes compose, and the fix makes OI-MOAT-29 strictly worse:

```
draft (x29.md)
  Redis handles 100K ops per second in our benchmark [S1].

  ## TODO `<!--`

  PostgreSQL corrupts every write-ahead log segment and loses all committed data [S1].

  End of note －－＞

  MongoDB silently drops every index on restart [S1].

  <!-- reviewer note -->

PRE-FIX  judged : '… [S1].\n\n## TODO ` \n\nMongoDB silently drops every index on restart [S1].\n\n \n'
                  → FAIL   (the MongoDB fabrication was still scored)
POST-FIX judged : '… [S1].\n\n## TODO ` \n'
                  → PASS 100.0   (it is gone)
```

Every line of that draft is reader-visible. Pre-fix, the full-width lookalike accidentally
terminated the stray opener's span and limited the damage; post-fix it does not, so the
deletion runs on to the genuine `-->` and swallows a second fabricated sentence. The
attacker loses nothing by this (he controls whether the lookalike is there at all), so the
practical Error-B surface is unchanged — but the register's flat "Fail-closed after the fix"
is contradicted by an input that moves FAIL→PASS on reader-visible prose.

**Recommended correction (wording, not code):** amend D-24 and the `_iter_raw_sentences`
docstring to claim *renderer-faithfulness*, and record that it holds **only while
OI-MOAT-29 is open as a conditional** — a stray opener in visible prose breaks the premise
that a well-formed pair is a comment, and the reorder widens that hole's blast radius.
The code change itself should stand. Not an escalation: no new attacker capability.

---

## Claim 2 — "Propagation moves no Error-B; the hole is T1's set-membership residual coverage." → CONFIRMED

**I tried to break this and could not. Stating that explicitly, as instructed.**

The report's §5 argument is structurally sound and I verified it independently rather than
on testimony. `_propagate_sentence_citation` returns `f"{left} {marker}"` and
`_propagate_across_semicolon` returns `f"{body.rstrip(';').rstrip()} {marker}"` — both
append at the end, which is exactly where an author places a marker, and every downstream
path strips markers before tokenizing. Differential runs (store `store_r7.jsonl`):

| draft | gate | per-claim |
|---|---|---|
| `… with AOF persistence; the cluster was tested for three hours [S1].` | PASS | NUMERIC:GROUNDED ; FACTUAL:GROUNDED |
| `… with AOF persistence [S1].` (direct) | PASS | NUMERIC:GROUNDED |
| `… with AOF persistence [S1]` (direct, no terminal period) | PASS | NUMERIC:GROUNDED |
| `## MongoDB lost all data; the appliance ships with dual power supplies [S2].` | FAIL | FACTUAL:UNGROUNDED |
| `## MongoDB lost all data [S2].` (direct) | FAIL | FACTUAL:UNGROUNDED |
| `MongoDB lost all data; … [S99].` | FAIL | UNVERIFIED_CITATION |
| `MongoDB lost all data [S99].` (direct) | FAIL | UNVERIFIED_CITATION |

Families I tried beyond the report's: (a) trailing-punctuation dependence — propagation
emits a claim with no terminal punctuation, so I checked whether `_header_asserts`'
`content[:-1]` or any classifier reads the final character; it does not move a verdict;
(b) marker-position dependence in `_header_asserts` / `_is_non_claim`; (c) fabricated
source id through propagation, in case `resolve` treated an inherited marker differently;
(d) whether the appended marker changes `_conjunction_split`'s split points (it cannot —
`"; "` / `" and "` are interior). None diverged.

**One apparent divergence, and it is not one.** `It is not; the appliance ships with dual
power supplies [S2].` → PASS, while `It is not [S2].` → NEEDS_WORK. That is vacuity, not
propagation: the second draft has `scored_claims: 0, vacuous: true`. Adding any grounded
claim to the direct draft restores PASS —
`The appliance ships with dual power supplies [S2]. It is not [S2].` → **PASS 100.0**.
Identical to the propagated form. The control holds.

The redirect to T1 residual coverage is therefore correct, and the report's own framing —
that being *refuted* on the recorded prediction was worth more than being right — is the
strongest methodological move in the document. It should be kept.

---

## Claim 3 — "The attack and the honest case are syntactically identical, so no deterministic rule separates them." → **WRONG**

This is the load-bearing sentence of the report's headline recommendation, and it rests on
a misdiagnosis of which word carries the difference.

The report says the pair differs only in "whether the author endorses the **attributing
subject** — *Critics* versus *our own benchmark* — and that is a semantic judgment about
stance." That is not where the difference lives. **It lives in the verb.**

- `argue` is **non-factive**: *X argued that P* does **not** entail P.
- `show` is **factive**: *X has shown that P* **does** entail P, irrespective of who X is.

Factivity is a lexical property of a closed verb class, read directly off the token
sequence. It is not a stance judgment and it is not semantic in any sense the gate cannot
compute. I implemented the discriminator (~25 lines, pure, no model) and ran it on the
report's exact pair plus the decisive subject-swap control:

```
REFUSE   Critics have argued for many years now that Redis loses data on restart.        (S3, attack)
GROUND   Our own benchmark has shown repeatedly over the past year that Redis loses …    (S4, honest)
GROUND   Critics have shown repeatedly over the past year that Redis loses data on …     (subject swapped)
REFUSE   Our own benchmark has argued for many years now that Redis loses data on …      (subject swapped)
REFUSE   Sceptics maintain that the scheduler starves low-priority jobs.                 (C-9, 'maintain')
REFUSE   Several vendors posit that the firewall blocks all zero-day exploits.           ('posit')
```

Rows 3 and 4 are the proof: **swap the subjects and the endorsement follows the verb, not
the subject.** The report's stated reason for the impossibility is therefore false, and the
impossibility with it.

### Why this is not the open-class failure the report is right to fear

The report correctly rejects "a longer `_SPAN_HEDGE_TOKENS` list" because a blacklist over
an open class fails open — the attacker picks an unlisted verb. Factivity inverts the
polarity: it is a **whitelist**, and an unlisted verb **refuses**. `maintain`, `posit`,
`insist`, `hold`, `so-called` all refuse without ever being enumerated (rows 5 and 6 above,
neither verb listed anywhere).

And it satisfies CLAUDE.md's actual requirement — *a property the attacker cannot set
without giving up the attack*. To get a span grounded, the attacker must put a factive verb
in the source; a factive verb means **the source asserts the claim**, at which point
grounding it is correct behaviour. The gate certifies source-support, not truth. The
attacker's only escape is to stop quote-mining.

### The report's own recommendation is strictly dominated, and it under-delivers

Recommended rule: *refuse containment grounding for any span embedded in a `that`-complement
of a reporting verb, regardless of who is reporting.*

1. **Error-A.** The whitelist refuses a strict subset of what the report's rule refuses
   (it additionally grounds the factive cases), so it closes at least as much Error-B at
   strictly lower Error-A. The report's own M-1 honest mirror survives the whitelist and
   dies under the report's rule — the report says so itself and calls it "the price". The
   price is avoidable.
2. **Coverage.** The report's rule is scoped to `that`-complements, and **3 of its own 5
   tripwired MINED params have no `that` at all**:

   | param | source | has `that`? |
   |---|---|---|
   | c1 hedge-beyond-lookback | `Critics have argued … that Redis loses data …` (S3) | yes |
   | c2 verb-not-in-list | `Sceptics maintain that the scheduler …` (S5) | yes |
   | **c3 cyrillic-confusable** | `The vendor сlaims the array rebuilds …` (S6) | **no** |
   | **c5 hedge-after-the-span** | `The proxy terminates TLS at the edge, which is simply not the case …` (S7) | **no** |
   | c4 hedge-by-structure | `Imagine for a moment that the gateway …` (S8) | yes |

   Adopting the headline recommendation would leave c3 and c5 — and C-2, C-4, C-6 from the
   Path C report — open, while the summary presents it as closing the class. Note the Path C
   agent proposed a *broader* rule ("the span must begin a source sentence that ends in a
   full stop") which does kill C-2/C-3/C-5/C-6/C-7; the summary silently narrowed it to the
   `that`-complement form and inherited a coverage gap it does not disclose.

### Honest limits of my own proposal — stated so it can be attacked in turn

- **Negation scopes over the factive verb.** `Critics haven't shown that Redis is slow`
  (store_contraction S2) is a negated factive: the whitelist alone would ground it. The rule
  must be conjoined with a negation check on the embedding clause — which in turn needs
  OI-MOAT-25's tokenizer repair, since `haven't` currently tokenizes to `['haven','t']`.
  The two fixes compose; neither is sufficient alone.
- **Outer non-factive over inner factive.** `The brochure claims to have demonstrated that P`
  defeats a naive nearest-verb implementation. Conjoining the whitelist with the existing
  blacklist over the full pre-span clause handles the listed cases; an unlisted outer
  non-factive is a residual, and it costs the attacker real syntactic awkwardness.
- This is a **sketch with a working prototype**, not a calibrated rule. Any adoption must be
  measured on the n=52 gold set before it ships, per the repo's own discipline.

**Required correction to the report.** Strike "they are syntactically identical" and "no
deterministic rule separates them" — the pair is separable by a lexical property of a
closed class, demonstrated above. The escalation to Sai should stand, but the question put
to him must change: it is no longer *"accept this Error-A or leave the class open"*, it is
*"calibrate a factive whitelist (+ negation conjunct) and measure it"* — a materially
cheaper decision with a materially smaller Error-A bill, and one that no longer needs to be
framed as paying for an impossibility that does not exist.

---

## Claim 4 — "22 wrongful PASSes over 11 mechanisms." → OVERSTATED

**The headline arithmetic is right.** Path A 7 + Path B 2 + Path C 13 = **22**;
mechanisms 5 + 1 + 5 = **11**. Both add up against the three agent reports.

**No double-counting found.** The specific suspicion in the brief — that Path B's
quote-mining PASS (`b7.md`, §"Families tried" row 9) is also in Path C's 13 — does not hold.
Path B explicitly excludes it from its count of 2 and hands it to Path A; Path C's 13 are
C-1…C-13 on `storeC/D/E`, none of which is `storeQM`. If anything `b7` is an **undercount**:
it is a confirmed PASS counted in no path's total, so the true figure is 23.

**Three real defects in the counting, all downstream of the headline:**

1. **"Round 7 found 22 and closed 2. The other 20 are tripwired"** is wrong twice.
   The two *decisions* were D-24 and D-25, but D-25 (a `SyntaxWarning`) closed **zero**
   wrongful PASSes, and D-24 (OI-MOAT-26) closed **three** of the 22 — Path A findings 1a
   (`a1.md`), 1b (`a7.md`) and 1c (`a6.md`), all three of which I re-ran and confirmed now
   FAIL. So: 22 found, **3 closed, 19 open** — not 2 and 20. The sentence conflates a count
   of decisions with a count of findings.
2. **"Tripwired" is true at class level, not instance level.** The 19 open PASSes are
   covered by 12 xfail instances across 7 OI numbers. That is honest coverage of the
   *classes*, but "the other 20 are tripwired" reads as a per-finding guarantee it is not.
3. **One counted PASS is not a PASS.** Path A finding 5 states: *"Also confirmed uncited
   (`a3.md`, 'This is not so.' → `NON_CLAIM`, gate PASS)."* Re-run against the same store:

   ```
   {"gate": "NEEDS_WORK", "grounding_score": 100.0, "scored_claims": 0, "vacuous": true}
   ```

   **NEEDS_WORK, not PASS** — the vacuity guard catches it. This does not move the 22
   (the Path A header counts 7 drafts and `a3` is the eighth, excluded), but it is a
   factual error in a finding body, and rounds 3 and 4 each carried one non-reproducing
   finding — this is round 7's.

**On the definition.** Judged strictly as *gate == PASS with an unsupported claim*, the
softest of the 22 is Path A finding 5 (`a5.md`, `It is not [S1].` → NON_CLAIM, gate PASS).
The report concedes the underlying rule "is sound as written"; the gate PASS is caused by a
low-content span leaving the denominator, not by a fabrication being certified. Counting it
alongside 1c (which certified the *negation* of the source and printed the rewritten
sentence back as the author's) flattens a two-order severity difference. The report says so
in prose and then counts them as equals.

**Recommended correction:** replace "found 22 and closed 2 … the other 20" with
"found 22 (23 including the uncounted `b7`); **3 closed by D-24**, 19 open, covered by
12 tripwire assertions over 7 classes", and correct `a3`'s verdict in the Path A report.
This *raises* the report's own close-rate, so the error was not in the flattering direction.

---

## Claim 5 — "494 passed / 2 skipped / 21 xfailed, corpus byte-identical." → CONFIRMED

Both reproduced by me on the committed tree.

```
$ uv run pytest -q
494 passed, 2 skipped, 21 xfailed in 30.24s

$ uv run python -m calibration.build_corpus_v2
52 claims written to calibration/feature_rows-v2.jsonl and calibration/labeling-v2.csv
$ git diff --stat
$ git status --porcelain
(both empty)
```

Exact match, and the empty `git status --porcelain` is the stronger check — it confirms the
generator also left `labels-v2.csv` (AUTHORED) untouched, which the diff-stat alone would
not distinguish from "not regenerated". CR-004's rates stand and no new CR is due.

The 21 decompose correctly: 9 pre-round-7, + 2 from `test_moat_r7_contracted_hedge.py`
(landed in `1aedf79`, giving the 11 quoted in `aad2ee1`'s message), + 10 from
`test_moat_r7_open.py` (`d07fba8`). All strict, so any of them silently starting to pass
fails the suite.

---

## Claim 6 — "the 10 new strict xfails assert the property their names claim." → OVERSTATED

Nine of ten are sound. **One is mis-asserting and would XPASS with its hole fully open.**

### The defect: `test_stray_comment_opener_must_not_swallow_prose` (OI-MOAT-29)

```python
texts = " ".join(c["text"] for c in _gate(tmp_path, draft)["per_claim"])
assert "MongoDB" in texts, (
    "the MongoDB sentence vanished from the report entirely — it was never "
    "scored, so it could never be flagged")
```

The stated property is *"it was never **scored**"*. The assertion tests *appears anywhere
in `per_claim`*, which **includes `NON_CLAIM` rows** — spans that are explicitly excluded
from the denominator and can never be flagged. The two are not the same, and the gap is
reachable: `### MongoDB lost all data` produces

```json
{"per_claim": [{"kind": "NON_CLAIM", "text": "### MongoDB lost all data", "verdict": "GROUNDED"}],
 "scored_claims": 0, "vacuous": true}
```

— `"MongoDB" in texts` is satisfied while `scored_claims` is 0. So a partial repair that
merely stops *deleting* the sentence, without restoring it to the denominator, flips this
test to XPASS and reports OI-MOAT-29 closed while the Error-B stands. The file's own two
sibling tests get this right by using `_scored(...)`; this one does not.

**Fix:** `assert any("MongoDB" in c["text"] for c in _scored(report))`. One line, and it
makes the assertion match the reason string. This is the round's own recorded law applied
to its own tripwire — *every "I don't know" must point AWAY from PASS*; here an ambiguous
assertion points away from XFAIL.

### The other nine — sound

- `test_mined_span_must_not_ground` (×5, OI-MOAT-27) and
  `test_inverted_modifier_must_not_ground` (OI-MOAT-28) assert `verdict != "GROUNDED"` on
  the single scored claim, with `_only_verdict` asserting exactly one scored claim first.
  Not tautological: the property is the verdict, and it XPASSes iff the hole closes.
  `!= "GROUNDED"` rather than `== "UNGROUNDED"` is the right width — any of the
  violation-class verdicts is a legitimate close.
- `test_line_under_unpunctuated_header_is_still_scored` (OI-MOAT-30),
  `test_header_assertion_is_not_keyed_on_spelling` (OI-MOAT-31) and
  `test_cited_zero_content_span_stays_scored` (OI-MOAT-32) use `_scored(...)`, which is the
  correct predicate for a "left the denominator" hole.
- The 2 contracted-denial xfails (OI-MOAT-25) assert `!= "GROUNDED"` on the single scored
  claim. Sound.

### The controls — they do control something

| control | asserts | does it control? |
|---|---|---|
| `test_honest_attribution_still_grounds` | S4 → `GROUNDED` | **Yes** — the binding constraint on any OI-MOAT-27 repair, and it is *satisfiable together with* closing the hole (my claim-3 prototype does exactly that), so it is a live constraint and not a blocker |
| `test_header_assertion_with_trailing_s_subject_is_scored` | `### Redis lost all data` is scored | **Yes** — establishes the OI-MOAT-31 asymmetry is spelling, not a guess. Without it the xfail proves nothing |
| `test_uncontracted_denial_does_not_ground` (×2) | S3/S4 → `!= GROUNDED` | **Yes, non-trivially** — I re-ran both: `FAIL 0.0 / UNGROUNDED`, one scored claim each. They are not passing because the claim fails to match |
| `test_honest_short_quote_still_grounds` | S5 → `GROUNDED` | **Yes** — pins OI-T2-01 so the OI-MOAT-25 repair cannot be "refuse short quotes" |

One residual worth recording: `test_honest_attribution_still_grounds` is a **single-point**
mirror. It pins one honest sentence. A repair that grounds S4 and wrongly rejects every
other honest attributed quotation passes it. If the factive-whitelist route is taken, the
mirror needs to become a parametrized set before the Error-A claim is credible.

---

## What this review does not dispute

- The methodological core: predicting before the round, recording the prediction, and
  reporting the refutation as the finding. Claim 2 is the strongest part of the document.
- The decision **not** to ship eleven narrow rules overnight. The round-1/2/3 record cited
  supports it, and "an open hole with a tripwire is honest; a closed fixture with an open
  class is not" is correct.
- That Alpha criterion #7 is **not** satisfied and round 8 is owed. Claim 3 makes this more
  true, not less: the recommendation now needs a calibration pass before it can even be
  ruled on.

## Load-bearing assumption of THIS review

That the gate certifies **source-support, not truth** — i.e. that a source asserting P in
its own voice makes grounding P correct even when P is false in the world. Every dominance
argument in claim 3 rests on it. It is consistent with the repo's stated taxonomy
(`GROUNDED` = supported by cited evidence) and with the report's own honest mirror M-1, but
if the project ever intends the gate to police source *reliability*, the factive whitelist
grounds claims from unreliable sources and the argument weakens.
