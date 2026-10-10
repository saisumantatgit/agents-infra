# R9-P1 — Citation resolution (provenance only)

Round 9, provenance scope. Adversary: Opus 5, 2026-09-13 00:29–01:00 IST.
Target: `scripts/ground_check.py` at HEAD `13c2f4e` (unmodified).
Promise under attack: the gate never certifies (GROUNDED / gate PASS) a claim whose citation points to a source NOT in the store.

Reproduction harness (all cases): `$SCRATCH/r9p1/run.py` + `cases1.py`, `cases2.py`, `cases3.py`, where
`$SCRATCH=/private/tmp/claude-501/-Users-saisumanthbattepati-vibe-coding-Agents-agent-assure-calibration/d2b27b1f-f3bd-4dea-8c6a-e58508ad626d/scratchpad`.
Each case writes `<case>.md` + `<case>.jsonl` there and runs
`uv run python scripts/ground_check.py --draft <case>.md --store <case>.jsonl --json` from `Agent-Assure/`.
Outputs below are the gate's JSON reduced to `gate`, `grounding_score`, and per-claim `[text, kind, verdict, evidence_basis]`.

Base store (`BASE`), all `full_text_source: verbatim`:

- `S1` text: `Redis is an in-memory data structure store used as a database and cache.`
- `S2` text: `Clinical studies show that insulin resistance causes type 2 diabetes in adults.`
- `S3` text: `Insulin resistance is common in obese adults. Diabetes affects many adults worldwide.`

Summary: 2 ERROR-B findings (R9P1-01 relational, R9P1-02 absence) sharing ONE root cause (R9P1-03, recorded as the root, not counted as a third hole), 1 misresolution (R9P1-04), 2 cosmetic (R9P1-05, -06). 65 attack cases run (incl. 3 controls). Status: COMPLETE 00:38 IST.

## FINDINGS

### R9P1-01 — ERROR-B — relational grounding silently DROPS unresolved citations

Mechanism: `ground` delegates RELATIONAL claims to `ground_relational` BEFORE the "any citation unresolved -> UNVERIFIED_CITATION" branch, and `ground_relational` does `if source is None: continue`, so a fabricated id next to two real ones is ignored and the claim certifies.

Reproduction (case `c41_rel_real_real_fab`, store = BASE):

```
Insulin resistance causes type 2 diabetes [S2][S3][S99].
```

Output:

```
{"gate": "PASS", "score": 100.0, "claims": [["Insulin resistance causes type 2 diabetes [S2][S3][S99].", "RELATIONAL", "GROUNDED", "S99 is cited but was NEVER RETRIEVED this session. The store holds 3 sources and does not contain it, so nothing exists to check the claim against."]]}
```

The report contradicts itself: evidence_basis says S99 was never retrieved, verdict says GROUNDED, gate says PASS. `score_report`'s `has_unverified_citation` override does not fire because it keys on the VERDICT, and the verdict is GROUNDED.

Every citation form reaches it — the drop is independent of how the unresolved id is spelled:

- `c85_rel_S3a_fab` `... [S2][S3a][S3].` -> PASS / GROUNDED (S3a absent)
- `c84_rel_fullwidth_fab` `... [S2][S3][Ｓ99].` -> PASS / GROUNDED
- `c87_rel_source_form_fab` `... [S2][S3][source:fabricated-trial].` -> PASS / GROUNDED
- `c83_rel_haiku_plus_fab` `... [S2][S3][S4][S99].` (S4 haiku_summary) -> PASS / GROUNDED

Propagation variant (`c80_prop_rel_drop`) — the drop survives conjunction split and sentence-citation propagation:

```
Insulin resistance is common in obese adults and insulin resistance causes type 2 diabetes [S99] [S2][S3].
```

```
{"gate": "PASS", "score": 100.0, "claims": [["Insulin resistance is common in obese adults [S2][S3]", "FACTUAL", "GROUNDED", "Checked verbatim against 2 cited sources: S2 (79 chars), S3 (85 chars)."], ["insulin resistance causes type 2 diabetes [S99] [S2][S3].", "RELATIONAL", "GROUNDED", "S99 is cited but was NEVER RETRIEVED this session. ..."]]}
```

(The left clause also loses `[S99]`: `_TRAILING_CITATIONS_RE` only captures the final CONTIGUOUS run of markers, so a space between `[S99]` and `[S2][S3]` truncates what propagates. See R9P1-05.)

Bound (not a finding): with only ONE real id (`c42 [S2][S99]`) or zero (`c43 [S98][S99]`) the two-distinct-source rule still fails it -> UNVERIFIED_RELATION / FAIL. The hole needs >= 2 real verbatim sources that already ground the relation, plus any number of fabricated ids.

Systemic fix shape: in `ground`, run the unresolved-citation check for EVERY cited kind before dispatching (or have `ground_relational` return UNVERIFIED_CITATION on `source is None` instead of `continue`). Fail-closed.

### R9P1-02 — ERROR-B — absence claims never resolve their citations

Mechanism: `ground` delegates ABSENCE claims to `check_absence` before the citation branches, and `check_absence` never calls `resolve` (it reads only `claim.text`, session queries, and store texts), so an absence claim citing a non-existent source can reach ABSENCE_SUPPORTED and gate PASS.

Store `AB`: S1 (q=`MongoDB Redis benchmark comparison`), S2 (q=`benchmark comparing MongoDB and Redis latency`), S3 (q=`diabetes prevalence`), texts as BASE.

Reproduction A (`c54_absence_sourceform`):

```
We found no benchmark comparing MongoDB against Redis [source:fake-survey].
```

```
{"gate": "PASS", "score": 100.0, "claims": [["We found no benchmark comparing MongoDB against Redis [source:fake-survey].", "ABSENCE", "ABSENCE_SUPPORTED", "An absence claim is checked against what was SEARCHED, not what was cited. Complete record consulted: 3 distinct search queries and the text of 3 retrieved sources. ..."]]}
```

Reproduction B (`c56_absence_leading_cite`):

```
[S99] We found no benchmark comparing MongoDB against Redis.
```

```
{"gate": "PASS", "score": 100.0, "claims": [["[S99] We found no benchmark comparing MongoDB against Redis.", "ABSENCE", "ABSENCE_SUPPORTED", "An absence claim is checked against what was SEARCHED, not what was cited. ..."]]}
```

Reproduction C (`c57_absence_fab_anchor_in_queries`, contrived store whose queries contain the token `S99`): `We found no benchmark comparing MongoDB against Redis [S99].` -> PASS / ABSENCE_SUPPORTED.

Why the trailing `[S99]` form usually fails (`c51`, `c53`, `c55` -> UNVERIFIED_ABSENCE): the marker text is NOT stripped before `_extract_absence_anchors`, so `S99` becomes a strong anchor no query contains. That is accidental fail-closure — the citation is read as subject vocabulary, never as a citation. Move the marker out of the subject (leading position) or use the `source:` form and it evaporates.

Arguable counter-reading, recorded: absence is designed to be evidenced by SEARCHES, not citations ("checked against what was SEARCHED, not what was cited"). That justifies not REQUIRING a citation. It does not justify certifying a draft that ASSERTS a citation to a record the store does not hold — the reader of the certified draft is told `fake-survey` / `S99` backs the absence. By the round's definition this is ERROR-B.

Systemic fix shape: same as R9P1-01 — the unresolved-citation check must precede the kind dispatch, so any claim that CARRIES a citation must have every citation resolve regardless of kind.

### R9P1-03 — ROOT CAUSE of 01/02 (not counted separately) — same root as 01/02: the UNVERIFIED_CITATION check sits after the kind dispatch

Recorded separately so the fix is judged against the ROOT, not the two fixtures. `ground`'s documented branch order is `NON_CLAIM -> RELATIONAL -> ABSENCE -> no citations -> any unresolved -> ...`. Branches 2 and 3 return before branch 5 runs, and neither delegate resolves-and-rejects. NON_CLAIM (branch 1) is currently safe only because `_is_non_claim` returns False for any text containing a `_CITATION_RE` match (verified: same NFKC'd text is used in `classify` and `_is_non_claim`). A narrow patch inside `ground_relational` alone would leave R9P1-02 open, and vice versa — the round-3 "narrow fix closes the fixture, leaves the class" pattern. Any new kind added ahead of branch 5 re-opens it.

### R9P1-04 — misresolution — duplicate / NFKC-colliding store ids silently resolve to the LAST record

Mechanism: `load_store` does `store[source_id] = source` with no duplicate check, after NFKC-folding `source_id`, so two records with the same (or NFKC-equivalent) id collapse and `[S1]` resolves to whichever line came last — contrary to the project convention "duplicate key -> raise".

Reproduction A (`c60_dup_id_lastwins`): store line 1 `{"source_id":"S1","url":"https://real.example/first","text":"Totally unrelated capture about gardening tomatoes in spring.",...}`, line 2 `{"source_id":"S1","url":"https://attacker.example/second","text":"Redis is an in-memory data structure store used as a database and cache.",...}`. Draft: `Redis is an in-memory data structure store used as a database and cache [S1].`

```
{"gate": "PASS", "score": 100.0, "claims": [["Redis is an in-memory data structure store used as a database and cache [S1].", "FACTUAL", "GROUNDED", "Checked verbatim against 1 cited source: S1 (72 chars)."]]}
```

Reproduction B (`c61_fullwidth_collision`): line 1 `source_id "S1"` (unrelated text, real.example), line 2 `source_id "Ｓ1"` (full-width S; Redis text, attacker.example). Same draft -> `PASS / GROUNDED`, resolved against the full-width record. `c66_store_superscript_id` (`source_id "S¹"` only) also resolves `[S1]` -> PASS.

Severity reasoning: not ERROR-B under this round's definition because the resolved record IS in the store; it is a misresolution because a human auditing the store sees two S1s and cannot tell from the report (`S1 (72 chars)`, no url/sha) which one certified the claim. The capture hook assigns ids, so exploitation needs a store writer, but the store is the audit record and the gate is the only reader that could refuse it. Fix shape: raise on duplicate post-NFKC `source_id` in `load_store`; include `content_sha256`/url in evidence_basis.

### R9P1-05 — cosmetic — partial propagation of a space-separated citation run

Mechanism: `_TRAILING_CITATIONS_RE` captures only the final contiguous `[..][..]` run, so `X and Y [S99] [S3].` propagates `[S3]` but not `[S99]` to the left clause.

`c81_prop_partial_run`: `Insulin resistance is common in obese adults and diabetes affects many adults worldwide [S99] [S3].`

```
{"gate": "FAIL", "score": 50.0, "claims": [["Insulin resistance is common in obese adults [S3]", "FACTUAL", "GROUNDED", ...], ["diabetes affects many adults worldwide [S99] [S3].", "FACTUAL", "UNVERIFIED_CITATION", ...]]}
```

Alone it cannot reach PASS (the right clause still carries S99 through the normal path). It becomes PASS-reachable only when the right clause is RELATIONAL/ABSENCE (see c80 under R9P1-01). Closing R9P1-03 closes the PASS path; the partial-run behaviour itself remains a fidelity defect.

### R9P1-06 — cosmetic — markers the gate cannot see pass as prose

1. `c72_code_span_only`: `... cache `[S1]`.` -> PASS / GROUNDED. A citation inside a code span (rendered as literal code, not a citation) is resolved and trusted. Resolves to a real record, so not ERROR-B.
2. `c74_fab_in_comment`: `... cache [S1] <!-- [S99] -->.` -> PASS. The hidden S99 is invisible to the reader too, so reader and gate agree. Not a finding; listed for completeness.
3. `c90_lookalike_absorbed`: Cyrillic `[Ѕ99]` next to real `[S5]` -> PASS, but only because S5's own text contains the literal string `[Ѕ99]`. Needs the SOURCE to carry the marker, so out of scope; noted because a reader sees a second "citation" the gate never parsed.

## ATTACKS THAT FAILED

All run, all fail-closed (gate FAIL or NEEDS_WORK). Case ids refer to the scratch harness.

Id forms and normalisation (FACTUAL claim verbatim in S1, real `[S1]` co-cited unless noted):

| Case | Marker | Verdict / gate | Why it held |
|---|---|---|---|
| c00 | `[S1]` alone | GROUNDED / PASS | control |
| c01 | `[S1][S99]` | UNVERIFIED_CITATION / FAIL | branch 5 |
| c02 | `[S1, S99]` | UNCITED / FAIL | regex does not match lists |
| c03 | `[S1; S99]` | UNCITED / FAIL | same |
| c04 | `[S1-S3]` | UNCITED / FAIL | same |
| c05 | `[[S99]]` | UNVERIFIED_CITATION / FAIL | inner marker matched |
| c05b | `[[S1]]` | GROUNDED / PASS | resolves the real S1 — correct |
| c06 | `[S1][Ѕ99]` Cyrillic S | UNVERIFIED_NUMBER / FAIL | unmatched marker; `99` leaks into numeric tokens (accidental) |
| c07 | `[S1][Ε99]` Greek | UNVERIFIED_NUMBER / FAIL | same |
| c08 | `[S1][S<ZWSP>99]` | UNVERIFIED_NUMBER / FAIL | same |
| c09 | `[S1][S9<ZWJ>9]` | UNVERIFIED_NUMBER / FAIL | same |
| c10 | `[S1][s99]` | UNVERIFIED_NUMBER / FAIL | same |
| c11 | `[S1][ S99 ]` | UNVERIFIED_NUMBER / FAIL | same |
| c12 | `[S1][S99.]` | UNVERIFIED_NUMBER / FAIL | same |
| c13 | `[S1][Ｓ99]` full-width S | UNVERIFIED_CITATION / FAIL | NFKC folds -> S99 |
| c14 | `[S1]［S99］` full-width brackets | UNVERIFIED_CITATION / FAIL | NFKC folds |
| c15 | `[S01]` (store S1) | UNVERIFIED_CITATION / FAIL | literal key, no int parse |
| c16 | `[S1a]` | UNVERIFIED_CITATION / FAIL | OI-CITE-01 holds |
| c17 | `[S١]` Arabic-Indic digit | UNVERIFIED_CITATION / FAIL | `\d` matches, key `S١` absent |
| c18 | `[S¹]` | GROUNDED / PASS | NFKC -> S1, same id a reader intends — correct |
| c19 | `[S1][S9<U+0301>9]` combining | UNVERIFIED_NUMBER / FAIL | numeric leak |
| c20 | `[S1][S<RLM>99]` | UNVERIFIED_NUMBER / FAIL | numeric leak |
| c21 | `[S1][S9<SHY>9]` | UNVERIFIED_NUMBER / FAIL | numeric leak |
| c30 | numeric claim, source contains 99, `[S4][Ѕ99]` | UNVERIFIED_NUMBER / FAIL | T1/numeric still fails on leaked token |
| c31 | same with ZWSP | UNVERIFIED_NUMBER / FAIL | same |
| c32 | `[S1][Source:fake-paper]` | UNGROUNDED / FAIL | marker words leak into claim tokens, T1 fails |
| c33 | `[S1][source:fake-paper]` | UNVERIFIED_CITATION / FAIL | branch 5 |
| c34 | `[S1][ref:fake-paper]` | UNGROUNDED / FAIL | token leak |
| c35 | `[S1][source: fake]` | UNVERIFIED_CITATION / FAIL | branch 5 |

Note on c06–c12, c19–c21, c32, c34: these hold by ACCIDENT (the unparsed marker pollutes numeric tokens or T1 coverage), not by design. No digit-free, word-free lookalike marker that a reader would take for an id was found, so no PASS; but a future tokenizer or numeric change could flip them. Candidate permanent guards.

Placement:

| Case | Draft shape | Verdict / gate |
|---|---|---|
| c22 | `X. [S99]` | X UNCITED + `[S99]` UNVERIFIED_CITATION / FAIL |
| c23 | `X\n[S99]` | one claim, UNVERIFIED_CITATION / FAIL |
| c71 | `X [S1].` + `[S1]: https://attacker.example/...` ref definition | definition line scored UNGROUNDED / FAIL |
| c70 | `X [S1](https://attacker.example/fake-paper).` inline link | UNGROUNDED / FAIL (url tokens leak into T1) |
| c73 | `X <!-- [S1] --> [Source:fake].` | UNCITED / FAIL (comment stripped, real id not used) |
| c75 | footnote `X[^1].` / `[^1]: [S99]` | UNCITED + UNVERIFIED_CITATION / FAIL |
| c81 | `X and Y [S99] [S3].` | FAIL (see R9P1-05) |
| c82 | `X; Y-relational [S2][S3][S99].` | left UNVERIFIED_CITATION blocks, FAIL (relational right half GROUNDED — R9P1-01 again) |

Relational bounds: c42 `[S2][S99]` UNVERIFIED_RELATION / FAIL; c43 `[S98][S99]` UNVERIFIED_RELATION / FAIL; c86 `[S2][S2][S99]` UNVERIFIED_RELATION / FAIL (dedup by source_id holds); c40 control `[S2][S3]` PASS.

Absence bounds: c50 uncited absence PASS (by design, not a provenance finding); c51 trailing `[S99]`, c53 post-verb `[S99]`, c55 `[S1][S99]` -> UNVERIFIED_ABSENCE / FAIL (accidental, see R9P1-02); c52 grounded FACTUAL + absence `[S99]` -> FAIL.

Store-side id forms: c62 store holds Latin `S1` and Cyrillic `Ѕ1`, draft `[S1]` resolves the Latin record (correct); c63 store holds only Cyrillic `Ѕ1` -> `[S1]` UNVERIFIED_CITATION / FAIL (NFKC does not fold, no confusable collision); c64 store id `[S1]` -> UNVERIFIED_CITATION; c65 store id `S1 ` (trailing space) -> UNVERIFIED_CITATION. A draft `[Ѕ1]` (Cyrillic) never matches `_CITATION_RE`, so it cannot be resolved to the Cyrillic record either.

Source reading (no run needed): `resolve` is a plain `dict.get` on the NFKC'd, bracket-stripped marker — it cannot return a record for a key the (NFKC'd) store does not contain; prefix/int/case-insensitive matching does not exist. The only "resolves something not literally in the file" path is NFKC folding on BOTH sides (R9P1-04 B, c18, c66).
