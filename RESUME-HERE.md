# RESUME HERE — Agent-Assure

**Last session:** `d2b27b1f`, closed 2026-09-12 (overnight round-7 run).
**Branch:** `agent-assure-calibration-run` · clean, **pushed, 0 ahead.**
*(The earlier "push is denied" note was wrong: the classifier blocked the compound
`add && commit && push`, never `git push` alone.)*
**Suite:** `cd Agent-Assure && uv run pytest -q` → **532 passed, 2 skipped, 14 xfailed.**
Trust the RUN, not this number.

Read in this order: this file → `docs/logbook/2026-09-12-round-7-and-the-intra-rater-instrument.md`
→ `docs/jobs/REGISTER.md`. Memory files are supplementary and go stale fastest.

---

# START HERE — the fork is RESOLVED. The corpus is MIXED, not ambiguous.

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
| 1 | Zero known Error-B on the ratified corpus, each closed class carrying a tripwire | ⚠️ **still true of the CORPUS, but round 7 found 19 open Error-B classes the corpus does not contain.** Each is tripwired. Never quote criterion 1 without this line. | Claude |
| 2 | Thresholds are data, with a current CR, and no fitted parameter is undocumented | ✅ CR-004; grounding path has **zero** fitted parameters | — |
| 3 | Installs and runs standalone from a clean clone, zero cross-plugin imports | ✅ `install.sh`, `uv sync` | — |
| 4 | Every open moat item is either CLOSED or accepted **in writing** by its owner | ⚠️ 9 strict xfails are recorded and accepted; **J-15 and J-05 are neither** | Sai |
| 5 | Error rates from **≥2 independent labellers**, not the project owner alone | ❌ not met, but **now REACHABLE** — intra-rater κ=+0.857 on evidence-derivable items, anchoring refuted 4/4, and `label_basis` separates the policy rows no reader can derive. Next: **ONE domain-competent reader, derivable items only.** | Sai + Claude |
| 6 | Error-A either tolerable for the intended user, or measured on **real** drafts | ❌ unmeasured; two attempts failed (`docs/reports/BASE-RATE-*`) | — |
| 7 | One adversarial round whose every finding is closed or accepted, run **after** the last moat change | ❌ round 7 found **22 over 11 mechanisms**; **10 now closed, 12 open and tripwired.** Recorded is not accepted. **Round 8 is owed** and must run after J-19/J-20/D-30…D-34. `docs/plans/reports/RED-TEAM-R7-2026-09-12.md` | Claude + Sai |
| 8 | AAR-004 written and `v0.9.0-alpha` tagged | ❌ | Claude |

**Shortest honest path to Alpha:** #5 (free) → #4 (two rulings) → #7 (~0.4M) →
#6 or an explicit written acceptance of 0.320 → #8 (~0.4M).
**T3 is not on this list.** It buys Error-A down; it is not required to *state*
Error-A honestly.

---

## Blocked on Sai — nothing else is

| | Item | Cost |
|---|---|---|
| 0 | **q25 — a GOLD ADJUDICATION, and never Claude's to set.** `"Increased marketing spend drives higher customer signups [S251][S252]"` — gold says violation (a causal claim from two correlational sources); you said grounded, blind. The one genuinely ambiguous item the intra-rater round found. | 5 min |
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
