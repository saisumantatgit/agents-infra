# RED-TEAM-R31: adversarial review of hardening-2026-10-25 (H1-H5, 82821cf..9662c48) vs main e92075b

**Verdict: claim UPHELD with a qualifier. 0 BLOCKERs (no draft+store found that the branch PASSes and main refuses); 1 LOW non-monotone path (R31-01, masked); large Error-A collateral (R31-02); several pre-existing holes still open (R31-03..06).**

Method: (a) reading the diff of every changed decision path; (b) differential CLI runs, main worktree (detached e92075b) vs branch, over 122 draft x store pairs found in the repo plus tests/usage_genres (40 drafts, 230 claims); (c) 32 perturbation/bypass probes (`w/probe.py`, case files `w/cases1p.json`..`cases5.json`, outputs `w/p1p.out`); (d) branch pytest: 1109 passed, 2 skipped, 60 xfailed, 0 failed.

## Monotonicity analysis (why no BLOCKER)
- **H1/H2/H4 (`_contained_with_matching_polarity`, `_anchor_sentence_covers`):** `_source_unit_contexts` produces exactly the same units, in the same order, as `_source_units` (same `_split_sentences` + same `\n+|;|[()]` split). Each loop now only adds an extra `continue`/conjunct (`_unit_denied`); the list-to-set change of `windows` does not change membership. Both functions are strictly narrower.
- **H3 (capture_core):** can only turn "ok" into "failed". Every consumer of "failed" in ground_check either drops the record from an ANY-grounds set (ground() `verbatim`, numeric_ok) or conjoins (absence chain runs both the full and the content-only population and requires both). Monotone.
- **H5 (`_self_source_ids`):** marks more Read records as self. In ground() the self set only shrinks `verbatim`, and every later rule is ANY-grounds or figure-in-some-source, so this is monotone. The single non-monotone consumer is the absence denominator (R31-01).
- **Executable:** 122 repo pairs: 5 differ, all GROUNDED->UNGROUNDED, 0 widen. usage_genres: 0 claims widened. 32 probes: 0 widened.

## Findings

### R31-01: LOW (latent, masked by ADR-009): H5 moves the absence gate denominator. NEW. Downgraded from MEDIUM in the partial.
Repro `w/cases2.json`: draft "There is no benchmark of the widget controller."; 2 exa fetches whose queries contain "benchmark"; 1 Read `benchmark-widget-controller-copy.md` = draft + 6 filler lines.
main `searches_do_not_qualify`; branch `searches_would_qualify`; verdict on both UNVERIFIED_ABSENCE / FAIL (ground() always demotes ABSENCE_SUPPORTED, J-97/ADR-009).
Why downgraded: the control without the Read (`R31-01_control_no_read`) gives `searches_would_qualify` on main too. The branch therefore equals "the author never read their own copy", which is what J-84/J-85 (the `_session_queries` docstring) say a self-Read must count as: neither count, denominator nor activation. Main refused only because it counted the draft copy as a search. An attacker gains nothing they could not get by not running the third search. It becomes relevant only if ADR-009's demotion is lifted; recommend a test pinning this before that day.

### R31-02: HIGH Error-A (collateral, not a moat breach): H5 marks honest copied sources as the draft. NEW.
usage_genres, main -> branch, same 230 claims:
- gates: PASS 4 -> 0, NEEDS_WORK 5 -> 1, FAIL 31 -> 39 (b01, b02, b04, b07 PASS->FAIL; b05, c03, c05, c07 NEEDS_WORK->FAIL).
- claims: GROUNDED 102 -> 49; UNGROUNDABLE 0 -> 69 (48 from GROUNDED, 21 from UNGROUNDED); 5 GROUNDED -> UNGROUNDED.
- Cause of the 69: a draft that quotes >= 80% of its lines from one real Read source makes `_source_reproduces_draft` true, so the genuine source is dropped as "self" (the CEILING's stated Error-A, but it hits every copied-bullets/copied-table draft in the genre set).
- Cause of the 5: H1/H2 lexical noise. `delete=False` tokenises to the denial word "false" in the NEXT sentence, which also holds "that"/"it" (python_tempfile.md); "A rebase that goes wrong" denies the sentence before it (git_rebase.md); "cannot"/"without" + "which" likewise.
- Repo pairs: 5 more GROUNDED->UNGROUNDED (honest_drafts_v2/batch_d draft_1, draft_5; quoting_drafts batch_b draft_3_literal and RESULTS.md; batch_c draft_3_natural).

### R31-03: HIGH (pre-existing Error-B, not closed by H5): diluted self-copy still PASSes when the draft has two short headings.
Repro `w/cases4.json`: draft "# Field notes / ## Key findings / 3 fabricated cited sentences"; Read `notes.md` = the 3 sentences between 16 filler lines. main PASS, branch PASS (3/3 GROUNDED). The headings count as 2 of 5 segments, so 3/5 = 60% < 80%. This is H5's documented CEILING, but a title plus one section heading is the default shape of a real draft, so the bypass costs nothing. Fix shape: count only segments that decompose into scored claims in the denominator.
(For reference, H5 does close a plain diluted copy and a shuffled diluted copy: `H5_control_diluted_copy` and `H5_shuffled_diluted` main PASS -> branch FAIL.)

### R31-04: MEDIUM (pre-existing, outside H1/H2 scope): denial bypasses still ground on both.
All PASS/GROUNDED on main and branch (source padded so it is not a near-copy):
- denial 6 sentences back ("None of the following is true." + 6 sentences + claim);
- 2 back with no forward word ("Every word of this page is invented.");
- after the claim: "That is a lie.", "Lies.", "Bogus.", "Fake.", "No, not at all, sir, never.";
- a prose label followed by a list, claim as 2nd item (the previous sentence is item 1);
- a 7+ word label; "Nonsense:" label; Cyrillic "FАLSE:" (homoglyph; NFKC does not fold it).
Inconsistency: "fake" is in `_DISOWNING_LABEL_TOKENS` but not in `_DENIAL_TOKENS`, so "Fake." after the claim grounds.
Closed by the branch (main PASS -> branch FAIL): "Nope.", "Wrong.", HTML `<ul>` under "Myths" (welded into one sentence). "FALSE:" and full-width "ＦＡＬＳＥ：" were already refused on main.

### R31-05: INFO: two H3 strings are tested on the wrong tool.
"No results were found for your search query" and "An error occurred while searching" come from the DDG *search* tool, which capture_core does not record (it returns snippets -> None). The regex is applied only to `mcp__ddg-search__fetch_content`, and the test feeds them through fetch. Harmless (refusal-only), but the stated coverage is nominal.

### R31-06: verified: the R8A-05 xfail -> pass flip is for the right reason.
"Nobody has established that Redis loses acknowledged data.": main GROUNDED -> branch UNGROUNDED, also padded and with "Nobody" on its own line. Control "Everybody has established ..." stays GROUNDED on both, so the refusal comes from the token "nobody". The parameter moved from the strict-xfail list to a passing guard (test_moat_h1_far_denial.py:49); the other three R8A-05 forms ("failed to", "unable to", "declined to") stay strict xfail, so they are still open and visible. Not masking.

## Load-bearing assumption
"No widening" rests on ground() staying ANY-grounds over its source set. A future rule that refuses because one cited source *contradicts* the claim would make the H3/H5 removals non-monotone, as R31-01 already is for absence.
