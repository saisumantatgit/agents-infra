The headline answer is that "No first-party feature surveyed is a post-hoc verifier that takes an arbitrary (draft, evidence) pair with no model in the loop and returns a deterministic verdict" [S2].

Google's Check Grounding API is post-hoc, since it "takes an already-produced `answerCandidate` plus up to 200 `facts` as separate inputs" [S2].

Anthropic's Citations API is vendor-reported as "increasing recall accuracy by up to 15%" versus custom prompt-based implementations, with no independent replication found [S2].

For AWS Bedrock ApplyGuardrail, the check is "still a trained relevance/grounding classifier, not a symbolic span-matcher, and AWS publishes no accuracy numbers for it at all" [S2].

The note was "Compiled for the Agent-Assure moat-vs-market-redundancy question" on a research date of 2026-09-12 [S2].
