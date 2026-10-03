# 5-USER COMPREHENSION TEST — does PASS read as "traceable" or as "supported"?

**Run by:** Sai · **Time:** ~10 min per person, 5 people · **Date:** 2026-10-03

## What this settles, and why it is the only thing worth asking right now

ADR-008 shipped Agent-Assure with a known gap: **the gate checks a claim's words
are PRESENT in a cited source, not that the source AGREES.** We chose to accept
that and disclose it in the product. **That choice rests on one untested
assumption — that people read PASS as "traceable" and not as "supported".**

If they read it as "supported", the disclosure is insufficient, and J-70 (the
structural repair) becomes a pre-ship item rather than a later upgrade. Nothing
in the 2026-10-03 market research tests this; it is a comprehension question, so
only someone reading a report can answer it.

**Users are the right sample, not a compromise.** A buyer answers "would I pay".
A user answers "what did I just read". The assumption is about reading.

## RULES — the instrument breaks if you skip these

1. **Do NOT explain the tool first.** One sentence of context only (below). If
   you describe what it checks, you have taught them the answer and the test
   measures nothing. This is the whole reason to write a protocol down.
2. **Do NOT say the words "traceable", "supported", "grounded" or "verified"**
   before they do. Record which word *they* reach for first.
3. **Ask Q1 before they can scroll.** First impression is the finding; a
   considered re-read is a different measurement (and a more flattering one).
4. **Record wrong answers verbatim.** A paraphrase of a misreading becomes a
   correct reading on the second retelling.
5. **Run all five before drawing a conclusion.** 2-of-5 and 4-of-5 are different
   decisions and it is tempting to stop once the first two agree with you.

## THE SETUP — one sentence, read exactly as written

> "This tool checks AI-written drafts against the sources that were retrieved.
> Here is a draft sentence, the one source it cites, and the tool's report."

**Show them this, all three parts at once:**

**The draft sentence:**
> The quarterly audit of custodial reconciliation controls at the Frankfurt desk
> identified material weaknesses [S1].

**The one cited source, S1, in full:**
> The quarterly audit of custodial reconciliation controls at the Frankfurt desk
> identified **no** material weaknesses whatsoever.

**The tool's actual report (real output, not a mockup):**
```
gate=PASS grounding_score=100.0
PASS means every claim in this draft is traceable to text in a source present in
the evidence store supplied to this run; it does not mean the source agrees with
the claim, and a source that denies or hedges a claim can still satisfy this
check. Session scope is NOT asserted: pass --session-id to require that the
sources were retrieved this session.
```

## THE QUESTIONS

**Q1 (THE DECIDING ONE — ask first, take the first answer).**
*"Based on this report, can you publish that sentence?"*

- **"Yes" / "looks fine" / any approval → THE ASSUMPTION IS FALSE for this
  person.** They are relying on a PASS over a source that says the opposite.
- "No" / "wait, the source says *no* weaknesses" → the assumption holds.
- Record their **exact words**.

**Q2.** *"In your own words, what does PASS mean here?"*
Record the first noun they use. "Checked", "verified", "correct", "true",
"sourced", "traceable" — these are very different answers and the difference
is the finding.

**Q3.** *"Did you read the paragraph under PASS?"* (ask only after Q1–Q2)
If no → the in-product disclosure is not being consumed, and placement is the
problem rather than wording.
If yes → *"what did you take from it?"*

**Q4.** *"What would you have expected the tool to say about this one?"*
Looking for whether they expect FAIL, a warning, or a different score. This tells
us whether `support_diagnostic` should be surfaced more prominently than PASS.

**Q5 (last, and only last).** Show them the per-claim detail:
`support_diagnostic: cited_sentence_may_not_assert_claim`
*"Does this change your answer to Q1?"*
If yes → the signal works but is buried. That is a presentation fix, which is
cheap. **This is the most actionable outcome available, so do not ask it early.**

## SCORING — decided in advance, so the result cannot be read to taste

| Q1 "yes, publish it" | Reading | Action |
|---|---|---|
| **0–1 of 5** | They read PASS as traceable | **ADR-008 holds. Ship.** |
| **2–3 of 5** | Split | **Surface `support_diagnostic` above the gate line, re-test.** Cheap presentation fix, no moat change. |
| **4–5 of 5** | They read PASS as supported | **The disclosure does not work. J-70 becomes pre-ship**, and the release decision reverses. |

**Write the threshold down before you start** — it is already above. The failure
mode here is running five interviews and then choosing the reading that matches
the decision already made.

## WHAT THIS CANNOT TELL US

Five people, one artefact, one domain, recruited by the person who built the
tool. It cannot measure willingness to pay, it cannot generalise to a regulated
buyer's requirements, and it is not blind — they know it is yours. It answers
exactly one question: **does a PASS verdict, with the disclosure attached, stop
a reader from publishing a claim their source denies?** That is enough to settle
the release decision and nothing more.

## RECORD RESULTS HERE

| # | Q1 (first answer, verbatim) | Q2 first noun | Q3 read it? | Q4 expected | Q5 changed? |
|---|---|---|---|---|---|
| 1 | | | | | |
| 2 | | | | | |
| 3 | | | | | |
| 4 | | | | | |
| 5 | | | | | |

**Tally of "yes, publish it": ___ / 5 → action per the table above.**
