# Session-B queue — 2026-09-12 afternoon (window closes in ~6h)

Cron-advanced. Durable; the cron itself dies with the session.
**Target is NOT Alpha** — it is not reachable in the window, and a tag that
claims it would lie. Target: **close the moat work, leave the corpus split
clean**, so the next session starts on "recruit one reader" instead of "can we
trust anything".

## Ratified by Sai this session
D-24 ratified · OI-MOAT-27 approved (factive whitelist) · the 5-item plan
ratified · J-20 DONE and pushed.

## Parked — no ruling given, do NOT assume one
J-15 (rhetorical questions) · D-07 (`install.sh --no-dev`) ·
`docs/consulting/` privacy · **q25 gold adjudication** (Escalation #2, standing
gate — a gold label is never Claude's to set).

## Queue

- [x] **1. `score.py` catch-all fixed + the round written up.** 2 branches -> 5;
      none now asserts a pattern it has not checked. Report:
      `docs/reports/INTRA-RATER-2026-09-12.md`. Headline: anchoring REFUTED 4/4;
      κ=+0.857 on evidence-derivable items, 0/2 on policy items — and the
      2026-09-03 "my page's wording caused it" diagnosis is RETRACTED, because
      the rebuilt page stated provenance outright and the answer did not change.
- [x] **2. J-19 DONE (partial, scope stated).** Factive whitelist + negation
      conjunct, purely additive. Round-7 c1/c2/c4 XPASSED -> permanent guards;
      **c3 and c5 stay OPEN** (no complementizer — J-19 cannot reach them).
      Subject-swap control verified: endorsement follows the VERB, not the
      subject. Honest mirror GREEN. `posit` refuses without being enumerated —
      the whitelist polarity working. Suite 524/2/17, corpus byte-identical, so
      no CR is due. Open Error-B classes 18 -> 15.
- [x] **3. THREE of four closed (D-30/31/32); the fourth ESCALATED.**
      29 (comments no longer stripped inside code spans), 30 (blank line forced
      after a header), 32 (a cited span is never zero-content NON_CLAIM) all
      XPASSED and are permanent guards. **31 deliberately NOT patched:** every
      narrow fix is the blacklist/length shape that has failed five times, and
      the sound fix inverts a default, which moves the Error-A/Error-B trade-off
      = Escalation #1. Also D-33: hoisted `import re as _re` to the top — three
      NameErrors in this file have had that one cause, one of them today.
      Suite 527/2/14, corpus byte-identical. Open Error-B classes 15 -> 12.
- [x] **4. DONE (D-34).** `label_basis` column on the scaffold (DERIVED) +
      `reliability_eligible()` in calibrate.py. κ excludes policy rows; **error
      rates include them, pinned by a source-inspection test** so nobody later
      "helpfully" drops them from the rates too. 52 labels still gold, zero
      stale — a new column does not change `claim_sha`. Suite 532/2/14.
  ~~old: **4. Segregate POLICY-labelled rows**~~
      Tonight's finding: 3 raters × 2 `haiku_summary` rows = 0/6 agreement with
      gold, because the label follows a RULE not the evidence. Reliability on
      such items measures rule-memorisation. Scaffold-side ONLY — **no generator
      may touch `labels-v2.csv`** (PIR-002). ~0.4M
- [x] **5. DONE (D-35, OI-UX-01).** Sai stalled on 6/20 rows, all of them
      evidence-reads-as-absent. If the gate's author can't tell "nothing found"
      from "page broken", a stranger reading a report can't either. ~0.3M
- [x] **6. Round 8 RAN — 21 findings, 12 Error-B, 0 classes closed.** Three
      Opus adversaries + a solo gate. The gate REFUTED my own headline: D-36
      closed `that the <span>` and left `that <any other function word>
      <span>` open, denial included, at PASS/100.0 — so R8A-01/02 are
      REOPENED and the round closed nothing. 20 findings tripwired (43 strict
      xfails). D-36 kept (fail-closed, closes a real shape) with its "CLOSED"
      claim retracted and a NEW unmeasured Error-A recorded. New job J-21:
      sentence-bounded complement detection via syntok — deliberately not
      attempted tonight, because a third leftward-scan patch is the shape with
      a 100% failure record here. Whitelist additions escalated to Sai
      (PASS-enabling). Suite 563/2/56. Corpus byte-identical.
- [x] **7. CLOSED 2026-09-12.** 7-step close run in order: memory synced (the
      2026-09-03 inter-rater entry corrected — that fork is resolved), tree
      audited, logbook entry with all four withdrawals and a reflection,
      RESUME-HERE rewritten to lead with "round 8 closed nothing", J-21/22/23
      registered with owners, temp scripts removed, pushed, verified clean.
      No CR due — corpus byte-identical all session. Cron deleted.

## Stop conditions
- Any PASS-enabling change -> tripwire, do not fix.
- A gold label needs changing -> STOP, it is Sai's (standing gate).
- **Hard stop with ~1.2M left, jump to item 7.** A half-finished round 8 with no
  handoff is worse than no round 8, and it is the one failure I can still cause.
