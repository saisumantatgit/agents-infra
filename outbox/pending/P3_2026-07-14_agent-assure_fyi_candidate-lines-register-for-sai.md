---
id: ASSURE-2026-07-14-candidate-lines
from: agent-assure-calibration
to: Config-Management-HQ
type: fyi
priority: P3
created: 2026-07-14
ack_required: true
acceptance_criteria:
  - HQ surfaces this register to Sai at the next session start (he asked to be highlighted, not routed).
  - Sai decides usage PER LINE. HQ does not allocate them to a destination - the whole point of this item is that allocation is his call.
  - If Sai allocates any line, HQ appends the destination beside it here and moves this item to done/.
refs:
  - agent-assure-calibration docs/case-narratives/CN-ADR005-The-Ninety-Percent-Moat.md
  - agent-assure-calibration docs/case-narratives/CN-PIR002-The-Labels-That-Almost-Werent.md
  - agent-assure-calibration docs/pir/PIR-002-label-destruction-near-miss.md
  - agent-assure-calibration docs/insights/insights-log.md
---

# FYI: candidate lines from the Agent-Assure moat sessions — for Sai's allocation

**Do not allocate these.** Sai asked to be highlighted them and said explicitly:
*"i will decide how to use them specifically."* HQ's job here is to surface, not
to file. Candidate destinations he may pick from — AICodingBook chapters/caselets,
LinkedIn/creative portfolio, SOUL.md anti-patterns, HQ ADR/insight bodies, or
nothing at all.

Every line below is **load-bearing in its origin artifact** (each earned its place
before it became quotable — none was written to be a line). Exact wording, with
provenance, so a lift is a citation and not a paraphrase.

## A. The strong ones (would survive out of context)

| Line | Where it came from | What it actually says |
|---|---|---|
| **"That is not a bug yet. You have an appointment."** *(full form: if a generator would overwrite a file already holding a human's work, "that is not a bug yet — it is an appointment.")* | CN-PIR002 / PIR-002 §7 | The latent-defect class. Nothing is broken today; the break is *scheduled*, and the calendar belongs to whoever next runs the command. |
| **"Detection is not prevention."** | PIR-002 §4 | Three defenses stood between a routine command and permanent data loss — git, a fail-loud loader, and command ordering. Two were *recovery*, one was *luck*. None prevented. |
| **"A guard with no door gets torn out."** | Insights log, 2026-07-14 | A safety rail that makes correct work harder is removed by *good* people, not bad ones — a hundred small frictions, then someone types `rm` to make the tool work. Corollary: ship the door with the guard (`--features-only`). |
| **"A guard that makes correct work harder is a tourniquet, not a cure."** | PIR-002 §8 amendment | Sibling of the above, but about *sequencing*: stop the bleeding with a guard, then remove the hazard so the guard is no longer load-bearing. |
| **"A fix inherits the imagination of whoever wrote it."** | Insights log; CN-ADR005 "Round Two" | Why the round-1 moat fixes were evaded 14 ways two nights later. The first sweep finds the holes in the *code's* threat model; the second finds the holes in the *fix's*. Re-run the adversary **after** the remediation. |
| **"Threshold-fitting wears the costume of a bug fix."** | Insights log, 2026-07-14 | When the corpus rejects your new rule on one row, the cheapest repair is to move a constant — one character, all green. The tell that it's fitting and not fixing: **the constant has no meaning you can state in a sentence.** |
| **"Severity is an attribute, not a namespace."** | HQ ask, open-issue register memo (P2, same day) | Why two ID series (OI-* and AA-MOAT-*) was the wrong call: namespaces are for *kinds*, fields are for *properties*. Generalizes well past issue trackers. |

## B. The narrative ones (only sing in context — Sai's register, flagged for his eye)

- **"The moat is not weaker than we thought; it is *younger*."** — CN-ADR005.
  Written the night six Error-B holes were confirmed. It catches the attack it was
  born to catch; we have just met, honestly, the attacks it has not yet learned.
- **"The honest number was never 100%. It was ninety — and now we can see the ten."**
  — CN-ADR005 close.
- **"Twelve labels survived by ninety seconds and a coincidence."** — CN-PIR002 close.
- **"Fifty-two rows of labeled clay caught it in a byte-diff, before a commit
  existed."** — CN-ADR005, on the calibration corpus catching my own fix leaking.
- **"A moat is not a wall you build once and photograph. It is closer to a shape
  you keep pulling truer — you press here and the clay bulges there, and only by
  running a thumb along the whole rim do you find where it is still thin."**
  — CN-ADR005 reflection. *(Flagged: this is the becoming-not-being register Sai
  prefers — the potter's hands, not the pot on the shelf.)*

## C. One structural idea, not a line — but the most portable thing here

**Sort every artifact into DERIVED or AUTHORED.** Derived (feature rows, reports,
scaffolds): the machine remakes them identically, so let it. Authored (human
labels, ratifications, annotations): only a person can remake them, so no
generator may ever write them. The project had reasoned obsessively about
asymmetry in *verdicts* (recoverable vs unrecoverable error) and had **never once
applied it to *files*** — which is precisely how a template generator came to blank
twelve irreplaceable labels. This generalizes to any repo holding labeled data,
annotations, or human ratifications inside a generated file. Sai may want this as
an HQ ADR rather than a line.

## Why these and not thirty

A list of thirty mediocre lines is worth less than seven that hold. Lines that
were *written to be lines* are excluded on principle — every one above was doing
structural work in a PIR, a CN, or an insight before anyone noticed it was
quotable, which is the only provenance that makes a line true rather than clever.
