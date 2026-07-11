# Phase 2b — T3 NLI Entailment Tier — TDD Implementation Plan

**Slice:** 2b (per `docs/PHASE2-SEQUENCING.md`, order 2c-harness → **2b** → 2a → 2d).
**Format:** writing-plans (same as the Phase 1a/1b TDD plans). Ordered tasks, each
with goal / files / red-first test / exit criterion. **This is a plan — no code is
written here.**
**Author:** Claude (autonomous, on Sai's delegated authority, 2026-07-11).

---

## Source-document status (read before trusting this plan)

| Cited source | Status in this worktree |
|---|---|
| `docs/superpowers/specs/2026-06-20-agent-assure-design.md` | **ABSENT** — no `superpowers/` dir exists here. Phase-2b requirements below are taken from the **task brief's α3 property list** and the live code (`scripts/ground_check.py`, `scripts/calibrate.py`), which are authoritative in its absence. If the design spec resurfaces, reconcile §4.4/§4.6 (tier dispatch) and §12 (calibration) against Tasks 3 and 5 before merge — spec-source conflict is a **Sai escalation** (CLAUDE.md Escalation §3), not a silent choice. |
| `docs/plans/ALPHA-READINESS-PLAN.md` (phase α3) | **ABSENT** — `docs/plans/` holds only `reports/`. α3 requirements are consumed from the task brief verbatim (enumerated in "Required properties" below). |
| `docs/PHASE2-SEQUENCING.md` | Present — read. 2b sized "Medium (~1–2M), fail-closed, optional." |
| `calibration/CR-001-bootstrap-lex-tau.md` | Present — `nli_tau` projected 0.8, **status `deferred`** (T3 unbuilt). Task 6 supersedes with CR-002. |

---

## The moat boundary this slice must not cross (non-negotiable)

Copied from the task brief + CLAUDE.md so every executor sees it before touching code:

1. **Error-B (a fabrication / unsupported claim certified PASS) is UNRECOVERABLE.**
   Error-A (false alarm on a real claim) is recoverable. No change may reduce
   Error-A by raising Error-B. T3 exists **only** to cut Error-A (paraphrase
   false-flags); it may never create an Error-B.
2. **The verdict is a mechanical fact about the store.** Verdict taxonomy is
   **CLOSED** — T3 invents no verdict. Its *only* permitted effect is flipping a
   single claim `UNGROUNDED → GROUNDED` when entailment ≥ `nli_tau`. Every other
   verdict is untouchable.
3. **`haiku_summary` can NEVER ground a claim** → the claim stays `UNGROUNDABLE`.
   T3 runs on verbatim sources only; the dispatcher reaches T3 strictly *after*
   the verbatim filter.
4. **NFKC-normalize before ANY text match** — premise and hypothesis both
   normalized at the tier's ingestion boundary before tokenizing into the model.
5. **Any adversarial draft that reaches gate PASS despite a fabrication /
   unsupported claim is a RELEASE BLOCKER.**

### The local-classifier boundary — make this explicit in code + ADR

The moat statement (CLAUDE.md, `ground_check.py` header) currently reads "**ZERO
LLM calls during grounding**." A **local DeBERTa-MNLI classifier is NOT an "LLM in
the grounding path" the way a generative judge is**, and the plan must encode
*why*, in three mechanical guarantees the ADR (Task 0) ratifies:

- **It classifies, it does not generate.** Input = (premise, hypothesis); output =
  a fixed 3-way probability vector `{entailment, neutral, contradiction}`. There is
  no free-text generation, no instruction-following, no place for a fabricated
  `[S9]` to "argue" for itself.
- **It runs locally + deterministically.** Pinned model revision (sha), CPU device,
  `eval()` mode, `torch.no_grad()`, no dropout, no sampling, no network at gate
  time. The same (premise, hypothesis) yields the same score bit-for-bit → a
  verdict stays a *reproducible mechanical fact*, which is the property calibration
  (LOO held-out) depends on. A nondeterministic tier would break the moat even if
  local.
- **It can never CREATE a PASS.** Its output feeds exactly one branch:
  `UNGROUNDED → GROUNDED` under `nli_tau`. It sits *after* citation resolution, the
  verbatim filter, and the numeric gate — so it structurally cannot touch
  `UNVERIFIED_CITATION`, `UNVERIFIED_NUMBER`, `UNGROUNDABLE`, `UNCITED`, or any
  relational/absence verdict.

**Default posture: the tier ships DEFAULT-OFF.** `ground()`'s pure default
(`model=None`) is byte-identical to today's behaviour — the "zero-model" moat holds
unchanged for every caller that does not opt in. The tier is enabled only when a
model handle is threaded in, and only after (a) the Task-0 ADR is accepted and
(b) `nli_tau` is gold-calibrated (Task 6). Until then it is a flagged, opt-in,
provisional capability — the same "ship-flagged → instrument → recalibrate" path
the spec used for `lex_tau`.

**Load-bearing assumption (surface it, per CLAUDE.md):** the entailment *direction*
is `premise = source window`, `hypothesis = claim` (source entails claim), and the
chosen DeBERTa-MNLI checkpoint is deterministic on CPU. If the direction is
inverted, or the checkpoint carries nondeterministic kernels, the tier is unsound
and Task 1's determinism test is the tripwire that must catch it before Task 3.

---

## Where T3 slots in (evidence trace)

`ground()` (`scripts/ground_check.py:1145–1199`) dispatches in order. The T1/T2
tier check is the penultimate step:

```
1193  if claim.kind == NUMERIC and not numeric_ok(claim, verbatim): return UNVERIFIED_NUMBER
1196  if t1_verbatim(claim, verbatim) or t2_lexical(claim, verbatim): return GROUNDED
1199  return UNGROUNDED        # ← T3 inserts on THIS fall-through only
```

T3 is inserted between line 1196 and line 1199, guarded by `model is not None`:
`if model is not None and t3_nli(claim, verbatim, model, nli_tau): return GROUNDED`.
Every short-circuit above line 1196 (UNCITED, UNVERIFIED_CITATION, UNGROUNDABLE,
UNVERIFIED_NUMBER) is untouched — this is the structural proof T3 cannot rescue a
fabrication. The `tier_sensitive` calibration seam (`calibrate.py:96`, the
`f11f8d4` bug class) is the #1 risk and gets its own task (Task 5).

---

## Task 0 — ADR: local-classifier moat boundary (PREREQUISITE, escalation)

- **Goal:** Amend the moat statement to permit a local, deterministic,
  non-generative classifier whose sole effect is `UNGROUNDED → GROUNDED` under a
  threshold. Encode the three mechanical guarantees above as acceptance criteria.
  This is a moat-boundary change → **STOP and get Sai's approval** (CLAUDE.md
  Escalation §1/§4). No tier code merges to a shipping default until accepted.
- **Files touched:** `docs/adr/ADR-004-local-classifier-moat-boundary.md` (new);
  on acceptance, amend the moat paragraph in `CLAUDE.md` and the `ground_check.py`
  module header. Use the ADR-023 amendment form for CLAUDE.md/spec cross-refs.
- **Red-first test:** none (governance artifact). Its "test" is Sai's ratification.
- **Exit criterion:** ADR status `Accepted` (Sai) **OR** tier remains DEFAULT-OFF
  and unshipped. Task 3+ may be *built and tested* behind the off-default before
  acceptance; they may not become a shipping default until Task 0 is Accepted.

## Task 1 — NLI adapter: pinned, local, deterministic, fail-closed load

- **Goal:** Isolated module wrapping the local DeBERTa-MNLI. Public surface:
  `load_nli_model() -> NliModel | None` (returns `None` on ANY load failure —
  never raises, never hangs, never touches the network at gate time) and
  `entailment_score(model, premise, hypothesis) -> float`. NFKC-normalize both
  strings first. Deterministic: pinned revision constant, `cpu`, `eval()`,
  `no_grad()`, no sampling. Model weights vendored/cached under a repo-local path;
  load reads local files only.
- **Files touched:** `scripts/nli_tier.py` (new); `tests/test_nli_tier.py` (new);
  `pyproject.toml` (add `transformers`/`torch` as an **optional extra**, e.g.
  `[project.optional-dependencies] nli = [...]`, so `Assure installs alone` and the
  base gate stays dependency-light).
- **Red-first tests (write first, run RED before implementing):**
  1. `test_load_failure_returns_none_not_raise` — point the model path at a bogus
     dir → `load_nli_model()` returns `None`, does not raise. (RED: symbol absent.)
  2. `test_entailment_score_deterministic` — same (premise, hypothesis) over two
     independent loads yields a score equal to a **frozen expected value** to fixed
     decimals. Catches nondeterministic kernels / wrong device.
  3. `test_nli_load_and_score_open_no_socket` — monkeypatch `socket.socket` to raise;
     load + score still succeed (proves no network at gate time).
  4. `test_nli_nfkc_normalizes_inputs` — a homoglyph/compatibility-form premise
     scores identically to its NFKC form.
- **Exit criterion:** all four RED→GREEN; model pinned by a `_MODEL_REVISION`
  constant; determinism test green across two loads.

## Task 2 — `t3_nli`: pure tier predicate (verbatim-only, fail-closed)

- **Goal:** `t3_nli(claim, verbatim_sources, model, nli_tau) -> bool`. True iff for
  some ±2-sentence window of some verbatim source,
  `entailment_score(model, window, claim.text) >= nli_tau`. Reuses the existing T2
  windowing helper (`_split_sentences` + ±2 window) so premise granularity matches
  T2. Returns `False` when `model is None` (tier disabled → fail-closed) and when
  `verbatim_sources` is empty. Strips citations from the claim before scoring.
- **Files touched:** `scripts/ground_check.py` (new function next to `t2_lexical`);
  `tests/test_nli_tier.py` (extend).
- **Red-first tests:**
  1. `test_t3_grounds_genuine_paraphrase` — fixture where the claim is a true
     restatement of a verbatim source with **< 8-token verbatim span AND lexical-F1
     < lex_tau** (assert `t1_verbatim` False and `t2_lexical` False first, locking
     that T1/T2 genuinely miss), yet `t3_nli` True at `nli_tau`. (RED: symbol absent.)
  2. `test_t3_disabled_returns_false` — `model=None` → False regardless of content.
  3. `test_t3_ignores_haiku_only` — sources all `haiku_summary` (filtered out by the
     caller) → the verbatim list is empty → `t3_nli` returns False. Guards invariant 3.
  4. `test_t3_no_upgrade_on_neutral` — claim is *related but not entailed*
     (neutral) → entailment < `nli_tau` → False. The Error-B guard **for the tier
     itself**; prove RED against a naive "any nonzero entailment ⇒ True".
- **Exit criterion:** all RED→GREEN; paraphrase flips True, neutral/contradiction
  stay False, disabled/empty stay False.

## Task 3 — Wire T3 into `ground()` on the UNGROUNDED fall-through ONLY

- **Goal:** Thread an optional `model` (default `None`) and `nli_tau` through
  `ground()` and `score_report()`. Insert the T3 branch **between `ground_check.py`
  lines 1196 and 1199** — after citation resolution, verbatim filter, and the
  numeric gate. Default (`model=None`) path must be **byte-identical** to today.
- **Files touched:** `scripts/ground_check.py` (`ground`, `score_report`, `main`
  signatures + `--nli` CLI opt-in flag that loads the model; default off);
  `tests/test_ground_nli.py` (new).
- **Red-first tests — the moat-critical "cannot rescue" quartet (write, run RED):**
  1. `test_nli_cannot_rescue_fabricated_citation` — claim cites `[S9]` absent from
     store, NLI enabled + entailment forced high → verdict stays
     `UNVERIFIED_CITATION`, gate never PASS. (RED against a mis-ordered wire that
     runs T3 before citation resolution.)
  2. `test_nli_cannot_rescue_bad_number` — NUMERIC claim whose number mismatches the
     source, NLI enabled → stays `UNVERIFIED_NUMBER` (T3 sits after the numeric gate).
  3. `test_nli_cannot_rescue_ungroundable` — all-`haiku_summary` cited source, NLI
     enabled → stays `UNGROUNDABLE` (never reaches T3).
  4. `test_nli_upgrades_only_ungrounded` — parametrized over every verdict: the only
     transition an enabled model can cause is `UNGROUNDED → GROUNDED`; assert all
     other verdicts identical model-on vs model-off.
  5. `test_ground_default_model_none_byte_identical` — run the full golden matrix
     (`test_golden_matrix.py` rows) with `ground(..., model=None)` and assert
     per-claim verdicts are **identical** to the pre-Task-3 baseline (capture the
     baseline from `git stash`/pre-branch run). Proves the pure default is preserved.
- **Exit criterion:** quartet + byte-identical test RED→GREEN; full existing suite
  (`uv run pytest`) still green with default-off.

## Task 4 — Report surfaces tier state + `nli`-sourced tagging

- **Goal:** `score_report` output gains a top-level
  `nli_tier: {enabled: bool, reason: str, model_revision: str | null}` block. On
  model-load failure the tier is **disabled, the gate PROCEEDS, and the report SAYS
  SO** (`enabled: false`, `reason` non-empty) — required by α3. Each `per_claim`
  entry grounded via T3 carries `grounded_via: "T3_NLI"` and `tier_sensitive: true`.
- **Files touched:** `scripts/ground_check.py` (`score_report`, YAML/JSON emit in
  `main`); `references/grounding-failure-types.md` (document the T3 path under
  GROUNDED + the disabled-notice); `tests/test_report_nli.py` (new).
- **Red-first tests:**
  1. `test_report_says_nli_disabled_on_load_failure` — `load_nli_model()` returns
     `None` → report `nli_tier.enabled == False`, `reason` non-empty, gate still
     computed and emitted (not aborted).
  2. `test_report_tags_t3_grounded_claim` — a T3-grounded claim → its `per_claim`
     entry has `grounded_via == "T3_NLI"` and `tier_sensitive == true`.
  3. `test_report_omits_nli_block_never` — the `nli_tier` block is present even when
     `model=None` (so consumers always see whether NLI ran).
- **Exit criterion:** RED→GREEN; report schema carries disabled-notice + tag;
  reference doc updated.

## Task 5 — Calibration coupling: split `tier_sensitive` into lex vs nli (#1 RISK)

- **Goal:** Extend `calibrate.py` so a two-threshold gate calibrates correctly. Add
  `nli_entail: float` to `ClaimFeatureRow`; **split** the single `tier_sensitive`
  flag into `lex_tau_sensitive` and `nli_tau_sensitive` (or a `governed_by` enum:
  `{T1_FIXED, T2_LEX, T3_NLI, NON_TIER}`). `predicted_is_violation` must re-threshold
  on the **correct score column**: a T2-decided row against `t2_f1` vs `lex_tau`; a
  T3/UNGROUNDED-decided row against `nli_entail` vs `nli_tau`. Add `sweep_nli_tau` +
  an `nli_tau` `loo_operating_point` under the **same Error-B monotonicity bound**
  (`select_operating_point` unchanged in spirit: minimize Error-A s.t. Error-B ≤
  bound). This is the `f11f8d4` bug class extended to two knobs — a sweep that
  re-thresholds the wrong column silently miscounts.
- **Files touched:** `scripts/calibrate.py` (`ClaimFeatureRow`, `emit_claim_features`,
  `predicted_is_violation`, new `sweep_nli_tau` / LOO variant);
  `tests/test_calibrate_nli.py` (new); `tests/test_calibrate_features.py`,
  `tests/test_calibrate_overfit.py` (extend for the split flag).
- **Red-first tests:**
  1. `test_lex_sweep_ignores_nli_grounded_rows` — a T3-grounded row must NOT flip
     under a `lex_tau` sweep (only under `nli_tau`). Prove RED against a naive
     implementation that re-thresholds every `tier_sensitive` row on `t2_f1`.
  2. `test_nli_sweep_ignores_t1_and_t2_rows` — a T1-verbatim row and a T2-lexical row
     are invariant to an `nli_tau` sweep.
  3. `test_nli_sweep_flips_only_nli_governed_rows` — only `governed_by == T3_NLI`
     rows change verdict across an `nli_tau` sweep.
  4. `test_error_b_monotonicity_holds_for_nli_sweep` — for the `nli_tau` operating
     point, decreasing `nli_tau` (more upgrades) never lowers Error-A at the cost of
     raising Error-B past the bound; `select_operating_point` refuses any tau whose
     Error-B exceeds the bound (reuse the existing raise-path test shape).
- **Exit criterion:** RED→GREEN; each sweep re-thresholds only its own column; the
  Error-B ≤ bound invariant is preserved for the `nli_tau` selector.

## Task 6 — CR-002: `nli_tau` Calibration Record (ADR-025)

- **Goal:** Emit `CR-002` (≤80 lines, projection-vs-actual + delta column,
  held-out LOO Error-A/B), superseding CR-001's `nli_tau: deferred` row. Projection
  = 0.8 (CR-001). **Actual is `deferred` until gold NLI labels exist** — the same
  human gate as lex_tau (Claude-labeling-Claude's-own-entailment is circular →
  candidate only). Tier ships with a **flagged provisional `nli_tau`** default;
  gold ratification is a **Sai gate** (CLAUDE.md Escalation §2). Every quoted number
  carries "(n<50, provisional, CR-002)".
- **Files touched:** `calibration/CR-002-nli-tau.md` (new); `scripts/calibrate.py`
  (`emit_cr` extended for the nli row) if the emitter is reused;
  `tests/test_calibrate_cr.py` (extend).
- **Red-first test:** `test_cr002_has_nli_tau_row_and_held_out_error_b` — emitted
  CR-002 contains an `nli_tau` projection-vs-actual row, a held-out Error-B line,
  and is ≤80 lines. (RED: emitter lacks the nli row.)
- **Exit criterion:** RED→GREEN; CR-002 conforms to ADR-025 (≤80 lines, delta column,
  LOO held-out); `nli_tau` marked provisional pending gold labels.

## Task 7 — Red-team regression harness extension (`assure-red-team`)

- **Goal:** Add a frozen NLI-enabled store + adversarial drafts to the golden matrix
  and red-team fixtures. **Every fixture asserts its expected verdict; C and D are
  proven RED against a naive over-upgrading T3.** ANY unexpected PASS = release blocker.
- **Files touched:** `tests/fixtures/nli/` (new: frozen store JSONL + drafts A–D);
  `tests/test_redteam_nli.py` (new); `tests/test_golden_matrix.py` (add T3 rows);
  `demo/` (optional: an NLI-on variant of the demo, kept default-off).
- **Red-team fixtures (required):**
  - **A — paraphrase-legit (the tier's job):** real claim paraphrased from a
    verbatim source. NLI **ON** → `GROUNDED` via T3; NLI **OFF** → `UNGROUNDED`
    (documents the Error-A the tier removes). Assert both.
  - **B — fabricated-citation-under-NLI (byte-identical FAIL):** the demo's
    fabricated `[S3]`/`[S9]` draft run with NLI **ON** → still gate `FAIL`, and the
    `UNVERIFIED_CITATION` per-claim verdict bytes are **identical** to the NLI-OFF
    run. Byte-compare against `demo/expected/fabricated-report.json` (modulo the
    additive `nli_tier` block). Proves T3 cannot touch that path.
  - **C — paraphrase-overreach (tier Error-B guard):** claim asserts MORE than the
    source entails (neutral) → entailment < `nli_tau` → stays `UNGROUNDED`. Prove RED.
  - **D — contradiction:** claim contradicts the source → contradiction class → stays
    `UNGROUNDED`, never `GROUNDED`. Prove RED.
- **Exit criterion:** all four green; B is byte-identical to the frozen fabricated
  report on the citation path; C/D proven RED-then-GREEN; harness wired into the
  `assure-red-team` skill's fixed-store run.

## Task 8 — Whole-branch Opus adversarial gate + determinism re-derivation

- **Goal:** Final gate before any merge (NOT downgradeable — CLAUDE.md model-routing
  "adversarial verification — final whole-branch" = Opus, "a miss here is terminal").
  Verify **artifacts, not reports** (Discontinuity-distrust): fresh `git status` +
  diff-stat, full `uv run pytest`, re-run the red-team harness, and **re-derive the
  `nli_tau` LOO number deterministically** before it enters CR-002.
- **Files touched:** none (review); findings feed fixes back into Tasks 1–7.
- **Checks:**
  1. `ground(..., model=None)` byte-identical to pre-branch across the golden matrix.
  2. The four "cannot rescue" invariants (Task 3) hold under adversarial drafts.
  3. The `tier_sensitive` split (Task 5) does not let a `lex_tau` sweep silently
     re-count T3 rows (the `f11f8d4` seam).
  4. No path under `ground_check.py` calls the network or a generative model; the
     NLI adapter is local, pinned, deterministic, and default-off.
  5. **Release-blocker sweep:** no adversarial draft reaches gate PASS.
- **Exit criterion:** full suite green, red-team harness green, Opus whole-branch
  review CONFIRMED-clean (or all findings fixed and re-reviewed), CR-002 numbers
  re-derived and matching. Then merge decision is Sai's.

---

## Dependency order

`Task 0 (ADR, Sai gate)` → `1` → `2` → `3` → `4` → `5` → `6 (gold-label Sai gate)` →
`7` → `8 (Opus gate, Sai merge)`. Tasks 1–5 and 7 are buildable/testable behind
the off-default before Tasks 0 and 6 clear their human gates; nothing ships as a
default until both gates are green.

## Model routing for execution (CLAUDE.md table)

- Tasks 1–4, 7 (multi-file TDD against this locked plan): **Opus-class** executor,
  **Sonnet-class** per-task review.
- Task 5 (two-knob calibration seam, the `f11f8d4` bug class): **Opus-class**
  executor AND **Opus-class** review — cross-boundary, a miss corrupts calibration.
- Task 8 (whole-branch adversarial gate): **Opus-class**, never downgraded.
