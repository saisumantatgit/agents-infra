# S1: does a narrow `ident=False` rule win back the usage_genres H1 losses?

Ruling pack for Sai (pass-widening; nothing in scripts/ or tests/ was changed). Measured on main 81cee97 with scratch copies under /private/tmp/claude-501/s1/ (main, narrowA, narrowB, narrowC, trace); worktree results.json untouched.

## Verdict
- **Win-back:** the narrow rule recovers 1 of the 9 segments (c01 `gettempdir`). 8 of 9 stay refused because their trigger is not a code token.
- **Safety:** it lets fabrications through that main refuses (6 of 8 `=`-form attacks in the first batch; 3 more with `: `). Recommendation: do NOT adopt as stated. If Sai wants the 1 segment, adopt only the backtick-scoped form (variant C), which closes the unbackticked attacks but not the backticked ones.

## 1. Trigger per segment (traced on main by instrumenting `_unit_denied`)
| # | Draft / claim | Rule that refuses | Exact token | Class |
|---|---|---|---|---|
| 1 | c01 `gettempdir` sentence | next-sentence denial + back-reference (`it`, `that`) | `false` from `` `delete=False` `` in the NEXT sentence | (i) `ident=False` |
| 2 | c02 `delete=False` claim | next-sentence denial + back-reference `it` | `cannot` -> `can not` in "On Windows ... cannot be opened ... while it is still open" | (iii) prose |
| 3 | c02 `SpooledTemporaryFile` | next-sentence denial + back-reference `it`/`which` | `without` in "returns a name without creating the file" | (iii) prose |
| 4 | c02 "then rolls it over to disk" | same as 3 | `without` | (iii) prose |
| 5 | c03 `git rebase -i` | next-sentence denial + back-reference `that`/`which` | `wrong` in "a rebase that goes wrong" | (iii) prose |
| 6 | c05 "default index type is B-tree" | denial before match in the same welded sentence | table cell `No` (rows Hash, GIN: "Supports range queries = No") | (iii) prose-like table word, not code |
| 7 | c05 "CREATE INDEX ... unless" | same as 6 | `No` (table) | (iii) |
| 8 | c06 "status 304 ... has not changed" | denial before match | `none` from the header name `If-None-Match` | (ii) other code token (hyphenated identifier) |
| 9 | c07 `.assure/evidence-store.jsonl` | next-sentence denial + back-reference `that` | `not` in "Do not paste the snippet that install.sh prints" | (iii) prose |

Counts: (i) 1, (ii) 1, (iii) 7. The drift report's wording ("`delete=False` -> false in the next sentence") is right only for #1; for #2 the `delete=False` is in the claim itself and is not the trigger.

## 2. Measured win (usage_genres, scratch main vs patched copies)
- Baseline scratch main: 4 PASS / 3 NEEDS_WORK / 33 FAIL; authored grounded 48/171.
- Variant A (`ident=`/`ident==` + False/True/false/true/null/None): authored 49/171, gates identical. Only c01 flips UNGROUNDED -> GROUNDED. Variant B (adds `ident: `): same 1. Variant C (A, inside inline backticks only): same 1.
- Draft-level PASS count does not move (c01 still FAILs on its other sentences). The win is 1 claim of 171.
- Existing suite on variant B: 1276 passed, 2 skipped, 60 xfailed, identical to main (no test pins the old behaviour).
- Harness caveat: scratch main differs from committed results.json in 2 b03 claims (README/ALPHA-TESTER-GUIDE moved since 295438a); unrelated to the rule.
- Not tried, would add segment 8: also masking hyphenated header names (`If-None-Match`). It is a separate rule with the same hole class.

## 3. Attacks (single-claim drafts, source says the claim is false; main REFUSES, patched GROUNDS)
| Attack source (claim = "The vendor passed the security audit last year") | main | A | B | C (backticked) |
|---|---|---|---|---|
| "...last year. That is_true=False." | refuse | SLIP | SLIP | SLIP if `` `is_true=False` `` |
| "The report is true=False. The vendor passed..." | refuse | SLIP | SLIP | SLIP if backticked |
| "...last year. this_claim_is_valid=False. It was in fact never audited." | refuse | SLIP | SLIP | SLIP if backticked |
| "This statement has valid=False. The vendor passed..." | refuse | SLIP | SLIP | SLIP if backticked |
| "Everything below has verified=False. The vendor passed..." | refuse | SLIP | SLIP | SLIP if backticked |
| "Note that is_accurate==False here. ..." | refuse | SLIP | SLIP | not tested |
| "...last year. That claim, per the checker: result: False." | refuse | refuse | SLIP | refuse |
| "Verdict on the following: false. ..." | refuse | refuse | SLIP | refuse |
| "...last year. This is checked as claim: False." | refuse | refuse | SLIP | refuse |
| fenced block "That:\n```\nis_true=False\n```" | refuse | SLIP | SLIP | refuse |
Still refused in every variant: draft-side fabrications (`The audit passed=False` against a source saying it passed; `retries=False` flipping `retries=True`; the draft's literal keeps a distinct token `lit_false`), JSON `{"verified": false}`, `rating: false` labels, `Rating=False;` same-sentence, a bare `Supported=False.` next sentence, `claim: False` after a scope sentence.
Pre-existing hole (unchanged, any variant): `is_fabricated=True` grounds on main already.
Load-bearing assumption: the lexical shape `ident=False` carries no information about WHICH identifier it is; the 3 attacks above differ from honest `delete=False` only in the identifier name, so no lexical rule tells them apart (a name blocklist is the enumerating-side rule this project already abandoned).

## 4. Implementation spec (if Sai rules to adopt variant C)
1. In `_tokenize` (scripts/ground_check.py), before `.casefold()`, rewrite each exact literal `False|True|false|true|null|None` that directly follows `\b\w+(?:==|=)` INSIDE a single-line inline backtick span to `lit_<literal>`. Same transform on claim and source so verbatim matching is unchanged; `lit_false` is not in any denial set, and `delete=True` vs `delete=False` stay distinct.
2. Only `=`/`==`. Do not add `: ` (variant B adds 3 more slips and wins nothing in the corpus beyond A).
3. Fenced blocks and hyphenated identifiers are out of scope.
4. Tests to add (each proven red on main first): c01 grounds; `` `delete=True` `` claim vs `` `delete=False` `` source stays refused; unbackticked `is_true=False` back-ref stays refused; JSON `"verified": false` stays refused; fenced `is_true=False` stays refused; draft `The audit passed=False` vs source "The audit passed" stays refused.
5. CEILING: breaks as soon as a backticked identifier carries a denial meaning (`` `is_true=False` ``, `` `claim=False` ``); 3 of 3 such probes ground a claim the source denies. Upgrade path: parse real code spans against a closed list of well-known API parameter names (a whitelist from the cited source's own prose, e.g. the identifier also appears as an argument name in a signature), or a source-type tag so only code-documentation sources get the exemption.

## 5. Recommendation
Do not adopt A or B. Variant C buys 1 of 171 authored claims (0 drafts to PASS) at the cost of a known, undefendable hole for backticked denial-named identifiers. The real mass is class (iii): 7 of 9 losses come from the next-sentence denial + back-reference rule firing on ordinary words (`cannot`, `without`, `wrong`, `not`) and from table cells (`No`). That is the systemic issue (Error-A of H1's lexical rule); this narrow rule is a case resolution of 1 segment. Systemic fix to rule on instead: make the next-sentence rule require the denial to be clause-adjacent to the back-reference word, and drop table-cell tokens from `prefix`. Not measured here.
