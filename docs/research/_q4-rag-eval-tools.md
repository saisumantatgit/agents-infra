# Q4 — Production RAG-evaluation tools, and the small-purpose-built-model option

Research notes, 2026-09-12. Every number carries source + whether it is authors'-own.

## 4.1 The benchmark landscape first (so the tool numbers mean something)

**LLM-AggreFact** (Tang et al., MiniCheck paper, EMNLP 2024) is the closest thing to a
standard for "does this document support this claim". 11 datasets, four families:
summarization (AggreFact-CNN/XSum, TofuEval-MeetB/MediaS, RAGTruth), RAG
(ClaimVerify, LFQA, ExpertQA, RAGTruth), post-hoc grounding (REVEAL, Factcheck-GPT),
human-written claims (WiCE). Each item is `(D, c, y)`: grounding document set, claim,
boolean support label. ~13K test items.
Source: https://llm-aggrefact.github.io/blog , https://aclanthology.org/2024.emnlp-main.499/

**Headline balanced accuracies on LLM-AggreFact** (Table 2, MiniCheck paper — *authors'
own numbers for MiniCheck, third-party numbers for the baselines they ran*):

| System | Size | Balanced acc. |
|---|---|---|
| GPT-4 | API | **75.3%** |
| MiniCheck-FT5 (Flan-T5-L) | 770M | **74.7%** |
| Claude-3 Opus | API | 74.1% |
| Mistral-Large | API | 73.4% |
| MiniCheck-RoBERTa-L | 355M | 72.7% |
| MiniCheck-DeBERTa-L | 355M | 72.6% |
| AlignScore (RoBERTa-L) | 355M | 70.4% |
| GPT-3.5 | API | 69.6% |
| SummaC-CV | small | 62.1% |
| FT5-ANLI-L | 770M | 61.4% |
| **T5-NLI-Mixed (T5-XXL)** | **11B** | **61.0%** |

Source: https://arxiv.org/html/2404.10774v2 (Table 2)

Two things matter here for Agent-Assure:

1. **The ceiling for ALL approaches is ~75%.** A frontier LLM judge and a 770M local
   model land within 0.6 points of each other. The claim "an LLM will fix entailment"
   is not supported: the best measured number for any method on the standard
   benchmark is three-quarters.
2. **Generic NLI is the worst option measured.** An 11B T5-NLI model scores 61.0% —
   *14 points below* a 770M model purpose-trained for grounding. The project's
   original ADR-004 plan (local DeBERTa-MNLI) sits in that weak family. Purpose-built
   grounding models (MiniCheck, HHEM) beat generic MNLI checkpoints decisively.

**Cost** (MiniCheck paper Tables 3–4, authors' own, for the 13K LLM-AggreFact test set):

| System | Cost for 13K claims |
|---|---|
| MiniCheck-FT5 (self-hosted) | **$0.24** |
| GPT-3.5 | $4.75 |
| GPT-4 | $107 |
| Claude-3 Opus | $165 |
| GPT-4 with atomic decomposition | $212 |

≈445× cheaper than GPT-4 at equal accuracy. Source: https://arxiv.org/html/2404.10774v2

**Claim decomposition did NOT help.** MiniCheck explicitly tested decomposing claims
into atomic facts before checking: "near-zero performance change for GPT-4 and mixed
changes for specialized fact-checkers … there is no clear indication that decomposing
claims into atomic facts can consistently improve models' performance." This
contradicts the RAGAS/FActScore design assumption. Source: same paper.

## 4.2 THE MOST IMPORTANT NUMBER — FaithBench

FaithBench (Bao et al. 2024, NAACL 2025 short; **Vectara authors**) built a benchmark
deliberately out of the cases where SOTA detectors *disagree with each other*, i.e. the
hard middle. Result:

| Detector | FaithBench balanced accuracy |
|---|---|
| GPT-4o (zero-shot judge) | **56.29%** |
| HHEM-2.1 | **55.68%** |
| MiniCheck-RoBERTa-L | **55.03%** |

"The balanced accuracies of all detectors are near 50%."
Source: https://arxiv.org/pdf/2410.13210 (and summary at
https://www.emergentmind.com/topics/faithfulness-hallucination-detection)

Caveat, stated plainly: FaithBench is *selected for hardness by construction* — items
were chosen because detectors disagreed. It is therefore not an estimate of real-world
accuracy; it is an estimate of accuracy **on the cases a deterministic gate would also
find hard**, which is exactly Agent-Assure's residual-31-open-classes population.
That makes it the more relevant number for this decision, not the less.

Note the COI direction: Vectara authored FaithBench and also makes HHEM; HHEM does
*not* win on it (55.68 vs GPT-4o's 56.29). The benchmark is not self-flattering.

**Partial counter-evidence — FaithJudge.** The same group later showed that an LLM
judge (o3-mini-high) prompted with *human-annotated examples of hallucinated spans for
the same source document* reaches ~85% balanced accuracy on FaithBench.
Sources: https://arxiv.org/pdf/2505.04847 , https://github.com/vectara/FaithJudge
**But the precondition is fatal for Agent-Assure**: FaithJudge needs pre-existing human
annotations *for that specific document* at inference time. It is a leaderboard
instrument, not a deployable gate. Zero-shot on a fresh source, you are back at ~56%.

## 4.3 Tool-by-tool

### RAGAS — LLM-judge, non-deterministic
`faithfulness` = LLM decomposes answer into atomic statements, then an LLM returns a
binary supported/not verdict per statement; score = supported/total.
Source: https://docs.ragas.io/en/stable/concepts/metrics/available_metrics/faithfulness/
Published accuracy: the RAGAS paper reports 0.95 agreement with human annotators on
**WikiEval** for faithfulness (authors' own, single small dataset).
Independent contradiction: GroUSE (144 unit tests, 7 generator failure modes) finds
RAGAS-style metrics "do not perform well on many individual test cases" despite
correlating with GPT-4 overall. Source: https://arxiv.org/abs/2409.06595
RAGAS now optionally wraps Vectara HHEM-2.1-Open as an alternative faithfulness
backend — i.e. the ecosystem itself is migrating toward the small local model.

### DeepEval — LLM-judge, non-deterministic
`FaithfulnessMetric`: extract claims, check each against retrieval context, ratio.
Source: https://deepeval.com/docs/metrics-faithfulness
No published benchmark accuracy found.
**Documented failure of exactly the kind CLAUDE.md warns about:** with *no* context
supplied, DeepEval defines faithfulness as "absence of claims contradicting the
context"; with nothing to contradict, the score defaults to near-perfect. An absent
input is read as *unconstrained* and points toward PASS. Source: GroUSE-adjacent
analysis cited in https://arxiv.org/pdf/2409.06595 discussion and RAGAS/DeepEval
comparisons. This is the Agent-Assure round-4 bug, shipped in a production tool.

### TruLens — BOTH, configurable
Offers `Groundedness` as (a) an NLI feedback function (HuggingFace provider, splits
response into sentences, runs an NLI model against the source) and (b) an LLM-provider
feedback function. Recent releases re-aligned groundedness toward the LLM-based path.
Sources: https://www.trulens.org/reference/trulens/providers/huggingface/ ,
https://www.trulens.org/getting_started/core_concepts/feedback_functions/
No published head-to-head accuracy found from TruLens itself.

### Arize Phoenix — LLM-judge
`HallucinationEvaluator`, prompt-template based, returns `factual` / `hallucinated`
plus an explanation. Arize also published **LibreEval**, an open hallucination dataset
+ model, where ground truth was an *LLM judge council consensus label* — note that is
model-derived ground truth, not human.
Sources: https://arize.com/docs/ax/evaluate/evaluators/llm-as-a-judge ,
https://arize.com/wp-content/uploads/2023/04/LibreEval-Phoenix-Open-Source-Hallucination-Evaluation-Model-Dataset-1.1.pdf

### Galileo Luna — small fine-tuned encoder
440M DeBERTa-v3-Large, fine-tuned on production RAG data; handles 16k tokens.
Claims: 18% more accurate than GPT-3.5 at RAG hallucination detection, with 97% cost
and 91% latency reduction. **Vendor/authors' own numbers; baseline is GPT-3.5, not
GPT-4 — a weak comparator by 2024 standards.** No LLM-AggreFact or FaithBench number
published. Sources: https://arxiv.org/abs/2406.00975 ,
https://aclanthology.org/2025.coling-industry.34/

### Vectara HHEM-2.1-Open — small purpose-built, Apache-2.0
- **0.1B params**, Flan-T5-Base backbone. Unlimited context (v1.0 was capped at 512).
- **<600MB RAM at fp32; ~1.5 s for a 2k-token input on a modern x86 CPU.** No GPU needed.
- Balanced accuracy (model card, Vectara's own numbers):

| Dataset | HHEM-2.1-Open | HHEM-1.0 | GPT-3.5-Turbo | GPT-4 |
|---|---|---|---|---|
| AggreFact-SOTA | 76.55% | 78.87% | 72.19% | 73.78% |
| RAGTruth-Summ | 64.42% | 53.36% | 58.49% | 62.62% |
| RAGTruth-QA | 74.28% | 52.58% | 56.16% | 74.11% |

Source: https://huggingface.co/vectara/hallucination_evaluation_model
On FaithBench (harder, third-party-ish): 55.68%.
This is the single best fit for a project that wants to keep the "no API call, runs
locally, small" story: 0.1B, Apache-2.0, CPU-only, beats GPT-4 on two of three RAG
datasets by its maker's measurement.

### Patronus Lynx — large open LLM judge
8B and 70B Llama-3 fine-tunes. On the authors' own HaluBench (15k samples):
Lynx-70B beats GPT-4o by ~1 point average, +8.3 points on PubMedQA; Lynx-8B beats
GPT-3.5 by 24.5 points, Claude-3-Sonnet by 8.6, Claude-3-Haiku by 18.4. All
authors'-own, on a benchmark the authors built.
Sources: https://arxiv.org/html/2407.08488v1 ,
https://www.patronus.ai/blog/lynx-state-of-the-art-open-source-hallucination-detection-model
70B is not a plausible local dependency for this project.

### Cleanlab TLM + the "Real-Time Evaluation Models for RAG" survey
arXiv 2503.21157 (Ashish Sardana) compares LLM-as-a-Judge (GPT-4o-mini), Prometheus-2,
Lynx-70B, HHEM-2.1 and Cleanlab TLM across FinQA, ELI5, FinanceBench, PubmedQA,
CovidQA, DROP. Conclusion: TLM wins on precision/recall on 4 of 6.
**Severe COI: the paper is hosted on Cleanlab's blog with Cleanlab's reproduction repo,
and TLM is Cleanlab's product. Treat as vendor marketing with an arXiv number.**
Sources: https://arxiv.org/abs/2503.21157 , https://cleanlab.ai/blog/rag-evaluation-models/
Useful neutral fact from it: all evaluators beat chance (AUROC > 0.5) but the paper
publishes ROC curves rather than a numeric AUROC table — so the margins cannot be
independently read off.

## 4.4 Determinism — the property most at risk

**None of the LLM-judge tools is deterministic, and `temperature=0` does not make one
deterministic.** Thinking Machines Lab (2025-09-10) sampled 1,000 completions at
temperature 0 from Qwen3-235B-A22B-Instruct-2507 and got **80 unique completions**;
the first 102 tokens were identical across all runs, divergence began at token 103.
Root cause is not floating-point concurrency but **lack of batch invariance** — a
request's output depends on what else was batched with it, which varies with server
load. Fixing it requires batch-invariant kernels at ~61% of baseline throughput
(26s → 42s for 1,000 sequences on Qwen3-8B with the optimized attention kernel).
Source: https://thinkingmachines.ai/blog/defeating-nondeterminism-in-llm-inference/
Corroborating: https://arxiv.org/pdf/2506.09501 (numerical sources of nondeterminism),
https://arxiv.org/pdf/2407.10457 (evaluation should not ignore non-determinism).

Implication for Agent-Assure specifically: an **API** call to a hosted model can never
be made bit-reproducible by the caller — batch composition is the provider's, not
yours. A **locally hosted small encoder** (HHEM-2.1-Open, MiniCheck-FT5, a DeBERTa)
run single-item, fixed seed, fixed weights, fixed precision on CPU *is* reproducible
in practice, because there is no cross-request batching and the graph is fixed. The
determinism story survives a local classifier; it does not survive an API call.

## 4.5 Reference table

| Tool / model | Approach | Size | Deterministic? | Published accuracy | Whose number |
|---|---|---|---|---|---|
| RAGAS `faithfulness` | LLM judge, atomic-statement decomposition | API | No | 0.95 human-agreement on WikiEval | authors' own |
| DeepEval `Faithfulness` | LLM judge, claim extraction | API | No | none found | — |
| TruLens Groundedness | NLI model *or* LLM judge (configurable) | varies | NLI path: yes | none found | — |
| Arize Phoenix Hallucination | LLM judge, prompt template | API | No | LibreEval, but ground truth = LLM council | authors' own |
| Galileo Luna | fine-tuned DeBERTa-v3-Large | 440M | Yes (local) | +18% vs GPT-3.5; −97% cost, −91% latency | vendor, weak baseline |
| **Vectara HHEM-2.1-Open** | fine-tuned Flan-T5-Base classifier | **0.1B** | **Yes (local, CPU, 1.5s/2k tok)** | 76.6 / 64.4 / 74.3 BAcc; 55.7 on FaithBench | vendor own + FaithBench(vendor) |
| **MiniCheck-FT5** | fine-tuned Flan-T5-L on GPT-4 synthetic data | **770M** | **Yes (local)** | **74.7% BAcc LLM-AggreFact** (GPT-4 = 75.3) | authors' own |
| MiniCheck-DeBERTa-L | fine-tuned DeBERTa | 355M | Yes (local) | 72.6% BAcc | authors' own |
| Bespoke-MiniCheck-7B | fine-tuned 7B | 7B | Yes (local) | SOTA on LLM-AggreFact leaderboard | authors' own |
| Patronus Lynx 70B / 8B | fine-tuned Llama-3 judge | 70B / 8B | Yes (local) but impractical size | ~+1 pt vs GPT-4o on HaluBench | authors' own, own benchmark |
| Cleanlab TLM | LLM self-reflection + sampling consistency | API | No (samples multiple times) | "highest precision/recall" on 4/6 | vendor, severe COI |
| AlignScore | RoBERTa-L, alignment-trained | 355M | Yes (local) | 70.4% BAcc | third-party (MiniCheck ran it) |
| Generic T5-NLI-Mixed | off-the-shelf NLI | 11B | Yes (local) | **61.0% BAcc** | third-party |
| SummaC-CV | NLI + sentence-pair aggregation | small | Yes (local) | 62.1% BAcc | third-party |

## 4.6 What this section concludes

- The LLM judge is **not** the best entailment checker available; it is roughly tied
  with a 770M local model and ~445× more expensive.
- The *original* ADR-004 plan (generic DeBERTa-MNLI) is the weakest measured family at
  61%. If a model tier is added, it should be a **purpose-built grounding checker**
  (MiniCheck-FT5 770M or HHEM-2.1-Open 0.1B), not a generic MNLI checkpoint.
- Every measured approach is at ~75% on the standard benchmark and **~55% on the hard
  cases**. That is the number to plan against, because Agent-Assure's residual open
  classes *are* the hard cases.
- Determinism survives a locally hosted small classifier. It does not survive an API
  call, at any temperature.
