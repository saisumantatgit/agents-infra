# OVERNIGHT 2026-11-22 — instrument (OVN-1122; how to DERIVE work each cycle)

GOAL: by morning, a fabricated claim that the draft assembles from its own structure (a heading, a lead-in,
a continuation, a definition) or that changes a word or figure of the source run is no longer certified
PASS, so the PASS an alpha tester sees keeps the "traceable" promise as written, measured on our corpora.

Status: AGREED by Sai 2026-11-21 22:45 IST (D-142). Hard stop 01:30 IST 2026-11-22. Budget 8M Claude
new tokens (Sai: "Budget 8M"; output + cache creation, each message counted once by message id), ceiling 9.6M.
Tick 20 min (:07/:27/:47). Executor: Claude Code agents ONLY, no Codex (Sai, 2026-11-21: "till 1:30 use Claude
agent, Claude Code agent ... not codex agents"); overrides the Codex-primary rule for this run only.
Branch for docs: overnight-2026-11-22 (worktree ~/vibe-coding/Agents/ai-overnight-1122).
Branch per build item: ovn-1122-<id>, each in its own worktree ~/vibe-coding/Agents/ai-ovn1122-<id>.

## STOP RULE
Disarm ONLY at: hard stop · budget ceiling · circuit breaker · diff zero. An empty queue is NOT a stop:
re-derive the next queue from §2 and log the derivation. At 50% budget, log position. At 80%, stop starting
new items. Times in the record come from `TZ=Asia/Kolkata date` or git, never estimated.

## §1 Each cycle, derive state (code first)
1. Duplicate check: CronList shows one job; no other session runs an OVN-1122 tick.
2. `git -C ~/vibe-coding/Agents/agents-infra fetch -q && git log --oneline origin/main -5`; `gh pr list --state open`.
3. Worktrees and in-flight agents: `git worktree list`; running Claude agents (task notifications are truth;
   an agent is in flight until its completion notice arrives).
4. On main (or the merged tree), from `Agent-Assure/`: `uv run pytest -q > out 2>&1; echo $?`;
   `md5 -q calibration/labels-v2.csv` == 6215b526d03147295b003d7ccb0d171f;
   `uv run python tests/<corpus>/run.py --base $PWD` for error_b_corpus, error_b_corpus_v2,
   error_b_corpus_v3, error_a_corpus.
5. DIFF = §2 rows neither BUILT (gated green, PR open or merged) nor OWNED BY A NAMED HUMAN with the reason.
   Recompute it; never quote last cycle's number. Work the first row not DONE and not BLOCKED.

Baselines on main 5e47ebf, measured first-hand 2026-11-21 22:40-22:44 IST: suite 1585 passed / 2 skipped /
88 xfailed; gold md5 6215b526...; v1 0/280 certified; v2 0/269; v3 490/510 (C1 families: f2 15, f3 10, f7 15,
f8 15 of 15 each; C2 families: n1 15, n2 15, n4-n9 15/10/15/15/15/15, n10 10, n11 15, d9 15); Error-A 336
drafts PASS 5 / NW 156 / FAIL 175, grounded 2044/3990.

## §2 Queue (in order; each item's DONE is stated)
C1 R3 compose-before-grounding — Class T families F2, F3, F7, F8 (R45) and E2-reassembled headings: the claim
   the reader sees is composed from draft structure, and no single source run contains it. Ground the
   COMPOSED claim, not its fragments. Fail-closed only (can only move claims away from PASS).
   DONE = proven-red tests per family; v3 certified PASS for these families reduced (target 0) and no
   class rises in v1/v2/v3; Error-A movement measured and every honest claim lost justified one by one;
   structural guard (test_moat_r42_additive_structure) kept, re-pinned only with the reason in the PR;
   Opus adversary round with 0 blockers vs main; merged under D-100. If a family cannot close without
   refusing honest prose: CEILING + strict-xfail tripwire + report, not merged.
C2 R5 figure parsing — Class T families N7, N8, N9, N10 (R46 Root B): spelled numbers, space-grouped
   numbers, ranges, dates and versions. Same DONE bar. Built IN PARALLEL with C1 (D-143); merges after C1
   on the combined tree. N1–N6 (R4) need Sai's ruling per R46; N11 is the pending C2-percent ruling; D9 needs
   a controls re-run first — all three are re-derive candidates, not tonight's C2.
Stretch (only once C1 is DONE or BLOCKED; C2 first):
S0 #51 rework — a heading that E2-lite cannot align is REFUSED (scored as an ungrounded claim), never raised
   as an exception that kills the whole report; no flag parameter. Same DONE bar; the new PR names #51 as
   superseded (the draft is left open for Sai to close).
S1 D11 — do not ground on a partial read whose cut point falls inside the paragraph (Class S, near-zero
   honest cost per R45-R46-CLASSIFICATION rec. 4). Same DONE bar.
S2 Red-team the surfaces nobody has probed (currency words, multi-source figures, the relational branch
   beyond J-57…J-64): findings file + T/S label + corpus rows; fixes only via a later C-row.
Re-derive when all are DONE or BLOCKED: next candidates from open Class T rows in R45-R46-CLASSIFICATION.md,
   v3 per-family certified counts, then Error-A per-class failures (measure only) — ranked by error cost.

## §3 Executor ladder and the cycle
Build (code, tests, corpus rows) = Claude Opus subagent, one per item, `isolation: worktree` or a named
ai-ovn1122-<id> worktree, written brief in <scratch>/ovn1122/<id>/brief.md. Opus because this is multi-file
TDD on the moat, where a miss ships. Every brief says: "if the spec conflicts with the repo, STOP and say
where." The builder writes a findings file at start and fills it (checkpoint, not terminal-only).
Adversary on every PR touching the verifier = a DIFFERENT Opus subagent with full context, never the
builder (reviewer ≠ author). Measurement-only runs with fully specified commands = Haiku.
Main loop (Claude): briefs, gates first-hand, diff review, commits by explicit path, PRs, merges.
Agent output is testimony: the diff + a fresh first-hand test run are the evidence.
Same terminal failure class twice on one item (agent dies, refuted twice) ⇒ escalate once per the routing
table, else BLOCKED with the class named, move on.

## §4 Gates (D-100 for any merge)
`&&`-chained; `cmd > out 2>&1; echo $?`; stage by explicit path; assert `git branch --show-current` before
every commit; never push to main; after merge check origin/main^{tree} == tested tree.
Merge bar: suite green on the merged tree; gold md5 unchanged; Error-B not higher in any class of any corpus;
Error-A movement stated; every fix proven red; adversary 0 blockers. Authority for merging a fail-closed fix
tonight: Sai's AGREED to this file (D-120 precedent); anything that lets more claims pass is NOT merged.

## §5 Breaker
Two consecutive cycles with unchanged diff and nothing in flight ⇒ halt, name the class, teardown, disarm.
Two consecutive failures of the same terminal class ⇒ halt that lane, name the class.

## §6 Teardown BEFORE disarm (disk)
Remove every ~/vibe-coding/Agents/ai-ovn1122-* worktree once its branch is merged or pushed, and any
agent-created worktree under .claude/worktrees; ai-overnight-1122 goes after its PR merges. Delete merged
local and remote ovn-1122-* branches; `git worktree prune`; .venv dirs go with their worktrees; empty
<scratch>/ovn1122/ after copying evidence (<1 MB text) into Agent-Assure/reports/ovn-1122-evidence/.
Any dataset over 5 MB that need not live locally goes to Google Drive (Agent-Assure/overnight-2026-11-22/),
its link noted in the morning report. `du -sh ~/vibe-coding/Agents` and `df -h /` before and after, recorded.

## Park list
Escalation #1 pass-widening (C2 "N percent", hedge-window change, D-102 rows, allow-list additions); R1
render-first (new dependency, awaiting Sai); Error-B T-only reporting change; merging #44; closing #45/#48/#51;
gold labels; install.sh; hooks (D8 capture provenance); SOUL.md; ~/.claude writes except the memory
directory; deleting Codex session logs; anything outward.

## §2-A (apply verbatim) REVERSIBILITY; COST OF DELAY vs ERROR inverts at night; FMEA DETECTABILITY (name
the sibling); GOODHART (a corpus is an instrument, not the goal). §2-B and §2-C: the standing order text,
re-read before any consequential decision.
