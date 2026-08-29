# RESUME HERE — Agent-Assure Calibration Workspace

**Last session:** 2026-08-30 (autonomous close-out run under Sai's 10M sanction + standing order).
**Authoritative handoff:** `docs/logbook/2026-08-30-autonomous-closeout.md`, then `docs/decisions/RATIFICATION-REGISTER-2026-08-30.md` (every autonomous call + its undo). This file is the quick-start pointer, not the record.
**Branch:** `agent-assure-calibration-run` — **~30 commits NOT PUSHED**: `git push` was denied by the permission classifier this session. Push is the first thing to do.

## What changed on 2026-08-30

Every item parked behind "Sai must rule" was re-examined against one question:
*does this need a human ruling, or was it merely unresolved?* The separator
turned out to be **reversibility, not importance** — a fail-closed change cannot
manufacture the unrecoverable error. Three July deferrals were mine; the rest
stayed yours. Then the red team ran three times and reshaped the day.

| Was | Now |
|---|---|
| OI-MOAT-03 / -05 / -07 (open since July) | **FIXED** (D-03/-04/-05) |
| OI-CAL-01 (gate ran 0.65 while docs said 0.71) | **RESOLVED** — 0.71 deployed + `--lex-tau` (D-06) |
| OI-ENV-01, OI-NUM-02 | **FIXED** (D-07, D-12) |
| AA-MOAT-* IDs | **renamed** OI-MOAT-{NN} per HQ ADR-039 (D-08) |
| cpc-book ask (open since 07-19) | **answered** + batch ingestion built (D-09) |
| Red-team rounds **3, 4, 5** | **65 wrongful PASSes found**; OI-MOAT-11…19, 22/23/24 closed |
| Error-A never measured | `tests/honest_drafts/` harness added (D-13) |

## Orientation (5 minutes)

1. `cd Agent-Assure && uv sync && uv run pytest` → **453 passed + 1 skipped + 3 xfailed**
   (the count moves every red-team round — trust the run). The 3 xfails are
   deliberately-open items: OI-MOAT-20, OI-MOAT-21, OI-T2-01.
   `--extra dev` is no longer needed (OI-ENV-01 fixed).
2. `CLAUDE.md` (root) — the operating manual. **`lex_tau` now RUNS at 0.71.**
3. `docs/decisions/RATIFICATION-REGISTER-2026-08-30.md` — the 14 autonomous calls.
4. `Agent-Assure/docs/plans/reports/RED-TEAM-R{3,4,5}-2026-08-30.md` — **read R5's
   convergence assessment before trusting any of the fixes.**
5. `ls inbox/pending/` — one P1 item still waits on **you**.

## Waiting on you

| # | Decision | Where | One-line context |
|---|---|---|---|
| 1 | **Ratify gold labels** (30–45 min) | inbox P1 + `calibration/RATIFICATION-BRIEF-v2.md` | STILL THE LONG POLE. **Edit `labels-v2.csv`.** Nothing this session touched them; all 52 remain `candidate`. |
| 2 | **Push the branch** | — | `git push origin agent-assure-calibration-run`, plus 1 commit in `~/vibe-coding/Agents/Claude`. My push was denied; I did not route around it. |
| 3 | **Ratify or reverse the 14 autonomous calls** | the register | Each row carries its undo. Includes a self-disclosed side effect: the pytest change altered what `install.sh` does for END USERS. |
| 4 | **OI-MOAT-21 — T2 is not sound** | OPEN-ISSUES | **The most consequential open item.** T2 alone suffices for GROUNDED, and T2 is an F1 *ratio* over the claim's own length. Round 5 hit F1=1.000 with a false-order recitation; it PASSes at lex_tau **0.99**. Demoting T2 changes the gate's meaning and invalidates the calibration — Escalation #1+#3. |
| 5 | **OI-DEC-01** | OPEN-ISSUES | The first PASS-*enabling* fix in the cohort ⇒ yours. |
| 6 | **OI-T2-01** | OPEN-ISSUES | A **verbatim** short quote reads UNGROUNDED. Pre-existing; found by the new Error-A harness, invisible to red-teaming by construction. |
| 7 | **OI-MOAT-20** | OPEN-ISSUES | Verb-final header escapes scoring. Closing it deterministically needs a POS tagger ⇒ ADR-004 Q3 territory. |
| 8 | **ADR-004 / Phase-2b** | `docs/plans/ADR-004-DECISION-PACKAGE.md` | **Read the 2026-08-30 addendum**: T3's case has *inverted*, not shrunk. |

## State snapshot

| Thing | State |
|---|---|
| Phase 1 (gate + capture + plugin) | COMPLETE |
| Demo | READY — re-verified after every fix today (honest PASS 100.0, fabricated FAIL 50.0) |
| Moat | Rounds 1–5 done. **Each round found holes in the previous round's fixes.** R5 convergence: drafts/mechanism 7.4→10.3→12.5, every R4 fix attacked directly held, but surviving attacks are *more* natural. Verdict: **the process is converging; the T2 design is not.** |
| Calibration | CR-001 stands (n=12). Labels: 52 candidate, **untouched**. Batch ingestion built for incremental multi-domain corpora |
| α2 / CR-002 | **BLOCKED on your ratification** (unchanged) |
| α5 sign-off | Gated on ratification + **OI-MOAT-21**, which is a live Error-B hole |

## Standing discipline (each learned by being burned)

- **Regenerate the corpus and diff it after ANY classify/tiers/score change** —
  `uv run python -m calibration.build_corpus_v2 --features-only`. It has caught a
  bad fix in **four** sessions running, including one a 446-test green suite waved through.
- **Never tune a constant to make one corpus row pass.** Change the rule's meaning.
- **Re-run the red team after every remediation.** Five rounds; every one found
  holes in the last, twice within hours.
- **Never key a defence on a property the author controls** — a token count was
  walked under, its proper-noun replacement was beaten by the Shift key.
- **Every "I don't know" must point AWAY from PASS.** `NON_CLAIM`, `None`, and an
  empty set were all catch-alls pointing toward it.
- **Fix BOTH branches.** Three of round 5's four findings were one fix applied to
  one side of a two-branch decision (T1 not T2; query side not contradiction side).
- **Measure both directions.** Red-teaming cannot find a wrongful FAIL by
  construction; `tests/honest_drafts/` exists for that half.
- **Green-on-first-run is not evidence.** Mutation-check new guards.
