# RESUME HERE — Agent-Assure

**Last session:** `d2b27b1f`, closed 2026-09-03.
**Branch:** `agent-assure-calibration-run` · clean, pushed.
**Suite:** `cd Agent-Assure && uv run pytest -q` → **489 passed, 2 skipped, 9 xfailed.**
Trust the RUN, not this number.

Read in this order: this file → `docs/logbook/2026-09-02-to-03-t2-demotion-and-real-prose.md`
→ `docs/jobs/REGISTER.md`. Memory files are supplementary and go stale fastest.

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
| 2 | Rhetorical questions and prose furniture not scored as claims | ❌ 9.4% of real-prose claims are questions (J-15) |
| 3 | An interface a visitor can look at | ❌ CLI + a YAML file. Slice 2a unbuilt |
| 4 | Capture hook works live in the visitor's own session | ⚠️ built and live-validated; never exercised by a stranger |

**Do not attempt D-2.** One flagged sentence in three reads as "broken", not
"strict", and there is nothing to look at. **Blockers in order: J-15 → Error-A →
2a front-end.**

---

# ALPHA READINESS — defined

Alpha = *the gate can be handed to a friendly external user with its error rates
stated honestly.* Eight criteria; **four met.**

| # | Criterion | State | Owner |
|---|---|---|---|
| 1 | Zero known Error-B on the ratified corpus, each closed class carrying a tripwire | ✅ CR-004; `tests/red_team_moat/` | — |
| 2 | Thresholds are data, with a current CR, and no fitted parameter is undocumented | ✅ CR-004; grounding path has **zero** fitted parameters | — |
| 3 | Installs and runs standalone from a clean clone, zero cross-plugin imports | ✅ `install.sh`, `uv sync` | — |
| 4 | Every open moat item is either CLOSED or accepted **in writing** by its owner | ⚠️ 9 strict xfails are recorded and accepted; **J-15 and J-05 are neither** | Sai |
| 5 | Error rates from **≥2 independent labellers**, not the project owner alone | ❌ **FAILED 2026-09-03**, not merely unattempted — two readers reproduced the labels at κ 0.54 / 0.16 and agreed with each other at κ **0.09**. `docs/reports/INTER-RATER-2026-09-03.md` | Sai + Claude |
| 6 | Error-A either tolerable for the intended user, or measured on **real** drafts | ❌ unmeasured; two attempts failed (`docs/reports/BASE-RATE-*`) | — |
| 7 | One adversarial round whose every finding is closed or accepted, run **after** the last moat change | ❌ round 7 not run — D-15…D-20 landed after round 6 | Claude |
| 8 | AAR-004 written and `v0.9.0-alpha` tagged | ❌ | Claude |

**Shortest honest path to Alpha:** #5 (free) → #4 (two rulings) → #7 (~0.4M) →
#6 or an explicit written acceptance of 0.320 → #8 (~0.4M).
**T3 is not on this list.** It buys Error-A down; it is not required to *state*
Error-A honestly.

---

## Blocked on Sai — nothing else is

| | Item | Cost |
|---|---|---|
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
