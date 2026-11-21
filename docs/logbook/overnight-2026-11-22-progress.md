# OVN-1122 progress (instrument: docs/planning/OVERNIGHT-2026-11-22.md)

| # | IST | DIFF | What changed | New tokens (Claude, output + cache creation, de-duplicated) | Frameworks |
|---|---|---|---|---|---|
| 0 | 2026-11-21 22:45 IST | 2 (C1, C2) | Armed. Baseline on main 5e47ebf first-hand (instrument). | 0 (pre-run; measured from transcripts at close) | Reversibility; First principles |
| 1 | 2026-11-21 22:47 IST | 2 (C1, C2) | C1 builder (Opus) dispatched 22:51 in ai-ovn1122-c1; C2 builder (Opus) dispatched in ai-ovn1122-c2 (D-143). Both time-boxed to 00:20. | not measured yet (measured at close) | Critical path; Reversibility |
| 2 | 23:12 IST | 2 (C1, C2) | Both builders in flight (diffs growing; findings 7.7 KB / 3.7 KB). C2 removed a strict-xfail on R14-02 (spelled 'one million'): its tripwire went red because the fix closes it; assertion body unchanged — checked. origin/main still 5e47ebf. | not measured (at close) | FMEA detectability (tripwire flip read, not trusted) |
| 3 | 23:32 IST | 2 (C1, C2) | C1 round 1 back (D-144: -136 honest, not mergeable); round 2 in flight (findings 18 KB, after3/ present). C2 in flight (diff +276/-35; findings unchanged since 23:12 — checkpoint lag noted, diff growing so alive). | not measured (at close) | Asymmetry of error cost |
| 4 | 23:35 IST | 2 (C1, C2) | C1 round 2 back; my probe found a '|' evasion (D-145); round 3 in flight to 00:35. C2 in flight. | not measured (at close) | Swiss cheese; FMEA detectability |
| 5 | 23:39 IST | 2 (C1, C2) | C2 back (testimony: n7/n8/n9/n10 55→0, 0 honest lost, suite 1633 green). First-hand: 22 new tests fail on pristine main (red proven); gold md5 unchanged; committed b4d3905 on ovn-1122-c2 (a hook blocked restoring results.json over uncommitted work — correct; committed first). Suite + corpora re-running first-hand; Opus adversary dispatched on C2 to 00:40. DENIED (harness): C2 builder's findings-file write blocked; detail kept from its hand-back. C1 round 3 in flight. | not measured (at close) | Reversibility (commit on branch is two-way) |
| 6 | 23:47 IST | 2 (C1, C2) | C2 adversary: 2 blockers, confirmed first-hand (D-146); C2 round 2 to 00:45. C1 committed fe2057e (29 new tests red on main), gate run + Opus adversary in flight to 00:45. MISTAKE: my probe re-run wrote 6 store files into the c2 and mainchk trees via a relative path; removed, nothing tracked touched. | not measured (at close) | Contradiction-as-locator |
| 7 | 23:52 IST | 2 (C1, C2) | C1 first-hand gate: suite 1623/2/91 exit 0; v1, v2 runs exit 0; v3/Error-A/usage running. C1 adversary in flight. C2 round 2 in flight (working-tree diff +91/-53 on b4d3905). | not measured (at close) | — (no decision this tick) |
| 8 | 00:02 IST | 2 (C1, C2) | C1 round 4 committed bd1b37d (adversary probes 0/73 PASS; testimony); first-hand gate running. C1 → draft PR (D-148). C2 round 2 committed 81e7013; first-hand gate running; Opus adversary round 2 to 00:35. | not measured (at close) | Asymmetry of error cost; Goodhart |
| 9 | 00:10 IST | 1 (C2) | C1 → draft PR #53 (first-hand gate on bd1b37d: suite 1636/2/91 green, v3 450, Error-A identical). C2 round 2 gated first-hand green; adversary r2 found 2 punctuation evasions; round 3 in flight to 00:45. DIFF = C2 only (C1 owned by Sai, reason: unmeasured honest cost). | not measured (at close) | Asymmetry of error cost |
| 10 | 00:12 IST | 1 (C2) | C2 round 3 in flight (hand-back 00:45). Spend so far ~3.23M new tokens (main 0.30M + agents 2.93M; output + cache creation, de-duplicated by message id, since 22:34 IST). | ~3.23M | — |
| 12 | 01:34 IST | 0 open for the agent (C1 #53, C2 #54 owned by Sai) | Hard stop. Morning report written; teardown; disarm. | 3.65M final | Reversibility |

# MORNING REPORT — OVN-1122 (final, written 01:35 IST 2026-11-22)

Verdict: both fixes are built, gated first-hand and pushed, but nothing merged. Each fix closes its targeted fabrications on our corpora, with no honest claim lost there. C2 (figure parsing, PR #54) is held because its final adversary found three evasions that main shares. C1 (compose before grounding, draft PR #53) is held because it refuses an honest shape our corpora cannot measure. I recommend merging both.

## 1. DONE (each proven by output the main loop saw)

- **PR #54 (C2, R5 figure parsing), fail-closed, tree c31df39:** spelled numbers, space-grouped numbers, ranges, dates and decimals are compared as whole figures. Families N7, N8, N9 and N10 go from 55 certified to 0.

  | Check (first-hand, from `Agent-Assure/`) | main 5e47ebf | c31df39 |
  |---|---|---|
  | `uv run pytest -q` | 1585 passed / 2 skipped / 88 xfailed | 1659 passed / 2 skipped / 87 xfailed, exit 0 |
  | v1 / v2 (`tests/error_b_corpus*/run.py --base $PWD`) | 0/280, 0/269 | results.json byte-identical to main's |
  | v3 | 490/510 certified | 435/510 (n7, n8, n9, n10: 15/15/15/10 → 0; n11 unchanged at 15) |
  | Error-A corpus | PASS 5 / NW 156 / FAIL 175, 2044/3990 | results.json byte-identical (0 claims changed) |
  | usage_genres | 4/40 PASS | byte-identical |
  | Gold md5 | 6215b526d03147295b003d7ccb0d171f | unchanged |
  | Adversary probe sets, re-run by the main loop | — | 195 probes, 0 where C2 is more permissive than main |

  - **Fails on main:** 22 tests on pristine main in round 1, then more on each round's predecessor commit.
  - **Review:** 3 Opus adversary rounds. Round 1 found 2 real regressions (C2 passed what main refused): a date token skipped main's sign and % checks, and citation markers joined spelled runs. Round 2 found 0 regressions and 2 punctuation evasions. Round 3 found 0 regressions across 100 probes and 3 evasions (section 2).
- **PR #53 (C1, R3 compose before grounding), fail-closed, draft, tree bd1b37d:** a cited list item with no predicate is joined to the heading, lead-in or item that supplies one, and the joined reading must ground. Families F3, F7 and F8 go from 40 certified to 0.
  - **Suite:** 1636 passed, 2 skipped, 91 xfailed, exit 0.
  - **Corpora:** v1 and v2 identical; v3 490 → 450; Error-A and usage identical.
  - **Fails on main:** 29 of the new tests fail on pristine main.
  - **Review:** 1 Opus adversary round. It found 1 blocker (a wordless line between heading and item), fixed in round 4. Its probes now pass 0 of 73 against 29 on main (builder's run). It found nothing that C1 passes and main refuses.
  - **The main loop found the round-2 `|` evasion first-hand (D-145)** and checked the F3 per-claim verdict against the builder's report (D-147).
- **Records:**
  - ratification rows D-142 to D-150 in `docs/decisions/RATIFICATION-REGISTER-2026-08-30.md`;
  - the instrument `docs/planning/OVERNIGHT-2026-11-22.md`;
  - briefs in `docs/planning/briefs/OVN-1122-C{1,2}.md`;
  - evidence (216 KB of text) in `Agent-Assure/reports/ovn-1122-evidence/`.

## 2. NOT DONE

- **C2 evasions from round 3 (shared with main, so not regressions):**
  - a date followed by "-word", e.g. "03/04/2023-dated memo" grounds "04/03/2023-dated";
  - currency ranges other than $, e.g. "£40-£50" grounds "£50";
  - lakh and crore missing from `_SPELLED_NUMBER_WORDS`, so "two lakh pilots" grounds "two pilots".

  Next: a round 4 on branch ovn-1122-c2 with these three probes, under the same bar. The probes are in `reports/ovn-1122-evidence/C2-probes-adv3-r*.json`.
- **C1 open tripwires (strict xfail, CEILING in code):**
  - F2, a disowning heading over a verbatim claim; it needs heading meaning, which is author-controlled;
  - a bare name as a paragraph or blockquote under a heading;
  - multi-word names with a suffixed inner word;
  - tables nested in lists.
- **Not started:** C2's N1–N6 (they need your ruling, per R46), N11 (the pending C2-percent ruling), D9, and stretch items S0, S1 and S2.
- **Combined tree:** C1 and C2 were never measured merged together. They touch different functions, but run the full gate on the merge before landing the second one.

## 3. DENIED

- **C2 builder:** the harness blocked its findings-file write ("subagents should return findings as text"). The detail was kept from its hand-back. Nothing was rerouted.
- **Hooks:** a hook twice refused a file-restore over uncommitted work: once on a real restore, and once because this report's text contained the pattern. Both refusals were correct. I committed first and restored with `git show HEAD:<p> > <p>`.

## 4. ONE-WAY DOORS QUEUED (for you)

- **Merge PR #54:** `gh pr merge 54 --merge`, then `git fetch && git rev-parse origin/main^{tree}`, and check that it equals the tested tree `git rev-parse c31df39^{tree}`. Main has not moved since 5e47ebf, so the merge is a fast-forward tree.
- **Merge PR #53:** after #54, re-run the full gate on the merged tree, then `gh pr ready 53 && gh pr merge 53 --merge`.
- **Earlier items:** #44, #45, #48 and #51, plus the 21 MB of Codex logs, all from OVN-1121, are unchanged.

## 5. DECISIONS WAITING ON YOU (recommendation and why)

1. **PR #54 (C2): MERGE.** 0 regressions in 395 adversary probes and every corpus; 55 fabrications closed. The 3 open evasions are holes main already has. What would flip it: a probe where #54 passes and main refuses.
2. **PR #53 (C1): MERGE.** "## Criminals / - Alder Haulage [S1]" certifies an accusation PASS 100 on main, and that is unrecoverable. The honest loss is a bare-name list under a topic heading ("## Company / - Fenton Ltd [S1]"), which shows as NEEDS_WORK and is recoverable by stating the predicate. What would flip it: real tester drafts where such lists are frequent and honest.
3. **v3 f3 honest control:** "## Carriers / - Alder Haulage" is now refused. Either relabel it as Class T-refusable or accept the loss as disclosed. I recommend relabelling: "Carriers: Alder Haulage" is not traceable.
4. **The OVN-1121 list is unchanged:** C2 percent YES, R1 YES, T-only Error-B YES, hedge window NO, C1u record, Escalation #1 reading, #45 close, #48 and #51.

## 6. UNKNOWNS

- **Honest-cost frequency:** how often testers write bare-name lists under headings (C1's cost). It is 0 in our corpora, so unmeasured, not zero.
- **C2 private-use marks:** the "nothing newly accepted" argument rests on private-use marks never entering a qualifier set. Round 3 checked it by probe; no test pins it.
- **C1 + C2 combined:** not measured.
- **Tick gap:** the ticks at 00:47, 01:07 and 01:27 were delivered together at about 01:32, after the C2 round-3 adversary finished. Between about 00:35 and 01:32 no work happened. Cause unknown (it may be the scheduler's idle requirement). I did not check.

## 7. BUDGET

- **Total:** 3.65M new tokens of 8M sanctioned (ceiling 9.6M), counted as output plus cache creation, each message once, from transcripts since 2026-11-21 17:04Z.
- **Main loop:** 0.59M (output 0.09M, cache creation 0.50M).
- **6 agents, 3.06M:**
  - C1 builder (Opus): 1.18M;
  - C2 builder (Opus): 1.41M;
  - 4 adversaries (Opus): 0.48M in total, 0.11–0.14M each.
- **Codex:** none (Sai's instruction).

## 8. WITHDRAWALS

- **The serial plan:** "C2 only if C1 merged by 00:15" was replaced by parallel builds (D-143).
- **C2 scope:** "C2 = N1, N2, N4–N11 and D9" in my §0 reply was narrowed to N7–N10. R46 records that N1–N6 need your ruling, and I had not read that row before proposing.
- **The "C2 merges tonight" expectation** from D-148's row did not hold (D-150).
- **My F3 "contradiction" (D-147) was a misreading.** The v3 manifest marks the heading as the fabricated span; the bare name itself is UNGROUNDED.
- **Process mistakes:**
  - my first probe re-run used a relative store path and wrote 6 store files into two worktrees (removed; nothing tracked touched);
  - a mistyped heredoc stopped one brief before it started (no side effects);
  - at times I estimated the clock instead of reading it. Recorded times come from `date`.

## 9. FRAMEWORKS

- **Asymmetry of error cost:** drafts, not merges, where the honest cost was unmeasured (C1) or an in-scope evasion remained (C2).
- **"Never key on an author-controlled surface":** the `|` evasion.
- **Contradiction-as-locator:** "only refuses more" against the adversary probes; the seam was C2's early-exit branches.
- **Swiss cheese:** three adversary rounds, each finding a different layer.
- **Critical path:** the parallel build.
- **Goodhart:** a corpus showing 0 loss is not 0 honest cost.
- **Cost of delay vs error, inverted at night:** no merge after the hard stop.

## 10. TEARDOWN

- **Worktrees removed (3):** ai-ovn1122-c1, ai-ovn1122-c2 and ai-ovn1122-mainchk; their .venvs went with them. ai-overnight-1122 (this docs branch) is removed after its PR merges. No agent-created worktrees were found under .claude/worktrees.
- **Branches:** local ovn-1122-c1 and -c2 deleted. The remote branches are kept because they hold open PRs #53 and #54.
- **Scratch:** 57 MB removed (probe stores, gate outputs, briefs). Text evidence was copied first into `Agent-Assure/reports/ovn-1122-evidence/` (216 KB).
- **Disk:** the Agents folder was 3.7G at close and 3.6G after teardown. The volume had 689Gi free at the 22:38 start and 678Gi before and after teardown; the 11Gi drop came from outside these directories (not investigated).
- **Drive:** nothing to move. No artefact over 5 MB was created.
- **Cron:** 7e643f11 deleted in the close-out turn.
