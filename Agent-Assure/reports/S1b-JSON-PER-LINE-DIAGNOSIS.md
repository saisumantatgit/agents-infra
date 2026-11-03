# "One JSON object per line [S1]." UNGROUNDED against README (agents-infra 41a7e2e)

Verdict: false alarm, same mechanism as the "per" diagnosis but a different hedge word. "per" inside the claim is irrelevant.

Root cause: scripts/ground_check.py `_span_is_hedged` (line 1411-1423) called from `_claim_contained_verbatim` (line 1561). It checks the 5 FLAT source tokens before the match against `_SPAN_HEDGE_TOKENS` (line 1389). README line ~66 ends the prior section "...deleting a claim is not." then "---" and heading "## EvidenceStore JSONL Format". Window before the claim = [is, not, evidencestore, jsonl, format]. "not" (denial hedge) hit -> hedged -> containment skipped. Claim has 5 tokens (<8) so the long-span T1 path is closed -> UNGROUNDED (ClaimKind.ATTRIBUTION because _ATTRIBUTION_RE matches "per "; same code path as FACTUAL, not a cause).

Intermediates: claim tokens [one,json,object,per,line]; one source match at flat index 597; hedged=True, nonfactive=False. Sentence-unit checks all pass (unit prefix = heading tokens, denied=False, polarity True, limited False; _contained_with_matching_polarity True). Only the flat window blocks.

Minimal repro (RetrievedSource verbatim, FACTUAL, t1_verbatim):
- "It is not.\n\n---\n\n## Store Format\n\nOne JSON object per line." -> False
- same with "It is fine." -> True
- "## Store Format\n\nOne JSON object per line." -> True; "not Store Format One JSON ..." -> False
So: any hedge word within 5 tokens, even in a previous section across a horizontal rule and a 3-word heading.

Protective or false alarm: false alarm. The window crosses a section boundary; the source asserts the claim in its own voice. Documented as deliberately blunt/fail-closed.

Fix shape (same as S1-BLANK-LINES-DIAGNOSIS): restrict the hedge window to the claim's own sentence unit (_source_unit_contexts, ctx.prefix + tokens[:i], as _unit_denied does) and treat markdown headings/rules/paragraph breaks as unit boundaries. Strictly more permissive: it would let more claims pass (hedge in previous sentence/section no longer counts) and loses fail-closed coverage of "Critics claim the following. X." Existing tests pin hedge behaviour (tests/test_support_diagnostic.py, red_team_moat) so red-team re-validation required. PASS-enabling -> Sai's ruling. Nothing applied.

Load-bearing assumption: the only hedge in the window is "not" (verified: replacing it with "fine" flips to True).
