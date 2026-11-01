# RED-TEAM-R33: branch run-2026-11-01-bc (6e82335) vs origin/main c8743b3

Verdict: 4 BLOCKERS (R33-01..04). Do not merge.
Ruling applied: only lines that MAKE NO CLAIM may go unscored; denial inside code does not deny. PASS on branch + refused on main = BLOCKER.
Harness: r33/probe.py (from r32) with d.json, e.json, t.json, n.json; diff.py (+DROPPED detection); one.py. Baseline draft "{CLAIM} [S1]." grounds on both.

## R33-01 BLOCKER: prose in a code-labelled fence is unscored
Repro (main FAIL, branch PASS): "{DRAFT}\n```python\nThe bank collapsed in April and 300 people lost savings.\n```\n".
Same: "# The bank collapsed" comment in ```python; ~~~python; ```PYTHON; "```python " (trailing space or NBSP); fence opener indented 3 spaces.
Cause: `_closed_fence_lines` blanks any line in a closed fence whose info string is a language. The CEILING in the code admits this, but the ruling says a claim-bearing line may not go unscored.
Fix: blank only fence lines that are not prose (a prose detector), or score every uncited fence line that contains a finite verb or a figure.

## R33-02 BLOCKER: a label number makes a verb-bearing heading unscored
Repro (main FAIL, branch PASS), each followed by "{DRAFT}":
"## Step 2: the bank collapsed", "## Step 2 — bank collapsed", "# ADR-006 fraud confirmed", "# Phase 3 trial failed", "## 1.2.3 Revenue fell sharply", "# FY-2024 revenue fell", "# ADR-006 fraud".
Cause: on main the number alone kept these headings scored. The branch removes label numbers, and the heading then falls into the existing verbless-heading gap (OI-MOAT-19): `_header_asserts` misses past-tense verbs such as collapsed, failed, fell, confirmed. "FY-2024" (a year attached to an identifier) is also treated as a label.
Fix: treat a heading as a label only if the text left after removing the label number contains no word at all apart from stopwords and title nouns, or contains no verb by a POS check. Exclude 4-digit years from the identifier rule.
Refused on both (no regression here): "# Part 1: 300 people died", "### 1. Profits doubled", "# Twelve banks failed", "## Stage 3 cancer killed him", "# Chapter 11 bankruptcy filed by Acme".

## R33-03 BLOCKER: claim-bearing table header rows are unscored
Repro (main FAIL, branch PASS): "| H |\n|---|\n| {CLAIM} [S1] |\n" with H set to each of "Acme fraud confirmed", "Step 2 bank collapsed", "Phase 3 trial failed", "1.2 Revenue fell sharply", "FY-2024 revenue fell".
Also: a heading line used as the header ("# Step 2 bank collapsed |"), and a second table stacked under the first.
Cause: `_label_only` uses the same `_header_asserts` and label-number logic as R33-02. This carries the verbless-heading gap into table headers, which main scored ("Acme fraud confirmed" has no number at all).
Refused on both: "The bank collapsed in April" (has a finite verb), "300 dead", "ADR-006 losses tripled", "[S9]" in a cell, a header that is a list item, a full-width pipe.

## R33-04 BLOCKER: table cells are checked on raw text, before NFKC
Repro (main FAIL, branch PASS): header cell "³⁰⁰ dead" or "½ of staff fired".
Cause: `_blank_structural_lines` calls `_label_only(cell)` on the raw cell, so `_NUMERIC_RE` does not see superscript digits or vulgar fractions. Headings are not affected: they are checked after NFKC ("## Part 1 ³⁰⁰ dead" is refused).
Fix: run `_figures_are_section_numbers` / `_header_asserts` on `_nfkc(cell)`.

## R33-05 INFO (accepted cost under the ruling): denial inside code is ignored
Main FAIL, branch PASS, with "{CLAIM}." in the source next to: "`No.`" on the next line; "`Myths:`" list label; "`None of the following is true.`"; a ```python / ```bash fence with "# No." / "# That claim is false." / "echo That is false:"; ``That is false`` (double backticks); "`That is false` says the regulator" (no sentence boundary inside the span).
All fall under "denial words inside code don't deny". Sai should know the accepted cost covers fences, H4 list labels and scope sentences, not only one-line backtick spans.

## R33-06 INFO: new refusals (Error-A, fail-closed, intended by R32-05)
Main PASS, branch FAIL: the claim in backticks in the draft only; the claim in backticks in the source only; source "`did not`" against a prose draft. Code grounding code ("`{CLAIM}`" on both sides) is refused on BOTH main and branch.
No way found to make code ground prose, or to ignore a denial inside a code unit that grounds. Tested: denial inside the same span, a code span before the claim in the same unit, mixed spans, "`never`", "`It is not true that`".

## Full differential
- **usage_genres (40 drafts):** 3 gate changes (c01, c03, t01: FAIL -> NEEDS_WORK). Every dropped segment is a real python/bash/sql fence or a label table header (Directive|Meaning, Station|..., Index type|...). Body rows are still scored. All intended.
- **Repo draft/store pairs (114):** 0 gate changes. Refused -> grounded only for label headings: "## 1." .. "## 6." (DEMO-SCRIPT), "# ADR-006/007/009 notes", "# CR-013 capture contract", "# ALPHA-5 clean-clone install". Dropped segments: bash fences and table header rows only; for batch_d/draft_2 I checked that the body row is still scored. All intended.
- **Gold:** measure_rates output byte-identical (md5 06088c72...) on main and branch; test_golden, test_golden_matrix and test_gold_labels_separation give 24 passed on each.
- **Not reached:** none of the R33-01..04 shapes occur in the repo corpus. The blockers are adversarial, not a regression on honest drafts.
