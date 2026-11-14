# UNGROUNDABLE on short verbatim sources: ruling pack (2026-11-15)

Worktree `ovn1115-q3`, branch `ovn-1115-q3` (base `ef3ae1f`), not committed.

**Verdict:** the bug reproduces, and it is not in how sources are classified. The
R26-04 near-copy rule (the rule that refuses a source whose text is mostly the
draft's own text) treats an honest short source as the draft. Landed (fail-closed
only): the verdict, `evidence_basis` and the diagnostic now agree, and the hidden
fabricated figure is now flagged. **Held for Sai:** grounding the honest claim.
By text alone it is the same object as three R26-04 attacks, so it would let a
fabricator pass (Escalation #1, the rule that any change to the Error-A/Error-B
trade-off is Sai's call).

## 1. Repro (first-hand, worktree code)

Copy `t.py` from `/private/tmp/claude-501/ovn1115-q3/work/` and point it at
`uv run --project Agent-Assure python Agent-Assure/scripts/ground_check.py`. Result:

| Source text (claim = first sentence, cited [S1]) | Verdict on main |
|---|---|
| `Code source: <claim>. Other.` | GROUNDED |
| `<claim>. Other.` | UNGROUNDABLE, `no_cited_verbatim_source` |
| `<claim>. <long tail>` | GROUNDED |
| alpha `d5` (3 verbatim sentences of S5) | all 3 UNGROUNDABLE |
| alpha `d2` (90000 where S2 says 25000) | all UNGROUNDABLE; the figure is never flagged |

On every refused row, `evidence_basis` says "Checked verbatim against 1 cited source: S2".

## 2. Root cause

Chain: `main()` → `_self_source_ids()` → `ground()` → `evidence_basis()` / `support_diagnostic()`.

1. **The trigger:** `_self_source_ids` applies R26-04's `_near_copy_of_draft`. A
   `Read` source counts as the draft when **at least 80%** of its adjacent word
   pairs (bigrams) also occur in the draft (`_NEAR_COPY_BIGRAM_SHARE = 0.8`).
   Measured shares:

   | Case | Shared bigrams / source bigrams | Treated as the draft |
   |---|---|---|
   | min repro `<claim>. Other.` | 10/11 = 0.909 | yes |
   | `Code source: ` prefix | 10/13 = 0.769 | no |
   | d5 / S5 | 37/39 = 0.949 | yes |
   | d2 / S2 (with the wrong figure) | 42/46 = 0.913 | yes |
   | d1 / S1 | 31/39 = 0.795 | no (one bigram away) |

   An honest draft that quotes a short source almost in full meets the bar by
   construction. The rule's own `CEILING:` comment already names this Error-A
   (refusing an honest claim). The alpha store's `full_text_source=verbatim` was
   read correctly.
2. **The verdict:** `ground` removes the source from the set that may certify →
   no verbatim source left → `UNGROUNDABLE`. That return came **before** the figure
   check, so the wrong figure (90000) was never examined.
3. **The display contradiction:** `evidence_basis` received `self_source_ids` but
   ignored it in its citation branch. It rebuilt its own verbatim list, so it
   announced a check against the very source the verdict had excluded. This is
   the D-35 class: the report describes evidence the verdict did not use.
4. **The wrong reason:** `support_diagnostic` was given the store with S2 removed,
   so it reported "no cited verbatim source" on a source whose store line says
   `verbatim`.

## 3. Fix (landed in the worktree; one file, `scripts/ground_check.py`, +176/-65)

Systemic fix for points 2 to 4. Point 1 is held (section 7).

- **One certifying predicate:** new functions `_certifying_verbatim` and
  `_excluded_as_draft`. Both `ground` and `evidence_basis` call them. An AST guard
  (a test that reads the code's syntax tree) keeps it that way.
- **Inference kept apart from identity:** `_self_source_ids` is now
  `_self_source_ids_by_identity` (path, inode, digest, containment) united with
  `_near_copy_source_ids` (R26-04). It returns the same set as before. The CLI
  also passes `inferred_self_ids`: near-copy matches that no identity test made.
- **Figure unmasked, fail-closed:** when every cited verbatim source was excluded
  *by inference only*, and a figure (digits or spelled) is absent from their text,
  `ground` returns `UNVERIFIED_NUMBER`. Otherwise it still returns `UNGROUNDABLE`.
  This can never produce GROUNDED. A source *identified* as the draft (by path or
  digest) keeps `UNGROUNDABLE`, because its text is the draft's, which
  `test_a_draft_cited_by_PATH_cannot_certify_itself` pins. `inferred_self_ids`
  defaults to empty, so library callers get the old verdict.
- **Legible display:** `evidence_basis` names the excluded source and the reason:
  the 80% bigram rule or path/digest identity, and that a short source quoted
  almost whole looks the same as a copy. It lists only the sources actually
  checked. New diagnostic code `cited_source_is_the_draft`.
  **Docs follow-up, not done by me (docs are another agent's):**
  `references/grounding-failure-types.md` and the alpha guide should describe
  this code and the near-copy refusal.

## 4. Red to green

New file `tests/test_ungroundable_verbatim_short_source.py`, 7 tests. On unmodified
code (`--runxfail`): **6 failed, 1 passed.** The pass is a control: a figure that
IS in the excluded text must stay UNGROUNDABLE, so it is meant to pass on both.

| Test | main | fix |
|---|---|---|
| honest short verbatim source grounds | FAIL | **strict xfail, HELD** |
| fabricated figure in the near-copy shape reads UNVERIFIED_NUMBER | FAIL | pass |
| control: figure present in the excluded text stays UNGROUNDABLE | pass | pass |
| evidence_basis does not claim a check the verdict excluded | FAIL | pass |
| support_diagnostic names the draft | FAIL | pass |
| partial exclusion is named beside the sources checked | FAIL | pass |
| AST guard: one certifying predicate | FAIL | pass |

The strict xfail on the honest-grounding test goes red the day the rule changes,
which forces the twin attack (A03 below) to be re-read at that point.

## 5. Gates

| Gate | Baseline (main) | Fix (landed) | Option B (held, measured only) |
|---|---|---|---|
| Full suite | 1276 passed, 2 skipped, 60 xfailed | **1282 passed** (+6 new), 2 skipped, 61 xfailed | 8 failed (3 R26-04 moat tests plus 5 tests in the new file) |
| labels-v2.csv md5 | 6215b526… | **6215b526d03147295b003d7ccb0d171f** (unchanged) | unchanged |
| test_measure_rates.py | 3 passed | **3 passed, file untouched** | n/a |
| Error-A cells fp/tn | 12/13 | **12/13** | 12/13 |
| **Error-B cells fn/tp** | **0/27** | **0/27** (unchanged) | 0/27 |
| r36_probe | 4/34 | **4/34** (b1 to b4) | **5/34**: b5 `draft_headings_plus_source_headings` newly reproduces |
| usage_genres PASS / NEEDS_WORK / FAIL | 4 / 3 / 33 | 4 / 3 / 33 | 4 / 3 / 33 |
| usage_genres grounded (segments, authored) | 59, 48 | 59, 48 (`results.json` byte-identical) | 59, 48 |

`tests/usage_genres/results.json` was restored with
`git show HEAD:Agent-Assure/tests/usage_genres/results.json > …` after each run.
Option B leaves the gold corpus and usage_genres unchanged: neither one contains
the near-copy shape, so a zero change there is no measurement, not evidence of safety.

## 6. Self-attack: 15 drafts across main, the fix and option B

Harness: real files beside the draft, store lines from the CLI. Option B is the
fix with the near-copy rule disabled. Each cell shows target verdict / gate.

| # | Draft | main | fix | option B |
|---|---|---|---|---|
| A01 | alpha d2: 90000 vs source 25000 | UNGROUNDABLE / FAIL | UNVERIFIED_NUMBER / FAIL | UNVERIFIED_NUMBER / NEEDS_WORK |
| A02 | R26-04 #3: planted file holding only the fabricated claim | UNGROUNDABLE / FAIL | UNGROUNDABLE / FAIL | **GROUNDED / PASS** |
| A03 | planted file = claim + " Other." (the alpha min-repro shape) | UNGROUNDABLE / FAIL | UNGROUNDABLE / FAIL | **GROUNDED / PASS** |
| A04 | same, partial read | UNGROUNDABLE / FAIL | UNGROUNDABLE / FAIL | **GROUNDED / PASS** |
| A05 | copy of the draft one word off, whole read | UNGROUNDABLE / FAIL | UNGROUNDABLE / FAIL | **GROUNDED / PASS** |
| A06 | citing the draft file itself (path), stale text | UNGROUNDABLE / FAIL | UNGROUNDABLE / FAIL | UNGROUNDABLE / FAIL |
| A07 | near-copy file + genuine unrelated source | UNVERIFIED_NUMBER / FAIL | UNVERIFIED_NUMBER / FAIL | **GROUNDED / PASS** |
| A08 | spelled figure changed | UNVERIFIED_NUMBER / FAIL | UNVERIFIED_NUMBER / FAIL | UNVERIFIED_NUMBER / FAIL |
| A09 | near-copy file + haiku_summary source | UNGROUNDABLE / FAIL | UNGROUNDABLE / FAIL | **GROUNDED / PASS** |
| A10 | near-copy file, failed fetch | UNGROUNDABLE / FAIL | UNGROUNDABLE / FAIL | UNGROUNDABLE / FAIL |
| A11 | "Code source: " + claim + " Other." | UNGROUNDABLE / FAIL | UNGROUNDABLE / FAIL | **GROUNDED / PASS** |
| A12 | relational fabrication via near-copy file | UNGROUNDABLE / FAIL | UNGROUNDABLE / FAIL | **GROUNDED / PASS** |
| A13 | two fabricated claims backed by one planted file (d5 shape) | UNGROUNDABLE / FAIL | UNGROUNDABLE / FAIL | **GROUNDED / PASS** |
| A14 | digit figure changed (4.7 vs 4.2) | UNGROUNDABLE / FAIL | UNVERIFIED_NUMBER / FAIL | UNVERIFIED_NUMBER / FAIL |
| A15 | **baseline hole (J-35):** planted file padded below the 0.8 share | GROUNDED / PASS | GROUNDED / PASS | GROUNDED / PASS |

- **The landed fix:** 0 of 15 drafts move toward PASS. 2 verdicts change
  (A01, A14), both from one refusal to another refusal that names the cause.
- **Option B:** 9 of 15 fabrications go from refused to PASS (A02 to A05, A07, A09,
  A11 to A13).
- **A15, the gap on main itself:** the near-copy rule is defeated by padding the
  planted file with about 20% extra words. That is J-35 write-then-Read laundering,
  which is Sai's open item (Escalation #4) and is not changed by either option.
- **Coordinator lead (testimony, agrees with this trace):** the separate Error-A
  corpus build saw the same trigger, and saw that padding the sources made the
  rule fire zero times. Rows A11 and A15 show both sides of that.

## 7. Held option and recommendation

**Why there is no textual fix.** The honest minimal repro (source
`<claim>. Other.`) and attack A03 have **byte-identical stores and drafts**. Every
part of the verdict is a function of that text, so no rule that reads text can
ground one and refuse the other. A two-sided share (also requiring the source to
cover the draft) does not help either: d5 is a draft made entirely of its source,
which is exactly a copy.

| Option | Honest short sources | Fabricators | Cost |
|---|---|---|---|
| A. Keep the rule, land this fix | still refused, now with the stated reason | no change (0/15 move to PASS) | Error-A on honest drafts that quote short sources almost whole |
| B. Drop or loosen R26-04 | ground | **9/15 attacks PASS**; r36 goes 4 → 5; 3 moat tests go red | Error-B shapes, unrecoverable |
| C. Provenance: capture Write/Edit (and Bash-written files) in the hook, and refuse a Read of an agent-authored path; then retire the text inference | ground | closes A02 to A13 and also A15 | hook change (Escalation #4), plus a decision for stores that carry no provenance |

**Recommendation: land A now and rule on C, not B.** Why:

- **Against B:** it turns an Error-A into Error-B. The invariant ranks Error-B as
  unrecoverable, and A02 to A13 are measured passes, not hypothetical ones.
- **A is pure gain:** no verdict moves toward PASS, Error-B is 0/27 as before,
  and it ends the self-contradiction and the masked figure the tester flagged as
  High severity.
- **Only C separates the twins:** the honest source and the planted file differ
  only in who wrote the file. C is also the upgrade path the rule's own `CEILING:`
  comment names, and it would close A15, which main misses today.
- **What would change this:** evidence that real short sources are captured
  through a path the hook cannot see (for example hand-built stores like the alpha
  tester's) and are common. Then C alone leaves those users refused, and a
  documented "quote less than the whole source" workaround becomes the
  near-term answer.

**Load-bearing assumption:** that the stores in sections 1 and 6 are the shapes
real users produce. The trigger depends on source length relative to the quote,
so a corpus of real short sources would price option A's Error-A more accurately
than these 5 alpha drafts do.

**Classification:** systemic fix for the disagreement and the masked figure. For
the honest refusal, this is case resolution: legible refusal only, because the
root fix (C) is Sai's (Escalation #1 and #4). It stays open until he rules.
