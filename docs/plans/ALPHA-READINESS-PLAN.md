# Agent-Assure — Alpha Readiness Plan

**Author:** Fable 5, 2026-07-07 (handoff artifact). **Executor:** Opus 4.8 leads; Sonnet 5 on mechanical tasks as marked. **Status:** PLAN — execute top-to-bottom; every phase has checkable exit criteria.

**Alpha definition (the bar this plan reaches):** Agent-Assure installable as a Claude Code plugin in a *second, unrelated* repo by someone other than its author, capture → verify loop working end-to-end on a real research session, gate thresholds calibrated on Sai-ratified labels at n≥50, with the moat property (fabricated citation can never PASS) regression-protected. Alpha explicitly does NOT include: 2a research front-end, 2d cross-platform, marketplace listing.

---

## Phase α0 — Trust re-establishment (Opus, first 30 min, non-skippable)

This plan crosses an execution discontinuity (Fable → Opus). Per the discontinuity-distrust rule, verify before building:

- [ ] `git -C Agent-Assure status` clean; branch state matches HANDOFF-MASTER-PLAN §1.
- [ ] `uv run pytest` from `Agent-Assure/` — all green; record count in logbook.
- [ ] Re-read `calibration/CR-001-bootstrap-lex-tau.md`; confirm lex_tau=0.71, Error-B=0.143, n=12.
- [ ] Confirm with Sai whether the 2026-07-03 live capture validation counts as the Phase-1b human gate being CLOSED, or still open. **Do not infer.**

**Exit:** logbook entry "α0 verified" with test count + gate status answer.

## Phase α1 — Gold-label ratification package (Opus; the long-pole human gate)

The single Alpha blocker only Sai can clear. Make his ratification as cheap as possible:

1. Widen the corpus: extend `calibration/build_corpus.py` runs to n≥50 claims across ≥25 queries, mixed real sessions + constructed adversarial cases (Sonnet can generate; Opus curates for class balance — target ≥30% violation class, since positives are the pinned class).
2. Emit `calibration/labeling-v2.csv` with candidate labels, each row carrying: claim, source excerpt, candidate verdict, one-line rationale, `label_status=candidate`.
3. Produce a 1-page ratification brief for Sai: what to check, expected time (~30–45 min), the 10–15 rows where candidate confidence is lowest flagged for closest attention.

**Exit criteria:** labeling-v2.csv exists, fail-loud loader rejects it while `label_status=candidate` (test proves it — red first), ratification brief delivered to Sai via inbox item (`inbox/pending/P1_...`).

## Phase α2 — Calibration run v2 (Opus for adjudication, Sonnet for mechanics; BLOCKED on α1 ratification)

- [ ] Ingest ratified labels; loader accepts only `label_status=gold`.
- [ ] Rerun threshold sweep + leave-one-out on n≥50.
- [ ] Operating-point selection under the moat constraint: **Error-B ≤ 0.143 (current), then minimize Error-A.** If no point satisfies this, STOP and escalate — do not pick "best F1."
- [ ] Emit CR-002 (≤80 lines, projection = CR-001 actuals, delta column).
- [ ] Update README/docs: replace "provisional" language with "(n=NN, CR-002)" citations. Grep for `0.71`, `provisional`, `n=12`, `n≈12` to catch stale claims.

**Exit:** CR-002 committed; every quoted error rate in the repo traces to it.

## Phase α3 — 2b NLI tier (Opus; per PHASE2-SEQUENCING order, NLI lands before FINAL calibration — so run α2 as bootstrap-v2, then re-run calibration after α3 as CR-003)

- [ ] Local DeBERTa-MNLI entailment tier per design spec; **fail-closed**: NLI can upgrade UNGROUNDED→GROUNDED for paraphrase only when entailment ≥ nli_tau; it can never influence UNVERIFIED_CITATION or numeric verdicts; model-load failure → tier disabled, gate proceeds without it (and says so in the report).
- [ ] Tag NLI-influenced verdicts `tier_sensitive` correctly (the `f11f8d4` class of bug is the #1 risk here).
- [ ] Red-team: paraphrase fixtures flip A-errors to GROUNDED; fabricated-citation fixtures still FAIL byte-identically.
- [ ] CR-003: post-NLI calibration re-run (labels already gold from α1 — cheap).

**Exit:** paraphrase Error-A measurably reduced vs CR-002, Error-B not increased, all prior tests green.

## Phase α4 — Second-repo install validation (Sonnet execution, Opus sign-off)

- [ ] Fresh clone of an unrelated repo (e.g. `financial-advisor-india`); run `install.sh`; register plugin.
- [ ] Real research session: ≥5 retrievals captured; `/assure-verify` on a genuine draft; verify store contents match what the session saw.
- [ ] Deliberate fabrication inserted into the draft → gate FAILs it.
- [ ] Record friction list — every manual step, confusing output, or missing doc becomes an issue.

**Exit:** end-to-end transcript saved under `docs/alpha/`; friction list triaged.

## Phase α5 — Alpha sign-off (Opus whole-branch adversarial review — this gate never downgrades)

- [ ] Whole-branch Opus review per global routing table (a miss here ships).
- [ ] Moat regression suite green (assure-red-team fixture matrix, Lane A spec §6.2).
- [ ] AAR-004 written; logbook closed; version tagged `v0.9.0-alpha`.

**Exit:** Sai says go. Alpha declared.

## Risks and their tripwires

| Risk | Tripwire | Response |
|---|---|---|
| Sai ratification stalls (long-pole) | α1 inbox item >7 days old | Ship-flagged path per spec: keep thresholds provisional, proceed to α3/α4, hold α5 |
| NLI tier creates an Error-B | any red-team fabrication fixture PASSes | Release blocker; revert tier; escalate |
| n≥50 corpus skews easy | violation class <30% | Opus curates harder negatives before labeling brief goes out |
| Executor drift from this plan | any phase exits without its logbook entry | Re-read this plan; missing evidence = phase not done |
