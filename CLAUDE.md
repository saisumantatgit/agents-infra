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
   into atomic claims, classifies each, and grounds each via **T1 alone**
   (a contiguous verbatim span ≥8 tokens, OR the whole claim contained verbatim
   in a cited source and not under an attribution/denial hedge), numeric
   value+unit matching, absence 2-query and relational 2-source rules. It
   returns a gate verdict. **T2 (lexical F1) was DEMOTED 2026-09-02 (ADR-006)
   and decides nothing** — it is emitted as a diagnostic only.

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
uv sync                              # provisions runtime deps AND pytest (dev group)
uv run pytest                        # full suite — 478 passed + 2 skipped + 9 xfailed
                                     #   (2026-09-02; the count moves with every
                                     #   red-team round, so trust the RUN, not this
                                     #   number). The 9 xfails are deliberately-open
                                     #   items: OI-MOAT-20, OI-T2-01 (x2), and
                                     #   OI-MOAT-21 (x6 — one legacy + the five
                                     #   argument-swap tripwires in
                                     #   tests/red_team_moat/test_moat_oi_moat_21.py).
                                     #   Those five are the SAME open Error-B counted
                                     #   per instance, not five new holes.
                                     # (`--extra dev` is no longer needed: pytest moved to
                                     #  [dependency-groups] dev, which uv sync installs by
                                     #  default — OI-ENV-01. A conftest guard fails loud if
                                     #  pytest ever resolves outside the project .venv.)
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
- **Thresholds are data, not code — and the grounding path now has NONE.**
  **`lex_tau` is RETIRED (ADR-006 / CR-003, 2026-09-02)**; `--lex-tau` RAISES
  rather than silently no-op'ing. T2 was demoted because a true and a false
  claim can be the same one-token delta and score an identical `t2_f1` (5/5
  matched pairs), and because a bag of words has no order (a false reordering
  scored 1.000). **Current rates: Error-A=0.320 / Error-B=0.000, n=52 gold
  (CR-004)** — 'zero' means no KNOWN violation escapes; the 95% upper bound
  on 0/27 is ~10.5%, so never quote it as zero — held-out BY CONSTRUCTION, since with zero fitted parameters the
  in-sample bias LOO existed to remove does not arise. Supersedes CR-002
  (0.76, A=0.200/B=0.111); Error-B monotonicity holds. The 0.320 is real: honest
  paraphrase now reads UNGROUNDED, counted as strict xfails, recoverable only by
  T3/NLI (ADR-004), which is now LOAD-BEARING rather than optional. Score gate
  default = 90 — but per ADR-005 (accepted 2026-07-12) the score is a
  SECONDARY bar: PASS additionally requires an EMPTY retained appendix (zero
  violation-class verdicts); a ratio can never buy a PASS past a retained
  violation.
- **A fix to the moat gets red-teamed too — this is now a three-round law, not
  a maxim.** Round 1 (2026-07-12) closed four Error-B holes; round 2
  (2026-07-14) found fourteen wrongful PASSes evading those very fixes; round 3
  (2026-08-30) found seventeen more over five mechanisms, **two of them
  evasions of fixes landed hours earlier the same day**. A narrow fix closes
  the fixture it was written against and leaves the class open — every time so
  far. Ship the adversary as a permanent guard (`tests/red_team_moat/`), and
  re-run the sweep after every tier change.
- **Never key a moat rule on a surface property the author controls.** Round 3
  killed a `>= 6 content tokens` rule with a five-token fabrication; round 4
  killed its proper-noun replacement with the **Shift key** (Title Case).
  Length and capitalisation are both set by whoever writes the draft. Prefer a
  property the attacker cannot set without giving up the attack — a positional
  or grammatical signal, or the presence of the very tokens that make the claim
  a claim.
- **Every "I don't know" must point AWAY from PASS.** Round 4's four findings
  were three instances of ONE bug: an absent or unreadable field read as
  *unconstrained*. `NON_CLAIM` ("could not classify") left the denominator;
  `claim_rate=None` ("could not read a rate") imposed no constraint; an empty
  corroborator set ("subject too thin to check") reported no objection. In a
  gate whose job is to constrain, a catch-all must fail closed. **Audit every
  new `None`, empty-collection, and default branch for which way it points.**
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
- **`tier_sensitive` is now ALWAYS False** (ADR-006): no verdict consults
  `lex_tau`, so no row may enter a lexical sweep. The field is kept, not
  deleted — a sweep over an empty set is a visible no-op, whereas dropping the
  field would let a future threshold silently re-thresholds verdicts that cannot
  move and report a fabricated operating point.
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
| `Agent-Assure/calibration/labeling-v2.csv` | **Scaffold** — DERIVED (claim, evidence, **source_type**, candidate, rationale). No human column; regenerate freely |
| `Agent-Assure/calibration/labels-v2.csv` | **Labels** — AUTHORED. **RATIFIED GOLD 2026-09-02** (52 rows, Sai). No generator writes it |
| `Agent-Assure/calibration/CR-004-absence-scope.md` | **Current CR**: absence SCOPE rule, A=0.320 B=0.000 — deployed 2026-09-03 |
| `Agent-Assure/calibration/CR-003-t2-demotion.md` | T2 demoted, lex_tau RETIRED (A=0.320 B=0.074) |
| `docs/decisions/ADR-006-demote-t2.md` | Why T2 cannot be sufficient, why the coverage repair was rejected, what quote-mining costs |
| `Agent-Assure/calibration/CR-002-gold-lex-tau.md` | Superseded by CR-003 (lex_tau=0.76, A=0.200 B=0.111) |
| `Agent-Assure/calibration/CR-001-bootstrap-lex-tau.md` | Superseded by CR-002 (n=12 bootstrap; kept for the delta column) |
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
4. **Quoting error rates without their provenance.** → Every rate carries
   "(n=52, single ratifier, CR-004)". The ratifier is the project owner and the
   gold labels differ from the machine candidates on only 4/52 rows — strong,
   but NOT external ground truth. A second blind labeller is the open step.
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

**Reading of #1 used on 2026-08-30 — UNRATIFIED, Sai to confirm or reject.** The
2026-08-30 autonomous session interpreted #1 as protecting *reversibility*, not
*importance*: a **fail-closed** change (one that can only move claims AWAY from
PASS) cannot manufacture the unrecoverable error, so it was treated as inside
the agent's authority; a **PASS-enabling** change was treated as squarely #1's
and escalated. On that reading OI-MOAT-03/-05/-07 were fixed and OI-DEC-01 was
not (see `docs/decisions/RATIFICATION-REGISTER-2026-08-30.md`). The reading is
recorded here because it was ACTED ON, not because it is settled — until Sai
rules, treat #1 by its literal text and escalate either direction.
