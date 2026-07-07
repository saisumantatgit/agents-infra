# Gold-Label Ratification Brief — Agent-Assure Calibration v2

**For:** Sai · **From:** assure-calibration (Phase α1) · **Date:** 2026-07-08
**Artifact:** `calibration/labeling-v2.csv` — 52 candidate claims / 52 queries
**Expected effort:** 30–45 min · **Blocks:** Phase α2 calibration run (CR-002)

---

## What this is

A widened calibration corpus (n=52, up from the n=12 bootstrap) with a
**candidate** grounding label pre-filled on every row. Your job is not to
label from scratch — it is to **ratify or correct** the candidate calls, then
mark the file gold. The gate cannot calibrate on these labels until you do:
`load_labels` refuses any row whose `label_status != gold` (fail-loud, tested).

Class balance: **25 violation / 27 grounded (48% violation)** — comfortably
above the 30% positive-class floor. Every failure type in
`references/grounding-failure-types.md` is represented.

## How to ratify (3 steps)

1. Open `calibration/labeling-v2.csv`. Each row shows `claim_text`, the
   `evidence` the gate would see, the `candidate_verdict`, and a one-line
   `rationale`. The label you judge lives in **`human_label`** (pre-set equal
   to the candidate).
2. For each row, decide **grounded** (the evidence genuinely supports the
   claim) or **violation** (it does not). Change `human_label` only where you
   disagree. `candidate_verdict` and `rationale` are a frozen record — leave
   them.
3. When done, set **`label_status` to `gold` on every row** (find-and-replace
   `candidate` → `gold`). Save. That flip is what unblocks α2.

Judge grounding as a human would: does the cited source text (or, for absence
claims, the listed searches) actually establish the sentence? The gate's own
mechanical verdict is deliberately **not** shown, to keep your call
independent — but see the caveat below.

## The 14 rows to look at hardest

These are where the candidate call is least certain — the divergence rows
(the mechanical gate and the human read disagree) and the near-miss traps a
quick skim mislabels. Spend most of your 30–45 min here.

| CSV line | id | Candidate | Why it's hard |
|---|---|---|---|
| 44 | q25 | violation | Relational **over-association**: spend-up and signups-up sit in two sources, but neither states spend *causes* signups. Gate grounds it; the causal link is unearned. |
| 45 | q26 | violation | Same trap — latency-up and churn-up co-occur; causation is asserted by the draft, not the sources. |
| 46 | q48 | violation | Same — remote-work and cost-decline are two independent facts; the link is inferred. |
| 48 | q46 | violation | Number **and** phrasing match the source, but the source is the *logistics* division and the claim says *mapping*. One-word swap the gate grounds. |
| 49 | q27 | grounded | Faithful paraphrase with **low lexical overlap** — meaning fully supported, but the words diverge enough that the gate likely calls it UNGROUNDED. Is a true paraphrase grounded? |
| 50 | q47 | grounded | Same paraphrase question — "keeps the drone flying longer" vs "extends airborne duration per charge." |
| 51 | q30 | violation | Absence claim about **fraud**; the two searches shown mention "evidence" but concern data-loss and latency — the fraud absence is not actually searched. Gate's substring rule accepts it. |
| 52 | q49 | grounded | Absence of **replication**; two replication searches were run, but the gate keys on the head noun "independent" and misses them. Do the searches substantiate the claim? |
| 10 | q31 | grounded | Claim `$4M`, source `$4,000,000` — same value, different surface form. Genuinely grounded; the gate's literal numeric-presence check may miss it. |
| 28 | q16 | violation | **Unit drift**: claim `25%`, source bare `25`. Easy to eyeball as a match; it is not. |
| 29 | q17 | violation | **Magnitude drift**: claim `100,000`, source `10,000`. One zero. |
| 30 | q50 | violation | **Decimal drift**: claim `3.5 GHz`, source `3.2 GHz`. |
| 33 | q19 | violation | **Plausible fabricated citation**: the 62% number reads real, but `[S19]` was never retrieved this session. A fabricated citation is a violation *regardless* of whether the number is true — this is the core moat call. |
| 47 | q28 | violation | **Negation inversion**: "failed repeatedly" vs source "lasted … without failure." High word overlap, opposite meaning. |

## The one assumption that, if wrong, collapses this

**The positive class is pinned to _violation_, and "grounded" means _the cited
evidence establishes the claim_ — not "the claim is true in the world."** q19
and q46 are the test: their claims may well be factually true, but they are
**violations** because the evidence-store link is fabricated/mismatched. If you
ratify them as "grounded" on real-world truth rather than on store-grounding,
every threshold α2 derives will be miscalibrated toward passing fabrications
(Error-B, the unrecoverable one). If your mental model of "grounded" differs
from this, stop and flag it — that disagreement, not the individual rows, is
what matters.

---
*After ratification, drop an `ack` in `outbox/` or reply on the inbox item;
α2 (threshold sweep + CR-002) runs against the gold file.*
