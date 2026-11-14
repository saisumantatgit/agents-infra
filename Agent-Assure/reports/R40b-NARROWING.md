# R40b-NARROWING: honest cost of the R40 fixes on the error_a corpus, and the narrowing

**Verdict: all 54 lost claims came from ONE R40 sub-fix (the H4 "never took place" branch). Narrowing that branch recovers all 54: the corpus result is byte-identical to main (PASS 5 / NEEDS_WORK 156 / FAIL 175, 2044 of 3990 grounded). No R40 attack test reopened; no other sub-fix was changed or dropped.**

Worktree `ovn1115-q1`, branch `ovn-1115-q1` at a928dbe (R40 + main bb9b024). Not committed. References: `/private/tmp/claude-501/ovn1115-q1b/gc_main.py` (`git show origin/main:...`), full trees of origin/main and HEAD (pre-narrowing R40) under `/private/tmp/claude-501/ovn1115-q1b/{mainbase,r40base}/`. Probes and outputs: `/private/tmp/claude-501/ovn1115-q1b/{attr.py,probe/,out/}`.

## Attribution

Method (`attr.py`): load the R40 gate in-process, build each affected draft's store once with the real capture hook, then re-score with ONE sub-fix reverted at a time (module-attribute patches; the gate file was not edited for this). A lost claim is attributed to sub-fix X when reverting X alone re-grounds it. `_falsity_construction` was split into its 13 branches so H2-H6 are attributed per word family.

| Sub-fix | Honest claims lost (of 54) | Example | Attack shapes it closes |
|---|---|---|---|
| H1 same-sentence trailing denial | 0 | | "C, which is a myth.", "C (fabricated)." |
| H2 cooked/dreamed/trumped up, makes up | 0 | | "The account was cooked up." |
| H3 apocryphal, falsif\*, fabricates, lies/misinformation, invented/inaccurate (content subject), falsely | 0 | | "The account is apocryphal.", "It was all lies." |
| **H4 negator + "take place"** | **54** | "The planned follow-up wave never took place because funding ended." (18 sources), "The promised launch of the West showroom never took place in January.", "The security review of the data migration never took place last quarter." Each is a strong denial, so the R36 next-sentence and R38 paragraph rules refused every neighbouring claim ("Sales reached 606 thousand dollars in July", "The study ran for 5 years", ...). 31 drafts, 9 NEEDS_WORK → FAIL. | "It never took place." |
| H4 negator + "occur(s)", "not real" | 0 | | "The tale I tell did not occur.", "None of it is real." |
| H5 verdict verb + false | 0 | | "Reporters called it false." |
| H6 next-sentence siblings | (follows H2-H4; counted under H4) | | "C. The event did not occur." |
| H7 comparison copy | 0 | | Latin alpha, ZWSP, soft hyphen, dotless i |
| H8 forward denial up to 24 tokens | 0 | | "What follows in the rest of this short note ... did not occur." |
| H10/H11/H12 heading scope, labels, long lines | 0 | | "## Myths ... ### The collapse", "## Wrong claims", 13-24 token falsity line |
| H13 "what comes after/next/below" | 0 | | "What comes after is untrue." |
| H14 headline verbs/predicates | 0 | | "# Acme Stumbles", "# Acme Under Investigation" |

Every one of the 54 re-grounds when only the take-place branch is reverted, and no other single revert re-grounds any of them. Zero corpus cost for a sub-fix is a non-measurement for shapes the corpus does not contain (e.g. "did not occur" appears in no corpus or usage_genres source), not proof of zero Error-A.

## Decisions

1. **H4 take-place and occur: NARROWED.** Why: "X never took place <when/why>" is routine honest prose (31 of 336 corpus sources) and reports a non-event, not a falsity; the attack shape points at other content. New rule (`_event_negation_points`): the event negation is strong only when the clause ends at the verb ("It never took place.", "The collapse never took place.") or the words from the subject to the verb hold a pointing word (`_EVENT_POINTING_TOKENS` = `_DEICTIC_REFERENT_TOKENS` minus content-material nouns such as data/figures/document, or a demonstrative "that"). Applied to "occur" too: same shape, same honest risk, and every R40 occur attack (tale, event, what follows) keeps its pointing subject. A first cut used the full deictic set and recovered 46 of 54; the remaining 8 had subject "the data migration", so content-material nouns were removed (data does not "take place").
   CEILING (in the docstring): fail-open for a non-pointing subject plus an adjunct ("The launch never took place in May."), which is exactly main's behaviour; Error-A remains for a bare clause-final non-event ("The follow-up wave never took place.") and for a pointing word within six words before the negator.
2. **All other sub-fixes: KEPT unchanged.** Why: zero measured honest cost on the corpus, usage_genres and the R37 controls; narrowing them would trade attack coverage for no measured gain. Their R40 CEILINGs stand.
3. **Nothing dropped**, so no attack test moved to xfail.

New tests: `tests/red_team_moat/test_moat_r40b_event_negation.py`, 4 honest controls + 6 attack pins. Proven red: on HEAD a928dbe (R40 as first written), all 4 honest controls FAIL and 6 attacks pass; on origin/main bb9b024, 2 attacks FAIL (`event_subject_clause_final`, `story_did_not_occur_adjunct`; main certifies them) and the other 4 are refused by main's adjacency rules. On R40b: 10 passed.

## Corpus before / after

| Run | PASS | NEEDS_WORK | FAIL | Grounded of 3990 |
|---|---|---|---|---|
| main bb9b024 (committed results.json) | 5 | 156 | 175 | 2044 |
| R40 (a928dbe) | 5 | 147 | 184 | 1990 |
| R40b, first cut (full deictic set) | 5 | 154 | 177 | 2036 |
| **R40b, final** | **5** | **156** | **175** | **2044** |

The final `results.json` is byte-identical (`cmp`) to main's committed file; 0 claim or gate differences. The committed file was then restored from HEAD.

## Gates

All gates were run on the final code (after the second cut).

| Gate | Result |
|---|---|
| (a) Nothing passes that main refuses | Function level (`probe/mono.py`, main = origin/main bb9b024): seeds 1-4 x 30,000 sources = **11,085,788 match positions**, MONO_VIOLATION **0**, HEADER_VIOLATION 0, misalign 0, crash 0. Gate level (`probe/fuzz3.py`): R37 and R38 grammars, seeds 1, 2, 3, 7 x 20,000 = **160,000 drafts**, `r38_pass_main_refuses` **0**, crash 0. R37 harness c1-c6: **0 BLOCKER, 0 CRASH**. By construction too: the narrowing only shrinks a branch that main does not have, and main's own `_has_strong_denial` tests run before it unchanged. Limit: neither fuzz lexicon contains "place", so the take-place branch is covered by the logic argument and the new test file, not by the fuzz. |
| (b) Full suite | `uv run pytest -q`: **1381 passed, 2 skipped, 74 xfailed**, exit 0 (1371 + the 10 new R40b tests). Every existing test file is unchanged against HEAD (`git diff --quiet HEAD -- tests/`, with the new file excluded). No xfail was added. |
| (c) Calibration | `labels-v2.csv` md5 `6215b526d03147295b003d7ccb0d171f`; `tests/test_measure_rates.py` untouched (`git diff --quiet origin/main`). |
| (d) r36_probe | **4/34** reproduce (hole b only), 0 broken controls. |
| (e) error_a corpus | **5 / 156 / 175, 2044 grounded**, byte-identical to main; R40 was 5 / 147 / 184, 1990. All 54 recovered. `results.json` restored from HEAD. |
| (f) usage_genres | PASS **4**, authored grounded **51 of 171**. The generated `results.json` is byte-identical (`cmp`) to what origin/main bb9b024 produces from its own tree, and to what R40 (HEAD) produces. The brief's "48" is the ef3ae1f figure: current main already grounds 51, and the committed `tests/usage_genres/results.json` (13 lines differ) is stale relative to main's own gate. This is a main-side artifact issue, not an R40 or R40b delta; the committed file was restored from HEAD and not regenerated here. |

## Load-bearing assumption

That "X never took place / did not occur" with a non-pointing subject AND a following adjunct is honest far more often than it is an attack. An attacker can write "The collapse never took place in March." next to the claim and it now grounds, exactly as on main; R40 had refused it. If the red team shows that shape in use, the upgrade path is the clause parse named in the CEILING, not a wider word list.
