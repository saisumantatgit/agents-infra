# usage_genres drift: committed results.json vs main 295438a

Method: harness (run.py, manifest, drafts, sources) fixed at 295438a; `--base` = each commit under test; results.json restored after every run. Per-run outputs: res-<sha>.json in this folder.

## Verdict
- Committed results.json is byte-equivalent (all 230 claims, all gates) to a fresh run on 385190f. So the file was honest for its frozen base; the drift is real engine change, not a stale file.
- Main 295438a: 4 PASS / 3 NEEDS_WORK / 33 FAIL (committed 4/5/31); authored grounded 50 (committed 57); GROUNDED segments 91 (committed 102). 11 segments differ, 2 drafts move NEEDS_WORK->FAIL (c03, c05).
- First-parent view: 9 of 11 enter via merge 28cb1cb (PR #25 hardening-2026-10-25; ce809fc itself, which added results.json, sits INSIDE that PR, based on 385190f). 2 of 11 enter via f58929e (PR #29 run-2026-11-04). Merges 6eb3d5c, c8743b3, 41a7e2e, 295438a: zero change.

## Bisect inside PR #25 (first-parent hides this)
385190f 4/5/31 | 82821cf (H1) 4/3/33 | ab18151 H2, 7bacc9b H3, d755f87 H4: same | 9662c48 (H5) 0/1/39 | 3c8d089 (H5 withdrawn) 4/3/33.
All 9 PASS-side losses flip at H1 (82821cf, "far and unlisted denials"); H2-H4 add none; H5 added 40+ more losses, fully reverted by 3c8d089.

## Per differing segment (committed GROUNDED -> now)
| Draft | Claim (start) | Now | First commit | Intended or Error-A |
|---|---|---|---|---|
| c01_code_copied | "By default the files are created in the directory returned by gettempdir..." | UNGROUNDED | 82821cf H1 (PR #25) | Error-A |
| c02_code_copied | "Passing delete=False to NamedTemporaryFile keeps the file..." | UNGROUNDED | 82821cf H1 | Error-A |
| c02_code_copied | "The SpooledTemporaryFile class keeps data in memory until max_size..." | UNGROUNDED | 82821cf H1 | Error-A |
| c02_code_copied | "then rolls it over to disk" | UNGROUNDED | 82821cf H1 | Error-A |
| c03_code_copied | "The interactive form, git rebase -i, lets the author reorder..." | UNGROUNDED (gate NEEDS_WORK->FAIL) | 82821cf H1 | Error-A |
| c05_code_copied | "The default index type is B-tree" | UNGROUNDED (gate NEEDS_WORK->FAIL) | 82821cf H1 | Error-A |
| c05_code_copied | "CREATE INDEX builds one unless another method is named with USING" | UNGROUNDED | 82821cf H1 | Error-A |
| c06_code_copied | "the server answers with status 304 when the resource has not changed" | UNGROUNDED | 82821cf H1 | Error-A |
| c07_code_copied | "The store is written to .assure/evidence-store.jsonl in the project..." | UNGROUNDED | 82821cf H1 | Error-A |
| t06_tables_copied | row "FAIL | score < 60 - checked first ..." | UNGROUNDED | b5893b0 prev_denial_stray (PR #29, f58929e) | Error-A, disclosed |
| t10_tables_paraphrased | heading "# Rainfall, reworded" | GROUNDED -> UNCITED (draft already FAIL) | 85a1510 OI-MOAT-19 (PR #29) | Intended side effect, disclosed |

## Intended vs unintended
- The mechanism of each commit is an intended refusal (fail-closed denial lookups; heading scoring). The 9 H1 losses are collateral Error-A: lexical denial tokens (`delete=False` -> "false" in next sentence; "not", "unless", "without" in neighbours). HARDENING-H1-H5.md states the CEILING ("over-refuses an unrelated same-sentence denial") but measured cost only on the gold set (12/25, 0/27 unchanged); it never ran usage_genres. First quantified in RED-TEAM-R31 R31-02 ("5 GROUNDED->UNGROUNDED ... H1/H2 lexical noise") and the "H5 WITHDRAWN" note (H1-H4: 57 -> 51 authored). Not documented per-claim; no fix planned.
- t06: RUN-2026-11-04.md item 2 reports it explicitly (Error-A, draft already FAIL). t10: item 1 reports it (NON_CLAIM->UNCITED, draft already FAIL); that item's "62->62 GROUNDED" counts scored segments, so it is not a loss there.
- Net: 0 widenings (no UNGROUNDED->GROUNDED anywhere); 0 PASS drafts lost. Cost is 2 drafts NEEDS_WORK->FAIL and 7 authored claims.

## Caveats
- Segment count reported as "11" matches; counting authored claims it is 7 (57 -> 50).
- Two manifest sources are real repo docs read from `--base` (README, ALPHA-TESTER-GUIDE); these are identical-or-immaterial across runs (3c8d089..295438a stable except the 2 above), but the harness is only fully frozen if those docs are frozen too.
- Recommended fix to the instrument: re-baseline results.json on 295438a and pin the frozen sha in FINDINGS.md; the H1 Error-A (delete=False, "not changed" tokenisation) is a standing open cost, not a regression to revert.
