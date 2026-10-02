# RESUME HERE — Agent-Assure

**Last session:** overnight 2026-10-01→02, ratified at a §0 handshake (D-51).
**Branch:** `plugin-validation-2026-10-02`, child of `agent-assure-calibration-run`.
**Pushed. NOT merged — the merge is your GO.** Undo the night with
`git branch -D plugin-validation-2026-10-02`; `main` untouched. The previous night's work is already MERGED (PR #5).
**Suite:** `cd Agent-Assure && uv run pytest -q` → 750 passed, 2 skipped,
63 xfailed. Trust the RUN, not this number.

Read: this file → `docs/logbook/overnight-2026-10-01B-progress.md` (the morning
report, §0 answers "is it ready to ship?") → `docs/decisions/RATIFICATION-REGISTER-2026-08-30.md`
(D-51…D-60) → `docs/jobs/REGISTER.md`.

---

# IS IT READY TO SHIP? Ready as both CLI and plugin — one 2-minute check left.

**J-52 is closed as far as it can be closed without you.** Report:
`Agent-Assure/docs/reports/J52-PLUGIN-PATH-2026-10-02.md`.

Validated and pinned (`tests/test_plugin_contract.py`): the manifest is
discoverable; the hook matcher covers **every** shipped retrieval tool in both
directions; the exact `hooks.json` command line fires with `CLAUDE_PLUGIN_ROOT`
resolved and writes a store carrying the session id; command and skill
frontmatter are discoverable. Plus α4's full stranger journey (install → demo
PASS/FAIL → hook captures → session enforcement → fabrication FAILs).

## J-54 — the one human step. Two minutes.

```
claude --plugin-dir /path/to/Agent-Assure
#   /hooks            -> expect PostToolUse listing capture_hook.py
#   read any file     -> expect .assure/evidence-store.jsonl to appear
#   /assure-verify <draft>
```

**Proven unreachable non-interactively**, not merely unfinished: `claude -p`
executes no PostToolUse hooks under ANY of three registrations (plugin
`--plugin-dir`, project `.claude/settings.json`, explicit `--settings`) — none
fired while the tool call itself ran every time. Everything J-54 would confirm is
already proven in parts.

## J-55 — the limitation that search found, and it is a roadmap question

**In `claude -p` / CI / piped mode the capture hook never runs**, so the store
stays empty and every claim reads `UNCITED` — the gate fails everything for a
reason unrelated to the draft. Nobody had written this down. It is now on the
README and the skill and pinned as a disclosed limitation. **If CI is a target,
capture needs a non-hook mechanism** (a wrapper, or SDK-level capture). That is a
design decision, not a bug fix, and it is yours.

## The thing not to launch quietly, unchanged: Error-A is 0.320

A third of honest claims read UNGROUNDED, because the gate certifies verbatim
provenance and nothing else. The surfaces disclose it. T3/NLI was the fix and the
HHEM diagnostic measured it as adding **zero**. Put it on the README's first
screen and ship as an alpha.

# What changed

| | |
|---|---|
| **CLAIM-1** | All four shipped surfaces promised "actually retrieved this session" — there was no session boundary. Rewritten to what is enforced, each with a limitations block. `tests/test_product_claim.py` pins promises AND limitations, so closing a limitation fails the suite and forces the claim text to change. **"No LLM calls during grounding" had ZERO tests before this**; it is now an AST import walk. |
| **J-38** | `session_id` on every captured record; `--session-id` REFUSES a foreign-session store. It raises rather than filters, because a filtered store is fail-OPEN on the absence path (D-54). |
| **J-41r** | Comment stripping is SAME-LINE only — the 4th design; three earlier ones lost rounds 9, 10 and 11. |
| **J-22** | `conclude*`/`indicate*` added, `report*` out, `found`≡`concluded` parity pinned. |
| **CR-005** | A=0.320 / B=0.000 re-derived. Its load-bearing section: **a zero delta is NON-MEASUREMENT, not safety** — no corpus row carries the shapes any of these changes touch. |
| **α4** | Run for the first time ever. Found the defect eleven red-team rounds could not. |

# Withdrawn last night — read #3 before trusting my judgment on a trade-off

1. "Delete comment stripping" — deletion failed every draft containing a comment.
2. "Annotate CR-004 instead of CR-005" — failure-mode 9 makes the CR mandatory.
3. **D-52: I extended the comment rule BEYOND your ruling to protect a UX finding.
   An adversary found 3 ERROR-B in my extension within the hour. Reverted.** I
   traded an unrecoverable error for a recoverable one — the one trade the moat
   invariant forbids. §1 licenses deciding; it does not license overriding a
   ratified SAFETY decision to buy UX.
4. "Renderer-faithful by construction" — it assumed `-->` is the only comment close.
5. "Stamp `fetched_at` for real" — the sentinel is deliberate; scoping needs an
   identity, not a clock.

# Yours

**J-52** (plugin path, the launch gate) · **J-43** + **J-44** (both move the
Error-A/Error-B trade-off on unmeasured prose) · **J-48** (multi-line notes
scored; cheapest mitigation is documentation) · **J-51** (`install.sh` text) ·
**J-37** (whether CR-004 must be re-derived) · **J-49** (expose a session id to
the skill) · **q25** · **J-24** (the product call, still unmade — but round 10
reframed it: see the previous section below).

---

# THE ONE RECOMMENDATION I WOULD PUT FIRST — J-41

**Stop stripping HTML comments from drafts. Delete the feature.**

The comment-stripper has now lost rounds **7, 8, 9, 10 AND 11**, across **three
implementations** — backtick-only, a code-region scanner, and a block-structure
rule. It produced **12 ERROR-B tonight alone.** Each version closed the fixtures
written against it and left the class open.

The cause is structural, not a run of bad luck: the gate is trying to
reimplement a Markdown renderer's block model well enough to decide what a
reader sees, **against an adversary who writes the document.** Every round finds
another construct the model lacks. It is the blacklist shape this project's own
law forbids, three times over.

Deleting the feature ends the sequence permanently and turns seven functions
into dead code. The trade is an **unrecoverable** Error-B for a **recoverable**
Error-A: a draft containing an authoring note would fail, and "remove your TODOs
before submitting this for verification" is a defensible thing for a
verification gate to require.

**It is yours because it moves the Error-A/Error-B trade-off and the contract
with the author (Escalation #1), and because its Error-A cost is unmeasured —
no row of the n=52 corpus contains an HTML comment.** The only other option that
ends the sequence is adopting a real CommonMark parser as the oracle, which I
rejected at 03:00 for putting third-party code in the verdict path. You may
weigh that differently in daylight.

---

# ROUND 10 CHANGED THE QUESTION — read this before J-24

Three Opus adversaries ran against tonight's repaired tree. **13 ERROR-B.**
Reports: `Agent-Assure/docs/plans/reports/RED-TEAM-R10-{A,B,C}-*.md`.

**The finding is not any single bug. It is WHERE the bugs are.** Ten rounds have
hardened the gate's deterministic logic. Six of tonight's thirteen live in the
**CAPTURE layer**, and not one of them is reachable by editing
`ground_check.py`:

- **`Read` is trusted unconditionally** (J-35). An agent writes a fabrication to
  a file, reads it back, cites it → **PASS 100.0 / GROUNDED**, with the numeric
  tier "verifying" figures the same model invented. The identical text via
  `WebFetch` is correctly refused. The laundering happens BEFORE the store, so
  no amount of loader validation can see it.
- **The absence ledger is attacker-written** (J-36). No SEARCH tool is captured
  at all, so the "two distinct search queries" that certify an absence are two
  strings the drafting agent picked — file names it chose, or one page fetched
  twice with different URL fragments.
- **There is no "this session"** (J-38). No `session_id` on any record,
  `fetched_at` is a constant sentinel, the store is append-forever. A later
  session's draft citing a prior session's `[S2]` → **PASS 100.0.** This one
  strikes the founding spec's own sentence: "actually retrieved THIS session."

**So we have been optimising the wrong constraint.** The moat's logic is in
decent shape. The evidence entering it is not.

**This reframes J-24.** "Ship provenance-only" is not currently on the menu
either, because provenance is not enforced where evidence is captured. The
honest options now look like: (a) fix the capture layer — all Escalation #4,
all yours; (b) narrow the product's claim to what is actually enforced; or
(c) both. **I did not presume any of them.**

**And one measurement you relied on is weaker than advertised** (J-37):
`build_corpus_v2.py` builds its store objects directly and **never calls
`load_store`**, using a tool the loader now refuses. So the mandatory
"regenerate the corpus" adversary is blind to every loader change, and
**CR-004's A=0.320 / B=0.000 is measured on stores the shipped gate would
reject.** I wrongly counted that check as a passed gate for J-26 last night;
the correction is D-45.

---

# What changed: provenance is MORE true, and still not true

Three fail-closed fixes landed. Each was proven red, corpus-diffed, and
adversarially reviewed.

| | what it closes | evidence |
|---|---|---|
| **J-25** | A fabricated citation that PARSES certified PASS on RELATIONAL and ABSENCE claims, because the unresolved-citation check sat BELOW the kind dispatch. | 2 strict xfails → 9 passing regressions |
| **J-26** | `load_store` silently repaired self-contradicting stores: duplicate ids, NFKC id collisions, duplicate JSON keys, mistyped fields, tool/source-type disagreement. Line order decided verdicts. | 19 of 27 proven red |
| **J-27** | Comment delimiters inside tilde fences, indented code and backslash escapes deleted visible prose from the scored denominator. | 7 of 13 red, plus 6 pre-existing xfails converted |

## The one thing to read before touching this again

**I claimed J-25 closed the class. It did not, and the solo gate refuted me
within the hour** (D-42). J-25 closed UNRESOLVED citations — markers the gate
parses and fails to find. It did nothing about **UNRECOGNISED** ones:
`_CITATION_RE` is case-sensitive, so `[s99]` is not an unresolved citation but
**no citation at all**, and RELATIONAL/ABSENCE certify with zero citations by
design. `[S99]` FAILs. `[s99]` PASSes. One Shift keystroke — round 4's lesson
for the third time in this project.

## THE DECISION WAITING ON YOU — J-31 + J-33, as ONE package (D-44)

Not made. Do not presume it.

The spelling-based fix for J-33 is the losing shape: the attacker sets the
spelling. The structural fix — **require citations on ABSENCE and RELATIONAL
claims** — closes it regardless of spelling, but it cannot land alone, because
**J-31** means a correctly-cited absence claim is ALREADY refused while the
identical uncited one is certified. Requiring citations while cited ones fail
would refuse every absence claim.

So the package is: fix J-31 → then require citations → then measure both error
rates. **Step 1 is PASS-ENABLING, so the package is Escalation #1 and yours.**

**And you cannot measure it with what we have.** `labeling-v2.csv` came back
byte-identical after all three fixes, because none of the 52 rows carries an
uninterpretable bracket, an HTML comment, or a malformed store. **A=0.320
bounds none of tonight's work.** A corpus extension is a prerequisite, and
authoring rows sits next to the gold-label gate, which is also yours.

## Still yours, unchanged

**J-24 — ship PROVENANCE-only, or fund ENTAILMENT?** Still not made. Tonight
did not presume it: everything built is required under BOTH branches, because
entailment layers on provenance rather than replacing it. The measured case
against buying entailment now is unchanged — HHEM-2.1-Open catches 3 of 17 open
attacks, all 3 already caught by the gate, union gain **zero**, and it is right
only where it would have to LIFT a flag, which the moat forbids.

Also yours: **J-22** (factive whitelist, PASS-enabling), **J-28** (spec §7.5
hook registration, Escalation #4), **q25** gold adjudication, **OI-MOAT-31**,
**J-15**, **D-07**, `docs/consulting/` privacy.

## Round 11 (2 adversaries): J-28B refuted, and TWO OF MY OWN FIXES withdrawn

- **R10C-03's query restriction was an ERROR-B I introduced** and claimed
  fail-closed. `queries` is both a numerator and a **denominator** — it sizes
  the blanket-corpus-word refusal — so shrinking it switched that refusal off.
  Reverted; the narrower hole is reopened deliberately as J-42.
- **J-40 grounded a figure against the whole store** rather than the claim's
  citations. Fixed.
- Open and tripwired: **J-43** ("ninety-seven percent" is never extracted —
  `_NUMERIC_RE` needs a digit), **J-44** ("migraine" ≠ "migraines", Error-A),
  **J-45** (`evidence_basis` announces queries the verdict ignored).

## Withdrawn — do not repeat these

- "The founding spec does not exist." It is in the HQ repo.
- "Provenance cannot lose a red-team round." It lost round 9.
- **"No fabricated citation can certify PASS on any claim kind" (b8d4584).**
  Refuted the same night. D-42.
- **"J-27 closes the comment-delimiter class."** Refuted by round 10. D-45.
- **"R10C-03's query restriction is fail-closed."** FALSE — it was an Error-B I
  introduced and withdrew the same night. D-50.
- **"J-39 is strictly fail-closed."** Right about Error-B, wrong as stated. J-44.

**Eight withdrawals, six of them the same shape: a confident general claim drawn
from a check narrower than the claim.** The sharpest came AFTER I had written the
warning — I named the direction trap in `check_absence`, tested it, commented
it, then introduced that exact failure one argument to the left.

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
