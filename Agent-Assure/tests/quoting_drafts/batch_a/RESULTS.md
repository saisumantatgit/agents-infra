# Quoting test, batch A: results

Question: does a writer who follows the guide's advice (quote the source, cite [Sn] inside the sentence) get a PASS?

Answer: no. 0 of 10 drafts reached PASS (all FAIL). See the summary table, then per-claim rows.

Hypotheses by an AI agent — testimony; the orchestrator traces causes in code

Store: store.jsonl, built through scripts/capture_hook.py from the 5 real files (S1 README.md, S2 grounding-failure-types.md, S3 ADR-006, S4 ADR-007, S5 ADR-009), all verbatim. Every quotation was machine-checked as an exact substring of its source before the run. Reports: draft_*.md.report.json. Note: my draft titles (a '# ...' line) are claims to the checker in drafts 2-5 (UNCITED); they are listed but excluded from the per-variant counts below.

| Variant | Segments (excl. titles) | GROUNDED | Drafts PASS |
|---|---|---|---|
| literal | 27 | 2 | 0 of 5 |
| natural | 36 | 7 | 0 of 5 |

Gate per draft: draft_1_literal.md FAIL (16.7); draft_1_natural.md FAIL (55.6); draft_2_literal.md FAIL (0.0); draft_2_natural.md FAIL (0.0); draft_3_literal.md FAIL (0.0); draft_3_natural.md FAIL (0.0); draft_4_literal.md FAIL (14.3); draft_4_natural.md FAIL (12.5); draft_5_literal.md FAIL (0.0); draft_5_natural.md FAIL (11.1)

Most common non-GROUNDED shapes (variant, verdict, engine diagnostic): ('natural', 'UNGROUNDED', 'cited_sentence_may_not_assert_claim'): 14; ('literal', 'UNGROUNDED', 'cited_sentence_may_not_assert_claim'): 13; ('natural', 'UNGROUNDED', 'no_hedge_in_cited_sentence'): 13; ('literal', 'UNGROUNDED', 'no_hedge_in_cited_sentence'): 12; ('natural', 'UNCITED', 'no_cited_verbatim_source'): 1; ('natural', 'UNVERIFIED_ABSENCE', 'no_hedge_in_cited_sentence'): 1

Authored claims vs segments: each variant has 25 authored claims (5 per draft). The decomposer split some of them into fragments (literal 27 segments, natural 36), so segment counts are not claim counts. Counting an authored claim as GROUNDED only if every fragment is GROUNDED: literal 0 of 25, natural 1 of 25 (draft 1 'Refusing a note is recoverable in one keystroke; deleting a claim is not', which the splitter cut at ';' and each half is a whole-fragment source span). The 2 literal GROUNDED segments are fragments of claims whose other fragment failed.

Root-cause lead for the orchestrator (read from scripts/ground_check.py t1_verbatim, lines ~1563-1700, not yet traced end to end): T1 certifies only if (a) the whole segment is a contiguous source span, or (b) an 8+ token span matches AND every content word of the segment is in the source vocabulary AND the span starts at the segment's first content word. A guide-style sentence ('The README states there are "..." [S1]') adds own framing words that are not in the source, so (b) fails; and the quotes the guide's own example models are 5 words, so (a)/(b) never reach the floor.

## Per-claim results (claims as the checker segmented them)

Quote-len = words inside double quotes in that segment (0 if none in the segment). Hypothesis column only for non-GROUNDED.

| Draft | Variant | # | Claim segment | Verdict | Quote-len | Hypothesis |
|---|---|---|---|---|---|---|
| 1 | literal | 1 | The README states there are "No LLM calls during grounding" [S1]. | UNGROUNDED | 5 | framing words not in source (readme) fail the residual-coverage rule; quote is 5 words, under the 8-token floor, and the whole segment is not a contiguous source span |
| 1 | literal | 2 | The capture hook, per the README, "appends a verbatim-tagged record" [S1]. | UNGROUNDED | 5 | framing words not in source (readme) fail the residual-coverage rule; quote is 5 words, under the 8-token floor, and the whole segment is not a contiguous source span |
| 1 | literal | 3 | The README warns that a misplaced marker "becomes its own segment" [S1]. | UNGROUNDED | 4 | framing words not in source (readme, warns, misplaced) fail the residual-coverage rule; quote is 4 words, under the 8-token floor, and the whole segment is not a contiguous source span |
| 1 | literal | 4 | For summarised pages, the README says "the gate refuses to certify against it" [S1]. | UNGROUNDED | 7 | framing words not in source (summarised, pages, readme) fail the residual-coverage rule; quote is 7 words, under the 8-token floor, and the whole segment is not a contiguous source span |
| 1 | literal | 5 | On authoring notes, the README says only a comment that "opens [S1] | UNGROUNDED | 2 | framing words not in source (readme) fail the residual-coverage rule; quote is 2 words, under the 8-token floor, and the whole segment is not a contiguous source span; segment is a FRAGMENT: the decomposer split the sentence mid-quote or at ';' / ', and' / 'and' |
| 1 | literal | 6 | closes on the same line" is stripped [S1]. | GROUNDED | 3 |  |
| 1 | natural | 1 | Agent-Assure's README says "the engine is pure Python, deterministic, and audit-defensible" [S1]. | UNGROUNDED | 9 | framing words not in source (readme) fail the residual-coverage rule |
| 1 | natural | 2 | Only a comment that opens [S1] | UNGROUNDED | 0 | no quotation in this segment; whole segment is not a verbatim span |
| 1 | natural | 3 | closes on the same line is stripped [S1]. | GROUNDED | 0 |  |
| 1 | natural | 4 | The README notes that a marker placed after the period "becomes its own segment [S1] | UNGROUNDED | 5 | framing words not in source (readme, placed) fail the residual-coverage rule; quote is 5 words, under the 8-token floor, and the whole segment is not a contiguous source span; segment is a FRAGMENT: the decomposer split the sentence mid-quote or at ';' / ', and' / 'and' |
| 1 | natural | 5 | detaches from its claim" [S1]. | GROUNDED | 1 |  |
| 1 | natural | 6 | The native WebFetch summary is tagged [S1] | UNGROUNDED | 0 | no quotation in this segment; whole segment is not a verbatim span |
| 1 | natural | 7 | "the gate refuses to certify against it" [S1]. | GROUNDED | 7 |  |
| 1 | natural | 8 | Refusing a note is recoverable in one keystroke [S1] | GROUNDED | 0 |  |
| 1 | natural | 9 | deleting a claim is not [S1]. | GROUNDED | 0 |  |
| 2 | literal | 0 | # Failure types reference notes | UNCITED | 0 | Draft title line was segmented as a claim and has no citation; a header is NON_CLAIM only in draft 1 (not a quote problem; my own authoring choice). |
| 2 | literal | 1 | The reference says a GROUNDED verdict is "the only state that certifies" provenance [S2]. | UNGROUNDED | 5 | framing words not in source (provenance) fail the residual-coverage rule; quote is 5 words, under the 8-token floor, and the whole segment is not a contiguous source span |
| 2 | literal | 2 | On UNCITED, it says such a claim is "indistinguishable from an assertion the model invented" [S2]. | UNGROUNDED | 7 | quote is 7 words, under the 8-token floor, and the whole segment is not a contiguous source span |
| 2 | literal | 3 | For summaries, it warns of "a second model's paraphrase" [S2]. | UNGROUNDED | 5 | framing words not in source (summaries, warns) fail the residual-coverage rule; quote is 5 words, under the 8-token floor, and the whole segment is not a contiguous source span |
| 2 | literal | 4 | An UNVERIFIED_CITATION means "The source was never retrieved this session" [S2]. | UNGROUNDED | 7 | framing words not in source (means) fail the residual-coverage rule; quote is 7 words, under the 8-token floor, and the whole segment is not a contiguous source span |
| 2 | literal | 5 | Headers and opinion are "excluded from the scored denominator" [S2]. | UNGROUNDED | 5 | quote is 5 words, under the 8-token floor, and the whole segment is not a contiguous source span |
| 2 | natural | 0 | # Failure types reference notes | UNCITED | 0 | Draft title line was segmented as a claim and has no citation; a header is NON_CLAIM only in draft 1 (not a quote problem; my own authoring choice). |
| 2 | natural | 1 | A claim's verdict is a fact about the evidence store, not an opinion [S2]. | UNGROUNDED | 0 | no quotation in this segment; whole segment is not a verbatim span |
| 2 | natural | 2 | The reference argues that "Value-and-unit matching stops a claim from borrowing a source's digits while changing their meaning" [S2]. | UNGROUNDED | 17 | framing words not in source (argues) fail the residual-coverage rule |
| 2 | natural | 3 | For re-retrieval it advises a raw Read, because "native WebFetch returns a Haiku summary" [S2]. | UNGROUNDED | 6 | framing words not in source (retrieval, advises) fail the residual-coverage rule; quote is 6 words, under the 8-token floor, and the whole segment is not a contiguous source span |
| 2 | natural | 4 | An uncited factual claim is indistinguishable from an assertion the model invented [S2]. | UNGROUNDED | 0 | no quotation in this segment; whole segment is not a verbatim span |
| 2 | natural | 5 | It says that a single glance "is not evidence of absence — it is absence of evidence" [S2]. | UNGROUNDED | 10 | quote >=8 words and no missing words, so likely subject-anchor rule (span must start at the claim's first content word) or a line break/tokenization in source; diagnostic: cited_sentence_may_not_assert_claim |
| 3 | literal | 0 | # ADR-006 notes | UNCITED | 0 | Draft title line was segmented as a claim and has no citation; a header is NON_CLAIM only in draft 1 (not a quote problem; my own authoring choice). |
| 3 | literal | 1 | ADR-006 states that "T2 no longer decides any verdict" [S3]. | UNGROUNDED | 6 | framing words not in source (states) fail the residual-coverage rule; quote is 6 words, under the 8-token floor, and the whole segment is not a contiguous source span |
| 3 | literal | 2 | It describes T2 as "a bag of words" [S3]. | UNGROUNDED | 4 | framing words not in source (describes) fail the residual-coverage rule; quote is 4 words, under the 8-token floor, and the whole segment is not a contiguous source span |
| 3 | literal | 3 | The retired option "raises rather than silently doing nothing" [S3]. | UNGROUNDED | 6 | framing words not in source (option) fail the residual-coverage rule; quote is 6 words, under the 8-token floor, and the whole segment is not a contiguous source span |
| 3 | literal | 4 | Its load-bearing assumption is "That honest drafts quote more often than they paraphrase" [S3]. | UNGROUNDED | 9 | quote >=8 words and no missing words, so likely subject-anchor rule (span must start at the claim's first content word) or a line break/tokenization in source; diagnostic: cited_sentence_may_not_assert_claim |
| 3 | literal | 5 | The ADR records that "Honest paraphrase now reads UNGROUNDED" [S3]. | UNGROUNDED | 5 | framing words not in source (records) fail the residual-coverage rule; quote is 5 words, under the 8-token floor, and the whole segment is not a contiguous source span |
| 3 | natural | 0 | # ADR-006 notes | UNCITED | 0 | Draft title line was segmented as a claim and has no citation; a header is NON_CLAIM only in draft 1 (not a quote problem; my own authoring choice). |
| 3 | natural | 1 | A tier that cannot distinguish a claim from its inversion, or from its falsification, is not measuring support [S3]. | UNGROUNDED | 0 | no quotation in this segment; whole segment is not a verbatim span |
| 3 | natural | 2 | ADR-006 concludes that such a tier "is not measuring support. | UNCITED | 4 | framing words not in source (concludes) fail the residual-coverage rule; quote is 4 words, under the 8-token floor, and the whole segment is not a contiguous source span; segment is a FRAGMENT: the decomposer split the sentence mid-quote or at ';' / ', and' / 'and' |
| 3 | natural | 3 | It is measuring vocabulary reuse" [S3]. | UNGROUNDED | 1 | quote is 1 words, under the 8-token floor, and the whole segment is not a contiguous source span; segment is a FRAGMENT: the decomposer split the sentence mid-quote or at ';' / ', and' / 'and' |
| 3 | natural | 4 | When the whole claim is quoted, "it grounds regardless of length" [S3]. | UNGROUNDED | 5 | framing words not in source (quoted) fail the residual-coverage rule; quote is 5 words, under the 8-token floor, and the whole segment is not a contiguous source span |
| 3 | natural | 5 | Waiting for T3 was rejected because it "Leaves five demonstrated fabrications passing for the weeks T3 takes" [S3]. | UNGROUNDED | 10 | framing words not in source (waiting, because) fail the residual-coverage rule |
| 3 | natural | 6 | The 52 calibration claims were authored for calibration [S3] | UNGROUNDED | 0 | no quotation in this segment; whole segment is not a verbatim span |
| 3 | natural | 7 | they are not a sample of user drafts [S3]. | UNGROUNDED | 0 | no quotation in this segment; whole segment is not a verbatim span |
| 4 | literal | 0 | # ADR-007 notes | UNCITED | 0 | Draft title line was segmented as a claim and has no citation; a header is NON_CLAIM only in draft 1 (not a quote problem; my own authoring choice). |
| 4 | literal | 1 | ADR-007 decides that "Relational grounding decides nothing" [S4]. | UNGROUNDED | 4 | quote is 4 words, under the 8-token floor, and the whole segment is not a contiguous source span |
| 4 | literal | 2 | Round 12 found Error-B shapes, "two of them CRITICAL" [S4]. | UNGROUNDED | 4 | quote is 4 words, under the 8-token floor, and the whole segment is not a contiguous source span |
| 4 | literal | 3 | The preserved diagnostic is information for a human, "never an input to a verdict" [S4]. | UNGROUNDED | 6 | quote is 6 words, under the 8-token floor, and the whole segment is not a contiguous source span |
| 4 | literal | 4 | UNVERIFIED_RELATION stays in the taxonomy [S4] | GROUNDED | 0 |  |
| 4 | literal | 5 | "becomes unreachable from the verdict path" [S4]. | UNGROUNDED | 6 | quote is 6 words, under the 8-token floor, and the whole segment is not a contiguous source span |
| 4 | literal | 6 | The ADR cites evidence that "incremental repair here does not converge" [S4]. | UNGROUNDED | 6 | framing words not in source (cites) fail the residual-coverage rule; quote is 6 words, under the 8-token floor, and the whole segment is not a contiguous source span |
| 4 | natural | 0 | # ADR-007 notes | UNCITED | 0 | Draft title line was segmented as a claim and has no citation; a header is NON_CLAIM only in draft 1 (not a quote problem; my own authoring choice). |
| 4 | natural | 1 | Two prior fixes in this area were themselves withdrawn within hours of landing (D-52 → D-54 [S4] | UNGROUNDED | 0 | no quotation in this segment; whole segment is not a verbatim span |
| 4 | natural | 2 | D-68 → D-69), which is the strongest available evidence that incremental repair here does not converge [S4]. | UNGROUNDED | 0 | no quotation in this segment; whole segment is not a verbatim span |
| 4 | natural | 3 | The ADR calls the old rule "a surface statistic standing in for a meaning" [S4]. | UNGROUNDED | 8 | framing words not in source (old) fail the residual-coverage rule |
| 4 | natural | 4 | The decision is that "Relational grounding decides nothing" [S4]. | UNGROUNDED | 4 | quote is 4 words, under the 8-token floor, and the whole segment is not a contiguous source span |
| 4 | natural | 5 | A relational claim now "falls through to the ordinary citation/verbatim path" [S4]. | UNGROUNDED | 8 | quote >=8 words and no missing words, so likely subject-anchor rule (span must start at the claim's first content word) or a line break/tokenization in source; diagnostic: no_hedge_in_cited_sentence |
| 4 | natural | 6 | The old rule was reconstructing "this source asserts a relation between A [S4] | UNGROUNDED | 8 | framing words not in source (old) fail the residual-coverage rule; segment is a FRAGMENT: the decomposer split the sentence mid-quote or at ';' / ', and' / 'and' |
| 4 | natural | 7 | B" out of token co-occurrence [S4]. | GROUNDED | 6 |  |
| 5 | literal | 0 | # ADR-009 notes | UNCITED | 0 | Draft title line was segmented as a claim and has no citation; a header is NON_CLAIM only in draft 1 (not a quote problem; my own authoring choice). |
| 5 | literal | 1 | ADR-009 is titled "Absence claims are reported, never certified" [S5]. | UNGROUNDED | 6 | framing words not in source (titled) fail the residual-coverage rule; quote is 6 words, under the 8-token floor, and the whole segment is not a contiguous source span |
| 5 | literal | 2 | Its status says it is "NOT accepted until he merges" [S5]. | UNGROUNDED | 5 | framing words not in source (says) fail the residual-coverage rule; quote is 5 words, under the 8-token floor, and the whole segment is not a contiguous source span |
| 5 | literal | 3 | The ADR admits that "the usage price is unmeasured" [S5]. | UNGROUNDED | 5 | framing words not in source (admits) fail the residual-coverage rule; quote is 5 words, under the 8-token floor, and the whole segment is not a contiguous source span |
| 5 | literal | 4 | The upgrade path is to "capture real search queries" [S5]. | UNGROUNDED | 4 | quote is 4 words, under the 8-token floor, and the whole segment is not a contiguous source span |
| 5 | literal | 5 | The remaining hole involves "pages the agent picked" [S5]. | UNGROUNDED | 4 | framing words not in source (remaining, hole, involves) fail the residual-coverage rule; quote is 4 words, under the 8-token floor, and the whole segment is not a contiguous source span |
| 5 | natural | 0 | # ADR-009 notes | UNCITED | 0 | Draft title line was segmented as a claim and has no citation; a header is NON_CLAIM only in draft 1 (not a quote problem; my own authoring choice). |
| 5 | natural | 1 | Round 20 to round 23 closed the cheapest routes (failed and blank fetches counted as searches) [S5] | UNGROUNDED | 0 | no quotation in this segment; whole segment is not a verbatim span |
| 5 | natural | 2 | the class remains: two SUCCESSFUL fetches of pages the agent picked can still certify that something does not exist [S5]. | UNVERIFIED_ABSENCE | 0 | Absence-shaped words ('does not exist') routed to the absence rule, which never certifies (ADR-009); the segment also quotes nothing. |
| 5 | natural | 3 | The ADR says the searches are strings, "URLs [S5] | UNGROUNDED | 2 | framing words not in source (says) fail the residual-coverage rule; quote is 2 words, under the 8-token floor, and the whole segment is not a contiguous source span; segment is a FRAGMENT: the decomposer split the sentence mid-quote or at ';' / ', and' / 'and' |
| 5 | natural | 4 | file paths the drafting agent chose" [S5]. | UNGROUNDED | 1 | quote is 1 words, under the 8-token floor, and the whole segment is not a contiguous source span; segment is a FRAGMENT: the decomposer split the sentence mid-quote or at ';' / ', and' / 'and' |
| 5 | natural | 5 | The ADR records that "Four tripwires close BY DEMOTION, not repair" [S5]. | UNGROUNDED | 7 | framing words not in source (records) fail the residual-coverage rule; quote is 7 words, under the 8-token floor, and the whole segment is not a contiguous source span |
| 5 | natural | 6 | It would be reversed by "A customer job where absence is the product" [S5]. | UNGROUNDED | 8 | framing words not in source (reversed) fail the residual-coverage rule |
| 5 | natural | 7 | The sample is one row [S5] | UNGROUNDED | 0 | no quotation in this segment; whole segment is not a verbatim span |
| 5 | natural | 8 | the usage price is unmeasured [S5]. | GROUNDED | 0 |  |
