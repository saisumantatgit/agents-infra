# OVERNIGHT 2026-11-21 — instrument (OVN-1121; how to DERIVE work each cycle)

GOAL: by morning, a fabrication planted as a document heading or stated one or more sentences before its
denial is no longer certified PASS, and the fabrication test set covers more kinds of lie, so that an
alpha tester's PASS can be trusted, measured on our own corpora.

Status: AGREED by Sai 2026-11-20 23:39 IST (D-119). Open asks unanswered ⇒ defaults: no pass-widening; no Claude build fallback (a lane failing twice same class is BLOCKED). Hard stop 07:30 IST 2026-11-21. Budget 10M Claude new tokens
(output + cache creation, de-duplicated by message id), ceiling 12M. Codex tokens measured and reported
separately from ~/.codex/sessions rollouts whose cwd is an OVN-1121 worktree. Tick 30 min (:07/:37).
Branch for docs: overnight-2026-11-21 (worktree ~/vibe-coding/Agents/ai-overnight-1121).
Branch per build item: ovn-1121-<id>, each in its own worktree ~/vibe-coding/Agents/ai-ovn1121-<id>.

## STOP RULE
Disarm ONLY at: hard stop · budget ceiling · circuit breaker. An empty queue is NOT a stop: re-derive the
next queue from §2 and log the derivation. At 50% budget, log position. At 80%, stop starting new items.
Times in the record come from `TZ=Asia/Kolkata date` or git, never estimated.

## §1 Each cycle, derive state (code first)
1. `git -C ~/vibe-coding/Agents/agents-infra fetch -q && git log --oneline origin/main -5`; `gh pr list --state open`.
2. Worktrees and in-flight executors: `git worktree list`; `pgrep -fl "codex exec"`; running Claude agents.
   An executor is in flight if its process is alive OR its events.jsonl grew since the last tick.
3. On main (or the merged tree): `cd Agent-Assure && uv run pytest -q > out 2>&1; echo $?`;
   `md5 -q calibration/labels-v2.csv` == 6215b526d03147295b003d7ccb0d171f;
   `uv run python tests/error_b_corpus/run.py --base $PWD` and `tests/error_a_corpus/run.py --base $PWD`.
4. The queue item to work = first item in §2 not DONE and not BLOCKED. If none: re-derive (§2 last line).

Baselines on main aa78683, measured 2026-11-20 between 23:34 and 23:38 IST (re-confirm before building on them):
suite 1425 passed / 2 skipped / 74 xfailed; Error-B 7/280 certified PASS (claim_heading 5, denied_2back 1,
denied_3plus_back 1), 11 fabrications grounded; Error-A 336 drafts PASS 5 / NW 156 / FAIL 175,
claims grounded 2044/3990.

## §2 Queue (in order; each item's DONE is stated)
C1 Claim-heading + far-denial holes (Error-B classes claim_heading, denied_2back, denied_3plus_back).
   Fix fail-closed only (narrows passes). DONE = proven-red tests per hole; Error-B corpus certified PASS
   for these 3 classes reduced (target 0), no other class rises; Error-A movement measured and stated, and
   no larger than the honest-claim loss the fix's report justifies claim by claim; structural-guard digest
   re-pinned only with the reason written in the PR; Opus adversary round 0 blockers vs main; PR merged
   under D-100. If a hole cannot be closed without refusing honest headings: CEILING + report, not merged.
C2 Fabrication corpus v2: add classes the 280-draft set lacks — direction flip (rose→fell), quantifier
   inflation (some→all), dropped condition (if X then Y → Y), date/period shift, comparative flip, scope
   widening (one product → all products) — each ≥15 drafts with an honest control twin, text we write.
   DONE = merged with per-class baseline on main; every escape becomes a C3 row.
C3 Close C2 escapes, same DONE bar as C1, one PR per hole family.
Re-derive when C1–C3 are DONE or BLOCKED: next candidates from open items in reports/RED-TEAM-R4*.md,
   Error-B escapes, Error-A per-genre and per-class failures (diagnose and measure only unless a ruling
   allows shipping) — ranked by error cost (Error-B first), then tester impact.

## §3 Executor ladder and the cycle
Build (code, tests, fixtures, corpus drafts) = Codex: `(caffeinate -dimsu codex exec -s workspace-write
-C <worktree> -m gpt-6.1-terra -c model_reasoning_effort="high" --json -o <final> "$(cat brief.md)"
< /dev/null > events.jsonl 2> stderr.txt &)`. Brief, events, final, stderr live in
<scratch>/ovn1121/<id>/. Every brief says: "if the spec conflicts with the repo, STOP and say where."
Exit classified OK / EXHAUSTED / UNAUTHENTICATED / FAILED from exit code + stderr + final.
Main loop (Claude): briefs, gates first-hand, review of the diff, commits by explicit path, PRs, merges.
Adversary on every PR touching the verifier = Claude Opus subagent, never Codex (reviewer ≠ author).
Fallback: Codex EXHAUSTED/UNAUTHENTICATED twice ⇒ Claude build subagents only if Sai pre-authorized it
in §0; otherwise that item is BLOCKED and the cycle moves to review/measurement work.
Codex output is testimony: the diff + a fresh first-hand test run are the evidence.

## §4 Gates (D-100 for any merge)
`&&`-chained; `cmd > out 2>&1; echo $?`; stage by explicit path; assert `git branch --show-current`
before every commit; never push to main; after merge check origin/main^{tree} == tested tree.
Merge bar: suite green on merged tree; gold md5 unchanged; Error-B not higher in any class; Error-A
movement stated; every fix proven red; adversary 0 blockers.

## §5 Breaker
Two consecutive cycles with unchanged diff and nothing in flight ⇒ halt, name the class, teardown, disarm.
Two consecutive failures of the same terminal class (e.g. EXHAUSTED) ⇒ halt that lane, name the class.

## §6 Teardown BEFORE disarm (disk)
Remove every ~/vibe-coding/Agents/ai-ovn1121-* and ai-overnight-1121 worktree once its branch is merged
or pushed; delete merged local and remote ovn-1121-* branches; `git worktree prune`; worktree .venv dirs
go with them; empty <scratch>/ovn1121/ after copying Codex token counts into the morning report.
Any dataset over 5 MB that need not live locally goes to Google Drive (Agent-Assure/overnight-2026-11-21/),
with its Drive link noted in the morning report. `du -sh` before and after, both recorded.

## Park list
Escalation #1 (anything that lets more claims pass vs main: C2-percent ship, hedge-window change, D-102
rows, hole b, allow-list additions) unless Sai's §0 reply rules otherwise; gold labels; install.sh; hooks;
SOUL.md; ~/.claude writes except the memory directory; anything outward.

## §2-A (apply verbatim) REVERSIBILITY; COST OF DELAY vs ERROR inverts at night; FMEA DETECTABILITY (name
the sibling); GOODHART (a corpus is an instrument, not the goal).
