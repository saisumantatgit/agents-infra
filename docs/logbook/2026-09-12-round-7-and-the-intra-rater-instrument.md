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
