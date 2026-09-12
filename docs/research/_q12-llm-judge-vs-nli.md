# Q12 — How reliable is an LLM-as-judge at deciding whether a source SUPPORTS a claim?

**Research date:** 2026-09-12. **Scope:** faithfulness / groundedness / attribution / entailment judging —
i.e., exactly the decision Agent-Assure's `ground_check.py` currently makes deterministically without any
LLM call. This note asks the counterfactual: if Assure *did* let an LLM judge decide GROUNDED vs
UNGROUNDED, what would the empirical hit rate be, and how does that compare to the small-NLI-model
alternative already named in `ADR-004` (T3 NLI tier)?

**Method:** WebSearch + WebFetch against arXiv, ACL Anthology, and benchmark authors' own pages. Several
PDFs on arXiv could not be parsed by the fetch tool (binary/FlateDecode streams defeated the text
extractor) — those are marked "PDF unreadable by tool" below and the numbers instead come from
secondary summaries (emergentmind, alphaxiv, docs pages) that quote the papers' own tables. Where a
number is quoted by a third party rather than read directly off the paper, that is flagged in the table.

---

## 1. Numbers table

| # | Benchmark | Model / Method | Metric | Value | Source URL | Authors' own number? |
|---|---|---|---|---|---|---|
| 1 | LLM-AggreFact (MiniCheck, EMNLP 2024) | GPT-4 (zero-shot judge) | Balanced accuracy (avg over 10 datasets) | **75.3%** | https://arxiv.org/abs/2404.10774 / https://arxiv.org/pdf/2404.10774 | Y (MiniCheck authors, Tang et al. 2024) |
| 2 | LLM-AggreFact | Claude-3 Opus (zero-shot judge) | Balanced accuracy | **74.1%** | https://arxiv.org/pdf/2404.10774 | Y |
| 3 | LLM-AggreFact | GPT-3.5-turbo (zero-shot judge) | Balanced accuracy | Reported as a weak baseline, materially below GPT-4/Claude-3 (exact figure not extracted; secondary source describes it only qualitatively) | https://arxiv.org/pdf/2404.10774 | Y (unverified exact digit) |
| 4 | LLM-AggreFact | MiniCheck-Flan-T5-Large (770M) | Balanced accuracy | **74.7%** — matches/edges GPT-4 | https://arxiv.org/pdf/2404.10774 ; https://www.getmaxim.ai/blog/minicheck-llm-fact-check/ | Y |
| 5 | LLM-AggreFact | MiniCheck-DeBERTa-Large (355M) | Balanced accuracy | **72.6%** | https://arxiv.org/pdf/2404.10774 | Y |
| 6 | LLM-AggreFact | MiniCheck-RoBERTa-Large (355M) | Balanced accuracy | **72.7%** | https://arxiv.org/pdf/2404.10774 | Y |
| 7 | LLM-AggreFact | AlignScore (RoBERTa-Large, 355M) | Balanced accuracy | **70.4%** | https://arxiv.org/pdf/2404.10774 | Y (MiniCheck's own re-run of AlignScore) |
| 8 | LLM-AggreFact | SummaC-ZS | Balanced accuracy | **67.9%** | https://arxiv.org/pdf/2404.10774 | Y |
| 9 | LLM-AggreFact | SummaC-Conv | Balanced accuracy | **62.1%** | https://arxiv.org/pdf/2404.10774 | Y |
| 10 | LLM-AggreFact | QAFactEval | Balanced accuracy | **66.5%** | https://arxiv.org/pdf/2404.10774 | Y |
| 11 | LLM-AggreFact (public leaderboard, post-paper) | Bespoke-MiniCheck-7B | Balanced accuracy | **77.4%** (tops the public leaderboard, beats GPT-4-turbo) | https://docs.bespokelabs.ai/models/bespoke-minicheck ; https://github.com/Liyan06/MiniCheck | Y (Bespoke Labs, method authors, not independent) |
| 12 | LLM-AggreFact | GPT-4-turbo (gpt-4-0125-preview) | Balanced accuracy | Cited as "top evaluator" alongside Bespoke-7B at time of leaderboard snapshot; exact digit not independently confirmed by this pass | https://arxiv.org/pdf/2501.14883 (title only readable; PDF unreadable by tool) | Y (leaderboard self-report) |
| 13 | TRUE (Honovich et al., NAACL 2022) | Large NLI models (T5-11B-ANLI etc.) | ROC-AUC | SOTA on TRUE at publication; TrueTeacher-augmented model raises AUC **82.7 → 87.8** | https://aclanthology.org/2022.naacl-main.287/ ; https://arxiv.org/html/2305.11171 (TrueTeacher) | Y (TrueTeacher authors' delta, not independent) |
| 14 | TRUE | AlignScore-Large (355M) | Average AUC-ROC | Highest average AUC-ROC on TRUE, beating "metrics based on ChatGPT and GPT-4, which are orders of magnitude larger" (exact digit not extracted) | https://arxiv.org/pdf/2305.16739 ; https://liner.com/review/alignscore-evaluating-factual-consistency-with-unified-alignment-function | Y (AlignScore authors) |
| 15 | SummaC benchmark (6 inconsistency-detection datasets) | SummaC-Conv | Balanced accuracy | **74.4%**, "+5 pts over prior work" at publication (2022) | https://arxiv.org/abs/2111.09525 ; https://aclanthology.org/2022.tacl-1.10/ | Y |
| 16 | AttributionBench | GPT-4 / GPT-3.5 (zero-shot judge) | Accuracy | **>80%** on short-evidence subsets (AttributedQA, AttrEval-GenSearch); degrades on longer/harder subsets (no digit extracted for the hard split) | https://osu-nlp-group.github.io/AttributionBench/ | Y (benchmark authors) |
| 17 | RAGTruth (ACL 2024) | GPT-4-turbo (prompted zero-shot judge) | Precision / Recall / F1 (response-level) | **P=33.2, R=90.6, F1=45.6** | https://aclanthology.org/2024.acl-long.585/ ; secondary summary via WebSearch | Y (RAGTruth authors' own evaluation of GPT-4-turbo as detector) |
| 18 | RAGTruth | GPT-4 (general, various prompts) | Response-level F1 | Reported range **63–64%** in a follow-up survey framing (moderate) | secondary summary, exact paper not isolated | Ambiguous — likely a survey's re-quote, not RAGTruth's own primary number; treat as low-confidence |
| 19 | FaithBench (NAACL 2025 short) | GPT-4o-as-judge and other SOTA detectors | Accuracy on the "challenging" (disagreement-selected) subset | **~50%**, i.e. near chance — explicit finding of the paper | https://aclanthology.org/2025.naacl-short.38/ | Y (FaithBench authors) |
| 20 | FaithBench / FaithJudge (Vectara, 2025) | HHEM-2.1 (small NLI-style hallucination model) | Balanced accuracy / F1-macro | **52.6% / 32.9%** | https://github.com/vectara/FaithJudge ; https://arxiv.org/pdf/2505.04847 | Y (Vectara, HHEM's own vendor) |
| 21 | FaithBench / FaithJudge | o3-mini-high, **zero-shot** LLM judge | Balanced accuracy / F1-macro | **68.8% / 60.7%** | https://github.com/vectara/FaithJudge | Y (Vectara) |
| 22 | FaithBench / FaithJudge | o3-mini-high **+ FaithJudge** (few-shot with human-annotated hallucination examples for the same source article) | Balanced accuracy / F1-macro | **84.0% / 82.1%** | https://github.com/vectara/FaithJudge | Y (Vectara) |
| 23 | Vectara Hallucination Leaderboard (generation-side, NOT judge accuracy — included for contrast) | GPT-4o / Gemini-2.0-Flash / Claude-3-Opus | Hallucination rate on ~1k-doc summarization set | GPT-4o **1.5%**, Gemini-2.0-Flash **0.7%**, Claude-Opus **10.1%**, Claude-Sonnet **4.4%** | https://www.vectara.com/blog/introducing-the-next-generation-of-vectaras-hallucination-leaderboard | Y — and note this measures generation faithfulness, not judge accuracy; do not conflate with rows above |
| 24 | FActScore (Min et al. 2023) | Human vs human (two annotators) | Inter-annotator agreement | **84.8%** raw agreement, **Cohen's κ = 0.55** on factuality labels | secondary summary of Min et al. 2023, plus ExpertQA's independent-unit κ = 0.52 | Y (benchmark authors' own annotation-quality report) |
| 25 | RAGTruth | Human vs human (2 annotators, 3rd tiebreak) | Inter-annotator agreement | **91.8%** response-level, **78.8%** span-level | https://aclanthology.org/2024.acl-long.585/ (secondary summary) | Y |
| 26 | MiniCheck synthetic-data QC | Human vs human, on C2D / D2C synthetic instances | Accuracy vs a "gold" answer, Fleiss' κ | C2D: 80% acc, κ=0.51; D2C: 78% acc, κ=0.70; human baseline accuracy 85% (C2D) / 88% (D2C) | https://arxiv.org/pdf/2404.10774 (via emergentmind extraction) | Y |
| 27 | DeBERTa-v3-large-MNLI-FEVER-ANLI-LING-WANLI (MoritzLaurer) | — | Accuracy on MultiNLI matched / mismatched (not a faithfulness benchmark, but the base entailment task) | **91.2% / 90.8%** | https://huggingface.co/MoritzLaurer/DeBERTa-v3-large-mnli-fever-anli-ling-wanli | Y (model card, self-reported) |
| 28 | Ad hoc "factual entailment with NLI" study | GPT-4 zero-shot vs DeBERTa-NLI | Accuracy | Both **~80%**, reported as roughly tied | https://arxiv.org/pdf/2406.16842 (title/abstract level; PDF not fully parsed) | Y, single small study — do not over-generalize |

---

## 2. What the numbers say, synthesized

### 2.1 On LLM-AggreFact, GPT-4-class judges land at 74–75% balanced accuracy — and a 770M-parameter NLI-style model matches them

The single most load-bearing number for this decision is from MiniCheck (Tang et al., EMNLP 2024,
https://arxiv.org/abs/2404.10774), because it is the only paper found that (a) evaluates GPT-4, GPT-3.5,
and Claude-3 Opus as zero-shot faithfulness judges, (b) evaluates several purpose-built small models on
the *identical* aggregated benchmark, and (c) reports the metric (balanced accuracy) the taxonomy in this
repo's `ADR-006` already treats as the right yardstick.

- GPT-4: 75.3% BAcc (row 1)
- Claude-3 Opus: 74.1% BAcc (row 2)
- MiniCheck-Flan-T5-Large (770M, $0.24 for the 13K-example test set): 74.7% BAcc (row 4) — statistically
  indistinguishable from GPT-4, at **~400× lower cost** than the paper's own GPT-4 API bill ($107 for the
  same test set)
- AlignScore (355M RoBERTa): 70.4% (row 7) — 5 points below GPT-4, but zero-LLM-call and near-instant
- SummaC-ZS/Conv, QAFactEval (all pre-LLM-era, 2021–2022 vintage): 62–68% (rows 8–10) — meaningfully
  weaker than either GPT-4 or MiniCheck

A subsequently released model from the same MiniCheck lineage, Bespoke-MiniCheck-7B, tops the *public*
leaderboard at 77.4% (row 11), ahead of GPT-4-turbo. That number is self-reported by the model's own
vendor (Bespoke Labs) rather than by an independent replication, so treat it as directional, not
definitive — but it corroborates the qualitative finding: purpose-trained small models are not just
"close to" GPT-4-class judges on this task, they can beat them.

**Reading against Assure's decision:** none of GPT-4, Claude-3 Opus, GPT-4-turbo, MiniCheck, or AlignScore
clears 80% balanced accuracy on this aggregate benchmark. That is the ceiling literature currently shows
for *any* automatic faithfulness judge — LLM or small-model — on a benchmark that spans summarization,
dialogue, and long-form QA. This directly supports Assure's existing design bet (deterministic T1 rules,
ADR-006) over "just ask GPT-4," because GPT-4 does not clear a bar Assure's own CR-004 already exceeds in
a narrower, harder-to-game way (Error-B = 0.000 on 52 gold rows, by refusing to trust anything but
verbatim span match).

### 2.2 On adversarially curated ("challenging") cases, judge accuracy collapses toward chance

FaithBench (row 19, ACL Anthology 2025.naacl-short.38) is explicitly constructed by selecting summaries
where state-of-the-art hallucination detectors — including GPT-4o-as-judge — *disagreed* with each other.
On that disagreement-selected subset, "most state-of-the-art hallucination detection models have near-50%
accuracies" — i.e., indistinguishable from a coin flip on the exact cases that matter most (the ones where
a real gate decision is contested). This is the sharpest evidence in this pass that **LLM-judge reliability
is not a fixed number — it is benchmark-difficulty-dependent, and it degrades hardest exactly where a gate
needs it most:** the boundary cases, not the easy ones.

Vectara's own FaithJudge follow-up (rows 20–22, https://github.com/vectara/FaithJudge) makes the mechanism
explicit: a small purpose-built NLI-style model (HHEM-2.1) scores 52.6% BAcc / 32.9% F1-macro on
FaithBench-hard — barely above chance. A zero-shot LLM judge (o3-mini-high) does meaningfully better at
68.8% BAcc / 60.7% F1. But the big jump comes from neither architecture change nor scale: giving that same
o3-mini-high judge a handful of **human-annotated hallucination examples for the same source article**
(few-shot, in-context) lifts it to 84.0% BAcc / 82.1% F1 — a +15-point swing from prompt design/context
alone. This is the paper's own load-bearing finding, and it is squarely "what moves the numbers" (research
question 3): retrieval-augmented, example-grounded prompting beats both raw model scale and raw zero-shot
LLM judgment.

### 2.3 Claim granularity: atomic decomposition helps weak verifiers, has diminishing/negative returns for strong ones

The "Decomposition Dilemmas" paper (arxiv 2411.02400) and the granularity-search literature it cites (WiCE,
DnDScore) converge on a claim that is directly relevant to Assure's own atomic-claim decomposition step in
`ground_check.py`: decomposing into atomic sub-claims **reduces the complexity a weak verifier has to
handle and helps it most**; a strong verifier's marginal accuracy gain from decomposition may not offset
the extra noise decomposition introduces (over-decomposition errors, loss of context, "context omission").
No paper reviewed in this pass reports a single universal atomicity level — each verifier they test has
"its own preferred input atomicity at which verification confidence peaks." This is evidence *for* keeping
Assure's grounding deterministic and rule-driven (a rule can be tuned per verdict class without model
retraining) and evidence *against* assuming finer-grained decomposition is a free win if an LLM judge were
ever added as a secondary check.

### 2.4 Document length and long-context degradation

The original SummaC paper (Laban et al. 2022, arxiv 2111.09525 / TACL) exists specifically because
"NLI datasets are sentence-level" while "inconsistency detection is document-level" — sentence-pair NLI
degrades when forced onto whole long documents, which is why SummaC segments into sentence pairs and
aggregates (binning + 1-D convolution) rather than running one NLI call over an entire document. A more
recent 2025 stress-test paper ("Stress Testing Factual Consistency Metrics for Long-Document
Summarization," arxiv 2511.07689 — PDF unreadable by the fetch tool, so this is a lower-confidence read)
reports that NLI-based (SummaC, AlignScore) and QA-based (QAFactEval) metrics all lose accuracy as document
length grows past what they were trained/calibrated on, and that chunking + aggregation is the standard
mitigation rather than any single-pass fix. No exact accuracy-vs-length curve could be extracted from the
tool in this pass — flag this as a literature gap (see §3).

**Relevance to Assure:** this is the direct analogue of why `ground_check.py`'s T1 rule requires a
"contiguous verbatim span ≥8 tokens" rather than whole-document semantic matching — it sidesteps the
long-document NLI degradation problem entirely by not doing soft semantic matching over long spans at all.

### 2.5 Human agreement ceiling

Every human-vs-human number found in this pass is well under 100%, which bounds what *any* automatic
judge — LLM or NLI — can be expected to achieve if measured against a single ratifier's labels, matching
this repo's own CR-004 caveat ("single ratifier ... NOT external ground truth"):

- FActScore: 84.8% raw agreement, Cohen's κ = 0.55 (row 24)
- ExpertQA: κ = 0.52 on the "independent unit" judgment (row 24, cross-reference)
- RAGTruth: 91.8% response-level agreement, but only 78.8% at the harder span-level granularity (row 25)
- MiniCheck's own synthetic-data QC: κ = 0.51 (C2D) / 0.70 (D2C), human accuracy against a gold answer of
  85–88% (row 26)

Two things to take from this: (1) span-level and claim-level agreement (78.8%, ~80–85%) is consistently
lower than response/document-level agreement (91.8%) — agreement drops as the judgment gets more granular,
which is exactly the granularity Assure operates at (atomic claim, not whole document); (2) no LLM judge
number surveyed here (52–84% BAcc depending on benchmark difficulty) clears even the *low* end of the human
agreement band with confidence — GPT-4's 75.3% on LLM-AggreFact sits inside typical human-disagreement
territory, not comfortably above it.

### 2.6 The NLI-vs-LLM-judge cost/latency question

Numbers found:
- MiniCheck-FT5 (770M, CPU/small-GPU-feasible): $0.24 for a 13K-example test set (row 4)
- GPT-4 API cost for the same 13K-example set: ~$107 (row 4) — **~446×** more expensive, consistent with
  the paper's own "400× cheaper" framing
- AlignScore (355M): comparable-or-better accuracy to ChatGPT/GPT-4-based metrics on TRUE, at orders of
  magnitude fewer parameters (row 14) — no exact latency figure was extracted, but sub-second local
  inference is implied by the small model size (355M parameters run comfortably on a single GPU or even
  CPU for short inputs)

No paper in this pass reported wall-clock latency numbers precisely (tokens/sec, ms/claim) for GPT-4 vs
DeBERTa-class models — that is a literature gap; the cost-per-test-set numbers above are the only
apples-to-apples comparison found, and they are unambiguous: **an API call per claim is not justified by
the accuracy gap.** The accuracy gap between GPT-4 (75.3%) and a 355M-parameter specialist (70.4%,
AlignScore) is 4.9 points; between GPT-4 and a 770M specialist trained for exactly this task
(MiniCheck-FT5, 74.7%) it is 0.6 points, within noise of a single held-out run. Given Assure's own
architecture doctrine ("ZERO LLM calls during grounding" is the moat, not a preference), this literature
supports the T3 NLI tier named in ADR-004 over any LLM-judge alternative on accuracy grounds, before even
counting the moat-integrity argument (an LLM call inside the grounding path reopens exactly the prompt-
injection / talk-its-way-to-PASS attack surface the moat exists to close).

---

## 3. Where the literature does not answer the question (explicit gaps)

1. **No paper found isolates "chain-of-thought vs no-CoT" or "document-first vs claim-first" prompt-order
   ablations on a faithfulness/attribution benchmark with a reported accuracy delta.** General LLM-as-judge
   literature (Improve LLM-as-a-Judge, arxiv 2502.11689; various RAG-eval surveys) discusses CoT and rubric
   design qualitatively as bias-mitigation techniques, but no benchmark-specific number for "faithfulness
   judging accuracy with vs without CoT" was located in this pass. The nearest empirical analogue found is
   FaithJudge's few-shot-with-human-examples result (row 22), which is a different lever (in-context
   examples, not CoT reasoning) but is the strongest "prompt design moves the number" evidence available.
2. **No exact accuracy-vs-document-length curve** was extracted (the 2511.07689 stress-test PDF was
   unreadable by the fetch tool); the qualitative direction (longer → worse) is well corroborated across
   three independent sources (SummaC's original motivation, the stress-test paper's abstract-level claim,
   and general "LLMs degrade over long sequences" folk knowledge cited in a WiCE-adjacent search result),
   but no single number should be quoted from this file for "X% drop per Y tokens."
3. **Domain-specific numbers (legal vs news vs dialogue) were not separately isolated** beyond what
   LLM-AggreFact's dataset mix implies (it spans CNN/XSum summarization, MediaSum/MeetingBank dialogue
   summarization via TofuEval, and QA-style ExpertQA/LFQA) — the paper reports one averaged balanced
   accuracy per model, not a domain-stratified breakdown, in the material this pass could extract. A
   dataset-by-dataset breakdown likely exists in the paper's full results table (Table 2 was only partially
   recovered via the emergentmind secondary extraction) — recommend a follow-up direct PDF-text extraction
   (e.g. via `pdftotext` locally) if per-domain numbers become decision-relevant.
4. **GPT-4o specifically (as opposed to GPT-4 / GPT-4-turbo) was not found benchmarked on LLM-AggreFact
   with an extractable balanced-accuracy digit** in this pass — GPT-4o appears in FaithBench (row 19, as a
   generator, and implicitly among the "SOTA hallucination detection models" that score ~50% on the hard
   subset) and in the Vectara generation leaderboard (row 23, a different task), but not with a directly
   attributable LLM-AggreFact BAcc number.

---

## 4. Source list

- MiniCheck (Tang, Laban, Durrett; EMNLP 2024) — https://arxiv.org/abs/2404.10774 / https://arxiv.org/pdf/2404.10774 / https://aclanthology.org/2024.emnlp-main.499/
- MiniCheck GitHub (model cards, benchmark demo notebook) — https://github.com/Liyan06/MiniCheck
- Bespoke-MiniCheck docs — https://docs.bespokelabs.ai/models/bespoke-minicheck
- "Verify with Caution: The Pitfalls of Relying on Imperfect Factuality Metrics" — https://arxiv.org/pdf/2501.14883 (title/context only; full text unreadable by fetch tool this pass)
- TRUE: Re-evaluating Factual Consistency Evaluation (Honovich et al., NAACL 2022) — https://aclanthology.org/2022.naacl-main.287/
- TrueTeacher (Gekhman et al. 2023) — https://arxiv.org/abs/2305.11171 / https://arxiv.org/html/2305.11171
- AlignScore (Zha et al., ACL 2023) — https://arxiv.org/abs/2305.16739 / https://arxiv.org/pdf/2305.16739 / https://aclanthology.org/2023.acl-long.634/
- SummaC (Laban et al., TACL 2022) — https://arxiv.org/abs/2111.09525 / https://aclanthology.org/2022.tacl-1.10/
- AttributionBench (OSU NLP Group) — https://osu-nlp-group.github.io/AttributionBench/
- RAGTruth (Niu et al., ACL 2024) — https://aclanthology.org/2024.acl-long.585/
- FaithBench (NAACL 2025 short) — https://aclanthology.org/2025.naacl-short.38/ (PDF unreadable by tool; findings via ACL abstract page + secondary summaries)
- Vectara FaithJudge (2025) — https://github.com/vectara/FaithJudge
- Benchmarking LLM Faithfulness in RAG with Evolving Leaderboards (Vectara et al., EMNLP-Industry 2025) — https://arxiv.org/abs/2505.04847 / https://arxiv.org/pdf/2505.04847
- Vectara Hallucination Leaderboard blog — https://www.vectara.com/blog/introducing-the-next-generation-of-vectaras-hallucination-leaderboard
- FActScore (Min et al. 2023) — cited via secondary search summary; original: "FActScore: Fine-grained Atomic Evaluation of Factual Precision in Long Form Text Generation," arXiv:2305.14251 (not independently re-fetched this pass)
- ExpertQA (Malaviya et al. 2024) — cited via secondary summary alongside FActScore
- Decomposition Dilemmas: Does Claim Decomposition Boost or Burden Fact-Checking Performance? — https://arxiv.org/html/2411.02400v1
- Optimizing Decomposition for Optimal Claim Verification — https://arxiv.org/pdf/2503.15354
- Stress Testing Factual Consistency Metrics for Long-Document Summarization — https://arxiv.org/pdf/2511.07689 (PDF unreadable by tool; findings summarized from partial extraction only — low confidence)
- MoritzLaurer DeBERTa-v3-large-mnli-fever-anli-ling-wanli model card — https://huggingface.co/MoritzLaurer/DeBERTa-v3-large-mnli-fever-anli-ling-wanli
- "Exploring Factual Entailment with NLI: A News Media Study" — https://arxiv.org/pdf/2406.16842 (abstract-level only)
- getmaxim.ai summary of MiniCheck cost figures — https://www.getmaxim.ai/blog/minicheck-llm-fact-check/

---

## 5. Load-bearing assumption in this report

The single most decision-relevant number — GPT-4 at 75.3% BAcc on LLM-AggreFact vs MiniCheck-FT5 at 74.7%
— comes from **one paper's own benchmark and one paper's own re-implementation of the baselines**
(MiniCheck authors ran GPT-4 themselves; they are not quoting an independent GPT-4-on-LLM-AggreFact
replication). If MiniCheck's prompt for GPT-4 was suboptimal (no CoT, unfavorable ordering, etc. — see gap
#1 above), the true GPT-4 ceiling could be a few points higher, which would weaken the "small NLI model is
competitive" conclusion somewhat. It would not overturn the report's central finding, since FaithBench's
independent ~50%-on-hard-cases result and the human-agreement ceiling numbers (κ ≈ 0.5–0.7) are from
different author groups and point the same direction: no automatic judge, LLM or NLI, is currently
reliable enough on hard/adversarial cases to be trusted as a sole arbiter, which is the finding Assure's
zero-LLM-call moat design already assumes.
