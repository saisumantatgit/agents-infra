# Logbook — 2026-07-12 — Moat remediation: ADR-005 accepted, 4 of 6 Error-B holes closed

**Branch:** `agent-assure-calibration-run` · **Suite:** 351 passed + 2 xfailed (was 334 + 6 xfailed) · **Follows:** `2026-07-12-moat-red-team-sweep.md`

## What

Sai adjudicated the red-team cohort (AskUserQuestion, this session): **ADR-005
accepted as proposed** (PASS requires empty retained appendix; ≥90 stays as a
secondary bar; no soft-gate flag); **greenlit** the numeric unit-blindness and
absence-anchoring fixes; **deferred** AA-MOAT-003 (T1 overreach) and
AA-MOAT-005 (relational predicate). Label-ratification timing left unanswered —
inbox P1 unchanged. All three fixes implemented in the main loop (moat-critical
math — not delegated), per-change design checked against every existing test
before writing.

## Done (evidence)

1. **ADR-005 in `score_report`:** `retained_appendix` non-empty → NEEDS_WORK
   (generalizes the UNVERIFIED_CITATION override). Closes AA-MOAT-002/-006.
2. **Numeric rate qualifiers** (`_rate_qualifier`, `_extract_numeric_mentions`,
   qualifier-aware `numeric_ok`): claim stating "per minute" no longer grounds
   against "per second"; qualifier-less claims bit-identical to old behavior.
   One seam found mid-flight: the numeric regexes' `\s?` swallows the boundary
   space — without the prepended-space fix the qualifier silently read None on
   BOTH sides and AA-MOAT-001 didn't flip. Closes AA-MOAT-001.
3. **Absence discriminating anchors** (`_extract_absence_anchors`, rewritten
   `check_absence`): supporting queries must contain ALL strong anchors
   (entities + numerics) AND the subject head noun; entity-free claims fall
   back to head noun with a >50% majority filter at ≥3 distinct queries.
   Closes AA-MOAT-004.
4. **Error-B monotonicity incident (important):** the FIRST absence draft
   (entities-only, no head-noun requirement) flipped corpus case q22 — a
   labeled violation — to ABSENCE_SUPPORTED. Caught by regenerating corpus-v2
   and diffing feature rows BEFORE commit; fixed via the head-noun
   requirement; pinned by `test_entity_mention_without_subject_not_support`.
   The corpus acted as the fix's own adversary.
5. **Harness protocol honored:** 4 xfails flipped XPASS(strict) → converted to
   permanent green guards (`test_fixed_fabrication_stays_blocked`); 2 remain
   strict-xfail with the deferral reason. Red-first evidence = the recorded
   xfail state on `51b3d02` flipping this session.
6. **New coverage:** +6 numeric qualifier tests, +7 absence anchor tests,
   +1 threshold-consulted test; 2 legacy tests updated to ADR-005 semantics
   (annotated in-place with the ADR reference).
7. **Calibration impact verified, not assumed:** corpus-v2 regeneration is
   byte-identical post-fix (labeling-v2.csv untouched → ratification brief
   remains valid; lex_tau feature inputs unchanged → CR-001 stands). The gate
   bar itself was `deferred` in CR-001 and will calibrate under ADR-005
   semantics at CR-002 (gold labels).
8. **Docs synced:** ADR-005 → Accepted + Amendments entry (ADR-023 form);
   OPEN-ISSUES table + closure evidence + residuals; README gate table;
   CLAUDE.md (test count, thresholds convention); CN epilogue; RESUME-HERE.

## Structural property (state it because it's checkable)

All three fixes are one-directional by construction: ADR-005 only removes
PASSes; qualifier-less numerics are unchanged; the new absence rule matches a
strict subset of the old rule's queries. A violation cannot move toward PASS.

## Open / blocked

- AA-MOAT-003, AA-MOAT-005 — OPEN by Sai's ruling (xfail tripwires live).
  α5 sign-off blocked until closed or explicitly accepted.
- α2/CR-002 — still blocked on gold-label ratification (inbox P1, unchanged).
- OI-CITE-01 (regex widening), OI-BUILD-01 (rebase reference builds), absence
  stemming + numeric quantity-noun residuals — recorded in OPEN-ISSUES.

**Reflection:** The fix for a hole found by an adversary needed an adversary of
its own — and got one for free from 52 rows of labeled corpus. The q22 catch is
the Error-B monotonicity invariant doing real work: not as a sentence in
CLAUDE.md but as a diff that refused to stay clean. Deterministic regeneration
turned "did my fix leak?" from a judgment call into a byte comparison; that is
the same move the gate itself makes against drafts, applied one level up.

**Next action:** Sai — ratify labels (inbox P1) and rule on AA-MOAT-003/-005
timing. Then: `assure-calibrate` → CR-002.
