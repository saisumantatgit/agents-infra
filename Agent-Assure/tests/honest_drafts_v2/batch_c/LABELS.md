CANDIDATE labels by an AI agent — NOT gold; only Sai ratifies gold.

All 38 claim units (the gate splits sentences at conjunctions/commas: 30 sentences became 38 units) are written to be true to the cited file (labelled HONEST); a non-GROUNDED/ABSENCE_SUPPORTED verdict is therefore a false alarm candidate.

| draft | claim | CANDIDATE label | gate verdict | AGREE/DISAGREE |
|---|---|---|---|---|
| 1 | On LLM-AggreFact, GPT-4 used as a zero-shot judge reaches 75.3% balanced accuracy [S1] | HONEST | UNGROUNDED | DISAGREE |
| 1 | Claude-3 Opus reaches 74.1% [S1]. | HONEST | UNGROUNDED | DISAGREE |
| 1 | MiniCheck-Flan-T5-Large, at 770M parameters, scores 74.7%, essentially level with GPT-4 [S1]. | HONEST | UNVERIFIED_NUMBER | DISAGREE |
| 1 | The paper's own GPT-4 bill for the test set was $107, against $0.24 for MiniCheck-Flan-T5-Large [S1]. | HONEST | UNGROUNDED | DISAGREE |
| 1 | AlignScore, a 355M RoBERTa-Large model, scores 70.4%, about five points below GPT-4 [S1]. | HONEST | UNVERIFIED_NUMBER | DISAGREE |
| 1 | Bespoke-MiniCheck-7B tops the public leaderboard at 77.4%, but that figure is self-reported by Bespoke Labs [S1]. | HONEST | GROUNDED | AGREE |
| 1 | On FaithBench-hard, HHEM-2.1 scores 52.6% balanced accuracy, while o3-mini-high rises from 68.8% zero-shot to 84.0% when given human-annotated examples for the same article [S1]. | HONEST | UNVERIFIED_NUMBER | DISAGREE |
| 2 | Wang et al. measured a GPT-4 verdict conflict rate of 46.3% under order swapping for one comparison pair, and 82.5% for ChatGPT on one pair [S2]. | HONEST | UNGROUNDED | DISAGREE |
| 2 | On MT-Bench, GPT-4's order-swap consistency was 65.0% against 46.2% for GPT-3.5 [S2]. | HONEST | UNGROUNDED | DISAGREE |
| 2 | Under the repetitive-list attack, Claude-v1 and GPT-3.5 picked the padded answer 91.3% of the time, versus 8.7% for GPT-4 [S2]. | HONEST | UNGROUNDED | DISAGREE |
| 2 | GPT-4 agreed with human experts 85% of the time on second-turn MT-Bench questions, compared with 81% agreement between humans [S2]. | HONEST | UNGROUNDED | DISAGREE |
| 2 | In the self-preference study, GPT-4 scored 0.705 on XSUM [S2] | HONEST | UNGROUNDED | DISAGREE |
| 2 | 0.912 on CNN, where 0.5 means no self-preference [S2]. | HONEST | UNVERIFIED_ABSENCE | DISAGREE |
| 2 | The note found no study that reports repeated-identical-call verdict agreement for a grounding-specific judge [S2]. | HONEST | UNVERIFIED_ABSENCE | DISAGREE |
| 3 | In Table 2 of the MiniCheck paper, GPT-4 scores 75.3% balanced accuracy, MiniCheck-FT5 scores 74.7% [S3] | HONEST | UNVERIFIED_NUMBER | DISAGREE |
| 3 | Claude-3 Opus scores 74.1% [S3]. | HONEST | UNGROUNDED | DISAGREE |
| 3 | The 11B T5-NLI-Mixed model scores only 61.0%, about 14 points below the 770M MiniCheck-FT5 [S3]. | HONEST | UNGROUNDED | DISAGREE |
| 3 | For the 13K-claim test set, self-hosted MiniCheck-FT5 costs $0.24, GPT-4 costs $107 [S3] | HONEST | UNVERIFIED_NUMBER | DISAGREE |
| 3 | Claude-3 Opus costs $165 [S3]. | HONEST | UNGROUNDED | DISAGREE |
| 3 | GPT-4 with atomic decomposition costs $212 [S3] | HONEST | UNGROUNDED | DISAGREE |
| 3 | the paper reports near-zero performance change for GPT-4 from decomposing claims [S3]. | HONEST | UNGROUNDED | DISAGREE |
| 3 | On FaithBench, GPT-4o reaches 56.29%, HHEM-2.1 55.68% and MiniCheck-RoBERTa-L 55.03% [S3]. | HONEST | UNGROUNDED | DISAGREE |
| 3 | The note judges FaithJudge undeployable as a gate because it needs human annotations for the specific document at inference time [S3]. | HONEST | UNGROUNDED | DISAGREE |
| 4 | Anthropic's launch blog claims Citations increases recall accuracy by up to 15% against most custom implementations, a vendor-reported figure with no independent replication found [S4]. | HONEST | UNVERIFIED_ABSENCE | DISAGREE |
| 4 | Citations is generation-time only, because the same model call that answers the question emits the citation objects [S4]. | HONEST | UNGROUNDED | DISAGREE |
| 4 | Vertex AI Check Grounding takes an answer candidate plus up to 200 facts [S4] | HONEST | UNGROUNDED | DISAGREE |
| 4 | returns support scores between 0 and 1, with latency documented under 500ms [S4]. | HONEST | UNGROUNDED | DISAGREE |
| 4 | Azure Groundedness detection takes text plus grounding sources, is optimized for English [S4] | HONEST | UNGROUNDED | DISAGREE |
| 4 | publishes no precision or recall numbers [S4]. | HONEST | UNVERIFIED_ABSENCE | DISAGREE |
| 4 | AWS Bedrock's contextual grounding check has a configurable threshold from 0 to 0.99 [S4] | HONEST | UNGROUNDED | DISAGREE |
| 4 | the AWS docs publish no accuracy figures [S4]. | HONEST | UNVERIFIED_ABSENCE | DISAGREE |
| 4 | The note finds no first-party feature that is a post-hoc verifier returning a deterministic verdict with no model in the loop [S4]. | HONEST | UNVERIFIED_ABSENCE | DISAGREE |
| 5 | The STORM paper (Shao et al., NAACL 2024, arXiv:2402.14207) reports citation recall of 84.83% and citation precision of 85.18% [S5]. | HONEST | UNVERIFIED_NUMBER | DISAGREE |
| 5 | Those figures come from Mistral-7B-Instruct judging whether the cited passage entails each generated sentence, so the metric is itself an LLM call [S5]. | HONEST | UNGROUNDED | DISAGREE |
| 5 | In the paper's error analysis, improper inferential linking is the most common failure category, ahead of classic factual hallucination [S5]. | HONEST | UNGROUNDED | DISAGREE |
| 5 | Seven of ten editor-evaluators in the human study said STORM output reads as emotional or unneutral [S5]. | HONEST | UNVERIFIED_NUMBER | DISAGREE |
| 5 | CiteAudit reaches 97% on synthetic cases but 90% on real-world ones [S5]. | HONEST | UNGROUNDED | DISAGREE |
| 5 | The design spec for Agent-Assure was never committed, so the note relies on PHASE2-SEQUENCING.md dated 2026-07-03 [S5]. | HONEST | UNGROUNDED | DISAGREE |
