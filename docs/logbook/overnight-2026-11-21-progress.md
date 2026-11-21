# OVN-1121 progress (checkpoint every tick; times from TZ=Asia/Kolkata date)

| IST | queue | action | Claude new tokens (cum.) | Codex tokens (cum.) | frameworks |
|---|---|---|---|---|---|
| 23:38 | C1–C3 open | §0 handshake: instrument drafted; baselines re-measured on main aa78683 (Error-B 7/280, Error-A PASS 5/336); awaiting AGREED | — | 0 | reversibility |
| 23:44 | C1, C2 in flight | AGREED (D-119; open asks unanswered ⇒ no widening, no Claude build fallback). Cron c2971578 armed (:07/:37, 00–07 IST). Codex gpt-6.1-terra high dispatched: C1 (wt ai-ovn1121-c1), C2 (wt ai-ovn1121-c2). Disk before: Agents 3.6G, volume 690Gi free | ~0.3M (est., measured at first tick) | in flight | reversibility, critical path |
| 00:24 | C1 in flight (run 2); C2 DONE | Tick 00:18. C1 run 1: Codex stopped on CLAUDE.md Escalation #1 conflict (correct stop; D-120a), re-briefed with Sai's AGREED as authority. C2 reviewed: probe with positive control confirms single-word flips inside long verbatim sentences FAIL (my "templates too short" hypothesis withdrawn). Gates first-hand green; PR #43 merged, main d8c2ec0, tree match. Side finding (Error-A, recorded only): an honest claim is refused when the next paragraph's unrelated sentence holds "not" (verbatim_but_next_sentence_denies across a paragraph break). | 0.20M (out 0.04M + cc 0.16M, 58 msgs) | C2 1.17M in (1.12M cached), 8k out; C1r1 45k in, 0.3k out | contradiction-as-locator, Goodhart, calibration (positive control) |
| 00:28 | C1, C3 BLOCKED (Codex EXHAUSTED x2 until 26 Nov 13:52); re-derived to analysis | D-121. C1 ruling pack written: Family H rule H1 measured (15/15 attacks caught; 3/5 honest Error-A PASS lost; 175/532 honest headings carry a novel word); Family D label contradiction (denial precedes the claim, backward pointer; 37 honest claims lost to the existing two-back rule). Side finding: 19/183 next-sentence refusals cross a paragraph. Opus adversary on the pack in flight. | measured next tick | 0 new (EXHAUSTED) | contradiction-as-locator, Goodhart, error-cost asymmetry, competence boundary |
| 00:29 | analysis | Error-A map written (reports/ERROR-A-MAP-2026-11-21.md): 1,946 honest refusals decomposed; 4 pending rulings address up to 1,186 (61%); hedge refusals: 541/682 look back across a full stop (upper bound, my tokenizer). Opus adversary on the C1 pack still running. Note: uv created Agent-Assure/.venv in the docs worktree (gitignored), removed at teardown. | measured next tick | 0 | Pareto, error-cost asymmetry, calibration |
| 00:41 | C1/C3 BLOCKED; analysis | Adversary verdict on the C1 pack: corrected (D-122). Two live Error-B families reproduced first-hand (E1 pronoun 'cooked up' after the claim; E2 source-word headings). Not built (no capacity under D-119), recorded as the morning P0. Pack and map rewritten; Family D diagnosis and paragraph-cut recommendation withdrawn. S-rule cost measured: honest PASS 9→2, 198/532 headings scored. | measured next tick | 0 | inversion, Swiss cheese, contradiction-as-locator, COST OF DELAY vs ERROR (night) |
| 00:49 | C1/C3 BLOCKED (Codex quota rechecked 00:48: still exhausted until 26 Nov 13:52) | Tick 00:48. Ready-to-dispatch briefs written for E1 (pronoun 'made up'), E2 (headings: S + closed label list, no-oracle reason) and C2b (corpus: denial-after-claim, source-word headings, controls WITH headings) in docs/planning/briefs/. Reviewer on the Error-A map in flight. | 0.57M (main 0.32M = out 0.08 + cc 0.24; reviewer 0.25M) | 0 (EXHAUSTED) | degradation under constraint, critical path |
| 00:50 | C1/C3/E1–E3 BLOCKED (capacity) | Adversary on the Error-A map: corrected (D-123). Third live Error-B E3 (attribution beyond the 5-token window) reproduced first-hand; brief E3 written. Map rewritten: measured gains 706 (36%); only C2 percent is ready to ship. | ~0.95M (est. from the last tick plus the reviewer's 0.26M; measured next tick) | 0 | Goodhart (refused ≠ gain), contradiction-as-locator (records disagree on C1u), FMEA detectability |
| 00:51 | R45 lanes A+B in flight | D-124: red-team round R45 dispatched (2 Opus agents, read-only). | measured next tick | 0 | error-cost asymmetry, Swiss cheese, opportunity cost |
| 00:59 | R45 lane A done, lane B in flight | Lane A: 11 Error-B families claimed (70 PASS runs); main loop reproduced 1 probe per family first-hand with a new claim string and both controls: 11/11 PASS 100 (A1 strikethrough, A2 footnote denial, A3 later-paragraph falsity, D1 J-22 evasion without 'that', D2 attribution after the claim/colon, B1 retraction words, B2 sarcasm, B3 question+rebuttal, C1 scope negation, E1 conditionals, G1 H4 label-list evasion). | measured next tick | 0 | Swiss cheese, via negativa (blacklists keep losing) |
| 01:08 | R45 DONE (analysis); builds BLOCKED | Lane B: 8 families; main loop reproduced 8/8 first-hand. R45 report consolidated (22 families, 3 root causes), D-125. | 1.00M (main 0.39M = out 0.11 + cc 0.28; reviewer 0.25M; lane A 0.13M; lane B 0.23M) | 0 (EXHAUSTED) | first principles (root causes), via negativa, Goodhart (corpora measure known holes) |
| 01:10 | R46 dispatching | D-126: R2 clause-prefix measurement committed; R46 lanes C (numbers) and D (absence/relational/citations) dispatched. | ~1.05M (main measured 0.39M at 01:07 + agents 0.61M; next tick measures) | 0 | first principles, Goodhart, reachability |
| 01:19 | R46 lane C done; lane D in flight | Lane C: 11 numeric Error-B families; main loop reproduced 11/11 first-hand (N4 only in narrower shapes). DENIED (agent level): the harness blocked lane C's FINDINGS write ('subagents should return findings as text'); the agent did not route around it; main loop wrote the file from its hand-back. Codex quota rechecked 01:18: still exhausted. | measured next tick | 0 | calibration (own controls), FMEA detectability |
| 01:24 | R46 DONE | R46 consolidated, D-127 (42 families total). Red-team rounds stopped deliberately: more families will not change the rulings needed. | measured next tick | 0 | via negativa, opportunity cost |
| 01:25 | analysis | D-128: 42 families split into 22 traceability breaks (bugs by the written promise) and 20 support breaks (Sai's product call). R45 rec 1 withdrawn as new work. | measured next tick | 0 | contradiction-as-locator, JTBD (what a tester acts on), Chesterton (why the scope field says what it says) |
| 01:29 | analysis | D-129: classification corrected by the adversary; T 20 / S 22; four withdrawals logged. | measured next tick | 0 | contradiction-as-locator, Chesterton (ADR-008), calibration |
| 01:30 | analysis | Corpora re-read as T/S: v1 T 5/184 certified, S 2/96; v2 T 0/224. The corpora cover 1 of the 20 Class T families found by hand. | measured next tick | 0 | Goodhart |
| 01:51 | parser research in flight (Sonnet) | Tick 01:51. Codex rechecked: still exhausted. | 1.76M (main 0.50M = out 0.15 + cc 0.35; 6 agents 1.26M) | 0 | — |
| 01:54 | analysis | D-130: R1 parser note, verified first-hand. | measured at morning report | 0 | reuse ladder (installed dependency vs write), CEILING |

| 02:18 | BREAKER cycle 1 of 2 | Codex still EXHAUSTED; nothing in flight; main unchanged d8c2ec0; open PR #44 waits on Sai. Remaining queue items all need build capacity or a Sai ruling. | 1.99M | 0 | via negativa |
| 02:31 | E1, E2 in flight (Codex) | D-131: breaker reset, Codex verified available; E1 and E2 dispatched. The morning report above is superseded at disarm. | 2.0M | in flight | critical path, reversibility |
| 02:54 | E1 committed (00d01f9, adversary in flight); E2 run 2 in flight | E1 gates first-hand: suite 1467 green; 34/40 new tests fail on main (proven red); v1 certified 7→5, escapes 11→5; v2 0; Error-A corpus unchanged; usage 4/40 unchanged; gold md5 unchanged; 1 v1 honest control lost. feature_rows-v2 was already stale on main (clean main regenerates the same md5 9b2b4e60), a pre-existing finding. E2 run 1 stopped at investigation (FAILED class 1 of 2), run 2 dispatched to implement. | ~2.2M (measured at next checkpoint) | E1 done; E2 in flight | error-cost asymmetry, FMEA detectability |
| 03:04 | E1 r2 + C2b in flight; E2 held (draft #45) | D-132. | measured next tick | 2 lanes | Chesterton (OI-MOAT-31), error-cost asymmetry, D-107 precedent |
| 03:22 | E1 r3 + C2b part 2 in flight; #46 merged | D-133. | measured next tick | 2 lanes | competence boundary (no lexical separation), Goodhart |
| 03:54 | E1 adversary r2 in flight; D8N review build in flight; #47 merged | D-134. | measured next tick | 2 lanes | competence boundary (authority scope), reversibility |
| 03:57 | E1 r4 (final) + D8N in flight | D-135. | measured next tick | 2 lanes | sunk cost (bound the rounds), FMEA detectability (tripwires record what is open) |
| 04:21 | E1 final adversary in flight; D8N held (draft #48) | D-136. | measured next tick | 0 Codex lanes | competence boundary (hook = Escalation #4) |
| 04:24 | E1 MERGED (#49); E2-lite in flight | D-137: the far-denial half of the goal is met on the corpora (denied_2back/3plus/after certified 0). | measured next tick | 1 lane | error-cost asymmetry |
| 04:51 | E2-lite r2 in flight | D-138: round 1 closed every heading attack and kept honest PASS, but cost 45 v2 controls through my brief's over-broad 'contained in'; narrowing. | measured next tick | 1 lane | FMEA detectability (the twin controls caught it), calibration |
| 06:01 | E2-lite r3 (bounded, cut-off 06:55) | D-139. | 2.62M (main 0.74M + 10 agents 1.87M) | 1 lane | COST OF DELAY vs ERROR (cut-off), degradation under constraint |
| 06:18 | E2-lite follow-up (IndexError → named error, CEILING notes) in flight, cut-off 06:40 | D-140: #50 merged; main 1a94d08 verified first-hand (suite 1585; v1 0/280; v2 0/269; v3 490/510; Error-A unchanged). Teardown started: 7 worktrees removed; merged branches deleted local+remote; remote branches kept for open PRs #44 #45 #48. | ~2.9M (measured at disarm) | 1 lane | reversibility |
| 05:19–05:50 | (no checkpoint rows written at these two ticks: a miss against the instrument; their work is in D-138/D-139) | | | | |
| 06:30 | close-out | E2-lite follow-up held as draft #51; teardown done; morning report final; D-141. | 2.84M | 0 | — |

---

# MORNING REPORT — OVN-1121 (final; supersedes the 02:14 draft, in git history at cf11ad7)

Verdict: the goal is met on the corpora, and both fixes are merged. Fabrications written as a document heading (E2-lite, PR #50), or disowned by the source around the claim (E1, PR #49), are no longer certified PASS. Fabrication corpus v1 went 7 → 0 of 280 certified, and v2 went 12 → 0 of 269. Honest-draft results are unchanged. Two new corpora now measure all 42 fabrication families found tonight. The 490 of 510 still certified on v3 are the families awaiting your rulings.

## 1. DONE (each proven by output the main loop saw)

- **PR #43 (C2): fabrication corpus v2.** 224 drafts, 8 classes, tests only.
- **PR #46 (C2b part 1): 3 T/S-labelled classes.** denied_after, and source-word headings in verbatim and reassembled forms.
- **PR #47 (C2b part 2): corpus v3.** All 34 R45/R46 families, 510 drafts, each with an honest twin. Baseline on main: Class T 270/285 certified, Class S 220/225.
- **PR #49 (E1): fail-closed.** "That was cooked up", "It was cooked up" and "The press made that up" no longer certify a disowned claim.
  - **Fabrications:** v1 7 → 5; v2 12 → 0.
  - **Honest drafts:** Error-A corpus and usage unchanged; 1 v1 honest control lost.
  - **Adversary:** 3 rounds; the last found 0 blockers across 2,494 corpus jobs and 218 probes.
  - **Latency:** none (0.84 s → 0.53 s, 200 sources).
- **PR #50 (E2-lite): fail-closed.** A draft heading that copies a sentence the source disowns, or asserts a predicate found in no source, is scored as a claim.
  - **Fabrications:** v1 `claim_heading` 5 → 0, so v1 is 0/280.
  - **Honest drafts:** 0 honest controls lost in any corpus; Error-A and usage identical to main.
  - **Latency:** at main's level (0.23 s, 200 sources).
  - **Adversary:** 3 rounds; the last found 0 blockers. Remaining honest-label refusals: 1/21 probes (`Lost and found`).
- **Every merge:** proven-red tests (they fail on main), the suite green on the merged tree, gold md5 unchanged, and `origin/main^{tree}` equal to the tested tree.
- **Final first-hand run on main `1a94d08`:**

  | Check | Result |
  |---|---|
  | Suite | 1585 passed, 2 skipped, 88 xfailed |
  | v1 | 0/280 certified |
  | v2 | 0/269 certified |
  | v3 | 490/510 certified |
  | Error-A corpus | PASS 5 / NW 156 / FAIL 175, 2044/3990 grounded (unchanged) |
  | Gold labels md5 | 6215b526d03147295b003d7ccb0d171f |

  Commands, from `Agent-Assure/`: `uv run pytest -q`, then `uv run python tests/<corpus>/run.py --base $PWD`.
- **Analysis**, in `Agent-Assure/reports/` (this PR):
  - RED-TEAM-R45 and R46: 42 families, all reproduced first-hand;
  - R45-R46-CLASSIFICATION: Class T 20 / Class S 22;
  - C1-RULING-PACK, ERROR-A-MAP, R2-CLAUSE-PREFIX-MEASUREMENT, R1-RENDER-FIRST-PARSER-NOTE;
  - the reviewers' evidence in `reports/ovn-1121-evidence/`.
- **Briefs:** `docs/planning/briefs/`.

## 2. NOT DONE

- **Draft #45, the full E2 heading rule:** superseded by #50. It costs honest PASS 9 → 3 and reverses OI-MOAT-31. Recommendation: close it.
- **Draft #48, D8N:** contrary evidence plus number parsing. It needs capture provenance, which is a hook change (Escalation #4), and as built it costs 94 honest claims.
- **Draft #51, E2-lite follow-up:** it makes some headings (`__ Bank fines`) crash the whole report and adds a flag parameter. Recommendation: refuse the heading instead of raising.
- **The other Class T fixes** need your rulings: render-first (R1), compose-before-grounding (R3), number agreement (R4). Once ruled, the next step is dispatching the matching brief to Codex.

## 3. DENIED

- **One harness block:** an R46 agent's findings-file write was blocked. It did not work around it; I wrote the file from its hand-back.
- **Codex quota:** exhausted from 00:18 to about 02:29. Builds were not routed to Claude (D-119). A peer relayed "Codex is back", and I verified that first-hand before resuming.
- **Nothing was rerouted.**

## 4. ONE-WAY DOORS QUEUED

- **PR #44 (tester guide, Class T list):** merge if you approve the wording.
- **Codex session logs from tonight:** 20 files, 21 MB; deletion command in section 10.

## 5. DECISIONS WAITING ON YOU (recommendation and why)

1. **C2 "N percent": YES.** +69 honest claims, 0 lost, 0/12 attacks pass, and it closes N11.
2. **R1 render-first dependency (markdown-it-py 4.3.0 and mdurl, both MIT): YES.** It closes 6 Class T families structurally (Escalation #4).
3. **Report Error-B for Class T only, and Class S as disclosed: YES.** Class T is 270/285 certified on v3.
4. **Hedge-window sentence stop: NO for now.** It frees 351 honest claims but opens Error-B.
5. **C1u list ordinals:** the records disagree (D-116 vs my logbook). Settle which stands.
6. **The CLAUDE.md Escalation #1 reading (fail-closed = agent authority): ratify or reject.** Codex stopped on it, correctly. Tonight's fail-closed builds outside C1 were held as drafts because of it.
7. **Close draft #45:** E2-lite supersedes it without E2's honest cost. What would flip it: a source-word heading attack E2-lite misses and E2 catches.
8. **Drafts #48 and #51:** see section 2.

## 6. UNKNOWNS

- **The 8 claims the clause-prefix measurement would refuse** are unchecked, and it ran on a text model.
- **E2-lite's lexical predicate test** can misread a title-cased noun compound.
- **markdown-it-py determinism** is spot-checked only.
- **Surfaces not probed:** currency words, multi-source figures, and the relational branch beyond J-57…J-64.
- **Codex quota:** whether another repo's Codex lane caused the exhaustion.

## 7. BUDGET

- **Claude:** 2.84M new tokens of 10M sanctioned (ceiling 12M), counted as output plus cache creation, each message counted once, from the session and subagent transcripts since 2026-11-20 18:04Z. Main loop 0.81M (output 0.27M, cache creation 0.54M); 11 agents 2.03M (10 Opus reviewers and red-team lanes, 1 Sonnet researcher).
- **Codex:** 15 runs; 48.8M input tokens, of which 47.5M cached (1.33M uncached), and 0.18M output, from events.jsonl `turn.completed`.

## 8. WITHDRAWALS

- **From the 02:14 draft, all stand:** the C2 template hypothesis; the Family D label diagnosis; the paragraph-break cut; "1,167 / 60%"; the "541" bound; C1u stated as settled; R45 recommendation 1 as new work; "D7/D8 Error-B under any reading"; D7 in Class T; recommendation (a); the overstated contradiction.
- **My E1 round-2 brief** contradicted round 1. Codex flagged it, and I ruled that the narrower rule governs.
- **My E2-lite brief's rule (a), "contained in",** cost 45 honest controls. Narrowed.
- **"E1 closes the heading classes":** not claimed. That was a side effect of the corpus's cooked-up sources.
- **Process mistakes:**
  - two unquoted heredocs stripped identifiers from two briefs (both runs killed and re-dispatched);
  - no checkpoint rows at the 05:19 and 05:50 ticks;
  - early rows carried an estimated token figure;
  - my scratch deletion removed the filled-in morning-report draft before I had written it into the log. I rewrote it from the text in the session; this is that rewrite.

## 9. FRAMEWORKS

- **Error-cost asymmetry and Goodhart:** red-team before fixing; corpora read as a floor; the T/S split.
- **Contradiction-as-locator:** every reviewer correction.
- **Chesterton:** ADR-008, OI-MOAT-31.
- **Cost of delay vs error, inverted at night:** bounded rounds, cut-offs, drafts rather than merges outside authority.
- **D-107 precedent:** narrow before merge.
- **FMEA detectability:** strict-xfail tripwires record each open hole.
- **Reversibility:** a revert row for every merge.

## 10. TEARDOWN (disk)

- **Worktrees removed (12):** ai-ovn1121-c1, c2, e1, e2, e2l, e2f, c2b, d8n, guide, mainchk, plus the two perf check worktrees. Their `.venv`s went with them. The docs worktree ai-overnight-1121 is removed after its PR merges.
- **Branches:** merged branches deleted locally and on GitHub (ovn-1121-c2, -e1, -c2b, -c2c, -e2l). Remote branches kept only for open PRs: ovn-1121-guide (#44), -e2 (#45), -d8n (#48), -e2f (#51).
- **Scratch:** 95 MB removed (briefs, events logs, probes, perf fixtures). The adversary reviews and red-team findings were copied first into `Agent-Assure/reports/ovn-1121-evidence/` (156 KB of text).
- **Disk:** Agents folder 3.6G before, 3.6G after; volume 690Gi free before, 704Gi after.
- **Drive:** nothing to move. The largest artefact kept in the repo is corpus v3 at 638 KB.
- **Queued for you (one-way door):** Codex's own session logs from tonight's 20 runs, 21 MB in `~/.codex/sessions/2026/11/20` and `/21`. They are needed for `codex resume`, so I left them. To delete them: `cd ~/.codex/sessions/2026/11 && for f in 20/*.jsonl 21/*.jsonl; do head -1 "$f" | grep -q ai-ovn1121 && rm "$f"; done`.
