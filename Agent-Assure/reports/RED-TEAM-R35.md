# RED-TEAM-R35 — adversary on run-2026-11-04b @ a4bc1f8 (D-104 heading exemptions)
Bound: branch must never PASS/ground an input 41a7e2e refuses. Status: in progress.

## Verdict: 0 BLOCKERS. D-104 bound holds on everything tried.

## Method
1. Code read: `git diff f58929e a4bc1f8` touches only `_header_asserts` (two new exemption helpers gate the two OI-MOAT-19 tests). `_header_asserts` has one caller (`_is_non_claim`, ground_check.py:1291). The exempted tests do not exist at 41a7e2e and everything before them is byte-identical, so branch-True ⊇ 41a7e2e-True structurally; all other f58929e changes are additive refusals.
2. Function-level differential (`fn_diff.py`): 41,573 heading bodies (3-token combinatorial over exemption words x claim words x casing/Cyrillic/ZWSP/full-width/punctuation, plus 40 hand attacks). Header-asserts violations (41a True, branch False): 0. `_is_non_claim` violations on `#`, `##`, bare forms: 0.
3. End-to-end gate differential (`e2e.py`, project .venv, worktrees w41/wf58): 39 headings x 13 draft shapes = 507 runs (ATX, ATX with [S1], setext `===`/`---`, `<h2>`, two headings + two claims, table containing the phrase, list item, bold, heading after claim, uncited body line repeating the heading, closed ATX, indented). Branch PASS where 41a7e2e refused: 0. Branch GROUNDED count > 41a7e2e: 0. Errors: 0.
4. Builder harness d104/diff.py re-run independently against fresh worktrees: branch-PASS & 41a-refused 0 (matches builder).
5. Full suite on branch: 1179 passed, 2 skipped, 60 xfailed; R34-04/05, line-welded, two-back, OI-MOAT-19 subset 54 passed.

## Findings
R35-01 (MEDIUM, not a blocker, within bound): exemptions re-open OI-MOAT-19 attacks that f58929e refused (41a7e2e also passes them). Repro (heading over one cited grounded sentence, PASS on branch, refused on f58929e): `# Record of fraud`, `# Scandal notes`, `# Insolvent overview`, `# Bankrupt sections`, `# Massive fraud notes`, `# Bank solvent, not fraud-tainted`, `# Acme, not bankrupt-declared`, `# This record cannot tell lies`. Causes: (a) label-final-noun rule exempts ANY claim word at i==0 in 2–3 word headings ending notes/overview/sections, not just a fixed idiom; (b) "Record of X" exempts any 2-word X; (c) "X, not Y-ed" exempts any hyphenated final participle; (d) "cannot tell" only checks the next two tokens. The CEILING comment names only "Widespread fraud notes"; it under-states (a)-(d). Fix if wanted: require exact whole-heading idioms (e.g. ("record","of","decisions")), or restrict the final-noun rule to non-claim-word heads.
R35-02 (INFO): prompt's combined attacks are refused on branch: "Track record: 300 died" (figure), "What changed — bank collapsed", "Fraud, not denied", "Bank collapsed notes", "300 dead overview" — none pass where 41a refuses. Casing/Cyrillic/ZWSP variants of exempt idioms (e.g. "TRACK RECORD", "Тrack record") are exempted like the plain form — consistent with fold, not a bound breach.
R35-03 (INFO): setext/HTML/bold/table shapes behave identically on all three trees for the bound question.

Load-bearing assumption: the e2e harness uses one source/claim pair; bound proof otherwise rests on the structural argument in Method 1.
Worktrees w41/wf58 removed at end.
