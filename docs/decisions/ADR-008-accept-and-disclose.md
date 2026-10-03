# ADR-008 — Ship provenance, accept and disclose the agreement gap

**Status:** Accepted · **Date:** 2026-10-03 · **Decider:** Sai
**Supersedes:** nothing. **Related:** ADR-005 (hard cap), ADR-006 (T2 demotion),
ADR-007 (relational demotion), J-69/J-70/J-62+J-71 (open, Sai, Escalation #1)

## Context

Round 14 (2026-10-02) demonstrated that the gate certifies claims their own cited
source **denies**. T1 anchors its ≥8-token span at the claim's first content
word, so a long-subject claim matches a span inside its own subject; the
predicate is then checked only by set-membership coverage, and `_span_is_hedged`
inspects only the five tokens *before* the span. Measured: the same denial moved
*before* the subject refuses the claim (FAIL 0.0); left *after* it, the claim
certifies (**PASS 100.0**). It reproduces on plain `FACTUAL` with no causal
vocabulary, so the relational demotion (ADR-007) does not cover it.

This is not an exotic attack. *"We found no evidence that X"* is the ordinary way
a real source reports a negative finding, so the shape arises from **honest
retrieval**, with no adversarial control of the source.

Two repairs were priced and both were rejected as the default:

| Candidate | Closes | Error-A | Error-B | Honest drafts |
|---|---|---|---|---|
| Baseline (shipped) | — | **0.400** | **0.000** | 7 pass / 3 xfail |
| Whole-source hedge scan | R14-01, R14-04 | 0.560 | 0.000 | **5 FAIL / 2 pass** |

The blunt repair **breaks a verbatim quotation of the cited source** — the defect
`tests/honest_drafts/` was built to catch (OI-T2-01). It was recommended, then
withdrawn the same night.

## Decision

**Ship the provenance claim. Accept the agreement gap and disclose it IN THE
PRODUCT.** Three parts:

1. **Every report states its own scope** (J-73). Not a README footnote — a field
   on the report and a line on the human CLI path, printed on every verdict.
   Two variants, because the gate may not claim session scope unless
   `--session-id` was passed (J-56).
2. **The contradiction signal ships as a MEASUREMENT, never a verdict** (J-74):
   a deterministic diagnostic, AST-guarded against every verdict path.
3. **The claim is REFUSAL, not determinism** (J-75). Never "verified" or
   "grounded" unqualified.

## Rationale, with the evidence

- **A contradiction VERDICT is indefensible at the current state of the art.**
  MiniCheck-FT5 74.7 and GPT-4 75.3 on LLM-AggreFact (EMNLP 2024); HHEM-2.1-Open
  64.4 / 74.3 on RAGTruth. Godbole & Jia (arXiv 2501.14883) find SOTA evaluators
  disagree per instance and specifically miss close paraphrases. **At ~70% a
  verdict is a coin-flip wearing a gate's clothes**, and gating on it would
  manufacture Error-A at scale while still missing cases.
- **Deterministic span tracing is a genuine gap.** Langfuse's only citation
  evaluator checks that an answer cites *at least one* retrieved source. The
  platforms score faithfulness with an LLM judge or a small model. The only
  competitors that hard-refuse are three repos created Jan–Aug 2026 with 0–14
  stars.
- **A disclosure outside the product does not work.** Ding et al. (AAAI 2025):
  trust RISES with citations **even when the citations are random**, and falls
  only when users check them. Magesh et al. (Stanford, JELS) quotes a vendor's
  "100% hallucination-free" claim beside a measured 17–33% hallucination rate.
- **The law supports a narrow claim.** *Whiting v. City of Athens* (6th Cir.,
  2026-03-13) sanctioned two attorneys $15,000 each and held that **verification
  cannot be delegated** and every citation must be personally read. A tool that
  refuses to certify agreement is behaving as the court expects.
- **Determinism is contested; refusal is not.** Clearbrief states its
  cite-checking is "not generative AI" — but its patent AU2022223275A1 describes
  vectors, a learned relevancy score 0–1 and a threshold, so "not generative"
  does not mean reproducible. **No commercial product hard-refuses what it
  cannot trace.** That is the defensible claim.

## Consequences

- **Error-A stays 0.400** and the gate keeps refusing honest paraphrase. That
  cost is now explicit in the product rather than discovered by a user.
- **J-70 remains OPEN and is Sai's.** Promoting the diagnostic to a verdict later
  is a documented threshold change, not a breaking upgrade — which matters,
  because an upgrade that turns a passing CI red gets the gate switched off, and
  **a gate that is switched off has unbounded Error-B.**
- **The diagnostic yields a number nobody currently has:** how often real drafts
  cite a source that contradicts them.

## The load-bearing assumption, stated so it can be attacked

**That buyers read PASS as "traceable" and not as "supported".** Nothing in the
2026-10-03 research tests this — no buyer interviews, no analyst sizing, no named
purchase. **Five buyer interviews would settle it**, and if they came back the
other way, the footer is insufficient and J-70 becomes a pre-ship item.

## Alternatives rejected

- **Fix J-70 before shipping.** Rejected on sequencing, not merit: the structural
  repair needs sentence-scoped source text, which `_span_is_hedged` cannot have
  (`_tokenize` strips punctuation), so it is a signature change across three
  call sites plus its own adversarial round.
- **Extend `_RELATIONAL_RE`** (J-69). Rejected as the wrong layer: R14-04
  reproduces with no causal word, so a lexicon closes 22 fixtures and leaves the
  class open — the pattern that lost five rounds to the comment stripper.
- **Say nothing and ship.** Rejected: that is the Magesh outcome.

## Basis

`docs/research/market-2026-10-03/SYNTHESIS.md` (five strands, saved with their
queries and counter-evidence) · `Agent-Assure/reports/RED-TEAM-R14-2026-10-02.md`
· `docs/logbook/2026-10-02D-the-refusal-that-one-word-walked-around.md`
