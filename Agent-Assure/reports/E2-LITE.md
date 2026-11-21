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

## Round 2 update (merged main `0c0ddc4`)

The round-1 figures above describe the older baseline and are superseded by this section. Rule (a) no longer promotes a short heading merely because it occurs inside a denied sentence. It checks the trimmed sentence or a substring of at least six tokens and requires a word from the existing E2 predicate vocabulary; rule (b) is unchanged. Promotion still applies only to headings classified `NON_CLAIM` by main, so this change cannot turn a main refusal into a PASS. Sai's D-119/D-120 authorisation remains limited to fail-closed changes. No commit was made.

**Important limitation:** the predicate check is lexical, not a main-verb parser. It misses unlisted verbs even in an exact sentence and may mistake a subordinate verb or noun for a main verb. In an extra probe, `## Review of where investigators found missing records` is a label, but is scored FACTUAL and the draft FAILs when a source says `The review of where investigators found missing records was thorough. That never happened.` Therefore the requested unconditional guarantee that a label is never scored by (a), and complete recognition of equal sentences and six-token runs with a main verb, are **not achieved**. The 45 controls below do not prove that general guarantee.

All measurements below use the project `.venv/bin/python`. Main values are from `origin/main`'s committed `results.json` at `0c0ddc4`; changed values were regenerated into `/private/tmp`, with the same checked-out corpus data. Existing modified result files were preserved. Certified means whole-draft PASS, not an assertion of general safety.

| Instrument | Main certified / controls PASS | Round 2 certified / controls PASS | Main PASS controls lost |
|---|---:|---:|---:|
| Error-B v1 | 5/280 / 189 | 0/280 / 189 | 0 |
| Error-B v2 | 0/269 / 138 | 0/269 / 138 | 0 |
| Error-B v3 | 490/510 / 510 | 490/510 / 510 | 0 |

Per-class control loss is **zero for every class**: v1's 18 classes, v2's 11 classes, and v3's 34 classes. In particular, v2 `denied_after`, `heading_from_source_words_verbatim`, and `heading_from_source_words_reassembled` each retain 15/15 main PASS controls (0 lost per class). No measured fabricated draft changes from non-PASS to PASS. The v3 escapes remain open.

Error-A: 5 PASS, 156 NEEDS_WORK, 175 FAIL, 2,044/3,990 authored claims grounded, matching main's committed summary. Usage genres: 4 PASS, 3 NEEDS_WORK, 33 FAIL; 61/200 scored segments grounded, matching main's committed measurements. Gold `calibration/labels-v2.csv` MD5 is `6215b526d03147295b003d7ccb0d171f`; regenerated features MD5 is `9b2b4e60140dda089a100c89099238eb`, matching the fresh-main value recorded in CR-014.

Verification: full suite **1580 passed, 2 skipped, 86 xfailed**, exit 0; focused E2 tests **52 passed**, exit 0. The new 45 actual corpus-control tests failed on the round-1 checker (45 failed, attack passed) and pass after narrowing. They pass on main by definition, so a demand that each control fail against main is incompatible with retaining main's behavior. Against the extracted main checker, the 45 controls passed and the new exact-copy attack failed (1 failed, 45 passed); all 46 pass on the changed checker. The four corpus runners and usage runner exited 0. `git diff --check` exited 0. The small probe above demonstrates a remaining honest-label false alarm despite these passing measurements.

## Round 3 update (main `0c0ddc4`)

The seven reported labels `Charges`, `Fraud`, `Crash`, `Arrests`, `Memory leaks`, `Code folding`, and `Fast charging` now remain `NON_CLAIM` and their grounded drafts PASS. Rule (b) requires a preceding subject-like word and excludes standalone gerunds and noun-only predicate entries; ambiguous two-word s-final forms require a capitalized predicate. This is a lexical approximation, not a part-of-speech parser: e.g. title-cased `Memory Leaks` can still be read as a clause, while lower-case `Plover folds` can be missed. A question-like label containing `found` may also be misread. The previous `Revenue Doubling` and `Quay Trust leaking` refusals are now open, as on main, and are retained as strict xfails. This change is therefore fail-closed relative to main, not relative to the round-2 branch. The main scoring path remains unchanged; only main's uncited `NON_CLAIM` headings can be promoted.

**Correction to round 2:** the `Review of where investigators found missing records` example was already scored on main, so it was not a new E2 false alarm. The actual additional honest-label costs were the single-word and compound labels identified in the round-3 review; the seven requested examples are covered here.

Source words are built once per report with an eligible heading. Rule (a) is skipped for headings without a candidate predicate, checks for the normalized span before parsing, and caches denial units by source text when needed. In a 200-source store with 40 sentences per source and 30 plain headings with grounded bodies, five serial CLI runs measured median **0.281 s on main and 0.294 s here** (1.05×); both returned PASS. The fixture has distinct source texts and ran with the same project interpreter after the other gates completed. This is one synthetic workload, not a general latency bound.

| Instrument | Main certified / controls PASS | Round 3 certified / controls PASS | Main PASS controls lost |
|---|---:|---:|---:|
| Error-B v1 | 5/280 / 189 | 0/280 / 189 | 0 |
| Error-B v2 | 0/269 / 138 | 0/269 / 138 | 0 |
| Error-B v3 | 490/510 / 510 | 490/510 / 510 | 0 |

No class rose in certified or escaped counts, and no fabricated draft gained PASS compared with main's committed results. V1 `claim_heading` remains 0/15 certified (5/15 on main). Error-A: PASS 5, NEEDS_WORK 156, FAIL 175, with 2,044/3,990 authored claims grounded. Usage genres: PASS 4, NEEDS_WORK 3, FAIL 33; 61/200 scored segments grounded, with no gate changes versus main. Gold labels MD5 remains `6215b526d03147295b003d7ccb0d171f`.

Full suite: **1585 passed, 2 skipped, 88 xfailed**; focused tests: **18 passed, 13 xfailed**. The seven label tests failed on the starting round-2 branch and pass here; they also pass on main, necessarily, so cannot be proven red against main. With the extracted main checker, the five retained attack tests failed, seven label tests passed, and the gerund case xfailed; the focused tests pass here. The Error-B v1/v2/v3 and Error-A runners used `--out` and `--work` under `/private/tmp`, `--jobs 4`, and `--no-ablate` for Error-A; usage output was redirected to `/private/tmp`. All runners exited 0. No commit was made.
