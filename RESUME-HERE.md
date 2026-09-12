# RESUME HERE — Agent-Assure

**Last session:** `d2b27b1f`, closed **2026-09-13 01:30 IST** (overnight after the
launch analysis; round 9).
**Branch:** `agent-assure-calibration-run` · clean, **pushed, 0 ahead.**
**Suite:** `cd Agent-Assure && uv run pytest -q` → **564 passed, 2 skipped, 60 xfailed.**
Trust the RUN, not this number.

Read in this order: this file → `docs/logbook/2026-09-13-the-launch-question-and-what-provenance-actually-is.md`
→ `docs/jobs/REGISTER.md`.

---

# START HERE — one decision is Sai's, and everything waits on it

**Ship PROVENANCE-only, or fund ENTAILMENT?** Not made. Do not presume it.

| | provenance | entailment |
|---|---|---|
| what it answers | is every citation a source actually retrieved this session, verbatim? | does the source support the claim? |
| the founding spec | **its one-sentence identity** — "mechanically traced to a source that was actually retrieved this session" (HQ repo, `docs/superpowers/specs/2026-06-20-agent-assure-design.md` §1) | the means (§4.3 T1/T2/T3), not the promise |
| state | **NOT yet true** — round 9 found 2 ERROR-B; fix list is 4 items, all fail-closed | ~31 open ERROR-B classes; nothing measured fixes them |
| human blockers | none | q25, J-22, second reader, calibration |

## Why entailment is not buyable right now — measured, not argued

- STORM verifies its own citations with an LLM at ~85%, and names "red herrings"
  (q25's shape) as its unsolved failure.
- Nothing on the standard benchmark clears 80%. An API judge buys 0.6pp over a
  770M local checker at 446× the cost, is non-deterministic at temperature 0,
  and is prompt-injectable ~91% of the time.
- **Our own diagnostic:** HHEM-2.1-Open catches 3 of 17 open attacks, **all 3
  already caught by the gate — union gain zero.** It is right only where it
  would have to *lift* a flag, which the moat forbids.
  `docs/research/diagnostic/RESULTS-2026-09-12.md`

## If provenance — the launch fix list (all fail-closed)

1. **Run the unresolved-citation check in `ground()` BEFORE the kind dispatch.**
   Today RELATIONAL and ABSENCE claims skip it: `[S2][S3][S99]` and
   `[S99] We found no evidence…` both certify **PASS 100.0**. Fixing either
   checker alone leaves the other open.
2. **`load_store` must raise** on a duplicate normalised id, duplicate JSON keys,
   wrong types, and a `tool`/`full_text_source` mismatch. Today a duplicate
   `source_id` launders a summary to verbatim by line order.
3. **Comment stripping must detect code the way CommonMark does** (tilde fences,
   indented blocks, escaped openers) — or stop stripping comments. One family:
   R8B-01/02, R9P2-05/06/07.
4. **Spec §7.5 — absence claims fail OPEN on an incomplete store.** The hook
   does not capture WebSearch, search tools, Bash, Grep/Glob or most MCP
   readers, and auto mode routes file reads through Bash. **Remedy touches hook
   registration → Sai.** Launch option: exclude absence claims.
   `Agent-Assure/docs/reports/SPEC-7.5-STORE-COMPLETENESS-2026-09-13.md`

Then **round 10, provenance only**, against the repaired tree.

## Withdrawn — do not repeat these

- "The founding spec does not exist." It is in the HQ repo.
- "Provenance cannot lose a red-team round." It lost round 9.

---

# Round 8 (2026-09-12) — closed nothing; the endorsement-guard lesson

**Round 8 ran 2026-09-12** (`docs/plans/reports/RED-TEAM-R8-2026-09-12.md`):
**21 findings, 12 Error-B, over three surfaces. Zero classes closed.**

**Do not read the xfail count as decay.** 14 → 56 is not the gate getting
worse; it is 43 tripwires over holes that were already there and unrecorded
this morning. Each fails today and goes RED the day someone fixes it.

## The one thing to understand before touching the moat

`_span_is_hedged` and `_span_under_nonfactive_complement` are called from
T1's **exact-containment** path. The **≥8-token span path** applied neither.
So the moat's endorsement check fired for short claims and was silent for long
ones — **the author switched it off by typing more words.**

D-36 narrowed that. It did **not** close it:

```
source:  A blogger speculated that at least three Redis nodes silently lose
         acknowledged writes on restart under default settings.
claim:   same text, frame stripped [S1]
verdict: GROUNDED    gate: PASS    score: 100.0     (denial form: identical)
```

The leftward scan skips only DETERMINERS, so `that the …` is caught and
`that at least three …` is not. **Every fixture in the test file that
certified D-36 used `that the …`** — the fix and its test shared one blind
spot. R8A-01 was itself the fix for round 7's quote-mining class, so this is
the third link in one chain, and it is the convention proving itself:
*a narrow fix closes the fixture it was written against and leaves the class
open.*

**J-21 is the sound fix and it is specified, not built:** bound the
complementizer search AND the factive prefix to the SOURCE SENTENCE containing
the span, using the `syntok` segmenter `decompose` already depends on. One
rule closes this residue and R8A-03 together. **It needs its own adversarial
round before anyone calls it closed.**

## The method finding, which outlives the bug

A guard can be **correct and unreached**. J-19's logic was sound the day it
shipped and was wired into one of two call sites. No case enumeration finds
that, because every case you test goes through the site you wired.

**Enumerate call sites AND the input shapes that reach them.**

And the second-order version, which is the reason the solo gate is not
optional: I *predicted this exact blind spot in the gate's own dispatch
prompt*, then wrote a test file that had it. Naming a bias did not prevent it.
What caught it was an outside reader attacking a conclusion **already
committed**, so it could not be revised to dodge them.

---

# The corpus fork — RESOLVED (2026-09-12)

**The intra-rater test ran 2026-09-12** (`docs/reports/INTRA-RATER-2026-09-12.md`).

| result | figure |
|---|---|
| **Anchoring** | **REFUTED 4/4** — every row where Sai overruled the machine, he overruled again, blind and shuffled. The labels are **not** a mirror of the gate's output. |
| Self-agreement, evidence-derivable items | **κ = +0.857** (13/14) |
| Self-agreement, including policy items | κ = +0.636 (13/16) |
| The 2 `haiku_summary` rows | **0/2** — and 0/2 for *both* external readers too |

**The finding.** The corpus mixes two kinds of item. An **evidence-derivable**
row's label follows from what the labeller is shown. A **policy** row's label
follows from a gate rule that is *not in the item* — an AI summary cannot ground
anything, whoever wrote it. Three raters have judged those two rows and all
three disagreed with gold **in the same direction**, including the author of the
labels judging blind.

**RETRACTED:** the 2026-09-03 report blamed the review page's wording. The
rebuilt page stated the provenance outright and the answer did not move. The
wording was not the cause; the item is unlabelable from its own contents.

`label_basis` now marks the split (D-34). **κ excludes policy rows; Error-A and
Error-B include them, always** — a source-inspection test enforces that, because
dropping them from the rates would score the gate only on the questions it finds
easy.

**Alpha #5 is reachable again.** Next step: **ONE domain-competent reader, on
evidence-derivable items only.** Not another lay reader, and not on all 52.

**T3 is still not the next move.** It buys Error-A down; it is not needed to
state Error-A honestly, and 12 Error-B classes are open.

---

## The gate, in one paragraph

A claim is GROUNDED only if **T1** fires: a contiguous verbatim span of ≥8 tokens
from the claim appears in a cited source, **or** the whole claim is a contiguous
span of a cited source (exact containment, any length, refused when the span sits
under an attribution or denial, **or the span is a `that`-complement of a
NON-FACTIVE verb** — `argued` refuses, `shown` grounds, and an *unlisted*
verb refuses because the rule is a WHITELIST, J-19). Contracted negations are
expanded before tokenizing, so `isn't` can no longer hide a denial (J-20).
**T2 was demoted 2026-09-02 and decides nothing**
(ADR-006); `lex_tau` is retired and `--lex-tau` raises. Absence claims need two
searches that address the claim's own **scope**. PASS means an EMPTY retained
appendix, not a score (ADR-005).

**Current rates: Error-A 0.320 / Error-B 0.000, n=52 gold (CR-004).**
Never quote the zero bare — on 0 misses of 27, the 95% upper bound is **~10.5%**,
and rounds 3–5 found 65 wrongful PASSes in classes the corpus does not contain.
Say *"no remaining Error-B among the 52 ratified rows"*, and attach
*(n=52, single ratifier, CR-004)*. **Attach the reliability result, which improved
2026-09-12:** intra-rater **κ = +0.857** on evidence-derivable items and
**anchoring refuted 4/4**, so the labels are reproducible by their author and
are not circular. Two *external* readers still reproduced them at only κ 0.54
and 0.16 (κ 0.09 with each other) on a corpus that was label-sorted and mixed
policy rows in — **Alpha #5 is reachable but NOT yet met.**

**AND attach this:** round 7 found **22 wrongful PASSes over 11 mechanisms** in
a gate that had already survived six rounds. **12 classes remain open.** The
rates describe the 52-row corpus; they do not describe the gate.

---

# DEMO READINESS — defined

Two different things get called "a demo". They have different bars.

## D-1 · Scripted offline demo — **READY**

*You drive, on frozen fixtures, showing the moat.*

| # | Criterion | State |
|---|---|---|
| 1 | Runs from a clean checkout with documented commands | ✅ `demo/DEMO-SCRIPT.md` |
| 2 | Honest draft → PASS; draft citing a fabricated `[S3]` → FAIL | ✅ tested (`-k demo`, 5 tests) |
| 3 | Deterministic — same verdict every run, every machine | ✅ frozen store, no RNG |
| 4 | Zero network and zero model calls in the verdict path | ✅ enforced by moat tests |
| 5 | A non-engineer can follow the script | ✅ |

**Verify before showing:** `cd Agent-Assure && uv run pytest -q -k demo` → 5 passed.

**What it proves:** a fabrication cannot argue its way to a pass, because nothing
in the verdict path can be persuaded. That is the differentiated half of the
product and it is true today.

## D-2 · Live demo on a visitor's own document — **NOT READY**

| # | Criterion | State |
|---|---|---|
| 1 | False alarms rare enough that a real page is not a third flagged | ❌ **Error-A 0.320** |
| 2 | Rhetorical questions and prose furniture not scored as claims | ❌ **7.9%** of real-prose claims are question-form (1,337 claims, 10 chapters, measured 2026-09-12) — and **zero carry a citation**, so they read UNCITED, not UNGROUNDED. `docs/reports/J15-BRIEF-2026-09-12.md` |
| 3 | An interface a visitor can look at | ❌ CLI + a YAML file. Slice 2a unbuilt |
| 4 | Capture hook works live in the visitor's own session | ⚠️ built and live-validated; never exercised by a stranger |

**Do not attempt D-2.** One flagged sentence in three reads as "broken", not
"strict", and there is nothing to look at. **Blockers in order: J-15 → Error-A →
2a front-end.**

---

# ALPHA READINESS — defined

Alpha = *the gate can be handed to a friendly external user with its error rates
stated honestly.* Eight criteria; **three met** (criterion 1 was downgraded by
round 7 — the corpus is still clean, the gate is not).

| # | Criterion | State | Owner |
|---|---|---|---|
| 1 | Zero known Error-B on the ratified corpus, each closed class carrying a tripwire | ⚠️ **still true of the CORPUS, and now false of the GATE by a wider margin: rounds 7+8 leave ~31 open Error-B classes the corpus does not contain.** All tripwired (56 xfails, of which 3 are the ADR-006 Error-A price, not holes). Never quote criterion 1 without this line. | Claude |
| 2 | Thresholds are data, with a current CR, and no fitted parameter is undocumented | ✅ CR-004; grounding path has **zero** fitted parameters | — |
| 3 | Installs and runs standalone from a clean clone, zero cross-plugin imports | ✅ `install.sh`, `uv sync` | — |
| 4 | Every open moat item is either CLOSED or accepted **in writing** by its owner | ⚠️ 9 strict xfails are recorded and accepted; **J-15 and J-05 are neither** | Sai |
| 5 | Error rates from **≥2 independent labellers**, not the project owner alone | ❌ not met, but **now REACHABLE** — intra-rater κ=+0.857 on evidence-derivable items, anchoring refuted 4/4, and `label_basis` separates the policy rows no reader can derive. Next: **ONE domain-competent reader, derivable items only.** | Sai + Claude |
| 6 | Error-A either tolerable for the intended user, or measured on **real** drafts | ❌ unmeasured; two attempts failed (`docs/reports/BASE-RATE-*`) | — |
| 7 | One adversarial round whose every finding is closed or accepted, run **after** the last moat change | ❌ **round 8 ran and closed ZERO classes** — 21 findings, 12 Error-B, 20 tripwired (J-23). Recorded is not accepted. **Round 9 is owed after J-21 lands**, and J-21 is itself a moat change that needs attacking. `docs/plans/reports/RED-TEAM-R8-2026-09-12.md` | Claude + Sai |
| 8 | AAR-004 written and `v0.9.0-alpha` tagged | ❌ | Claude |

**Shortest honest path to Alpha:** #5 (free) → #4 (two rulings) → **J-21 then
round 9** (~1.5M, was estimated 0.4M before round 8 tripled the open set) →
#6 or an explicit written acceptance of 0.320 → #8 (~0.4M).

**The estimate moved for a reason worth keeping:** every round so far has found
more than the previous one, in a gate that keeps getting better. That is not a
contradiction — the adversaries keep getting sharper prompts. Budget round 9
as a real round, not a formality.
**T3 is not on this list.** It buys Error-A down; it is not required to *state*
Error-A honestly.

---

## Blocked on Sai — nothing else is

| | Item | Cost |
|---|---|---|
| 0 | **q25 — a GOLD ADJUDICATION, and never Claude's to set.** `"Increased marketing spend drives higher customer signups [S251][S252]"` — gold says violation (a causal claim from two correlational sources); you said grounded, blind. The one genuinely ambiguous item the intra-rater round found. | 5 min |
| 0a | **J-22 — add `concluded` / `indicates` to `_FACTIVE_VERBS`?** D-36 newly REFUSES honest sources that endorse with a verb not on the whitelist: `Our benchmark concluded that …` grounded before and FAILs now. Adding them is **PASS-ENABLING** = Escalation #1. **`reported` must NOT be added** — "The blog reported that X" is attribution, and adding it opens Error-B. The class is **absent from the n=52 corpus, so A=0.320 does not bound it** — unmeasured, not small. | ~free once ruled |
| 0b | **OI-MOAT-31 — invert `_header_asserts`' default?** It asks *"is this an assertion?"* and defaults to NO, so a header escapes scoring when the test is inconclusive — a default pointing toward PASS. `### Redis lost all data` is caught only because "Redis" ends in "s". **Every narrow fix is the blacklist/length shape that has failed five times**; the sound fix inverts the default and moves the Error-A/Error-B trade-off. Escalation #1. | ~0.3M |
| 0c | **J-15** — score rhetorical questions? *(recommend: no exemption — 7.9% of real-prose claims are questions and **zero** carry a citation, so they read UNCITED, which already blocks PASS)* | ~0.3M |
| 0d | **D-07** — `install.sh` ships pytest to end users. *(recommend: `uv sync --no-dev`)* | free |
| 0e | **`docs/consulting/`** — *(recommend: confirm private **AND** de-identify the client name, so the visibility toggle stops being the only control)* | free |
| 1 | **Re-run the inter-rater test.** The first attempt FAILED (κ 0.09 between readers). Two page defects were mine and are fixable: item order leaked the answer (corpus is sorted by label), and the AI-summary question asked about content when the rule is about provenance. **Decide the population**: one lay reader + one domain-competent reader is the test that distinguishes "wrong readers" from "ambiguous corpus". | ~0.2M + 2×40 min |
| 2 | **J-15 / OI-DEC-02** — score rhetorical questions or not? Exempting them removes them from the denominator, and `Isn't Redis capable of 128000 ops/sec [S1]?` is scored today. | ~0.3M |
| 3 | **D-07** — `install.sh` now provisions pytest for END USERS. Keep, or `uv sync --no-dev`? | free |
| 4 | **D-01** — park-list reading (named items live in iVal 2.0; general clause applied). | free |
| 5 | **Ratify D-15…D-20** — six autonomous fail-closed calls, each with its undo. | free |
| 6 | **`docs/consulting/` stays private** — it names a client and records that they have no signed paper. | free |

---

## Already done — do NOT redo

α2 · CR-002 → **CR-003** (T2 demoted, `lex_tau` retired) → **CR-004** (absence
scope). OI-MOAT-21, OI-T2-01, OI-DEC-01, OI-ABS-01, OI-QM-01, OI-DEC-03…06 all
CLOSED. Red-team rounds 3–6. The Error-A harness, the T2-discrimination batch,
the quote-mining guard.

**Two things that look undone but are deliberate:**
- **The paraphrase base rate is unmeasured and two runs failed.** v1's filter
  discarded the population it was counting; v2 fixed that but only ~4 sentences
  are genuinely eligible. **Do not quote 10.1%, 1.2% or 14.3%.** A third attempt
  on this corpus will fail the same way — it needs sampled real drafts.
- **9 strict xfails are the recorded Error-A price**, not regressions. They
  XPASS when T3 lands.

## The standing trap

Ask of any new metric: **what could it not have detected?** Three instruments
were blind this session, each to exactly the case that would have decided the
question, and each produced a plausible number. The tell was always a
suspiciously clean result.
