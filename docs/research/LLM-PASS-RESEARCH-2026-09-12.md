# Adding an LLM entailment pass after the deterministic gate — evidence review

**Date:** 2026-09-12
**Question:** Agent-Assure's provenance check (Job 1) is sound. Its entailment check
(Job 2) is failing — ~31 open false-negative classes after 8 red-team rounds, Error-A
0.320 on n=52 gold (CR-004). Proposal on the table: add an LLM pass *after* the
deterministic gate to decide entailment. Does the literature support that?
**Method:** web search + direct fetch of papers, model cards, leaderboards and vendor
docs. Supporting detail lives in four companion files in this directory:
`_q12-llm-judge-vs-nli.md`, `_q3-judge-failure-modes.md`, `_q4-rag-eval-tools.md`,
`_q56-vendors-and-prior-art.md`.

**Citation discipline used here:** every number carries its source and is marked when it
comes from the authors of the method being measured. Where two sources disagree, both are
shown and the disagreement is named rather than averaged.

---

## RECOMMENDATION, STATED FIRST

**Add a model tier, but make it a small purpose-built grounding classifier running
locally — not an API call to a frontier LLM — and restrict its authority to moving
claims toward FAIL only.**

Three measured reasons, each falsifiable:

1. **The accuracy gap that would justify the API call does not exist.** GPT-4 as a
   grounding judge scores 75.3% balanced accuracy on LLM-AggreFact; MiniCheck-FT5, a
   770M model you can run on a laptop, scores 74.7% — a 0.6-point difference at ~446×
   the cost ($107 vs $0.24 per 13K claims). Source: MiniCheck, EMNLP 2024,
   https://arxiv.org/html/2404.10774v2 (authors' own table, but the baselines are
   third-party systems they re-ran).
2. **The determinism claim cannot survive an API call, at any temperature.** 1,000
   completions at temperature 0 from one model produced 80 unique outputs; the cause is
   batch-invariance in the serving stack, which is the provider's business, not the
   caller's. Source: https://thinkingmachines.ai/blog/defeating-nondeterminism-in-llm-inference/
   A locally hosted, single-item, fixed-weight classifier *is* reproducible in practice.
3. **An LLM in the verdict path reopens the precise attack the product claims to close.**
   Optimization-based prompt injection embedded in the evaluated content achieves 90.8%
   average attack success against LLM judges. Source: JudgeDeceiver, ACM CCS 2024,
   https://arxiv.org/abs/2403.17710 (attack authors' own numbers, no independent
   replication found). "A fabricated citation cannot talk its way to a pass" stops being
   true the moment a model reads attacker-controlled text and its output can gate a
   verdict.

**What would flip this:** a measured demonstration that a frontier LLM judge beats
MiniCheck-FT5 by a large margin *specifically on negation and attribution reversal* —
the failure class Agent-Assure actually has. No such measurement exists in the surveyed
literature (see Q3). If someone runs it and the gap is 15+ points, the cost argument
loses and the determinism argument becomes the only objection.

**The load-bearing assumption underneath all of this:** that Agent-Assure's residual
failure population resembles the *hard* slice of these benchmarks rather than the average
slice. If the ~31 open classes are actually easy cases the current regexes simply do not
cover, the ~75% average numbers apply and a model tier helps a lot; if they are genuinely
contested cases, the ~55% FaithBench numbers apply and a model tier helps much less than
it appears to. Nobody has measured which. That measurement is the cheapest next step and
is described at the end of this document.

---

## Q1 — How reliable is an LLM as a judge of whether a source supports a claim?

**Short answer: ~75% balanced accuracy on the standard benchmark, ~55% on hard cases,
and never independently verified above the human-agreement floor.**

### The standard benchmark

**LLM-AggreFact** (Tang et al., MiniCheck, EMNLP 2024) is the closest thing to a canon
for this exact task: 11 datasets, ~13K items, each a `(grounding documents, claim,
boolean support label)` triple. Sub-datasets span summarization (AggreFact-CNN/XSum,
TofuEval, RAGTruth), RAG (ClaimVerify, LFQA, ExpertQA), post-hoc grounding (REVEAL,
Factcheck-GPT) and human-written claims (WiCE).
Sources: https://aclanthology.org/2024.emnlp-main.499/ , https://llm-aggrefact.github.io/blog

| System | Balanced accuracy |
|---|---|
| Bespoke-MiniCheck-7B (post-paper leaderboard) | 77.4% |
| GPT-4 | 75.3% |
| MiniCheck-FT5 (770M) | 74.7% |
| Claude-3 Opus | 74.1% |
| Mistral-Large | 73.4% |
| MiniCheck-RoBERTa-L (355M) | 72.7% |
| MiniCheck-DeBERTa-L (355M) | 72.6% |
| AlignScore (355M) | 70.4% |
| GPT-3.5 | 69.6% |
| QAFactEval | 66.5% |
| SummaC-ZS | 67.9% |
| SummaC-Conv | 62.1% |
| FT5-ANLI-L (770M) | 61.4% |
| **T5-NLI-Mixed (11B)** | **61.0%** |

All from https://arxiv.org/html/2404.10774v2 Table 2. **These are the MiniCheck authors'
numbers**, including the baselines they re-ran; the leaderboard row is Bespoke Labs'
self-report. No independent replication of the full table was found.

**Nothing clears 80%.** Not a frontier model, not a specialist, not an 11B NLI model.

### The hard cases

**FaithBench** (Bao et al., NAACL 2025 short, Vectara authors) was built specifically from
the cases where SOTA detectors *disagree with one another*. On it:

| Detector | FaithBench balanced accuracy | Source |
|---|---|---|
| GPT-4o zero-shot judge | 56.29% | https://arxiv.org/pdf/2410.13210 |
| HHEM-2.1 | 55.68% | same |
| MiniCheck-RoBERTa-L | 55.03% | same |

The paper's own summary: "the balanced accuracies of all detectors are near 50%."

**A discrepancy worth naming rather than averaging.** Vectara's later FaithJudge work
reports HHEM-2.1 at 52.6% BAcc / 32.9% macro-F1 and o3-mini-high zero-shot at 68.8% /
60.7% on FaithBench (https://github.com/vectara/FaithJudge , https://arxiv.org/pdf/2505.04847),
which does not reconcile with the FaithBench paper's 55.68% / 56.29%. The two use
different label binarizations (FaithBench has a three-way Unwanted / Questionable /
Benign taxonomy, and how "Questionable" is folded in changes the number materially) and
different judge models. Both are Vectara's. **Do not quote a single FaithBench number as
settled**; quote the range 52–69% for zero-shot detectors with the setup attached.

### The thing that actually moved the number

FaithJudge — the *same* o3-mini-high judge, given few-shot **human-annotated hallucinated
spans for the same source article** — jumps to 84.0% BAcc / 82.1% macro-F1.
Source: https://github.com/vectara/FaithJudge (Vectara's own).

That is the largest single effect found in this review: **prompt context moved the judge
further than model choice did** (68.8 → 84.0, versus 74.1 → 75.3 across Claude-3-Opus to
GPT-4). It is also unusable here: it requires pre-existing human annotations *for that
specific document at inference time*. It is a leaderboard instrument, not a gate.

### What else moves the numbers

- **Claim decomposition into atomic facts: no consistent gain.** MiniCheck tested it
  directly: "near-zero performance change for GPT-4 and mixed changes for specialized
  fact-checkers… no clear indication that decomposing claims into atomic facts can
  consistently improve models' performance" (https://arxiv.org/html/2404.10774v2). This
  contradicts the design premise of RAGAS and FActScore. It also costs money — GPT-4 with
  decomposition ran $212 vs $107 without.
- **Document length degrades NLI-family checkers.** SummaC exists because sentence-pair
  NLI degrades on document-length premises; chunk-and-aggregate is the standard
  mitigation (https://arxiv.org/abs/2111.09525). **No clean accuracy-vs-length curve was
  found** — flagged as a gap.
- **Prompt-order / CoT ablations:** no paper found isolating these for grounding
  judgment. Gap.
- **Domain:** no domain-stratified (legal / news / dialogue) breakdown found for judge
  accuracy on grounding. Gap.

### The ceiling nobody can exceed

Human-vs-human agreement on this task is itself modest, and it drops as granularity gets
finer — which matters because Agent-Assure judges at the atomic-claim level:

| Benchmark | Human–human agreement |
|---|---|
| RAGTruth, response level | 91.8% |
| RAGTruth, **span level** | **78.8%** |
| FActScore | 84.8% raw, Cohen's κ = 0.55 |
| ExpertQA (independent unit) | κ = 0.52 |
| MiniCheck synthetic-data QC | 85–88% accuracy, Fleiss' κ 0.51–0.70 |

Sources: https://aclanthology.org/2024.acl-long.585/ , MiniCheck paper, ExpertQA. All
are the benchmark authors' own annotation-quality reports.

GPT-4's 75.3% sits *inside* typical human-disagreement territory, not above it. This also
independently validates CR-004's own caveat that a single ratifier is not external ground
truth — the literature's own ratifiers agree with each other at κ≈0.5–0.7.

---

## Q2 — LLM judge vs a small NLI model

**Short answer: the gap is 0.6 points against a purpose-built small model and ~5 points
against a generic one — and the project's originally planned model family is the worst
option measured.**

| | Balanced acc. (LLM-AggreFact) | Size | Cost / 13K claims |
|---|---|---|---|
| GPT-4 judge | 75.3% | API | $107 |
| Claude-3 Opus judge | 74.1% | API | $165 |
| GPT-3.5 judge | 69.6% | API | $4.75 |
| **MiniCheck-FT5** | **74.7%** | **770M** | **$0.24** |
| MiniCheck-DeBERTa-L | 72.6% | 355M | ~$0.24 |
| AlignScore | 70.4% | 355M | — |
| **Generic T5-NLI-Mixed** | **61.0%** | **11B** | — |
| FT5-ANLI-L | 61.4% | 770M | — |

Cost figures: https://arxiv.org/html/2404.10774v2 Tables 3–4, authors' own, self-hosted
inference vs list API pricing at the time.

**Three conclusions, in order of importance to this decision:**

1. **A purpose-built 770M model matches GPT-4 at 1/446th the cost.** 0.6 points is inside
   the noise of a single held-out run on 13K items. There is no accuracy case for the API
   call.
2. **ADR-004's original plan — a generic DeBERTa-MNLI entailment tier — is the weakest
   measured family.** Generic NLI checkpoints land at 61%, *fourteen points below* a
   770M purpose-trained grounding model and nine points below a 355M one. An 11B generic
   NLI model loses to a 355M specialist. If a model tier is built, it should be
   MiniCheck-FT5 or HHEM-2.1-Open, **not** `cross-encoder/nli-deberta-v3-large` or
   similar. This is the single most actionable correction to the existing plan.
   (Note the nuance: MiniCheck-DeBERTa-L at 72.6% shows the *architecture* is fine — it
   is the generic MNLI *training objective* that is wrong for this task.)
3. **Latency:** HHEM-2.1-Open (0.1B, Flan-T5-Base) processes a 2k-token input in ~1.5 s
   on a modern x86 CPU in <600MB RAM, Apache-2.0.
   Source: https://huggingface.co/vectara/hallucination_evaluation_model (vendor's own).
   No wall-clock ms/claim figures for GPT-4 vs DeBERTa-class models were found in any
   paper — gap.

**Where each fails:** small NLI models degrade on long premises (the SummaC problem) and
on anything requiring world knowledge outside the passage; LLM judges fail on the
attacker-controlled surface features catalogued in Q3, cost 400×, and cannot be made
reproducible over an API.

---

## Q3 — Known failure modes of LLM judges

**Short answer: the biases are large and measured; negation — the exact failure Agent-Assure
has — is the one place the literature is emphatically *not* reassuring, and modern
reasoning models have never been tested on it.**

### Biases, with magnitudes

| Bias | Measured magnitude | Source |
|---|---|---|
| Position (order swap flips verdict) | GPT-4 conflict rate 46.3%; ChatGPT up to 82.5% on contested pairs. MT-Bench formulation: GPT-4 order-swap consistency 65.0%, GPT-3.5 46.2% | https://arxiv.org/abs/2305.17926 , https://arxiv.org/abs/2306.05685 |
| Verbosity (padded, content-free answer wins) | Claude-v1 and GPT-3.5 fooled 91.3% of the time; GPT-4 8.7% | https://arxiv.org/abs/2306.05685 |
| Self-preference | GPT-4 +~10pp for its own outputs; Claude-v1 +~25pp. Strength correlates linearly with the model's self-recognition ability | https://arxiv.org/abs/2306.05685 , https://arxiv.org/abs/2404.13076 |
| 12-bias taxonomy (position, verbosity, bandwagon, distraction, **authority**, fallacy-oversight, sentiment, CoT-presence, refinement-aware, compassion-fade, diversity, self-enhancement) | "significant biases persist in certain specific tasks" across popular models; per-bias table in the paper body | https://arxiv.org/abs/2410.02736 (ICLR 2025) |

**Every one of these is keyed on a surface property the author of the text controls** —
position, length, self-authorship signal, cited authority. That is the *same class* of
vulnerability the project's own CLAUDE.md forbids ("never key a moat rule on a surface
property the author controls" — killed by a five-token fabrication in round 3 and by the
Shift key in round 4). The finding here is that **LLM judges have this disease too**, with
larger measured magnitudes than the regexes did.

Caveat stated plainly: all of these are measured on *pairwise preference* judging, not on
*single-item binary entailment*. The transfer is an inference, not a measurement.

### Inconsistency and calibration

- Repeated identical calls produce materially different scores; `temperature=0` can
  *degrade* human agreement relative to a small positive temperature. Tested across
  GPT-4o, GPT-4o-mini, Gemini-2.5-Flash, Claude-Haiku-4.5, Claude-Sonnet-4.5.
  Source: https://arxiv.org/abs/2510.27106 (EMNLP Findings 2025).
  **No study measures same-prompt repeat-agreement on a binary entailment judgment** — gap.
- Judge confidence is badly calibrated: GPT-4o and DeepSeek-R1 cluster self-reported
  confidence at 90–100% while true accuracy in that bin is well below.
  Source: https://arxiv.org/abs/2508.06225. **This kills any design that thresholds on an
  LLM-emitted confidence score** — which is structurally the same reason ADR-006 demoted
  T2 and ADR-005 made the score a secondary bar behind an empty retained appendix.
  (No exact ECE digit extracted — pull the table before quoting one.)

### NEGATION — the section that matters most

This is Agent-Assure's actual reported bug ("It is not true that Redis loses your data"
→ certified). The literature here is worse than neutral.

| Model | SAR | SNLI-neg | MNLI-neg | RTE-neg | NaN-NLI | MoNLI |
|---|---|---|---|---|---|---|
| GPT-3 (175B) | 50.1% | **26.7%** | 35.9% | 52.5% | 46.9% | 54.0% |
| InstructGPT (175B) | 68.7% | 64.0% | 54.8% | 76.7% | 64.7% | 47.0% |

Truong et al., *SEM 2023, https://arxiv.org/abs/2306.08189. Headline finding: **inverse
scaling on negation** — the smallest model tested outperformed larger variants on MKR-NQ;
larger LMs become *more* insensitive to the presence of negation, not less. Scaling does
not fix this.

- **ScoNe** (scoped negation, ACL 2023, https://arxiv.org/abs/2305.19426): best few-shot
  CoT prompting reached 82% overall, but the authors call the number misleading — it is
  inflated by the subset where negation could be ignored and the label still guessed.
  RoBERTa/DeBERTa-class models only solve it after many-shot fine-tuning on the phenomenon
  specifically, never out of the box.
- **CondaQA** (https://arxiv.org/abs/2211.00295): best fine-tuned model 73.26% accuracy
  but only **42.18% consistency** across minimally-different negation variants (human:
  91.94% / 81.58%). The consistency gap is the damning one — a judge can be right on one
  phrasing of "Redis loses data" and wrong on a near-identical one.
- **Do 2024–2026 reasoning models fix it? Unknown — nobody has run the test.** No paper
  found benchmarks GPT-4o, Claude-3.5+/4-class, or o1/o3-class on ScoNe / NegNLI / MoNLI /
  NaN-NLI / CondaQA. The closest adjacent evidence points the wrong way: under
  negation-framed adversarial prompting, o4-mini fell from 73.2% to 47.6% accuracy and
  Gemini-2.5-Flash dropped 35.4 points on MathVista (https://arxiv.org/abs/2506.09677).
  A 2025 negation-robustness paper still cites Truong 2023 as standing evidence and tests
  only BERT/RoBERTa-scale models (https://arxiv.org/abs/2502.07717).
  **Absence of counter-evidence is not evidence of a fix.**

### ATTRIBUTION REVERSAL ("critics argued that X")

The linguistic mechanism is the **factive / non-factive** distinction — "realize that X"
commits the speaker to X; "claim that X", "argue that X" do not. The benchmark is
CommitmentBank (https://ojs.ub.uni-konstanz.de/sub/index.php/sub/article/view/601), whose
whole design is clausal complements under entailment-cancelling operators — negation,
question, modal, conditional.

BERT reaches 85% F1 on CommitmentBank's three-way task, **but the paper's own analysis
concludes the model does not capture the factive/non-factive distinction** — it
pattern-matches surface cues that correlate with commitment in that corpus
(https://aclanthology.org/D19-1630/). Same shape as ScoNe: high aggregate score, mechanism
not learned.

**No paper found re-runs a CommitmentBank-style factivity task against a modern LLM judge
with a reported number.** Whether GPT-4o or Claude reliably treats "X claimed P" as not
entailing P is, in the surveyed literature, **untested in either direction.**

### Adversarial robustness — the moat-relevant one

| Attack | Effect | Source |
|---|---|---|
| JudgeDeceiver — optimization-based prompt injection placed inside the evaluated content | **90.8% average attack success rate**; per-model 88–98.9% | https://arxiv.org/abs/2403.17710 (ACM CCS 2024) — **attack authors' own numbers, no independent replication found** |
| Null model emitting one fixed, input-irrelevant string | 86.5% length-controlled win rate on AlpacaEval 2.0; 83.0 on Arena-Hard-Auto; 9.55 on MT-Bench | https://arxiv.org/abs/2410.07137 (ICLR 2025) |

The first row is structurally the closest analogue to Agent-Assure's threat model: an
attacker-controlled draft, or a poisoned captured source, trying to talk the judge into a
PASS. This converts "zero LLM calls in the grounding path" from a stylistic preference
into a position with an external measured number behind it.

---

## Q4 — What production RAG-evaluation tools actually do

**Short answer: the open-source frameworks are LLM-judge based and non-deterministic; the
purpose-built small models (MiniCheck, HHEM, Luna) are the ones that preserve
determinism, and they perform as well or better.**

Full detail in `_q4-rag-eval-tools.md`. Reference table:

| Tool / model | Approach | Size | Deterministic? | Published accuracy | Whose number |
|---|---|---|---|---|---|
| RAGAS `faithfulness` | LLM judge; decompose into atomic statements, binary verdict each, ratio | API | No | 0.95 human agreement on WikiEval | authors' own, one small dataset |
| DeepEval `Faithfulness` | LLM judge; claim extraction + contradiction check | API | No | none published | — |
| TruLens Groundedness | configurable: NLI feedback function **or** LLM provider | varies | NLI path yes | none published | — |
| Arize Phoenix `HallucinationEvaluator` | LLM judge, prompt template, factual/hallucinated + explanation | API | No | LibreEval — but its ground truth is an **LLM judge council consensus**, not human | authors' own |
| Galileo Luna | fine-tuned DeBERTa-v3-Large, 16k context | 440M | Yes (local) | +18% vs **GPT-3.5**; −97% cost, −91% latency | vendor's own, weak baseline, no LLM-AggreFact number |
| **Vectara HHEM-2.1-Open** | fine-tuned Flan-T5-Base classifier | **0.1B** | **Yes — local, CPU, ~1.5s/2k tokens, <600MB RAM, Apache-2.0** | AggreFact-SOTA 76.55, RAGTruth-Summ 64.42, RAGTruth-QA 74.28; FaithBench 52.6–55.7 | vendor's own |
| **MiniCheck-FT5** | Flan-T5-L fine-tuned on GPT-4-generated synthetic errors | **770M** | **Yes (local)** | **74.7% BAcc LLM-AggreFact** (GPT-4 = 75.3) | authors' own |
| Bespoke-MiniCheck-7B | 7B fine-tune | 7B | Yes (local) | 77.4% BAcc, tops the leaderboard | authors' own |
| Patronus Lynx 70B / 8B | fine-tuned Llama-3 judge | 70B / 8B | Yes, but impractical size | ~+1pt vs GPT-4o average on HaluBench; +8.3pt on PubMedQA; 8B beats GPT-3.5 by 24.5pt | authors' own, on the authors' own benchmark |
| Cleanlab TLM | LLM self-reflection + multi-sample consistency | API | No (samples repeatedly) | "highest precision/recall on 4 of 6" | **severe COI — see below** |
| AlignScore | RoBERTa-L, alignment-trained | 355M | Yes (local) | 70.4% BAcc; best average AUC-ROC on TRUE | third-party re-run / authors' own |
| SummaC-Conv | NLI + sentence-pair binning & convolution | small | Yes (local) | 62.1% BAcc (LLM-AggreFact); 74.4% on its own SummaC benchmark | third-party / authors' own |
| Generic T5-NLI-Mixed | off-the-shelf NLI | 11B | Yes (local) | **61.0% BAcc** | third-party |

**Provenance warnings on this table:**

- **Cleanlab TLM / "Real-Time Evaluation Models for RAG" (https://arxiv.org/abs/2503.21157):**
  single author, the paper is co-published on Cleanlab's own blog with Cleanlab's
  reproduction repo, and TLM — which wins — is Cleanlab's product. The paper also
  publishes ROC *curves* rather than a numeric AUROC table, so the margins cannot be read
  off independently. Treat as vendor marketing carrying an arXiv number.
- **Galileo Luna** benchmarks against GPT-3.5, not GPT-4, and publishes no LLM-AggreFact
  or FaithBench number.
- **Patronus Lynx** wins on HaluBench, which Patronus built.
- **Arize LibreEval's ground truth is model-generated.** A detector validated against an
  LLM council's consensus is measuring agreement with LLMs, not with facts.
- **RAGAS's 0.95** is on WikiEval only. GroUSE (144 hand-built unit tests over 7 generator
  failure modes, https://arxiv.org/abs/2409.06595) finds that judges correlating well with
  GPT-4 overall "do not generalize to our proposed criteria" and fail many individual
  cases — i.e. aggregate correlation hides per-case failure, which is precisely what a
  gate cares about.

**One finding deserves its own line, because it is Agent-Assure's own round-4 bug shipped
in a production tool.** DeepEval defines faithfulness as the *absence* of claims
contradicting the context; **with no context supplied, there is nothing to contradict, and
the score defaults to near-perfect.** An absent input read as *unconstrained*, pointing
toward PASS. The project's CLAUDE.md already names this class ("Every 'I don't know' must
point AWAY from PASS"). It is worth citing in the ADR as external evidence that the rule
generalizes beyond this repo.

**On MiniCheck and HHEM specifically, as requested:** both are small, local, permissively
licensed, and preserve determinism. HHEM-2.1-Open is 0.1B / Apache-2.0 / CPU-only /
unlimited context and beats GPT-4 on two of three RAG datasets by its maker's measurement.
MiniCheck-FT5 is 770M and matches GPT-4 on the standard benchmark at 1/446th the cost.
Either is a far better fit for this project's architecture than an API call, and both are
strictly better than the generic DeBERTa-MNLI that ADR-004 currently names.

---

## Q5 — First-party vendor citation/grounding features

**Short answer: none of them makes a third-party grounding gate redundant, and the two
that are even structurally comparable are opaque trained classifiers with zero published
accuracy.**

| Feature | Generation-time or post-hoc | Deterministic? | Published accuracy |
|---|---|---|---|
| **Anthropic Citations API** | Generation-time only — chunks supplied alongside the query; the same call emits citations | No | "up to 15% recall accuracy" improvement vs "most custom implementations" — vendor blog, no benchmark named, no methodology, no independent replication |
| **OpenAI Responses API annotations** (`url_citation`, file citations) | Generation-time only | No | none published |
| **OpenAI Evals model/fact graders** | Post-hoc, but the grader is itself an LLM call | No | task-specific rubrics only |
| **Google Vertex — Gemini `groundingSupports`** | Generation-time only | No | none published |
| **Google Vertex — Check Grounding API** | **Post-hoc** — takes an `answerCandidate` + up to 200 `facts` | No — model-based support classifier | none published; latency <500ms documented |
| **Azure AI Content Safety — Groundedness detection** | **Post-hoc** — `text` + `groundingSources` | No — classifier; "reasoning mode" literally calls a model | none published; English-optimized, no benchmark disclosed |
| **AWS Bedrock Guardrails — contextual grounding check** (`ApplyGuardrail`) | **Post-hoc, no model invoked in that call** | No — undisclosed trained classifier | **none published anywhere in AWS docs** |

Sources: https://claude.com/blog/introducing-citations-api ,
https://platform.claude.com/docs/en/build-with-claude/citations ,
https://developers.openai.com/api/docs/guides/tools-file-search ,
https://docs.cloud.google.com/generative-ai-app-builder/docs/check-grounding ,
https://learn.microsoft.com/en-us/azure/ai-services/content-safety/concepts/groundedness ,
https://docs.aws.amazon.com/bedrock/latest/userguide/guardrails-contextual-grounding-check.html

**The structural point.** Anthropic Citations, OpenAI annotations and Gemini
`groundingSupports` are all **generation-time**: they attach citations to text the same
model call is producing. None has an endpoint that accepts an already-written draft plus
a source store and returns a verdict. They therefore cannot be pointed at Agent-Assure's
actual input at all — a Markdown draft plus an evidence store captured in a separate
session. This is not a competitive weakness; it is a scope mismatch.

The three genuinely post-hoc ones (Vertex Check Grounding, Azure Groundedness, Bedrock
contextual grounding) compete on *scope* but not on *mechanism*: all three are opaque
trained classifiers, none claims determinism, and **not one publishes a precision, recall
or F1 number.** A regulated buyer who needs a defensible verdict cannot get one from any
of them.

Two further notes:
- Anthropic's "15%" is against ad hoc prompted citation, not against a grounding gate, and
  every vendor framing is "helps", "reduces", "improves" — never "certifies" or
  "guarantees".
- **Azure's "correction" feature silently rewrites ungrounded spans.** That is the exact
  architectural inverse of this project's fail-loud convention, and Microsoft discloses no
  error rate for the correction step itself.

**Verdict: no vendor feature makes `ground_check.py` redundant.** The differentiator that
survives contact with all of them is the one the project already has — a verdict that is a
mechanical, reproducible, auditable fact about the store rather than a classifier's score.

---

## Q6 — Prior art for the exact hybrid being proposed

**Short answer: no, the asymmetric-authority rule does not appear under any name in the
literature. Its two properties are provable from the definition, but they are original
synthesis and must be written into the ADR as claims to be tested, not cited as
established results.**

Adjacent literature clusters, each capturing part of the idea:

| Framing | What it covers | What it does not |
|---|---|---|
| **Selective prediction / learning to defer / abstention** (https://aclanthology.org/2021.acl-long.84/ , https://arxiv.org/pdf/2306.04459) | Risk–coverage vocabulary; a model abstaining when likely wrong; routing to an expert | Single-stage — the model decides for *itself*, not whether to overturn another stage |
| **Conformal factuality** — Mohri & Hashimoto, ICML 2024 (https://arxiv.org/abs/2402.10978) | Decompose into subclaims, calibrate a retention threshold by split conformal prediction, back off until the output is provably ≥1−α correct. Reported 80–90% correctness guarantees on FActScore/NQ/MATH while retaining a substantial portion of claims | Statistical guarantee over a distribution, not a per-claim mechanical fact; needs a calibration set |
| **"One-sided error"** (property testing / group testing) | A checker that can err in only one direction | Describes a *single* checker's error profile, not a two-stage combination rule |
| **"Sound but incomplete"** (formal verification) | A checker that never wrongly accepts, but may wrongly reject | Same limitation |
| **Neuro-symbolic generate-and-verify** (Logic-LM, SMT/Lean-checked LLM output) | A symbolic checker is authoritative; a neural component proposes | **Order is inverted:** LLM proposes → solver decides. Agent-Assure would be: deterministic gate decides → model may only demote |
| **Model cascades** (FrugalGPT, cheap-then-expensive routing) | Two-stage cost optimization | Routing for cost, not authority restriction |

**The finding, stated plainly: no source found names, states, or proves "a model-based
stage may only move a verdict toward FAILURE, never toward PASS" as a general design
pattern.** The closest vocabulary is "one-sided error" and "sound but incomplete", and
neither is about combining two stages.

The two properties of the design *do* follow directly from its definition, and should be
written as such:

1. **It preserves the first stage's Error-B exactly.** A one-directional veto cannot
   create a wrongful PASS, so the system's false-negative rate on the violation class is
   bounded above by the deterministic gate's alone. Error-B monotonicity — the project's
   own asymmetric invariant — is satisfied *by construction*, not by tuning.
2. **It can only increase Error-A.** Every FAIL the second stage adds is by definition a
   case the first stage would have passed. System-wide false alarms are monotonically
   non-decreasing in whatever the model adds.

These are original synthesis in this review, not a cited theorem. **Do not write "the
literature shows" next to them in ADR-004.**

**An important consequence for the actual problem.** Property 2 means an
add-flags-only model tier **cannot reduce the 0.320 Error-A rate — it can only make it
worse.** The current Error-A is driven by honest paraphrase reading UNGROUNDED; a tier
that may only move claims *away* from PASS cannot rescue a single one of those. So the
asymmetric design fixes the ~31 Error-B classes and worsens the false-alarm problem.
If the goal is *also* to recover honest paraphrase, that requires letting the model create
PASSes — which is squarely Escalation item #1, is not reversible, and should not be
decided by an agent.

---

## CONSOLIDATED REFERENCE TABLE

| System | Type | Size | Deterministic | Headline accuracy | Benchmark | Source is authors' own |
|---|---|---|---|---|---|---|
| GPT-4 judge | LLM judge | API | No | 75.3% BAcc | LLM-AggreFact | Y (MiniCheck's re-run) |
| GPT-4o judge | LLM judge | API | No | 56.3% BAcc | FaithBench | Y (FaithBench authors) |
| o3-mini-high zero-shot | LLM judge | API | No | 68.8% BAcc / 60.7% F1 | FaithBench (FaithJudge setup) | Y (Vectara) |
| o3-mini-high + FaithJudge few-shot | LLM judge + human annotations | API | No | 84.0% BAcc / 82.1% F1 | FaithBench | Y (Vectara) |
| Claude-3 Opus judge | LLM judge | API | No | 74.1% BAcc | LLM-AggreFact | Y |
| Bespoke-MiniCheck-7B | purpose-built | 7B | Yes (local) | 77.4% BAcc | LLM-AggreFact | Y |
| MiniCheck-FT5 | purpose-built | 770M | Yes (local) | 74.7% BAcc | LLM-AggreFact | Y |
| MiniCheck-DeBERTa-L | purpose-built | 355M | Yes (local) | 72.6% BAcc | LLM-AggreFact | Y |
| HHEM-2.1-Open | purpose-built | 0.1B | Yes (local, CPU) | 76.6 / 64.4 / 74.3 BAcc | AggreFact-SOTA / RAGTruth-Summ / RAGTruth-QA | Y (vendor) |
| HHEM-2.1 | purpose-built | 0.1B | Yes | 52.6–55.7% BAcc | FaithBench (two conflicting setups) | Y (vendor) |
| Galileo Luna | purpose-built | 440M | Yes (local) | +18% vs GPT-3.5 | proprietary RAG data | Y (vendor) |
| Patronus Lynx-70B | LLM judge fine-tune | 70B | Yes (local, impractical) | ~+1pt vs GPT-4o | HaluBench (own) | Y |
| AlignScore | alignment-trained | 355M | Yes (local) | 70.4% BAcc; best avg AUC on TRUE | LLM-AggreFact / TRUE | Y |
| SummaC-Conv | NLI + aggregation | small | Yes (local) | 62.1% / 74.4% BAcc | LLM-AggreFact / SummaC | Y |
| QAFactEval | QA-based | small | Yes (local) | 66.5% BAcc | LLM-AggreFact | Y |
| T5-NLI-Mixed | generic NLI | 11B | Yes (local) | 61.0% BAcc | LLM-AggreFact | third-party |
| DeBERTa-v3-large-MNLI-FEVER-ANLI | generic NLI | 435M | Yes (local) | 91.2 / 90.8 on MNLI (**not** a faithfulness benchmark) | MultiNLI | Y (model card) |
| RAGAS faithfulness | LLM judge pipeline | API | No | 0.95 human agreement | WikiEval only | Y |
| DeepEval faithfulness | LLM judge pipeline | API | No | none | — | — |
| TruLens groundedness | NLI or LLM | varies | NLI path yes | none | — | — |
| Arize Phoenix | LLM judge | API | No | LibreEval (LLM-council ground truth) | — | Y |
| Cleanlab TLM | multi-sample LLM | API | No | "best on 4/6" (ROC curves only) | 6 RAG datasets | Y, severe COI |
| Vertex Check Grounding | vendor classifier | — | No | none published | — | — |
| Azure Groundedness | vendor classifier | — | No | none published | — | — |
| Bedrock contextual grounding | vendor classifier | — | No | none published | — | — |
| Anthropic Citations | generation-time | — | No | "up to 15%" vs prompted citation | none named | Y |

---

## WHAT THE EVIDENCE DOES NOT SETTLE

These are the questions where no solid measurement was found. They are listed in
descending order of how much they matter to this decision.

1. **Whether any modern LLM judge handles negation.** No paper benchmarks GPT-4o,
   Claude-3.5+/4-class, or o1/o3-class models on ScoNe, NegNLI, MoNLI, NaN-NLI or
   CondaQA. The most recent direct measurements are on GPT-3 / InstructGPT (2023), which
   showed *inverse scaling*. The only adjacent modern evidence (o4-mini under
   negation-framed adversarial prompting, −25.6 points) points the wrong way. **This is
   the single most decision-relevant unmeasured fact**, because negation is the project's
   named failure.
2. **Whether any modern LLM judge handles attribution reversal.** No paper re-runs a
   CommitmentBank-style factive/non-factive task against GPT-4o or Claude with a number.
   The one relevant finding is that BERT scores 85% F1 on CommitmentBank *without*
   learning the factive/non-factive distinction — high score, mechanism absent.
3. **Run-to-run stability of a binary entailment verdict.** The inconsistency literature
   measures preference/quality scoring. No study reports "N identical calls, X% identical
   binary entailment verdict." Without that, the reproducibility cost of an LLM tier
   cannot be quantified for this specific task.
4. **Whether DeBERTa-MNLI beats or loses to an LLM judge on negation specifically.** No
   same-test-set head-to-head exists. The general "specialist beats generalist on its own
   turf" pattern (DeBERTa-v3 vs GPT-3-class on ANLI) is suggestive but not a measurement
   of this.
5. **Accuracy-vs-document-length curves for NLI-family checkers.** Everyone agrees
   degradation happens and chunk-and-aggregate is the fix; nobody publishes the curve.
   This matters because Agent-Assure's evidence store holds whole captured pages.
6. **Prompt-design ablations for grounding judgment.** No CoT-vs-no-CoT, no
   document-first-vs-claim-first isolation. Yet the FaithJudge result (68.8 → 84.0 from
   few-shot examples alone) says prompt context is the *largest* lever found — so the
   unmeasured thing is the thing that matters most.
7. **Domain stratification.** No breakdown of judge accuracy by domain (legal, medical,
   technical, news) for grounding.
8. **Exact wall-clock latency** for GPT-4 vs DeBERTa-class per claim. Only cost-per-test-
   set is comparable across sources.
9. **The FaithBench discrepancy** (HHEM-2.1 at 52.6% vs 55.68%; GPT-4o 56.29% vs
   o3-mini-high 68.8%) is unresolved here. Both sets are Vectara's, under different label
   binarizations of the three-way Unwanted/Questionable/Benign taxonomy.
10. **Independent replication is almost entirely absent across this whole field.** Nearly
    every number in this report is from the authors of the method or the vendor of the
    product. LLM-AggreFact's baselines re-run by the MiniCheck team are the closest thing
    to third-party measurement found, and even those are a competitor evaluating
    competitors.
11. **No prior art for the asymmetric-authority pattern.** Its two properties are derived,
    not cited.

---

## THE CHEAPEST NEXT STEP (not a recommendation to act, a measurement to run)

Everything above turns on one unmeasured fact: whether Agent-Assure's ~31 open Error-B
classes are *average* cases or *hard* cases. The repo already has the instrument — the
red-team fixtures in `tests/red_team_moat/` are a ready-made labeled set of exactly the
failures in question.

Run MiniCheck-FT5 (770M, local, free) and HHEM-2.1-Open (0.1B, CPU, free) over those
fixtures plus the 52 gold rows, as a *diagnostic only*, with no wiring into
`ground_check.py`. That produces the one number this literature cannot supply: how many
of *this project's* open classes a small local grounding model actually catches, and how
many honest-paraphrase rows it would newly flag. Both models are Apache-2.0 or
research-permissive, run offline, cost nothing, and touch no verdict path — so the
measurement itself is inside agent authority even though acting on it is not.

---

## SOURCE LIST

**Benchmarks and core papers**
- MiniCheck / LLM-AggreFact — https://arxiv.org/abs/2404.10774 , https://arxiv.org/html/2404.10774v2 , https://aclanthology.org/2024.emnlp-main.499/ , https://llm-aggrefact.github.io/blog
- FaithBench — https://arxiv.org/pdf/2410.13210 , https://aclanthology.org/2025.naacl-short.38/
- FaithJudge / Benchmarking LLM Faithfulness in RAG with Evolving Leaderboards — https://arxiv.org/pdf/2505.04847 , https://github.com/vectara/FaithJudge
- TRUE (Honovich et al., NAACL 2022) — https://aclanthology.org/2022.naacl-main.287/
- TrueTeacher — https://arxiv.org/html/2305.11171
- AlignScore — https://arxiv.org/pdf/2305.16739
- SummaC — https://arxiv.org/abs/2111.09525 , https://aclanthology.org/2022.tacl-1.10/
- RAGTruth — https://aclanthology.org/2024.acl-long.585/
- AttributionBench — https://osu-nlp-group.github.io/AttributionBench/
- GroUSE (meta-evaluation of judges) — https://arxiv.org/abs/2409.06595
- Lynx / HaluBench — https://arxiv.org/html/2407.08488v1 , https://www.patronus.ai/blog/lynx-state-of-the-art-open-source-hallucination-detection-model
- Galileo Luna — https://arxiv.org/abs/2406.00975 , https://aclanthology.org/2025.coling-industry.34/
- Real-Time Evaluation Models for RAG (Cleanlab COI) — https://arxiv.org/abs/2503.21157 , https://cleanlab.ai/blog/rag-evaluation-models/

**Judge failure modes**
- Large Language Models are not Fair Evaluators — https://arxiv.org/abs/2305.17926
- Judging LLM-as-a-Judge with MT-Bench and Chatbot Arena — https://arxiv.org/abs/2306.05685
- LLM Evaluators Recognize and Favor Their Own Generations — https://arxiv.org/abs/2404.13076
- Justice or Prejudice? Quantifying Biases in LLM-as-a-Judge (CALM) — https://arxiv.org/abs/2410.02736 , https://llm-judge-bias.github.io/
- Rating Roulette: Self-Inconsistency in LLM-As-A-Judge — https://arxiv.org/abs/2510.27106
- Large Language Models are Inconsistent and Biased Evaluators — https://arxiv.org/abs/2405.01724
- Overconfidence in LLM-as-a-Judge — https://arxiv.org/abs/2508.06225
- LLMs Cannot Reliably Judge (Yet?) — https://arxiv.org/abs/2506.09443

**Negation and factivity**
- Language models are not naysayers — https://arxiv.org/abs/2306.08189
- ScoNe — https://arxiv.org/abs/2305.19426 , https://github.com/selenashe/ScoNe
- CondaQA — https://arxiv.org/abs/2211.00295
- xNot360 — https://arxiv.org/abs/2306.16638
- Benchmarking Gaslighting Negation Attacks Against Reasoning Models — https://arxiv.org/abs/2506.09677
- Making Language Models Robust Against Negation — https://arxiv.org/abs/2502.07717
- The CommitmentBank — https://ojs.ub.uni-konstanz.de/sub/index.php/sub/article/view/601
- Evaluating BERT for NLI: A Case Study on the CommitmentBank — https://aclanthology.org/D19-1630/
- DeBERTa — https://arxiv.org/abs/2006.03654
- DeBERTa-v3-large-mnli-fever-anli-ling-wanli model card — https://huggingface.co/MoritzLaurer/DeBERTa-v3-large-mnli-fever-anli-ling-wanli

**Adversarial**
- JudgeDeceiver — https://arxiv.org/abs/2403.17710
- Cheating Automatic LLM Benchmarks: Null Models Achieve High Win Rates — https://arxiv.org/abs/2410.07137
- Vulnerability of LLM-as-a-Judge Architectures to Prompt-Injection — https://arxiv.org/abs/2505.13348

**Determinism**
- Defeating Nondeterminism in LLM Inference (Thinking Machines Lab, 2025-09-10) — https://thinkingmachines.ai/blog/defeating-nondeterminism-in-llm-inference/
- Understanding and Mitigating Numerical Sources of Nondeterminism in LLM Inference — https://arxiv.org/pdf/2506.09501
- The Good, The Bad, and The Greedy: Evaluation of LLMs Should Not Ignore Non-Determinism — https://arxiv.org/pdf/2407.10457

**Tools and models**
- Vectara HHEM-2.1-Open — https://huggingface.co/vectara/hallucination_evaluation_model
- Vectara hallucination leaderboard — https://github.com/vectara/hallucination-leaderboard
- RAGAS faithfulness — https://docs.ragas.io/en/stable/concepts/metrics/available_metrics/faithfulness/
- DeepEval faithfulness — https://deepeval.com/docs/metrics-faithfulness
- TruLens feedback functions — https://www.trulens.org/getting_started/core_concepts/feedback_functions/ , https://www.trulens.org/reference/trulens/providers/huggingface/
- Arize Phoenix LLM-as-a-judge — https://arize.com/docs/ax/evaluate/evaluators/llm-as-a-judge
- Arize LibreEval — https://arize.com/wp-content/uploads/2023/04/LibreEval-Phoenix-Open-Source-Hallucination-Evaluation-Model-Dataset-1.1.pdf
- Bespoke-MiniCheck — https://docs.bespokelabs.ai/models/bespoke-minicheck , https://github.com/Liyan06/MiniCheck

**Vendor grounding features**
- Anthropic Citations — https://claude.com/blog/introducing-citations-api , https://platform.claude.com/docs/en/build-with-claude/citations
- OpenAI file search / web search — https://developers.openai.com/api/docs/guides/tools-file-search , https://developers.openai.com/api/docs/guides/tools-web-search
- OpenAI graders — https://developers.openai.com/api/docs/guides/graders
- Vertex AI check grounding — https://docs.cloud.google.com/generative-ai-app-builder/docs/check-grounding
- Vertex grounding metadata — https://cloud.google.com/vertex-ai/generative-ai/docs/reference/rest/v1beta1/GroundingMetadata
- Azure groundedness detection — https://learn.microsoft.com/en-us/azure/ai-services/content-safety/concepts/groundedness
- Azure correction capability — https://techcommunity.microsoft.com/blog/azure-ai-foundry-blog/correction-capability-helps-revise-ungrounded-content-and-hallucinations/4253281
- AWS Bedrock contextual grounding check — https://docs.aws.amazon.com/bedrock/latest/userguide/guardrails-contextual-grounding-check.html

**Prior art / selective prediction**
- Conformal Language Modeling / Language Models with Conformal Factuality Guarantees (Mohri & Hashimoto, ICML 2024) — https://arxiv.org/abs/2402.10978 , https://proceedings.mlr.press/v235/mohri24a.html
- The Art of Abstention (ACL 2021) — https://aclanthology.org/2021.acl-long.84/
- Uncertainty in NLP survey — https://arxiv.org/pdf/2306.04459
