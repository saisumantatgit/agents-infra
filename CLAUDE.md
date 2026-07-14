@SOUL.md

# Agent-Assure — Calibration Working Repo

The **calibration workspace** for Agent-Assure: a verification-first grounding
gate that certifies every factual claim in an AI draft against evidence actually
retrieved this session. Phase 1 (capture hook + deterministic gate) is complete
and live-validated; current work is Phase 2 calibration on branch
`agent-assure-calibration-run`. This file overrides the inherited suite CLAUDE.md
for `Agent-Assure/`.

## Architecture — two halves, one moat

1. **Capture (automatic).**  A `PostToolUse` hook (`hooks/hooks.json` →
   `scripts/capture_hook.py` → `capture_core.py`) fires after each retrieval tool
   (Exa fetch, `Read`, native `WebFetch`, DDG fetch) and appends a verbatim-tagged
   record to `.assure/evidence-store.jsonl` — audit evidence holding exactly what
   the model saw. Native `WebFetch` is Haiku-summarized, so it is tagged
   `haiku_summary` and the gate refuses to certify against it.
2. **Verify (deterministic gate).** `scripts/ground_check.py` decomposes a draft
   into atomic claims, classifies each, and grounds each via two lexical tiers
   (T1 verbatim ≥8-token span; T2 lexical-F1 ≥ lex_tau window with numerics
   present), numeric value+unit matching, absence 2-query and relational
   2-source rules. It returns a gate verdict.

**The moat: pure Python, deterministic, ZERO LLM calls during grounding.** A
verdict is a mechanical fact about the store — which is exactly why a fabricated
`[S9]` cannot talk its way to a pass. Nothing under `ground_check.py`'s call tree
may call a model. This is the product, not a style choice.

**Verdict taxonomy (closed — a new state requires an ADR first):**
- Gate: `PASS` / `NEEDS_WORK` / `FAIL`.
- Claim: `GROUNDED`, `ABSENCE_SUPPORTED`, `UNGROUNDED`, `UNCITED`,
  `UNVERIFIED_CITATION`, `UNVERIFIED_NUMBER`, `UNVERIFIED_ABSENCE`,
  `UNVERIFIED_RELATION`, `UNGROUNDABLE`, `NON_CLAIM`.
- Evidence `full_text_source` ∈ {`verbatim`, `haiku_summary`}: tiers run only on
  `verbatim`; a claim citing only `haiku_summary` → `UNGROUNDABLE`.

## Commands

Run from `Agent-Assure/` (env is `uv`; `install.sh` provisions runtime `.venv`).

```bash
bash install.sh                      # provision .venv (Python >=3.11 + runtime deps)
uv sync --extra dev                  # one-time: add pytest (dev deps)
uv sync --extra dev                  # REQUIRED before pytest — without it `uv run pytest`
                                     #   silently falls back to a GLOBAL pytest and reports
                                     #   ~46 bogus ModuleNotFoundErrors (OI-ENV-01)
uv run pytest                        # full suite — 376 pass + 3 xfail (open moat items) on this branch
uv run python scripts/ground_check.py \
    --draft DRAFT.md --store STORE.jsonl [--threshold 90] [--json]   # manual gate
uv run python -m calibration.run_calibration   # sweep + LOO + emit CR (module form)
```

- `ground_check.py` exit codes: `0` = PASS, `1` = NEEDS_WORK or FAIL. Without
  `--json` it writes `grounding-report.yaml` to CWD; with `--json` it prints JSON.
- Plugin command `/assure-verify path/to/draft.md` wraps `verify-grounding`
  (defaults `--store .assure/evidence-store.jsonl`).
- The calibration runner MUST run as a module (`-m calibration.run_calibration`) so
  `scripts.calibrate` resolves; `python calibration/run_calibration.py` breaks it.

## Conventions

- **Fail loud, never fallback.** Malformed JSONL, missing field, blank/unknown
  label, duplicate key → raise with the offending line/key. The store is audit
  evidence; silent repair destroys defensibility. (`e839891`, `ccddf3e`, `86a7f46`)
- **Moat-integrity is an asymmetric INVARIANT, not a preference.** Error-B (false
  negative on the violation class = a fabrication certified as PASS) is
  UNRECOVERABLE; Error-A (false alarm on a real claim) is recoverable. No change
  may reduce Error-A by raising Error-B. Positive class is pinned to VIOLATION
  (`dcce427`) — never flip it.
- **Thresholds are data, not code.** Changing one = new calibration run + new
  CR, never an inline edit. **The gate RUNS at `lex_tau = 0.65`** (the
  `t2_lexical` default); CR-001's calibrated **0.71 was never deployed** —
  deploying it moves the live operating point and is Sai's call (OI-CAL-01).
  Quote neither number as "the" threshold without saying which. Score gate
  default = 90 — but per ADR-005 (accepted 2026-07-12) the score is a
  SECONDARY bar: PASS additionally requires an EMPTY retained appendix (zero
  violation-class verdicts); a ratio can never buy a PASS past a retained
  violation.
- **A fix to the moat gets red-teamed too.** Round 1 (2026-07-12) closed four
  Error-B holes; round 2 (2026-07-14) found fourteen wrongful PASSes that
  evaded those very fixes (nine rate phrasings, a Cyrillic homoglyph, a
  quantity swap, an absence leak). Ship the adversary as a permanent guard
  (`tests/red_team_moat/`), and re-run the sweep after every tier change.
- **Regenerate the calibration corpus after ANY tier/classify change and diff
  it.** It is the fix's own adversary: it caught an entity-only absence rule
  flipping a labeled violation to supported (q22, round 1) and an
  adjective-counting coverage rule raising a false alarm on a labeled-grounded
  claim (q37, round 2) — both before commit. Byte-diff, then adjudicate every
  drifted row against its label; never tune a constant to make one row pass.
- **Held-out numbers only** (leave-one-out, per-claim); in-sample is not a result.
- **Sort every artifact into DERIVED or AUTHORED** (PIR-002). Derived (feature
  rows, scaffolds, reports, CRs): the machine remakes them identically — let it.
  Authored (human labels, ratifications): only a person can remake them, so **no
  generator may ever write them.** They live in their own file (`labels-v2.csv`,
  created once by `init_labels`) and are bound to what was judged by `claim_sha`
  — the loader fails loud on a STALE label rather than re-pointing a human's
  judgment at text they never read. Ask of any new writer: *what does this do if
  the file already holds a human's work?* If the answer is "overwrite it", that
  is not a bug yet — it is an appointment.
- **`tier_sensitive` / lex_tau-invariant tagging** (`f11f8d4`, `ff24a82`):
  verdicts not governed by lex_tau must be tagged invariant or calibration
  miscounts. Any new verdict path must declare its tag.
- **NFKC-normalize before ANY text match** at every text path's ingestion boundary.
- **`haiku_summary` can never ground a claim** — tiers must not run on it;
  claim → `UNGROUNDABLE`. Preserve on every new evidence path.
- **ADR-025 CRs are mandatory** after every calibration run: ≤80 lines, projection-vs-actual table with a delta column.
- **Assure installs alone.** Zero cross-plugin imports (no `Agent-PROVE`, etc.).

## Key Files

| Path | Purpose |
|------|---------|
| `Agent-Assure/scripts/ground_check.py` | Deterministic gate CLI — the moat |
| `Agent-Assure/scripts/capture_hook.py`, `capture_core.py` | PostToolUse capture into the store |
| `Agent-Assure/scripts/calibrate.py` | Pure calibration functions (metrics, sweep, LOO, emit_cr) |
| `Agent-Assure/calibration/run_calibration.py` | Bootstrap sweep entry (legacy `labeling.csv`, n=12, inline labels — frozen, CR-001 depends on it) |
| `Agent-Assure/calibration/labeling-v2.csv` | **Scaffold** — DERIVED (claim, evidence, candidate, rationale). No human column; regenerate freely |
| `Agent-Assure/calibration/labels-v2.csv` | **Labels** — AUTHORED. Human-owned; no generator writes it. `init_labels` creates it once, refuses to overwrite |
| `Agent-Assure/calibration/CR-001-bootstrap-lex-tau.md` | Current CR: recommends lex_tau=0.71 (n=12); gate still RUNS 0.65 — OI-CAL-01 |
| `Agent-Assure/references/grounding-failure-types.md` | Every verdict, what it catches, how to fix |
| `Agent-Assure/docs/PHASE2-SEQUENCING.md` | Phase 2 slice order (2c-harness → 2b → 2a → 2d) |
| `Agent-Assure/demo/` | Offline moat demo: fabricated `[S3]` → FAIL, frozen fixtures |

## Gotchas

- **No build step** — prompt/skill/hook based; `uv` manages the env, no compile.
- **Store is per-session.** Grounding runs against sources captured THIS session; a
  draft citing prior-session sources fails, correctly.
- **Citation placement matters.** Markers go inside the sentence before the final
  period; a marker after the period detaches and reads `UNCITED` (fail-safe).
- **`gate` / `nli_tau` are `deferred` in CR-001**, not derived: single-claim
  reports give degenerate scores, and the T3 NLI tier is Phase 2b (unbuilt).
- **`calibration-plan.md` is not in the repo** — it is named in code docstrings;
  CR-001 and `scripts/calibrate.py` are the live sources of the calibration rules.

## Failure Modes (Mistake → Rule)

1. **LLM inside the grounding path** ("just have a model check paraphrase"). →
   Nothing under `ground_check.py` may call an LLM. Paraphrase is the T3 NLI tier
   (local DeBERTa, fail-closed, Phase 2b) — and even that never *creates* a PASS.
2. **Silent fallback on malformed input** (skip a bad JSONL line, default a field).
   → Raise with the offending line/key; the store is audit evidence.
3. **Trading Error-B for Error-A** while tuning. → Minimize Error-A subject to
   Error-B ≤ the current held-out value; violations rejected regardless of F1.
4. **Quoting n=12 numbers as validated.** → Every error rate carries
   "(n=12, provisional, CR-001)" until a ≥n=50 ratified-label run supersedes it.
5. **Self-labeling calibration data.** → Claude-generated labels are `candidate`;
   only Sai-ratified labels are `gold`; calibrate on gold only.
6. **Inventing verdicts** (`PARTIAL_PASS`, …). → Taxonomy is closed; ADR first.
7. **Green tests as proof for a bug fix** without seeing them red. → INS-005: run
   the regression against pre-fix code, paste the red output in the PR/logbook.
8. **Skipping NFKC on a new text path** (new capture tool, extractor). → Normalize
   at the ingestion boundary; grep `unicodedata.normalize` parity in text PRs.
9. **Editing thresholds / feature logic without re-running calibration + CR.** →
   `calibration/` outputs go stale the moment `classify`/`tiers`/`score` change:
   change → rerun → CR.
10. **Assuming suite repos are present/coupled** (importing from Agent-PROVE). →
    Assure installs alone; zero cross-plugin imports.

## Escalation — STOP and ask Sai (do not "reasonably assume")

1. Any change that alters the Error-A/Error-B trade-off or the gate score bar.
2. Gold-label ratification or correction is needed (standing gate).
3. Two authoritative sources conflict (spec vs calibration-plan vs CR) — adjudicate
   by direct evidence trace; if still conflicting, it is Sai's spec-source call.
4. `SOUL.md`, `install.sh`, or hook registration changes (installers write into user repos).
5. Anything that would publish externally (GitHub release, marketplace listing).

Otherwise: proceed, log the decision, mark Case vs Systemic per the global rules.
