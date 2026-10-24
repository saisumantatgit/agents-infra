# OVERNIGHT 2026-10-25 — progress

## Cycle 0 (01:09 IST) — handshake, nothing armed
- State from code: main 80196b2; 996/2/61; gold md5 unchanged; A 0.480, B 0/27.
- **Finding at handshake:** the tester guide's own quoting example FAILS.

## Cycle — 01:4x · C1 done · C2 WITHDRAWN · C3 under round 29

- **C1** `686bcb6`: the guide's quoting example FAILED; corrected; its examples now
  RUN as a test (proven red). Quoting set: framing + quote grounds 0 whole claims;
  a claim that IS the source sentence grounds; real prose sentences 76/119 (64%).
- **C2 (look-back stops at sentence boundary) — WITHDRAWN.** Round 28: 14 flat
  denials ("This never happened.", "No such event occurred.", "Not at all.") in
  the previous sentence let the next sentence ground — refused on base. Reproduced
  by me: r28-target PASS GROUNDED vs base FAIL. Cause: C2 dropped negators unless
  the previous sentence held one of 16 truth words — a word list that LICENSES a
  pass (D-69). Not offered to Sai. Branch kept as the record.
- **C2's plan item was itself a withdrawal of my first C2 (framed quotations),**
  replaced because framing's subject is uncheckable (misattribution Error-B).
- **C3** fail-closed fixes + 'myths' (found by C2's agent): suite 1033 green, rates
  unchanged; round 29 attacking it alone (round 28 did not cover C3's own fixes).
- Pre-existing, registered: denials beyond 5 tokens back; unlisted denials
  ("Hardly.", "None of that happened.", "We dispute the following.").

---

# MORNING REPORT — 2026-10-25 · DISARMED at DIFF ZERO (~02:55 IST), well before the 07:30 stop

## 1. DONE
| Item | Proof | Result |
|---|---|---|
| C1 quoting measured; guide corrected | `uv run pytest tests/test_guide_examples.py` (red on the old guide) | **PR #21** |
| C3 five fail-closed fixes, round 29 | suite 1029 passed on c3-residue | **PR #22** |
| S1 + S2 stretch, round 30 | suite 1043 passed on stretch-s1-s2 | **PR #23** (stacked on #22) |
| Gates on every branch | gold md5 6215b526…d171f unchanged | Error-A 0.480 · **Error-B 0/27** |

## 2. NOT DONE
Nothing in the committed set. Open, registered: denials beyond 5 tokens / unlisted
denials (R28-03/04); short replies "No." beside a claim; more DDG failure texts;
"Fallacies:/Debunked:" labels; a near-copy diluted with unrelated lines.

## 3. DENIED
Nothing.

## 4. ONE-WAY DOORS — Sai's
    gh pr merge 21 --merge --repo saisumantatgit/agents-infra
    gh pr merge 22 --merge --repo saisumantatgit/agents-infra
    gh pr merge 23 --merge --repo saisumantatgit/agents-infra   # ONLY if you accept S2's price
**Decision:** S2 refuses a short genuine source quoted in full — it collides with
option A. Accept, or I split S1 out and drop S2.

## 5. UNKNOWNS
What the guide's corrected advice yields on a real tester's sources (measured
64% prose / 34% bullets on repo docs only).

## 6. BUDGET
Subagents, derived from completion records: **1150874** (11 agents).
Main loop: UNKNOWN exactly; estimate ~2.0M total of 4M sanctioned.

## 7. WITHDRAWALS
- **The guide's quoting example (shipped in #19) — wrong.** I wrote it without running it.
- **C2 as planned (framed quotations) — withdrawn** before building: misattribution Error-B.
- **C2 as built (look-back stops at sentence boundary) — withdrawn** after round 28:
  14 flat denials let the next sentence ground.
- **C3 fix 4 (textarea comments) — reverted** after round 29; redone properly in S1.
- My R27/R28 shell slips: a zsh `$B:A` path modifier and the scratch-path fix.

## 8. FRAMEWORKS
*Calibration* — the guide's own example was the first thing run, and it failed.
*Inversion* — framed quotations: what would an attacker do with an uncheckable
subject? *Via negativa* — fix 4 reverted rather than reworked at 2 a.m.
*Asymmetry of error cost* — S2's Error-A price stated, not hidden.

## §8 — 5-USER COMPREHENSION TEST (yours, today)
Five people who READ verification reports, not buyers; ten minutes each; follow
`docs/research/user-test-2026-10-03/PROTOCOL.md`. **Ask about FAIL as well as
PASS** — and show them the corrected guide's advice: does "copy the source's own
sentence" read as reasonable, or as a burden?

## §6 DISK
REMOVED: worktrees wt-c3, wt-c2, wt-s1-comment-citations, wt-s2-near-copy; scratch
r28 (464K), r29 (14M), r30 (644K), bb, gen, helpers. Keep-awake 5856 stopped.
Cron 1e749876 deleted; CronList empty. KEPT: ~/tmp/assure-probe, ~/tmp/assure-probe2.
