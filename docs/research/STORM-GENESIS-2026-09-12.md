# STORM and the Agent-Assure Genesis — Research Note

Author: Claude (Sonnet 5), 2026-09-12. Sources: web (paper, GitHub, follow-ups) for Part 1; local repo files for Part 2. All web claims carry their source; all local claims carry the file and, where useful, the commit.

---

## Part 1 — Stanford STORM

### 1. What STORM does, stage by stage

STORM ("Synthesis of Topic Outlines through Retrieval and Multi-perspective Question Asking") is a **pre-writing** system: it does not write the article directly from a prompt, it does the research and outlining that should precede writing. Pipeline (paper: Shao, Jiang, Kanell, Xu, Khattab, Lam, NAACL 2024, arXiv:2402.14207):

1. **Perspective discovery** — the system surveys tables of contents of related, already-existing Wikipedia articles to extract distinct editorial perspectives on the topic (e.g., a "historian" angle vs. a "policy" angle vs. a "technical" angle).
2. **Simulated conversations** — for each discovered perspective, an LLM role-plays a "Wikipedia writer with that perspective" interviewing an LLM "topic expert." This is multi-turn, not one-shot.
3. **Question asking** — each simulated writer asks perspective-guided questions, refined iteratively as answers come back — this is the "multi-perspective question asking" the acronym names.
4. **Retrieval** — each expert-turn answer is grounded via live internet search (trusted-source filtering, per Wikipedia sourcing norms), not the model's parametric memory.
5. **Outline generation (curation)** — the transcripts of all simulated conversations are distilled into a structured outline, refining a draft outline built from the perspective survey.
6. **Article generation** — the system writes the article section-by-section against the outline, retrieving supporting passages per section (semantic retrieval over the collected sources) and attaching citations as it writes.

STORM produces the **outline + draft**; Co-STORM (below) adds a live human-in-the-loop layer on top of the same research machinery.

### 2. Citation handling and grounding — including the paper's own numbers

STORM does attach citations during generation (source retrieval feeds section writing directly), but the **paper does not claim the gate is verified as correct** — it reports a measured citation quality, obtained by an **LLM judge**, not a deterministic check:

- **Citation Recall: 84.83%**, **Citation Precision: 85.18%** (Table 4). Measured by having **Mistral-7B-Instruct judge whether the cited passage entails the generated sentence** — i.e., STORM's own grounding metric is itself an LLM call, not a mechanical one.
- The paper's own error analysis: the dominant failure mode is **not** "widely discussed factual hallucination" — it is **red herrings**: "improper inferential linking" (the most common category), inaccurate paraphrasing, and citing an irrelevant-but-topically-adjacent source. The paper explicitly separates this from classic hallucination: *"Addressing such verifiability issues is more nuanced, surpassing basic fact-checking."*
- **Source bias transfer**: because retrieval pulls from whatever is dominant on the open internet, the paper reports the generated articles inherit that bias — quoting the authors, articles are *"grounded on information on the Internet which contains some biased or discriminative content on its own,"* and **7 of 10** editor-evaluators in the human study said STORM output reads "emotional" or "unneutral."
- Editors were unanimous that STORM helps the pre-writing stage; roughly 80% found it useful specifically for unfamiliar/new topics.

Net: STORM measures citation support with an LLM judge and reports it as reasonably high (~85%), but by its own account this number does not capture the harder failure class (over-association / red herrings), and it has **no deterministic, model-free check** that a citation actually entails its sentence — grounding assessment there is itself a language model's judgment call, the exact thing Agent-Assure was built to not depend on.

### 3. Authors' own stated weaknesses

In their own words / substance (NAACL 2024 paper, and its abstract framing of the human study):
- Source bias transfer from the open web into generated prose (tone, "emotional/unneutral" per 7/10 editors).
- Over-association / red herrings: shaky inferential links and irrelevant-but-cited content, described as going *"beyond basic fact-checking"* — i.e., admitted as an open, harder-than-anticipated problem, not something the pipeline solves.
- The citation-quality number itself (84.83%/85.18%) is produced by an LLM judge, which the paper does not claim is ground truth.

### 4. What has shipped since — does anything close the verification gap?

- **Co-STORM (EMNLP 2024)**, now merged into the `knowledge-storm` package (live since 2024/09): adds a **human-in-the-loop, multi-expert roundtable** with a moderator surfacing under-explored questions and a live "concept hierarchy" the human can steer — this improves *what gets researched and discussed*, not *whether a citation supports a sentence*. It does not add a deterministic entailment check; verification is still implicit in retrieval quality plus human oversight.
- The wider "AI research report" field (GPT Researcher, Perplexity-style deep research, OpenAI/other deep-research agents) has moved toward two concrete verification patterns as of 2026, per current literature (arXiv 2604.03173, 2605.08583, 2602.23452, industry write-ups):
  - **Citation-existence checking** — does the cited URL/reference resolve at all (catches fully fabricated references; distinguishes "citation hallucination" — a made-up source — from "statement hallucination" — a real source that doesn't say what's claimed).
  - **Entailment/grounding checking** — does the cited passage actually entail the sentence, via either an LLM-judge pass (still model-dependent, same category STORM used) or, in newer benchmarks (CiteAudit, CiteCheck, GhostCite), a retrieval-grounded automatic check. Reported real-world performance is uneven — CiteAudit's benchmark hits 97% on synthetic cases but only 90% on real-world ones, and even a frontier model's entailment F1 drops sharply (96%→33%) off the easy distribution — underscoring that LLM-judged grounding remains unreliable at exactly the tail Agent-Assure targets.
  - No mainstream shipped system found (STORM/Co-STORM included) implements a **model-free, deterministic** span-level grounding check equivalent to Agent-Assure's T1/T2 tiers. Verification in the wild is either "does the URL exist" (cheap, catches fabrication only) or "ask another LLM if it's entailed" (catches more, but is itself unverified and the newest benchmarks show it degrading badly on real text).

**Sources:**
- [Assisting in Writing Wikipedia-like Articles From Scratch with Large Language Models (ACL Anthology, NAACL 2024)](https://aclanthology.org/2024.naacl-long.347/)
- [arXiv:2402.14207 (HTML)](https://arxiv.org/html/2402.14207)
- [stanford-oval/storm (GitHub)](https://github.com/stanford-oval/storm)
- [Co-STORM module, stanford-oval/storm](https://github.com/stanford-oval/storm/blob/main/knowledge_storm/collaborative_storm/modules/co_storm_agents.py)
- [Detecting and Correcting Reference Hallucinations in Commercial LLMs and Deep Research Agents (arXiv 2604.03173)](https://arxiv.org/html/2604.03173v1)
- [Source or It Didn't Happen: A Multi-Agent Framework for Citation Hallucination Detection (arXiv 2605.08583)](https://arxiv.org/pdf/2605.08583)
- [CiteAudit (arXiv 2602.23452)](https://arxiv.org/pdf/2602.23452)
- [CiteCheck (arXiv 2605.27700)](https://arxiv.org/pdf/2605.27700)
- [GPTZero — ICLR 2026 hallucination findings](https://gptzero.me/news/iclr-2026/)

---

## Part 2 — Agent-Assure's genesis vs. what got built

### What the repo's own record says the project set out to build

The design spec named in the sequencing doc — `docs/superpowers/specs/2026-06-20-agent-assure-design.md` — **does not exist anywhere in this repo's git history, working tree, or the sibling `agents-infra` worktree.** It is referenced but was never committed (confirmed via `git log --all --diff-filter=A --name-only` across all branches — zero hits for the filename or path — and `find` across the whole `~/vibe-coding/Agents/` tree). This report therefore relies on the one document that quotes the spec's own framing: `Agent-Assure/docs/PHASE2-SEQUENCING.md` (2026-07-03).

That document is explicit about the original two-part architecture the design spec laid out, and about STORM's exact role in it:

> "**2a Research front-end** | PLAN → PERSPECTIVES (STORM) → GATHER → SYNTHESIZE, feeding the gate"

and, on why the front-end was deprioritized rather than dropped:

> "It is the spec's own **'commodity half'** (§1.1) — valuable for the full 'ask a question → grounded report' product, but the **differentiated** value is the gate, which 2c+2b harden. Worth its ~5M only once the gate it feeds is trustworthy."

So per the spec's own §1.1 (as paraphrased in the sequencing doc, since the spec file itself is unavailable): Agent-Assure was designed as **a full research-and-report product with two halves** — a STORM-shaped "research front-end" (PLAN → PERSPECTIVES → GATHER → SYNTHESIZE, explicitly naming STORM's perspective-discovery step as the model for stage 2) that produces a draft, and a **deterministic verification gate** sitting downstream of it, checking that draft's claims against evidence actually retrieved. The spec itself called the gate the "differentiated" component and the STORM-like front-end the "commodity" component — i.e., even at design time, the authors knew the front-end was replicating something that already existed (STORM/GPT-Researcher-class systems) and that Agent-Assure's actual novelty was the verification layer, not the research pipeline.

`Agent-Assure/README.md` (current) confirms this same self-positioning after the fact:

> "Agent-Assure is the verification-first research member of the `agents-infra` suite... Cite does LLM-based citation *discovery* (does a claim have *a* source somewhere on the web?); Assure does *mechanical* grounding (does every claim trace to a source *actually retrieved this session*, proven without a model?)."

and states plainly what was built vs. deferred:

> "**Phase 1 scope (built):** a `PostToolUse` capture hook... the deterministic grounding engine... **Phase 2 (research front-end, NLI paraphrase tier, calibration, cross-platform) is future work.**"

### Answering the framing question directly

Agent-Assure was **not** conceived as a STORM clone. It was conceived as a two-part product where the STORM-shaped research front-end was the *delivery vehicle* (get a draft with citations) and the actual product idea was the verification layer bolted downstream of that vehicle — a deterministic check that STORM/GPT-Researcher-class systems, per Part 1 above, do not themselves have. The spec self-identified the front-end as "commodity" (replicable, already exists) and the gate as "differentiated" (the moat) at design time, before any of it was built.

### What actually got built (confirmed against the codebase and commit history)

- Phase 1 (complete, per `Agent-Assure/CLAUDE.md`, README, and the commit trail from `d693f1a` through `bce055b`/`680b530`): the deterministic grounding engine (`ground_check.py` — decomposition, classification, T1 verbatim + T2 lexical tiers, numeric/absence/relational checks, score gate), the `PostToolUse` capture hook (`capture_hook.py`/`capture_core.py`), and Claude Code plugin packaging + offline moat demo.
- Four rounds of adversarial red-teaming against the gate (commits and `docs/logbook/2026-07-12-*`, `2026-07-14-*` entries), and a full calibration cycle against a 52-row Sai-ratified gold set (CR-004, current: Error-A=0.320, Error-B=0.000).
- **2a "Research front-end" (the STORM-shaped half) — never built.** `PHASE2-SEQUENCING.md` recommended build order **2c-harness → 2b → 2a → 2d**, explicitly putting the STORM-like piece *last* of the three substantive slices, reasoning that pouring ~5M tokens into more claims feeding an uncalibrated gate would be waste. No later logbook entry, commit, or CLAUDE.md line records 2a ever starting.
- 2b (T3 NLI paraphrase tier) is also still unbuilt — CLAUDE.md calls it "now LOAD-BEARING rather than optional" precisely because Error-A sits at 0.320 (honest paraphrase reads UNGROUNDED) and only T3 can close that gap, but it remains future work.

**Confirmed:** the premise in the task prompt is correct. The repo today is almost entirely the deterministic verification gate plus its calibration corpus (the "differentiated half" the spec named); the STORM-like research front-end that was meant to feed it — the "commodity half" — was deliberately sequenced last on cost/risk grounds and has not been built at all.

### The sharpest original-intent-vs-today gap

The spec set out to ship a full "ask a question → grounded report" product (STORM-shaped front-end + verification gate); what exists today is only the verification gate, calibrated against a corpus of *hand-written* adversarial and gold-labeled drafts rather than against the output of any research pipeline — so Agent-Assure has never yet graded a single claim that its own system produced end-to-end, only claims fed to it by hand.

---

# CORRECTION, 2026-09-13 — the design spec EXISTS

**This report and a commit message both state that
`2026-06-20-agent-assure-design.md` does not exist anywhere on disk or in git
history. That is FALSE.** It is at:

`~/vibe-coding/Agents/Claude/docs/superpowers/specs/2026-06-20-agent-assure-design.md`
— 474 lines, in the **HQ repo**. The path quoted in `PHASE2-SEQUENCING.md` is
relative to HQ, not to this repo. The search covered this repo's tree and git
history, found nothing, and I repeated "does not exist" as fact instead of
"not in this repo". A negative result is only as wide as where you looked.

## What the founding spec actually says — three findings that matter

### 1. The spec's stated identity is PROVENANCE, not entailment

> *Agent-Assure is the first plugin in `agents-infra` to guarantee that every
> claim in a research report can be **mechanically traced to a source that was
> actually retrieved this session** — proven by a deterministic gate, not
> asserted by the model that wrote the claim.* (§1)

**Traced to a source that was actually retrieved.** That is the provenance
product, verbatim, in the founding document's one-sentence identity. The
narrow launch recommended on 2026-09-12 is **not a retreat from the original
vision — it is the original vision.** Entailment (T1/T2/T3) is machinery the
spec introduces in §4.3 as the *means*; traceability is what it promises.

### 2. The spec already ruled on the LLM-pass question, and the diagnostic
now updates its ruling

> *the only learned component is a fail-closed, single-purpose NLI
> classifier — **never a generative "is this well-cited?" judge**.* (§1)

> *T3 is the **only** learned step, and it is an NLI discriminative
> classifier, not a generative judge — a closed yes/no entailment task,
> fixed/versioned/offline/pinned (record `model_sha`), **fail-closed** (below
> threshold → UNGROUNDED, no benefit of doubt). It cannot see the research
> goal — only `(span, claim)`.* (§4.3)

The 2026-09-12 analysis reached the same architecture independently —
asymmetric authority, local classifier over API judge — which is mild evidence
the reasoning is sound rather than novel. **But the spec assumed a fail-closed
NLI tier would WORK.** The diagnostic measured it: on the 17 open attack
classes, HHEM-2.1-Open caught 3, all 3 already caught by the deterministic
gate — **union gain zero**. Its real skill showed up only where it would have
to *lift* a flag, which §4.3's fail-closed rule forbids by design.

So §4.3's T3 is not merely unbuilt. **As specified — fail-closed, no benefit
of the doubt — it is measured to add nothing.** That is new information the
spec could not have had, and it should be recorded against ADR-004.

### 3. The spec's own named #1 risk has never been closed

> *§7.5 The single biggest risk … **The gate is only as truthful as the
> EvidenceStore, and the store is complete only if every retrieval flows
> through an instrumented tool that captures verbatim full text.** … Sub-risk
> (i) [un-hooked retrieval] is the genuinely hard one and is a harness
> guarantee, not a skill-logic guarantee … **Get this wrong and the score is
> theater. This is the top implementation-plan risk to close.***

The capture hook was live-validated once by its author and **has never been
exercised by a stranger** (`RESUME-HERE.md`, demo criterion 4, still ⚠️).

**The spec named the top risk. Two months went to the entailment tier
instead** — the component §4.3 calls "the only learned step" and the
diagnostic now shows contributes nothing as specified. Meanwhile the risk the
spec said turns the whole score into theater is exactly as open as it was on
day one.

**This sharpens the launch recommendation rather than changing it.** Ship
provenance — the spec's own identity — and close §7.5, which is the one thing
that can make provenance itself untrue.
