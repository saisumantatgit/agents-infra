---
name: assure-calibrate
description: >
  Run one full Agent-Assure calibration cycle — ingest ratified gold labels,
  sweep lex_tau, select the moat-integrity operating point, leave-one-out
  validate, and emit the ADR-025 Calibration Record. Use when a threshold
  (lex_tau, score gate) needs (re)calibrating, or after ANY change to
  classify/tiers/score logic makes the current calibration/ outputs stale.
  Enforces the Error-B monotonicity invariant and the gold-vs-candidate label
  rule. All commands run from the Agent-Assure/ directory.
license: MIT
allowed-tools: Bash Read Edit
---

# assure-calibrate

One command, one cycle, one CR. This skill wraps
`calibration/run_calibration.py` with the discipline a manual run tends to
slip: it refuses candidate labels, reports held-out (never in-sample) numbers,
and blocks any operating point that raises the unrecoverable error. Grounding
itself is pure-Python and LLM-free — so is this. You run the harness and read
its output; you never hand-derive a threshold.

## The one invariant this skill exists to protect

**Error-B (false negative on the violation class = a fabrication certified as
PASS) is UNRECOVERABLE. Error-A (a real claim flagged) is recoverable.** The
operating point is chosen by `select_operating_point`: among taus whose
`error_b <= error_b_bound`, take the LOWEST `error_a`, ties toward the higher
(stricter) tau. F1/accuracy maximization is forbidden — it weights the two
errors equally, which is exactly the asymmetry the gate exists to deny.

**Cross-run monotonicity:** the new run's held-out Error-B must NOT exceed the
prior CR's. The current ratified baseline is **Error-B = 0.143** (0.14285…),
Error-A = 0.2, lex_tau = 0.71, n = 12 (CR-001). Any new operating point with
held-out Error-B > 0.143 is a moat regression — STOP and escalate (it alters
the Error-A/Error-B trade-off; Escalation rule 1). Never accept it to buy a
lower Error-A.

## Preconditions (checklist — all must hold before you run)

1. **Labels are gold, not candidate.** Claude-generated labels are `candidate`
   and MUST NOT be calibrated on. Only Sai-ratified labels are `gold`. If the
   labels in `calibration/labeling.csv` are unratified, STOP and ask Sai
   (Escalation rule 2) — do not self-ratify.
2. **`calibration/labeling.csv` exists and every row is labeled.** `human_label`
   must be exactly `grounded` or `violation` (NFKC-normalized). `load_labels`
   fails loud on a blank/unknown label or a duplicate `claim_id` — that is the
   intended behavior; fix the CSV, never suppress the raise.
3. **Feature rows are current.** `calibration/feature_rows.jsonl` must reflect
   the current engine. If `classify`/`tiers`/`score` changed, regenerate it via
   `calibration/build_corpus.py` before calibrating — stale features calibrate a
   gate that no longer exists.
4. **Tests are green.** `uv run pytest` passes (327 on branch
   `agent-assure-calibration-run`).
5. **You know the prior baseline.** Read the latest `calibration/CR-00N-*.md`
   and record its held-out Error-B (currently CR-001 → 0.143).

## Procedure

```bash
# from Agent-Assure/
uv run pytest                              # gate: must pass first
uv run python -m calibration.run_calibration   # MODULE form — resolves scripts.calibrate
```

The runner prints: label counts, the collapsed sweep (breakpoints where
error_a/error_b change), the in-sample operating point, and the leave-one-out
modal tau with held-out confusion (tp/fp/tn/fn). It then calls `emit_cr`, which
writes the CR only if the rendered content is ≤80 lines and `held_out.n` equals
`n_claims` — both are hard raises, not warnings.

- `python calibration/run_calibration.py` (script form) BREAKS: `sys.path[0]`
  becomes `calibration/`, so `from scripts.calibrate import …` fails. Always use
  `-m calibration.run_calibration`.
- To calibrate a NEW corpus/CR, add a sibling runner (or parameterize paths) and
  point `_CR_PATH` at `calibration/CR-00N-<slug>.md`; never overwrite a prior CR.

## Verification gates (all must pass to claim the run valid)

1. **Held-out, not in-sample.** The Error-A/Error-B you report and write to the
   CR are the leave-one-out numbers (`loo_operating_point`), never the in-sample
   ones. In-sample is diagnostic only.
2. **Error-B monotonicity.** New held-out Error-B ≤ prior CR's (≤ 0.143 now). If
   greater → STOP, escalate, do not commit the CR.
3. **CR shape (ADR-025).** ≤80 lines, projection-vs-actual table with a delta
   column, one-line explanation for any delta >20%. `emit_cr` enforces the line
   ceiling; you enforce the explanations.
4. **Provisional labeling honored.** The CR states n and split method and marks
   n<50 runs provisional. Every error rate quoted anywhere else carries
   "(n=NN, provisional, CR-00N)".
5. **Diff vs prior CR.** Read the prior CR and state what moved (tau, Error-A,
   Error-B) and why in the logbook. A silent threshold move is not allowed.

## Red flags → required response

| You observe / are tempted to | Required response |
|---|---|
| "In-sample error looks better than held-out" | Report the HELD-OUT number anyway. In-sample is not a result. |
| No tau meets the Error-B bound (`select_operating_point` raises) | Do NOT lower the bound to force a pick. The raise is correct — a gate that cannot hit the bound is not shippable. Escalate. |
| New held-out Error-B > 0.143 | Moat regression. STOP, escalate (rule 1). Never trade it for lower Error-A. |
| Labels are ones Claude generated this session | They are `candidate`. STOP; ask Sai to ratify (rule 2). |
| Tempted to hand-edit lex_tau in code | Thresholds are data, not code. Rerun this cycle and emit a CR; never inline-edit. |
| `load_labels` raised on a bad/blank/dup row | Fix the CSV. Never wrap the call to swallow the raise — silent repair corrupts every derived threshold. |
| CR would exceed 80 lines | `emit_cr` raises and writes nothing. Trim narrative to CN/INS; keep the CR a skeleton. |

## References

- `Agent-Assure/scripts/calibrate.py` — `select_operating_point`,
  `loo_operating_point`, `error_rates`, `emit_cr` (live source of the rules).
- `Agent-Assure/calibration/run_calibration.py` — the bootstrap runner.
- `Agent-Assure/calibration/CR-001-bootstrap-lex-tau.md` — current baseline.
- CLAUDE.md → Conventions, Failure Modes, Escalation.
