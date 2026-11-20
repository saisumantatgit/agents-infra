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
---

# MORNING REPORT — OVN-1121 (written 02:14 IST; budget and teardown lines updated at disarm)

Verdict: the goal was not met. The heading and far-denial fabrications still certify PASS, because Codex ran out of quota at 00:18 (until 26 Nov 13:52) and D-119 barred a Claude build fallback. The fabrication corpus did grow (PR #43, 224 drafts). The night's real output is the map of what the gate gets wrong: 42 fabrication families certify PASS on main, all reproduced first-hand. 20 of them break the product's own written promise ("PASS means traceable"), and those are bugs.

## 1. DONE

- **PR #43 merged (C2):** fabrication corpus v2, tests only, 224 drafts in 8 classes. Baseline 0/224 certified, control PASS 93. Proof: `cd Agent-Assure && uv run python tests/error_b_corpus_v2/run.py --base $PWD` → "drafts: 224 | fabrication GROUNDED (escaped): 0 | draft PASS (certified): 0". Suite 1427 passed, 2 skipped, 74 xfailed. Merge d8c2ec0; `origin/main^{tree}` equals the tested tree (TREE_MATCH).
- **Red-team rounds R45 and R46 (analysis):** 42 families certify PASS 100 on main d8c2ec0.
  - 35 were reproduced by my own scripts, with my own claim text and both controls.
  - 5 by re-running the agent's script with controls; 2 attack-only.
  - Reports: `Agent-Assure/reports/RED-TEAM-R45.md`, `RED-TEAM-R46.md`.
- **Classification (D-129):** `R45-R46-CLASSIFICATION.md`. Class T has 20 families, where the reader's claim is not an unbroken run of cited source text; these are bugs. Class S has 22: traceable text the source disowns, disclosed under ADR-008.
- **Measurements for your rulings:**
  - `C1-RULING-PACK-2026-11-21.md`: headings and denial-after-claim.
  - `ERROR-A-MAP-2026-11-21.md`: the 1,946 honest refusals by cause. Measured gains: hedge stop +351, C1u +286, C2 +69.
  - `R2-CLAUSE-PREFIX-MEASUREMENT.md`: a word-list-free frame test, honest cost 8/2,044 on a text model.
  - `R1-RENDER-FIRST-PARSER-NOTE.md`: markdown-it-py 4.3.0, MIT, verified on PyPI.
- **Ready-to-run briefs:** `docs/planning/briefs/` holds E1 (pronoun "made up"), E2 (headings), E3 (attribution past the window), and C2b (corpus classes for every R45/R46 family).
- **PR #44 opened, not merged:** tester-guide Known issues listing the Class T shapes. This is your call, because it changes what testers are told.
- **Every report was adversary-checked.** Four challenges, all came back corrected, all corrections adopted (D-122, D-123, D-129, plus the classification).

## 2. NOT DONE

- **C1, heading and far-denial fixes:** BLOCKED on capacity (Codex EXHAUSTED, D-121). Next command, after 26 Nov 13:52 or once credits are added: `(caffeinate -dimsu codex exec -s workspace-write -C <worktree> -m gpt-6.1-terra -c model_reasoning_effort="high" --json -o final.md "$(cat docs/planning/briefs/OVN-1121-E2-headings.md)" < /dev/null > events.jsonl 2> stderr.txt &)`. Same for E1, E3 and C2b.
- **C3:** nothing to close. C2 found 0 escapes; R45/R46 replace it.
- **Codex cannot commit in its sandbox** (git index.lock outside the workspace). The main loop commits for it, so this is a process note, not a blocker.

## 3. DENIED

- **The harness blocked one red-team agent's write** of its findings file ("subagents should return findings as text"). The agent did not work around it, and I wrote the file from its hand-back.
- **Nothing else was denied.** No action was routed to another session or identity.

## 4. ONE-WAY DOORS QUEUED (for you)

- **Buy Codex credits:** this is a payment, so I didn't. https://chatgpt.com/codex/settings/usage. Otherwise the quota resets 26 Nov 13:52.
- **Or authorise Claude Opus build agents for the fail-closed fixes** until Codex is back. One sentence from you, with a token cap. My recommendation is YES for D8 and E2, which are small and moat-relevant.
- **Merge PR #44** (tester guide), if you approve the wording.

## 5. DECISIONS WAITING ON YOU (each with my recommendation and why)

1. **C2 "N percent": YES.** +69 honest claims, 0 lost, 0 of 12 new attacks pass, re-measured tonight on current main, and it also closes N11.
2. **Build order once capacity returns:** Class T first, all fail-closed, inside the existing authority. R46 lists the order: D8 and D11 as cheap S-class refusals, E2/R3 headings and lists, the number parser fixes N7/N8/N10/N11, then render-first.
3. **R1, render-first parser dependency (Escalation #4, install change): YES.** It closes 6 families structurally. The library is MIT and pure Python with one MIT dependency.
4. **Label every finding and corpus class T or S, and report Error-B for T only: YES.** On the corpora today, Class T certified is 5/184 (v1) and 0/224 (v2), while 20 Class T families were found by hand.
5. **Hedge-window sentence stop: NO for now.** It frees 351 honest claims, but it raises certified fabrications 7→9 and newly PASSes 5 of 15 attack shapes.
6. **C1u list ordinals:** the records disagree. The 15 Nov pack and D-116 say ship-with-CEILING; my logbook line says NO. I still lean NO, because it keys on capitalisation. Settle which record stands.
7. **The CLAUDE.md Escalation #1 reading** (fail-closed = agent authority) is still unratified. Codex stopped on it, correctly. Ratify it or reject it.
8. **Whether PASS should promise support, not just traceability:** this supersedes ADR-008, so it waits for the five buyer interviews ADR-008 names. No action now.

## 6. UNKNOWNS

- **Unprobed surfaces:** families on surfaces R45/R46 did not try (currency words, multi-source figures, the relational branch beyond J-57…J-64).
- **The 8 newly refused claims under the clause-prefix rule are unchecked**, and the rule was measured on my text model, not the gate.
- **markdown-it-py determinism** was spot-checked, not audited.
- **The other lane holding Codex quota:** a Codex session started 23:27 in another repo. I don't know whether its usage exhausted the quota before C1 started.

## 7. BUDGET

- **Claude:** 1.99M new tokens of 10M sanctioned (ceiling 12M), counted as output plus cache creation, each message counted once. Main loop 0.53M (output 0.16M, cache creation 0.37M); 7 agents 1.46M (5 Opus: reviewer and four red-team lanes; 1 Sonnet: research; plus the reviewer's three rounds). Derived from the session transcript and the subagent transcripts since 2026-11-20 18:04Z.
- **Codex:** 1.22M input (1.15M cached) and 8.4k output, across 2 runs, from its events.jsonl. Then EXHAUSTED.

## 8. WITHDRAWALS

- **"The C2 templates are too short to test the whole-claim rule":** a probe showed one-word flips inside 29-token sentences are refused.
- **Family D was "a labelling problem; narrow the two-back rule":** the two-back rule decides 0 of 26, and the escapes are a lexical gap in R40 (D-122).
- **The paragraph-break cut for next-sentence denial:** it has an attack.
- **"Up to 1,167 (60%)" honest claims unlockable:** that summed refused counts. Measured gains are 706, or 36% (D-123).
- **"541, upper bound" for the hedge stop:** the gate's tokenizer gives 576 earlier-sentence cases and 351 freed.
- **"My C1u recommendation was NO", stated as settled:** the records disagree.
- **R45 recommendation 1 ("don't present PASS as a guarantee") as new work:** the guide already disclaims that.
- **"D7 and D8 are Error-B under any reading":** D7 is documented (README:200).
- **D7 in Class T:** moved to S.
- **Recommendation (a), "promise support now":** it would supersede ADR-008 without its evidence.
- **The "promise vs direction" contradiction:** the real gap is measurement (D-129).

## 9. FRAMEWORKS

- **Error-cost asymmetry and Goodhart** set the night: red-teaming over idling, and corpus numbers read as a floor, not a rate.
- **Contradiction-as-locator:** five times, each time a reviewer or a record disagreed with me.
- **Cost of delay vs error, inverted at night:** stop-and-record rather than routing around D-119.
- **Via negativa:** stopping red-teaming once more families could not change a ruling.
- **Chesterton:** ADR-008 before proposing to replace it.
- **CEILING:** block-level source mapping in R1.
- **Degradation under constraint:** briefs written so the builds start on capacity.
