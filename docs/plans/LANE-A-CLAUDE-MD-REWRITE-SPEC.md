# Lane A Spec — CLAUDE.md Rewrite as a Weaker-Model Operating Manual

**Author:** Fable 5, 2026-07-07. **Executor:** Opus 4.8. The judgment is IN this spec; the executor's job is assembly, verification of every cited path/claim against the repo, and polish. Do not soften the rules.

**Target:** replace this repo's `CLAUDE.md` (currently the inherited agents-infra suite file) with an Assure-calibration-specific manual, 90–140 lines, five sections per ADR-style convention (Architecture, Commands, Conventions, Key Files, Gotchas) PLUS two new sections this repo needs: **Failure Modes** and **Escalation**. Keep `@SOUL.md` include.

---

## §1 Conventions to carry forward (verified present)

1. Engine is **pure Python, deterministic, zero LLM calls during grounding** — this is the moat, not a style choice.
2. **Fail loud, never fallback** — established repeatedly: report-gate tie fails loud (`e839891`), fail-loud label ingestion (`ccddf3e`), dup-key guard (`86a7f46`).
3. Fixed verdict taxonomy: gate `PASS/NEEDS_WORK/FAIL`; claims `GROUNDED/UNGROUNDED/UNGROUNDABLE`; evidence `verbatim/haiku_summary`. No new verdicts.
4. NFKC normalization before ANY text matching.
5. ADR-025 CRs mandatory after every calibration run; ≤80 lines; projection-vs-actual table.
6. Positive class pinned to VIOLATION in Error-A/Error-B computation (`dcce427`) — never flip it.
7. Held-out (leave-one-out) error rates only; in-sample numbers are not results.
8. `uv` for env; tests via `uv run pytest` from `Agent-Assure/`.

## §2 Conventions to ADD (Fable additions — gaps a weaker model falls into)

1. **Moat-integrity constraint is asymmetric:** Error-B (false PASS — fabrication certified) is UNRECOVERABLE; Error-A (false alarm) is recoverable. No change may reduce Error-A by increasing Error-B. State this as an invariant, not a preference.
2. **`tier_sensitive` / lex_tau-invariant tagging** (`f11f8d4`, `ff24a82`): verdicts not governed by lex_tau must be tagged invariant or calibration miscounts. Any new verdict path must declare its tag.
3. **Thresholds are data, not code:** lex_tau=0.71 is an n=12 calibration output. Changing it = new calibration run + new CR, never an inline edit.
4. **haiku_summary evidence can never ground a claim** — tiers must not run on it; claim → UNGROUNDABLE. Preserve on every new evidence path.

## §3 Failure Modes — named, with the preventing rule

Format in the manual: *Mistake → Rule*. These 10, verbatim or tightened:

1. **Adding an LLM judgment call inside the grounding path** ("just use a model to check paraphrase"). → Rule: nothing under `scripts/ground_check.py`'s call tree may call an LLM. Paraphrase belongs to the T3 NLI tier (local DeBERTa, fail-closed), Phase 2b, and even that never *creates* a PASS.
2. **Silent fallback on malformed input** (skip bad JSONL line, default a missing field). → Rule: raise with the offending line/key. The store is audit evidence; silent repair destroys defensibility.
3. **Trading Error-B for Error-A** during threshold tuning. → Rule: operating-point selection is constrained: minimize Error-A subject to Error-B ≤ current; violations rejected regardless of aggregate F1.
4. **Trusting n=12 numbers as validated** (writing "the gate has 14% FN rate" in docs/marketing). → Rule: every quoted error rate carries "(n=12, provisional, CR-001)" until a ≥n=50 ratified-label run supersedes it.
5. **Self-labeling calibration data** (generating gold labels and calibrating on them in one session). → Rule: labels Claude generates are `candidate`; only Sai-ratified labels are `gold`; calibration runs on gold only.
6. **Inventing verdicts** (`PARTIAL_PASS`, `MOSTLY_GROUNDED`). → Rule: taxonomy is closed; a new state requires an ADR first.
7. **Green tests as proof for a bug fix** without seeing them red. → Rule: INS-005 — run the regression test against pre-fix code, paste the red output in the PR/logbook.
8. **Skipping NFKC on a new text path** (new capture tool, new claim extractor). → Rule: normalize at ingestion boundary; grep for `unicodedata.normalize` parity in any PR touching text.
9. **Editing thresholds/feature logic without re-running calibration** and emitting a CR. → Rule: `calibration/` outputs are stale the moment `classify`/`tiers`/`score` change; CI-of-the-mind: change → rerun → CR.
10. **Assuming the suite repos are present/coupled** (importing from Agent-PROVE etc.). → Rule: Assure installs alone; zero cross-plugin imports.

## §4 Quality bar per deliverable — checkable criteria

- **Code change:** all tests pass (`uv run pytest`, paste count); new behavior has a test seen red first; no new verdicts; NFKC on new text paths; fail-loud on new error paths.
- **Calibration run:** ratified-gold labels only; held-out method stated; Error-B ≤ prior operating point; CR emitted ≤80 lines with delta column and one-line explanations for deltas >20%.
- **Governance doc:** logbook entry per session; AAR/PIR/ADR per their templates in `docs/`; CRs sibling to their TDR.
- **Demo asset:** runs offline from frozen fixtures; fabricated-citation FAIL reproduces byte-identically; no network dependency.

## §5 Escalation rules — exact

STOP and ask Sai (do not proceed, do not "reasonably assume") when:

1. Any change alters the Error-A/Error-B trade-off or the gate score bar.
2. Gold-label ratification or correction is needed (standing gate).
3. Two authoritative sources conflict (spec vs calibration-plan vs CR) — adjudicate by direct evidence trace; if still conflicting, it's Sai's spec-source call.
4. `SOUL.md`, `install.sh`, or hook registration changes (installer writes into user repos).
5. Anything would publish externally (GitHub release, marketplace listing).
Otherwise: proceed, log the decision in the logbook, mark Case vs Systemic per global rules.

## §6 The 3 skills (highest hours-saved; write as full SKILL.md files under `.claude/skills/` or `Agent-Assure/skills/`)

1. **`assure-calibrate`** — one-command calibration cycle: ingest ratified labels (fail-loud on candidate labels), rerun sweep + leave-one-out, enforce the Error-B monotonicity constraint, emit CR-00N, diff vs prior CR. Saves the most hours because every gate/tier change triggers this whole cycle and each manual run risks a discipline slip (in-sample numbers, missing CR). Include: preconditions checklist, exact commands, CR template injection, red-flag table ("in-sample looks better" → report held-out anyway).
2. **`assure-red-team`** — generate adversarial drafts against a store (fabricated citation, numeric drift, paraphrase restatement, absence-claim, stale-source) and assert gate verdicts per `references/grounding-failure-types.md`. This is the moat's regression harness; hours saved = every release re-verification. Include a fixture matrix: failure-type × expected-verdict, and the rule that ANY unexpected PASS is a release blocker.
3. **`assure-slice`** — the Phase-2 slice executor: reads `PHASE2-SEQUENCING.md`, drafts the TDD plan in the writing-plans format used for 1a/1b, runs subagent-driven-development with per-task Sonnet review + whole-branch Opus gate (per the global model-routing table). Hours saved = the orchestration overhead Sai currently pays per slice.

**Executor note:** each skill must carry frontmatter (name, description with "Use when…" trigger), a checklist, and verification gates. Test each by dry-running its checklist against the current repo before claiming done.
