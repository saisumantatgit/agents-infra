# A. Provenance / traceability demand (research dated 2026-10-03)

Labels: [V] vendor marketing, [I] independent/user, [R] regulator/primary text, [INF] my inference. Every URL was returned by a search/fetch this session; pages were NOT all opened in full (search-snippet-only items are marked "snippet").

## Conclusion
1. BEST-SUPPORTED: Demand for claim/citation-level verification with an audit artifact is real, funded and priced today, concentrated in LEGAL (hallucinated-citation sanctions). At least 8 vendors sell it, per-seat or per-document, with "audit trail / certificate" as a headline feature. [V] (Q4)
2. Deterministic-verdict is used as a SALES differentiator by several vendors (EdgeCite, LexiCite360, Veriprajna, VARI's deterministic channel). Buyer-side REQUIREMENT for it is only indirectly evidenced (reproducibility is a model-validation premise). [V]+[INF] (Q3)
3. The buyer pays to verify that a CITATION EXISTS in an authoritative corpus (CourtListener, ISAP, EUR-Lex), not that a sentence traces to a session-retrieved document. Agent-Assure's "session evidence store" framing has no located buyer vocabulary. [INF]
4. Regulatory forcing functions exist (EU AI Act Art.12, ABA Op.512, SR 11-7, FINRA 24-09) but none I found mandates claim-to-source traceability of generated text; they mandate logging, verification-by-human, or validation. [R] (Q2)
5. WEAKEST: that SR 11-7 / auditors REQUIRE non-LLM verification. I found commentary asserting it, no primary text saying it. UNVERIFIED as a requirement.

## Q1. Words buyers use
- "Citation verification / cite-check" for AI briefs: strongest, many vendors (see Q4). Sanctions database: Charlotin AI Hallucination Cases; counts quoted by secondary sites conflict (2,046 as of 2026-09-21 per haqq.ai; 1,353 per another) so treat as "1,000+, rising" https://www.haqq.ai/blog/ai-legal-hallucination-audit , https://gc.ai/blog/ai-hallucination-legal-cases [V, secondary, 2026]
- "AI output traceability for compliance audits" / "audit trail": r/mlops thread 2026-08-12 [I]. Terms "provenance and lineage", "traceability from source to report" appear in job posts (OKX Internal Audit, 2026-07-22; Wise, 2026-09-23) [V-employer].
- "Groundedness/grounding": appears in bank AI-risk job spec (UOB, undated: "evaluation harnesses for truthfulness, grounding... hallucinations") https://www.efinancialcareers.sg/jobs-Singapore-Singapore-First_VP_Group_Risk_Management_AI__Data_Risk_Governance__Control_-_Advanced_AI_Risk_Specialist.id24070762 [V-employer, undated]
- "Evidence chain", "verification certificate/protocol" used by legal vendors (LEGAION, VARI).
- Search VOLUME: NOT MEASURED (no keyword-tool access). Not located.

## Q2. Who buys / what forces it
| Segment | Instrument | Forces | Fit [INF] |
|---|---|---|---|
| Law firms/litigators | ABA Formal Op. 512 (2024-07-29): lawyers must review/cross-check AI output, MR 1.1, 3.3 https://natlawreview.com/article/american-bar-association-issues-formal-opinion-use-generative-ai-tools ; court sanctions + standing orders | Rule 11-type sanctions, license risk | HIGH but needs case-law DB checks, which Assure lacks |
| Banks | SR 11-7 (Fed/OCC 2011) validation independent + reproducible https://www.federalreserve.gov/supervisionreg/srletters/sr1107.htm (not opened) | Examiners | MEDIUM; LLM in scope by use case https://www.sphereinc.com/blog (2026-09-03) [V] |
| Broker-dealers | FINRA Reg Notice 24-09 (2024-06-27), SEC 17a-4: no new rules, existing supervision/recordkeeping apply (Mayer Brown, Debevoise summaries) [snippet] | Exams | LOW-MEDIUM: records of AI comms, not claim verification |
| EU high-risk AI | AI Act Art.12 logging, Art.13 transparency https://ai-act-service-desk.ec.europa.eu/en/ai-act/article-12 [R] | Provider/deployer duty | Art.12 logs system EVENTS, not sentence-level provenance; weak match |
| Pharma/MLR | FDA CSA final guidance (2025-09-24 per one secondary); human approval required for promo material [V snippets] | GxP validation | MEDIUM; no tool-specific citation requirement found |
| Internal audit | ISA 500 revised effective periods from 2026-12-15 recognises automated tools (snippet, unverified at source) | Audit evidence | LOW-MEDIUM |
Not located: SEC/FDA/EMA text requiring per-claim source traceability; ISO 42001 clause; SOC 2 criterion.

## Q3. Is determinism valued? (most important)
Evidence FOR (all weak-to-moderate):
- EdgeCite: "Deterministic — not another model's opinion"; deterministic validation "before any AI inference" https://edgelex.com/platform/edgecite [V]
- LexiCite360: "byte-for-byte matching... not a confidence interval" https://www.lexicite360.com/ [V]
- Veriprajna CiteGuard: existence check and gate are "pure Python"; LLM support-check abstains, "the gate, not the model, decides" https://veriprajna.com/demos/legal-ai-citation-verification [V, demo not deployed]
- VARI: deterministic CourtListener auditor, "hard failures override LLM opinions" https://getvari.ai/legal.html [V]. Note VARI also sells LLM cross-vendor adversaries: market is HYBRID, not pure non-LLM.
- Tetrate (2026-01-13): "You can't validate what you can't reproduce... non-deterministic breaks" validation; claims SR 11-7 requires reproducible behaviour https://tetrate.io/blog/the-tier-3-problem [V; paraphrase of guidance, not guidance text]
- Search-surfaced arXiv items on deterministic verifiers for audit (e.g. 2609.12156, snippet only, not read) [academic, UNVERIFIED]
Evidence AGAINST/absent: no RFP, audit standard or regulator text found requiring a non-LLM verifier. Vendors that pair deterministic checks with LLM support-checks still sell. LLM-as-judge is described as accepted alongside human review in banks (search summary, snippet).
Verdict: determinism is a credible VALUE PROPOSITION (reproducibility = precondition of independent validation) but NOT located as an explicit buyer REQUIREMENT. [INF]

## Q4. Willingness to pay and shape (public pricing, all [V])
- LEGAION Verifier $67/seat/mo (100 verifications), Platform $419/seat/mo; includes "Evidence Chain", "immutable audit" https://www.legaion.com/en/pricing?plan=verifier
- Ascero AI: $79/mo unlimited or $29/doc; cites Lexis+ AI $150+/mo as comparator https://asceroai.com/legal/citation-verifier
- CiteShield: per-document, no price seen https://citeshield.com/ ; OWL: per-brief, quote on request https://owl-ai-agency.com/ ; EdgeCite, VARI: enterprise/contact.
- Shape: standalone per-doc/per-seat tools for small firms; embedded feature for large platforms (EdgeCite inside DMS/Word). Services: Veriprajna sells design engagement for the certificate. Market sizes (AI governance ~$492M spend 2026, Gartner) are category-wide, not this niche https://www.gartner.com/en/newsroom/press-releases/2026-02-17-gartner-global-ai-regulations-fuel-billion-dollar-market-for-ai-governance-platforms [snippet].
- Signal [INF]: price points of $29-$419 imply a crowded, price-compressed legal niche; WTP for session-evidence provenance outside law NOT located.

## Q5. Unmet need
- r/mlops 2026-08-12 [I, 5 comments]: auditor-facing traceability; commenters say teams "stitch together screenshots and timestamps" or dump to warehouse and build own audit views. This is trace/logging, not claim-level provenance. https://www.reddit.com/r/mlops/comments/1vmmj98/
- r/LLMDevs 2026-09-03 [I]: builder rejects uncited claims "through deterministic validation" for repo-scan findings https://www.reddit.com/r/LLMDevs/comments/1vperza/
- Job posts requiring "traceability from source to report", "immutable audit trails" (OKX Internal Audit 2026-07-22; LIST Luxembourg RAG for NAV controls "traceable, auditable, defensible", undated) [V-employer].
- No post saying "nothing does this" found.

## WHAT I SEARCHED AND DID NOT FIND
Queries: SR 11-7 LLM reproducibility/LLM-as-judge; EU AI Act Art.12/13; hallucinated citation sanctions; FDA GxP/CSA/MLR citation traceability; citation verification pricing/deterministic (Exa); auditor reperformance/ISA 500 AI; ABA 512; FINRA 24-09/17a-4; Reddit/HN traceability need (Exa); job posts audit trail/source attribution (Exa); "deterministic not an LLM" auditors; SR 11-7 text replicate; market size.
NOT_LOCATED_UNDER those: (a) primary text requiring non-LLM verification; (b) any pharma/insurance/government/publisher buyer of claim-level traceability; (c) keyword volume; (d) RFPs; (e) ISO 42001/SOC 2 clauses; (f) any buyer of evidence-store-of-session-retrievals (the capture-hook model). Kinds covered: label, plain noun, artifact (regulation number/vendor/job phrase), so absence verdicts here are "not found by these", not "absent".

## IF I WERE WRONG
Strongest counter-evidence: the paying market verifies existence against authoritative external corpora and increasingly bundles LLM support-checks (VARI, Veriprajna, CiteShield "confirm case says what you claim"), because buyers want "is it TRUE", which Assure explicitly does not answer. Per-doc prices of $29 and free tiers (OWL, LexiCite360) suggest low WTP. Regulators located require logging/human review, not provenance. Load-bearing assumption: that a session-captured-source gate is a distinct need from corpus-based cite-checking; I found no buyer stating it.
