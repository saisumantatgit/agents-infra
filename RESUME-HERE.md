# RESUME HERE — Agent-Assure

**Last session:** `d2b27b1f`, closed 2026-09-12 (overnight round-7 run).
**Branch:** `agent-assure-calibration-run` · clean, **NOT pushed — push is DENIED**
by the permission classifier. 13 commits are local. Sai must push or grant it.
**Suite:** `cd Agent-Assure && uv run pytest -q` → **510 passed, 2 skipped, 22 xfailed.**
Trust the RUN, not this number.

Read in this order: this file → `docs/logbook/2026-09-12-round-7-and-the-intra-rater-instrument.md`
→ `docs/jobs/REGISTER.md`. Memory files are supplementary and go stale fastest.

---

# START HERE — the one test that unblocks the rest

**The inter-rater check FAILED on 2026-09-03** (κ = 0.09 between two independent
readers — chance). We cannot currently tell whether the readers were wrong or the
**corpus is ambiguous**, and that fork decides everything downstream.

**The cheapest decisive test is intra-rater, and it needs only Sai: re-label 20 of
his own rows, blind and shuffled, ~20 minutes.**

**IT IS BUILT AND WAITING:**
https://claude.ai/code/artifact/170c9801-14fa-4231-9468-1fa2371f5319
Paste the block it gives you; `Agent-Assure/calibration/intra-rater/score.py`
returns the branch. Four branches, all dry-run verified.

**The fork has THREE outcomes, not two.** `init_labels.py` seeds every row with
Claude's `candidate_verdict` and the ratifier corrects it, so on 48 of 52 rows
gold == candidate — and on those rows "Sai agrees with himself" and "Sai agrees
with the machine" are the SAME observation. Only 4 rows (q14, q16, q37, q49)
separate them, so the sample is stratified to contain all four. A plain random
draw of 20 missed every one of them (p=0.133) and would have measured nothing.

| outcome | meaning | next |
|---|---|---|
| Sai agrees with himself, κ > 0.8 | corpus is sound; the problem was reader population | recruit ONE domain-competent reader; Alpha criterion #5 is reachable |
| Sai does not | the corpus holds genuinely ambiguous items — **no reader population fixes that** | rebuild the corpus with defensible items, or change what the product claims |
| **He re-labels the 4 probe rows onto the MACHINE's original call** | **the labels are anchored on the gate's own output** — the gate was calibrated against a mirror | worse than ambiguity: the corpus is not ground truth at all, and every rate built on it is partly circular |

Neither outcome wastes the twenty minutes, which is more than the last two
measurement runs managed. **Do not build T3 before this resolves** — its whole
justification is buying down an Error-A figure we can no longer defend.

**Both of those are DONE (2026-09-12).** The page defects are fixed in the new
instrument (deterministic shuffle; provenance stated on every row). Round 7 ran:
**22 wrongful PASSes over 11 mechanisms, 3 closed, 19 open and tripwired.**
**Round 8 is now what is owed.**

---

## The gate, in one paragraph

A claim is GROUNDED only if **T1** fires: a contiguous verbatim span of ≥8 tokens
from the claim appears in a cited source, **or** the whole claim is a contiguous
span of a cited source (exact containment, any length, refused when the span sits
under an attribution or denial). **T2 was demoted 2026-09-02 and decides nothing**
(ADR-006); `lex_tau` is retired and `--lex-tau` raises. Absence claims need two
searches that address the claim's own **scope**. PASS means an EMPTY retained
appendix, not a score (ADR-005).

**Current rates: Error-A 0.320 / Error-B 0.000, n=52 gold (CR-004).**
Never quote the zero bare — on 0 misses of 27, the 95% upper bound is **~10.5%**,
and rounds 3–5 found 65 wrongful PASSes in classes the corpus does not contain.
Say *"no remaining Error-B among the 52 ratified rows"*, and attach
*(n=52, single ratifier, CR-004)*. **Since 2026-09-03 also attach the inter-rater
result:** two independent readers reproduced those labels at κ 0.54 and 0.16 and
agreed with each other at κ **0.09**. The labels are NOT established as
reproducible. The gate's DESIGN findings are unaffected (established by
construction, not by labels); every quoted RATE is.

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
| 5 | Error rates from **≥2 independent labellers**, not the project owner alone | ❌ **FAILED 2026-09-03**, not merely unattempted — two readers reproduced the labels at κ 0.54 / 0.16 and agreed with each other at κ **0.09**. `docs/reports/INTER-RATER-2026-09-03.md` | Sai + Claude |
| 6 | Error-A either tolerable for the intended user, or measured on **real** drafts | ❌ unmeasured; two attempts failed (`docs/reports/BASE-RATE-*`) | — |
| 7 | One adversarial round whose every finding is closed or accepted, run **after** the last moat change | ❌ **round 7 RAN 2026-09-12: 22 wrongful PASSes, 11 mechanisms. 3 closed, 19 open and tripwired.** Recorded is not accepted — 2 of the acceptances are Sai's rulings. **Round 8 is owed.** `docs/plans/reports/RED-TEAM-R7-2026-09-12.md` | Claude + Sai |
| 8 | AAR-004 written and `v0.9.0-alpha` tagged | ❌ | Claude |

**Shortest honest path to Alpha:** #5 (free) → #4 (two rulings) → #7 (~0.4M) →
#6 or an explicit written acceptance of 0.320 → #8 (~0.4M).
**T3 is not on this list.** It buys Error-A down; it is not required to *state*
Error-A honestly.

---

## Blocked on Sai — nothing else is

| | Item | Cost |
|---|---|---|
| 0 | **Ratify or reverse D-24** — I shipped a moat change on a fail-closed claim that the solo gate proved FALSE. The change stays (reverting reinstates a worse hole) but its basis is retracted and the authority call is yours. `git revert aad2ee1` is the undo. | free |
| 0b | **OI-MOAT-27 — the quote-mining class.** Recommendation CORRECTED: a **factive-verb whitelist + negation conjunct**, not the large-Error-A refusal I first proposed. Unlisted verbs refuse, so the attacker is off the enumerating side of the rule. Needs calibration on the n=52 gold set, and must compose with OI-MOAT-25's tokenizer repair. | ~0.5M |
| 0c | **PUSH IS DENIED** — 13 commits local. Not routed to another session; that would launder the denial. | free |
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
