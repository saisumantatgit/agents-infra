The review reports that "GPT-4 as a grounding judge scores 75.3% balanced accuracy on LLM-AggreFact; MiniCheck-FT5, a 770M model you can run on a laptop, scores 74.7%" [S1].

On determinism, "1,000 completions at temperature 0 from one model produced 80 unique outputs", which the review traces to the serving stack rather than the caller [S1].

Prompt injection is a real threat, because "Optimization-based prompt injection embedded in the evaluated content achieves 90.8% average attack success against LLM judges" [S1].

The recommendation is to "Add a model tier, but make it a small purpose-built grounding classifier running locally" and not a frontier API call [S1].

Cost is the other side of the comparison, at "a 0.6-point difference at ~446× the cost ($107 vs $0.24 per 13K claims)" [S1].
