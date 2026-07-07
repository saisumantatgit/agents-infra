# Lane A Execution Report — CLAUDE.md Rewrite + 3 Skills

**Executor:** Opus 4.8. **Date:** 2026-07-08. **Branch:** `agent-assure-calibration-run`.
**Scope modified:** `CLAUDE.md`, `.claude/skills/{assure-calibrate,assure-red-team,assure-slice}/SKILL.md`. No git commands run.

## Deliverables & line counts

| File | Lines | Budget | Status |
|---|---|---|---|
| `CLAUDE.md` | 140 | 90–140 | PASS (sections: Architecture, Commands, Conventions, Key Files, Gotchas, Failure Modes, Escalation; `@SOUL.md` on line 1) |
| `.claude/skills/assure-calibrate/SKILL.md` | 113 | — | PASS |
| `.claude/skills/assure-red-team/SKILL.md` | 107 | — | PASS |
| `.claude/skills/assure-slice/SKILL.md` | 108 | — | PASS |

All 10 Failure Modes (spec §3) and 5 Escalation triggers (spec §5) present, tightened for budget. All 4 §2 additions (moat asymmetry invariant, tier_sensitive tagging, thresholds-are-data, haiku_summary-never-grounds) carried.

## Facts verified against the repo (not carried on trust)

| Claim in manual/skills | Verification | Result |
|---|---|---|
| 327 tests pass via `uv run pytest` | ran from `Agent-Assure/` | 327 passed in 3.38s ✓ |
| lex_tau=0.71, n=12, held-out Error-B=0.143, Error-A=0.2 | `CR-001` + live `uv run python -m calibration.run_calibration` | held-out error_a=0.2000 error_b=0.1429, lex_tau=0.71 ✓ |
| Branch `agent-assure-calibration-run` | `git rev-parse --abbrev-ref HEAD` | ✓ |
| Cited commits e839891, ccddf3e, 86a7f46, dcce427, f11f8d4, ff24a82 | `git log --oneline \| grep` | all 6 exist ✓ |
| Calibration runner invocation | `python calibration/run_calibration.py` fails on `scripts.calibrate` import; `-m calibration.run_calibration` works | module form is the only correct form — documented ✓ |
| `ground_check.py` CLI + `--json` report shape (`gate`, `per_claim[].verdict`) | live run on `demo/draft-fabricated.md` | gate FAIL, verdicts {GROUNDED, UNVERIFIED_CITATION, UNVERIFIED_NUMBER} ✓ |
| Red-team assertion one-liner (in assure-red-team) | executed verbatim | prints `FAIL [...]`, exit 0, assertion holds ✓ |
| `select_operating_point` rule (min Error-A s.t. Error-B≤bound; raises if none) | read `scripts/calibrate.py:563` | matches manual/skill text ✓ |
| `emit_cr` ≤80-line ceiling + `held_out.n==n_claims` hard raises | read `scripts/calibrate.py:914` | ✓ |
| `load_labels` fail-loud on bad/blank/dup label; `human_label ∈ {grounded, violation}` | read `scripts/calibrate.py:331` | ✓ |
| Red-team fixture matrix derived from real taxonomy | read `references/grounding-failure-types.md` | 7 failure verdicts mapped, no invented types ✓ |
| Paths cited in skills exist | `ls`/`find` | run_calibration.py, calibrate.py, build_corpus.py, feature_rows.jsonl, labeling.csv, CR-001, grounding-failure-types.md, demo/* , tests/test_golden_matrix.py, PHASE2-SEQUENCING.md, PHASE1B-RESUMPTION.md — all present ✓ |

## Deviations from spec (with reasons)

1. **Skill location.** Spec §6 allowed `.claude/skills/` OR `Agent-Assure/skills/`. Chose `.claude/skills/` (repo root) per the task's explicit target paths. These are dev-workflow skills for working *on* Assure, distinct from the shipped `Agent-Assure/skills/verify-grounding/` product skill — correct separation.
2. **`calibration-plan.md` is NOT cited as an existing file.** The spec (§2.3, §6.1) and the code docstrings reference `calibration-plan.md`, but it is not vendored in this repo (`find` returned nothing). Rather than send a weaker model to a dead path, the manual has an explicit Gotcha ("`calibration-plan.md` is not in the repo — CR-001 and `scripts/calibrate.py` are the live sources"), and skills point to the live code instead. Flagged loud, not silently assumed.
3. **Design-spec path softened in assure-slice.** `docs/superpowers/specs/2026-06-20-agent-assure-design.md` (named in PHASE2-SEQUENCING.md) is not present under `Agent-Assure/docs/`. Step 1 now reads it "if present" and instructs not to block on it, since PHASE2-SEQUENCING.md carries the decided scope.
4. **Error-B monotonicity encoded as two distinct constraints.** The code's in-run `_ERROR_B_BOUND=0.20` (needed for n=12 LOO fold fragility) is separate from the cross-run invariant the spec wants. assure-calibrate states both: within-run selection bound vs the cross-run rule "never accept held-out Error-B > 0.143 (the current CR-001 baseline)". This is the load-bearing distinction — conflating them would let a run pass the code's 0.20 bound while regressing the moat past 0.143.

## Side effects

- Running `uv run python -m calibration.run_calibration` during verification re-emitted `calibration/CR-001-bootstrap-lex-tau.md`. Output is deterministic; re-read confirmed byte-identical content. No net change to that file.
- Created empty scratch/report artifacts (`report.json`, `/tmp/report.json`) during the red-team dry-run; both deleted.

## Load-bearing assumption (surfaced per global rules)

The whole manual treats **held-out Error-B = 0.143 as the ratchet the moat must never loosen.** If Sai later rules that the n=12 bootstrap baseline is too noisy to serve as a hard monotonicity floor (a legitimate call at n<50), the assure-calibrate cross-run gate would need to re-anchor to the first ≥n=50 ratified run instead. The invariant's *direction* (Error-B never trades up for Error-A) is unconditional; only the numeric anchor is provisional.
