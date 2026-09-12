# Q56 — Vendor Citation/Grounding Features and Prior Art for Asymmetric-Authority Verification

Research date: 2026-09-12. Compiled for the Agent-Assure moat-vs-market-redundancy question:
does any first-party vendor citation/grounding feature make `ground_check.py` (a deterministic,
post-hoc, zero-LLM-call grounding gate) redundant, and does the "model may only move a verdict
toward FAILURE, never toward PASS" design have named prior art.

**Headline answer, stated first:** No first-party feature surveyed is a post-hoc verifier that
takes an arbitrary (draft, evidence) pair with no model in the loop and returns a deterministic
verdict. Every generation-time feature (Anthropic Citations, OpenAI annotations, Gemini
`groundingSupports`) only attaches citations to text the *same model call* is producing — it
cannot certify a draft the model didn't write this turn, and none of them publish a hard
guarantee (all are framed as "reduces," "helps," "improves," never "eliminates" or "certifies").
The two genuinely post-hoc checkers — **Vertex AI Check Grounding** and **Azure Groundedness
Detection** — are themselves LLM-based classifiers (not deterministic, not zero-LLM-call), so
even where they compete on scope they do not compete on moat mechanism. **AWS Bedrock
`ApplyGuardrail`** is the one vendor surface that can run standalone against arbitrary text with
no model invocation in that call — but the check itself is still a trained relevance/grounding
classifier, not a symbolic span-matcher, and AWS publishes no accuracy numbers for it at all.

---

## Topic A — First-party citation/grounding features

### Vendor comparison table

| Feature | Generation-time or post-hoc | Deterministic? | Published accuracy | Source |
|---|---|---|---|---|
| Anthropic Citations API | Generation-time only (chunks are supplied alongside the query; the *same* model call produces the citation) | No — model-generated, not stated to be deterministic | "increasing recall accuracy by up to 15%" vs "most custom [prompt-based] implementations" — vendor-self-reported, no independent replication found, no benchmark name or eval methodology published on the blog | [Introducing Citations on the Anthropic API](https://claude.com/blog/introducing-citations-api); [Citations docs](https://platform.claude.com/docs/en/build-with-claude/citations) |
| OpenAI Responses API — `web_search` / `file_search` annotations | Generation-time only (`url_citation` / file-citation annotations are emitted inline with the same response) | No | None published (no accuracy/eval number found for the annotation mechanism itself) | [Web search guide](https://developers.openai.com/api/docs/guides/tools-web-search); [File search guide](https://developers.openai.com/api/docs/guides/tools-file-search) |
| OpenAI Evals — model graders / fact graders | Post-hoc, but the grader itself is another LLM call (not deterministic, not zero-LLM) | No | Task-specific only (e.g., HealthBench rubric scores); no general groundedness accuracy figure | [Graders](https://developers.openai.com/api/docs/guides/graders); [Model Spec Evals](https://alignment.openai.com/model-spec-evals/) |
| Google Vertex AI — Grounding with Google Search / with your data (Gemini `groundingMetadata`) | Generation-time only — `groundingSupports` links response spans to `groundingChunks` produced in the same generate call | No | None published as a standalone grounding-accuracy number | [Grounding metadata reference](https://cloud.google.com/vertex-ai/generative-ai/docs/reference/rest/v1beta1/GroundingMetadata); [Grounding with Google Search](https://ai.google.dev/gemini-api/docs/google-search) |
| **Google Vertex AI — Check Grounding API** | **Post-hoc** — takes an already-produced `answerCandidate` plus up to 200 `facts` as separate inputs; explicitly documented as evaluating text that need not have come from the same call | Not stated to be deterministic; it is a model-based support-score classifier, not a symbolic matcher | Overall support score (0–1) and per-claim support score (0–1) are returned per request; no published aggregate accuracy/precision/recall benchmark found; latency documented as <500ms | [Check grounding with RAG](https://docs.cloud.google.com/generative-ai-app-builder/docs/check-grounding) |
| **Azure AI Content Safety — Groundedness detection** | **Post-hoc** — takes `text` + `groundingSources` (+ optional `query`) as independent inputs; not tied to a generation call | No — it is an LLM/classifier-based detector; "Reasoning mode" literally calls a model to produce an explanation | No published precision/recall/F1 numbers in the public docs surveyed; English-only, and accuracy is stated to be "optimized for English" with no benchmark disclosed; correction feature is a *generative rewrite*, not a verified-safe patch | [Groundedness detection concepts](https://learn.microsoft.com/en-us/azure/ai-services/content-safety/concepts/groundedness); [Correction capability](https://techcommunity.microsoft.com/blog/azure-ai-foundry-blog/correction-capability-helps-revise-ungrounded-content-and-hallucinations/4253281) |
| **AWS Bedrock Guardrails — Contextual grounding check** | **Post-hoc-capable** — via `ApplyGuardrail`, no model is invoked in that call at all; you pass `grounding_source`, `query`, and the content-to-guard directly, so it can run over an arbitrary already-written draft | Not stated to be deterministic; scores are produced by an underlying (undisclosed) classifier model, not a rule engine | Grounding and relevance scores in [0, 1] with a configurable threshold (0–0.99); **no published accuracy, precision/recall, or benchmark numbers found anywhere in AWS docs** — only worked qualitative examples | [Contextual grounding check docs](https://docs.aws.amazon.com/bedrock/latest/userguide/guardrails-contextual-grounding-check.html) |

### Per-vendor detail

**1. Anthropic Citations API.**
Mechanism: the caller marks a `document` block with `"citations": {"enabled": true}`; Anthropic
chunks the document into sentences server-side; the *same* model call that answers the user's
question emits citation objects referencing those chunks. This is unambiguously
**generation-time**: citations are a byproduct of one generation, not a separate check you run
against a draft that already exists. There is no documented endpoint or parameter that accepts an
arbitrary already-written draft plus a source and returns citations or a verdict for that draft —
i.e., **Citations cannot be run post-hoc over a draft the model already wrote in a prior turn or
a different system**. The published number — "increasing recall accuracy by up to 15%" — is
stated on Anthropic's own launch blog as a comparison against "most custom implementations"
(i.e., ad hoc prompted citation), not against a third-party grounding gate, not against a
held-out human-labeled benchmark with a disclosed methodology, and not independently replicated
anywhere found in this search. Anthropic does not claim citations are guaranteed accurate — the
framing throughout is "helping you track and verify," "reducing hallucinations," never
"eliminates" or "certifies." No determinism claim is made anywhere in the docs (citations come
from an autoregressive model call, so nothing suggests they would be deterministic across
identical requests).
Verdict: **does not compete with `ground_check.py`.** It is a UX/trust feature bolted onto
generation, not a verifier that can even be pointed at Agent-Assure's actual input (a
model-authored Markdown draft plus a captured evidence store from a separate session).

**2. OpenAI — file_search / web_search annotations, Responses API.**
`url_citation` and file-citation objects are `annotations` attached inline to the same response
that used the tool; the offsets (`start_index`/`end_index` or character ranges) point into the
model's own output text. Same structural limitation as Anthropic: generation-time only, no
standalone "verify this arbitrary draft against these sources" endpoint. OpenAI Evals' model
graders (including "fact graders" that check specific factual claims against expected facts) *can*
run post-hoc over arbitrary text, but the grader is itself another LLM call scored 1–7 by rubric —
not deterministic, not free of LLM calls, and not marketed as a groundedness-specific product with
a published accuracy number; it is a generic eval-framework primitive, task-scored per rubric
(e.g., HealthBench), not a general-purpose grounding certifier.
Verdict: **no post-hoc, deterministic, vendor-published-accuracy competitor** at OpenAI.

**3. Google Vertex AI.**
Two distinct things exist and are easy to conflate:
- *Grounding with Google Search* / *Grounding with your data* + Gemini's `groundingMetadata`
  (`groundingChunks`, `groundingSupports`, `webSearchQueries`) — generation-time, exactly like
  Anthropic/OpenAI: spans in the model's own output are linked to chunks retrieved during that
  same call.
- **Check Grounding API** (part of Vertex AI Agent Builder / Search) — this is the one Google
  surface that is genuinely post-hoc: it takes an `answerCandidate` (already-written text, up to
  4096 tokens) and a `facts` array (up to 200 facts, ≤10k characters each) as two independent
  inputs, with no requirement that the candidate came from a Vertex generation call at all. It
  returns an overall `supportScore` (0–1) and, if `enableClaimLevelScore` is set, a per-claim
  score plus citations mapping each claim to supporting facts. Documented latency is under 500ms.
  No determinism claim and no published precision/recall/F1 benchmark were found — Google
  describes the score's meaning ("how much the answer candidate agrees with the given facts") but
  not a validated accuracy rate against any gold set.
Verdict: **this is the closest first-party analog to `ground_check.py`'s task shape** (arbitrary
draft + arbitrary facts in, verdict out) but it is a black-box neural classifier, not a
deterministic span-matcher — it cannot offer the "zero LLM calls, mechanical fact about the
store" property that is Agent-Assure's actual moat claim, and Google publishes no accuracy number
to weigh against Agent-Assure's own CR-004 rates.

**4. Azure AI Content Safety — Groundedness detection.**
Post-hoc by design: input is `text` (already-produced) + `groundingSources` + optional `query`,
independent of any generation call. Two modes: **Non-Reasoning** (fast, binary
grounded/ungrounded, no explanation) and **Reasoning** (slower, returns a `reasoning` field
explaining flagged spans — this mode is documented as invoking additional model reasoning, so it
is not deterministic either). The **correction** capability (preview) goes further than any other
vendor surveyed: it rewrites the ungrounded span to match the grounding source and returns a
`correctedText` field — worked examples in the docs show it substituting a wrong name, wrong
percentage, wrong date, and wrong version number. This is architecturally the opposite of
Agent-Assure's fail-loud stance: it silently repairs the draft rather than flagging it for human
resolution, and Microsoft's docs disclose no accuracy number bounding how often the "correction"
itself introduces a new error. No independent accuracy/precision/recall figures were found; the
docs state only that accuracy "is optimized for English" and is not guaranteed for other
languages. Latency is not published in the pages reviewed.
Verdict: **post-hoc and scope-competitive, but not deterministic, not zero-LLM, and its flagship
differentiator (auto-correction) is a design Agent-Assure's own conventions explicitly reject**
("fail loud, never fallback"; "an empty retained appendix" is required for PASS, not a
model-rewritten one).

**5. AWS Bedrock Guardrails — Contextual grounding check.**
Structurally the most interesting: via `ApplyGuardrail`, **no model is invoked in that API call at
all** — you supply `grounding_source`, `query`, and the content-to-guard as three tagged content
blocks and get back grounding/relevance scores. This means it genuinely can run over an arbitrary
already-written draft with nothing else in the loop for that call, which is the shape a
"redundancy" argument would need. But: (a) the grounding/relevance scores come from an AWS-trained
classifier model, not a rule engine — "deterministic" is never claimed and nothing in the docs
supports it; (b) **AWS publishes literally no accuracy, precision/recall, or benchmark number for
this feature** anywhere found in this search — only qualitative worked examples (e.g., "capital of
Japan" toy cases) and threshold-configuration guidance (0–0.99, common example thresholds 0.5/0.7);
(c) the documented use cases explicitly exclude conversational QA/chatbot ("supported use cases
include summarization, paraphrasing, and question answering... Conversational QA/Chatbot use
cases are not supported"), which is closer to Agent-Assure's typical draft shape than not, but
still a documented scope gap; (d) it evaluates chunk-relevance with an OR semantics bug-shaped
behavior worth flagging: "If any one chunk is deemed relevant, the whole response is considered
relevant" — a single relevant chunk among many irrelevant ones passes the whole response, which is
a coarser granularity than Agent-Assure's per-claim verdict.
Verdict: **the only vendor surface that is simultaneously post-hoc AND callable with zero model
invocation in that call** — but it is an opaque trained classifier with zero published accuracy,
coarser-than-per-claim granularity, and an explicit non-support statement for the
conversational/chatbot use case. It competes on API shape, not on moat mechanism or on any
evidenced accuracy claim.

### Cross-cutting findings for Topic A

1. **No vendor guarantees zero false negatives (Error-B) on fabrication.** Every vendor frames its
   feature as reducing/improving/helping, and none publish a Error-A/Error-B-style breakdown
   (the closest is Vertex's 0–1 support score and Bedrock's 0–1 grounding score, which are
   continuous confidence outputs a caller must threshold themselves — the vendor supplies no
   recommended operating point tied to a published false-negative rate).
2. **Every generation-time feature (Anthropic, OpenAI, Gemini native grounding) is structurally
   incapable of grounding an already-written draft from a separate session** — which is exactly
   Agent-Assure's operating mode (draft written this session, evidence captured this session,
   gate run afterward). This alone rules out three of the five vendors as competitors regardless
   of accuracy.
3. **Of the two/three post-hoc-capable checkers (Vertex Check Grounding, Azure Groundedness,
   Bedrock Contextual Grounding), all three are trained classifiers, none is deterministic, and
   none publishes a validated accuracy number with methodology.** This is the load-bearing gap
   for Agent-Assure's positioning: the moat's differentiator ("pure Python, deterministic, ZERO
   LLM calls during grounding... a verdict is a mechanical fact about the store") has no
   first-party analog surveyed here. A fabricated citation cannot "talk its way" past a
   deterministic span-matcher the way it plausibly could past a black-box classifier scoring
   continuous confidence — none of the vendor docs address adversarial robustness to a fabricated
   but plausible-sounding source at all.
4. **Azure's correction feature is the one vendor capability that actively diverges from
   Agent-Assure's philosophy** (fail-loud vs. silent-repair) and is worth naming explicitly if
   this research is used to argue "why not just use Azure": correction risks papering over a
   fabrication with another unverified rewrite, with no disclosed error rate on the correction
   step itself.

---

## Topic B — Prior art for asymmetric-authority (model may only move toward FAILURE) verification

### Does the exact idea appear under a name?

**No single named term for "a neural/model component may only add flags or move a verdict toward
FAILURE, never toward PASS" was found.** The literature has multiple adjacent, well-established
framings that each capture part of the idea, but none states it exactly as a design rule for
*combining* a deterministic first stage with a model-based second stage where the second stage is
authority-restricted to one direction. The closest exact framing is **"one-sided error"** from
group testing / property testing theory, and **"sound but incomplete"** from formal verification —
both describe a single checker's own error profile, not a two-stage combination rule. The
two-stage combination itself is closest to what appears (unnamed) in the neuro-symbolic
"generate-and-verify" literature and in Amazon's own model-cascade framing (below), but neither
paper states the asymmetric-authority *property* (recall preservation, monotone false-alarm-only
addition) as a theorem — it is implicit in how a "verifier gates a proposer" pipeline is built,
not proven as a general result.

### What each cluster says, and its bearing on the property

**1. Selective prediction / learning to defer / abstention.**
Selective prediction lets a model abstain on inputs where its prediction is likely wrong, trading
coverage for risk (the "risk-coverage curve" framing, [Uncertainty in NLP survey](https://arxiv.org/pdf/2306.04459); ["The Art of Abstention" (ACL 2021)](https://aclanthology.org/2021.acl-long.84/)).
Learning-to-defer (L2D) generalizes this to route uncertain cases to an external expert (human or
stronger model). This is a **single-stage** abstention framing: the model decides *for itself*
whether to answer, not whether to overturn another stage's decision. It establishes the
risk/coverage vocabulary Agent-Assure's own CR error-rate reporting already uses (Error-A/Error-B
functions like a coverage/risk pair), but it is not itself a two-stage asymmetric-authority design.

**2. Conformal prediction for LLM factuality/abstention.**
- **Mohri & Hashimoto, "Language Models with Conformal Factuality Guarantees" (ICML 2024)**
  ([paper](https://proceedings.mlr.press/v235/mohri24a.html), [arXiv:2402.10978](https://arxiv.org/abs/2402.10978)):
  treats correctness as an uncertainty-quantification problem — the model's output is decomposed
  into subclaims, each subclaim's estimated correctness probability is compared to a threshold
  calibrated via split conformal prediction, and only subclaims clearing the threshold are
  retained (a "back-off" that makes the output less specific until it is provably ≥1−α correct
  with high probability, evaluated on FActScore/NaturalQuestions/MATH — reported to retain a
  "substantial portion" of claims while giving 80–90% correctness guarantees).
- **Conformal Abstention** (Abbasi-Yadkori et al., 2024, cited alongside Mohri & Hashimoto in
  later surveys) extends this to whole-response abstention rather than subclaim filtering.
- Relevance to Agent-Assure: conformal methods give a **statistically calibrated, provable**
  coverage guarantee, which is a stronger and differently-shaped claim than Agent-Assure's
  held-out CR-004 rate (n=52, single ratifier, not a conformal guarantee). This is the most
  directly transferable piece of literature if Agent-Assure ever wants a *provable* bound instead
  of an empirically-measured one — but note it calibrates a **single scoring pipeline's**
  threshold, not a two-stage symbolic-then-neural cascade; it does not itself contain the
  asymmetric-authority idea.

**3. Cascades / model routing (FrugalGPT and descendants).**
[FrugalGPT (Chen, Zaharia, Zou, 2023)](https://arxiv.org/abs/2305.05176) routes a query to a cheap
model first; a learned scorer (fine-tuned DistilBERT predicting answer correctness from the
(query, response) pair, per the search summary) decides whether the cheap answer is "good enough";
if not, escalation proceeds to progressively larger/more expensive models. This is a **cost-driven
cascade**, not an accuracy/safety-driven asymmetric-authority cascade: the later stage does not
have restricted authority — it can fully override the earlier stage's answer with its own,
including presumably converting a wrong cheap answer into a "pass" via a different (also
imperfect) expensive model. The direction of authority is symmetric, not one-sided. This is a
structurally different cascade shape than Agent-Assure's design and should not be over-claimed as
prior art for the one-sided property — it is prior art for "staged pipelines with a cheap gate
before an expensive one," which is a related but distinct idea.

**4. Fail-closed / one-sided-error / sound-but-incomplete framings.**
- Formal statement of "one-sided error tester": always accepts objects that truly have the
  property (zero false negatives on the accept side), only rejects with some probability <1
  when the property doesn't hold — from property-testing theory, explicitly named in
  ["Aligning Model Properties via Conformal Risk Control"](https://arxiv.org/pdf/2406.18777) and
  in classical group-testing work (["Optimal Non-Adaptive Group Testing with One-Sided Error
  Guarantees"](https://arxiv.org/pdf/2506.10374)).
- Neuro-symbolic software verification is explicitly described (in a 2606.16886 arXiv summary
  surfaced in this search) as **"always sound but incomplete due to the inherent undecidability of
  the problem"** — soundness meaning it never accepts an invalid artifact, incompleteness meaning
  it may fail to certify a valid one. This maps closely onto Agent-Assure's `PASS`/`NEEDS_WORK`/
  `FAIL` asymmetry: a sound-but-incomplete checker is allowed unlimited Error-A (false alarms /
  under-certification) as the price of guaranteed-zero Error-B (never wrongly certifying).
- **This is the correct formal vocabulary for Agent-Assure's own moat invariant** ("No change may
  reduce Error-A by raising Error-B") — Agent-Assure's rule is a soundness-preservation rule
  stated in engineering terms; the formal-methods literature calls the target property soundness
  and explicitly accepts incompleteness (i.e., Error-A) as the necessary cost. No paper found
  states this as a rule for *adding a second, less-trusted checker on top of a first* — it is
  usually stated about a single checker's own properties.

**5. Neuro-symbolic "generate-and-verify" (Logic-LM and descendants).**
[Logic-LM (Pan et al., EMNLP Findings 2023)](https://arxiv.org/abs/2305.12295) has the LLM
translate a natural-language problem into a symbolic formulation, then a **deterministic symbolic
solver** (Pyke/Prover9/Python-constraint/Z3) performs the actual inference — the LLM proposes, the
solver decides, and a self-refinement loop feeds the solver's error messages back to the LLM to
fix its formulation. Reported gains: 39.2% over LLM-alone prompting, 18.4% over LLM+CoT, across
five reasoning datasets. The general pattern surfaced by this search as **"generate-and-verify"**
— "symbolic reasoning runs first, and the LLM is invoked only on the residue that symbolic methods
cannot close... every candidate, regardless of its origin, is discharged by the verifier before it
is accepted, making the pipeline sound by construction" — is architecturally **the inverse order**
of Agent-Assure's design (Agent-Assure runs the deterministic checker first as the authoritative
gate, and would add a model — the planned T3 NLI tier — *after*, restricted to only add failure
verdicts). Logic-LM's LLM proposes and the solver disposes; no paper in this cluster describes a
model added *after* an authoritative deterministic pass whose only remaining power is to demote a
tentative PASS to FAIL. This is the single most relevant negative finding: **the specific
ordering and authority-restriction Agent-Assure's ADR-004 (planned T3/NLI tier) implies — sound
deterministic gate first, an unsound heuristic layered on top with vote-to-fail-only power — does
not appear to have a named counterpart in the neuro-symbolic verification literature surveyed.**
It is a natural extension of the sound-but-incomplete framing (item 4) applied at the *system*
level rather than the single-checker level, but no source found states or analyzes it as a general
pattern with proven properties (recall-preservation, monotone-false-alarm-only).

**6. Guardrail stacks in practice (NeMo Guardrails, "defense in depth").**
Industrial practice (per the arXiv 2402.01822 "Building Guardrails for LLMs" survey and NVIDIA's
own NeMo Guardrails docs) has converged on a **layered defense-in-depth architecture**: input
moderation → intent routing → structured decoding → output monitoring/self-checking → agent-level
validation → continuous red-teaming. NeMo Guardrails specifically ships a "hallucination rail"
that cross-checks consistency across multiple LLM-generated answers, and separate moderation rails
for harmful content — these are **parallel/sequential filters that each independently block**,
not a system where a later stage is authority-restricted to only tightening (never loosening) an
earlier stage's verdict. The "output guardrails ... might involve content moderation classifiers,
regex scrubbing, schema validators, or calling external APIs to verify the response" framing is
the closest informal industry description of a rules-then-model stack, but again does not encode
the specific one-directional authority rule.

### Summary judgment on Topic B

The exact combination — **deterministic/symbolic check is authoritative for PASS; a model-based
check may only convert a tentative PASS into FAIL, never the reverse** — is a coherent synthesis
of two established but separately-named ideas (sound-but-incomplete / one-sided-error verification,
and neuro-symbolic generate-and-verify cascades), but **no source found in this search states,
names, or proves it as a general pattern**. Its two provable-in-principle properties, if adopted:
(a) it **preserves the recall (Error-B rate) of the first stage exactly** — the second stage
cannot ever create a wrongful PASS, so the system's false-negative rate on violations is bounded
above by the first stage's alone; (b) it **can only increase the false-alarm rate (Error-A)** —
every additional FAIL the second stage produces beyond the first stage's own FAILs is, by
construction, a case the first stage would have passed, so system-wide Error-A is monotonically
non-decreasing in whatever the second stage adds. Both properties follow directly from the
definition (a one-directional veto can't undo a veto-free path, so it can't reduce Error-B; it can
only add to the direction it's allowed to move) and match the sound-but-incomplete framing in item
4 applied recursively — but this is original synthesis for this document, not a citation to a
named theorem. If ADR-004's T3/NLI tier is built this way, that reasoning — not "the literature
already proved this" — should be what is written into its own ADR, with the two properties stated
as claims to be tested against the calibration corpus rather than assumed from prior art.

---

## Source list

**Topic A**
- [Introducing Citations on the Anthropic API](https://claude.com/blog/introducing-citations-api)
- [Anthropic Citations docs](https://platform.claude.com/docs/en/build-with-claude/citations)
- [OpenAI — Web search guide](https://developers.openai.com/api/docs/guides/tools-web-search)
- [OpenAI — File search guide](https://developers.openai.com/api/docs/guides/tools-file-search)
- [OpenAI — Graders](https://developers.openai.com/api/docs/guides/graders)
- [OpenAI — Introducing Model Spec Evals](https://alignment.openai.com/model-spec-evals/)
- [Google Cloud — Check grounding with RAG](https://docs.cloud.google.com/generative-ai-app-builder/docs/check-grounding)
- [Google Cloud — GroundingMetadata reference](https://cloud.google.com/vertex-ai/generative-ai/docs/reference/rest/v1beta1/GroundingMetadata)
- [Google AI — Grounding with Google Search](https://ai.google.dev/gemini-api/docs/google-search)
- [Microsoft Learn — Groundedness detection concepts](https://learn.microsoft.com/en-us/azure/ai-services/content-safety/concepts/groundedness)
- [Microsoft — Correction capability announcement](https://techcommunity.microsoft.com/blog/azure-ai-foundry-blog/correction-capability-helps-revise-ungrounded-content-and-hallucinations/4253281)
- [AWS — Contextual grounding check](https://docs.aws.amazon.com/bedrock/latest/userguide/guardrails-contextual-grounding-check.html)
- [AWS CDK — ContextualGroundingFilterType](https://docs.aws.amazon.com/cdk/api/v2/docs/@aws-cdk_aws-bedrock-alpha.ContextualGroundingFilterType.html)

**Topic B**
- [Mohri & Hashimoto — Language Models with Conformal Factuality Guarantees (ICML 2024)](https://proceedings.mlr.press/v235/mohri24a.html) / [arXiv:2402.10978](https://arxiv.org/abs/2402.10978)
- ["The Art of Abstention: Selective Prediction and Error Regularization for NLP" (ACL 2021)](https://aclanthology.org/2021.acl-long.84/)
- [Uncertainty in Natural Language Processing: Sources, Quantification, and Applications (survey)](https://arxiv.org/pdf/2306.04459)
- [FrugalGPT (Chen, Zaharia, Zou, 2023)](https://arxiv.org/abs/2305.05176)
- [Aligning Model Properties via Conformal Risk Control](https://arxiv.org/pdf/2406.18777)
- [Optimal Non-Adaptive Group Testing with One-Sided Error Guarantees](https://arxiv.org/pdf/2506.10374)
- [Neuro-Symbolic Software Verification: Hyper-charging Local Language Models with Symbolic Reasoning at Scale](https://arxiv.org/html/2606.16886v1)
- [Neuro-Symbolic Verification of LLM Outputs for Data-Sensitive Domains (extended preprint)](https://arxiv.org/html/2605.26942)
- [Logic-LM: Empowering Large Language Models with Symbolic Solvers for Faithful Logical Reasoning (EMNLP Findings 2023)](https://arxiv.org/abs/2305.12295)
- [Building Guardrails for Large Language Models (survey)](https://arxiv.org/html/2402.01822v1)
- [NVIDIA-NeMo/Guardrails (GitHub)](https://github.com/NVIDIA-NeMo/Guardrails)

## Load-bearing assumption

This document treats "no published accuracy number found" as equivalent to "no independently
verifiable guarantee exists." That's a search-completeness assumption, not a certainty — a vendor
could have published a benchmark in a venue this search pass didn't surface (e.g., a re:Invent or
Google I/O talk, an internal whitepaper behind a support-tier gate, or a number that has since been
added to docs after this date). If a specific vendor accuracy claim later surfaces, it should be
re-verified against its primary source before being used to argue for or against building
Agent-Assure's own moat.
