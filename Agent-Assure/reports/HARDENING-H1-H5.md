# Hardening H1-H5 (2026-10-25)

Branch `hardening-2026-10-25`. Five fail-closed fixes to `scripts/ground_check.py` /
`scripts/capture_core.py`: each may only move a claim AWAY from PASS. Baseline before H1:
1045 passed, 2 skipped, 61 xfailed. Gold `calibration/labels-v2.csv` md5
`6215b526d03147295b003d7ccb0d171f` (checked after every fix). Rates are from
`calibration.measure_rates.measure()`; per-row predicted verdicts were diffed against
baseline after every fix.

## H1: far and unlisted denials

- **Hole:** a denial beyond the 5-token hedge lookback, across a `;` / `(` / line split
  inside the same sentence, in a forward-pointing previous sentence, or an unlisted denial
  word, left the grounding sentence free to certify.
- **Red (pre-fix code):** `tests/red_team_moat/test_moat_h1_far_denial.py`: 8 failed,
  2 passed (the 2 are controls). All 8 attacks were GROUNDED / gate PASS:
  `prev_sentence_never_6_back`, `same_sentence_semicolon`, `same_sentence_newline`,
  `same_sentence_paren`, `we_dispute_the_following`, `this_is_false_far`,
  `none_of_that_happened`, `hardly_before`.
- **Fix:** `_source_unit_contexts` + `_unit_denied` + `_DENIAL_TOKENS`, wired into both T1
  paths (`_contained_with_matching_polarity`, `_anchor_sentence_covers`). A match is refused
  when a denial word sits before it in the same sentence, the previous sentence denies and
  points forward (or is ≤3 tokens), or the next sentence denies and points back.
- **Green:** 11 passed. Full suite 1056 passed, 2 skipped, 60 xfailed.
- **Side effect, good:** R8A-05 `nobody-has-established` (a strict xfail, open finding)
  XPASSed, so it was promoted from the xfail list to a passing guard.
- **Design correction during the fix:** the first version refused on ANY denial word in the
  previous sentence. It broke `test_relational_row_is_not_tier_sensitive`: the honest source
  "Insulin resistance occurs when cells do not respond well to insulin. Sustained insulin
  resistance causes type 2 diabetes ..." lost its T1 match. Narrowed to forward-pointing or
  bare-short previous sentences.
- **Rates:** Error-A 12/25, Error-B 0/27 — unchanged; zero gold rows drifted.
- **CEILING (in code):** lexical, not referential. Over-refuses an unrelated same-sentence
  denial; under-refuses a denial two sentences away, an unlisted denial word, or a
  previous-sentence denial with no forward reference.
- **Commit:** `82821cf`.

## H2: short denial reply next to the grounding sentence

- **Hole:** "<claim>. No." (also "Not so.", "Untrue.", "False.", "Hardly.", "Nope.")
  certified the claim. Before-side replies were already refused by the hedge lookback,
  except "Nope." (not a listed word).
- **Red (pre-fix = H1 commit 82821cf):** `tests/red_team_moat/test_moat_h2_short_reply.py`:
  7 failed, 8 passed. Failing: all 6 after-side replies + before-side "Nope.". The 5 other
  before-side cases and 3 affirmation controls passed.
- **Fix:** in `_unit_denied`, a following sentence of ≤3 tokens holding a denial word
  denies; "nope" added to `_DENIAL_TOKENS` (H1's ≤3-token previous-sentence rule then
  covers the before side).
- **Green:** 15 passed. Full suite 1071 passed, 2 skipped, 60 xfailed.
- **Rates:** Error-A 12/25, Error-B 0/27 — unchanged; zero gold rows drifted.
- **CEILING (in code):** 3-token cut. A longer bare reply ("No, not at all, sir.") stays
  open; an honest short negative after the claim ("Not always.") is refused (Error-A).
- **Commit:** `ab18151`.

## H3: DuckDuckGo failure texts read as successful reads

- **Source of strings (read, not guessed):** `duckduckgo_mcp_server` 0.7.0 `server.py`
  (md5 `b7d61b6791f8aad2fd78172f36a13fa4`, identical in all 9 uv-cache copies; the
  configured `ddg-search` MCP runs it via `uvx`). Every `fetch_content` error return is
  already `Error: ...`-prefixed (covered by R26-05). New shapes found:
  - `"No results were found for your search query. ..."` (`format_results_for_llm`);
  - `"An error occurred while searching: {e}"` (search tool except-branch);
  - `_CLOUDFLARE_BODY_SIGNALS` (`cf-mitigated`, `Just a moment...`, `Enable JavaScript
    and cookies to continue`, `Checking your browser before accessing`): a challenge body
    that the curl retry also hits is returned as page text;
  - an EMPTY page returns only the metadata trailer `---\n[Content info: Showing characters
    0-0 of 0 total ...]`, which has words, so the no-word rule never fired.
- **NOT_LOCATED_UNDER**(`grep -n -i "anomaly|captcha|bots use|rate limit|429|too many"` over
  that `server.py`, returned strings only): no DDG anomaly/captcha page text and no
  rate-limit failure string (the limiter waits; it returns nothing). Not recognised.
  Note also: `mcp__ddg-search__search` is not a captured tool, so its two strings only
  matter if they ever arrive through `fetch_content`; recognised anyway (refusal-only).
- **Red (pre-fix = H2 commit ab18151):** `tests/red_team_moat/test_moat_h3_ddg_failure_texts.py`:
  8 failed (all 8 failure shapes stored `"ok"`), 2 passed (controls: a real page with its
  trailer; a page saying "no results were significant").
- **Fix:** `capture_core._ddg_text_is_error` gains the two prefixes, the four challenge
  signals, and "body empty once the trailer is removed".
- **Green:** 10 passed. Full suite 1081 passed, 2 skipped, 60 xfailed.
- **Rates:** Error-A 12/25, Error-B 0/27 — unchanged (capture-side; no gold row drifted).
- **CEILING (in code):** a phrase list; a site's own block page not in the server source
  stays `"ok"` (the existing R20 CEILING).
- **Commit:** `7bacc9b`.

## H4: disowning list labels

- **Hole:** "Myths:" refused only the FIRST item (via the 5-token lookback). "Rumours:" /
  "Rumors:" refused nothing; "Fallacies:", "Debunked:", "False claims:", "Myths:",
  "Misconceptions:" refused the first item but grounded the second and later items.
- **Red (pre-fix = H3 commit 7bacc9b):** `tests/red_team_moat/test_moat_h4_list_labels.py`:
  16 failed, 9 passed. Failing: all 7 labels on the second item and on a numbered list
  under a `##` heading; Rumours/Rumors also on the first item. Passing pre-fix: 5 first-item
  cases (already refused, by the lookback or H1's same-sentence rule) and 4 controls
  (neutral labels "Key facts:", "Timeline:", "Findings:"; a list that ends at a plain
  paragraph).
- **Fix:** `_disowned_lines` marks the text after a short disowning label's colon and every
  following list-item line (blank lines allowed) until the first non-item line;
  `_UnitContext.disowned` makes `_unit_denied` refuse such units.
- **Green:** 25 passed. Full suite 1106 passed, 2 skipped, 60 xfailed.
- **Rates:** Error-A 12/25, Error-B 0/27 — unchanged; zero gold rows drifted.
- **CEILING (in code):** line-shaped lists only; a label two paragraphs up, a table, an HTML
  list, a colon-less "the following are myths", or an unlisted label word still grounds.
  An item whose words recur elsewhere in the source is refused there too (Error-A).
- **Commit:** `d755f87`.

## H5: near-copy of the draft diluted with unrelated lines

- **Hole:** R26-04 measures the share of the SOURCE's bigrams found in the draft. A Read file
  holding the whole draft with 2-3 unrelated lines after each draft line drops that share
  far below 0.8, so the draft certified itself.
- **Red (pre-fix = H4 commit d755f87):** `tests/red_team_moat/test_moat_h5_diluted_near_copy.py`:
  2 failed (both gate `PASS`: the copy diluted 2:1, and the copy diluted 3:1 with one word
  changed per line), 1 passed (control: a draft under its own title quoting two sentences of
  a long genuine file).
- **Fix:** `_source_reproduces_draft`, a second test measured over the DRAFT's own
  segments: a Read source is the draft when it reproduces ≥80% of the draft's lines or
  sentences, at least two, each with ≥60% of that segment's bigrams.
- **Design note:** a pooled share of draft bigrams was rejected before landing: it would have
  refused the control (27/33 = 0.82 of the draft's bigrams sit in the genuine file).
- **Green:** 3 passed; R26-04's 5 tests still pass. Full suite 1109 passed, 2 skipped,
  60 xfailed.
- **Rates:** Error-A 12/25, Error-B 0/27 — unchanged. This is NON-MEASUREMENT: no gold row
  uses a Read source copied from the draft (same caveat applies to H3).
- **CEILING (in code):** fail-open when two or more ORIGINAL headings/lines in a
  five-segment draft keep the reproduced share under 80%, or the draft is one segment.
  Error-A on a genuine Read file the draft quotes ≥80% of its segments from. Upgrade path:
  Write/Edit provenance in the capture store.
- **Commit:** `9662c48`.

## Summary

| Fix | Commit | Red pre-fix | Green | Error-A | Error-B |
|---|---|---|---|---|---|
| H1 far/unlisted denials | `82821cf` | 8 attacks PASS | 11/11 | 12/25 | 0/27 |
| H2 short denial reply | `ab18151` | 7 attacks PASS | 15/15 | 12/25 | 0/27 |
| H3 DDG failure texts | `7bacc9b` | 8 shapes "ok" | 10/10 | 12/25 | 0/27 |
| H4 disowning list labels | `d755f87` | 16 attacks PASS | 25/25 | 12/25 | 0/27 |
| H5 diluted near-copy | `9662c48` | 2 attacks PASS | 3/3 | 12/25 | 0/27 |

Final suite: 1109 passed, 2 skipped, 60 xfailed (baseline 1045 / 2 / 61; one xfail promoted
to a guard by H1). `tests/test_measure_rates.py` pin (fp,tn)=(12,13) untouched and green.
Gold md5 unchanged. Not pushed.

**Load-bearing assumption:** the gold corpus does not exercise denial context, list labels,
DDG failures or diluted self-copies, so "rates unchanged" says these fixes cost nothing on
the 52 rows. It does NOT measure their Error-A cost on real sources; the CEILING comments
name where each over-refuses.
