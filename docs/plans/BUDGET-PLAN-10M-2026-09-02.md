# Agent-Assure — how to spend a 10M sanction

**Written:** 2026-09-02, immediately after CR-002 closed α2.
**Status:** PLAN. Tranche 0 is free and gates everything below it.
**Author:** Claude (Fable 5), autonomous session `d2b27b1f`.

---

## BLUF

**Do not spend 10M on Alpha. Alpha needs about 3M.**

The remaining Alpha work is gated by **four rulings only Sai can make**, not by
budget — I could burn the whole sanction without touching any of them. And the
two genuinely budget-hungry slices (2a research front-end, 2d cross-platform)
are the spec's own "commodity half"; building a delivery layer on a core with a
known-open Error-B hole is the sequencing error 2c-first was designed to avoid.

**Recommendation: authorise ~3M, reach a defensible Alpha, and re-decide the
remaining ~7M against α5's evidence rather than against today's optimism.**

The one-line why: **α5 is the checkpoint that tells you whether the front-end is
worth building.** Spending the front-end budget before it buys the answer and
the question in the wrong order — the same mistake CR-002 just avoided by
measuring before deploying.

---

## Tranche 0 — costs nothing, unblocks the most (do this first)

| # | Item | Owner | Why it gates the rest |
|---|---|---|---|
| 0.1 | **Second blind labeller** on the same 52 (review page is built; link in the logbook) | Sai → a family member | CR-002's rates are from a single ratifier who is also the project owner and had seen 9 candidates. This is the only step that converts them into **independent** ground truth, and it costs 0 tokens and ~40 min of someone else's time. |
| 0.2 | **Rule OI-MOAT-21** — demote T2 from sufficient-for-GROUNDED, or accept the residual | Sai | A live, demonstrated Error-B hole. **α5 cannot honestly precede it.** Sizes tranche 1. |
| 0.3 | **Rule OI-DEC-01** (PASS-enabling citation propagation) and **OI-MOAT-20** (verb-final header) | Sai | Both one-line calls. Each is small work behind a decision. |
| 0.4 | **Rule ADR-004 Q1–Q6** (NLI tier semantics + the "zero LLM calls" slogan) | Sai | Decides whether tranche 2 exists at all. Read the 2026-08-30 addendum first: T3's case has *inverted*, not shrunk. |

**Nothing below starts well without 0.2 and 0.4.**

---

## Tranche 1 — the defensible-Alpha spend (~3M, recommended now)

| # | Work | Est. | Depends on |
|---|---|---|---|
| 1.1 | **OI-MOAT-21 structural fix** — if ruled "demote": rework `ground()` so T2 corroborates rather than decides, re-run the sweep, emit **CR-003** (lex_tau's meaning changes when T2 stops deciding alone, so the old number does not carry) | 1.2–2.0M | 0.2 |
| 1.2 | **Red-team round 6** against the CR-002 deployment and the 1.1 rework | 0.3–0.5M | 1.1 |
| 1.3 | **Second-labeller ingestion**: agreement stats, adjudication of disagreements, CR amendment removing the independence caveat | 0.2–0.3M | 0.1 |
| 1.4 | **OI-T2-01** (verbatim short quote reads UNGROUNDED) + **OI-DEC-01** + **OI-MOAT-20** | 0.3–0.5M | 0.3 |
| 1.5 | **α5 sign-off**: Opus whole-branch adversarial review, AAR-004, tag `v0.9.0-alpha` | 0.4–0.6M | all above |
| | **Total** | **~2.4–3.9M** | |

**Exit:** Alpha declared on evidence — gold-calibrated, independently labelled,
five red-team rounds deep, with every residual either closed or explicitly
accepted in writing.

---

## Tranche 2 — decision-gated, only if ADR-004 says build (~3.6–6.1M)

**2b NLI tier (α3).** The ADR-004 package's own estimate. Note what changed on
2026-08-30: T3 is **no longer needed** for OI-MOAT-03 (closed deterministically),
but it *is* now the only principled answer to the subject-swap class round 4
found, and to OI-T2-01's paraphrase false alarms.

**Do not start this before 1.1.** If T2 gets demoted, the tier structure T3
plugs into changes, and a rebase done first would be done twice.

---

## Tranche 3 — hold until α5 exists (~5M)

**2a research front-end (~4–5M)** and **2d cross-platform (~0.5M)**.

Both are delivery layers over the gate. Your own spec calls 2a the commodity
half; the differentiated half is the gate, and the gate currently has one open
Error-B hole and a single-ratifier calibration. **Every claim the front-end
makes inherits the gate's trustworthiness**, so building it first multiplies an
unvalidated core rather than a validated one.

Revisit after α5 with three questions answered: did the independent labeller
agree? did round 6 find anything? is the moat closed or explicitly accepted?

---

## What 10M buys if you spend it all today, and why not to

Tranche 1 + 2 + 3 ≈ 11–15M — the sanction does not actually cover everything,
so it *will* be allocated whether deliberately or not. Spending it in listed
order without the tranche-0 rulings produces:

- 2a built against a gate whose operating point may move under 1.1 → rework.
- 2b rebased onto a tier structure that then changes → rework.
- α5 signed over a known-open Error-B hole → the one thing that makes the
  product claim false in public.

**The binding constraint is not tokens. It is four decisions and forty minutes
of a second reader.**

---

## The load-bearing assumption

**That α5 is still the right next milestone.** If the goal has shifted from
*a defensible verification gate* to *a demoable end-to-end research product*,
tranche 3 moves first and this plan inverts — and that is a legitimate product
call, not an error. But it should be made knowingly: the demo would then rest
on a core carrying a documented, reproducible way to pass a false claim.

If that shift is what you want, say so and I will rewrite this plan around it
rather than quietly optimising for the wrong milestone.
