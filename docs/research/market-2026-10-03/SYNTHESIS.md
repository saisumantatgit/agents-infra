# SYNTHESIS — Where is the utility, and how should Agent-Assure ship?

**Commissioned:** 2026-10-03 by Sai, to decide whether "accept-and-disclose" is
safe and whether J-70 (contradiction detection) is a pre-ship item or a later
upgrade. Five parallel strands (A…E), each saved in this directory with its own
queries, sources and "IF I WERE WRONG" section.

**ANSWER: ship provenance, accept-and-disclose — with three changes to the plan.**
Sai's lean is supported. It is not supported for the reason he expected.

---

## 1. The decision, and what the evidence actually says

| Question | Answer | Strength |
|---|---|---|
| Where is the utility? | **Provenance.** Contradiction is crowded, funded, and its state of the art is too weak to gate on. | STRONG |
| Is "accept and disclose" defensible? | **Yes — but not as a README footnote.** The limit must sit inside the claim and print on every PASS. | MODERATE (~65%) |
| Is J-70 pre-ship? | **No.** Ship it as a NON-BLOCKING DIAGNOSTIC in v1, promote later if ever. | STRONG |
| Is determinism the differentiator? | **Partly. Reframe it.** "Not generative" is taken; **"refuses what it cannot trace"** is not. | STRONG |
| Which segment? | **AI agent/research pipelines, NOT legal.** | MODERATE |

## 2. Why NOT contradiction (strand B, strand C)

- **The state of the art is 65–75% balanced accuracy.** MiniCheck-FT5 74.7, GPT-4
  75.3 on LLM-AggreFact (EMNLP 2024); HHEM-2.1-Open 64.4 / 74.3 on RAGTruth.
  Godbole & Jia (arXiv 2501.14883, Jan 2025): SOTA evaluators disagree per
  instance and specifically miss unsupported claims that paraphrase closely.
  **At ~70% you cannot gate a release.** Our missing check is a smaller gap than
  it looked — and anyone who gates on it is shipping a coin-flip as a verdict.
- **It is a free feature of funded platforms.** Ragas/TruLens free; Braintrust,
  Galileo, Arize, Patronus ship it; Bedrock ~$0.10/1k text units. Arize $70M
  Series C, Braintrust $80M Series B at ~$800M, Galileo acquired by Cisco.
  Humanloop, Context.ai, Guardrails (→Harvey, 2026-09-09) and Galileo all
  absorbed inside ~18 months. **Competing here means competing with free, funded
  and consolidating.** (Funding figures are from search summaries, not primary
  pages — treat as indicative.)
- **No checker runs without a model.** Local pinned models (HHEM, MiniCheck,
  DeBERTa) are repeatable but probabilistic.

## 3. Why provenance IS the gap (strand C)

- **The platforms do not do deterministic span tracing.** They score faithfulness
  with an LLM judge or a small model. **Langfuse's only citation evaluator checks
  that the answer cites at least one retrieved source** — that is the state of
  built-in citation checking in a major observability tool.
- **Competition is nascent, not absent.** CiteGuard, verbatim-citation-gate,
  VeriQuote, DeepCitation, sourcecheck — all created Jan–Aug 2026, **0–14 stars**.
  Someone else noticed the same gap this year. Nobody has won it.
- **Nobody commercial hard-refuses.** Scores and soft tiers are the norm
  (BriefCatch RealityCheck is Green/Yellow/Red). Only three OSS repos refuse.
  **That is the positioning axis, and its price is recall — our Error-A.**

## 4. The determinism claim, corrected twice

My first statement ("nobody does deterministic verification") was **wrong**:
Clearbrief explicitly says its cite-checking is **"not generative AI"**, is
Word-embedded, claims 7 patents, and names AmLaw 10, Microsoft, LexisNexis,
Fastcase vLex, Perkins Coie.

The correction then went the other way. **Clearbrief's patent AU2022223275A1
describes assertions and sources as vectors, a learned relevancy score 0–1, a
threshold (example 0.5), and a model trained on user approve/reject feedback.**
So "not generative" does NOT mean reproducible. It is a learned scorer with a
cut-off. (Patent→shipped-product link is INFERRED; Clearbrief's own pages do not
state the mechanism.)

**Net: do not claim "deterministic" or "non-generative" as the differentiator —
one is contested and the other is taken. Claim the behaviour:** *a reproducible
verdict that refuses what it cannot trace, with no model in the verdict path.*

## 5. The size of the problem we actually solve

| Source | Measure |
|---|---|
| STORM's own paper | 84.83% citation recall / 85.18% precision → **~15% of sentences unsupported** |
| Liu et al. 2023 (human auditors) | **51.5%** of sentences fully supported |
| DeepTRACE (Sep 2025) | unsupported statements **12.5%** (GPT-5 DR) → **97.5%** (Perplexity DR) |
| DeepResearch Bench (Jun 2025) | citation accuracy 78–90% |
| Magesh et al. (Stanford, JELS) | Lexis+ AI and Westlaw hallucinate **17–33%** |

**The caveat that matters: every benchmark rate above is an LLM-judged SEMANTIC
support measure.** They quantify *"does the source agree"* — J-70, our gap — not
*"is the claim traceable"*, which is what T1 catches.

**Reconciliation (orchestrator's, not any agent's).** Real sanctions split the
other way: Charlotin's database lists **894 "Misrepresented" of 2,125 cases**, so
roughly **1,231 (~58%) are fabricated or nonexistent** — squarely traceability.
So benchmarks measure the agreement half; courts punish the fabrication half more
often. **Agent-Assure catches the larger real-world half deterministically and
refuses to opine on the other.** Treat 58/42 as an interpretation of a case
database, not a measurement — a case may fall in both buckets.

## 6. The expectation risk, and the exact wording (strand D)

**Disclosure is NOT enough as a footnote.** Evidence:
- **Ding et al., AAAI 2025:** trust rises with citations **even when the citations
  are random**, and falls only when users check them. A PASS buys unearned trust.
- **Verma (Bloomberg), arXiv 2608.12571:** models accept citations on *topical
  overlap*, catching only **37–61%** of wrong-pinpoint errors — our failure mode,
  measured in someone else's product.
- **Magesh et al.** exists to rebut "hallucination-free" marketing. That is the
  fate of an unqualified claim.
- **Whiting v. City of Athens** (6th Cir., 2026-03-13): $15,000 each against two
  attorneys, plus fees across three appeals, double costs, disciplinary referral;
  **verification cannot be delegated and every citation must be personally read.**
  This HELPS a narrow claim: a tool that refuses to certify agreement is behaving
  as the court expects, not deficiently.

**Adopt this as the PASS-report footer, verbatim:**

> PASS means every claim in this draft is traceable to text in a source retrieved
> this session; it does not mean the source agrees with the claim, and a source
> that denies or hedges a claim can still satisfy this check.

**Never use "verified" or "grounded" unqualified.** Precedents for a loudly narrow
claim: Semgrep ("No soundness guarantees"), TypeScript's soundness non-goal,
seL4's enumerated proof statements with stated assumptions.

## 7. The three changes to the plan

1. **The limitation goes INSIDE the claim and prints on every PASS report** — not
   in a README. (Strand D; this is the one change that makes accept-and-disclose
   defensible rather than merely legal.)
2. **Ship J-70 as a non-blocking DIAGNOSTIC in v1.** Not a verdict. Rationale now
   doubly supported: at ~70% SOTA accuracy a verdict is indefensible anyway, AND
   promoting a diagnostic later is a documented threshold change rather than a
   breaking upgrade that turns passing CI red and gets the gate switched off.
   Same pattern as the T2 demotion and ADR-007: ship the measurement, withhold
   the verdict. It also yields the one number nobody has — how often real drafts
   cite a source that contradicts them.
3. **Position on refusal, not determinism. Beachhead is AI agent/research
   pipelines, not legal.** Legal has an entrenched, patented, Word-distributed
   incumbent and a buyer who wants "is it TRUE". STORM-class tools are a
   complement: they produce cited drafts and verify nothing.

## 8. Integration, with one blocking unknown

STORM is the cleanest target — it writes `storm_gen_article.txt`,
`url_to_info.json` and `raw_search_results.json` to disk. **But its repo last
pushed 2025-09-30 (~1 year stale).** The Anthropic Citations API is the live
alternative, though it guarantees pointers only for documents sent through it.
Closed vendors retrieve server-side, so the hook never sees what the model saw —
unreachable by design.

**BLOCKING UNKNOWN, registered not assumed:** whether STORM's stored `snippets`
are **verbatim page text**. The agent read the code but never ran STORM. If those
snippets are model-processed, Agent-Assure tags them `haiku_summary` and
**refuses every claim** — the integration fails closed on 100% of input. A
~30-minute empirical check settles it and must precede any integration work.

## 9. What this research does NOT establish — read before acting

- **No buyer interviews. No analyst sizing. No named purchase.** Every segment
  and purchase-trigger claim in strand A is INFERRED.
- **Strand A is unreliable on landscape and pricing.** It listed eight obscure
  legal vendors with precise prices and **missed Clearbrief, the category
  leader, entirely.** LEGAION is real (per-seat Word add-in + "Verifier") but its
  $67/$419 prices were NOT on the page fetched and are not repeated here.
- **No regulatory instrument mandates per-claim provenance.** ABA Op. 512, SR
  11-7, FINRA RN 24-09 and EU AI Act Art.12 were located; Art.12 logs system
  events, not sentence-level provenance. The "regulation requires a non-LLM
  verifier" line is **NOT_LOCATED** as a buyer requirement — it is a vendor
  talking point.
- **Funding, acquisition and price rows come from search summaries**, not primary
  pages. Each platform's docs were read only one or two pages deep, so a built-in
  span-attribution feature could exist on a page nobody read.
- **Exa hit its free rate limit** mid-run in two strands; most searching fell back
  to WebSearch/WebFetch. Coverage is therefore shallower than commissioned.
- **THE LOAD-BEARING ASSUMPTION, untested:** that buyers read PASS as *"claims are
  supported"* rather than *"claims are traceable"*. **Five buyer interviews would
  settle it**, and nothing in this research substitutes for them.

## 10. What would change the recommendation

- If five buyer interviews showed buyers read PASS as "supported" even with the
  footer printed → the footer is insufficient and J-70 becomes pre-ship.
- If a major platform shipped free deterministic span attribution → the gap closes
  and the product becomes a feature.
- If the beachhead turned out to be legal after all → Clearbrief's patent position
  and Word distribution make it a bad fight, and the answer is to integrate
  rather than compete.
