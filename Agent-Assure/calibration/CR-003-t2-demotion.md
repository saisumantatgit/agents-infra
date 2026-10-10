# CR-003 — T2 demotion + exact-containment T1

**Executes:** ADR-006 (`docs/decisions/ADR-006-demote-t2.md`), approved by Sai 2026-09-02.
**Supersedes:** CR-002 (lex_tau=0.76). **Status:** DEPLOYED 2026-09-02.
**Corpus:** the same 52 Sai-ratified GOLD labels as CR-002. No labels changed.

---

## There is no operating point in this record

CR-001 and CR-002 selected `lex_tau`. This one **retires it**. T2 no longer
decides any verdict, so the gate has **zero fitted parameters** on the grounding
path.

One consequence is worth stating plainly, because it is the only good news in
this record: CR-002 needed leave-one-out because selecting a threshold on the
same rows you evaluate on is optimistically biased. **With no parameter to
select, that bias does not exist**, so the numbers below are held-out by
construction rather than by resampling. `--lex-tau` is now a hard error, not a
no-op.

## Projection vs actual

| Measure | Projected | Actual | Δ |
|---|---|---|---|
| Error-A (false alarm on an honest claim) | 0.320 | **0.320** | 0% |
| Error-B (fabrication certified) | 0.074 | **0.074** | 0% |
| Confusion (tp/fp/tn/fn) | 25/8/17/2 | **25/8/17/2** | 0% |
| Corpus rows whose verdict changes | 5 | **5** | 0% |
| Rows rescued by exact containment | 0 | **0** | 0% |
| Corpus rows with any feature change | 5 | **6** | +20% |

Deltas >20%: the sixth row is **q36**, whose *verdict is unchanged* (GROUNDED)
but whose `t1_verbatim` flipped False→True — exact containment now supplies the
span that `ground_relational` had reached without it. A feature moved, a verdict
did not. Projected on verdicts, counted on features.

## Movement against CR-002

| | CR-002 | CR-003 | |
|---|---|---|---|
| Error-A | 0.200 | **0.320** | worse by 0.120 — the price, paid knowingly |
| Error-B | 0.111 | **0.074** | better by 0.037 |
| `lex_tau` | 0.76 | **retired** | |

**Error-B monotonicity holds.** The invariant forbids buying Error-A down by
raising Error-B; this trade goes the permitted direction.

## The five rows that moved, adjudicated against their gold labels

| row | gold | was | now | reading |
|---|---|---|---|---|
| q46 | violation | GROUNDED | UNGROUNDED | **Error-B closed.** `mapping` for `logistics` |
| q05 | grounded | GROUNDED | UNGROUNDED | new false alarm — faithful reorder |
| q08 | grounded | GROUNDED | UNGROUNDED | new false alarm — faithful trim |
| q09 | grounded | GROUNDED | UNGROUNDED | new false alarm — faithful trim |
| q35 | grounded | GROUNDED | UNGROUNDED | new false alarm — faithful reorder |

None of the four carries a novel token, so **no coverage rule would have saved
them either**; only T3/NLI can.

## Residual Error-B — and it is no longer T2's

The two remaining false negatives are **q14** and **q37**, both
`ABSENCE_SUPPORTED` out of `check_absence`. T2 owned exactly one of the three
CR-002 false negatives, and that one is now closed. **The next Error-B work is
in the absence rule, not the tiers.**

## What this record cannot tell you

Error-A 0.320 is measured on 52 claims authored for calibration, ratified by a
**single** labeller who is also the project owner. Whether 0.320 is tolerable
depends on how often real drafts paraphrase rather than quote — **which nobody
has measured**, here or anywhere in this repo. Quote as
*(n=52, single ratifier, CR-003)*, and treat the tolerability question as open.

Second blind labeller: still open (J-06).
