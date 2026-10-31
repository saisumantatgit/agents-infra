# S1 diagnosis: "Blank lines are skipped [S1]." UNGROUNDED against README

Verdict: false alarm (Error-A) from a blunt lexical guard; the refusal protects nothing here. Fix is PASS-enabling, so it is Sai's call.

Root cause: scripts/ground_check.py `_span_is_hedged` (line ~1411) via `_SPAN_HEDGE_TOKENS` (line ~1384). The word "per" is on the list as an attribution hedge ("per the vendor"). `_claim_contained_verbatim` (line ~1561) tokenizes the WHOLE source into one flat stream and looks at the 5 tokens before the match (`_SPAN_HEDGE_LOOKBACK`). README line 73 reads "One JSON object per line. Blank lines are skipped." The 5 tokens before "blank" are one/json/object/per/line, so "per" hits, the span is "hedged", containment is skipped. The claim has 4 tokens (<8), so t1_verbatim's long-span path is unavailable: `ground()` falls to UNGROUNDED.

Trace values (README, claim tokens [blank, lines, are, skipped]): one source match at flat index 602; hedged=True; nonfactive=False. The sentence-unit checks all pass: unit prefix empty, denial False, polarity True, negated_claim_is_limited False, unit not disowned. So the only blocker is the flat 5-token window crossing a sentence boundary.

Minimal repro (RetrievedSource verbatim, FACTUAL claim; scripts in this dir: bisect.py, trace.py):
- "Blank lines are skipped." -> GROUNDED
- "Rain fell. Blank lines are skipped. Sun rose." -> GROUNDED
- "per line. Blank lines are skipped." -> UNGROUNDED (minimal: 2 words before the claim)
- "One JSON object per line. Blank lines are skipped." -> UNGROUNDED
- same with "per" -> "each" or "on every" -> GROUNDED
- "per" 6+ tokens back -> GROUNDED
- paragraph break or heading between "per line." and the claim -> still UNGROUNDED (window ignores structure)
- full README -> UNGROUNDED; README with "per line" reworded -> GROUNDED
Same cause very likely hits the sibling claims in b06 whose preceding sentence has a hedge word within 5 tokens; "One JSON object per line [S1]." also refuses (cause not isolated here; not "per" before the span, since "evidencestore jsonl format" precedes it).

Correct or false alarm: false alarm. "per" is a hedge only in "per the vendor / per X's report". Here it is a preposition in a PREVIOUS sentence about line format. The source asserts the claim in its own voice. Note the guard is documented as deliberately blunt and fail-closed (comment above `_SPAN_HEDGE_TOKENS`), so the refusal is by design, but it costs honest claims.

Fix shape: confine the hedge window to the claim's own sentence unit (use `_source_unit_contexts`: hedge tokens only from `ctx.prefix + ctx.tokens[:i]`, as `_unit_denied` already does), instead of the flat token stream; optionally drop "per" or require "per the|a|an" + noun. Would it let more claims pass: yes. Sentence-bounded window is more permissive than today (any hedge word in a previous sentence stops counting). It would also lose the fail-closed coverage of a hedge just before a sentence break ("Critics claim the following. Redis is slow."), and existing tests pin "per" (tests/test_support_diagnostic.py:190; red_team_moat j19/r7/r8) so it needs red-team re-validation. Per ADR-006/Escalation #1 pattern, PASS-enabling changes are Sai's decision. Not applied.

Load-bearing assumption: the README's "per" is the only hedge in the 5-token window (verified: the "on each" rewording flips it to GROUNDED).
