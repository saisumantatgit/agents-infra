# RED-TEAM-R32 — run-2026-11-01 vs origin/main 6eb3d5c

Verdict: NOT MERGEABLE. 4 blockers (3 in B, 1 in C). A is clean.

Method: the same CLI gate (`scripts/ground_check.py --json`), one-record store
(source = `CLAIM. TAIL` from tests/red_team_moat/_h_helpers.py), run on a
detached worktree of main and on the branch. Harness: r32/probe.py, cases
r32/b.json (B) and r32/c.json (C), differential r32/diff.py. Draft `{DRAFT}` =
the cited honest claim; each attack adds one fabricated, uncited line.

## Findings

### R32-01 BLOCKER (B) — a heading carrying a count of up to 3 digits is now unscored
`_figures_are_section_numbers` treats any 1–3 digit number as a section label. A count is not a label.
- `# 300 people died` main FAIL -> branch PASS
- `# 40 percent fraud rate` main FAIL -> branch PASS ("percent" spelled out escapes `%`)
- `## 12 dead in bank riot` FAIL -> PASS
- `# 999 staff fired` FAIL -> PASS
Not intended: Sai's ruling covers "lines that make no claim"; each of these asserts a figure.
Fix direction: exempt only a number that FOLLOWS a label word (Part/Step/Section/Chapter/Phase/Round) or a leading `N.`/`N)` enumerator, never a bare leading count; treat "percent"/"per cent" as a unit.

### R32-02 BLOCKER (B) — table header rows carrying claims are blanked
`_label_only` per cell reuses the heading test, so verb-final / verbless / small-count cells pass.
- `| Record profits | Fraud widespread |` + `|---|---|` FAIL -> PASS
- `| 300 dead | 12 banks |` FAIL -> PASS
- `| Fraud rate 40 percent | CEO jailed |` FAIL -> PASS
- `Minister resigned |` + `|---|` (one-cell, no leading pipe) FAIL -> PASS
- `- The minister resigned |` + `|---|` (LIST ITEM turned into a "header row" by a trailing pipe) FAIL -> PASS
Not intended. Note: headings with the same verbless text ("## Record profits") were already unscored on main (OI-MOAT-19); the branch EXTENDS that residue to table rows and list items, and the list-item route is a new shape that is not structure at all.
Fix direction: require a real table (header with >= 2 cells AND >= 1 body row with the same cell count), never a line starting with a list marker; apply the R32-01 number rule.

### R32-03 BLOCKER (B) — prose inside a closed fence is unscored, whatever the fence says
- ```` ```text ```` / `The central bank secretly printed 4 trillion dollars in 2019.` / ```` ``` ```` FAIL -> PASS
- ```` ```prose ```` fence FAIL -> PASS; `~~~` fence FAIL -> PASS; 3-space-indented fence FAIL -> PASS; closer longer than opener FAIL -> PASS
- Unclosed->closed trick: ```` ``` ```` then the cited claim then the fabrication then ```` ``` ```` FAIL -> PASS (the cited line survives because of its bracket; the uncited fabrication beside it is blanked)
- Whole draft wrapped in a fence: PASS (only the cited line is scored)
The code names this as a CEILING; it is not inside Sai's ruling, whose rationale is "they make no claim, so no fabrication can pass through them". A full English sentence with a figure and a year makes a claim regardless of fence. Fix direction: blank a fenced line only if it does not read as prose (e.g. no sentence-final period AND code-shaped tokens), or only for code info strings (python/bash/sql/...), never text/prose/markdown/none.

### R32-04 BLOCKER (C) — a stray backtick earlier on the line masks a prose denial
Source: ``The flag ` is odd. {CLAIM}. That is false. Use `x`.`` main FAIL (denied) -> branch PASS.
`_INLINE_CODE_SPAN_RE` pairs the stray backtick with the next one, swallowing the claim and its denial. Not the accepted case (the denial is not wrapped in backticks by the author). Same mechanism with full-width ｀ (U+FF40), which NFKC turns into a backtick before masking although no renderer treats it as code: FAIL -> PASS.
Fix direction: mask only spans with no sentence boundary inside (no `. ` + capital), shorter than N tokens; do not NFKC before code detection.

### R32-05 MEDIUM (C, consistent with ruling, worth naming) — asymmetry: code text grounds a claim but cannot deny it
Source: a closed fence containing `{CLAIM}. That is false.` FAIL -> PASS. Within the ruling (denial inside code), but claim matching still reads the fenced text, so the source "supports" a claim only through code it simultaneously says is false. Recommend: if a denial is masked as code, the claim match in that same code span should not ground either.

### R32-06 INFO (A) — no widening found
Every A change (scope_denied, `_is_bare_denial` superset of `len<=3`, confusable folding, long labels) only adds refusal paths; the only reads that changed direction are the masked `d_*` views, which belong to C. The new ValueError alignment checks did not fire on `4.5`, `$4`, `v1.2.3`, `it's`, `1,000` inside code.

## Differential (main vs branch)
- tests/usage_genres (40 drafts, run via copied run.py in scratch): 3 gate changes, all FAIL -> NEEDS_WORK (c01, c03, t01). Real claims refused->grounded: c01 "files are created in the directory returned by `gettempdir`..." and c06 "server answers with status 304..." — both honest and verbatim in source; intended (B: fence lines no longer welded into adjacent sentences / C). t01 "max-age=N ... fresh for N seconds [S1]" UNGROUNDED -> GROUNDED after the separator split the welded row; intended (B).
- All other repo store/draft pairs (114 pairs: demo, honest_drafts, honest_drafts_v2, quoting_drafts, red_team_moat fixtures, fixtures): 0 gate changes; 21 refused->grounded, all headings (`## 1.`, `# ADR-006 notes`, `# Red team round 20`) — intended by B.
- Golden + red_team_moat suites on branch: 595 passed, 1 skipped, 56 xfailed.
- Not observed in the corpus: any R32-01..04 shape. The corpus did not exercise them; the attacks are synthetic.
