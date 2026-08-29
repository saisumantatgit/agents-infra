# CN-OI-MOAT-11 — The Number the Attacker Chose

*Companion case narrative to the 2026-08-30 autonomous session and the
OI-MOAT-11…15 cohort. Written the same day, a few hours after the fix it is
about was found to be broken.*

---

## A backlog that was not what it looked like

Three holes had been sitting open in the register since mid-July, each with the
same annotation: *deferred by Sai's ruling; needs its own decision.* They had
the settled look that items acquire after a few weeks — not forgotten, exactly,
but no longer questioned. The reason they were waiting had stopped being
examined, because "waiting on a human ruling" is a complete-sounding
explanation.

The session that opened them again did so with one question: *does this
actually require a human ruling, or is it merely unresolved?* Those are
different conditions with the same appearance. An item that needs a judgment
call only a person can make will sit forever until that person makes it. An
item that is simply undone looks identical from the outside, and also sits
forever, for no reason at all.

What separated them turned out to be a property nobody had named. The
escalation rule says to stop for *any change that alters the Error-A/Error-B
trade-off*, and all three items plainly altered something. But the gate's whole
architecture rests on an asymmetry: a false alarm is recoverable, a certified
fabrication is not. A change that can only move claims **away** from PASS
cannot manufacture the unrecoverable error, no matter how wrong its author is
about the details. A change that can move a claim **toward** PASS can. Read
that way, the rule is not about how important a change is; it is about whether
being wrong about it costs anything you cannot get back.

Under that reading the backlog sorted itself in about a minute. Three items
were fail-closed, and were fixed. A fourth — propagating a citation across a
conjunction split, which would let clauses that are currently blocked become
groundable — was not, and stayed exactly where it was, with the question
written out in one line. The pile had never been one pile.

## Three fixes, and a corpus that kept disagreeing

The fixes themselves were unremarkable, and each was interrogated by the same
adversary: the 52-row calibration corpus, regenerated after every change and
diffed byte-for-byte.

It earned its keep on the relational fix. The rule had been that a relation is
grounded when each of its endpoints appears in some cited source — so
"marketing spend rose" in one document and "signups rose" in another together
certified *"increased marketing spend drives higher customer signups."* The new
rule demanded that some source actually assert the link. Regeneration flipped
exactly three rows, and all three were already labeled *violation* by a human.
Two more relational rows, labeled *grounded*, did not move. The corpus did not
merely fail to object; it agreed with the fix on all five rows it had an
opinion about. That is a different and much stronger thing than a green test
suite, which can only tell you that nothing you thought to check has changed.

By evening the three items were closed, the thresholds were coherent for the
first time in six weeks, and the suite was green with no deliberate failures
left in it. It was, briefly, a finished-looking day.

## The five-token sentence

Then the adversary ran.

The standing rule in this repo is that a fix to the moat gets red-teamed too,
and it exists because round 1's four fixes were evaded fourteen ways by round
2. Round 3 was dispatched against fixes that were hours old. It came back with
seventeen wrongful PASSes over five mechanisms, and two of them were evasions
of that same morning's work.

The one worth telling is this. To stop a fabrication from escaping the scored
denominator by simply dropping its verb — `Redis: unquestionably the fastest
datastore in all of human history.` reads as an assertion to any human and
classified as a non-claim to the gate — the fix drew a line: a verbless
fragment carrying six or more content words is a claim, not a heading. Six was
chosen because it is about the length of a real section label, and it closed
the attack it was written against.

The adversary wrote:

```
PostgreSQL: unrecoverable corruption under load.
```

Five content words. `gate=PASS, score=100.0`.

There is nothing clever in that. It is not an exploit so much as an
observation: the defender publishes the threshold, in code, once; the attacker
reads it and writes to it. **A number that separates benign from malicious is a
parameter the attacker controls and the defender does not.** Six was never
going to hold, and neither would five, or four — the number was not the
problem, the *shape* of the answer was.

The tell had been there when it was written, and it is the same tell this
project had already recorded once, one level down, in an insight about tuning
constants until the corpus agrees: **the number had no meaning that could be
stated in a sentence.** "About the length of a real heading" describes the
benign class. It does not name a property that distinguishes the two classes,
and only such a property can be defended.

The property, once looked for, was not subtle. A heading or a label **names**
things. An assertion **predicates** something about them. `Redis Postgres
MongoDB` names; `PostgreSQL: unrecoverable corruption` predicates, and it
cannot stop predicating and remain a fabrication. The test that follows —
whether the fragment's content words are all proper nouns, or whether it
introduces descriptive content — has no dial on it. An attacker cannot shorten
their way underneath it, because the tokens that make the claim a claim are the
same tokens the test looks for.

## The check that was disproved by adding evidence

The second finding was worse in what it implied, and quieter.

Guarding a verbatim span against certifying words it never checked seems to
call for a coverage test: every content word of the claim should appear in the
cited sources. Written the obvious way, that test pools the cited sources
together and checks membership in the union.

The adversary submitted a claim attributing Redis's throughput number to
PostgreSQL, and cited it twice. Cited to S1 alone the gate correctly returned
`FAIL` — "postgresql" appears nowhere in S1. Cited to *both* sources it
returned `PASS` at 100.0, because S2 contributed that single missing word and
nothing else of relevance.

Adding a citation had made a false claim easier to ground. In a tool whose
entire purpose is that claims must trace to evidence, more evidence made
verification weaker. It is difficult to construct a sharper inversion of a
product's premise, and it arrived not from a subtle bug but from the most
natural way to write the check.

The general form is worth keeping: **a per-claim check must be able to name the
source that discharges it.** Pooling first and testing second is what lets an
unrelated document launder a term into a claim's support. A check that cannot
say *which* source satisfied it is not doing grounding; it is doing set
membership, and set membership over a large enough union is satisfied by
anything.

## The corpus, a third time, refusing a fix

One more, because the pattern is now impossible to dismiss as coincidence.

The fourth finding was that the absence path reasons only over what was
*searched* and never over what was *found* — so against a store consisting
entirely of benchmark throughput figures, `No benchmark throughput figures
exist.` was certified as a supported absence. The gate asserting the direct
opposite of its own evidence is about as bad as this system gets.

The obvious repair: refuse an absence when the retrieved sources mention its
subject. Written, tested, suite green.

Then the corpus regenerated, and three rows moved — all three labeled
*grounded* by a human, all three now false alarms. Their supporting sources
read: *"No recall evidence was found in the manufacturer's safety bulletin
archive."* *"The public recall database returned zero results."*

Those sentences contain the subject's words **precisely because they report the
absence.** Presence is not contradiction. The repair had been checking whether
the store *talked about* the subject, while believing it was checking whether
the store *contradicted* the claim, and on the corpus's evidence those are
opposite verdicts on the same text. The distinction the check actually needed —
an affirmative mention refutes an absence, a negated one corroborates it — is
one sentence long and was invisible until the labels objected.

The test suite had nothing to say about any of it. Only the corpus did, and
only because regenerating and diffing it is mandatory rather than advisable.
That is now three sessions running in which the calibration corpus has caught a
bad fix that a green suite waved through.

## What the day was actually about

The visible result is nine closed register items and a moat with five more
holes in it than anyone knew about that morning. The durable result is smaller
and less comfortable.

Every one of the three failures above has the same interior. A rule was written
that described the benign case accurately — headings are short; cited sources
support claims; sources that mention a topic speak to it — and each was
mistaken for a rule that distinguishes the benign case from the malicious one.
Those are not the same rule, and the gap between them is invisible from inside,
because the benign examples all pass. It takes an adversary, or a corpus of
human judgments, standing outside the author's imagination, to find the edge
the author defined the rule to exclude.

Which is the same lesson the ninety-percent moat taught in July, arriving by a
different road: the thing that had been tested was not the thing that was
believed. The believing is the fast part. The testing is the whole job.
