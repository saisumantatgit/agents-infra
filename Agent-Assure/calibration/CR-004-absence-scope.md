# CR-004 — absence scope rule (OI-ABS-01)

**Executes:** an autonomous fail-closed change under the ratified Escalation-#1
reading (D-15). **Date:** 2026-09-03. **Corpus:** the same 52 GOLD labels.
**Follows:** CR-003 (T2 demotion). **Labels unchanged.**

---

## What changed

`check_absence` verified that the negated SUBJECT was searched twice. It never
looked at the claim's SCOPE — the domain the absence is asserted over. So a
writer could search narrowly and assert broadly:

    claim   "no recall of the Zentara inhaler IN ANY REGULATED MARKET"
    queries "Zentara inhaler recall search" / "FDA recall database Zentara recall"

Both queries carry the subject, so the two-search rule passed. Neither
establishes anything about "any regulated market" — one is explicitly the FDA,
a single jurisdiction standing in for all of them.

**Rule added:** a query counts toward the two-search minimum only if it also
addresses the scope. To establish that something is absent from a domain you
must have looked in that domain; a search outside the claimed scope is not weak
evidence, it is none.

## Projection vs actual

| Measure | Projected | Actual | Δ |
|---|---|---|---|
| Error-A | 0.320 (unchanged) | **0.320** | 0% |
| Error-B | 0.000 | **0.000** | 0% |
| Confusion (tp/fp/tn/fn) | 27/8/17/0 | **27/8/17/0** | 0% |
| Corpus rows whose verdict changes | 2 | **2** | 0% |
| Existing tests broken | 0 | **1** | see below |

The broken test is the delta worth reading. `test_specific_subject_supported_
when_corroborated` asserted `ABSENCE_SUPPORTED` for **corpus row q37** — which
Sai gold-labeled **violation**. It had been green for weeks asserting the
opposite of a ratified human judgment, and it was named *"Error-A guard"*, which
is why nobody looked. A test named for a property must assert that property
(INS-005); this one was named for Error-A and was protecting an Error-B.
Corrected, and split so the stemming property it also carried is kept.

## Movement

| | CR-003 | CR-004 |
|---|---|---|
| Error-A | 0.320 | **0.320** |
| Error-B | 0.074 | **0.000** |

Error-B fell without Error-A rising — a strict improvement, not a trade.

## Read this before quoting "zero"

**Error-B = 0.000 means no KNOWN violation escapes. It does not mean none can.**
On 0 misses out of 27 violations, the 95% one-sided upper bound on the true rate
is **~10.5%** — the corpus is far too small for "zero" to mean zero. And every
red-team round so far has found violation CLASSES the corpus does not contain:
rounds 3–5 found 65 wrongful PASSes across 12 mechanisms, none of them corpus
rows. The honest statement is *"no remaining Error-B among the 52 ratified
rows"*, and the next round will very likely add some.

Quote as *(n=52, single ratifier, CR-004)* **plus the inter-rater result**: two
independent readers (2026-09-03) reproduced these labels at Cohen's κ = **0.54**
and **0.16**, and agreed with **each other** at κ = **0.09** — chance. The
independence check FAILED. Only 22 of 50 rows are unanimous across all three
people, and on that core Error-A is *worse* (0.417); Error-B holds at 0.000 on
every subset. See `docs/reports/INTER-RATER-2026-09-03.md` — including two
defects in the review page that were mine, and which inflate the figures above.

## Scope of the rule, stated so it can be attacked

It fires only on a trailing prepositional phrase headed by
in/within/across/throughout/among/under/outside/beyond. `of` and `for` are
deliberately excluded — they attach to the subject ("no antidote FOR the
toxin"), and treating them as scope would fire on ordinary noun phrases. The
corpus's one gold-GROUNDED absence ("...affecting the X200 drone") is unscoped
under this definition and is unaffected. That exclusion is the rule's soft seam:
a scope introduced some other way ("no recall ANYWHERE", "no European recall")
is not detected.
