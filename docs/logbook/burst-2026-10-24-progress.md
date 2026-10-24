# BURST 2026-10-24 — progress

## Cycle 0 (18:1x)
- State unchanged since 10-22. 11 agents launching: W1 R25, W2a-d, W3a-d, W4, W5.

---

# REPORT — burst 2026-10-24 · DISARMED at diff zero, before the 20:15 stop

## 1. DONE
- **W1 round 25:** no Error-B against the latest fix; overflow regression confirmed closed.
- **W2 four adversaries:** W2a 4 new CRITICAL/HIGH (cross-sentence word swaps), W2b 6 numeric (sign/comparator/currency/decimal), W2c 1 HIGH (textarea comment), W2d 1 HIGH (relative-path self-citation). **All pre-existing on main; none introduced by PRs #12/#13.**
- **W3 usage instrument:** 20 honest drafts through the real hook — **0 PASS; 171 of 177 true claims refused (97%)**, recounted by me from the reports.
- **W4:** PR #13 safe to merge; its missing guards added and proven red.
- **W5:** alpha-tester guide; one stale line corrected before commit.
- **Fix PRs, each proven red by me on the base code:** #14 DDG (verified on Sai's real probe record), #15 W2A, #16 W2D, #17 W2B. Error-A 0.400 / Error-B 0.000 unchanged on every one.
- **Live probe:** exa failures leave no record; DDG 404 stored "ok" as a JSON wrapper.

## 2. NOT DONE
Merges — denied (below). #14–#17 unattacked.

## 3. DENIED
`gh pr merge 13` by the auto-mode classifier (no reason given). Not retried, not routed. Commands are Sai's.

## 4. ONE-WAY DOORS — Sai's, in this order
    gh pr merge 13 --merge --repo saisumantatgit/agents-infra
    gh pr merge 12 --merge --repo saisumantatgit/agents-infra
    gh pr merge 11 --merge --repo saisumantatgit/agents-infra
Then #14–#17 on review.

## 6. BUDGET
Subagents, derived from completion records: **1,490,575** (15 agents). Main loop: UNKNOWN exactly; estimate ~2.3M total of the 6M window.

## 7. WITHDRAWALS
My first J-97 guard fired on a docstring and failed the unmodified code — tightened. My first pre-fix check for W2a hit the suite's environment guard, not the code — redone. My `rm -rf $S/*` was correctly blocked — redone with literal named paths.

## §8 — 5-USER COMPREHENSION TEST
Still the only thing that can reverse D-83 — and now sharper: if 0 of 20 honest drafts pass, what a reader takes FAIL to mean matters as much as PASS.

## §6 DISK
REMOVED: worktrees wt13, wt-fix-w2a/w2b/w2d/ddg (each with .venv); scratch w1, w2a (124K), w2b (1.0M), w2c (360K), w2d (80K), w4, ev.json, mk.py, p.md; /tmp fix backups. Keep-awake 68214 stopped. Cron bc5d1b4a deleted; CronList empty. KEPT: ~/tmp/assure-probe, ~/tmp/assure-probe2 (Sai's live stores).
