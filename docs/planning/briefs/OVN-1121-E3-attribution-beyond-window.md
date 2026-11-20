# Brief E3: refuse a claim whose source sentence opens with an attribution beyond the 5-token window (fail-closed)

Executor: Codex (or Claude Opus on Sai's word). Branch `fix-e3-attribution` from main. Read repo-root
CLAUDE.md first. If this spec conflicts with the repo, STOP and say where. Fail-closed only.

## The hole (main d8c2ec0; plain control PASS)
Source sentence: "According to an anonymous forum post, Quay Trust was acquired by a larger rival last
spring." Draft: "Quay Trust was acquired by a larger rival last spring [S1]." → PASS 100. With 5 tokens
("According to a forum post, …") it is refused; 6 and 7 tokens PASS. Cause: `_SPAN_HEDGE_LOOKBACK = 5`
(ground_check.py:1665) only inspects 5 tokens; the round-7 "hedge beyond the window" class (comment at
the J-19 / OI-MOAT-27 block) is still open for sentence-initial attribution frames.

## Do
1. Systemic: when the matched span sits inside a sentence that OPENS with an attribution frame
   ("According to …,", "Per …,", "As reported by …,", "In the words of …,", "<Source> says/claims/
   reports that"), refuse at any distance up to the end of the frame, not only within 5 tokens. Prefer a
   structural signal (the frame opens the sentence and ends at the clause comma or "that") over a longer
   word list, per CLAUDE.md "never key a moat rule on a surface property the author controls".
2. Siblings to test: the frame after the claim ("…, according to an anonymous forum post."); the frame in
   a parenthesis; the frame split by a line break; a long frame (10+ tokens).
3. Honest controls: "According to the 2025 annual report, revenue rose 4%." cited to THAT report should
   stay as main treats it today. State honestly that today it is refused (5-token rule) when the frame is
   short, so measure the Error-A change and list every honest claim lost.
4. Proven-red tests in tests/red_team_moat/; r42 structural guard re-pinned only if additive.

## Measure / Deliver
As in E1 (both fabrication corpora, Error-A corpus, usage_genres, gold md5). reports/E3-ATTRIBUTION.md.
Do not push. Final message ≤ 30 lines.
