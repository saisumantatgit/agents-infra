# E2 heading checks — implementation and measurement, 2026-11-21

**Status: implemented but NOT ready to merge.** The new cases pass, but the full suite has 49 failures, including legacy expectations and a broken grounded demo. These require migration and review. The rule is fail-closed relative to the existing classifier: source and label exemptions apply only to headings already classified NON_CLAIM; they do not reverse existing refusals. A setext heading adds a check without removing the existing decomposition. Sources must be captured verbatim, not failed, and not identified as the draft itself.

The closed list has a ceiling: a claim written entirely using label words, such as “Known issues”, can still be exempt. A missing word causes scoring. A POS tagger is the suggested upgrade. The refusal text does not enumerate words. Existing refusals still apply even to a copied source heading. Source heading matching normalizes NFKC, case, whitespace and edge punctuation. This is an intentionally conservative implementation: source and label exemptions cannot widen main's passes.

## Proof and measurements

Main means `origin/main` d8c2ec0. Each attack includes a separately grounded cited body as a non-vacuous control. `.venv/bin/python -m pytest -q tests/test_e2_headings.py` with `E2_GATE=/private/tmp/e2-main-ground-check.py` (created by `git show origin/main:Agent-Assure/scripts/ground_check.py`) gave **45 failed, 3 passed**: each attack parametrization was red, while all three honest controls passed. On the modified checker, **48 passed**. The setext tests additionally require a scored heading entry: main already refused these particular drafts by another path, so their gate verdict alone was not a red test. The copied-heading control uses “Project architecture”; “Copied heading” is already refused on main and exempting it would widen passes.

| Measure | Main | S alone | S + list |
|---|---:|---:|---:|
| Error-A corpus: whole draft PASS / 336 | 5 | 2 | 3 |
| usage_genres: whole draft PASS / 40 | 4 | 0 | 0 |
| Combined initially passing honest drafts | 9 | 2 | 3 |
| v1 fabrication drafts certified / 280 | 7 | — | 2 |
| v1 claim_heading certified / 15 | 5 | — | 0 |
| v2 fabrication drafts certified / 224 | 0 | — | 0 |

S alone was measured with the same modified checker and an empty label set, not by weakening any old refusal. List recovery is one of the seven drafts lost under S, leaving six lost; this is below the ruling pack's product-review threshold. The other two remaining v1 certified cases are denied-source shapes, not heading claims. These synthetic corpora are instruments, not prevalence estimates. Across the 336 + 280 + 224 paired drafts, no draft went from non-PASS on main to PASS here; this is an empirical check, not a general proof.

Among the 532 ATX lines in the 336 Error-A and 40 usage drafts, direct per-line classification found 195 already scored on main, 329 under S, and 318 under S + list: the list exempts 11 of S's scored headings and 123 additional lines are scored compared with main. This line-level method includes previously scored headings and differs from the ruling pack's 198 figure; it does not claim to reproduce that estimate. Setext lines were not present in this 532-line count.

## Calibration record (ADR-025)

| Measurement | Projection | Actual | Δ |
|---|---:|---:|---:|
| Error-A, gold (25 grounded) | main 0.480 | 0.480 | 0 |
| Error-B, gold (27 violations) | main 0/27 | 0/27 | 0 |
| Fresh regenerated feature rows vs fresh main | identical | identical | 0 rows |

`calibration.measure_rates` is n=52, single ratifier; 0/27 has a ~10.5% 95% upper bound. Gold MD5 remains `6215b526d03147295b003d7ccb0d171f`. Regeneration differs from the *checked-in* stale feature rows at q03 and q13; both differences also occur when regenerating main, so neither is caused by E2. q03 is gold grounded and is now refused; q13 is gold grounded and is now refused. The fresh baseline is 0.480 rather than the historical CR-007 0.400. The legacy bootstrap calibration also ran; its n=12 result is not the deployed gold rate.

## Verification and outstanding work

- Focused E2 + R42 structural guards: **52 passed**. The R42 digest was not re-pinned: the original denial path is unchanged and its existing pin passes.
- Full suite: **49 failed, 1436 passed, 2 skipped, 64 xfailed**. It ran before a final punctuation-normalization cleanup; focused tests were rerun afterward. Failures include old expectations that unlisted headings stay NON_CLAIM, strict xfails now passing, and the bundled grounded demo and dependent tester-tool golden tests. These must be adjudicated and migrated; no test was muted to hide them. The demo needs an honest heading or source heading and regenerated reviewed outputs. Re-run the full suite after migration.
- `bash Agent-PROVE/scripts/validate-structure.sh` could not run: this worktree has no Agent-PROVE directory (exit 127).
- Error-A corpus ran with `--no-ablate`; this measures whole-draft gates and authored grounding, not ablation-based cause attribution. Corpus runners and the two gold calibration commands used the project `.venv` without network. An independent Opus adversary round recommended by the ruling pack has not been run.
- No commit or push. The current changes and derived feature rows are left for review.
