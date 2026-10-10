# Logbook — 2026-07-14 — Autonomous night: red-team round 2, OI-CITE-01, α4, ADR-004 package

**Branch:** `agent-assure-calibration-run` · **Suite:** 376 passed + 3 xfailed (was 351 + 2) · **Mode:** autonomous (Sai asleep), 4 agents + main-loop implementation

## What

Sai said "plan and execute long autonomous required work" with the standing
gates intact (no self-ratifying labels, no touching the two deferred moat
holes, no new Error-A/B decisions). Five workstreams ran; everything an agent
claimed was hand-verified before it entered the repo.

## Done

1. **Red-team round 2 (the headline).** A sweep against the *fixed* gate found
   **14 wrongful PASSes across 4 mechanisms** — all reproduced by hand. The
   2026-07-12 fixes were real but NARROW:
   - Rate-qualifier reading covered only `per <word>` / `/<word>` within two
     words. Evaded by: `each/every/a/one <unit>`, hyphenated `per-minute`,
     adverbial `hourly`, qualifier before the number or further from it, and
     **a Cyrillic homoglyph (`рer`, U+0440)** — NFKC does not fold it, so the
     rate became *invisible*, collapsing the claim to a bare number that
     matched the source.
   - Quantity nouns were never compared (`128000 gigabytes/sec` grounded by
     `128000 operations/sec`).
   - Absence anchoring leaked for entity-free subjects in <3-query sessions.
   **FIXED** (all three complete Sai's existing 07-12 rulings — see Scope
   below): unified `_numeric_context` extractor (quantity + rate, confusables-
   folded, reads before/after the number), subject-specificity absence rule.
   11 guards proven red → green (`tests/red_team_moat/test_moat_red_team_r2.py`).
2. **AA-MOAT-007 RECORDED, NOT FIXED.** A verbless colon-form fabrication
   ("Redis: unquestionably the fastest datastore in all of human history.")
   classifies NON_CLAIM, escapes the denominator, and rides inside a PASS.
   Fixing it changes *what counts as a claim* → Escalation #1 → Sai's call.
   Strict-xfail tripwire in place.
3. **OI-CITE-01 CLOSED.** `_CITATION_RE` widened to `S\d+[a-zA-Z]*`; red-first
   (4 tests failing pre-fix). `[S1a]` now reads UNVERIFIED_CITATION instead of
   silently detaching. The "numeric-only source IDs" fixture restriction is lifted.
4. **α4 second-repo install validation: READY (with caveats).** Fresh install
   3s, capture path built a real 5-source store from an unrelated repo, genuine
   draft → PASS, fabricated numeric → NEEDS_WORK naming the bad claim. New:
   **OI-ENV-01 (HIGH)** — `uv run pytest` without `uv sync --extra dev`
   silently uses a GLOBAL pytest and shows ~46 bogus failures (onboarding
   trap); **OI-DEC-01 (MEDIUM)** — decomposition quirks, fail-safe direction.
5. **ADR-004 / Phase-2b decision package** (`docs/plans/ADR-004-DECISION-PACKAGE.md`):
   the T3-vs-ADR-005 collision is confirmed by trace — under an empty-appendix
   gate, a T3 upgrade *removes* a claim from the appendix and therefore CAN
   create a PASS, contradicting "T3 never creates a PASS". Four options with
   Error-A/B analysis; agent recommends Option 4 (T3 may enable PASS + a
   `grounded_via` audit trail). Sai's ruling required.
6. **OI-CAL-01 found (twice, independently).** The gate SHIPS at `lex_tau=0.65`;
   CR-001's calibrated **0.71 was never deployed**, while CLAUDE.md/memory
   presented 0.71 as the operating value. Docs corrected to the truth; the
   deploy-or-hold decision is Sai's (it moves the live operating point).

## Scope discipline (why I fixed some and not others)

Fixed = **completing rulings Sai already gave**: AA-MOAT-001 was greenlit as
"compare value AND dimensional unit; fail-closed on any unit/quantity
mismatch" — round 1 under-delivered that; AA-MOAT-004 as "anchor absence on
discriminating tokens" — same. Homoglyph folding is the standing global NFKC
rule. Recorded-not-fixed = **new decisions**: AA-MOAT-007 (what counts as a
claim), OI-CAL-01 (deploy 0.71), ADR-004 (T3 semantics), OI-ENV-01/OI-DEC-01.

## The corpus caught my fix. Again.

Regeneration after the absence repair flipped THREE rows: q30 and q29 →
improvements (q30, a **labeled violation**, had been wrongly ABSENCE_SUPPORTED
since before this work — the gate now agrees with the human label; q29's "4,200
patients" vs source "4,200 units" caught by the new quantity comparison). But
q37 — a **labeled-grounded** absence — flipped to a false alarm: my first
coverage rule counted adjectives ("approved", "current") that no query would
carry, and "guidelines" ≠ "guideline". **The tempting fix was to lower the
coverage constant 0.5 → 0.4** (one character, all green). That is
threshold-fitting on n=1. The real fix was to change the rule's meaning: head
noun **plus one corroborating content word**, with plural stemming. q37 grounds;
the attack still dies. Final drift: 2 rows, both improvements.

**CR-001 re-run after the tier changes reproduces byte-identically** (lex_tau
0.71 recommended, held-out Error-A=0.20, Error-B=0.143, tp=6 fp=1 tn=4 fn=1) —
the "change → rerun → CR" rule satisfied with no CR update needed. Bootstrap
feature rows byte-identical.

**Near-miss worth recording:** `build_corpus.py` regenerates `labeling.csv` and
**wipes its human labels**. I ran it and blanked the n=12 bootstrap labels; the
fail-loud loader refused to calibrate on empty labels and I restored from git.
The loader's fail-loud design saved the audit evidence — but the builder should
never be able to destroy ratified labels. Logged as OI-CAL-02 below.

7. **OI-CAL-02 FIXED (label-destruction hazard).** `assert_labels_not_clobbered`
   in `scripts/calibrate.py`, called first by both labeling-CSV writers:
   a corpus rebuild now REFUSES to overwrite a CSV carrying any human label
   (names the file and the count). Red-first (both writers clobbered happily).
   Verified live: the builders now refuse to touch the 12 bootstrap and 52
   candidate labels. Added `--features-only` to `build_corpus_v2` so the
   post-change drift check — the very discipline that keeps catching my own
   fixes — regenerates gate predictions without going near the labels; without
   it, drift-checking a labeled corpus trips the guard, and that friction is
   exactly how someone eventually deletes the labels to "make it work."
   **This one was found by accident** (I ran the builder, it blanked CR-001's
   labels, the fail-loud loader stopped the calibration). It would have
   destroyed Sai's gold labels the first time anyone regenerated the corpus
   after ratification.

## Agents (telemetry)

| Agent | Model | Tokens | Tools | Outcome |
|---|---|---|---|---|
| Doc-conformance sweep | Sonnet 5 | 116,753 | 29 | Clean; independently re-derived OI-CAL-01 |
| Red-team round 2 | Opus 4.8 | 111,666 | 10 | 14 findings, all hand-verified true |
| α4 install validation | Sonnet 5 | 185,240 | 76 | READY + 3 new issues |
| ADR-004 package | Opus 4.8 | 82,271 | 19 | Confirmed T3/ADR-005 collision by trace |

Total ~496K subagent tokens. Zero re-dispatches. Every agent claim verified
against artifacts before acceptance; the red-team's 14 findings were reproduced
by hand at the CLI before a single line was written.

## Open / blocked (all Sai)

1. **Gold-label ratification** (inbox P1) — unchanged; package NOT affected by
   any of tonight's work (candidate verdicts are hand-authored, not gate-derived).
2. **AA-MOAT-007** — score verbless assertions as claims, or keep NON_CLAIM?
3. **AA-MOAT-003 / -005** — still deferred per 07-12 ruling.
4. **OI-CAL-01** — deploy lex_tau 0.71, or hold for CR-002?
5. **ADR-004 / Phase-2b** — rule on the T3 options (package written).
6. **OI-ENV-01** — make `install.sh` provision dev deps, or fail loud?

**Reflection:** The most instructive moment was not finding the homoglyph — it
was catching myself reaching for `0.5 → 0.4`. The corpus said one labeled row
disagreed with my new rule, and a single character would have silenced it. What
stopped it was that the constant had no *meaning* behind it; it was a knob I
had turned until the attack died, and turning it back until the false alarm
died too would have left a rule that was fitted to exactly two examples and
principled about nothing. Rewriting it as "head noun plus one corroborating
word" cost twenty minutes and produced a rule I can state in a sentence and
defend against a case I have not seen. That is the whole difference between
calibration and curve-fitting, and it showed up as a one-character temptation at
2 a.m.

**Next action:** Sai — six rulings above; ratification (inbox P1) is still the
one that unblocks the most (α2/CR-002 → α3 → α5).
