# B: Demand for contradiction / faithfulness / entailment checking (as of 2026-10-03)

Labels: [MEAS] = published measurement; [VENDOR] = vendor marketing/docs; [INFER] = my inference. Nothing older than 18 months flagged unless noted.

## Conclusions
1. Demand is real and crowded: faithfulness/groundedness/hallucination detection is a standard feature of every LLM eval/observability platform (Braintrust, Galileo, Arize, Patronus, Ragas, TruLens, Promptfoo) and of hyperscaler guardrails (AWS Bedrock). It is sold as a feature, rarely standalone. [VENDOR]
2. Best-supported claim: the SOTA checker is a model, probabilistic, and mediocre. MiniCheck-FT5 74.7% balanced acc vs GPT-4 75.3% on LLM-AggreFact (EMNLP 2024, 2024-11); HHEM-2.1-Open 64.4% (RAGTruth-Summ) / 74.3% (RAGTruth-QA) balanced acc. [MEAS, partly vendor-reported]. Not gate-grade by itself.
3. Independent evidence says even these scores overstate usefulness: five SOTA evaluators disagree at instance level, trade TPR/TNR differently per dataset, and miss unattributable claims that closely paraphrase the source (Godbole & Jia, arXiv 2501.14883, 2025-01; ~20 months old, flag). Vectara itself (EMNLP Industry 2025-11) says fine-tuned detectors and LLM judges "continue to struggle".
4. So Agent-Assure's lack of contradiction detection is a real but SMALLER gap than it looks: the buyer who wants "actually supported" has only ~65-85% balanced-accuracy, non-deterministic-or-pinned-model options. Agent-Assure's differentiator (deterministic, refuses what it cannot trace) is not offered by those tools. [INFER]
5. Weakest claim: buyer segments/triggers and willingness to pay. I found tool prices and incident anecdotes but NO survey/budget data tying a purchase to a faithfulness check specifically. Triggers below are INFERRED.

## 1. Category terms
- Terms with vendor/listicle volume: "hallucination detection", "RAG evaluation", "groundedness/contextual grounding", "faithfulness", "LLM-as-judge". Seen in Braintrust (2026-05-19), Giskard, FutureAGI 2026 roundups. [VENDOR; SEO-driven, volume UNVERIFIED]
- "Factual consistency"/"NLI/entailment"/"AutoAIS" are research terms (MiniCheck, AlignScore, LLM-AggreFact); buyers say "hallucination"/"groundedness". [INFER from where each term appears]
- Vendors by term: Vectara HHEM (faithfulness), Patronus Lynx (hallucination), Galileo Luna/ChainPoll, AWS Bedrock Guardrails contextual grounding, Ragas/TruLens/Phoenix (open source), Promptfoo (CI).

## 2. Who buys / triggers
- Evidence only for the product surface: tools are pitched at pre-deployment eval + CI gates, production monitoring, and runtime guardrails (Braintrust article). Sectors targeted: fintech, insurance, regulated domains (FutureAGI, Patronus FinanceBench). [VENDOR]
- Incidents that motivate the category: Moffatt v. Air Canada, 2024 BCCRT 149 (chatbot invented policy, C$650.88 damages; 2024-02); Mata v. Avianca fabricated citations (2023-06), still an active "fictitious case law" problem in Canada 2026 (National Magazine, 2026). [INDEPENDENT news]. I did NOT find a source linking a specific incident to a guardrail purchase. Trigger ranking (incident > launch gate > CI > mandate) is [INFER]; the CI/launch-gate framing is [VENDOR].
- Roles: AI/ML platform and RAG developers (tool users); legal/finance/compliance owners (risk owners). [INFER]

## 3. Pricing/packaging
- Ragas Apache-2.0 free; TruLens free; Phoenix self-host free; Lynx weights open. [VENDOR via FutureAGI roundup 2026]
- Patronus hosted evaluators ~$10-20 per 1,000 calls [VENDOR via roundup, UNVERIFIED at source]. Galileo free 5k traces/mo, paid from $100/mo [same]. Arize AX Pro $50/mo [same].
- AWS Bedrock contextual grounding check: $0.10 per 1,000 text units (1 unit = up to 1,000 chars) [secondary sources; verify at AWS]. Documented as probabilistic with configurable threshold.
- Pattern: open-source core + paid hosted/enterprise, or platform feature. No standalone high-priced "faithfulness product" found. [INFER] Willingness to pay for the check alone is therefore low; value accrues to the platform.

## 4. Accuracy ceiling
- MiniCheck-FT5 74.7 / GPT-4 75.3 / Claude-3-Opus 74.1 / AlignScore 70.4 balanced acc, LLM-AggreFact [MEAS, EMNLP 2024].
- HHEM-2.1-Open (110M params, flan-t5-base): 64.42% RAGTruth-Summ, 74.28% RAGTruth-QA balanced acc; <600MB RAM, ~1.5s per 2k tokens on CPU [VENDOR, Vectara; trained on RAGTruth train set, so in-domain].
- Lynx (Patronus, paper 2024-07, >18 months old): claims +~1% over GPT-4o avg on HaluBench; GPT-4o 84.3% on RAGTruth in their table [VENDOR]. Fine-grained numbers not verified.
- Godbole & Jia: low instance-level agreement among SOTA, poor system-level error-rate estimates, weakness on high-overlap/paraphrased unsupported claims [MEAS/INDEPENDENT]. Note this is the same failure class (surface similarity) that Agent-Assure's span matching also has.
- Cost/call: LLM judge = one LLM call per claim set; local HHEM/MiniCheck = CPU/GPU seconds, no per-call fee; Bedrock $0.10/1k units. [mixed]
- Gate-worthy? On these numbers a 25-35% balanced-error checker cannot be a release gate alone; vendors themselves recommend human validation (Braintrust, Godbole). [INFER from MEAS]

## 5. Determinism
- No credible checker found that runs with no model. All are models. Distinction: local pinned models (HHEM-2.1-Open, MiniCheck, AlignScore, DeBERTa NLI) are repeatable given fixed weights/hardware, but still probabilistic classifiers with the errors above. API LLM judges are neither pinned nor repeatable. Agent-Assure's "zero model" verdict path is, as far as I found, unique among faithfulness-adjacent tools, but it checks traceability, not support. [INFER]

## WHAT I SEARCHED AND DID NOT FIND
Queries: "Vectara HHEM hallucination leaderboard 2026"; "MiniCheck AlignScore LLM-AggreFact balanced accuracy"; "RAG faithfulness evaluation pricing Galileo Patronus Lynx Arize TruLens Ragas guardrails"; Exa: LLM-as-judge reliability RAGTruth F1; Bedrock grounding price; Vertex check-grounding price; Lynx HaluBench; Air Canada/Avianca; HHEM-2.1 accuracy.
NOT_LOCATED: any buyer survey, analyst (Gartner/Forrester) sizing, or named-customer purchase tied to faithfulness checking; Vertex "check grounding" per-call price (got other grounding prices only); primary-source pricing pages (all prices via roundups); RAGAS faithfulness accuracy vs human labels; FACTS benchmark numbers; Vectara 2026 leaderboard numbers beyond secondary snippets (rates 0.6-10% are generation hallucination rates, not detector accuracy). Absence here means not found by these queries, not no demand.

## IF I WERE WRONG
- If a regulator/standard (EU AI Act, sector rule) requires "support" evidence, buyers would pay for even 75%-accurate checks and the gap would widen. Not checked.
- If newer 2026 detectors reach ~90%+ balanced accuracy on realistic data, the "ceiling" argument weakens; my accuracy numbers are mostly 2024-2025 and Vectara/Patronus figures are vendor-reported.
- Load-bearing assumption: that LLM-AggreFact/RAGTruth balanced accuracy transfers to Agent-Assure's target drafts (multi-claim, cited). Unverified.
