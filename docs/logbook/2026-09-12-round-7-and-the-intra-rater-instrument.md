# 2026-09-12 — Round 7, and an instrument that would have measured nothing

**Session** `d2b27b1f` (continued) · branch `agent-assure-calibration-run`
**Mode:** overnight, cron-advanced, 10M sanctioned, standing order in force.
**Suite at close:** 510 passed · 2 skipped · 22 xfailed. Corpus byte-identical.

## What

Two things: built the intra-rater instrument Sai needs, and ran **red-team
round 7** — the first adversarial round against the D-15…D-20 decomposition
cohort, aimed by hazard analysis rather than by imagination.

## Why

Round 7 was owed: six moat changes landed after round 6, so the tree had never
been attacked. The instrument was owed because the inter-rater check failed
(κ 0.09) and the cheapest decisive next test needs only Sai's twenty minutes.

## Done

- **Intra-rater instrument** live, with its scoring script, four dry-run-verified
  branches, and a withheld key. D-21…D-23.
- **Round 7**: 3 Opus adversaries, one per STPA-derived control path.
  **22 wrongful PASSes over 11 mechanisms.** 3 closed (D-24), 19 open and
  tripwired across 7 classes. Every headline finding re-verified by hand.
- **Solo gate** on my own round-7 conclusions. 4 of 6 claims came back
  OVERSTATED or WRONG. Corrections landed the same night.
- **J-15 brief**: 1,337 real-prose claims measured. 7.9% question-form, **zero
  carrying a citation**. Recommendation: no exemption; fix the report instead.
- Hygiene: stale P1 inbox ask closed with its caveat carried forward; the dead
  worktree removed (lock-holder confirmed gone).

## Decisions

D-21…D-27 in the register, each with its undo. **D-24 is in Sai's queue with
its stated basis retracted** — see Withdrawals.

## Agents

4 dispatched, all Opus-class, all justified: three as moat adversaries (a miss
ships), one as the solo gate (nothing reviews it before it reaches Sai).
~485K subagent tokens, 79 tool calls. Every one wrote to a file and returned
≤12 lines. Two of the four produced findings I had explicitly predicted against.

## Withdrawals

1. **"D-24 is fail-closed."** False. My eight-case enumeration contained no
   mixed-delimiter shape, and on `<!-- note －－＞ FABRICATED -->` the new order
   deletes text the old order scored. Text leaving the denominator points toward
   PASS, so the change was not mine to take on that reasoning. Retracted in the
   register; the change stays because reverting is worse; the authority question
   went to Sai.
2. **"The attack and honest cases are syntactically identical, so no
   deterministic rule separates them."** False. The discriminator is the verb's
   factivity (`argued` non-factive, `shown` factive), proved by a subject-swap
   control. My recommendation was replaced with a factive whitelist.
3. **"Round 7 found 22 and closed 2."** D-25 closed zero; D-24 closed three.
   22 found / 3 closed / 19 open.
4. **My recorded prediction that path B's `;` rule would yield an Error-B.**
   It flips FAIL→PASS on one keystroke, but citing the same clause directly also
   passes — propagation certifies nothing self-citation could not. The Error-B
   is one level down in T1's set-membership residual coverage.
5. **I silently narrowed the Path C agent's proposal** from "span must begin a
   source sentence ending in a full stop" to a `that`-complement rule, and
   inherited an undisclosed coverage gap — 3 of my own 5 tripwires have no
   `that`. Caught by the solo gate, not by me.

## Reflection

The meta-finding is that five of round 7's findings break **one law five ways** —
*never key a moat rule on a surface property the author controls*. Round 3 died
on a token-count floor, killed by a five-token fabrication. Round 4 died on its
proper-noun replacement, killed by the Shift key. Round 7 added three more: a
noun that doesn't end in "s", an apostrophe, and one keystroke of punctuation.
Length, capitalisation, spelling, punctuation. The project keeps rediscovering
this one instrument at a time and repairing that instrument, which is why it
keeps rediscovering it.

What made tonight different was the solo gate's correction on OI-MOAT-27. I had
concluded the class was unfixable deterministically and that the only sound move
was to pay a large Error-A. The reviewer showed the discriminator exists and has
the **opposite polarity** to everything tried before: factivity is a
**whitelist**, so an unlisted verb REFUSES. Every failed rule in this project's
history was a blacklist over an open class the attacker draws from. That is the
actual lesson under the five instances — not "don't use surface properties" but
**"never put the attacker on the enumerating side of the rule."** And the test
CLAUDE.md already states falls straight out of it: to ground a mined span the
attacker must find a source using a factive verb, and a factive verb means the
source asserts the claim, at which point grounding it is correct. The attacker's
only escape is to stop attacking.

The second thing worth keeping is smaller and more embarrassing. My own
fail-closed proof was an enumeration that confirmed exactly what it was built to
confirm. That is the standing trap — *the filter and the measurement were the
same operation* — for the fourth time in this project, and this time it was
inside the test file whose job was to prevent it. It also happened twice tonight
in one session: the first intra-rater draw contained none of the four rows that
could detect anchoring. I caught that one by asking "what could this not have
detected?" in code. I did not think to ask it of my own proof.

## Next

1. **Sai: the intra-rater test, 20 minutes.** Everything downstream forks on it.
2. **Sai: ratify or reverse D-24** (basis retracted), and rule on OI-MOAT-27
   (factive whitelist — calibrate and measure, materially cheaper than what I
   first recommended).
3. **Claude: round 8 is owed** and is named as owed. Alpha #7 is not met: 19
   findings are *recorded*, not *accepted*.
4. **PUSH IS DENIED.** 12 commits sit local. Not routed elsewhere.

---

# Session B, afternoon/evening — D-35, round 8, and a fix that refuted itself

Same session `d2b27b1f`, continuing after a compaction. Cron-advanced through
`docs/plans/OVERNIGHT-2026-09-12B-QUEUE.md`, items 5 → 6 → 7.

## What

**Item 5 — OI-UX-01, the absence-presentation defect (D-35).** Sai stalled on
6 of 20 intra-rater rows and asked *"nothing here?"*. Every one was a row whose
evidence reads as absent. One law, broken three ways: `""` for an uncited
claim, `[NOT IN STORE]` for a fabricated citation — the moat's flagship case
rendered as a template failure — and a bare `|||`-joined query list for an
absence claim. All three show an *absence* and ask the reader to infer an
*assertion*. Added `evidence_basis(claim, store)`, emitted on every `per_claim`
and `retained_appendix` entry.

**Item 6 — red-team round 8.** Three Opus adversaries against surfaces that did
not exist when round 7 was designed, plus a solo gate. **21 findings, 12
Error-B, 0 classes closed.**

**Item 7 — this close.**

## Why

Alpha criterion #7 requires an adversarial round run *after* the last moat
change. Round 7 predated J-19, J-20 and D-30…D-35. Two of round 3's findings
were evasions of fixes shipped hours earlier the same day, so a round that
predates the tree proves nothing about it.

## Done

| | |
|---|---|
| Suite | 532 → **563 passed / 2 skipped / 56 xfailed** |
| Corpus | byte-identical throughout; 52 labels gold, zero stale; no CR due |
| Register | D-35, D-36 (+ same-day amendment) |
| Jobs opened | J-21, J-22 (Sai), J-23 |
| Tripwires | 43 strict xfails over 20 findings |

## Decisions

- **D-35 fixed the PRODUCT surface, not the calibration scaffold.** Changing
  the scaffold's `evidence` column moves `claim_sha` and marks gold labels
  STALE — Sai's gate. And by **detectability** the report was the worse defect:
  the scaffold's version is loud (a human hit it twice on first read), while
  `per_claim` carried *no evidence field at all* and no test asserted that a
  report explains itself.
- **Deliberately not one shared renderer.** The report states the summary
  policy outright because a user acting on a verdict needs the reason; the
  labelling instrument must not, or reliability measures rule-reading
  (Goodhart — the same contamination D-34 avoided).
- **D-36 kept, not reverted**, after the gate proved it does not close its
  class: it is fail-closed and it closes a real shape, and reverting reinstates
  the hole.
- **J-21 specified and deliberately NOT built tonight.** A third leftward-scan
  patch at that hour is the shape with a 100% failure record here.
- **Whitelist additions escalated (J-22).** Growing a whitelist is normal
  maintenance and still PASS-enabling.

## Agents

| role | model | count | outcome |
|---|---|---|---|
| red-team adversary | Opus | 3 | 21 findings, all with run reproductions |
| tripwire author | Sonnet | 1 | 39 strict xfails, 0 XPASS, verified by me |
| solo gate | Opus | 1 | **3 corrected, 2 upheld** |

Sonnet for the tripwire work was routed on merit: mechanical conversion of
already-found findings, under `strict=True`, with my verification as the gate.
It held — I re-ran and audited every marker rather than accepting the report.

## Withdrawals — part of the record

1. **"R8A-01/02 CLOSED."** False, retracted the same hour. D-36 closed
   `that the <span>` and left `that <any other function word> <span>` open,
   denial included, at PASS/100.0.
2. **"No new Error-A; the corpus is byte-identical."** False inference.
   Byte-identical means the 52 rows lack the shape. `concluded that` /
   `indicates that` grounded before D-36 and FAIL after.
3. **`evidence_basis` "mirrors `ground()`'s branch order exactly."** False when
   written — there is no RELATIONAL branch. Withdrawn from the docstring.
4. **`555/2/14` in a commit message** — not reproducible at that tree, which
   had moved two commits. Caught by the gate.

## Reflection

The round's most interesting finding is not a bug, it is a shape. J-19 shipped
this morning with sound logic and was wired into **one of its two call sites**,
so it was simultaneously correct and absent. No amount of case enumeration
finds that, because every case you test goes through the site you wired. I
proposed the lesson as *"enumerate call sites, not cases"*; the gate sharpened
it, having found no *fully* unreached helper: the right form is **"enumerate
call sites AND the input shapes that reach them"** — D-36 is a guard that *is*
called and still does not fire.

What makes this worth writing down is the second-order version. I predicted my
own failure mode in the gate's dispatch prompt — *"I enumerate cases that
confirm what I already believe; assume my test file has that blind spot"* — and
then wrote a test file whose every fixture used `that the …`. **Naming a bias
did not prevent it.** The prediction was accurate and useless on its own; what
caught the bug was a reader with no stake in the conclusion, attacking a
conclusion already committed so it could not be revised to dodge them. That
ordering is the whole mechanism, and it is cheap: one agent, one prompt, run
after you have written down what you believe.

## Next

Item 7 complete. **J-21** is the next build (sentence-bounded complement
detection via `syntok`, needs its own adversarial round). **J-22 is Sai's** and
blocks nothing else. Do NOT build T3. Do NOT change a gold label.
