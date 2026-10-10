# Intra-rater round — the corpus is MIXED, not ambiguous

**Date:** 2026-09-12 · **Rater:** Sai, blind, shuffled, 20 items, seed 20260912.
**Raw answers:** recorded in the session log. **Nothing was written to
`labels-v2.csv`** — this is not gold and no generator may touch that file.

## Headline

| stratum | agreement | Cohen's κ |
|---|---|---|
| All 16 random rows | 13/16 · 81.2% | **+0.636** |
| **The 2 `haiku_summary` rows** | **0/2** | — |
| **The other 14** | **13/14 · 92.9%** | **+0.857** |

**Anchoring: refuted, 4 of 4.** Every row where Sai once overruled the machine
candidate — q14, q16, q37, q49 — he overruled it again, blind, in shuffled
order, months later. **The gold labels are not a mirror of the gate's own
output.** That was the most serious of the three branches and it is dead.

## Why the sample was stratified

`init_labels.py` seeds every row with Claude's `candidate_verdict` and the
ratifier corrects it, so on 48 of 52 rows gold == candidate. On those rows
*"Sai agrees with himself"* and *"Sai agrees with the machine"* are the same
observation. Only 4 rows separate them. **A plain random draw of 20 contained
none of the four (p = 0.133) and would have been blind to the branch it existed
to detect.** All 4 were forced in; the strata are never pooled.

## The finding: two kinds of item, one instrument

Two of the three disagreements are the `haiku_summary` rows, and they are the
**same two rows both external readers hit, in the same direction**:

| rater | agreement with gold on those 2 rows |
|---|---|
| Pravallika (2026-09-03) | 0/2 |
| Nandu (2026-09-03) | 0/2 |
| **Sai (2026-09-12, provenance stated explicitly)** | **0/2** |

```
S24   "The compound showed strong efficacy in phase II trials with a
       favorable safety profile."
claim "The compound showed strong efficacy in phase II trials [S24]."
gold  violation
```

The evidence supports the claim word for word. Gold says violation for a reason
**not visible in the item**: an AI summary cannot ground anything, whoever wrote
it, because it is a paraphrase nobody verified against the source. That rule is
correct **as policy** and is not **derivable from the evidence shown**.

**Retraction.** The 2026-09-03 inter-rater report blamed my page's wording —
it asked *"does this summary support the statement?"* when the gold rule is
about provenance. The rebuilt page states the provenance outright
(*"AI-generated summary of the page — not the page text"*) and Sai still read it
as grounded. **The wording was not the cause.** The item is unlabelable from its
own contents.

So the corpus mixes **policy-labelled** items with **evidence-derivable** ones,
and has been measuring reliability across both with one instrument. On such an
item, inter-rater agreement measures whether the rater memorised a rule.

**The exclusion is not post-hoc.** These two rows were identified as
systematically divergent on 2026-09-03, from a different dataset, before this
test existed.

## The one genuinely ambiguous item

```
claim "Increased marketing spend drives higher customer signups [S251][S252]."
S251  Marketing spend increased twenty percent quarter over quarter…
S252  Customer signups rose…
gold  violation (a causal claim from two correlational sources)
now   grounded
```

Causation vs correlation. This is real ambiguity, not an instrument artifact.
**Adjudication is Sai's** — a gold label is never Claude's to set (standing gate).

## Consequences

1. **Alpha #5 is reachable again.** The κ 0.09 reader failure is now
   substantially explained: inflated by label-sorted ordering, dragged by policy
   items no reader could get right. Next step is ONE domain-competent reader on
   **derivable items only**.
2. **Policy items must be segregated** in the corpus — valid gate behaviour,
   invalid reliability data. Scaffold-side split; `labels-v2.csv` untouched.
3. **Rates may now be quoted with a caveat rather than an asterisk over
   everything.** Attach: *(n=52, single ratifier, CR-004; intra-rater κ=+0.857
   on evidence-derivable items, anchoring refuted 4/4, INTRA-RATER-2026-09-12)*.

## What this round could NOT have detected

n=4 on the anchoring probe. Four for four is the strongest available result and
it is still four. A rater anchored on a *different* axis — say, on the verdict
he gave most often — would not show up here at all. And the 14 derivable rows
are this corpus's items: they say nothing about items it does not contain,
which is exactly the blind spot rounds 3–7 keep exploiting.
