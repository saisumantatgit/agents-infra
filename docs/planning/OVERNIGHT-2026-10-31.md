# OVERNIGHT 2026-10-31 — instrument (how to DERIVE work each cycle; no hard-coded answers)

GOAL: Agent-Assure's fail-closed hardening (H1–H5) is on `main` with an adversary round behind it,
so tomorrow's alpha testers run a checker with five fewer ways for a fabrication to pass.

Sai: "Consider you have my agreed and proceed." Budget 5M new tokens (output + cache creation),
ceiling 6M. Hard stop 07:30 IST 2026-11-01. Tick 30 min. Worktree ../ai-overnight-1031.

## §1 Each cycle, derive state (code first)
1. `git -C <wt> log --oneline origin/main..HEAD`, `gh pr list --state open`, fresh
   `cd Agent-Assure && uv run pytest -q > out 2>&1; echo $?`, gold md5 (feature_rows-v2.jsonl
   per tests/test_measure_rates.py) == 6215b526d03147295b003d7ccb0d171f.
2. Diff rule — the queue is whatever of these is NOT yet true, in order:
   C1 R31 adversary round on hardening-2026-10-25 complete, report in Agent-Assure/reports/.
   C2 Every R31 BLOCKER (branch passes what main refuses) fixed fail-closed + proven red, or the
      offending fix reverted. Non-blocker NEW holes: fail-closed fixes allowed; pass-widening → Sai.
   C3 PR opened; D-100 bar met (suite green on head AND merged result; gold md5; B unchanged,
      A movement stated; proven red; adversary round) → merge with `gh pr merge --merge`.
      Classifier denial → command goes to morning report; never routed around.
   S1 (stretch, only after C3 merged) diagnose U1's "Blank lines are skipped" refusal — read-only
      diagnosis; a fix only if fail-closed.
   Diff zero = C1–C3 true and S1 done or blocked ⇒ disarm.
## §2 Gates: `&&`-chained; `cmd > out 2>&1; echo $?`; never pipe to tail. Explicit-path staging.
   Assert branch before every commit. No push to main.
## §3 Executor ladder: adversary + moat fixes = Opus (last gate / moat); diagnosis = Sonnet;
   main loop re-verifies every agent claim by diff + fresh test run (testimony ≠ evidence).
## §4 Breaker: 2 cycles unchanged diff, no in-flight growth ⇒ halt, name class, disarm.
   2 same-class terminal failures ⇒ halt. Disarm at diff zero / breaker / 07:30 / 6M.
## §5 Disk/infra teardown BEFORE disarm: remove worktree ../ai-overnight-1031 and any r31
   scratch worktrees (`git worktree prune`); empty scratchpad; no datasets created
   (if any >50MB appear, move to Drive before disarm and note it).
## Park list: Escalation #1 (pass-widening incl. U1 structural-UNCITED, code spans, parentheses),
   gold labels, install.sh, hooks, SOUL.md, ~/.claude writes, anything outward.
