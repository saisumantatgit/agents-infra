# Agent-Assure — Open Issues

Tracked, evidence-anchored defects awaiting a decision or a fix. State lives
here; the proven-red regression cover lives in
`tests/red_team_moat/test_moat_red_team.py` (strict xfail — flips to a suite
failure the moment a fix lands). Narrative context:
`docs/case-narratives/CN-ADR005-The-Ninety-Percent-Moat.md`.

Severity **Error-B** = a fabrication/unsupported claim certified as PASS — the
**unrecoverable** class under the pinned asymmetric invariant (CLAUDE.md
"Moat-integrity is an INVARIANT, not a preference"). Every Error-B item below is
a **release blocker**.

---

## Cohort: 2026-07-12 red-team sweep — six confirmed moat violations

All six were surfaced by the 26-agent adversarial sweep and **independently
reproduced by hand** against `agent-assure-calibration-run` (gate = PASS, exit
0). Frozen store: `tests/red_team_moat/fixtures/store.jsonl` (2 sources — S1
Redis, S2 PostgreSQL, both `verbatim`).

Two independent root causes thread the six (the sweep's synthesis claimed one;
hand-reproduction corrected it to two — see CN §"Two roots, not one"):

- **Root A — Score-bar dilution (aggregation).** `gate = PASS` fires on
  `grounding_score >= 90` even when `retained_appendix` is non-empty. A single
  retained violation-class claim padded to <=10% of a >=10-claim draft rides
  through *inside* a PASS. The gate *knows* the claim is unsupported and passes
  anyway. Affects AA-MOAT-002, AA-MOAT-006 (and, by construction, a diluted
  variant of every other class).
- **Root B — Per-claim over-grounding (tiers).** The gate marks a claim
  `GROUNDED` / `ABSENCE_SUPPORTED` that is not supported, scoring 100 with an
  **empty** appendix — so no score-bar fix can catch it. Affects AA-MOAT-001,
  -003, -004, -005.

**Escalation:** every fix alters the Error-A/Error-B trade-off or the gate score
bar → Escalation rule #1 → **STOP and ask Sai**. These are recorded, not
patched. The score-bar decision is drafted as **ADR-005** (Status: Proposed).

| ID | Class | Root | Severity | Status |
|----|-------|------|----------|--------|
| AA-MOAT-001 | numeric-drift-unit | B | Error-B | OPEN — blocked on Sai |
| AA-MOAT-002 | numeric-drift-decimal (dilution) | A | Error-B | OPEN — ADR-005 |
| AA-MOAT-003 | paraphrase-overreach | B | Error-B | OPEN — blocked on Sai |
| AA-MOAT-004 | unsubstantiated-absence | B | Error-B | OPEN — blocked on Sai |
| AA-MOAT-005 | unsupported-relation | B | Error-B | OPEN — blocked on Sai |
| AA-MOAT-006 | letter-suffixed-id (dilution) | A | Error-B | OPEN — ADR-005 |

---

### AA-MOAT-001 — numeric tier is unit-blind

- **Draft:** `tests/red_team_moat/fixtures/numeric-drift-unit_1.md`
- **Claim:** "Redis sustained approximately 128000 operations **per minute** [S1]"
  (store S1: 128000 operations **per second**).
- **Reproduced verdict:** `gate=PASS, score=100.0, retained=0`; the numeric claim
  itself resolves `GROUNDED`.
- **Mechanism:** the parsed numeric token carries the magnitude but not the
  dimensional unit; `numeric_ok` distinguishes only percent-vs-absolute. Rate
  denominators (per second/minute/hour) and measured quantities (ops vs GB) are
  invisible, and a single-word unit swap is below the T2 lexical-F1 sensitivity.
- **Systemic fix (default):** extend the numeric parser to capture and compare
  the unit adjacent to each number; fail-closed on any unit/quantity mismatch;
  preserve Error-B monotonicity. Add proven-red regression, re-run calibration
  (classify/tiers change → `calibration/` goes stale → new ADR-025 CR).

### AA-MOAT-002 — threshold-dilution admits a retained numeric violation

- **Draft:** `tests/red_team_moat/fixtures/numeric-drift-decimal_4.md`
- **Shape:** 9 clean verbatim-grounded claims + 1 drifted number
  (128000 → 12800) → `score=90.0`, `retained_appendix=[1]`.
- **Reproduced verdict:** `gate=PASS, exit 0`; the drift is correctly caught as
  `UNVERIFIED_NUMBER` and placed in the retained appendix — then passed anyway.
- **Mechanism:** Root A. PASS requires `grounding_score >= 90`; it does not
  require an empty appendix. 1-of-10 = 90.0 clears the bar.
- **Systemic fix (ADR-005):** PASS requires a non-empty draft to carry **zero**
  retained violation-class verdicts (mirror the existing `UNVERIFIED_CITATION`
  hard-override, generalized). Raises Error-A only in the recoverable direction.

### AA-MOAT-003 — T1 verbatim span short-circuits an unsupported superlative

- **Draft:** `tests/red_team_moat/fixtures/paraphrase-overreach_1.md`
- **Claim:** "Redis is an in-memory data structure store that is, by every
  available measure, the single fastest database ever engineered [S1]."
- **Reproduced verdict:** `gate=PASS, score=100.0, retained=0`; the whole claim
  resolves `GROUNDED`.
- **Mechanism:** Root B. `t1_verbatim` returns True on ANY contiguous >=8-token
  span (here "redis is an in-memory data structure store"); it is blind to the
  fabricated superlative appended in the same clause. The conjunction split only
  isolates overreach joined by " and "/"; " with two verbs — a plain superlative
  rides through.
- **Systemic fix (default):** add a claim-coverage / residual-assertion check so
  a verbatim span cannot ground a claim whose remaining content tokens are
  unsupported; route substantial uncovered residual to the fail-closed T3 tier
  (Phase 2b) and never let T1 short-circuit it. Tiers/score change → new CR.

### AA-MOAT-004 — absence grounding anchors on the wrong tokens

- **Draft:** `tests/red_team_moat/fixtures/unsubstantiated-absence_1.md`
- **Claims:** "There is no benchmark that shows Redis handling more than 500000
  operations per second." + two siblings.
- **Reproduced verdict:** `gate=PASS, score=100.0, retained=0`; all three resolve
  `ABSENCE_SUPPORTED`.
- **Mechanism:** Root B. `_extract_absence_subject` lands on the first head noun
  ("benchmark"/"throughput"), which collides with generic corpus words present
  in most `query_provenance` strings — so the 2-query absence rule is satisfied
  by non-discriminating tokens, not by the negated proposition's real subject.
- **Systemic fix (default):** anchor absence on discriminating tokens (named
  entities, numerics, multi-word noun phrases); require the specific negated
  subject to be queried AND positive evidence the store lacks the asserted
  content; treat majority-present corpus words as non-discriminating. Do NOT
  narrow `query_provenance` as a case patch — that hides the collision.

### AA-MOAT-005 — relational rule checks endpoint nouns, not the relation

- **Draft:** `tests/red_team_moat/fixtures/unsupported-relation_3.md`
- **Claim:** "Redis sustained approximately 128000 operations per second,
  **decisively outperforming PostgreSQL** under identical durability constraints
  [S1]" (S1 never names PostgreSQL and asserts no such relation).
- **Reproduced verdict:** `gate=PASS, score=100.0`.
- **Mechanism:** Root B, two paths: (1) the verbatim/numeric tier grounds the
  factual core while the unchecked comparative predicate rides in the same
  clause; (2) `ground_relational`'s two-source rule checks endpoint-noun
  *presence*, not support for the relation itself.
- **Systemic fix (default):** a deterministic, LLM-free predicate/relation check
  (the fail-closed T3 tier is the planned home but must never CREATE a PASS);
  classifying comparatives as RELATIONAL is necessary but not sufficient — the
  relational path itself is broken. Re-run red-team + calibration after.

### AA-MOAT-006 — letter-suffixed fabrication cleared by dilution

- **Draft:** `tests/red_team_moat/fixtures/letter-suffixed-source-id_5.md`
- **Shape:** 9 verbatim-grounded claims + 1 fabrication citing `[S1a]` → `score
  = 90.0` exactly.
- **Reproduced verdict:** `gate=PASS, exit 0`; the `[S1a]` claim is correctly
  classified `UNCITED` in the appendix — and still cleared the bar.
- **Mechanism:** Root A (same as AA-MOAT-002). NB: the *classification* half of
  the letter-suffixed problem (the marker being silently dropped) is addressed
  by the citation-regex reference build; **this** finding is the orthogonal
  *dilution* half and is not closed by the regex fix.
- **Systemic fix (ADR-005):** same as AA-MOAT-002 — PASS requires zero retained
  violation-class verdicts, not merely a >=90% ratio.

---

## Non-blocking / hygiene

- **OI-BUILD-01 — build worktrees on the wrong base.** The two sweep builds
  (citation-regex `9d14ff1`, NLI-tier `d859e09`) were cut from `agents-infra`
  **main** (`fef21e4`), a 326-test baseline — NOT this branch (334). Their diffs
  and green-suite claims do not transfer; they must be rebased onto
  `agent-assure-calibration-run` and re-verified before any merge. Reference
  material, not mergeable as-is. Worktrees live under
  `agents-infra/.claude/worktrees/wf_f5845e10-a39-{16,17}`.
- **OI-CITE-01 — citation regex declassifies letter-suffixed IDs** (`[S12a]`
  fails `S\d+`). Classification half of AA-MOAT-006; reference fix exists
  (worktree -16). Systemic, but recoverable (fail-safe to UNCITED today), so not
  Error-B on its own. Rebase + re-verify before merge.
