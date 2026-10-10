# Q3 — Measured Failure Modes of LLM-as-a-Judge (Grounding/Entailment Gate Focus)

Research pass, 2026-09-12. Every number below carries its source URL and measurement
conditions. Where a number is reported by the authors of the method/model being
evaluated (self-reported), it is flagged `[SELF-REPORTED]`.

---

## 1. Bias catalogue with measured magnitudes

| Bias | Measured magnitude | Model(s) / conditions | Source |
|---|---|---|---|
| **Position bias** (order swap flips verdict) | GPT-4 conflict rate 46.3% (one comparison pair); ChatGPT conflict rate 82.5% (one pair), 52.5% (another) — i.e. swapping candidate order flips the verdict on roughly half to five-sixths of contested comparisons | GPT-4 vs ChatGPT as judges, pairwise comparison, no calibration | Wang et al., "Large Language Models are not Fair Evaluators," arXiv:2305.17926 — https://arxiv.org/abs/2305.17926 |
| **Position bias** (headline example) | Vicuna-13B beats ChatGPT on 66/80 tested queries (82.5%) purely by being placed favorably, with ChatGPT as evaluator | ChatGPT-as-judge, GPT-4 example evaluator | Same as above |
| **Position bias** (MT-Bench formulation) | GPT-4 default-prompt order-swap consistency = 65.0%; GPT-3.5 = 46.2% (i.e., GPT-3.5 flips the verdict on the majority of order-swapped pairs) | GPT-4 vs GPT-3.5, MT-Bench Table 2 | Zheng et al., "Judging LLM-as-a-Judge with MT-Bench and Chatbot Arena," arXiv:2306.05685 — https://arxiv.org/abs/2306.05685 |
| **Position-bias mitigation** | Multiple Evidence Calibration (MEC) + Balanced Position Calibration (BPC) improved human-alignment accuracy by +9.8% (GPT-4) and +14.3% (ChatGPT); adding 20% human-in-the-loop annotation matched/exceeded average human performance while cutting annotation cost up to 39% | Same paper, calibration ablations | arXiv:2305.17926 |
| **Verbosity bias** ("repetitive list" attack — judge fooled by artificially lengthened, content-free answers) | Claude-v1 and GPT-3.5 failure rate 91.3% (judge picks the padded answer); GPT-4 failure rate 8.7% (far more resistant, not immune) | Claude-v1, GPT-3.5, GPT-4 as judges, MT-Bench Table 3 | arXiv:2306.05685 |
| **Self-enhancement / self-preference bias** | GPT-4-as-judge shows ~10 percentage-point higher win rate for its own outputs `[SELF-REPORTED-ADJACENT — GPT-4 judging GPT-4]`; Claude-v1-as-judge shows ~25 pp higher win rate for its own outputs. Authors flag the evidence as directionally consistent but based on limited data | GPT-4, Claude-v1 as both generator and judge | arXiv:2306.05685 |
| **Self-preference bias, mechanism** | Self-preference strength is *linearly correlated* with a model's own self-recognition accuracy (its ability to tell its own text apart from human/other-LLM text) — no single aggregate r reported at abstract level; paper reports per-model pairwise self-preference scores: GPT-4 0.705 (XSUM) / 0.912 (CNN); GPT-3.5 0.582 (XSUM) / 0.431 (CNN); Llama-2 0.511 (XSUM) / 0.505 (CNN) on a 0–1 preference scale (0.5 = no self-preference) | GPT-4, GPT-3.5, Llama-2 as self-judges on summarization (XSUM, CNN/DM) | Panickssery, Bowman & Feng, "LLM Evaluators Recognize and Favor Their Own Generations," arXiv:2404.13076 — https://arxiv.org/abs/2404.13076 (NeurIPS 2024) |
| **12-bias taxonomy (CALM framework)** | Position, Verbosity, Compassion-Fade (named-model vs anonymized-alias treatment), Bandwagon (majority-belief conformity), Distraction (irrelevant detail), Fallacy-Oversight (ignores broken reasoning, grades final answer only), Authority (unsupported authority citation swings verdict), Sentiment, Chain-of-Thought-presence, Self-Enhancement, Refinement-Aware (told "this is a refined answer"), Diversity (demographic-group mentions). Paper reports "significant biases persist in certain specific tasks" across popular models even where overall scores look strong; per-bias percentage table is in the full paper body/appendix (not extracted from abstract-level fetch — flag for anyone needing exact per-bias numbers to pull table 2/3 of the PDF directly) | Multiple popular LLMs, CALM automated modification framework | Ye et al., "Justice or Prejudice? Quantifying Biases in LLM-as-a-Judge," arXiv:2410.02736, ICLR 2025 — https://arxiv.org/abs/2410.02736 ; project page https://llm-judge-bias.github.io/ |
| **Human–judge agreement (ceiling context)** | GPT-4 pairwise agreement with human experts = 85% on second-turn MT-Bench questions, versus 81% human–human agreement (i.e., GPT-4 judge matches or slightly exceeds human-human agreement on this slice) | GPT-4 judge, MT-Bench Table 5 setup S2 | arXiv:2306.05685 |

**Reading for the grounding-gate decision:** every number above is a *symmetric-comparison* bias (pairwise/relative judgment: A vs B, order, length, self vs other). None of these papers measure the specific failure mode this gate cares about — a *single-draft absolute* grounding/entailment judgment ("does source S support claim C") — directly. The transferable finding is that **LLM judges are unreliable exactly on surface features the content author controls** (position, length, self-authorship signal, named-authority mentions) — the same category of vulnerability Agent-Assure's own CLAUDE.md already documents for its deterministic gate (round-3/round-4 red-team notes on token-count and capitalization-keyed rules). This is independent confirming evidence for the project's existing "never key a moat rule on an attacker-controlled surface property" rule — it is now shown to be a property of *LLM judges too*, not just naive heuristics.

---

## 2. Prompt-phrasing sensitivity and run-to-run inconsistency

- **Rating Roulette: Self-Inconsistency in LLM-As-A-Judge Frameworks**, arXiv:2510.27106 (EMNLP Findings 2025) — https://arxiv.org/abs/2510.27106 / https://arxiv.org/pdf/2510.27106
  - Finding: LLM judges show **low self-consistency across NLG tasks and metrics** — repeated identical calls to the same judge on the same input produce materially different scores. "Completeness" scoring showed the largest fluctuation of the metrics tested.
  - Temperature: intuitively, `temperature=0` should remove sampling variance, but the paper reports this **can paradoxically degrade** agreement with human judgments relative to a small positive temperature — i.e., there is a consistency/quality trade-off, not a straightforward "set temp=0 and you're safe" fix.
  - Cross-model: tested GPT-4o, GPT-4o-mini, Gemini-2.5-Flash, Claude-Haiku-4.5, Claude-Sonnet-4.5. Lower temperature stabilizes GPT-4o and Gemini more than it stabilizes the Anthropic models tested. Newer/larger models (e.g., Qwen 3 vs Llama 3.1) are more consistent but **still often fall short of standard reliability thresholds** — the paper does not report a single split-half or Krippendorff's-alpha headline number extractable from this fetch; treat "falls short of standard reliability thresholds" as the paper's own qualitative verdict, not a specific coefficient (flag for follow-up if an exact reliability coefficient is required for the calibration record).
  - Mitigation reported: aggregating multiple judge runs improves agreement with human evaluation (self-consistency / majority-vote style correction) — directionally useful but adds cost and does not fix the underlying instability.
- Related: "Large Language Models are Inconsistent and Biased Evaluators," arXiv:2405.01724 — https://arxiv.org/abs/2405.01724 (title alone, from search; not separately fetched — same claim family: inconsistency and bias treated jointly, consistent with the above).
- **No study found** in this pass that reports a clean "same-prompt, same-input, N repeated identical calls, X% exact-verdict-agreement" number for a grounding/entailment-specific judge (as opposed to general quality scoring). This is a genuine literature gap for Agent-Assure's specific use case — the existing studies measure inconsistency on preference/quality judgments, not on the narrower "is this claim supported by this exact passage" binary task the gate performs. **State this gap plainly: the literature establishes that LLM judges are unstable on quality judgments; it does not directly measure stability on binary entailment/grounding judgments of the kind ground_check.py would need if it ever used an LLM.**

---

## 3. Calibration of LLM-judge confidence/scores

- **Overconfidence in LLM-as-a-Judge: Diagnosis and Confidence-Driven Solution**, arXiv:2508.06225 — https://arxiv.org/abs/2508.06225 / https://arxiv.org/html/2508.06225v2
  - Finding: models such as DeepSeek-R1-0528 and GPT-4o **cluster predictions at high self-reported confidence (90–100%)** while their actual accuracy in that bin is well below the diagonal (ideal calibration) line — classic overconfidence, not merely noise.
  - Metrics used in this line of work: Expected Calibration Error (ECE), Adaptive Calibration Error (ACE), Maximum Calibration Error (MCE), Brier Score, Negative Log-Likelihood (NLL) — the field has converged on ECE/ACE/MCE as the standard trio for judge calibration, alongside a task-specific metric (TH-Score) the authors propose to focus on the high/low-confidence tails where decisions are actually made.
  - Practical implication cited: high-ECE models require increased human oversight to be usable, "diminishing the efficiency of automated judging" — i.e., calibration failure directly erodes the labor-saving rationale for using an LLM judge at all.
- No specific numeric ECE value (e.g., "ECE = 0.18") was extracted from the abstract-level fetches in this pass; the qualitative finding (clustering at 90–100% confidence with sub-90% actual accuracy) is well-supported across the search results but a precise ECE table requires pulling the full-text tables directly — flag as **a number to pull before citing an exact ECE figure in a decision memo**.
- Read for the grounding gate: this is strong corroborating evidence for Agent-Assure's ADR-006 decision to demote lexical/LLM-scored tiers and keep the score gate a *secondary* bar behind a hard "empty retained appendix" requirement (per project CLAUDE.md) — a numeric confidence/score from an LLM judge is exactly the kind of output this literature shows is poorly calibrated and clusters at the extremes, which would make a threshold-based PASS/FAIL cutoff on an LLM confidence score an unsound design choice independent of the moat's other reasons for avoiding LLM calls.

---

## 4. Negation and attribution-reversal handling — MOST IMPORTANT SECTION

### 4a. Negation benchmarks and (pre-reasoning-era) LLM performance

**Truong et al., "Language models are not naysayers: An analysis of language models on negation benchmarks,"** *SEM 2023, arXiv:2306.08189 — https://arxiv.org/abs/2306.08189 / https://arxiv.org/html/2306.08189

Benchmarks and models: GPT-Neo, GPT-3 (175B), InstructGPT (175B) evaluated across MKR-NQ (negated factual statements, n=3,360), MWR (antonym/synonym prediction, n=27,546), SAR (antonym/synonym classification, n=2,000), NegNLI (n=4,500, drawn from SNLI/MNLI/RTE), MoNLI (monotonicity + negation, n=200), NaN-NLI (sub-clausal negation, n=258).

| Model | SAR | SNLI-neg | MNLI-neg | RTE-neg | NaN-NLI | MoNLI |
|---|---|---|---|---|---|---|
| GPT-3 (175B) | 50.1% | 26.7% | 35.9% | 52.5% | 46.9% | 54.0% |
| InstructGPT (175B) | 68.7% | 64.0% | 54.8% | 76.7% | 64.7% | 47.0% |

Key finding — **inverse scaling on negation**: on MKR-NQ, the smallest model tested (GPT-Neo-125M) *outperformed* larger variants; the paper's headline claim is that larger LMs become *more* insensitive to the presence of negation, not less — scaling does not fix this failure mode and can worsen it.

**ScoNe (Scoped Negation NLI),** She et al., arXiv:2305.19426 (ACL 2023 short) — https://arxiv.org/abs/2305.19426 / repo https://github.com/selenashe/ScoNe
- Contrast sets of six examples with up to two negations, where 0/1/2 negative morphemes affect the gold NLI label — designed specifically to test whether a model tracks *scope*, not just presence, of negation.
- In-context learning with InstructGPT (`text-davinci-003`) using the best few-shot chain-of-thought prompt reached 82% overall accuracy, but the authors note this number is **misleading**: it is heavily inflated by the subset of examples where negation could be ignored entirely and the label still guessed correctly — i.e., high aggregate accuracy masks near-chance performance on the scope-sensitive subset.
- RoBERTa/DeBERTa-class models only "solve" ScoNe-NLI after **many-shot fine-tuning** specifically on the phenomenon — not out of the box, and not via prompting alone.

**xNot360 dataset** (negation detection assessment of GPT models), arXiv:2306.16638 — https://arxiv.org/pdf/2306.16638 (surfaced in search, not separately fetched this pass — listed for completeness; treat as unverified detail beyond the title/topic match).

**CondaQA (Contrastive reading comprehension for negation),** Ravichander et al., arXiv:2211.00295 — https://arxiv.org/html/2211.00295
- 14,182 QA pairs from 1,289 Wikipedia passages containing negation.
- Best model (fully fine-tuned UnifiedQA-v2-3B): 73.26% accuracy, 42.18% *consistency* (i.e., giving logically consistent answers across the contrast set, not just per-question accuracy).
- Estimated human performance: 91.94% accuracy, 81.58% consistency.
- The **consistency gap is the more damning number for a grounding gate**: a model can get the majority of individual negated questions "right" in isolation while still contradicting itself across minimally-different negation variants of the same underlying fact — exactly the failure mode that would let a judge pass "Redis loses data [S1]" against a source saying "it is not true that Redis loses data" on one phrasing and correctly reject it on another.

### 4b. Do 2024–2026 reasoning models (GPT-4o, Claude, o1-class) fix negation?

- **No paper found in this pass that runs the classic negation-NLI benchmark suite (NegNLI/ScoNe/CondaQA/MoNLI/NaN-NLI) against GPT-4o, Claude 3.5+/4-class, or o1/o3-class reasoning models with a clean accuracy table.** This is a literature gap, and it should be stated plainly rather than inferred: **the specific "did reasoning models fix negation" question is not directly answered by a benchmark paper found in this search pass.**
- Closest available evidence, and it points the wrong way for reasoning models specifically under adversarial framing: **"Benchmarking Gaslighting Negation Attacks Against Reasoning Models,"** arXiv:2506.09677 — https://arxiv.org/abs/2506.09677. Reports that OpenAI o4-mini's accuracy fell from 73.2% (baseline) to 47.6% after a "gaslighting negation" adversarial prompt was introduced (a 25.6-point drop), and Gemini-2.5-Flash suffered the largest single-benchmark decline (35.4 points) on MathVista under the same attack style. This is a *different* task (math reasoning under adversarial negation-based gaslighting, not entailment/grounding), but it is directly relevant: it shows reasoning-optimized 2025-era models remain **vulnerable to negation-framed adversarial pressure even when their negation-free baseline accuracy is decent** — i.e., reasoning ability does not immunize a model against negation-based attacks, it just raises the pre-attack baseline.
- "Making Language Models Robust Against Negation," arXiv:2502.07717 — https://arxiv.org/abs/2502.07717 / https://arxiv.org/html/2502.07717 — tests only BERT/RoBERTa-scale models with a targeted pre-training fix; explicitly does **not** benchmark GPT-4o/Claude/o1. It cites Truong et al. 2023 approvingly as still-standing evidence that "larger LMs such as GPT-3 and InstructGPT are also insensitive to the presence of negation," with no update for newer frontier models. In an appendix experiment, the authors tried using Llama-2 and GPT-4 to *generate* negation-perturbed sentences (not to be tested on negation understanding) and found both models "consistently made additional modifications to keep the meaning of the sentence intact" instead of performing a clean polarity flip when asked — a small but telling data point that GPT-4-class models resist/struggle with clean negation manipulation even as a generation task, let alone as a judgment task.
- **Bottom line for this section: absence of counter-evidence is not evidence of a fix.** No 2024–2026 paper in this pass demonstrates that GPT-4o/Claude/o1-class judges reliably solve scoped negation or attribution reversal on an entailment-style task. The one adjacent adversarial-robustness data point (o4-mini, gaslighting negation) shows a reasoning model's accuracy nearly halving under negation-framed adversarial pressure. **Recommendation: treat negation/attribution-reversal handling by an LLM judge as unverified-safe, not verified-safe, until a dedicated benchmark run is done against the actual candidate judge model.**

### 4c. Hedging, attribution, and factivity (reported speech, non-factive verbs)

**CommitmentBank** (de Marneffe, Simons & Tonhauser) — https://ojs.ub.uni-konstanz.de/sub/index.php/sub/article/view/601
- Corpus of naturally-occurring discourses where a clausal complement sits under an "entailment-canceling operator" (negation, question, modal, conditional) — precisely the structure of "critics argued that X" or "it is not true that X."
- Central linguistic claim tested: clause-embedding predicates split into **factive** (complement is asserted regardless of the embedding — e.g., "realize that X" commits the speaker to X) vs **non-factive** (complement is *not* asserted — e.g., "claim that X," "argue that X" do not commit the speaker to X). This factive/non-factive distinction is exactly the mechanism behind "critics argued that Redis loses data" not entailing "Redis loses data."
- Evaluating BERT on CommitmentBank (Jiang & de Marneffe, ACL Anthology D19-1630 — https://aclanthology.org/D19-1630/): a state-of-the-art BERT-based model reaches **85% F1** on the three-way commitment-degree task, but the paper's own analysis concludes the model **does not capture the underlying factive/non-factive pragmatic distinction** — it is pattern-matching surface cues that correlate with commitment level in this corpus, not tracking the linguistic mechanism. High aggregate F1 co-existing with "does not encode the actual generalization" is the same shape of risk as the ScoNe finding above (aggregate accuracy inflated by cases where the hard mechanism isn't actually needed).
- **No paper found in this pass that re-runs the CommitmentBank-style factive/non-factive discrimination task against GPT-4o/Claude/modern LLM judges with a reported accuracy number.** This is a second concrete literature gap directly on Agent-Assure's most safety-critical question (does the judge distinguish "X claimed P" from "P is true"). Flag explicitly: **unanswered by the literature surveyed.**

### 4d. Small NLI models (DeBERTa-MNLI) vs LLMs on negation specifically

- DeBERTa-v3 achieves strong general MNLI performance (DeBERTa-large: 91.1/91.1 on MNLI m/mm) and "outperforms almost all large models" on the adversarially-constructed ANLI benchmark, per its architecture/training-objective advantages (disentangled attention + replaced-token-detection pretraining + fine-tuning on curated NLI data including ANLI/WANLI). Source: DeBERTa paper arXiv:2006.03654 — https://arxiv.org/abs/2006.03654; ANLI comparison via HF model cards (MoritzLaurer/DeBERTa-v3-*-mnli-fever-anli-*) — https://huggingface.co/MoritzLaurer/DeBERTa-v3-large-mnli-fever-anli-ling-wanli.
- On negation specifically, the picture is **mixed, not a clean win for DeBERTa**: search results indicate DeBERTa does only "marginally better" than RoBERTa-MNLI on capability-wise (phenomenon-targeted) analysis and "still suffers" on spatial, numerical, knowledge, and implicature-style templates — negation is not called out as a category where DeBERTa is uniquely strong. On NegNLI-style evaluation, some purpose-built approaches outperform a BERT-negation baseline (BERTNOT) while roughly matching it on the original (non-negated) dev sets.
- **No head-to-head study found in this pass that directly benchmarks DeBERTa-MNLI against a modern LLM judge (GPT-4o/Claude) on the *same* negation test set with both accuracy numbers reported side by side.** The literature supports the general claim that small NLI models trained specifically on adversarial/negation-augmented data (ANLI, WANLI, NegNLI-style fine-tuning) can match or beat much larger models on the *narrow* phenomenon they were tuned for — this is the standard "specialist beats generalist on its own turf" pattern well documented for DeBERTa-v3 vs GPT-3-class models on ANLI — but a same-set negation-specific DeBERTa-vs-GPT-4o/Claude comparison is **not found** and should be flagged as an open empirical question rather than asserted.

---

## 5. Adversarial robustness of LLM judges

| Attack | Measured effect | Conditions | Source |
|---|---|---|---|
| **Null-model benchmark cheating** | A null model that always emits one fixed, input-irrelevant response achieves **86.5% length-controlled win rate on AlpacaEval 2.0**, **83.0 score on Arena-Hard-Auto**, **9.55 score on MT-Bench** — i.e., a response containing zero actual content beats the median real model on judge-scored leaderboards | Constant/null candidate response vs normal LLM-as-judge pipelines (AlpacaEval 2.0, Arena-Hard-Auto, MT-Bench) | Zheng et al./collaborators, "Cheating Automatic LLM Benchmarks: Null Models Achieve High Win Rates," arXiv:2410.07137, ICLR 2025 — https://arxiv.org/abs/2410.07137 |
| **JudgeDeceiver — optimization-based prompt injection into the evaluated candidate** | Average attack success rate **90.8%** across settings; per-target-model ASRs: Openchat-3.5 89.2%/88%, Mistral-7B 90.8%/93.2%, Llama-2-7B 98.9%/98.1% — a gradient-optimized injected sequence embedded in the attacker's own candidate response reliably forces the judge to select it | Judge = various open models; attack scenarios: search re-ranking, RLAIF, tool selection | Shi et al., "Optimization-based Prompt Injection Attack to LLM-as-a-Judge" (JudgeDeceiver), arXiv:2403.17710, ACM CCS 2024 — https://arxiv.org/abs/2403.17710 ; code https://github.com/ShiJiawenwen/JudgeDeceiver `[SELF-REPORTED — attack authors' own numbers, no independent replication found in this pass]` |
| **General prompt-injection vulnerability of judge architectures** | "Investigating the Vulnerability of LLM-as-a-Judge Architectures to Prompt-Injection Attacks" confirms decision instability, rephrasing-sensitivity, and manipulability as a general property of the paradigm; a related attack, EchoGram, is described as able to flip defensive-model verdicts, causing false approvals of harmful content or false-alarm flooding — specific quantitative ASR for EchoGram was not extracted from the sources fetched in this pass (flag for follow-up if a number is needed) | Various LLM-as-judge safety-classification setups | arXiv:2505.13348 — https://arxiv.org/abs/2505.13348 ; EchoGram reference via search snippet, not independently verified this pass |
| **Robustness stress-test survey** | "LLMs Cannot Reliably Judge (Yet?): A Comprehensive Assessment on the Robustness of LLM-as-a-Judge" is a broader robustness assessment (title/topic only, not fetched in full this pass) — flagged as a source to pull in full if a comprehensive robustness table is needed for the decision memo | — | arXiv:2506.09443 — https://arxiv.org/abs/2506.09443 |

**Read for the grounding gate:** the injected-content attack surface (JudgeDeceiver, 90.8% ASR) is structurally the closest analogue to Agent-Assure's actual threat model — an attacker-controlled draft or a compromised/adversarial source document trying to talk an LLM judge into a PASS. This is direct, measured, high-magnitude evidence that **if any LLM call were ever introduced into the grounding path, the injected-content attack surface is not a theoretical concern — it has a demonstrated >90% success rate against several open-weight judge models under optimization-based attack.** This corroborates, with an actual external number, the project's existing invariant ("nothing under `ground_check.py`'s call tree may call a model") rather than merely asserting it as a stylistic preference.

---

## Explicit gaps in the literature (say plainly where it doesn't answer)

1. No study found directly measures LLM-judge accuracy on the *specific* task Agent-Assure needs (binary "is claim C, as a whole, verbatim-or-entailed-supported by source S" under negation/attribution-reversal), as opposed to (a) general negation-NLI three-way classification, or (b) general pairwise quality/preference judging. The negation-NLI numbers (section 4a) and the pairwise-bias numbers (section 1) are the closest available proxies, not direct measurements.
2. No 2024–2026 paper found benchmarks GPT-4o/Claude/o1-class models on the classic negation-NLI suite (ScoNe/NegNLI/MoNLI/NaN-NLI/CondaQA) with reported accuracy — the "did reasoning models fix negation" question is open in the surveyed literature.
3. No paper found re-runs a CommitmentBank-style factive/non-factive attribution task against a modern LLM judge with a reported number — whether GPT-4o/Claude reliably treats "X claimed P" as not entailing P is untested in the literature surveyed here.
4. No same-test-set head-to-head of DeBERTa-MNLI vs a modern LLM judge specifically isolating negation performance was found.
5. Exact per-bias percentage tables from the CALM/12-bias paper (arXiv:2410.02736) were not extracted at full-text fidelity in this pass — the taxonomy is solid, the magnitudes need a direct table pull if cited to a decimal in a decision memo.

---

## Full source list

- Wang et al. 2023, "Large Language Models are not Fair Evaluators" — https://arxiv.org/abs/2305.17926
- Zheng et al. 2023, "Judging LLM-as-a-Judge with MT-Bench and Chatbot Arena" — https://arxiv.org/abs/2306.05685
- Panickssery, Bowman & Feng 2024, "LLM Evaluators Recognize and Favor Their Own Generations" — https://arxiv.org/abs/2404.13076
- Ye et al. 2024/2025, "Justice or Prejudice? Quantifying Biases in LLM-as-a-Judge" (CALM) — https://arxiv.org/abs/2410.02736 ; https://llm-judge-bias.github.io/
- "Rating Roulette: Self-Inconsistency in LLM-As-A-Judge Frameworks" — https://arxiv.org/abs/2510.27106
- "Large Language Models are Inconsistent and Biased Evaluators" — https://arxiv.org/abs/2405.01724
- "Overconfidence in LLM-as-a-Judge: Diagnosis and Confidence-Driven Solution" — https://arxiv.org/abs/2508.06225
- Truong, Baldwin, Verspoor & Cohn 2023, "Language models are not naysayers" — https://arxiv.org/abs/2306.08189
- She et al. 2023, "ScoNe: Benchmarking Negation Reasoning in Language Models" — https://arxiv.org/abs/2305.19426
- Ravichander et al. 2022, "CondaQA" — https://arxiv.org/abs/2211.00295
- "A negation detection assessment of GPTs: xNot360" — https://arxiv.org/abs/2306.16638
- "Benchmarking Gaslighting Negation Attacks Against Reasoning Models" — https://arxiv.org/abs/2506.09677
- "Making Language Models Robust Against Negation" 2025 — https://arxiv.org/abs/2502.07717
- de Marneffe, Simons & Tonhauser, "The CommitmentBank" — https://ojs.ub.uni-konstanz.de/sub/index.php/sub/article/view/601
- Jiang & de Marneffe, "Evaluating BERT for NLI: A Case Study on the CommitmentBank" — https://aclanthology.org/D19-1630/
- He, Gao & Chen, "DeBERTa: Decoding-enhanced BERT with Disentangled Attention" — https://arxiv.org/abs/2006.03654
- "Cheating Automatic LLM Benchmarks: Null Models Achieve High Win Rates" — https://arxiv.org/abs/2410.07137
- Shi et al. 2024, "Optimization-based Prompt Injection Attack to LLM-as-a-Judge" (JudgeDeceiver) — https://arxiv.org/abs/2403.17710
- "Investigating the Vulnerability of LLM-as-a-Judge Architectures to Prompt-Injection Attacks" — https://arxiv.org/abs/2505.13348
- "LLMs Cannot Reliably Judge (Yet?)" — https://arxiv.org/abs/2506.09443
