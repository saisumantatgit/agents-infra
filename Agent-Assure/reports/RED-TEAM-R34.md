# RED-TEAM R34 — branch run-2026-11-04 (7984dc6) vs origin/main 41a7e2e

Verdict: fail-closed claim UPHELD (no loosening found); Error-A for fix 1 is larger than the run report states; 4 new bypasses.

## Method
- Code read: all 3 diffs are pure additions of `return True` on refusal paths (`_header_asserts` -> scored; `_is_bare_denial` only consumed by `_unit_denied`; `previous_line`/`previous2` checks inserted before the unchanged `following` checks). No condition reordered or removed; `hits` path still reached.
- Differential harness (scratchpad diff.py) loads both ground_check.py in-process, same store, compares gate + per-claim verdicts.
- Corpus: every repo draft (.md, excl. docs/reports) x every .jsonl store; usage_genres run on both trees (copied to scratch, repo untouched); ~70 hand probes.

## Findings

### R34-01 — BLOCKER hunt: none found (severity: n/a)
- Corpus differential: 2,664 draft x store pairs (3 stores unloadable on both). 75 differ, all FAIL->FAIL; 0 loosenings (no claim moved toward GROUNDED, no gate toward PASS). 75 claim flips toward refusal: 4 headings x 18 stores ("## What this record cannot tell you", "## What changed", "## The moat: mechanical, not model-judged", "# Rainfall, reworded" -> UNCITED), t06 table row x2, one "the usage price is unmeasured [S5]" -> UNGROUNDED. Three of the four headings are this repo's own calibration docs (Error-A, see R34-02).
- usage_genres: gates identical (PASS 4/NW 3/FAIL 33 both); 2/230 claims flipped, both toward refusal (t06 table row GROUNDED->UNGROUNDED; t10 "# Rainfall, reworded" ->UNCITED). Matches report lines 16/24/37.
- Theoretical loosening path checked: a newly scored heading could only lift a vacuous draft to PASS if it GROUNDED; uncited headings score UNCITED, cited ones were already scored. Probe "# Acme fraud confirmed" alone: main NEEDS_WORK, branch FAIL.

### R34-02 — MEDIUM, Error-A (new): evaluative word list fires on common label nouns
Honest doc (one cited grounded sentence) under the heading flips PASS -> FAIL (not NEEDS_WORK: score 50 < floor):
"## Record of decisions", "## Track record", "# Widespread adoption notes", "# Historic overview", "# Dramatic irony", "# Huge pages", "## Collapse sections", "## Work completed" (participle rule).
Report documents only participle Error-A ("Lessons learned" — which already FAILed on main). "record" as a noun is the worst member (ADR/record-keeping docs: this repo's own genre). 8/38 probe headings newly refused; 13 of 38 already refused on main.

### R34-03 — MEDIUM, Error-A (new): denial two back / bare-denial widening
- "This is not a drill. Staff evacuated. <claim>." PASS -> FAIL (forward ref "this" two back).
- "He said it survived. That is a lie. <claim>." PASS -> FAIL (documented CEILING).
- "Fiction. Use z. <claim>." refused (intended).
Honest "Rumours ...not true. Records were checked. <claim>" unaffected.

### R34-04 — HIGH, bypass (new code, NEW): homoglyph/invisible in heading rules
New checks do not confusable-fold or strip format chars:
- "# Bank collapsеd" (Cyrillic e) -> PASS on branch.
- "# Recоrd profits" (Cyrillic o) -> PASS.
- "# Bank collapsed​" (ZWSP) -> PASS.
Elsewhere (`_is_bare_denial`) the code folds via `_confusable_fold`; `_header_asserts` additions don't. Fix: fold + strip Cf before both tests.

### R34-05 — MEDIUM, bypass (NEW, fix 3): content-only rule beaten by one adjective
"That is a total lie. <claim>." and "That is a big fat lie. <claim>." still GROUND (padding content word "total"/"big"/"fat").

### R34-06 — bypasses PRE-EXISTING / documented (LOW, ceilings named in code)
- Denial 3 sentences back ("None of this is true. Use z. Ok then. <claim>") GROUNDS.
- Following-side asymmetry: denial two sentences AFTER the claim GROUNDS (fix only extended backward).
- Previous-two denial without forward ref/bare ("Officials deny all of it entirely now. Use z. <claim>") GROUNDS.
- Verb-final -s ("# Bank Collapses", "### PostgreSQL Fails"), predicate adjectives outside list ("# Acme guilty", "# Fraud everywhere") remain NON_CLAIM.
- "Everything after is made up" (vocab gap) GROUNDS.
- Report's stated open welded case ("denial line then code line") is actually refused in my probe — CEILING comment overstates the hole (harmless).
