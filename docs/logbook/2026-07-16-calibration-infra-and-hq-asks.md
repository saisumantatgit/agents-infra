# Logbook — 2026-07-16 — Calibration-infra incidents closed, two HQ asks filed

**Branch:** `agent-assure-calibration-run` · **Suite:** 387 passed + 3 xfailed · **Follows:** `2026-07-14-red-team-round-2.md`
**Span:** continuation of the 2026-07-14 autonomous session through 07-16 (governance + infra + HQ correspondence).

## What

Closed the two calibration-infrastructure issues the red-team session surfaced,
wrote the incident record for the label near-miss, and filed two asks to
Config-Management-HQ. No moat-logic changes beyond what was already ratified;
the open moat holes (AA-MOAT-003/-005/-007) remain Sai's, untouched.

## Done (all committed + pushed)

1. **OI-CAL-02 — label-clobber guard** (`f675ec3`, extended in prior commits).
   `assert_labels_not_clobbered`: no writer may overwrite a labeling CSV carrying
   human labels. Red-first. `--features-only` added so the standing drift-check
   discipline never fights the guard.
2. **PIR-002 + CN-PIR002** (`f675ec3`). The near-miss record: a routine
   `build_corpus` blanked the n=12 bootstrap labels; the fail-loud loader caught
   it in ~90s; restored from git. Named the blind spot — the project reasons about
   asymmetry in *verdicts* (Error-A/B) but had never applied it to *artifacts*
   (derived/regenerable vs authored/irreproducible).
3. **OI-CAL-03 — separation** (`a8043ea`). Sai directed the systemic fix.
   `labeling-v2.csv` → derived scaffold (no human column); `labels-v2.csv` →
   human-owned, written once by `init_labels`. `load_gold_labels` joins them and
   fails loud on non-gold, bad/blank, duplicate, orphan, unlabeled, **and STALE**
   (a `claim_sha` bound each label to the exact text judged — a hole that had
   existed the whole life of the project, surfaced only by the separation).
   Migration verified: 52→52, zero labels/text altered, every sha validates.
4. **Demo honesty-beat correction** (`5d9490a`). The beat quoted CR-001's
   *recommended* lex_tau (0.71) as if deployed; the gate runs 0.65 (OI-CAL-01).
   In a grounding product, an inaccurate honesty beat is the sin the product
   exists to prevent — corrected to state both values and which is live.
5. **Two HQ asks** (in HQ repo `ee38931`, `7d51657`; outbox copies `4201047`,
   `f947f7a`):
   - **Open Issue Register standard** — proposes adopting `OI-{AREA}-{NN}` into
     the stack as the pre-decision inbox that *feeds* ADR/PIR (2 of 9 entries
     already graduated), and collapsing the two ID series (`OI-*` + `AA-MOAT-*`)
     into one type with severity as a **field**, not a namespace. Recorded my own
     counter-argument (a file register rots; bind INVARIANT entries to an xfail test).
   - **Candidate-lines register** — 7 strong lines + narrative/structural ones from
     the moat sessions, with provenance, for Sai to allocate. Explicitly "surface,
     do not file" per his instruction.

## Decisions (mine, on merit)

- The 3 round-2 fixes COMPLETE Sai's 07-12 rulings (dimensional unit; discriminating
  anchors) → in scope. AA-MOAT-007 (verbless NON_CLAIM smuggle) is a NEW claim-definition
  decision → recorded, escalated, xfail tripwire set.
- Open-issue taxonomy: ONE type, not two. Severity is an attribute → a field, not a
  second namespace. (Recommendation to HQ; the collapse is theirs to ratify.)
- Artifact classification (DERIVED vs AUTHORED) elevated to a CLAUDE.md convention —
  the generalizable root-cause lesson from PIR-002.

## Open / blocked (unchanged — all Sai)

Ratify labels (inbox P1 — the one bottleneck) · AA-MOAT-007 · AA-MOAT-003/-005 ·
OI-CAL-01 · ADR-004/Phase-2b · OI-ENV-01. Two HQ asks await HQ.

## Governance artifacts this session

PIR-002, CN-PIR002, ADR-005 (Accepted + amendment), CN-ADR005 (Round Two + epilogue),
OPEN-ISSUES (OI-CITE-01/CAL-01/02/03, ENV-01, DEC-01, NUM-02 + AA-MOAT cohort),
insights ×5 across the arc, 2 HQ inbox items.

**Reflection:** Two incidents this session had the same shape one level apart. The
gate certifies claims against evidence; the corpus builder should have certified its
own writes against the human judgment already in the file — and didn't, because the
"fail loud, never fallback" discipline was pointed at the evidence store and the
labels were standing somewhere else. The project's founding idea (a verdict is a
mechanical fact about what was actually retrieved) turned out to be the exact idea it
had failed to apply to its own toolchain (a rebuild should be a mechanical fact about
what a human actually judged). The moat and the label file wanted the same guarantee;
only one of them had it. Fixing the second made the first's philosophy honest.

**Next action:** Sai ratifies `labels-v2.csv` → `assure-calibrate` → CR-002. Then the
Alpha wall (AA-MOAT-003/-005/-007: fix or accept-as-residual) is one decision.
