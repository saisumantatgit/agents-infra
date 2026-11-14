# RED-TEAM-R44 — final pre-merge adversary, branch ovn-1115-q1 @ 813e5d9 vs origin/main

Question: is there any draft+store that HEAD PASSes/GROUNDs or scores higher where origin/main refuses?

## Verdict
**0 BLOCKER at 813e5d9, by proof and by measurement.** HEAD never PASSes, GROUNDs or scores higher than origin/main fefb9c5 on any input tried: 281,000 fuzz pairs, 150 r37 cases and 280 Error-B drafts plus their controls. The proof covers the paths outside the denial path too, not only `_match_denied` (section 1).

- **Load-bearing assumption:** the AST diff (section 1) is the whole behavioural delta. That holds only if nothing outside `ground_check.py` changed for the gate. `git diff --stat origin/main HEAD -- Agent-Assure/scripts` shows 1 file. `capture_core.py`, `capture_hook.py` and `hooks/` show no diff.

## 1. Changed paths outside `_match_denied`

**Method:** AST diff of every top-level def, class and module constant, HEAD vs origin/main fefb9c5, docstrings stripped (`/private/tmp/claude-501/ovn1115-r44/astdiff.py`, `astdiff2.py`).

- **Changed bodies:** exactly 4. `_UnitContext` (adds `suffix`, default `()`), `_anchor_sentence_covers`, `_contained_with_matching_polarity`, `_header_asserts`. 0 removed, 60 added names, 0 module constants rebound, 0 in-place mutations of module constants (`.add/.update/...` on `_UPPER` names), 0 `global` statements. No other function, including the splitter, `_source_unit_contexts`, `_unit_denial_reason`, `ground`, `score_report`, `classify`, `decompose`, differs from main.
- **`_header_asserts` (classification):** `_header_asserts_main` is AST-identical to main's `_header_asserts`; HEAD's is `main OR r40 OR (view-copy main OR r40)`. So HEAD NON_CLAIM implies main NON_CLAIM. The only new outcome is a heading main treats as NON_CLAIM being scored on HEAD. Its only caller is `_is_non_claim`, whose header branch returns False first for any heading with a citation or a number, so a promoted heading always has zero citations. In `ground()`, an uncited non-NON_CLAIM claim ends in UNVERIFIED_RELATION, UNVERIFIED_ABSENCE (J-97: ABSENCE_SUPPORTED is mapped to UNVERIFIED_ABSENCE) or UNCITED. None of these is in `_NUMERATOR_VERDICTS`. Claims are scored independently in `score_report`, so promotion can only add a retained violation: the score goes down, and a vacuous NEEDS_WORK becomes FAIL. **R42's Attack 4 holds by proof.**
- **Empirical check of the above** (`/private/tmp/claude-501/ovn1115-r44/hp/heading_probe.py`, 10 drafts through both CLIs, including an uncited absence heading with a two-query store and a Latin-alpha heading that only the comparison copy promotes): 0 HEAD-better. Every promoted case went down: NEEDS_WORK 100 to FAIL 0 (5 cases), PASS 100 to FAIL 50 (2 cases).
- **The two consumers:** both now iterate `_denial_units(source_text)` and read `unit.main.tokens`. `unit.main` comes from main's own `_source_unit_contexts` (unchanged), so they see the same units, the same tokens and the same candidate starts. The refusal test is `_unit_denied(unit.main, i) or <R40>`, a superset of main's. The result can only make `return True` (grounding) rarer: in either function, HEAD True at unit k implies main True at or before unit k. Both are positive conjuncts only. `_contained_with_matching_polarity` is called only from `_claim_contained_verbatim`, and that and `_anchor_sentence_covers` are called only from `t1_verbatim`, whose only use is `ground()` line 6439 returning GROUNDED. Neither is read in a refusal sense anywhere.
- **Splitter parity:** `_source_unit_contexts_r40` splits each sentence on `\n+` and then on `;|[()]`, dropping blank pieces. Main splits on `\n+|;|[()]` and drops blank pieces. These give the same pieces, and `_denial_units` raises `RuntimeError` if they ever differ. That exception is uncaught (main() catches only OSError/ValueError), so it is a crash with exit code 1, never a report. It cannot produce a PASS. No crash was seen in any run below.
- **Comparison copy:** `_comparison_view` feeds only `_header_asserts` (it can only promote) and `_view_unit_contexts`, which is read only inside `_r40_match_denied` (it can only refuse; alignment failure counts as denied).

## 2. Merge seam with PR #40 display fields
- **Display region:** the PR #40 refusal-reason code (`verbatim_refusal` and helpers, HEAD lines 7250-7400 vs main 6398-6548) is byte-identical. It still calls main's `_source_unit_contexts` and `_unit_denial_reason`. It runs after the verdict is fixed (`score_report`) and writes only `evidence_basis` and `support_diagnostic`.
- **`_UnitContext` fields:** `paragraph_denied`, `heading_denied` and `sentence_index` keep main's defaults. `_source_unit_contexts_r40` does not set them, but no verdict rule reads them (grep of `_unit_denial_reason`/`_unit_denied`: 0 reads), and display reads only `unit.main` contexts.
- **Display gap (not a verdict issue):** a claim refused only by the R40 reading gets no R40-specific reason text, because display uses main's rules. This is Error-A legibility only.
- **Structure guard:** `tests/red_team_moat/test_moat_r42_additive_structure.py` gives 4 passed at 813e5d9.

## 3. Fuzz re-runs against origin/main
**Harness setup:** copies were repointed to the fefb9c5 reference at `/private/tmp/claude-501/ovn1115-r44/probe/`. R42's copies pointed at the 746f337 file, which differs. Outputs are in `/private/tmp/claude-501/ovn1115-r44/out/`.

| Run | Pairs | HEAD better than main | Crashes / non-report diffs | Other |
|---|---|---|---|---|
| diff_fuzz42, seeds 1-8 x 8,000 | 64,000 | **0** | 0 | claim-count diff 0; all 6,515 verdict diffs are GROUNDED to UNGROUNDED; gate diff 2,337 |
| r41 diff_fuzz, seeds 1-4 x 8,000 | 32,000 | **0** | 0 | 0 verdict diffs |
| cutseam_fuzz, seeds 1-5 x 5,000 | 25,000 | **0** | 0 | branch_worse 3,170 |
| r38 fuzz3, grammar r37, seeds 1,2,3,7 x 20,000 | 80,000 | **0** (`r38_pass_main_refuses` absent = 0) | 0 | main-pass-HEAD-refuses 869 |
| r38 fuzz3, grammar r38, same seeds | 80,000 | **0** | 0 | main-pass-HEAD-refuses 558 |
| r37 c1-c6 | 152 cases | **0 BLOCKER** | 0 CRASH | 43 HOLE = PASS on both (pre-existing on main); 46 ERRA? = main PASS, HEAD refuses |

fuzz3 was run with B = M = the fefb9c5 copy, so its "2dc" column reads as "main".

## 4. Error-B corpus
**Runs:** `tests/error_b_corpus/run.py`, once with `--base` set to this worktree and once with `--base` set to a `git archive origin/main` export. Both used `--out` into `/private/tmp/claude-501/ovn1115-r44/out/`, so the committed `results.json` was never written; `git status` shows only this report as new.

- **Same draft set:** 280 drafts on both sides, identical ids.
- **No HEAD gain on any draft:** 0 drafts with a higher gate, 0 with a higher score, 0 newly escaped fabrications, 0 controls with a higher gate, 0 drafts that PASS on HEAD without passing on main.
- **Totals:** certified PASS HEAD 7 vs main 20; escaped 11 vs 36; control PASS 190 vs 195. These equal R42-FIX's numbers.
- **Error-A cost, already disclosed by R42-FIX:** 5 controls stop passing on HEAD.

## What was only read, not executed
- **Proof by reading:** the argument that a promoted heading is always uncited and never reaches a numerator verdict (`_is_non_claim` header branch, `ground()` order, `_NUMERATOR_VERDICTS`) is a reading of the code. The heading probe tested 10 instances of it, not all shapes.
- **Splitter parity by reading:** the claim that main's split equals the R40 split was read, not fuzzed directly. The `RuntimeError` guard was never triggered in any run.
- **Not run:** the full pytest suite (only the 4-test structure guard was run), the Error-A corpus and r36_probe.
- **Not inspected:** callers outside the gate (calibration runner, capture hook) and how they handle a gate crash.
