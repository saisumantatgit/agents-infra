---
name: assure-red-team
description: >
  Regression-harness the grounding moat: build adversarial drafts (fabricated
  citation, numeric drift, paraphrase over-reach, uncited claim, unsubstantiated
  absence, unsupported relation, summary-only source) against a fixed evidence
  store and assert each produces its expected FAILING verdict — never PASS. Use
  before any release or re-verification, and after ANY change to
  ground_check.py / classify / tiers / score. ANY unexpected PASS is a release
  blocker. Commands run from Agent-Assure/.
license: MIT
allowed-tools: Bash Read Write
---

# assure-red-team

The gate's value is that a fabricated `[S9]` cannot talk its way to a pass.
This skill proves that property still holds by attacking the gate with drafts
engineered to fail, and asserting the verdicts mechanically. It is the moat's
regression harness — run it every release. The gate is pure-Python and
LLM-free; so is this check. You assert on the engine's JSON, not on your reading.

## The one rule

**ANY draft in the matrix below that comes back `PASS` is a RELEASE BLOCKER.**
A false PASS is Error-B — a fabrication certified — which is unrecoverable. Stop
the release, file the regression, escalate (Escalation rule 1).

## Fixture matrix (failure-type × expected verdict)

Derived from `references/grounding-failure-types.md` — do not invent types.
Each adversarial draft targets one claim-level verdict; every one of these caps
the gate below PASS.

| # | Adversarial draft (what it does) | Expected claim verdict | Gate effect |
|---|---|---|---|
| 1 | **Fabricated citation** — cites `[S9]` whose `source_id` is not in the store | `UNVERIFIED_CITATION` | HARD cap at NEEDS_WORK; FAIL if score<60. Never PASS. |
| 2 | **Numeric drift** — real source, but the claim changes a value or unit (`25%`→`25`, `$4M`→`$8M`) | `UNVERIFIED_NUMBER` | violation |
| 3 | **Paraphrase over-reach** — claim restated so no ≥8-token span (T1) and lexical-F1 window (T2) supports it | `UNGROUNDED` | violation |
| 4 | **Uncited claim** — a factual assertion with no citation marker | `UNCITED` | violation |
| 5 | **Unsubstantiated absence** — "no X exists" backed by <2 distinct queries in `query_provenance` | `UNVERIFIED_ABSENCE` | violation |
| 6 | **Unsupported relation** — "A causes B" without 2 distinct verbatim sources, one per side | `UNVERIFIED_RELATION` | violation |
| 7 | **Summary-only source** — every cited source is `full_text_source != "verbatim"` (e.g. `haiku_summary`) or empty | `UNGROUNDABLE` | violation |

Positive control: a fully grounded draft (every claim traces to a verbatim
source) must return `GROUNDED` per claim and gate `PASS`. A harness that only
ever sees FAIL could be trivially broken; the positive control proves the gate
still *can* pass.

## Procedure

1. **Pick / freeze the store.** Use `demo/evidence-store.jsonl` (offline, frozen)
   or a purpose-built fixture store. The store must be immutable for the run —
   never edit a store to change a verdict (that is the one action the tool exists
   to make impossible).
2. **Assemble the drafts.** Reuse the shipped fixtures where they exist:
   - `demo/draft-fabricated.md` → verified FAIL (score 50, `UNVERIFIED_CITATION`
     + `UNVERIFIED_NUMBER`).
   - `demo/draft-grounded.md` → verified PASS (positive control).
   Author additional single-attack drafts under a scratch dir for matrix rows
   3–7 if not already covered by `tests/test_golden_matrix.py`.
3. **Run the gate on each draft:**
   ```bash
   # from Agent-Assure/
   uv run python scripts/ground_check.py \
       --draft <DRAFT> --store demo/evidence-store.jsonl --json > report.json
   ```
   Exit code `0` = PASS, `1` = NEEDS_WORK or FAIL.
4. **Assert on the JSON, not your reading.** The report has `gate`,
   `grounding_score`, `vacuous`, and `per_claim[]` each with
   `{index, kind, text, verdict}`. Check the targeted verdict appears and the
   gate is below PASS:
   ```bash
   uv run python -c "import json,sys; d=json.load(open('report.json')); \
     vs={c['verdict'] for c in d['per_claim']}; \
     print(d['gate'], sorted(vs)); \
     assert d['gate']!='PASS', 'RELEASE BLOCKER: adversarial draft PASSed'"
   ```
5. **Prefer the existing golden matrix.** `tests/test_golden_matrix.py` already
   pins one row per verdict path with the exact fixture that triggers it. Run
   `uv run pytest tests/test_golden_matrix.py` as the fast regression; use the
   hand drafts above for release-time end-to-end confirmation.

## Verification gates

1. Every matrix row returns its expected verdict AND gate ≠ PASS.
2. The positive-control grounded draft returns gate PASS.
3. No store was mutated during the run (grounding is against fixed evidence).
4. `uv run pytest tests/test_golden_matrix.py` is green.
5. Any deviation (unexpected PASS, or expected verdict missing) is logged and
   escalated before release — never waved through.

## Red flags → required response

| You observe | Required response |
|---|---|
| An adversarial draft returns `PASS` | RELEASE BLOCKER. Stop, file regression, escalate (rule 1). |
| Tempted to tweak the store so a verdict "looks right" | Never edit the store. The store is the fixed evidence the gate checks against. |
| Expected `UNVERIFIED_CITATION` shows as `UNCITED` | Check citation placement — a marker after the sentence-final period detaches and reads UNCITED. Fix the fixture, not the engine. |
| Matrix row has no verdict because the claim was `NON_CLAIM` | The attack hid in a header/fragment. Ensure the claim carries a verb or a number so it is scored (the anti-gaming path). |
| `vacuous: true` | The store had no scored claims — the run proves nothing. Rebuild the fixture. |

## References

- `Agent-Assure/references/grounding-failure-types.md` — the verdict taxonomy this matrix is built from.
- `Agent-Assure/demo/` — frozen store + fabricated (FAIL) and grounded (PASS) drafts + `expected/`.
- `Agent-Assure/tests/test_golden_matrix.py` — one pinned row per verdict path.
