# CHALLENGE — "Demote T2 to corroborating" (2026-09-02)

**Stance:** adversarial. Task was to REFUTE the three-part conclusion that T2 must
be demoted from SUFFICIENT to corroborating.

**Verdict summary:** (a) UPHELD, (b) REFUTED on the number, (c) **REFUTED — the
load-bearing premise of claim 1 is false**, (d) REFUTED as a concern (nothing
concrete breaks), (e) UPHELD, and a second overclaim found on the same page.

All numbers below were re-derived by running `scripts/calibrate.py`'s own
`error_rates` / `loo_operating_point` over `calibration/labels-v2.csv` +
`calibration/labeling-v2.csv` (n=52 gold, 25 grounded / 27 violation). No
repository file other than this report was modified; `ground_check.py` untouched.
Variants were measured by monkeypatching `t2_lexical` in a throwaway pytest
plugin outside the repo.

---

## (a) The 5-row population — **UPHELD**

Re-derived independently. Of 52 gold rows, `predicted_verdict == GROUNDED` with
`t1_verbatim == False` among the lex_tau-governed kinds (FACTUAL / ATTRIBUTION /
NUMERIC) is **exactly 5**:

| id | kind | t2_f1 | gold |
|---|---|---|---|
| q05 | NUMERIC | 0.762 | grounded |
| q08 | NUMERIC | 0.824 | grounded |
| q09 | FACTUAL | 0.857 | grounded |
| q35 | FACTUAL | 0.889 | grounded |
| **q46** | NUMERIC | **0.857** | **violation** |

Kind-gating is correct, and I checked it at the source rather than by trusting
the tag: `lex_tau` occurs in exactly one comparison in the whole gate —
`ground_check.py:923`, inside `t2_lexical`. `check_absence` and
`ground_relational` do not take a `lex_tau` parameter at all, and
`window_supports` (the relational tier's matcher, line 1740) is a **substring**
test with no threshold. So no ABSENCE or RELATIONAL row can be T2-decided. q12
and q36 (RELATIONAL, GROUNDED, t1=False) are grounded by the two-source window
rule, confirmed. No rows were missed: every other GROUNDED row has t1=True, and
every short-circuit verdict (UNCITED / UNVERIFIED_* / UNGROUNDABLE) is
`tier_sensitive=False` by construction.

**q46 is one of CR-002's 3 false negatives — confirmed.** At tau=0.76 the three
`fn` cells are **q14, q37 (both ABSENCE→ABSENCE_SUPPORTED) and q46 (T2)**. So
T2 owns exactly one third of the deployed Error-B, and the other two thirds sit
in `check_absence` — a fact the proposal does not mention and which materially
weakens "T2 is where the Error-B is".

Incidental correction to the record: in-sample at 0.76 the rates are
**A=0.160 / B=0.111 (tp=24 fp=4 tn=21 fn=3)**. CR-002's published fp=5 / A=0.200
is the leave-one-out figure. The two are not interchangeable and the extra false
positive is a fold-selection artifact.

---

## (b) The price of demotion — **REFUTED (0.360 is wrong)**

Demotion makes every `tier_sensitive` row a violation at every tau (the two
sensitive states are GROUNDED-via-T2 and UNGROUNDED; kill the first and both
collapse to violation). Modelled by forcing `t2_f1 = -1.0` and re-running the
real machinery:

| Variant | held-out Error-A | held-out Error-B | confusion |
|---|---|---|---|
| **Status quo** (T2 sufficient) | **0.200** | **0.111** | tp=24 fp=5 tn=20 fn=3 |
| **Demotion** (T2 → corroborating) | **0.320** | **0.074** | tp=25 fp=8 tn=17 fn=2 |
| Coverage repair (see (c)) | 0.240 | 0.074 | tp=25 fp=6 tn=19 fn=2 |

The claimed 0.360 is **wrong**, and wrong in a specific way: it stacks 4 new
false positives onto the LOO-inflated base of 5, but that inflation is a
tau-selection artifact that *vanishes* under demotion (with T2 gone, lex_tau
selects nothing, so held-out equals in-sample). The true held-out cost is
**0.200 → 0.320**, 8 false alarms on 25 honest claims.

Error-B does improve, 0.111 → 0.074 (q46 caught; q14/q37 remain). That direction
of the claim survives.

**Second-order finding the proposal misses: demotion kills the calibration.**
Under demotion I verified the error rates are *identical* at tau = 0.50, 0.76 and
0.95. `lex_tau` becomes a dead parameter, `loo_operating_point` returns 0.95
purely on its higher-tau tie-break, and CR-002 — the artifact that licenses the
deployed threshold — becomes vacuous. Any demotion must ship with an ADR retiring
lex_tau, not merely a new CR.

---

## (c) Does a feature already in the codebase separate q46? — **REFUTED. Yes, one does.**

Claim 1's *lemma* is true: no lex_tau separates the rows (honest q35 = 0.889 sits
above violation q46 = 0.857, and honest q05 = 0.762 sits below it — the classes
interleave in both directions). But the *conclusion* does not follow, because the
separating feature is not a threshold on the score.

**Why the existing misattribution rule does not fire on q46.** `t2_lexical`
builds `elsewhere` from `other_source_texts` — the store's **other** verbatim
sources, excluding the cited ones — and flags `tok not in source_vocab and tok in
elsewhere`. q46's store contains **exactly one source, S46**. `other_source_texts`
is therefore empty, `elsewhere` is the empty set, and `misattributed` is
necessarily empty *whatever the claim says*. The rule cannot fire by
construction. (35 of the 52 corpus stores hold 1 source, 12 hold 2, 5 hold 0.)
This is precisely the residual the code already documents: "catches
misattribution only when the session actually retrieved the other entity."
q46 is the same attack class the rule was written for — one entity swapped for
another ("mapping" for "logistics") — defeated by a single-source store.

**The feature that does separate it.** `t2_lexical` already computes
`source_vocab = set(_tokenize(source.text))` on the line above. Requiring that
some cited source's vocabulary **cover every claim content token** gives:

| id | novel content tokens vs cited source | gold |
|---|---|---|
| q05 | *(none)* | grounded |
| q08 | *(none)* | grounded |
| q09 | *(none)* | grounded |
| q35 | `every` | grounded |
| q46 | `mapping` | **violation** |

It separates q46 from q05/q08/q09 exactly, and costs one row (q35, on the
determiner "every"). Measured end to end: **held-out A=0.240 / B=0.074**.

**This dominates demotion: identical Error-B, and 0.240 vs 0.320 Error-A.**
Under the project's own selection rule — minimise Error-A subject to Error-B ≤
the bound — the repair is strictly preferred and demotion is not on the frontier.

Honest counterweight, stated because it is the strongest thing against my own
finding: this is the "require EVERY content token" rule `t2_lexical`'s docstring
already considered and rejected, and it fails on the same fixture cited there —
`grounded_t2` ("achieves" vs "delivers"). Under the repair the full suite gives
**2 failures** (`test_golden_verdict_matrix[grounded_t2]`,
`test_grounded_t2_tier_split`); under demotion, **8**. So the repair narrows T2
to reorder/stopword paraphrase and gives up one-word synonymy; that trade is a
real decision, but it is a *smaller* one than deleting the tier, and it is the
decision the evidence points at.

I checked the other candidate features and none of them separate q46: `numeric_ok`
is True (12% is in S46, the number is not the lie); polarity is neutral on both
sides; subject anchoring passes because the claim's first content token is
"revenue", which is in S46; `_relation_asserted` never runs (q46 is NUMERIC).

---

## (d) Is 0.32 Error-A tolerable? — **REFUTED as a concern**

I ran it rather than argued it. Baseline: `455 passed, 2 skipped, 4 xfailed`.

With T2 demoted (`t2_lexical` forced False): **8 failed, 447 passed**. All eight
are unit tests *of T2 itself* — `test_tiers.py` (3), `test_calibrate_features.py`
(2), `test_golden_matrix.py` (2), `test_t2_score.py` (1) — i.e. tests that would
be rewritten or deleted as part of the change, not collateral damage.

Critically for the attack I was asked to press: **`tests/honest_drafts/` passes
in full and `tests/test_demo_golden.py` passes.** The demo's honest draft
(`demo/draft-grounded.md`) still reaches PASS, because both of its claims are
grounded by T1 verbatim spans, not by T2. The whole red-team suite also stays
green. So the "it turns the product's own demo red" line of attack fails.

But that green is weaker evidence than it looks, and this is the finding that
matters: **`tests/honest_drafts/` contains no T2-only honest draft.** The suite
that exists to catch Error-A regressions is structurally blind to exactly the
regression demotion causes. The only canonical honest-T2 case anywhere in the
repo is the `grounded_t2` golden-matrix row, and that one *does* go red. Whatever
is decided about T2, `tests/honest_drafts/` needs a T2-only fixture, or the
Error-A guard is guarding nothing on this axis.

---

## (e) "T3 can never CREATE a PASS" — **UPHELD, and there is a second one**

The literal sentence is false, for exactly the reason given. `score_report`
(ADR-005) sets PASS iff score ≥ threshold **and** `retained_appendix` is empty
**and** no UNVERIFIED_CITATION. An `UNGROUNDED` claim is a retained-appendix
entry. On a draft whose only violation is one UNGROUNDED claim, T3's single
permitted transition empties the appendix and the gate moves NEEDS_WORK → PASS.
That is creating a PASS.

I looked for the charitable reading requested and neither candidate holds:

1. **Verdict-space reading** — the bullet's own supporting clause is about which
   verdicts T3 can touch ("structurally cannot touch UNVERIFIED_CITATION,
   UNVERIFIED_NUMBER, UNGROUNDABLE, UNCITED, or any relational/absence verdict").
   Read that way the true statement is "T3 cannot rescue a *categorically* failed
   claim." Defensible — but that is not what "never CREATE a PASS" says, and in a
   document whose other bullets are quoted as invariants, an absolute that means
   something narrower is a trap, not a shorthand.
2. **Default-off reading** — true only while the tier is off, and vacuous the
   moment it is enabled, which is the only state in which the guarantee is being
   claimed.

**Second overclaim, same page, line 29:** "it may reduce false-flags; it may
never create an Error-B." Any mechanism that turns UNGROUNDED into GROUNDED can
turn a *true-violation* UNGROUNDED into GROUNDED, which is an Error-B by
definition. Nothing structural prevents it; only `nli_tau` calibration bounds the
rate. This is a rate promise written in the grammar of a structural one — the
same category error as the PASS bullet, and the more dangerous of the two because
Error-B is the invariant.

**The empirical proof is already in this corpus.** q46 is an UNGROUNDED-by-rights
claim that a paraphrase tier upgraded to GROUNDED, producing an Error-B, via the
identical branch T3 will use. T2 is T3's precedent, and it has already done the
thing the plan says the successor cannot do.

Suggested wording, which is true and still says what the authors meant: *"T3 can
only ever move a claim along one edge, UNGROUNDED → GROUNDED. It cannot rescue a
claim that failed citation resolution, the verbatim filter, the numeric gate, or
an absence/relational rule. Because that one edge feeds ADR-005's retained
appendix, T3 CAN change a gate verdict from NEEDS_WORK to PASS, and can therefore
produce Error-B; the bound on that is nli_tau's calibration, not the structure."*

---

## Recommendation

**Reject the demotion; adopt the coverage repair instead** — and take the
decision to Sai under Escalation #1, because both options move the
Error-A/Error-B trade-off.

Why: on the only measured evidence available, the repair delivers the *same*
Error-B improvement as demotion (0.111 → 0.074) at *two thirds* of the Error-A
cost (0.240 vs 0.320), keeps `lex_tau` and CR-002 meaningful, and breaks 2 tests
instead of 8. Demotion is not on the error frontier; it is the repair plus four
avoidable false alarms.

**Load-bearing assumption, surfaced:** this rests on n=52, single ratifier, and
the gap between the two options is **two claims** (q05, q08, q09 vs q35). A
second blind labeller — already CR-002's named open step — could move it. The
repair's cost is also under-measured: it kills one-word synonymy (`achieves` /
`delivers`), which the 52-row corpus happens not to contain but real drafts will.

**What would flip the recommendation:** evidence that one-word synonym paraphrase
is common in honest drafts. If it is, the repair's true Error-A is higher than
0.240 and the right move is neither option but a synonym-tolerant coverage check
— which is the T3 NLI tier, i.e. Phase 2b, i.e. wait.

**Third finding, independent of the decision:** `tests/honest_drafts/` has no
T2-only fixture and cannot detect an Error-A regression in this tier. Fix that
regardless of which option is chosen.
