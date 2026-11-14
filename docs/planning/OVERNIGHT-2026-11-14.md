# OVERNIGHT 2026-11-14 — instrument (how to DERIVE work each cycle; no hard-coded answers)

GOAL: alpha testers get a checker on `main` that refuses four more known ways a fabricated claim
can be certified PASS (Error-B), with every new honest-claim refusal (Error-A) counted and disclosed.

Budget 5M new tokens (output + cache creation), ceiling 6M. Hard stop 07:30 IST 2026-11-15.
Tick 30 min. Worktree ../ai-overnight-1114 (branch overnight-2026-11-14). Status: ARMED cron c453c47b on AGREED (D-105).

## §1 Each cycle, derive state (code first)
1. `git -C <wt> log --oneline origin/main..HEAD`; `gh pr list --state open`; fresh
   `cd Agent-Assure && uv run pytest -q > out 2>&1; echo $?`; md5 of Agent-Assure/calibration/labels-v2.csv
   == 6215b526d03147295b003d7ccb0d171f; tests/test_measure_rates.py still pins (fp,tn)=(12,13).
2. Diff rule — queue = whichever is NOT yet true, in order (open holes per reports/RED-TEAM-R34/R35):
   C1 Adversary probe (Opus) re-confirms each hole below REPRODUCES on main 83a5cb9 (a hole that no
      longer reproduces is dropped, with the evidence row). Report reports/RED-TEAM-R36.md.
   C2 Fail-closed fix + proven-red test for each reproducing hole:
      a. denial three or more sentences before the claim;
      b. R31-03 heading-padding near-copy bypass;
      c. verbless claim headings ("# Bank Collapses", "# Acme guilty");
      d. "made up" / phrasal denial phrasing.
      Each fix: usage_genres re-run, Error-A delta stated per segment; any fix that drops a draft
      from PASS is WITHDRAWN (H5 precedent), not shipped.
   C3 Adversary round (Opus) on the C2 diff; every blocker fixed or its fix reverted.
   C4 PR opened; D-100 bar met (green on head AND merged tree; gold md5; Error-B unchanged, Error-A
      movement stated; proven red; adversary round) → `gh pr merge --merge`; verify
      origin/main^{tree} == tested HEAD tree. Classifier denial → morning report, never routed around.
   S1 (stretch) read-only diagnosis of the H1 `=False`/`=True` code-token misread (9 Error-A segments);
      write the narrow-fix spec only. Implementing it widens passes ⇒ Escalation #1 ⇒ Sai.
   Diff zero = C1–C4 true and S1 done or blocked ⇒ disarm.
## §2 Gates: `&&`-chained; `cmd > out 2>&1; echo $?`; never pipe to tail. Explicit-path staging.
   Assert branch before every commit. No push to main. Fresh worktree has no .venv → `uv run`.
## §3 Executor ladder: adversary probes + moat fixes = Opus (moat / last gate); usage re-runs and
   evidence capture = Sonnet; main loop re-verifies every agent claim by diff + fresh test run.
## §4 Breaker: 2 cycles unchanged diff, no in-flight growth ⇒ halt, name class, disarm.
   2 same-class terminal failures ⇒ halt. Refuted twice ⇒ step back. Disarm at diff zero / breaker /
   07:30 IST / 6M.
## §5 Disk/infra teardown BEFORE disarm: remove ../ai-overnight-1114 and any r36 scratch worktrees
   (`git worktree prune`); delete merged local branches; empty scratchpad; restore usage_genres
   results.json unless deliberately re-baselined. No datasets expected; any file >50MB → Drive, noted.
## Park list: Escalation #1 (anything that lets more claims pass, incl. D-102 rows 1–2, the S1 hedge
   window, the =False narrow fix, adding headings to _HEADING_ALLOWLIST), gold labels, install.sh,
   hooks, SOUL.md, ~/.claude writes (except memory dir), anything outward.
## Frameworks reference: §2-B/§2-C of Sai's standing-order template — re-read before consequential calls.
