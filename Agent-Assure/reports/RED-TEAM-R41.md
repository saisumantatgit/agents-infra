# RED-TEAM-R41 — pre-merge adversary, OVN-1115 Q3b (6f361f8 vs base ef3ae1f)

Date: 2026-11-15. Role: last gate on moat code (Opus). Read-only on `scripts/` and `tests/`.
Base reference copy: `git show ef3ae1f:Agent-Assure/scripts/ground_check.py > /private/tmp/claude-501/ovn1115-r41/gc_main.py`.

## Question

Is there any draft+store that 6f361f8 PASSes, GROUNDs, or scores higher, and ef3ae1f refuses?

## Verdict

**No. 0 BLOCKERs.** The change is refusal-only, by static argument and by 60,000 differential pairs plus three prior probe harnesses.

## Static reading of the diff

| # | Changed surface | Can it move a claim toward PASS? | Why not |
|---|---|---|---|
| 1 | `ground`: certifying list now `_certifying_verbatim(sources, self_source_ids)` | No | Same predicate, same three conjuncts, same order (`verbatim`, not self, not `failed`) as the inline list it replaced. |
| 2 | `ground`: new branch inside `if not verbatim:` | No | It returns either `UNVERIFIED_NUMBER` or `UNGROUNDABLE`. Both are refusals, and the branch runs only when nothing can certify. No `GROUNDED` return was added. |
| 3 | `_self_source_ids` split into `_by_identity` plus `_near_copy_source_ids`, unioned | No | In the base, the near-copy test sat mid-loop and only ever ran `matched.add(); continue`. No earlier check skipped a record without adding it. So the union is the same set by construction. The `draft_flat` input is identical (`_identity_flat(draft_text)`). The path, relative-basename, `samefile`, resolve, metadata digest, text digest and partial-containment tests are byte-unchanged (diffed). |
| 4 | `inferred_self_ids` (CLI: near-copy set minus identity set) | No | Read only by the new branch in row 2. It chooses between two refusals and never decides whether to refuse. Defaults to empty, which gives the old verdict. |
| 5 | Score denominator | No | `score_report` counts every non-`NON_CLAIM` claim. Both `UNGROUNDABLE` and `UNVERIFIED_NUMBER` fall outside `_NUMERATOR_VERDICTS` and both land in `retained_appendix`, so the score is unchanged and the gate is capped at NEEDS_WORK or below. The only verdict the gate reads by name is `UNVERIFIED_CITATION`, and the change never produces it or removes it. |
| 6 | `evidence_basis` and the new `support_diagnostic` value `cited_source_is_the_draft` | No | Display only. The gate reads only the verdict, the appendix and `has_unverified_citation`. No other script in the repo consumes either field (grep over `*.py` and `*.sh` outside tests and reports). |
| 7 | New calls to `numeric_ok` and `spelled_quantity_ok` on the excluded text | Crash only, never PASS | These calls run only in a branch that refuses anyway. A raise would crash the run (exit non-zero); the fuzz saw 0 crashes. |

## Side-by-side fuzz harness

The harness is `reports/r41_probe/diff_fuzz.py`. It loads both modules and calls each one's own `main()` in process with `--json`, so the real CLI wiring runs, including the branch's `inferred_self_ids`.

The grammar:
- **Drafts:** 1 to 3 claims, with figures (digits, comma-grouped numbers, percentages, millions, spelled-out numbers) or no figure, and an optional heading.
- **Markers:** cited, multi-cited or uncited.
- **Stores:** 1 to 3 sources.
- **Source kinds (20):** genuine; genuine with a changed figure; near-copy; near-copy with a changed figure; partial near-copy; short source quoted almost whole; absolute path match; relative-basename match; symlink; hardlink; metadata digest match; text digest match; summary; summary of the draft; failed fetch; failed fetch of the draft; empty text; partial Read contained in the draft; whole Read contained in the draft; irrelevant.

| Measure | Count |
|---|---|
| Pairs run (12 shards, seeds 101–112, 5,000 each) | **60,000** (23,953 single-source, 36,047 multi-source) |
| Each source kind sampled | 5,255 – 5,557 times |
| Branch PASS (harness is live) | 1,309 |
| **Branch better than base (gate, score, or any claim newly GROUNDED / ABSENCE_SUPPORTED)** | **0** |
| Gate differs | 0 |
| Score differs | 0 |
| Crash or input refusal on either module | 0 |
| Per-claim verdict differences | 3,163, all `UNGROUNDABLE -> UNVERIFIED_NUMBER` (the intended change) |

Exclusion paths, each checked one at a time on both modules (one claim, one source):
- **Still excluded:** absolute path, relative basename, symlink, hardlink, metadata digest, text digest, and a near-copy with the same figure. All read FAIL 0.0 / `UNGROUNDABLE` on both commits. Only the diagnostic changes, to `cited_source_is_the_draft`.
- **Summary and empty sources:** `UNGROUNDABLE` on both.
- **Failed fetch:** `UNGROUNDABLE` on both.
- **Genuine source (control):** PASS 100.0 on both.

## Prior probes re-run on the branch (r36, r37, r38)

| Probe | Result on 6f361f8 | Against base |
|---|---|---|
| `reports/r36_probe.py` (34 attacks plus controls, CLI) | 4/34 attacks reproduce; 0 broken controls | Base output byte-identical (diffed), so the 4 holes already existed and are not new |
| `r37_probe/harness.py` over cases c1–c6 (152 cases) | 0 BLOCKER, 0 "main passes, branch refuses" | 89 HOLE rows pass on BOTH commits, so they already existed |
| `r37_probe/fuzz.py` seed 37, n=10,000 | `branch_only_pass 0`, `main_only_pass 0`, crash 0 | — |
| `r38_probe/fuzz3.py` seed 38 (r38 grammar) and seed 39 (r37 grammar), n=10,000 each | `r38_pass_main_refuses` 0, crash 0 (208 and 323 passes) | The third module (2dc776b) was replaced by the ef3ae1f copy, so its columns compare base with base |

The probes hard-code `ai-overnight-1114` and `/private/tmp/claude-501/r3{7,8}/`. Repointed copies are in `/private/tmp/claude-501/ovn1115-r41/r37/` and `/r38/`; the originals were not edited.

Full suite on the branch: `uv run pytest` gives 1282 passed, 2 skipped, 61 xfailed.

## What was only read, not executed

- **Multi-claim `inferred_self_ids` subtraction:** a source that is both a near-copy and identity-matched. Argued statically (the set difference excludes it). The fuzz produced such stores (a draft-text source with a path match), but no row isolates them as a single targeted case.
- **Paths that cannot be reached from the CLI:** `ground` or `score_report` called with `inferred_self_ids` that are NOT a subset of `self_source_ids`. A library caller could pass this, but the new branch filters through `_excluded_as_draft`, which needs membership in `self_source_ids`. So extra ids can only change one refusal into another. Read, not fuzzed.
- **Not exercised by any probe:** `--session-id` enforcement and absence or relational claims backed by excluded sources. Neither touches the changed predicate except through row 1 above.

## Load-bearing assumption

The equality argument in row 3 assumes that `_identity_flat` is deterministic and that the base loop's near-copy check had no side effects. Both hold by reading. If either failed, the fuzz's 0 gate or score differences would be the backstop.
