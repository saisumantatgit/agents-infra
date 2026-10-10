# Phase-2b T3 NLI Tier — Reference Implementation Build Report

**Worktree:** `/Users/saisumanthbattepati/vibe-coding/Agents/agents-infra/.claude/worktrees/wf_f5845e10-a39-17` (subdir `Agent-Assure/`)
**Branch:** `worktree-wf_f5845e10-a39-17` (isolated) — **NOT merged**
**Date:** 2026-07-11
**Suite:** 340 passed (326 baseline + 14 new). Full run: `340 passed in 5.86s`.

---

## What was built (STEPS 1–5)

A DEFAULT-OFF, fail-closed, local-classifier T3 NLI entailment tier. `model=None`
(the shipping default) is byte-identical to the pre-T3 moat — `ground_check.py`
imports no torch/transformers/nli_tier and makes ZERO model calls on the default
path. The scorer is INJECTED via a structural `EntailmentScorer`
(`score(premise, hypothesis) -> float`), so the wiring is unit-tested with a
deterministic stub and no weights are downloaded (weights are not downloadable in
this sandbox — that IS the fail-closed condition under test).

### Files

| File | Change |
|------|--------|
| `scripts/nli_tier.py` (new, 201 L) | `load_nli_model()` (fail-closed → `None` on ANY failure, never raises, local-files-only), `NliModel.score` (CPU/`eval()`/`no_grad()`, NFKC, entailment-index resolved from `label2id`), `entailment_score` seam, `describe()` disabled-notice, `EntailmentScorer` Protocol. No generative call anywhere. |
| `scripts/ground_check.py` (+213/−33) | `t3_nli(claim, sources, nli, nli_tau)` predicate (verbatim-only, NFKC, citation-stripped hypothesis, ±2-sentence windows via new `_sentence_windows`); `_ground_traced` returns `(verdict, grounded_via)`; `ground`/`score_report` gain `nli=None, nli_tau=0.8` and delegate; T3 branch inserted STRICTLY on the UNGROUNDED fall-through (after citation resolution + verbatim filter + numeric gate); per_claim gets `grounded_via/tier_sensitive` ONLY for T3-upgraded claims. `EntailmentScorer` Protocol + `NLI_TAU_DEFAULT` constant (provisional, CR-002 pending). |
| `tests/test_ground_nli.py` (new) | The 4 required moat-critical integration tests (a–d). |
| `tests/test_nli_tier.py` (new) | 10 unit tests: fail-closed load, `describe`, `entailment_score` seam, `t3_nli` (disabled/empty/threshold/below-threshold/NFKC+citation-strip). |
| `docs/adr/ADR-004-local-classifier-moat-boundary.md` (new) | **Status: Proposed** (Sai-gated). Encodes the 3 mechanical guarantees. CLAUDE.md / header NOT amended — that is the Escalation §1/§4 Sai gate. |

## Moat boundary — what I did NOT do (escalation-respecting)

- **Did NOT amend CLAUDE.md or the `ground_check.py` "ZERO LLM" header.** That is
  a moat-boundary change (Escalation §1/§4) → ADR-004 written as **Proposed**, not
  Accepted. Because the tier ships DEFAULT-OFF and `ground_check` imports no model,
  the shipping default still makes zero model calls, so the header statement
  remains literally true today.
- **Did NOT implement Task 5 (calibration `tier_sensitive` split) or Task 6
  (CR-002).** `calibration/` is ABSENT in this worktree; `nli_tau=0.8` is carried
  as a provisional constant flagged "CR-002 pending" and is inert (default-off).
- **`nli_tau` is provisional, not validated** — gold-label ratification is a Sai
  gate (Escalation §2).

## Red-first evidence

### Stage 1 — symbols absent (all new tests RED)
`uv run pytest tests/test_ground_nli.py tests/test_nli_tier.py` before implementing:
```
ImportError: cannot import name 't3_nli' from 'scripts.ground_check'
1 error in 0.31s
```

### Stage 2 — moat-critical tests catch a real Error-B (INS-005 rigor)
Tests (b) and (d) are named for the "cannot rescue" property, so I proved they
FAIL against a deliberately MIS-ORDERED wire (T3 run against all store verbatim
sources BEFORE citation resolution and the numeric gate) — not merely at symbol
absence. Pre-fix (mis-ordered) output:
```
FAILED test_nli_cannot_rescue_fabricated_citation_byte_identical
  {'gate': 'FAIL'} != {'gate': 'PASS'}
  verdict 'UNVERIFIED_CITATION' != 'GROUNDED'      # fabricated [S9] reached gate PASS
FAILED test_nli_never_alters_numeric_or_citation_verdicts
  assert <Verdict.GROUNDED> == <Verdict.UNVERIFIED_NUMBER>   # 500 vs source 200 rescued
2 failed, 2 passed in 0.39s
```
The mis-order made a fabricated citation reach gate **PASS** (the unrecoverable
Error-B) and a numeric mismatch reach GROUNDED — precisely what (b)/(d) guard.
Reverting the mis-order to the correct fall-through order → GREEN.

### Post-implementation (correct wire)
```
tests/test_ground_nli.py tests/test_nli_tier.py .............. 14 passed
uv run pytest -q  →  340 passed in 5.86s
```

## The 4 required tests (a–d)

- **(a)** `test_nli_flips_paraphrase_ungrounded_to_grounded_tier_sensitive` — a
  paraphrase where `t1_verbatim` AND `t2_lexical` are asserted False first; tier
  OFF → UNGROUNDED, tier ON → GROUNDED; per_claim tagged
  `grounded_via="T3_NLI", tier_sensitive=True`.
- **(b)** `test_nli_cannot_rescue_fabricated_citation_byte_identical` — `[S9]`
  absent from store; `score_report(nli=None) == score_report(nli=stub(1.0))`
  byte-identical; verdict `UNVERIFIED_CITATION`; gate ≠ PASS; no `grounded_via`.
- **(c)** `test_model_load_failure_disables_tier_output_equals_off` —
  `load_nli_model("/nonexistent")` → `None` (no raise);
  `score_report(nli=None) == score_report(nli=failed)`; `describe(failed).enabled
  is False` with non-empty reason.
- **(d)** `test_nli_never_alters_numeric_or_citation_verdicts` — numeric mismatch
  → `UNVERIFIED_NUMBER`, fabricated citation → `UNVERIFIED_CITATION`, haiku-only
  → `UNGROUNDABLE`, all unchanged tier on/off; control asserts the ONE allowed
  transition (UNGROUNDED→GROUNDED) is live (guards against a dead no-op tier).

## Verification of moat invariants

- `grep -E "import torch|transformers|nli_tier" scripts/ground_check.py` → only a
  docstring mention; NO import. Scorer is injected.
- NFKC applied at every new text boundary (`t3_nli` premise+hypothesis;
  `NliModel.score`; `_resolve_entail_index`).
- Verdict taxonomy unchanged (closed); T3's only effect is UNGROUNDED→GROUNDED.
- haiku_summary never reaches T3 (caller passes verbatim-only; `t3_nli` empty-list
  guard; test_nli_tier covers it).
- 326 pre-existing tests (written against pre-T3 behavior) still pass unchanged →
  default-off byte-identity proof.

## For the Opus whole-branch gate (open items, deferred by design)

1. ADR-004 ratification + CLAUDE.md/header amendment wording (Sai gate).
2. Task 4 richer `nli_tier` report block (trades byte-identity for observability)
   — surfaced via `describe()` at the caller layer only; not added to
   `score_report` output to preserve strict default byte-identity. Design call
   for Opus/Sai.
3. Task 5 calibration `tier_sensitive` split + Task 6 CR-002 — blocked on absent
   `calibration/` dir and gold `nli_tau` labels.
4. `--nli` CLI opt-in flag in `main()` not added (out of STEPS scope; would load
   the model and record the disabled-notice).

**Do NOT merge** — reference implementation for review.


---

## Unified diff — scripts/ground_check.py (load-bearing seam)

```diff
diff --git a/Agent-Assure/scripts/ground_check.py b/Agent-Assure/scripts/ground_check.py
index 7443935..2726be2 100644
--- a/Agent-Assure/scripts/ground_check.py
+++ b/Agent-Assure/scripts/ground_check.py
@@ -12,7 +12,7 @@ import unicodedata
 from collections import Counter
 from dataclasses import dataclass
 from enum import Enum
-from typing import Iterator
+from typing import Iterator, Protocol
 
 
 # ---------------------------------------------------------------------------
@@ -1142,7 +1142,160 @@ def _session_queries(store: dict[str, RetrievedSource]) -> list[str]:
     return out
 
 
-def ground(claim: Claim, store: dict[str, RetrievedSource]) -> Verdict:
+# ---------------------------------------------------------------------------
+# T3 — NLI entailment tier (Phase 2b, DEFAULT-OFF; ADR-004 Proposed)
+# ---------------------------------------------------------------------------
+#
+# ground_check.py itself imports NO model and NO torch: the scorer is INJECTED
+# by the caller as a structural EntailmentScorer. With the shipping default
+# (nli=None) this whole path is inert, so ground_check still makes ZERO model
+# calls — the "ZERO LLM" moat statement holds unchanged for the default. The
+# opt-in scorer is a LOCAL, deterministic, non-generative classifier whose ONLY
+# permitted effect is flipping UNGROUNDED -> GROUNDED under nli_tau (see
+# scripts/nli_tier.py and ADR-004).
+
+# Provisional nli_tau. CR-001 projected 0.8 with status `deferred` (T3 unbuilt).
+# This is NOT a validated threshold: it stays provisional until a >=n=50
+# gold-labelled calibration run emits CR-002 (a Sai gate). Quote it only as
+# "(provisional, CR-002 pending)".
+NLI_TAU_DEFAULT: float = 0.8
+
+# Tag applied to a per_claim entry when the NLI tier caused the grounding.
+_GROUNDED_VIA_NLI: str = "T3_NLI"
+
+
+class EntailmentScorer(Protocol):
+    """Structural contract for the injected NLI scorer.
+
+    Any object exposing ``score(premise, hypothesis) -> float in [0, 1]``
+    qualifies. Defined here (not imported from nli_tier) so ground_check has no
+    dependency on the optional torch/transformers extra — Assure installs alone.
+    """
+
+    def score(self, premise: str, hypothesis: str) -> float:  # pragma: no cover
+        ...
+
+
+def _sentence_windows(text: str) -> list[str]:
+    """Return every ±2-sentence window of *text* (T2 windowing granularity).
+
+    Mirrors _best_window_score's window construction so the NLI premise
+    granularity matches the lexical tier. Pure function.
+    """
+    sentences = _split_sentences(text)
+    n = len(sentences)
+    windows: list[str] = []
+    for c in range(n):
+        lo = max(0, c - 2)
+        hi = min(n, c + 3)
+        windows.append(" ".join(sentences[lo:hi]))
+    return windows
+
+
+def t3_nli(
+    claim: Claim,
+    sources: list[RetrievedSource],
+    nli: EntailmentScorer | None,
+    nli_tau: float = NLI_TAU_DEFAULT,
+) -> bool:
+    """Return True iff the injected NLI classifier entails *claim* from some
+    ±2-sentence window of some source at score >= *nli_tau*.
+
+    Direction (load-bearing): premise = source window, hypothesis = the
+    citation-stripped claim text (the source entails the claim). Both strings are
+    NFKC-normalized at this ingestion boundary before scoring.
+
+    FAIL-CLOSED: returns False when *nli* is None (tier disabled) or *sources* is
+    empty — so the caller's default (no model) is inert. The caller MUST pass
+    verbatim-only sources (haiku_summary can never ground) — identical contract
+    to t1_verbatim / t2_lexical; this predicate does not re-filter.
+
+    This is the ONLY NLI-influenced predicate and its ONLY downstream effect is
+    UNGROUNDED -> GROUNDED. It classifies; it never generates; it can never
+    create a PASS on any other verdict.
+
+    Pure function w.r.t. its inputs — no mutation, no network, no random, no
+    wall-clock. (The injected scorer is contractually deterministic; see
+    nli_tier.NliModel.)
+    """
+    if nli is None or not sources:
+        return False
+
+    hypothesis = _nfkc(_strip_citations(claim.text))
+
+    for source in sources:
+        for window in _sentence_windows(source.text):
+            premise = _nfkc(window)
+            if nli.score(premise, hypothesis) >= nli_tau:
+                return True
+
+    return False
+
+
+def _ground_traced(
+    claim: Claim,
+    store: dict[str, RetrievedSource],
+    nli: EntailmentScorer | None = None,
+    nli_tau: float = NLI_TAU_DEFAULT,
+) -> tuple[Verdict, str | None]:
+    """Return (verdict, grounded_via) for a single classified claim.
+
+    ``grounded_via`` is ``"T3_NLI"`` iff the NLI tier upgraded an otherwise
+    UNGROUNDED claim to GROUNDED, else ``None``. ``ground`` and ``score_report``
+    are thin wrappers over this so the T3 seam lives in exactly one place.
+
+    The dispatch order below is IDENTICAL to the pre-T3 logic; the T3 branch is
+    inserted STRICTLY on the UNGROUNDED fall-through — after citation resolution,
+    the verbatim filter, and the numeric gate — so it structurally cannot rescue
+    UNVERIFIED_CITATION, UNVERIFIED_NUMBER, UNGROUNDABLE, or UNCITED. When
+    ``nli is None`` this function is byte-identical in effect to the pre-T3
+    ``ground``.
+
+    Pure function — no mutation, no LLM (the scorer is injected), no network,
+    no random, no wall-clock.
+    """
+    if claim.kind == ClaimKind.NON_CLAIM:
+        return Verdict.GROUNDED, None
+    if claim.kind == ClaimKind.RELATIONAL:
+        return ground_relational(claim, store), None
+    if claim.kind == ClaimKind.ABSENCE:
+        return check_absence(claim, _session_queries(store)), None
+
+    if not claim.citations:
+        return Verdict.UNCITED, None
+
+    sources = [resolve(c, store) for c in claim.citations]
+    if any(s is None for s in sources):
+        return Verdict.UNVERIFIED_CITATION, None
+    if any(not s.text for s in sources):
+        return Verdict.UNGROUNDABLE, None
+
+    verbatim = [s for s in sources if s.full_text_source == "verbatim"]
+    if not verbatim:
+        return Verdict.UNGROUNDABLE, None
+
+    if claim.kind == ClaimKind.NUMERIC and not numeric_ok(claim, verbatim):
+        return Verdict.UNVERIFIED_NUMBER, None
+
+    if t1_verbatim(claim, verbatim) or t2_lexical(claim, verbatim):
+        return Verdict.GROUNDED, None
+
+    # T3 NLI fall-through — the ONLY NLI-influenced branch. Reached only after
+    # every fabrication/numeric/UNGROUNDABLE short-circuit above. Default
+    # (nli is None) leaves this inert and the verdict UNGROUNDED, byte-identical
+    # to the pre-T3 gate.
+    if nli is not None and t3_nli(claim, verbatim, nli, nli_tau):
+        return Verdict.GROUNDED, _GROUNDED_VIA_NLI
+
+    return Verdict.UNGROUNDED, None
+
+
+def ground(
+    claim: Claim,
+    store: dict[str, RetrievedSource],
+    nli: EntailmentScorer | None = None,
+    nli_tau: float = NLI_TAU_DEFAULT,
+) -> Verdict:
     """Return the grounding Verdict for a single ALREADY-CLASSIFIED claim.
 
     Implements spec §4.4 decision logic in exact order. The input `claim` is
@@ -1162,41 +1315,24 @@ def ground(claim: Claim, store: dict[str, RetrievedSource]) -> Verdict:
       7. no verbatim source among cited → UNGROUNDABLE (all haiku_summary).
       8. NUMERIC and numeric_ok(verbatim) is False → UNVERIFIED_NUMBER.
       9. T1 or T2 supports on verbatim → GROUNDED.
+     9.5. (opt-in, DEFAULT-OFF) T3 NLI entails on verbatim → GROUNDED. Reached
+          ONLY on the UNGROUNDED fall-through; inert when nli is None.
      10. otherwise                     → UNGROUNDED.
 
     ATTRIBUTION and FACTUAL fall through to the citation/verbatim/tier path
     (the default). Tiers (t1_verbatim, t2_lexical) and numeric_ok run ONLY on
     the verbatim-filtered sources.
 
-    Pure function — no mutation, no LLM/network/random/wall-clock.
-    """
-    if claim.kind == ClaimKind.NON_CLAIM:
-        return Verdict.GROUNDED
-    if claim.kind == ClaimKind.RELATIONAL:
-        return ground_relational(claim, store)
-    if claim.kind == ClaimKind.ABSENCE:
-        return check_absence(claim, _session_queries(store))
-
-    if not claim.citations:
-        return Verdict.UNCITED
-
-    sources = [resolve(c, store) for c in claim.citations]
-    if any(s is None for s in sources):
-        return Verdict.UNVERIFIED_CITATION
-    if any(not s.text for s in sources):
-        return Verdict.UNGROUNDABLE
+    *nli* is an optional injected EntailmentScorer (DEFAULT None). With the
+    default, this function is byte-identical to the pre-T3 gate and makes ZERO
+    model calls. When provided, the ONLY behavioural change it can cause is
+    upgrading a single UNGROUNDED claim to GROUNDED (see _ground_traced / t3_nli).
 
-    verbatim = [s for s in sources if s.full_text_source == "verbatim"]
-    if not verbatim:
-        return Verdict.UNGROUNDABLE
-
-    if claim.kind == ClaimKind.NUMERIC and not numeric_ok(claim, verbatim):
-        return Verdict.UNVERIFIED_NUMBER
-
-    if t1_verbatim(claim, verbatim) or t2_lexical(claim, verbatim):
-        return Verdict.GROUNDED
-
-    return Verdict.UNGROUNDED
+    Pure function — no mutation, no network/random/wall-clock; makes no model
+    call on the default path (the scorer, if any, is injected by the caller).
+    """
+    verdict, _ = _ground_traced(claim, store, nli=nli, nli_tau=nli_tau)
+    return verdict
 
 
 # ---------------------------------------------------------------------------
@@ -1217,6 +1353,8 @@ def score_report(
     claims: list[Claim],
     store: dict[str, RetrievedSource],
     threshold: float = 90.0,
+    nli: EntailmentScorer | None = None,
+    nli_tau: float = NLI_TAU_DEFAULT,
 ) -> dict:
     """Compute the grounding SCORE, gate, and retained-violation appendix (spec §4.5).
 
@@ -1273,13 +1411,22 @@ def score_report(
     has_unverified_citation = False
 
     for claim in claims:
-        verdict = ground(claim, store)
-        per_claim.append({
+        verdict, grounded_via = _ground_traced(
+            claim, store, nli=nli, nli_tau=nli_tau
+        )
+        entry: dict = {
             "index": claim.index,
             "text": claim.text,
             "kind": claim.kind.value,
             "verdict": verdict.value,
-        })
+        }
+        # Tag ONLY the NLI-upgraded claims. When nli is None grounded_via is
+        # always None, so these keys never appear and every per_claim entry stays
+        # BYTE-IDENTICAL to the pre-T3 report — the default-off moat guarantee.
+        if grounded_via == _GROUNDED_VIA_NLI:
+            entry["grounded_via"] = _GROUNDED_VIA_NLI
+            entry["tier_sensitive"] = True
+        per_claim.append(entry)
 
         if verdict == Verdict.UNVERIFIED_CITATION:
             has_unverified_citation = True
```

New files (added whole, see commit d859e09): scripts/nli_tier.py, tests/test_ground_nli.py, tests/test_nli_tier.py, docs/adr/ADR-004-local-classifier-moat-boundary.md
