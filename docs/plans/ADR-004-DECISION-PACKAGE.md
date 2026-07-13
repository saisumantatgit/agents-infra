# ADR-004 / Phase-2b (T3 NLI Tier) — Decision Package for Sai

**Status:** Harvest-and-brief. No code integrated. Author: Claude (Opus 4.8), 2026-07-14.
**Sources:** reference worktree `agents-infra/.claude/worktrees/wf_f5845e10-a39-17`
(NLI build `d859e09` + drafted ADR-004); current branch `agent-assure-calibration-run`
post-moat-remediation (`6624e85`). All paths below are absolute-resolvable from those roots.

---

## 1. What the reference NLI build actually implements (`-17`, commit `d859e09`)

Files (from `git show d859e09 --stat`): `scripts/nli_tier.py` (+201, new),
`scripts/ground_check.py` (+213/−33), `tests/test_nli_tier.py` (+131),
`tests/test_ground_nli.py` (+192), `docs/adr/ADR-004-local-classifier-moat-boundary.md` (+81).
Base = agents-infra **main** (326 tests); build claims **340 passed** (326 + 14 new).

- **Classifier, not generator.** `nli_tier.py:52` pins `MoritzLaurer/DeBERTa-v3-base-mnli-fever-anli`;
  `NliModel.score` (`nli_tier.py:90`) returns `P(entailment)` in [0,1] — CPU, `eval()`,
  `torch.no_grad()`, no sampling. Direction fixed: premise = source window, hypothesis = claim.
- **Seam.** `ground_check` imports **no** torch / transformers / nli_tier. Scorer is injected via a
  structural `EntailmentScorer` Protocol (`score(premise,hypothesis)->float`). T3 is wired in
  `_ground_traced` (`d859e09` diff line ~186): `if nli is not None and t3_nli(...) → (GROUNDED, "T3_NLI")`,
  placed **strictly on the UNGROUNDED fall-through** — after citation resolution, verbatim filter,
  numeric gate. It structurally cannot touch UNVERIFIED_CITATION/_NUMBER/UNGROUNDABLE/UNCITED/absence/relation.
- **Fail-closed.** `load_nli_model()` (`nli_tier.py:113`) returns `None` on ANY exception
  (missing deps, corrupt/absent weights, bogus path) — never raises/hangs, `local_files_only=True`,
  no network at score time. `nli=None` (shipping default) → path inert → **zero model calls**, byte-identical to pre-T3 gate.
- **Model-absence handling.** In the sandbox torch/transformers are absent → load returns `None` →
  tier disabled → `describe()` (`nli_tier.py:183`) emits `{"enabled": false, ...}` in the report.
- **Test approach.** Determinism unit test is the named tripwire for the direction/kernel assumption;
  moat tests (b)/(d) proven **RED** first against a deliberately mis-ordered wire (fabricated citation
  reached PASS; numeric mismatch rescued), then GREEN after correct ordering. `nli_tau=0.8` provisional, CR-002 pending.
- **Honest gaps.** (i) `_MODEL_REVISION="main"` (`nli_tier.py:53`) is a **mutable tag**, not an immutable
  commit sha — the determinism/byte-stability guarantee is not yet pinned. (ii) Weights are **not vendored**;
  no repo-local weight path exists, so the enabled path is untested end-to-end in-tree. (iii) `nli_tau=0.8`
  is a projection, never LOO-validated on gold. (iv) Built on the 326-test main base — **predates ADR-005**
  (see §2, §4); the "T3 never creates a PASS" reasoning was written against the old ratio gate.

---

## 2. THE core moat-boundary question (state sharply for Sai)

**Under ADR-005, T3 flipping UNGROUNDED→GROUNDED CAN create a PASS that would not otherwise exist —
this collides with ADR-004's guarantee #3 as written.**

Mechanism, traced on current-branch `scripts/ground_check.py`:
`_NUMERATOR_VERDICTS = {GROUNDED, ABSENCE_SUPPORTED}` (line 1328). A scored claim whose verdict is NOT
in that set is appended to `retained_appendix` (line 1419). ADR-005 (accepted 2026-07-12) makes
`gate=PASS` require an **empty** appendix (line 1438: `or retained_appendix`). Therefore an
UNGROUNDED→GROUNDED T3 flip moves the claim **into** the numerator and **out of** the PASS-blocking
appendix — so a draft that was NEEDS_WORK purely because of that one UNGROUNDED claim becomes **PASS**.
That is T3 creating a PASS.

Reconciliation: the slogan "T3 never creates a PASS" was **never literally exact** even on `-17`'s ratio
base (8-grounded+1-UNGROUNDED = 88.9% NEEDS_WORK → T3 flip → 100% PASS). The *defensible* invariant is
narrower: **T3 never rescues a VIOLATION-class verdict** (fabrication/numeric/absence/relation/UNGROUNDABLE —
all short-circuit before T3). ADR-005 makes the residual gap unmissable because now a *single* plain
UNGROUNDED blocks PASS, so every T3 upgrade is potentially PASS-tipping. The decision is whether an
UNGROUNDED→GROUNDED classifier flip may unblock PASS.

### Options (Error-A recoverable false alarm; Error-B unrecoverable false PASS)

| # | Option | Error-A (paraphrase false flags) | Error-B (new false PASS) | Net |
|---|--------|----------------------------------|--------------------------|-----|
| 1 | T3 upgrades verdict but a T3-upgraded claim **still blocks PASS** (goes to a separate provisional appendix; not in empty-appendix predicate) | **Unchanged** — the paraphrase claim T3 was built to clear still blocks PASS | **Zero new** (structurally cannot create PASS) | T3 becomes cosmetic — kills its entire purpose under ADR-005 |
| 2 | T3 affects **score only**, not appendix | Unchanged (score is now informational per ADR-005) | Zero new | Same as (1): cosmetic under empty-appendix |
| 3 | **Full trust** once `nli_tau` gold-calibrated: T3 GROUNDED is a real GROUNDED, leaves appendix, can enable PASS | **Reduced** (design goal met) | **Non-zero & new**: a mis-entailment (neutral/contradiction scored ≥ nli_tau) creates a PASS. Bounded by nli_tau + fixtures C/D, NOT structurally zero | Breaks literal slogan; earns T3's value |
| 4 | **Hybrid (recommended):** same PASS semantics as (3), AND every T3-upgraded claim is listed separately in the report (`grounded_via: T3_NLI`) for human/audit eyes | Reduced (= option 3) | = option 3, but every PASS-enabling upgrade is independently spot-checkable | Option 3 + transparency; smallest delta from `-17` (tagging already built) |

**My recommendation (mine, not neutral): Option 4.** Options 1–2 preserve the slogan literally but make
T3 pointless — its only value is removing UNGROUNDED claims from the now-blocking appendix, which 1/2
forbid. The real trade is: keep an imprecise slogan and kill T3, OR keep T3 and state the invariant
honestly with an audit trail. The moat's true asymmetric guarantee (no VIOLATION-class rescue) survives
Option 4 intact; only the imprecise "never creates a PASS" phrasing must be amended to
"no *generative* model, and no rescue of a VIOLATION-class verdict; a local deterministic classifier may
upgrade UNGROUNDED→GROUNDED above a gold-calibrated `nli_tau`, and every such upgrade is logged and
auditable." `-17`'s `score_report` already tags `entry["grounded_via"]="T3_NLI"`, so Option 4 is the
least additional code. **Load-bearing premise:** Option 4's Error-B is acceptable ONLY if `nli_tau` is
LOO-validated on **gold** labels (never candidate) and fixtures C/D (paraphrase-overreach, contradiction)
hold — if that calibration is skipped, Option 4 degrades to an unbounded Error-B and must stay DEFAULT-OFF.

---

## 3. AA-MOAT-003, absence stemming, quantity-noun residuals under each option

- **AA-MOAT-003 (T1 verbatim over-reach on a superlative).** T1 marks the claim **GROUNDED**, so it
  **never reaches** the UNGROUNDED fall-through where T3 lives — *`-17` as built does nothing for it.*
  Closing it needs a **T1 residual-coverage check** (per OPEN-ISSUES systemic fix) that routes the
  uncovered residual to T3. Under Opt 1/2 that routing is futile (the routed claim would still block PASS
  even when correctly UNGROUNDED — actually fine for Error-B but the claim can never be *cleared* when it
  IS grounded). Under **Opt 3/4** the routed residual is entailment-checked and, being unsupported, stays
  UNGROUNDED → blocks PASS → **closes AA-MOAT-003**. So AA-MOAT-003's fix *requires Opt 3/4 semantics PLUS
  a T1-residual-routing change that is NOT in `-17`.*
- **Absence stemming ("docs" ≠ "documentation").** Absence path short-circuits before T3 → **orthogonal
  to the option chosen.** Needs a stemmer at the `check_absence` anchor boundary (current
  `ground_check.py:971`), fail-closed direction preserved. Rides *with* the 2b bundle, not gated by it.
- **Quantity-noun residual ("operations" vs "gigabytes").** Numeric tier, short-circuits before T3 →
  **orthogonal.** Needs the numeric parser to capture+compare the quantity-noun/unit (the AA-MOAT-001
  extension, fail-closed on mismatch). Independent of the T3 option.

Net: only **AA-MOAT-003** genuinely interacts with the T3 decision (and only via added T1 routing). The
other two are independent fail-closed tier fixes bundled into α3 for convenience, decidable regardless of option.

---

## 4. Rebase reality — bringing `-17` onto `agent-assure-calibration-run`

- **`-17` base = agents-infra main `fef21e4`, 326 tests** (OI-BUILD-01). Current branch is well past that:
  moat-remediation (`6624e85`) added ADR-005 empty-appendix cap, rate-qualifier `numeric_ok`,
  discriminating-anchor `check_absence`, and red_team_moat green guards. Current suite: **351 passed +
  2 xfailed** (AA-MOAT-003/-005, the deferred OPEN items) **+ 4 failed** — the 4 failures are the
  **in-flight citation-regex reimplementation** (`tests/test_letter_suffixed_citations.py`, TDD red),
  a separate on-branch workstream, NOT part of this package.
- **Conflicts expected in `scripts/ground_check.py` — near-certain.** `-17` rewrote `ground()`,
  `_ground_traced`, and `score_report` (+213/−33); ADR-005 edited the **same** `score_report` gate block
  (the `or retained_appendix` clause, line 1438) and the `ground()` region. `-17`'s `score_report` diff
  adds `nli=`/`nli_tau=` params and `grounded_via` tagging inside the block ADR-005 rewrote → manual
  three-way merge in `score_report` + `ground` is required. `nli_tier.py` and the two new test files are
  additive (no conflict).
- **Test-count delta.** `-17` claims +14 over a 326 base = 340. Re-baselined onto the current
  ~353-test branch, the 14 NLI tests should add cleanly, but **`-17`'s moat tests (b)/(d) assume the
  pre-ADR-005 gate** — they must be re-proven red/green against the *post-ADR-005* `score_report`, because
  their PASS/NEEDS_WORK expectations change under the empty-appendix cap. Do NOT trust `-17`'s green claim
  post-rebase (discontinuity distrust) — re-run the full suite + red-team harness from evidence.
- **Sequencing collision.** The citation-regex on-branch reimplementation also touches `ground_check.py`
  citation classification; land it (and its 4 red tests → green) **before** the NLI rebase to avoid a
  double three-way merge on the same file.

---

## 5. Blocking questions for Sai (each answerable in one line)

1. Adopt **Option 4** (T3 can enable PASS + per-claim `grounded_via` audit trail), or Option 1/2 (T3 stays
   cosmetic under ADR-005), or Option 3 (enable without the separate audit listing)?
2. Ratify ADR-004's three mechanical guarantees as the moat boundary (classifies-not-generates / local-deterministic / UNGROUNDED→GROUNDED-only)? (Escalation §1)
3. Approve amending the "ZERO LLM calls" slogan to "zero *generative* calls; local non-generative classifier permitted, no VIOLATION-class rescue, DEFAULT-OFF until gold-calibrated"? (Escalation §4)
4. Confirm you will ratify **gold** `nli_tau` labels before any shipping-default enablement (Opt 3/4 Error-B is bounded only by this)? (Escalation §2)
5. Should AA-MOAT-003's T1-residual-routing fix be scoped **into** α3 (it needs Opt 3/4 semantics), or deferred to its own slice?
6. Pin the model to an **immutable commit sha** and **vendor weights in-repo** before enablement (yes = determinism guarantee real; currently `revision="main"`, unvendored)?

---

## 6. Cost / effort estimate for α3 execution once ruled

| Work item | Est. tokens | Notes |
|-----------|-------------|-------|
| Rebase `-17` onto branch; resolve `ground_check.py` 3-way merge (`score_report`+`ground`) | ~0.8–1.2M | after citation-regex lands; Opus-tier merge |
| Implement chosen option semantics (appendix/score/audit-trail wiring) | ~0.4–0.8M | Opt 4 smallest (tagging exists); Opt 1/2 need a new provisional-appendix path |
| AA-MOAT-003 T1-residual routing → T3 (if scoped in, Q5) | ~0.6–1.0M | new coverage check + red-first regression |
| Absence stemming + quantity-noun numeric fixes (bundled residuals) | ~0.5–0.9M | orthogonal, fail-closed, red-first each |
| Pin sha + vendor weights; enabled-path end-to-end test | ~0.3–0.5M | infra; unblocks real inference test |
| Gold-label `nli_tau` set + LOO calibration + **CR-002** | ~0.6–1.0M | **needs Sai gold labels**; ADR-025 CR ≤80 lines |
| Red-team harness fixtures C/D (paraphrase-overreach, contradiction) + full-suite re-verify | ~0.4–0.7M | release gate; any unexpected PASS blocks |
| **Total α3** | **~3.6–6.1M** | matches spec's "2b Medium ~1–2M" only for the bare tier; the ADR-005 interaction + AA-MOAT-003 + calibration push it higher |

**Human-gated, cannot proceed without Sai:** Q1–Q4 rulings and the gold `nli_tau` labels (standing
gold-label gate). Everything else is buildable once ruled.

---
**Post-write correction (2026-07-14, same session):** the "4 failing tests"
noted in §Rebase reality were the in-flight red-first window of the
citation-regex fix (OI-CITE-01); that fix landed the same night — suite is
green (355 passed + 2 xfailed) and OI-CITE-01 is CLOSED, so the NLI rebase no
longer needs to sequence around it. Also relevant to Q-rulings: OI-CAL-01
(lex_tau runs at 0.65 shipped; CR-001's 0.71 undeployed) — see OPEN-ISSUES.
