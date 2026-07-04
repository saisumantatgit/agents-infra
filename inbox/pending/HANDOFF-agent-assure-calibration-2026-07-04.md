# Handoff: Agent-Assure Phase 2a Calibration — Bootstrap Complete, Next-Phase Plan

**Date:** 2026-07-04
**From:** Claude Sonnet 5 session (Config Management HQ — Agent-Assure calibration run)
**To:** Next Claude session working directly in `agents-infra` / `Agent-Assure`
**Repo:** `~/vibe-coding/Agents/agents-infra/Agent-Assure/` (main) + `~/vibe-coding/Agents/agent-assure-calibration/Agent-Assure/` (worktree, branch `agent-assure-calibration-run`, commit `86a7f46`, NOT pushed, no PR)
**Priority:** Medium-high — the calibration harness is proven and shippable now (Step 0), but the bigger decisions (Steps 1-3) shape real moat-integrity behavior and should not be defaulted into.

---

## Origin / Why This Handoff Exists

This work was done from a Config Management HQ session (governance/design repo), not a session with `agents-infra` open. HQ's job here is done — this file is the transfer point. **Everything below should be independently verified against the actual repo state before you build on it — don't take any claim on faith.** Where I say "confirmed by running X," re-run X yourself if you have any doubt. This is a briefing, not a source of truth.

## 1. What Agent-Assure Is (30 seconds)

Verification-first deep-research plugin (siblings: PROVE, Cite, Trace, Scribe, Drift, Litmus). Two halves: (a) a `PostToolUse` capture hook that writes an EvidenceStore (JSONL of `RetrievedSource` records) as tool calls happen in a live session; (b) a deterministic, no-LLM grounding gate (`ground_check.py`) that decomposes a draft into claims, classifies each (FACTUAL/NUMERIC/ABSENCE/ATTRIBUTION/RELATIONAL/NON_CLAIM), and grounds each against the EvidenceStore. Report-level gate: PASS/NEEDS_WORK/FAIL.

## 2. Current State — Verified 2026-07-04

- **Main branch:** `a41160c` — Phase 1 (capture hook + gate + packaging) and Phase 2a (calibration harness) merged. 326 tests green.
- **This session's work:** worktree `agent-assure-calibration`, branch `agent-assure-calibration-run`, commit `86a7f46`. 327 tests green (326 + 1 new). **Not pushed, no PR.**

Files this commit adds/touches (all under `Agent-Assure/`):

| File | What |
|---|---|
| `calibration/build_corpus.py` | Builds + labels a 12-claim synthetic bootstrap corpus spanning every violation class |
| `calibration/run_calibration.py` | Runs sweep → select_operating_point → loo_operating_point → emit_cr |
| `calibration/feature_rows.jsonl` | Per-claim raw features (t1_verbatim, t2_f1, numeric_ok, predicted_verdict, tier_sensitive) |
| `calibration/labeling.csv` | The 12 claims + hand-labels (grounded/violation) |
| `calibration/CR-001-bootstrap-lex-tau.md` | Emitted Calibration Record (ADR-025 format, 21/80 lines) |
| `scripts/calibrate.py` | + duplicate-`claim_id` guard in `load_labels` (was silently overwriting a label) |
| `tests/test_calibrate_features.py` | + proven-red regression for the guard above |

**Result: `lex_tau=0.71`** (up from provisional 0.65), derived on genuinely held-out (leave-one-out) error rates: Error-A (recoverable false alarm) = 0.20; Error-B (unrecoverable missed violation) = 0.143. `gate` and `nli_tau` are marked **deferred** in CR-001, not derived (see §4 — this is deliberate, not an oversight).

Verify before trusting any of the above:

```bash
cd ~/vibe-coding/Agents/agent-assure-calibration/Agent-Assure
uv sync --extra dev   # venv may not exist in this worktree — recreate if missing
PYTHONPATH=. .venv/bin/python3 -m pytest -q                    # expect 327 passed
PYTHONPATH=. .venv/bin/python3 calibration/run_calibration.py   # re-derives CR-001; diff before trusting
```

## 3. Two Load-Bearing Findings From This Run

### Finding A — `ground_relational` has a real over-association weakness

`ground_relational`'s two-distinct-source rule (spec §4.8) marks a RELATIONAL/causal claim GROUNDED if side_A is supported in one verbatim source AND side_B is supported in a *different* verbatim source — but never checks that any source asserts the *relationship* the claim makes. Concretely: "Increased marketing spend drives higher customer signups" was marked GROUNDED off a source confirming spend rose and a separate source confirming signups rose — neither ever says spend *caused* the signups. Confirmed independently by 3/3 blind-judge subagents with zero access to the mechanical verdict (full evidence trail: HQ `docs/insights/insights-log.md` INS-019). This is real Error-B ground truth in CR-001, not a labeling mistake — kept, not relabeled away.

**Needs a design decision, not a quiet code change.** Options to research (none designed yet):
- Require the causal connective phrase (or a close paraphrase of it) to appear in a supporting window of at least one cited source, in addition to the two-side check.
- Require both sides supported in the *same* source (stricter — may increase false negatives on legitimately-relational single-source claims that currently fail purely via the `<2 distinct sources` short-circuit).
- Whether Phase 2b's NLI/T3 tier, once built, should subsume this check entirely rather than `ground_relational` staying a separate rule.

### Finding B — n=12 is a bootstrap, not a calibrated corpus, and a bigger open methodology question

calibration-plan.md's own target is "a few hundred" labeled claims (§3). At n=12 (7 violations), leave-one-out folds are fragile: an `error_b_bound` of 0.15 (from the in-sample floor of 1/7 ≈ 0.143) succeeded in-sample but made `loo_operating_point` *raise* — a fold holding out a different violation-truth claim shrinks that fold's violation denominator to 6, and the one fixed miss (Finding A) then costs 1/6 ≈ 0.167 there. Widened to 0.20, confirmed empirically by running it, not by hand-derivation (full mechanism: HQ INS-020). **`lex_tau=0.71` is directional, not production-ready.**

**Bigger, genuinely unresolved question — surface to Sai, don't quietly work around it:** this entire 12-claim bootstrap corpus was hand-authored by the same AI whose gate it calibrates — wording was tuned against the live `t2_lexical_score` scorer until each example hit its intended verdict. That's fine for proving the harness works end-to-end (it does), but it's a real epistemic weakness for anything beyond that: a synthetic corpus authored with foreknowledge of the exact mechanism risks being systematically different from real usage. **Before scaling this corpus, decide: does the next ~200 claims come from more hand-authored synthetic examples, or from real EvidenceStores + real drafts pulled from actual Agent-Assure sessions** (calibration-plan.md §3's own language — "run the pipeline on ~20 bootstrap queries" — reads as assuming the latter). Not decided this session.

## 4. Why `gate` and `nli_tau` Are Deferred, Not Derived

- **`gate`** (report-level threshold, replaces the provisional 0.90): `derive_report_gate` needs reports with a genuine spread of `grounding_score` values (multiple claims per report, percentages other than exactly 0/100) to find a real separation point. This corpus's 12 reports each carry exactly one claim — every grounding_score is degenerate (0.0 or 100.0). Deriving a gate from that would produce a number with zero real interpretive content. **Needs:** multi-claim draft "reports" (several claims per draft, like real Agent-Assure output) + a human's *holistic* per-report trustworthy/not judgment (not per-claim) for each.
- **`nli_tau`:** Phase 2b (the NLI/T3 tier) isn't implemented in `ground_check.py` yet — confirmed by grep, no `nli_tau` reference exists anywhere in the module. Nothing to calibrate until that tier is built.

## 5. Recommended Execution Plan (sequenced, with rationale)

The sequence itself is a judgment call — confirm with Sai before committing to it, especially Step 0.

- [ ] **Step 0 (~5 min) — Ship the harness as a checkpoint.** Push `agent-assure-calibration-run` and open a PR against main for commit `86a7f46` as-is. The harness + bootstrap CR is a real, tested deliverable independent of everything below — don't let it sit unshipped while the bigger decisions get made. State plainly in the PR description that `lex_tau=0.71` is a bootstrap result, not a recommendation to change the production default yet (link CR-001).
- [ ] **Step 1 (design decision, needs Sai + research) — Resolve Finding A before scaling more RELATIONAL examples.** If the corpus scales with `ground_relational` unchanged, every future RELATIONAL example inherits the same over-association blind spot and you'll keep re-discovering Finding A instead of moving past it. Research the three options in §3, propose one (this is architecturally significant enough to warrant a short design pass, not just a code diff), get sign-off, implement with regression tests, *then* calibrate it.
- [ ] **Step 2 (methodology decision, needs Sai, blocks real scaling) — Resolve the synthetic-vs-real corpus question** (§3 Finding B, second paragraph). This determines *how* Step 3 happens, not just how much.
- [ ] **Step 3 (~200+ claims) — Scale the corpus per Step 2's answer, with multi-claim reports this time.** This kills two birds: real per-claim scaling, and finally makes the report-gate derivation in §4 possible in the same pass (genuine multi-claim reports give a real grounding_score spread). Re-run the full sweep → LOO → CR pipeline. Expect a *different* `lex_tau` than 0.71 — n=12 was too small to trust the exact value, only its direction (higher than 0.65).
- [ ] **Step 4 (after 1-3) — Phase 2b (NLI/T3 tier).** Sequenced last deliberately: building a third grounding tier before the first two tiers' calibration process is mature multiplies the same open questions (synthetic vs. real corpus, small-n LOO fragility) across a third dimension. Reversing this is a legitimate call, but should be made knowingly.

## 6. What Not To Do

- Don't treat `lex_tau=0.71` as ready to replace the shipped `0.65` default without a larger corpus (§3 Finding B).
- Don't "fix" Finding A quietly inline without a design pass and sign-off — it changes what RELATIONAL grounding means, a real behavior change to a moat-integrity mechanism, not a bug fix.
- Don't derive a report `gate` value from single-claim reports just to fill in CR-001's "deferred" row — it would look like real calibration and isn't (§4).
- Don't skip re-verifying the claims in this document against the actual repo before building on them — this document is frozen at 2026-07-04; the repo isn't.

## 7. Source Material

- This commit: `agent-assure-calibration` worktree, branch `agent-assure-calibration-run`, commit `86a7f46`.
- Calibration methodology: HQ `docs/research/agent-assure-design-inputs/calibration-plan.md` — read before touching lex_tau/nli_tau/gate again.
- Full findings write-up: HQ `docs/insights/insights-log.md` — INS-019 (relational over-association), INS-020 (small-n LOO fragility).
- Full session narrative: HQ `docs/logbook/2026-07-04-session-2.md`.
- Model-routing context (why this was run on Sonnet 5, and the verification-tiering revision that followed from it): HQ `docs/research/sonnet-5-vs-opus-4-8-model-routing-2026-07-03.md`.
- HQ memory pointer: `project_agent_assure.md` (Claude's memory store, not a repo file) — will go stale the moment this handoff is actioned; update it once progress is made.

---

**Acceptance:** this handoff is actioned when a Claude session in `agents-infra` has read this file, independently verified §2's claims against the repo, and either started Step 0 or explicitly chosen a different sequence with Sai.
