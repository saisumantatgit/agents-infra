# OVERNIGHT 2026-11-15 — instrument (OVN-1115; how to DERIVE work each cycle)

GOAL: move Agent-Assure toward alpha: fewer fabrications certified PASS, a measurement of honest-claim
refusals (Error-A) large enough to trust, and a first-run path a new tester can follow without help.

Sai: "AGREED GO" (D-112). Hard stop 07:30 IST 2026-11-15. Budget: 5M new tokens (output + cache creation)
for the night, ceiling 6M; OVN-1114 used ~1.1M (harness subagent_tokens). Tick 30 min.
Worktree ../ai-overnight-1115. Branch per queue item: ovn-1115-q<N>.

## STOP RULE (corrects OVN-1114)
Disarm ONLY at: hard stop 07:30 IST · budget ceiling · circuit breaker. An empty queue is NOT a stop:
re-derive the next queue from §2 and log the derivation. At 80% budget stop starting new items.
Times in the record come from `TZ=Asia/Kolkata date` or git timestamps, never estimated.

## §1 Each cycle, derive state (code first)
`git log --oneline origin/main -5`; `gh pr list --state open`; worktree status; fresh suite
`cd Agent-Assure && uv run pytest -q > out 2>&1; echo $?`; md5 calibration/labels-v2.csv ==
6215b526d03147295b003d7ccb0d171f; running agents. The queue = first item in §2 not DONE.

## §2 Queue (in order; each item's "done" is stated)
Q1 R37 hole classes (reports/RED-TEAM-R37.md — those also open on main). Done = each class fixed fail-closed
   with proven-red tests, or recorded as not safely fixable with a CEILING; adversary round 0 blockers vs
   main; Error-A measured (on Q2 corpus once it exists); PR merged under D-100.
Q2 Error-A corpus: ≥300 honest drafts with sources across genres (product docs, READMEs, API docs, FAQs,
   reports with tables, meeting notes, changelogs, code-review notes), built from text WE write or from
   repo-owned docs — no third-party/GPL text copied in. Each draft's claims honestly copied/grounded in its
   source. Runner reports per-genre PASS/NW/FAIL + grounded-claim rate; baseline on main. Done = merged with
   baseline numbers recorded. This becomes the Error-A gate for every later fix.
Q3 Alpha walkthrough: fresh clone into scratch, follow README + ALPHA-TESTER-GUIDE exactly as a new tester
   (Sonnet executor, no repo knowledge beyond the docs). Every stall/confusion/error = a finding. Done =
   report filed; doc/UX fixes that change no verdict merged; anything verdict-changing goes to the queue.
Q4 Next-sentence-rule ruling pack (7 of 9 H1 Error-A losses; reports/S1-CODE-TOKEN-DIAGNOSIS.md):
   measure candidate fixes on a scratch copy against Q2 + usage_genres + an attack set. Measure ONLY —
   shipping widens passes (Escalation #1, no ruling given). Done = report for Sai.
Re-derive when Q1–Q4 are done: next candidates come from RED-TEAM reports' open items, Q2 per-genre
   failures, Q3 findings, alpha-guide gaps — ranked by error cost (Error-B first), then tester impact.

## §3 Gates (D-100 for any merge) — `&&`-chained; `cmd > out 2>&1; echo $?`; explicit-path staging;
   assert branch before commit; no push to main; merged tree == tested tree checked after merge.
## §4 Executor ladder: moat fixes + adversary = Opus; corpus writing, walkthrough, measurement = Sonnet;
   main loop re-runs every load-bearing number before it enters a commit.
## §5 Breaker: 2 cycles no progress and nothing in flight ⇒ halt, name class. 2 same-class terminal failures ⇒ halt.
## §6 Teardown BEFORE disarm: remove ../ai-overnight-1115 and q-branches once merged; empty my scratch
   (/private/tmp/claude-501/ovn1115*); Agent-Assure/.venv in worktree goes with it; corpus stays in repo
   only if small (<5MB) — else Drive, noted.
## Park list: Escalation #1 (anything that lets more claims pass vs main: Q4 shipping, D-102 rows, hole b,
   allow-list additions), gold labels, install.sh, hooks, SOUL.md, ~/.claude writes, anything outward.
