# E2-lite: narrow heading refusal (2026-11-21)

E2-lite closes the five remaining v1 `claim_heading` certified fabrications while retaining all nine honest whole-draft PASSes in the two requested honest corpora. It does **not** close the two v2 source-word heading classes: each still has four certified fabrications. The v2 paired controls also expose a substantial cost that the honest whole-draft PASS count alone misses.

Authority is Sai's 2026-11-20 23:39 IST AGREED to C1, as recorded in D-119 and D-120 in the overnight worktree's ratification register: this heading change is fail-closed only. No commit was made. The main comparison is `origin/main` `375c828`, with the same corpus data and Python interpreter for both runs.

| Measure | Main | E2-lite | Full rule, draft PR #45 |
|---|---:|---:|---:|
| v1 `claim_heading` certified PASS | 5/15 | 0/15 | 0/15 (15/15 closed) |
| v2 `heading_from_source_words_verbatim` certified PASS | 4/15 | 4/15 | not independently measured here |
| v2 `heading_from_source_words_reassembled` certified PASS | 4/15 | 4/15 | not independently measured here |
| Honest whole-draft PASS, Error-A + usage genres | 9/376 | 9/376 | 3/376 (reported for PR #45) |
| v2 paired control PASS | 138/269 | 105/269 | not independently measured here |
| v3 certified PASS | 490/510 | 490/510 | not independently measured here |

The PR #45 figures are the comparison supplied in the brief, not an independent run in this worktree. `certified PASS` counts whole drafts, not only heading classifications. v1 overall certified fabrications fall 7 to 2 of 280; v2 remains 12 of 269. The v2 corpus includes 45 later-added cases beyond the original 224. Across v3's 34 classes, neither certified PASS nor escaped counts rose. No draft in v1, v2, v3, Error-A, or usage genres moved from non-PASS to PASS.

## What changed and what remains open

Only an existing uncited `NON_CLAIM` heading can be promoted; the added scored claim is therefore uncited and cannot turn a refusal into a PASS. Existing scored claims and both R42 denial readings remain intact. A matching source sentence uses the existing combined `_match_denied` decision, including the original reading first. Novel predicates use a closed refusal-only vocabulary. Its positional heuristic avoids treating the requested noun labels and examples such as `Recent arrests` and `Rebase cheat sheet` as predicates. It can miss a listed base-form verb in a medial position, and can still misread a noun as a verb. Missing vocabulary never causes a new pass. This is a lexical ceiling, not a POS tagger.

The four remaining PASSes in each v2 heading class already contain a citation and are scored on main; promotion of `NON_CLAIM` cannot change them. Their source uses a disowning expression outside main's existing denial readings. This work does not widen those readings. Verbatim disowned text is Class S; reassembled source-word headings are Class T, per R45/R46 classification. The v3 result is not a claim that its other known families are fixed.

Setext headings continue through main's existing decomposition and classification, with the additive promotion applied when a decomposed setext heading is `NON_CLAIM`. The setext examples checked during this work were already scored on main. R42's structural guard gains the new combined-denial consumer and still checks that it calls `_match_denied` rather than either reading alone.

The 33 lost v2 controls are 11 each in `denied_after`, `heading_from_source_words_verbatim`, and `heading_from_source_words_reassembled`. The sentence splitter can attach a source heading such as `Review notes` to the following denied sentence, making the matching draft heading newly scored. Those controls have no fabricated heading; this is honest-control cost, despite the corpus being a fabrication instrument.

## Honest heading changes

All newly scored heading occurrences in the 336 Error-A and 40 usage-genre drafts are listed below. All become uncited; repeated wording represents distinct drafts. No honest whole draft that passed on main lost PASS.

| Corpus | Draft | Newly scored heading |
|---|---|---|
| Error-A | `changelog_000` | `## Migration` |
| Error-A | `changelog_012` | `## Migration` |
| Error-A | `changelog_018` | `## New features` |
| Error-A | `howto_code_010` | `## Command` |
| Error-A | `howto_code_016` | `## Command` |
| Error-A | `howto_code_018` | `## Command` |
| Error-A | `howto_code_020` | `## Command` |
| usage genres | `c13_code_paraphrased` | `# Revalidation` |

Error-A whole-draft gates are PASS 5 → 5, NEEDS_WORK 156 → 155, FAIL 175 → 176; its authored grounded count remains 2,044/3,990. Usage genres remains PASS 4 → 4. A score can worsen without losing a PASS when the draft already had another refusal.

## Verification

- Full suite: `.venv/bin/python -m pytest -q` → **1440 passed, 2 skipped, 71 xfailed**, exit 0. Three previously strict-xfailed R40 heading tripwires are now ordinary passing tests; their unclosed siblings remain strict xfails.
- Proven red: copied `git show origin/main:Agent-Assure/scripts/ground_check.py` to `/private/tmp/e2-main-ground-check.py`, pointed the shared CLI test helper at that file, and ran the six E2-lite parametrized cases plus the R40 tripwires. All six new cases and all three promoted tripwires failed on main (9 failed, 11 expected xfails); the same tests passed on the changed checker. Cases cover an exact and a contained disowned source span, Unicode and mixed punctuation, three novel predicate forms, and noun-label controls.
- R42 guard, heading seam, E2-lite tests, and R40 ceiling tripwires: 21 passed, 11 xfailed. R42's main-path digest and main-first OR remain in force.
- The v1, v2, v3, and Error-A `run.py` runners were run with `--base` set first to a frozen main checkout and then to this worktree, `--out` and `--work` set to distinct `/private/tmp` paths, and `--jobs 4`; Error-A used `--no-ablate`. The usage runner was likewise run against both bases. Outputs were compared per draft and per class. Its generated tracked `results.json` was restored afterward.
- Regenerated v2 calibration features in `/private/tmp` with `--features-only`. They were byte-identical to a fresh main regeneration; the checked-in feature file differs from both fresh runs, so its existing drift is not attributed to this change. Authored gold labels were not touched.

No adversarial review beyond the listed tests and corpus comparisons is claimed. The lexical predicate ceiling, source sentence segmentation, existing denial vocabulary, and the remaining v2/v3 certified fabrications limit the result.
