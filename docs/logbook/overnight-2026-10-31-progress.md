# OVERNIGHT 2026-10-31 — progress
## Cycle 0 (22:2x IST) — Sai pre-AGREED in his message; armed
- State from code: main e92075b, 0 open PRs; branch hardening-2026-10-25 @ 0765405 (H1–H5 + U1),
  suite 1109/2/60, gold md5 unchanged, A 12/25, B 0/27. Disk 742Gi free.
- Hamming: the important problem is honest writing being refused (U1: 4/40 PASS) — every remedy
  there lets more claims pass, so it is Sai's ruling (Escalation #1), not tonight's work.

---
# MORNING REPORT — 2026-10-31→11-01 · DISARMED at DIFF ZERO (~23:3x IST), well before 07:30

## 1. DONE
| Item | Proof | Result |
|---|---|---|
| R31 adversary on H1–H5 | Agent-Assure/reports/RED-TEAM-R31.md | 0 blockers; 0 refused→grounded over 122 repo pairs, 230 usage claims, 32 probes |
| H5 withdrawn (R31-02) | `uv run python tests/usage_genres/run.py --base <ckout>` on main / H1–H4 / H1–H5 | PASS 4 / 4 / 0; claims grounded 57 / 51 / 13 |
| PR #25 merged under D-100 (28cb1cb) | `uv run pytest -q` → 1106 passed, 2 skipped, 60 xfailed; md5 calibration/labels-v2.csv = 6215b526…d171f; tests/test_measure_rates.py 3 passed; origin/main tree == tested head tree | Error-A 12/25, Error-B 0/27 unchanged |
| S1 diagnosed | Agent-Assure/reports/S1-BLANK-LINES-DIAGNOSIS.md; bisect: README with 'per'→'on each' GROUNDS | False alarm: hedge token "per" in the 5-token look-back crosses the sentence boundary (`_span_is_hedged`, `_SPAN_HEDGE_TOKENS`) |

## 2. NOT DONE
- R31-03 (heading padding bypasses near-copy bar 0.8, pre-existing on main) — a correct H5 needs draft provenance (Write/Edit records), not text similarity. Next: design brief.
- R31-04 denial variants ("That is a lie.", "Nonsense:", denial 6+ sentences back) — fail-closed, Claude's to do next run.

## 3. DENIED — nothing.
## 4. ONE-WAY DOORS / DECISIONS — Sai's (Escalation #1: each lets more claims pass)
- H1 misreads code (`delete=False` → denial "false"): restrict denial tokens to prose, not code spans.
- S1: bound the hedge look-back to the claim's own sentence, or narrow "per".
- U1: headings / code-fence lines / table headers scored UNCITED (17 of 40 honest drafts blocked by them alone).
## 5. UNKNOWNS
- Why "One JSON object per line [S1]." itself refuses (not the "per" look-back).
- H1–H4 cost on real retrieved web pages (usage set is AI-written, repo-sourced).
## 6. BUDGET — subagents from completion records: 145,144 + 179,152 (Oct 25) + 131,475 + 96,461 = 552,232 output-side; killed R31 attempt UNKNOWN. Main loop UNKNOWN exactly; estimate well under 2M of 5M.
## 7. WITHDRAWALS — 1: H5 (I shipped it to the branch; the usage set showed it refused honest copied drafts).
   Also corrected: instrument named feature_rows-v2.jsonl as the gold file; it is labels-v2.csv.
## 8. FRAMEWORKS — Moat asymmetry (Error-B unrecoverable) decided "merge H1–H4"; reversibility (revert restores main's exact behaviour) decided "withdraw H5, don't patch it at 23:00"; D-69 (word lists may only drive refusals) kept H1-narrowing and S1 fixes on Sai's list.
## Teardown: worktree ../ai-overnight-1031 removed, scratchpad emptied, cron f49d170d deleted. No datasets created.
