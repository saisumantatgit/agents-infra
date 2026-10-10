# Threshold Staleness Map — one-pass update after CR-002 ratification

**Purpose.** The moment Sai ratifies the n=52 gold labels and `assure-calibrate` emits
**CR-002** (superseding CR-001), every *provisional-threshold* mention must be updated in a
single sweep. This map is that sweep's checklist: it separates the lines that MUST change,
the lines that MUST NOT be touched, and the far larger set of hits that only *look* stale.

**Read-only artifact.** Nothing was edited to produce this. It is a locator, not a patch.

**Scope of the grep.** Entire worktree (code, docs, READMEs, docstrings, plans, jsonl),
excluding `.venv/` and `.git/`. Tokens searched: `0.71`, `lex_tau`, `provisional`, `n=12`,
`n=13`, `n≈12`, `Error-B`, `0.143`, `0.14`, `score gate`, `threshold 90`, `--threshold 90`.
(`n=13` → 0 hits.)

---

## Load-bearing assumption (probe this first)

The staleness of a **numeric literal** (`0.71`, `0.143`) is *conditional on CR-002 actually
moving the value.* The n=52 run may reproduce lex_tau≈0.71 and Error-B≤0.143 — in which case
the *digits* stay but the **qualifiers still change** (`provisional`→ratified, `n=12`→`n=52`,
`CR-001`→`CR-002`). So there are two independent update classes:

- **Qualifier updates — ALWAYS required** regardless of the new numbers: `provisional`,
  `n=12`/`n≈12`, `CR-001`-as-current.
- **Value updates — required only if CR-002 moves the number**: the `0.71` operating point and
  the `0.143` held-out Error-B rate.

If you sweep the literals but forget the qualifiers (or vice-versa), the update is half-done.

---

## Guardrail: digit collisions — DO NOT blind find/replace

Three distinct meanings share digits. A naive `s/0.143/…/` or `s/0.71/…/` will **corrupt
tau-invariant fixtures** and silently break tests. Always read the line's meaning first.

| Digits | Meaning A (STALE — a threshold/rate) | Meaning B (NOT stale — a fixture measurement) |
|--------|--------------------------------------|-----------------------------------------------|
| `0.71` | lex_tau **operating point** (CR-001 output) | fixture text's measured **T2 F1** (`0.714`, `0.7142857142857143`) — a property of the corpus string, invariant to tau |
| `0.143` / `0.14285714285714285` | held-out **Error-B rate** (1 fabrication / 7 violations) | a fixture claim's **t2_f1 = 1/7** in `feature_rows*.jsonl` — coincidentally identical digits, unrelated to Error-B |
| `0.65` | *projection baseline* / **runtime default** (see code seam) | test **sweep values** `(0.0, 0.5, 0.65, 0.9, 1.0)` exercising the function across tau |

---

## Replacement-token legend

| Stale token | Replace with (after CR-002) |
|-------------|-----------------------------|
| `0.71` (lex_tau operating point) | `<CR-002 lex_tau>` — re-derived; may stay 0.71 or move |
| `0.143` / `0.14` / `0.14285714285714285` (Error-B **rate**) | `<CR-002 held-out Error-B>` |
| `n=12` / `n≈12` | `n=52` (per `RATIFICATION-BRIEF-v2.md`: 52 claims / 52 queries) |
| `provisional` (thresholds) | `ratified (CR-002)` — or drop the hedge |
| `CR-001` referenced as *current* CR | `CR-002` (CR-001 becomes historical/superseded) |
| Error-B monotonicity **floor** `0.143` | **Sai decision**: keep 0.143 or re-anchor to first ≥n=50 run (RESUME-HERE #3) |

---

## Section A — CANONICAL sources (DEFINE the value; handled by supersession, not sweep)

These originate the numbers. Per ADR-025/ADR-023, CR-001 is **superseded by a new file
(CR-002), never edited in place** — so its literals stay as frozen history.

| file:line | current text | why | action after CR-002 |
|-----------|--------------|-----|---------------------|
| `Agent-Assure/calibration/CR-001-bootstrap-lex-tau.md:7` | `\| lex_tau \| 0.65 \| 0.71 \| +9.2% \|` | **Canonical define** of the operating point | Frozen. CR-002 is a new file; do not edit CR-001. |
| `…CR-001…:15` | `Error-B … 0.14285714285714285` | Canonical define of held-out Error-B | Frozen (historical). |
| `…CR-001…:20` | `n≈12 queries is calibration, not proof — provisional…` | Canonical hedge | Frozen (historical). |
| `Agent-Assure/scripts/calibrate.py` (45 hits) | metric/sweep/`emit_cr` machinery; `_PROJECTION` comment `lex_tau=0.65` | **Canonical mechanism** — *computes* the value, does not hardcode 0.71 | NOT stale. Only re-run; no literal to edit. |
| `Agent-Assure/calibration/run_calibration.py:73` | `_PROJECTION = {"lex_tau": 0.65, "gate": 0.90, "nli_tau": 0.80}` | The *projected* (pre-calibration) baseline — historical input column | NOT stale — the projection is a permanent record of what was projected. |

### A′ — CODE SEAM (live discrepancy, needs a CODE decision — not a doc edit)

| file:line | current text | why it matters | action |
|-----------|--------------|----------------|--------|
| `Agent-Assure/scripts/ground_check.py:651` | `lex_tau: float = 0.65,` | **The runtime default was NEVER wired to the CR-001 output (0.71).** "Thresholds are data, not code," yet the shipped default is the *pre-calibration* 0.65, and no JSON/YAML/TOML stores 0.71. | CR-002 must decide: wire the calibrated value into the default (or a config the gate reads) — else the gate runs at an un-calibrated tau. Surface to Sai; this is the load-bearing seam. |

---

## Section B — DOWNSTREAM quotes in LIVE docs (STALE — sweep these)

These merely quote CR-001 and are the operative surface Sai/agents read today. **Update all.**

| file:line | current text (trimmed) | stale token(s) | replacement |
|-----------|------------------------|----------------|-------------|
| `CLAUDE.md:69` | ``lex_tau = 0.71` is an n=12 calibration output` | 0.71, n=12 | `<CR-002 lex_tau>`, n=52 |
| `CLAUDE.md:90` | `Current CR: lex_tau=0.71, n=12` | 0.71, n=12, CR-001-as-current | `<CR-002 lex_tau>`, n=52, point row at CR-002 |
| `CLAUDE.md:116-117` | `Quoting n=12 numbers…"(n=12, provisional, CR-001)"` | n=12, provisional, CR-001 | n=52, ratified, CR-002 |
| `RESUME-HERE.md:20` | `lex_tau=0.71, held-out Error-B=0.143 (n=12, provisional)` | 0.71, 0.143, n=12, provisional | all four |
| `RESUME-HERE.md:31` | `Error-B monotonicity floor: keep 0.143 (n=12)…` | 0.143 (floor), n=12 | Sai floor decision; n=52 |
| `Agent-Assure/demo/DEMO-SCRIPT.md:132` | ``lex_tau`) is calibrated at 0.71, from a` | 0.71 | `<CR-002 lex_tau>` |
| `…DEMO-SCRIPT.md:133` | `bootstrap run of n=12 claims across 12 queries` | n=12 (×2) | n=52 / 52 queries |
| `…DEMO-SCRIPT.md:135` | `rate … is 0.143. This is provisional,` | 0.143 (rate), provisional | `<CR-002 Error-B>`, ratified |
| `…DEMO-SCRIPT.md:136` | `n=12 is a calibration run, not a production guarantee` | n=12 | n=52 (revisit the "not proof" framing at n=52) |
| `docs/plans/DEMO-READINESS-PLAN.md:29` | `calibrated at n=12, held-out Error-B=0.14, provisional` | n=12, 0.14 (rate), provisional | n=52, `<CR-002 Error-B>`, ratified |
| `docs/plans/ALPHA-READINESS-PLAN.md:15` | `confirm lex_tau=0.71, Error-B=0.143, n=12` | 0.71, 0.143, n=12 | all three |
| `…ALPHA-READINESS-PLAN.md:34` | `Error-B ≤ 0.143 (current), then minimize Error-A` | 0.143 (moat bound) | new bound = CR-002 held-out Error-B (Sai floor call) |
| `…ALPHA-READINESS-PLAN.md:70` | `keep thresholds provisional, proceed to α3/α4` | provisional | ratified once CR-002 lands (this row is the *ship-flagged* fallback) |
| `docs/plans/HANDOFF-MASTER-PLAN.md:29` | `lex_tau=0.71 (projected 0.65…), Error-B=0.143, n=12 claims` | 0.71, 0.143, n=12 | all three (keep "projected 0.65" as history) |
| `…HANDOFF-MASTER-PLAN.md:36` | `provisional until Sai ratifies… n=12 must widen to n≥50` | provisional, n=12 | ratified, n=52 (condition met) |
| `docs/plans/LANE-A-CLAUDE-MD-REWRITE-SPEC.md:24` | `lex_tau=0.71 is an n=12 calibration output` | 0.71, n=12 | `<CR-002 lex_tau>`, n=52 |
| `…LANE-A-CLAUDE-MD-REWRITE-SPEC.md:34` | `"(n=12, provisional, CR-001)" until a ≥n=50 …run supersedes` | n=12, provisional, CR-001 | n=52, ratified, CR-002 |
| `docs/plans/LANE-B-PORTFOLIO-AUDIT.md:41` | `Phase 2a (lex_tau=0.71, CR-001…)` | 0.71, CR-001-as-current | `<CR-002 lex_tau>`, CR-002 |

### B′ — META lines (self-satisfying; the sweep *executes* these, no rewrite needed)

| file:line | current text | note |
|-----------|--------------|------|
| `RESUME-HERE.md:36` | `Labels ratified → … CR-002 → update stale "provisional" citations repo-wide.` | This is the instruction this map operationalizes. |
| `docs/plans/ALPHA-READINESS-PLAN.md:36` | `replace "provisional" language with "(n=NN, CR-002)"… Grep for 0.71, provisional, n=12, n≈12` | The prior grep spec; this map extends it. |

---

## Section C — FROZEN HISTORY (do NOT edit — dated evidence of the CR-001 run)

Execution reports and logbook entries are timestamped records of what happened at CR-001 time.
Retroactively editing them destroys the audit trail (Global Rule: reports are evidence). They
correctly say `0.71`/`n=12`/`provisional` **as of their date**. Leave untouched.

| file:line | current text (trimmed) | why frozen |
|-----------|------------------------|-----------|
| `docs/plans/reports/LANE-A-EXECUTION-REPORT.md:22` | `lex_tau=0.71, n=12, held-out Error-B=0.143…` | Dated CR-001 execution evidence |
| `…LANE-A-EXECUTION-REPORT.md:39` | `_ERROR_B_BOUND=0.20 … regressing the moat past 0.143` | Historical design note (0.20 in-run bound ≠ 0.143 cross-run floor) |
| `…LANE-A-EXECUTION-REPORT.md:48` | `held-out Error-B = 0.143 as the ratchet…` | Historical rationale |
| `docs/plans/reports/DEMO-EXECUTION-REPORT.md:105` | `lex_tau=0.71 … Error-B=0.14285… n=12, provisional` | Dated demo-run evidence |
| `docs/logbook/2026-07-08-parallel-execution.md:24` | `manual pins monotonicity floor at 0.143 (n=12)` | Logbook = append-only history |

---

## Section D — NOT STALE (tau-invariant: identifiers, fixtures, sweeps, deferred thresholds)

The bulk of the 276 hits. None of these track the CR-001 *operating point*; changing lex_tau
does not change any of them. Do not sweep.

**D1 — `lex_tau` / `Error-B` as identifiers & concept-names.** `lex_tau` is a function
parameter and dict key; `Error-B` is the name of the moat invariant. The name persists across
every recalibration. Bulk: `scripts/calibrate.py` (~44 identifier hits), `test_calibrate_metrics.py`
(70), `test_calibrate_features.py` (25), `test_calibrate_integration.py` (11), `test_tiers.py`,
`test_t2_score.py`, `test_golden_matrix.py`, `ground_check.py`, `build_corpus_v2.py`,
`inbox/…ask_ratify…:32`, `ALPHA1-EXECUTION-REPORT.md:34`. **207 of 276 hits are in `.py`** — overwhelmingly this class.

**D2 — Fixture F1 measurements (`0.714`, `0.7142857142857143`, `0.14285714285714285` as t2_f1).**
Properties of corpus strings, invariant to tau. Digit-collide with the threshold/rate — see
Guardrail. Examples: `test_golden_matrix.py:16,116,291,293`; `feature_rows.jsonl:6,9`;
`feature_rows-v2.jsonl:39`; `build_corpus.py:282,286`.

**D3 — Parameter-sweep constants (`0.0, 0.5, 0.65, 0.70, 0.90, 0.99, 1.0`).** Test inputs that
exercise the grounding function across the tau range; not the calibrated point. Examples:
`test_calibrate_metrics.py:136,155,167,222,251,290,304,336`; `test_calibrate_features.py:323,327,344`;
`test_calibrate_cr.py:46,51,55,181,204`; `test_tiers.py:160`; `test_t2_score.py:100,151,155`;
`test_calibrate_integration.py:221`; `test_calibrate_overfit.py:92`.

**D4 — Projected/pre-calibration baseline `0.65`.** The "projected" column and shipped-v1 default
recorded in CR-001; permanent history. `run_calibration.py:73`, `calibrate.py:913`,
`PHASE2-SEQUENCING.md:23`, `PHASE1A-FINAL-REVIEW.md:133`. (Exception: `ground_check.py:651` — the
*runtime* default — is Section A′, a live seam, not mere history.)

**D5 — Score gate `90` / `--threshold 90` / provisional `0.90` gate.** A **separate deferred
threshold** (CR-001 lists `gate`/`nli_tau` as `deferred`, not derived). Unless CR-002's scope
explicitly includes the score gate, these are NOT touched by a lex_tau recalibration. If CR-002
*does* calibrate the gate, they move as their own class. Hits: `CLAUDE.md:48`, `README.md:5,38`,
`test_score.py:340`, `calibrate.py:746`, `test_calibrate_gate.py:4`, `PHASE2-SEQUENCING.md:23,31,33,57,70`.

**D6 — `n≈18` fixture in `test_calibrate_cr.py:85`.** A hard-coded CR-template test input, not the
real corpus size. Invariant.

---

## Summary

- **276** unique matching lines across the worktree (excl. `.venv/`, `.git/`): **207** in `.py`
  code/tests, **66** in `.md` docs, **3** in `.jsonl` fixtures.
- **~40** lines are genuinely value-bearing; the other **~236** are tau-invariant
  identifiers, fixtures, sweep constants, or the deferred score-gate class (Section D).
- **Actionable sweep (Section B): 18 live-doc lines** to update after CR-002 — all **downstream
  quotes** of CR-001, spanning CLAUDE.md, RESUME-HERE.md, DEMO-SCRIPT.md, and 5 plan docs.
- **Canonical (Section A): 4 sources** DEFINE the values (CR-001 + calibrate.py machinery +
  run_calibration projection + ground_check runtime default). CR-001 is superseded by a *new*
  CR-002 file, not edited.
- **1 code seam (A′):** `ground_check.py:651` runtime default is `0.65`, never wired to the
  calibrated 0.71 — a live discrepancy CR-002 must resolve. **Escalate to Sai.**
- **5 frozen-history lines (Section C)** must NOT be edited (reports + logbook = dated evidence).
- **Guardrail:** `0.143`/`0.71`/`0.65` each collide with tau-invariant fixture digits — read
  meaning before any replace; never blind-sweep.
