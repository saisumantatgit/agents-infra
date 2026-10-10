# 2026-10-02D — The refusal that one word walked around

**Session:** `d2b27b1f` · branch `delivery-queue-2026-10-02` · overnight run D-78
**Suite:** 797 passed · 2 skipped · 66 xfailed · exit 0 · gold md5 `6215b526…d171f` untouched
**Deployed rates UNCHANGED: Error-A 0.400, Error-B 0.000. CR-007 still governs.**

## What

Round 14 — the merge gate on PR #7 — ran against the flat relational refusal and
came back with three new CRITICAL Error-B shapes plus one re-confirmed finding
re-graded to CRITICAL. Nothing in the gate was repaired. Three candidate repairs
were priced and all three were left for Sai. One recommendation was published
and then withdrawn the same night.

## Why it mattered that the merge was conditional

In the §0 handshake I named the load-bearing assumption: *that a flat refusal
cannot be routed around.* It could. `ground()` refuses only on
`kind == RELATIONAL`, and `classify` sets that only from `_RELATIONAL_RE` — ten
surface forms over an open class. `causes` → `triggered` flips the same sentence
on the same store from FAIL / exit 1 to **PASS 100.0 / exit 0**, against a
source reading *"found no evidence that the migration triggered widespread
customer refunds."*

Had PR #7 merged last night on the strength of "the demotion is in and the suite
is green", that would have shipped.

## Done

- **Round 14 run, every finding reproduced by me** from the adversary's own
  fixtures before being recorded. 7/7 round-12 relational shapes confirmed
  refused; positive control independently re-verified at PASS 100.0.
- **The root cause located, and it is not the one the adversary named.** R14-01
  and R14-04 are one mechanism: T1 anchors its ≥8-token span at the claim's
  first content word, so a long-subject claim matches a span inside its own
  subject; the predicate is then checked only by set-membership coverage, and
  `_span_is_hedged` reads only the five tokens **before** the span. Measured
  decisively: the same denial moved *before* the subject refuses (FAIL 0.0),
  left *after* it certifies (PASS 100.0). It reproduces on plain FACTUAL with no
  causal word, **so extending the causal lexicon cannot fix it** — which is why
  the register recommends against the obvious repair.
- **Three candidates priced, none landed.** Whole-source hedge scan; figure
  checks before the absence verdict; lexicon extension.
- **J-45** fixed (display-only). **J-37** found already closed. **ADR-007
  amended** for my own overclaim. **CR-008** written. **J-69…J-72** registered
  with owners.

## Decisions

| id | Decision | Why |
|---|---|---|
| D-78 | Overnight run armed | Sai's handshake, agreed |
| D-79 | J-37 in scope | He confirmed; turned out already done |
| — | **Nothing in the gate repaired** | All three candidates alter which claims can pass — Escalation #1 |
| — | **J-62 and J-71 merged into one class** | One defect cannot be half mine and half Sai's; a register that splits a class stops being usable |
| — | **J-45 fixed by removing false precision, not by recomputing the count** | Two copies of a moat rule diverge; display must never become decision (D-34) |

## Withdrawals

**The J-70 repair, withdrawn after I had already published it in a PR comment.**
I priced it on the gold corpus at +0.160 Error-A — four extra false alarms in
25, which reads as tolerable — and recommended it. Then I ran the honest-draft
harness on the identical patch: **7 passing drafts → 5 failing**, one of them a
*verbatim quotation of the cited source* reading `UNGROUNDED`. Mechanism:
nearly every real source sentence contains some `_SPAN_HEDGE_TOKENS` member, so
scanning the whole source makes nearly every source look hedged.

**A cycle spent on finished work.** I wrote a complete duplicate test for J-37
before searching the suite. It had been closed on 2026-10-01; the register row
still described the pre-fix mechanism in the present tense, and I trusted the
row — the exact rule I had written into the instrument file an hour earlier.
Deleted. The one real gap it was missing (no `pytest.raises` anywhere in that
file, so all three of its tests were satisfiable by a loader whose validation
had been deleted) is now closed and mutation-checked.

**A count I inflated.** I wrote "four CRITICAL" in five places after silently
re-grading R14-04 from the adversary's "HIGH, re-confirmed". The re-grade is
right; doing it silently is how a number drifts. Caught by the Gap Analyst hat
on my own work, and now stated wherever the count appears.

## Agents

One Opus adversary (last gate, never downgraded): 35 tool calls, 169,384 tokens,
13 min. Report written to a file, ≤10-line hand-back. Everything else was mine.

## Reflection

**The instrument lesson inverted itself tonight, and that is the part worth
keeping.** Yesterday's entry concluded: for Error-A the instrument is the
corpus; for Error-B it is an adversary, never a corpus. Tonight the corpus
failed at **Error-A** — the thing it was supposed to be good for. It priced the
J-70 repair as cheap because it contains no row shaped like the drafts that
break; the honest-draft harness, seven files in a directory, said the same patch
destroys five of seven real drafts including a verbatim quote.

So the sharper statement is not about which instrument measures which error. It
is that **a corpus of labelled rows measures only the shapes someone thought to
label**, and a gate is used on documents nobody labelled. The gold corpus is a
*label* instrument. The honest-draft harness is a *usage* instrument. The
adversary is a *hostility* instrument. All three were needed tonight to get one
decision right, and I had already published a recommendation after consulting
one of them.

There is a quieter thing underneath. Three times in three days — J-44's stem,
the fall-through, and tonight's hedge scan — I produced a correct measurement
and drew a wrong conclusion from it, each time inside a ruling that touched the
moat. The failure is not arithmetic and not carelessness. It is that a number
feels like the end of an argument, and the question *"what could this instrument
not have shown me?"* has to be asked deliberately, because nothing in the number
prompts it. Tonight was the first time I asked it before landing rather than
after.

## Next

**PR #7 remains DO-NOT-MERGE.** Three CRITICAL classes open, all Sai's
(Escalation #1): J-69 the classifier-gated refusal, **J-70 the span/hedge
mechanism — the one to fix**, J-62+J-71 the absence figure checks (the cheap
one, Error-A 0.400 unchanged). His existing list is unchanged: J-54, J-51, q25.
Mine: J-72, and whatever follows his ruling on J-70.
