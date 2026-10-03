# D — Expectation risk: is "accept and disclose" the traceability-not-agreement gap defensible?

Date: 2026-10-03. Researcher: subagent (Sonnet 5.5). Tools: WebSearch (extended), Exa search/fetch, WebFetch.
Labels: MEASURED = a cited study/primary page reports it; INFERRED = my reasoning; VENDOR = marketing; INDEP = independent/academic/court.

## CONCLUSION

**Is disclosure enough? NO as a README footnote; YES-WITH-CONDITIONS if the limit is written into the claim itself and into every PASS output.**
Confidence: moderate (~65%). The conditional YES rests on INFERRED reasoning, not on any measured test of a disclosure changing behaviour (none located).

What drives it:
1. MEASURED: users trust the *presence* of a citation and rarely open it (Ding et al., AAAI 2025). A PASS is a stronger version of a citation. A disclosure that lives only in docs will not be read at the moment of reliance.
2. MEASURED: the exact failure (real source, proposition unsupported) is the one courts sanction ("misrepresented" = 894 of 2,125 cases in Charlotin's database, 2026-10-02) and the one existing checkers are documented to miss.
3. MEASURED: vendors who used absolute words ("100% hallucination-free linked citations") were publicly rebutted in a peer-reviewed study that named the quotes. The reputational damage came from the word, not from the limitation existing.
4. MEASURED: the narrow-claim precedents (Semgrep, TypeScript, seL4) succeeded by stating the limit *inside the product's own claim*, not beside it.
5. INFERRED: your gap is worse than the typical "known limitation", because the word PASS on a draft that asserts X while the source says "no evidence of X" is a *false assurance on the very axis a buyer assumes*. Hence the verdict word and output must carry the scope.

Load-bearing assumption: that buyers read PASS as "claims are supported", not "claims are traceable". I found no direct measurement of how buyers read a *deterministic traceability* verdict specifically. Everything on reading behaviour is from adjacent artefacts (citations, badges).

## Q1. What comparable tools PROMISE vs DELIVER

VENDOR marketing (quoted via the Stanford paper, which is the primary compilation; originals not re-fetched):
- LexisNexis: "Lexis+ AI delivers 100% hallucination-free linked legal citations connected to source documents, grounding those responses in authoritative resources that can be relied upon with confidence." (Wellen 2024a). Later: "our promise is not perfection, but that all linked legal citations are hallucination-free" (LexisNexis 2024).
- Casetext: "CoCounsel does not make up facts, or 'hallucinate'..."; Thomson Reuters: "We avoid [hallucinations] by relying on the trusted content within Westlaw and building in checks and balances that ensure our answers are grounded in good law"; TR exec: RAG "dramatically reduces hallucinations to nearly zero" (Ambrogi 2024).
  Source: https://arxiv.org/html/2405.20362v1 (Magesh et al.; also J. Empirical Legal Studies 2025, https://onlinelibrary.wiley.com/doi/full/10.1111/jels.12413). Fetched 2026-10-03.
- AWS Bedrock Guardrails contextual grounding: "Filters over 75% hallucinated responses for RAG and summarization workloads" (AWS News Blog, 2024-07-10, https://aws.amazon.com/blogs/aws/guardrails-for-amazon-bedrock-can-now-detect-hallucinations-and-safeguard-apps-built-using-custom-or-third-party-fms). Note: a quantified, bounded claim. Good model.
- Azure groundedness docs: "Groundedness detection ... helps you ensure that large language model (LLM) responses are based on your provided source material"; use-case text says the function helps "guaranteeing that readers obtain accurate and reliable medical information". https://learn.microsoft.com/en-us/azure/ai-services/content-safety/concepts/groundedness (fetched 2026-10-03). The doc's worked examples are all numeric/entity swaps (Jane/Kevin, 4.5%/5%, 1065/1066), i.e. the easy cases.
- Legal cite-checkers: CiteCheck AI is explicit about scope ("does not check non-case citations", existence lookup via CourtListener) https://www.lawnext.com/2025/06/lawdroid-launches-citecheck-ai-a-fail-safe-against-ai-citation-hallucinations.html (2025-06); but CEO line: "lawyers now have no excuses for citing hallucinated cases." Cite Sentinel "flags case law and statutes that might not exist"; Clearbrief founder: "not possible to get generative AI hallucinations down to 0%". https://valawyersweekly.com/2026/09/17/ai-hallucinations-legal-filings-citation-verification-tools/ (2026-09-17).

INDEP delivery evidence:
- Magesh et al.: Lexis+ AI and Westlaw tools "hallucinate between 17% and 33% of the time"; "the providers' claims are overstated." Their hallucination definition includes "a false assertion that a source supports a proposition", i.e. the misgrounded class. (same URL)
- Liu/Zhang/Liang, EMNLP Findings 2023: across Bing Chat, NeevaAI, perplexity.ai, YouChat "a mere 51.5% of generated sentences are fully supported by citations and only 74.5% of citations support their associated sentence". https://aclanthology.org/2023.findings-emnlp.467/
- Seo et al. 2026 ("Verified Misguidance", arXiv 2605.28565): of 761,495 citation pairs, "30.6% of citations distort their sources"; they name the pattern: models "cite real, accessible sources yet fail". LLM-judge-based, single judge (gpt-4o-mini) = a caveat. https://arxiv.org/pdf/2605.28565
- Verma (Bloomberg), "Is this Citation on Point?" arXiv 2608.12571: models catch 93-100% of wrong-case corruptions but "37-61%" of wrong-pinpoint ones; failures accept "based on topical overlap rather than page-level support". Directly analogous to presence-without-agreement. https://arxiv.org/pdf/2608.12571
- Shelf.io blog (2024-05-29): Azure Groundedness recall 0.352 on 250 permuted-answer hallucinations (88/250 detected). Practitioner blog, one dataset (SQuAD-derived), not a negated-source test. https://shelf.io/blog/limitations-of-azure-groundedness-service-in-detecting-hallucinations/

NOT_LOCATED: a published test where a tool returned "verified/grounded" on a source that negated or hedged the claim ("no evidence that X" vs "X"), with the tool named. Queries: (a) "groundedness tool contradiction missed negation", (b) "AI fact-checking supported when source said no evidence NLI", (c) "lexical overlap citation check fails contradiction". Closest: arXiv 2605.26663 / 2210.13865 surface "overlap mistaken for sufficiency" in NLI fact-checking (search-summary level only; I did not open them), and an unaffiliated hobby repo whose own README states the lexical verifier "can miss contradictions that reuse the context's words (e.g. a wrong number)" (https://github.com/ramenprotokol/hallucination-hunter; weak evidence, but a usable wording precedent).

## Q2. Has anyone been burned by this exact gap?

Yes, in the human-filing form of the gap (real authority, unsupported proposition). I found NO case where a *verification tool's* "verified" output was the thing relied on and sanctioned. That specific tool-reliance incident is NOT_LOCATED under: "citation checker said verified sanction", "relied on cite-check tool court", "tool marked citation valid sanctions".

Documented (INDEP):
- Charlotin AI Hallucination Cases database, as of 2026-10-02: 2,125 cases; Fabricated 1,752; False Quotes 572; Misrepresented 894; Outdated 35 (categories overlap; no formal definitions on page). https://www.damiencharlotin.com/hallucinations/
- Whiting v. City of Athens, 6th Cir., decided 2026-03-13 (No. 25-5424): "over two dozen fake citations and misrepresentations of fact"; each attorney $15,000 punitive, double costs, fees; referred for discipline. Court's rule: lawyers must personally verify authority "regardless of whether it came from generative AI, another lawyer, a research assistant, or any other source." (ABA Litigation News, https://www.americanbar.org/groups/litigation/resources/litigation-news/2026/fake-cases-real-sanctions-dangers-ai/). Caution: the case is mostly fabricated cites; I did not read the opinion (Justia fetch timed out), so I cannot say it is a real-case-misrepresented instance.
- Tercero v. Sacramento Logistics (E.D. Cal., 2025-09-09): $1,500; "ten other cases... [did] not contain the language quoted" and 12 "do not support the propositions". In re Hale (N.D. Ga., 2025-10-28): cases "did not exist, did not support the proposition for which they were cited, or misquoted the authority". Both via secondary source (Sterne Kessler 2025 review, https://www.sternekessler.com/news-insights/insights/ai-ip-year-in-reviewai-hallucinations-in-court-filings-and-orders-a-2025-review-of-sanctions-across-the-courts-and-rule-proposals/); I have no docket numbers or primary orders. Treat as UNVERIFIED at primary level.
- Mata v. Avianca, 678 F.Supp.3d 443 (S.D.N.Y. 2023), $5,000: fabricated cases, not the misgrounded class; cited only as the origin of the doctrine.
- Princeton (Liu, Stammbach, Henderson, arXiv 2606.21155): "over 1,000 filings containing fabricated citations... growing year-over-year"; best agent "struggles with verifying pincites, misquotes, and content misrepresentations." https://arxiv.org/pdf/2606.21155
- Magesh et al.: the misgrounded class in commercial tools. Same URL as Q1.

INFERRED: for a legal buyer, the duty is on the lawyer (Whiting: verification cannot be delegated), so a vendor of a traceability checker is unlikely to carry the sanction. The exposure is commercial and reputational (the Lexis precedent), plus possible misrepresentation claims if "verified" is used unqualified. I found no legal authority on vendor liability for this; I make no legal claim.

## Q3. How do users read "verified"?

- MEASURED: Ding et al., AAAI 2025 (https://ojs.aaai.org/index.php/AAAI/article/view/34550): "significant increase in trust when citations were present, a result that held true even when the citations were random"; trust fell significantly when participants checked them. Controlled live experiment; general QA, not legal.
- MEASURED (as characterised by Seo et al.): users "rely on citations as evidence that responses are grounded in real sources, and rarely verify the cited pages themselves" (citing Fogg 2003, Liu 2023).
- Bloomberg paper: "Fluency and superficial plausibility encourage overreliance" (cites prior work).
- Automation-bias literature (search-level, not opened): overtrust of authoritative-looking AI output is general.
- NOT_LOCATED: any study of a deterministic "verified/PASS" label specifically, or of whether a README disclosure changes reliance. Queries: "verified badge citation checker overtrust study", "disclaimer README changes behaviour", "usability meaning of verified citation". Do not cite this strand as showing disclosures fail or succeed; it shows only that the *signal* is over-read and the *source* is under-checked.
- INFERRED: a disclosure the user must go find will lose to the PASS they see. Disclosure must therefore travel with the verdict.

## Q4. Precedent for shipping a deliberately narrow, loudly-stated claim

- Semgrep docs: "No soundness guarantees ... Expect both false positives and false negatives." (https://docs.semgrep.dev/writing-rules/data-flow/data-flow-overview, fetched 2026-10-03). Stated in the design-trade-off section of the core docs. Semgrep is widely adopted; I did NOT measure whether the candour helped adoption (causality INFERRED only).
- TypeScript design goals, non-goal: "Apply a sound or 'provably correct' type system. Instead, strike a balance between correctness and productivity." (https://github.com/Microsoft/TypeScript/wiki/TypeScript-Design-Goals). Limit is a published goal, not a caveat.
- seL4: "there are still assumptions that must be met, and there may still be user expectations on kernel behaviour that are not captured by the properties proved so far" plus enumerated proof statements (functional correctness, binary correctness, security, initialisation) (https://sel4.systems/Verification/proofs.html). The claim names the property proved, then the assumptions. Note seL4 also makes strong claims ("world's highest level of assurance"): narrow-and-loud works when the narrow part is precise.
- Soundiness manifesto (CACM 2015): practitioners say "soundy", an analysis sound in a named core, aimed at ending claims of unqualified soundness. http://soundiness.org/ (search-level).
- Hobby-tool wording: "can miss contradictions that reuse the context's words" (hallucination-hunter README).
- Counter-evidence for "narrow honesty is free": none located, and none for "hurts adoption". NOT_LOCATED under "adoption impact of disclosed limits".

Pattern to imitate: (1) the claim names the property checked, not the property buyers want; (2) the limit is in the product's own docs front matter and in design goals; (3) bounded numbers beat adjectives (AWS "over 75%", Stanford "17-33%").

## Q5. Recommendation

"Accept and disclose" is defensible **only if the verdict never uses a word the buyer will read as agreement, and the limit appears in the report each time**. Recommendations, with why:
1. Do not call a PASS "verified" or "grounded" anywhere unqualified. Why: the Lexis "100% hallucination-free" precedent shows the rebuttal attaches to the unqualified word; Ding shows the word will be acted on without the source being opened.
2. Print the scope line on every PASS report, not just in the README. Why: Q3 behaviour evidence.
3. Name the sibling failure explicitly, using the term the field already uses ("misgrounded" / "verified misguidance"), and give the concrete example (a source saying "no evidence of X" can satisfy a draft asserting X). Why: a named, exemplified limit is falsifiable; a vague one reads as boilerplate.
4. State a fix-version, not a promise of a date.

Candidate scope statements (one sentence each):
A. "PASS means every claim in this draft is traceable to text in a source retrieved this session; it does not mean the source agrees with the claim, and a source that denies or hedges a claim can still satisfy this check."
B. "Assure checks provenance, not truth or agreement: it certifies that the words are there, never that the source supports them, so a PASS still requires you to read what the cited source concludes."
C. "Assure refuses claims it cannot trace to a retrieved source; it does not detect when a traced source contradicts the claim (known gap, contradiction detection planned)."
My pick: A for the report footer, B for the README headline. A is falsifiable and contains the failing example's mechanism.

Evidence that would make it INDEFENSIBLE:
- A buyer-facing artefact (landing page, sales deck, output) using "verified", "grounded", "no hallucinations" or "fact-checked" without the scope line.
- Evidence that a first user relied on a PASS in a regulated or court-facing workflow where the source denied the claim and the scope line was absent from that output.
- A marketing or legal reviewer finding PASS is shown to a third party (a client or court) stripped of the footer, e.g. exported certificates without the scope line.
- Your own corpus showing the contradiction shape is common in real drafts (not just constructed), which would make the gap the main use case, not an edge. CR-005 already warns the corpus carries no row for these shapes; that is itself unmeasured.

## WHAT I SEARCHED AND DID NOT FIND
Vectors used (label / plain noun / mechanism-or-number): "Lexis hallucination-free", "citation checker verified sanction", "misgrounded", "groundedness contradiction negation", "no evidence NLI supported", "lexical overlap citation check", "verified badge overtrust", "adoption of disclosed limitations", "pinpoint 37-61%", "30.6% distort".
NOT_LOCATED: (1) a named tool returning "verified/grounded" against a source that negates the claim; (2) a sanction where a verification tool's verdict was the reliance; (3) any study of README/doc disclosure changing reliance; (4) any adoption-effect study of narrow-claim honesty; (5) primary orders for Tercero and In re Hale; (6) Whiting opinion text.
Not opened though surfaced: arXiv 2605.26663, 2210.13865, 2608.25934 (NLI/NEI robustness); Farris (6th-circuit-adjacent summary mention only) deliberately omitted as I have no source I read.

## IF I WERE WRONG
- If buyers in your actual segment read PASS as "traceable" (e.g. compliance/audit teams who already distinguish provenance from truth), disclosure is enough and my footer-on-every-report advice is over-cautious. Test: five buyer interviews showing them a PASS and asking what it guarantees.
- If a vendor-liability theory for "verified" exists in your jurisdiction, even scoped wording may not suffice: that needs counsel, not me.
- My strongest evidence is for "citations are over-trusted"; I extrapolate to "a PASS verdict is over-trusted". If deterministic tool verdicts are read more sceptically than chatbot citations, the risk is lower.
- Secondary-sourced cases (Tercero, Hale) could be mis-summarised; none of my conclusions depend on them alone, since Magesh, Charlotin and Bloomberg support the same point.
