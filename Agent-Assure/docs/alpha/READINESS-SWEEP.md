# Agent-Assure — Alpha-Readiness Sweep Dossier

**Date:** 2026-07-11 · **Branch:** `agent-assure-calibration-run` · **Audience:** Sai + next session (assumes zero prior context)

This dossier is the single-page state-of-the-moat as of this sweep. It certifies
whether Agent-Assure's deterministic grounding gate is regression-clean against
the adversarial red-team harness, records the two unblocked builds now awaiting
the Opus whole-branch gate, and enumerates exactly what is done, what is blocked
on Sai, and what NOT to redo.

---

## 1. Executive Verdict

**NOT regression-clean this sweep. DO NOT RELEASE.**

Regression-clean is defined as: NO red-team attack class produced a wrongful PASS
**AND** no adversarial verifier confirmed a `moat_violation`. Both conditions fail.

- **6 of 12** red-team attack classes produced at least one wrongful PASS
  (`any_wrongful_pass=true`): numeric-drift-unit, numeric-drift-decimal,
  paraphrase-overreach, unsubstantiated-absence, unsupported-relation,
  letter-suffixed-source-id.
- **6 confirmed `moat_violation=true`** verdicts from adversarial verification,
  every one flagged RELEASE BLOCKER (all `red_first_credible=true` — the reds are
  real, independently reproduced, not artifacts of a bad harness).

Each moat violation is an **Error-B** event under the pinned invariant — a
fabrication certified as PASS, which is the unrecoverable class. Every one of the
six fixes alters the Error-A/Error-B trade-off or the gate score bar, so **all six
are Escalation-rule-#1 items requiring Sai adjudication** before any patch lands.

One structural finding threads all six: the **threshold-dilution vector**. A
single fabricated claim padded to ≤10% of a ≥10-claim draft clears the ≥90% score
gate, so the retained-appendix fabrication survives to PASS. The letter-suffixed
and numeric-drift-decimal verdicts both name this explicitly; the systemic fix
(any retained fabrication-class verdict hard-caps the gate below PASS) plausibly
closes most of the class at once — but that is Sai's threshold/spec call.

---

## 2. Moat Red-Team Results

12 attack classes, 49 adversarial drafts total. "Wrongful PASS?" = did any draft
in the class gate PASS when it must FAIL.

| Attack class | Drafts | Wrongful PASS? | What the result proves |
|---|---|---|---|
| fabricated-citation | 4 | No | Fabricated `[S9]`-style markers cannot talk their way to PASS — the core moat holds. |
| numeric-drift-unit | 4 | **YES** | Numeric tier compares magnitude but not the dimensional unit; a drifted unit rides through as GROUNDED. **Moat violation.** |
| numeric-drift-magnitude | 4 | No | A drifted magnitude with matching unit is caught by value matching. |
| numeric-drift-decimal | 4 | **YES** | A fabricated decimal survives via threshold-dilution — a gate-aggregation defect in `score_report`, not a numeric-tier break. **Moat violation.** |
| paraphrase-overreach | 4 | **YES** | A verbatim ≥8-token span short-circuits T1 while the claim's uncovered residual assertion goes unsupported. **Moat violation.** |
| uncited-claim-and-detached-marker | 4 | No | Detached markers (after the period) correctly read UNCITED and fail-safe. |
| unsubstantiated-absence | 4 | **YES** | Absence grounding anchors on the first head noun / generic corpus words, not the discriminating tokens of the negated proposition. **Moat violation.** |
| unsupported-relation | 4 | **YES** | Comparative/causal predicates ride through via (a) verbatim tier grounding the factual core and (b) two-source rule checking endpoint-noun presence, not the relation. **Moat violation.** |
| summary-only-source | 4 | No | Claims citing only `haiku_summary` correctly resolve UNGROUNDABLE. |
| homoglyph-nfkc-bypass | 4 | No | NFKC normalization at the ingestion boundary defeats homoglyph substitution. |
| letter-suffixed-source-id | 5 | **YES** | A fabricated letter-suffixed marker (`[S3a]`) was silently downgraded to UNCITED, then diluted below the 10% bar to reach PASS. **Moat violation.** (The regex half of this is FIXED — see §3; the dilution half is the escalation.) |
| verbatim-near-miss-and-cross-session | 4 | No | Near-miss spans and prior-session citations correctly fail; the store is per-session. |

**Held clean: 6/12.** fabricated-citation, numeric-drift-magnitude,
uncited/detached-marker, summary-only-source, homoglyph-nfkc-bypass,
verbatim-near-miss-and-cross-session.

---

## 3. Unblocked Builds — Reviewable Diffs (NOT merged; awaiting Opus whole-branch gate)

Two builds were completed this sweep. Both are **red-first verified** and
**moat-safe**, sitting in isolated worktrees. Neither is merged.

### 3a. citation-regex — letter-suffixed citation IDs

- **Worktree:** `/Users/saisumanthbattepati/vibe-coding/Agents/agents-infra/.claude/worktrees/wf_f5845e10-a39-16`
- **red_first:** true · **moat_safe:** true · **Suite:** 329 passed in 12.65s · **Blockers:** None
- **What it fixes:** Closes a genuine Error-B hole — a fabricated letter-suffixed
  citation (`[S3a]`) was silently downgraded to UNCITED, bypassing the hard cap and
  reaching PASS. The regex now recognizes letter-suffixed markers so they are
  classified and grounded rather than dropped.
- **Baseline reconciliation (load-bearing — read this):** the task brief cited a
  334 baseline and CLAUDE.md says 327, but the **verified artifact truth on this
  branch is 326 pre-existing tests**, all green on BOTH pre-fix and post-fix source
  (confirmed by git-stashing the source edit and re-collecting). The widening
  regresses zero existing tests; final suite is **326 + 3 = 329**.
- **Environmental note:** the `syntok` runtime dep had to be provisioned via
  `uv sync --extra dev` before the suite could run — the 39 initial failures were
  `ModuleNotFoundError`, not from this change.
- **Non-blocking follow-up:** if any gold label ever uses a letter-suffixed marker,
  re-run calibration + emit a fresh CR. None do today.

### 3b. Phase-2b T3 NLI entailment tier — reference implementation (DEFAULT-OFF, fail-closed)

- **Worktree:** `/Users/saisumanthbattepati/vibe-coding/Agents/agents-infra/.claude/worktrees/wf_f5845e10-a39-17`
- **red_first:** true · **moat_safe:** true · **Suite:** 340 passed in 5.28s (326 baseline + 14 new)
- **Ships DEFAULT-OFF:** `ground_check` imports no model; the shipping default
  (`nli=None`) is byte-identical to the pre-T3 gate and makes zero model calls, so
  the "ZERO LLM" header remains literally true today.
- **Blockers — deferred BY DESIGN (escalation-respecting), NOT defects:**
  1. **ADR-004 'local-classifier moat boundary'** written as **Status=Proposed**;
     CLAUDE.md and the `ground_check.py` "ZERO LLM" header were **NOT** amended —
     that is a moat-boundary change (Escalation §1/§4) requiring Sai ratification.
  2. **`nli_tau=0.8` is PROVISIONAL** (CR-002 pending); gold-label ratification is
     a Sai gate (Escalation §2).
  3. **Plan Task 5** (calibration `tier_sensitive` split into lex/nli) and
     **Task 6** (CR-002) NOT implemented — the `calibration/` directory is ABSENT in
     this worktree. (Also absent: design spec
     `docs/superpowers/specs/2026-06-20-agent-assure-design.md` and
     `ALPHA-READINESS-PLAN.md`; α3 reqs were taken from the task brief + live code
     per the plan's reconcile-on-resurface caveat.)
  4. **Task 4** richer always-present `nli_tier` report block NOT added to
     `score_report` (would break strict default byte-identity); the disabled-notice
     is surfaced via `nli_tier.describe()` at the caller layer instead — a design
     call left for the Opus gate.
  5. **`--nli` CLI opt-in flag** in `main()` not added (out of STEPS scope).
- **Untested-here caveat (load-bearing):** real DeBERTa weights are not downloadable
  in this sandbox — that is the fail-closed condition the tests exercise via a
  deterministic stub. Real-model determinism (Task 1's frozen-value test) is
  **untested here** and must be validated where weights are available before any
  shipping default.

---

## 4. Adversarial Verification Verdicts

All eight verdicts below are independent adversarial reviews with
`red_first_credible=true`.

### APPROVE / MERGE

**citation-regex build (letter-suffixed citation IDs) — commit `9d14ff1`**
`confirmed=true · moat_violation=false` — **APPROVE / MERGE.** Systemic fix
correctly closes a genuine Error-B hole (fabricated letter-suffixed citation
silently downgraded UNCITED → bypassed the hard cap → reached PASS). Fix is minimal,
moat-aligned (strictly reduces Error-B, no LLM, no new verdict, NFKC intact),
red-first evidence independently reproduced pre-fix, full suite green (329 passed).
Carry the section-7 follow-up (re-run calibration + CR only if any gold label ever
uses a letter-suffixed marker — none do today) as non-blocking calibration hygiene.

### ACCEPT AS REFERENCE — DO NOT MERGE / DO NOT ENABLE

**Phase-2b T3 NLI entailment tier (DEFAULT-OFF, fail-closed) — worktree `wf_f5845e10-a39-17`**
`confirmed=true · moat_violation=false` — **ACCEPT as a reference implementation;
DO NOT MERGE or enable.** The moat holds: the shipping default (`nli=None`) is
byte-identical to the pre-T3 gate and makes zero model calls; ADR-004 is correctly
filed as Proposed; CLAUDE.md / the `ground_check.py` "ZERO LLM" header are correctly
left un-amended pending the Sai gate. **Before ANY enablement:**
1. Sai-ratify ADR-004's three mechanical guarantees (Escalation §1/§4).
2. Resolve the `tier_sensitive`-vs-`nli_tau` calibration-conflation open item —
   introduce a distinct nli-sensitive tag so a `lex_tau` LOO never ingests a
   T3-governed row.
3. Run the ≥n=50 gold-labelled **CR-002** to validate `nli_tau` (currently
   provisional 0.8, inert).
4. Confirm the DeBERTa checkpoint is pinned to an immutable commit SHA (currently
   `revision='main'`) and vendored for `local_files_only` load before the tier is
   ever threaded on.

### RELEASE BLOCKERS — confirmed moat violations (all → Sai, Escalation rule #1)

**red-team numeric-drift-unit** — `confirmed=true · moat_violation=true` —
**RELEASE BLOCKER.** Systemic fix (not per-case): extend the numeric parser to
capture and compare the dimensional unit (rate denominator + measured quantity)
adjacent to each number, fail-closed on any unit/quantity mismatch, preserving the
Error-B ≥ Error-A monotonicity invariant. Add a proven-red regression against
pre-fix code (must show the GROUNDED/PASS results) before claiming coverage, then
re-run to green. After the classify/tiers/numeric changes, `calibration/` goes
stale — rerun calibration + emit a new ADR-025 CR. Escalate to Sai before any
release re-verification.

**red-team numeric-drift-decimal** — `confirmed=true · moat_violation=true` —
**BLOCK RELEASE.** The gate certifies (PASS, exit 0) a draft with a fabricated
numeric claim via **threshold-dilution** — Error-B. This is a gate-aggregation
defect in `score_report`, not a numeric-tier break. Fix requires changing gate
semantics so any retained violation-class verdict (UNVERIFIED_NUMBER at minimum;
consistently also UNGROUNDED / UNVERIFIED_ABSENCE / UNVERIFIED_RELATION / UNCITED /
UNGROUNDABLE) hard-caps the gate at NEEDS_WORK regardless of score — mirroring the
existing UNVERIFIED_CITATION override — OR a score-gate policy where no PASS may
carry a non-empty `retained_appendix`. Alters the Error-A/Error-B trade-off and the
gate score bar → Escalation #1 → Sai. Re-calibrate + new CR + proven-red regression
(`assert gate != PASS for any draft whose retained_appendix is non-empty`). Do NOT
autonomously patch the gate bar.

**red-team paraphrase-overreach** — `confirmed=true · moat_violation=true` —
**RELEASE BLOCKER.** Systemic fix (not case): add a claim-coverage / residual-
assertion gate to T1 so a verbatim ≥8-token span cannot ground a claim whose
remaining content tokens are unsupported — require the material assertion (not just
an embedded quote) be covered, or route any claim with substantial uncovered
residual to the T3 entailment tier and never let T1 short-circuit a fail-closed
check. Touches tiers/classify/score → fresh calibration + new ADR-025 CR; preserve
Error-B monotonicity. Add all four PASS drafts (1,2,3,6) to the regression harness
as must-FAIL, proven red first (INS-005). Escalate to Sai (rule 1).

**red-team unsubstantiated-absence** — `confirmed=true · moat_violation=true` —
**BLOCK RELEASE.** Fix `check_absence` / `_extract_absence_subject` before any
re-verification. Systemic fix (default): (1) anchor absence grounding on the claim's
discriminating tokens (named entities, numerics, multi-word noun phrase), not the
first head noun; (2) replace substring-in-`query_provenance` matching with a rule
requiring the specific negated proposition's subject to be queried AND positive
evidence the store lacks the asserted content; (3) treat generic corpus-wide words
(present in a majority of `query_provenance` strings) as non-discriminating and
insufficient for the 2-query bar. Add these drafts as proven-red fixtures
(`assert NOT PASS`) per INS-005 before claiming the fix. Do NOT narrow the store's
`query_provenance` as a case patch — that hides the collision. Escalate to Sai
(rule 1).

**red-team unsupported-relation** — `confirmed=true · moat_violation=true` —
**RELEASE BLOCKER.** Escalate to Sai (rule 1) + the moat invariant. The gate
certifies unsupported comparative/causal relations as PASS 100 via two paths:
(1) the NUMERIC/FACTUAL verbatim tier grounds a claim's factual core while an
unchecked relational predicate rides in the same clause; (2) `ground_relational`'s
two-source rule checks endpoint-noun presence, not support for the relation itself.
Both are genuine Error-B. A fix requires a deterministic, LLM-free predicate/relation
check (the T3 NLI tier is the planned Phase-2b home but must fail-closed and never
CREATE a pass); classifying comparatives as RELATIONAL is necessary but insufficient
since the relational path itself is broken. Any fix must re-run red-team +
calibration and add proven-red regression drafts for all four attacks first.

**red-team letter-suffixed-source-id** — `confirmed=true · moat_violation=true` —
**BLOCK RELEASE.** Do NOT fix autonomously — the fix changes the gate PASS bar and
the Error-A/Error-B trade-off (Escalation rule #1, STOP and ask Sai). Present to
Sai: the systemic fix is to extend the hard-override so that ANY fabrication-class
verdict in the retained appendix (UNCITED, UNGROUNDED, UNVERIFIED_*, UNGROUNDABLE —
not only UNVERIFIED_CITATION) caps the gate below PASS, i.e. PASS requires zero
unsupported factual/numeric claims rather than merely a ≥90% ratio. This raises
Error-A (a genuinely forgotten citation flips PASS→NEEDS_WORK) but that is
recoverable and permitted under the asymmetric invariant. Before any change: add a
proven-red regression asserting draft5 must NOT gate PASS, run against current code
to see it PASS-fail, then re-run the full harness — this dilution vector likely
affects EVERY attack class (numeric-drift, paraphrase, uncited, absence, relation),
since any single fabricated claim padded to ≤10% of a ≥10-claim draft will PASS.
Fold a padded-dilution variant into the fixture set for permanent regression cover.

**Note the citation-regex/letter-suffixed relationship:** the regex build (§3a,
merge-approved) closes the *classification* half — the marker is no longer silently
dropped to UNCITED. The letter-suffixed red-team verdict above is the *dilution*
half — even correctly classified as a fabrication, a single such claim padded below
10% still clears the score gate. The regex fix is necessary but not sufficient; the
dilution escalation is the systemic close.

---

## 5. Ratification-Day Prep — Where Each Artifact Lives

Produced this sweep to make Sai's ratification session turnkey:

| Artifact | Purpose | Location |
|---|---|---|
| Phase-1b evidence dossier | Evidence backing the Phase-1b gate decision | Phase-1b evidence dossier (ratification-day prep set) |
| Staleness map | Which `calibration/` outputs go stale on which code changes | Staleness map (ratification-day prep set) |
| NLI TDD plan | The red-first test-driven plan for the Phase-2b T3 tier | NLI TDD plan (ratification-day prep set) |

These three were prepared together as the ratification-day package. Confirm exact
paths at session start before relying on them (reconcile-on-resurface caveat applies —
some plan/spec docs were absent in the T3 worktree this sweep).

---

## 6. Blocked On Sai (nothing below proceeds without a Sai decision)

1. **Gold-label ratification (inbox P1)** — gates **α2** and **CR-002**. Claude-
   generated labels are `candidate`; only Sai-ratified labels are `gold`; calibrate
   on gold only. Standing gate (Escalation §2).
2. **Phase-1b gate decision** — the go/no-go on the Phase-1b tier, backed by the
   evidence dossier in §5.
3. **Error-B floor anchor** — the held-out Error-B value that all six moat fixes
   must not exceed (the monotonicity anchor for `Error-A minimized subject to
   Error-B ≤ floor`).
4. **All six moat-violation fixes (§4)** — every one alters the Error-A/Error-B
   trade-off or the gate score bar → Escalation rule #1. The likely-shared systemic
   fix (retained-fabrication hard-cap) is one threshold/spec decision that may close
   most of the class; still Sai's call.
5. **ADR-004 ratification** — the local-classifier moat-boundary (Status=Proposed),
   gating any T3 enablement and the CLAUDE.md / "ZERO LLM" header amendment.

---

## 7. Done Ledger — do NOT redo; and the exact next commands

### Already done — DO NOT REDO

- **citation-regex build** — complete, red-first verified, suite 329 green,
  merge-APPROVED at commit `9d14ff1`, worktree `wf_f5845e10-a39-16`. Awaits only the
  Opus whole-branch gate before merge. Do not re-implement or re-verify.
- **Phase-2b T3 NLI reference implementation** — complete as a DEFAULT-OFF reference,
  red-first, suite 340 green, ACCEPTED-as-reference (NOT to merge/enable), worktree
  `wf_f5845e10-a39-17`. Do not re-implement; the deferred items (§3b, §4) are Sai
  gates, not unfinished work.
- **12-class red-team sweep** — run this sweep (49 drafts). The six wrongful-PASS
  classes are characterized and verifier-confirmed; do not re-discover them. The
  work item is the FIX (Sai-gated), not another detection pass.
- **Baseline reconciliation** — the true baseline on this branch is **326** pre-
  existing tests (not 327 per CLAUDE.md, not 334 per the task brief), confirmed by
  git-stash re-collection. Use 326 as the baseline; do not re-audit.

### Exact next commands (for the next session, after Sai's gates)

Run from `Agent-Assure/`:

```bash
# 0. Provision env (syntok is a runtime dep; skipping it caused 39 phantom failures)
bash install.sh
uv sync --extra dev

# 1. Reproduce the current red-team state (confirm the 6 wrongful-PASS classes)
#    via the assure-red-team harness before touching any fix.

# 2. After Sai ratifies gold labels + the Error-B floor + the gate-bar decision,
#    add proven-red regressions FIRST (INS-005), run them against current code to
#    see them wrongly-PASS, THEN implement the retained-fabrication hard-cap fix.

# 3. Re-run the full suite (expect 326 baseline + new tests) and the red-team harness
uv run pytest
#    every red-team class must FAIL (never PASS).

# 4. Because classify/tiers/score change, calibration/ goes stale — rerun + emit CR
uv run python -m calibration.run_calibration   # MUST be module form; script form breaks scripts.calibrate

# 5. For T3 enablement only (after ADR-004 ratification): pin the DeBERTa checkpoint
#    to an immutable commit SHA, vendor for local_files_only, run CR-002 (>=n=50 gold).
```

**Load-bearing assumption of this whole dossier:** the red-team harness's expected
verdicts are correct — i.e., each of the 49 drafts genuinely *should* FAIL. Every
"wrongful PASS" and every `moat_violation` verdict is measured against that ground
truth. If a harness fixture were mislabeled (a draft that should legitimately PASS),
that class's blocker would collapse. The verifiers marked all six
`red_first_credible=true` and independently reproduced the reds, which is the outside
check on this assumption — but it is the one premise a fresh reviewer should probe
first.
