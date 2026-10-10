# Doc-Conformance Sweep — 2026-07-14

Audit of Agent-Assure docs against actual gate/tier behavior after the
2026-07-12 change (commit `6624e85`: ADR-005 gate hard-cap + AA-MOAT-001
numeric rate-qualifier fix + AA-MOAT-004 absence discriminating-anchor fix).
Every finding below was verified against `scripts/ground_check.py` source
lines before editing; code is authoritative where it and the sweep brief
disagreed (see "Prompt vs code" note at the end).

## Code verified (source of truth)

- Gate (`score_report`, lines 1332–1452): `FAIL` if score < 60.0 (checked
  first); `NEEDS_WORK` if score < threshold OR `retained_appendix` non-empty
  OR `has_unverified_citation`; `PASS` otherwise. Vacuous report (0 scored
  claims) → `NEEDS_WORK`, never `PASS`. Matches the task brief exactly.
- `numeric_ok` (lines 827–900): value AND unit must match; when the claim
  states a rate qualifier adjacent to the number, the matching source
  mention must carry the SAME qualifier (fail-closed); unqualified claims
  match by value+unit as before. Matches the task brief.
- `check_absence` / `_extract_absence_anchors` (lines 908–1036): strong
  anchors (capitalized tokens + numeric tokens of the negated subject) plus
  head noun required per supporting query when strong anchors exist;
  entity-free subjects fall back to head noun alone, rejected (fail-closed)
  when ≥3 distinct queries exist and the head noun is in a strict majority
  of them; `min_absence_searches` default = 2. Matches the task brief.

No disagreement found between the task brief and the code — all three
mechanisms verified as described.

## Files edited

### `README.md`

| Location | Was | Now | Verified against |
|---|---|---|---|
| Verdict Taxonomy: `ABSENCE_SUPPORTED` row | "backed by ≥2 distinct queries targeting the subject" | now states the strong-anchor + head-noun rule and the entity-free majority-word carve-out, tagged (2026-07-12 fix) | `ground_check.py:1015-1032` |
| Verdict Taxonomy: `UNVERIFIED_NUMBER` row | "value + unit both checked" | adds the rate-qualifier match requirement, tagged (2026-07-12 fix) | `ground_check.py:887-898` |
| Verdict Taxonomy: `UNVERIFIED_ABSENCE` row | "fewer than 2 distinct queries mentioning the subject" (stale — flagged by brief) | rewritten to the anchor rule + majority-word rejection, tagged (2026-07-12 fix) | `ground_check.py:1015-1032` |
| "Grounding Tiers" section, `numeric_ok()` sentence | no mention of rate qualifiers | appended one clause on the qualifier-match requirement, tagged (2026-07-12 fix) | `ground_check.py:892-896` |

Score gate table (lines 94–106) was left untouched per the brief — verified
it already matches current code (`FAIL`/`NEEDS_WORK`/`PASS` conditions,
appendix-cap language) exactly.

### `references/grounding-failure-types.md`

| Location | Was | Now | Verified against |
|---|---|---|---|
| New paragraph under `## Failing verdicts` heading | none (no gate-cap statement present for the 7 failing verdicts as a group) | added one paragraph: ADR-005 appendix-cap applies to ALL seven failing verdicts, not just `UNVERIFIED_CITATION` — any one caps the gate at `NEEDS_WORK` regardless of score | `ground_check.py:1436-1443` |
| `ABSENCE_SUPPORTED` → Meaning | "backed by ≥2 distinct queries ... that target the subject" (loose) | rewritten to the strong-anchor / head-noun rule, with the entity-free carve-out | `ground_check.py:1015-1032` |
| `UNVERIFIED_NUMBER` → Meaning/Fix | value+unit only | added the rate-qualifier clause + worked example ("per minute" vs "per second") | `ground_check.py:892-898` |
| `UNVERIFIED_ABSENCE` → Meaning/Fix/Why it matters | "fewer than 2 distinct queries mentioning the subject" | rewritten to the anchor rule, the MongoDB/Redis worked example already used elsewhere in the codebase docstring, and the majority-word rejection | `ground_check.py:978-1032` |

`GROUNDED` and `UNGROUNDED` sections checked and found accurate — unaffected
by the 2026-07-12 change (NON_CLAIM/T1/T2 classification logic did not
change). Left untouched.

### `skills/verify-grounding/SKILL.md`

| Location | Was | Now | Verified against |
|---|---|---|---|
| "Present the result" → PASS line | "(score N ≥ threshold, no fabricated citations)" | "(score N ≥ threshold, empty retained-violation appendix)" | `ground_check.py:1436-1443` |
| "Present the result" → NEEDS_WORK/FAIL line | implied only `UNVERIFIED_CITATION` caps the gate | now states ANY retained violation caps the gate at NEEDS_WORK (ADR-005, 2026-07-12) | `ground_check.py:1436-1443` |
| "Verdict → gate summary" table | pre-ADR-005 table: `PASS = score≥threshold AND zero UNVERIFIED_CITATION` | rewritten to the appendix-cap semantics, header tagged "(ADR-005 semantics, accepted 2026-07-12)" | `ground_check.py:1350-1362, 1436-1443` |

### Files checked, no changes needed

- `demo/DEMO-SCRIPT.md`, `demo/README.md` — the gate/score narration already
  describes current behavior correctly (e.g. demo/README.md's "the
  UNVERIFIED_CITATION alone would cap it at NEEDS_WORK, but FAIL is checked
  first" — still literally true post-ADR-005, since UNVERIFIED_CITATION is
  one instance of a retained violation). CR-001 numbers (lex_tau=0.71,
  Error-A=0.20, Error-B=0.143, n=12) untouched per instruction.
- `.claude/skills/assure-calibrate/SKILL.md` — no gate/absence/numeric
  behavioral claims; describes the calibration cycle, unaffected.
- `.claude/skills/assure-slice/SKILL.md` — no gate/absence/numeric
  behavioral claims.
- `.claude/skills/assure-red-team/SKILL.md` — row 1 ("HARD cap at
  NEEDS_WORK; FAIL if score<60. Never PASS") remains literally true post-
  ADR-005 (UNVERIFIED_CITATION is a retained-violation instance, so the
  described effect still holds).

## Follow-up flagged, not fixed (out of explicit scope)

`references/grounding-failure-types.md`'s `UNCITED`, `UNVERIFIED_RELATION`,
and `UNGROUNDABLE` sections still carry only "**Gate effect:** violation."
with no cross-reference to the new group-level ADR-005 note added under
`## Failing verdicts`. That note now covers them structurally (it sits above
all seven), so there is no misdescription, but for full internal consistency
each per-verdict box could echo the appendix-cap line the way
`UNVERIFIED_CITATION`'s box already does explicitly. Classified as
**Case Resolution** — the task brief scoped only
GROUNDED/UNGROUNDED/UNVERIFIED_NUMBER/UNVERIFIED_ABSENCE/ABSENCE_SUPPORTED
for per-verdict edits. Systemic fix (if wanted): add one clause to the three
untouched verdict boxes pointing at the group note, so no future reader can
miss the cap by reading only one box. Not logged to
`docs/open-issues/OPEN-ISSUES.md` per the "do not touch docs/open-issues/"
instruction — flagging here only.

`.claude/skills/assure-red-team/SKILL.md` row 5 ("Unsubstantiated absence —
'no X exists' backed by <2 distinct queries") describes the *pre-anchor-fix*
rule loosely. The row's assertion (expected verdict `UNVERIFIED_ABSENCE`,
gate effect "violation") still holds under the new anchor rule for any
draft built to trigger it, so it is not functionally wrong, only imprecise.
Left untouched — SKILL.md was in scope but this specific row's claim was not
flagged as a behavioral misdescription severe enough to override "fix
minimally."

## Prompt vs code — no disagreement found

The task brief's three behavioral summaries (gate, `check_absence`,
`numeric_ok`) were checked line-by-line against
`Agent-Assure/scripts/ground_check.py` and matched exactly. No escalation
needed.

## Unrelated pre-existing working-tree state (flagged per discontinuity-distrust) — IMPORTANT

At sweep start the working tree was NOT clean, despite the session's
git-status snapshot showing clean at conversation start. A concurrent/prior
process had already modified files this sweep never touched:

1. `scripts/ground_check.py` — `_CITATION_RE` widened to accept
   letter-suffixed markers (`[S1a]`), tagged `OI-CITE-01`, plus an untracked
   test `tests/test_letter_suffixed_citations.py`. Outside the region read
   for gate/absence/numeric verification; does not affect any claim
   documented above.
2. `docs/open-issues/OPEN-ISSUES.md` — modified (explicitly off-limits to
   this sweep, and NOT touched by it). The diff shows OI-CITE-01 marked
   fixed, and two NEW open issues dated 2026-07-14:
   - **OI-CAL-01 — lex_tau cross-artifact drift.** Per that entry, the CLI's
     `t2_lexical` default is **0.65** (what the gate actually runs), while
     CR-001's calibrated/ratified operating point is **0.71** (n=12,
     held-out) — recorded but never deployed. CLAUDE.md/memory/RESUME-HERE
     present 0.71 as authoritative, but per this open issue the live gate
     is NOT running at 0.71. **This bears directly on doc-conformance**: the
     lex_tau=0.71 figure this sweep was told to leave untouched in
     demo/DEMO-SCRIPT.md's honesty beat is the CR-001 *calibrated* value, not
     necessarily the *deployed* value — the open issue records that
     discrepancy as pending Sai's ruling (deploy 0.71 now vs. hold for
     CR-002 at n=52). This sweep did not re-open or re-litigate it (out of
     scope, and `docs/open-issues/` is explicitly off-limits) — surfacing it
     here because a doc-conformance sweep is exactly the process that should
     have hit this seam.
   - **OI-NUM-02** — a minor tokenization quirk (trailing space on numeric
     tokens), unrelated to this sweep's scope.
3. `docs/plans/ADR-004-DECISION-PACKAGE.md` — untracked file, unrelated to
   Agent-Assure or this sweep.

None of this was created by this sweep. Flagging per the discontinuity-
distrust rule: the repo had concurrent/prior in-flight work when this task
started, git status was stale, and OI-CAL-01 specifically means any reader
relying on "lex_tau = 0.71" as the LIVE operating threshold (not just the
calibrated one) should confirm against `docs/open-issues/OPEN-ISSUES.md`
before trusting it operationally. Recommend whoever owns that thread
reconciles or commits it separately; this sweep leaves it untouched.
