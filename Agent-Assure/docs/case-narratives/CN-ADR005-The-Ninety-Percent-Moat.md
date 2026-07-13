# CN-ADR005 — The Ninety-Percent Moat

*Companion case narrative to ADR-005 (gate score-bar semantics). Written
2026-07-12, the night the moat was measured instead of assumed.*

---

## The promise on the tin

Agent-Assure has one sentence it stakes everything on. It is in the CLAUDE.md,
in the SOUL, in the demo script's climactic beat:

> a fabricated citation cannot talk its way past this gate, because no LLM judges
> grounding — the verdict is a mechanical fact about the evidence store.

The demo proves it, cleanly. Point the gate at `draft-fabricated.md`, whose
`[S3]` was never retrieved, and it returns FAIL with `UNVERIFIED_CITATION`
naming the fake. No model in the loop, nothing to negotiate with. It is a good
demo because it is a true claim.

The trouble is the word *a*. "**A** fabricated citation cannot pass" is a claim
about one attack — a fabricated *source marker*. Somewhere between the code and
the pitch, the article quietly widened: everyone had started to hear "**no**
fabrication can pass." Those are different sentences. One was tested. The other
was believed. This is the story of the night we found the gap between them, and
of why 334 passing tests never once pointed at it.

## The sweep

The occasion was mundane: a token grant about to expire, and a standing
instruction to spend it on whatever hardens the product most. For a
verification gate, that is not "run more claims through it" — that is
*adversarial reproduction*: build drafts designed to break the moat, from as
many independent angles as possible, and see which ones the gate wrongly waves
through. Twelve attack classes, one frozen two-source store (S1 Redis, S2
PostgreSQL), forty-nine adversarial drafts, twenty-six agents. Each agent blind
to the others, each prompted to *refute* the moat rather than confirm it.

Six of the twelve classes came back carrying a wrongful PASS.

That number should stop you, because it contradicts the sentence on the tin. The
correct response to "the sweep says your core property is false six ways" is not
to write it down — it is to distrust it. Agents near a token boundary produce
confident, well-formatted, wrong things. A report is testimony. So the finding
was treated as an accusation, not a fact, and every one of the six was put back
through the gate **by hand**, on the working branch, watching the exit code with
my own eyes.

All six reproduced. `gate = PASS`, `exit 0`, on drafts that assert things the
store does not contain.

## Two roots, not one

The synthesis agent had a tidy story: one "threshold-dilution" thread runs
through all six — pad a fabrication below 10% of a long draft and the 90% score
bar lets it ride. Tidy, and *wrong*, and the way you can tell it is wrong is the
most useful thing in this narrative.

Two of the six drafts scored **100** with an **empty** appendix. If dilution
were the whole story, there would be a retained bad claim being outvoted — but
here the gate had marked the fabricated claim itself `GROUNDED`. Dilution wasn't
involved. The contradiction between "it's all dilution" and "these two scored a
clean 100" is not noise to average away; it is a *locator*. It points at a
second, independent defect the tidy story would have buried.

So: **two roots.**

**Root A — the ratio dilutes.** `PASS` fires on `grounding_score >= 90`. A ratio
is a proportion, and a proportion can always be diluted: nine true claims plus
one drifted number (128000 → 12800) is 90.0%, and 90.0 clears 90. The gate
*catches* the drift — it sits right there in `retained_appendix` as
`UNVERIFIED_NUMBER` — and passes the draft anyway. The detection works; the
detection just isn't allowed to block the verdict. The same vector cleared a
fabricated `[S1a]` citation (AA-MOAT-006): correctly flagged, correctly
appended, still nine-to-one outvoted into a PASS.

**Root B — the tiers over-ground.** Here the gate does something worse than
ignore a caught fabrication: it fails to catch it at all, scoring the bad claim
`GROUNDED` on a clean 100. Four distinct mechanisms, each a different organ of
the gate failing in its own idiom:

- *The verbatim short-circuit.* "Redis is an in-memory data structure store
  that is, by every available measure, **the single fastest database ever
  engineered** [S1]." The first eight tokens are a verbatim span from S1, so T1
  returns True and grounds the *entire sentence* — including a superlative the
  store never makes. An honest quote is used as a passport for the lie stapled
  to it.

- *The relation that is never read.* "Redis sustained 128000 ops/sec,
  **decisively outperforming PostgreSQL** under identical durability constraints
  [S1]." S1 never names PostgreSQL. The two-source relational rule confirms the
  *endpoint nouns* are present in the stores and calls it grounded — it checks
  that the words exist, not that the relationship between them is supported.

- *The unit that is invisible.* "128000 operations **per minute** [S1]" grounds
  against "128000 operations per second." The numeric tier compares the
  magnitude and the percent-vs-absolute flag; the dimensional unit — the entire
  meaning of the number — is not in the token it compares. Off by a factor of
  sixty, `GROUNDED`.

- *The absence that anchors on the wrong word.* "There is no benchmark showing
  Redis above 500000 ops/sec" grounds as `ABSENCE_SUPPORTED` because the subject
  extractor lands on the head noun "benchmark," which happens to appear in the
  retrieval provenance of the real queries. The gate confirms we searched for
  *something benchmark-shaped*, not that we searched for the specific negated
  proposition. The 2-query absence rule is satisfied by a coincidence of generic
  vocabulary.

Root A is one decision (ADR-005): make PASS a predicate — *zero retained
violations* — instead of a proportion. Root B is four separate tier repairs, and
notably ADR-005 does **not** touch it: an empty-appendix rule cannot help when
the bad claim never reaches the appendix. Conflating the two would have shipped a
"fix" that closed a third of the holes and declared victory.

## Why the green suite was blind

The load-bearing fact of this whole episode: **334 tests passed the entire
time.** They still do. Not one of them flagged the moat's actual boundary, because
tests written by the gate's authors encode the gate's authors' model of the
attack surface — and the attack surface is exactly where an author's imagination
runs out. The suite verified that the mechanisms the team *thought of* behave as
the team *intended*. It could not verify the property the team *believed* but had
never operationalized: "no fabrication passes." You cannot assert your way to
that property; a passing test is the author agreeing with themselves.

What found the gap was structurally different from a test: an adversary with no
stake in the gate being right, generating inputs the authors did not anticipate,
scored by the gate's own mechanical verdict. Self-verification cannot reach the
assumption you didn't know you were making. Only an outside process can — and the
red-team is that outside process wearing a token budget.

## What it drove

- **ADR-005 (Proposed):** PASS requires an empty retained appendix. Closes Root A.
  Blocked on Sai — it moves the gate bar and raises Error-A (recoverably), which
  is precisely the class of change the escalation rule reserves for the human.
- **`docs/open-issues/OPEN-ISSUES.md`:** all six as AA-MOAT-001…006, each with
  its reproduced verdict, mechanism, root, and systemic fix sketch.
- **`tests/red_team_moat/`:** the six drafts, frozen, as **strict xfail**
  regressions — proven red (they xfail today because the gate wrongly passes
  them), and rigged so that the day a fix lands, the XPASS turns the suite red and
  drags whoever fixed it back to delete the marker. The hole cannot be quietly
  reopened.

Nothing was patched. Every fix here alters the Error-A/Error-B trade-off, and the
one discipline that is not negotiable on this product is that the human, not the
model, moves that dial.

## Lessons

1. **Audit the article.** "*A* fabrication cannot pass" and "*no* fabrication can
   pass" are different guarantees. Products drift from the first to the second in
   the marketing, never in the code. Write down the property you actually hold,
   in the exact words the code earns.
2. **Testimony is not evidence, especially near a discontinuity.** Six confirmed
   findings from an agent swarm are an accusation to reproduce, not a result to
   record. The reproduction cost twenty minutes and changed a "6 violations"
   headline from *plausible* to *load-bearing*.
3. **A contradiction inside a synthesis is a locator.** "It's all one root" versus
   "two of them scored a clean 100" was the seam. Don't average it; dig there.
   The second root was living in it.
4. **The green suite measures agreement, not safety.** A gate's tests encode its
   authors' threat model. The moat's real boundary is found by an adversary, not
   by the suite — so the adversary belongs *in* the suite, as a permanent
   xfail-to-green tripwire.

## Reflection

A moat is not a wall you build once and photograph. It is closer to a shape you
keep pulling truer — you press here and the clay bulges there, and only by
running a thumb along the whole rim do you find where it is still thin. Tonight
the thumb was twelve adversaries and a pair of eyes on an exit code, and the rim
was thin in five places nobody had thought to touch. The gate is not weaker than
we thought; it is *younger* — it catches the attack it was born to catch, and we
have just met, for the first time honestly, the attacks it has not yet learned.
The honest number was never 100%. It was ninety — and now we can see the ten.

## Epilogue (2026-07-12, the morning after)

Sai woke, read the six, and ruled: ADR-005 accepted as proposed; the numeric
unit fix and the absence anchoring fix greenlit; the T1 overreach and the
relational predicate deferred to their own decisions. By the same evening four
of the six xfails had flipped XPASS and become permanent green guards, and the
suite stood at 351 passed + 2 xfailed — the two that wait, still visible,
still red where it is honest for them to be red.

One more lesson insisted on being learned during the fixing: the first draft
of the absence fix anchored on named entities alone, and the calibration
corpus immediately produced a counterexample — q22, a labeled violation, flipped
to supported because every query in its session happened to mention the
product name. The regeneration diff caught it before any commit. Even the fix
for a moat hole needs its own adversary; ours turned out to be fifty-two rows
of labeled clay.

---

## Round Two (2026-07-14): the fix gets red-teamed

The four fixes shipped on the 12th were verified the way fixes usually are —
against the attacks that motivated them. All six original drafts stopped
passing; the suite went green; the guards went permanent. By every measure
available *from inside the fix*, the holes were closed.

Two nights later a second sweep asked a different question: not "does the fix
stop the attack it was built for?" but "what does the fix actually *check*?"

The rate-qualifier fix compared "per second" against "per minute" — but it read
a rate only in the forms `per <word>` and `/<word>`, within two words of the
number. So the gate that now refuses *"128000 operations per minute"* happily
certified **"128000 operations each minute"**. And *"every minute"*. And *"a
minute"*. And *"per-minute"* with a hyphen. And *"hourly"*. And a rate stated
before the number. And — the one that should be framed and hung on a wall —
**"128000 operations рer minute"**, where the `р` is Cyrillic U+0440. NFKC
normalization, which the codebase applies religiously at every text boundary,
does not fold Cyrillic `р` to Latin `p`. The homoglyph didn't defeat the rate
check; it made the rate *invisible*, and an invisible rate meant "no rate
asserted", which meant the bare number 128000 matched the source's 128000, and
the draft sailed through at score 100.

Nine phrasings, one alphabet, fourteen wrongful PASSes.

The lesson is not that the first fix was bad. It is that **a fix inherits the
imagination of the person who wrote it**, exactly as the original code did. The
first round found the holes in the gate's threat model; the second round found
the holes in the *fix's* threat model. There is no reason to think a third
sweep would come back empty — and that is precisely why the adversary now lives
in the test suite rather than in a report.

## The corpus, again, as the fix's own adversary

The repair for the absence leak went through two designs. The first counted how
many of the negated subject's content words appeared in the session's queries,
and demanded half of them. It closed the attack. It also flipped corpus row q37
— *"There is no antidote approved for the toxin in current guidelines"*, a
**labeled-grounded** claim, backed by two genuinely targeted searches — into a
false alarm, because the rule was counting adjectives ("approved", "current")
that no researcher would ever type into a search box, and because the claim
said "guidelines" where the query said "guideline".

Fifty-two rows of labeled clay caught it in a byte-diff, before a commit
existed.

The tempting repair was to lower the coverage threshold from 0.5 to 0.4 — one
character, tests green, everybody home. That is threshold-fitting: tuning a
constant until a single row behaves, with n=1 of evidence and no principle
underneath. The actual repair was to change what the rule *means* — a query
must carry the subject's head noun **and at least one other content word of the
subject**, with plural stemming so "guidelines" meets "guideline". That rule
distinguishes *the session searched for this thing* from *the session used this
word*, which is the property the fix was always reaching for. q37 grounds. The
streaming-ingest fabrication does not. And q30 — a **labeled violation** the
gate had been wrongly certifying since before any of this began — flipped to a
violation verdict on its own, unasked.

The moat is measured now, not assumed. It is also, still, younger than its
promise.
