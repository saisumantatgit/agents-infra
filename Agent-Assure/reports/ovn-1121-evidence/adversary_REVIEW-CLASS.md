# Adversarial review: R45 + R46 classification (OVN-1121, 2026-11-21)

Target: `/Users/saisumanth/vibe-coding/Agents/ai-overnight-1121/Agent-Assure/reports/R45-R46-CLASSIFICATION.md`
(branch head `6a26767`). Read-only; the probe script is `class/contig.py`, run against main `d8c2ec0`.

**Verdict: the split is the right idea, but at least three families are in the wrong class, and the
promise-vs-engineering contradiction is overstated.**
- D7 is explicitly disclaimed by the README, so it is not a traceability break.
- E2's primary variant is verbatim, so it is traceable.
- N3 and D3 are the same mechanism, yet sit in opposite classes.
- Sai already decided the denial question in ADR-008 (Accepted, Decider: Sai), and fail-closed denial
  refusals do not contradict that decision.

Recommendation (a) holds only after its build, and only against the evidence ADR-008 names as deciding it.

Format: claim | verdict | evidence. Ordered by severity.

## 1. Family placement

**1a.** Claim: D7 (the draft fetched back through a web tool cites itself) is Class T, "traceable only to
itself".
| **REFUTED as Class T** |
Evidence: `README.md:200`, row "Where the evidence came from", reads: "The drafting agent's tool choices
are trusted, so a file it wrote and read back is a verbatim source." The scope line (`ALPHA-TESTER-GUIDE.md:264`)
promises traceability to "a source present in the evidence store", and the fetched-back draft is one.
The documents disclaim D7 more explicitly than any Class S family. It belongs with the disclaimed
families, or in a third class: disclaimed in the docs but engineered against (J-83 already refuses the
`Read` form). This also changes the count: Class T is 21, not 22. Separately, `RED-TEAM-R46.md`'s "D7 and
D8 are Error-B under any reading of what PASS means" is false: under reading (b), the literal promise,
both satisfy it.

**1b.** Claim: E2 is Class T, with the example `## Fraud at Quay Trust` "assembled from source words; no
source says it".
| **CORRECTED: E2 must be split** |
Evidence: `RED-TEAM-R45.md`, E2 row, gives as its primary example "a verbatim copy of a denied sentence
`## The regulator found fraud at Quay Trust`". The source text is `The regulator found fraud at Quay Trust.
That never happened.` (my D-122 sibling probe), so that heading IS text in the source. The verbatim
variant is Class S (the source states it, then disowns it). Only the reassembled variant (`## Fraud at
Quay Trust`, `## Regulator: fraud at Quay Trust`) is T. The classification renamed the family to
"(reassembled headings)" and so dropped R45's main example from the count. Note: the heading is
`NON_CLAIM`, so the gate traces neither variant at all. Even the verbatim one is "traceable" only in the
sense that the text exists in the source, not because the gate traced it.

**1c.** Claims: N1–N11 are all Class T ("the draft's figure, qualifier, unit … differs from the source's");
D1–D5 (lane D), including D3 widened subject, are Class S.
| **CORRECTED: the line cuts through one mechanism** |
Evidence (`class/contig.py`, main, the gate's own `_tokenize`):
- N3 `The depot lease costs 5 million pounds per month.` → claim `The depot lease costs 5 million pounds`:
  **PASS, contiguous in the source = True.**
- D3 `The night fleet of Larkfield Haulage does not use diesel engines.` → `Larkfield Haulage does not use
  diesel engines`: **PASS, contiguous = True.**

Both trim a scoping word off the end of the sentence and leave a verbatim substring, so both are equally
traceable. Placing N3 in T and D3 in S is inconsistent. The test the report needs is mechanical: is the
claim's token run contiguous in a cited source? Internal deletions (my N1 and N8 probes: contiguous =
False) are T. Prefix or suffix truncations (N3, D3, and D1 lane D "In Europe, X has never…") are traceable
by the written promise. R46's own probes were removed, so each N family's exact shape must be re-checked
against this test. I verified N3 only.

**1d.** Claim: Class S means "the source states the claim, then disowns it".
| **CORRECTED (definition)** |
Several S members do not fit it:
- D3, D5 and D1 (lane D) narrow the claim's scope; the source never states the claim.
- D8b: a different source corrects it.
- D11: the disowning text was never captured.

S is really "traceable, not supported". That is exactly the gap the scope line names ("does not mean the
source agrees with the claim"), so the class holds together under that label. The report's label for it is
wrong.

**1e.** Claims: A1/A2 (struck or footnote-retracted SOURCE text) are S; F1, F4, F5 (DRAFT markup) are T;
D9, D11 and D8 are placed as stated.
| **UPHELD** |
- A1/A2: the claim string is present in the raw source, so it is traceable, and the struck or retracted
  status is a disowning.
- F1/F4/F5: the reader reads a sentence that is not in the source.
- D9: the reader's joined sentence is in no source, though each half is.
- D11: the claim is in the captured text, so it is traceable.
- D8: the claim is in a captured source, so S is right. That is why the report has to special-case D8 into
  the first build; it is correct to do so, but on cost grounds, not on the promise.

**1f.** Family IDs collide across rounds.
| **CORRECTED (clarity)** |
R45 and R46 both have a D1 and a D2. The S table lists "D1 (lane A), D2" and "D1–D5 (lane D)". The totals
add up to 42 (22 + 20, checked by hand), but "D2" is ambiguous without a round prefix. Use R45-D1 /
R46-D1 and so on.

## 2. Is the "promise vs engineering direction" contradiction real?

**2a.** Claim: the documents disclaim denials, not only truth.
| **UPHELD** |
Evidence:
- `ALPHA-TESTER-GUIDE.md:50`: "A PASS means 'traceable', never 'true' and never 'supported'."
- `:264`, the scope line: "a source that denies or hedges a claim can still satisfy this check".
- `README.md:201`: "That the source AGREES with the claim | No."
- `README.md:209-212`: "we found no evidence that X" can satisfy the check.

Denials and hedges are disclaimed by name.

**2b.** Claim: this is "a product decision Sai has half-made", and R36–R44 contradict it.
| **CORRECTED** |
Evidence: `docs/decisions/ADR-008-accept-and-disclose.md`: Status **Accepted**, **Decider: Sai**,
2026-10-03. "Ship the provenance claim. Accept the agreement gap and disclose it IN THE PRODUCT." The
report never cites it, although README's own heading does ("What PASS means … (ADR-008)"). ADR-008
rejects a contradiction VERDICT and a whole-source scan; their Error-A cost was 0.400 to 0.560, and honest
drafts went from 7 pass to 5 FAIL. It does not forbid fail-closed refusals of detectable denial shapes.

CLAUDE.md's grounding definition (repo `CLAUDE.md:23`) builds denial into T1: "contained verbatim in a cited
source **and not under an attribution/denial hedge**". The scope line says "can still satisfy", which is a
permission, not a promise to accept. So "refuse when the gate can tell, disclose when it cannot" is
consistent. It is an asymmetry, not a contradiction.

What IS inconsistent is the bookkeeping. Red-team rounds count Class S shapes as Error-B and as moat holes,
while the external definition of PASS excludes them. The measured Error-B rate therefore depends on an
unwritten definition, and that is the seam to fix.

## 3. Recommendation (a), and other stated facts

**3a.** Claim: recommend (a), promise support. "Make the documents say … Then build R2 …".
| **Does not hold as sequenced** |
1. **The order is backwards.** Changing the documents first makes them false the same day: 20 Class S
   families are live, plus J-70, the R14-04 shape and the cooked-up hole (D-122). Under (a) the docs change
   only after the build passes its corpora and an adversary round.
2. **(a) supersedes an accepted ADR.** Under ADR-023 that needs a superseding ADR, and ADR-008 names its
   own flip evidence: "Five buyer interviews would settle it". The report's why ("an alpha tester reading
   PASS will act on the claim") restates the negation of ADR-008's load-bearing assumption without any new
   evidence. It remains a hypothesis; the alpha test (5 users) is the cheap place to measure it.
3. **"(b) would discard that work" is false.** Under (b) every R36–R44 refusal keeps working: they are
   fail-closed and nothing is removed. Only the hole-counting changes. The argument is also sunk cost.
4. **Cost understated.** R45 itself says R2 "will refuse honest attributed facts ('According to the annual
   report, revenue rose 4%')". Promise (a) refuses every honestly attributed sentence by definition, and
   the 8/2,044 does not measure that, because attributed sentences are already refused today (3b).

**3b.** Claim: "measured cost 8/2,044 for the prefix half".
| **CORRECTED (missing qualifier)** |
`R2-CLAUSE-PREFIX-MEASUREMENT.md:3`: "This is a measurement on a text model, **not on the gate**." `:24`:
the 8 have not been adjudicated ("it is Error-A until someone checks each one"). It also counts only claims
main grounds today, so it cannot see the attributed-fact cost in 3a.4.

**3c.** Claim: R45 recommendation 1 is withdrawn because the guide already disclaims "supported".
| **UPHELD** | `ALPHA-TESTER-GUIDE.md:50`.

**3d.** Claim: `support_diagnostic` "today catches about half (README:203)".
| **UPHELD** | README states recall 7/14 on its denial set (table row and `:214-216`). The line reference
is approximate.

## Load-bearing assumption of this review

Point 1a reads README:200 as part of the documented promise. If Sai holds that the scope line alone defines
PASS, D7 is still traceable to an evidence-store source by that line's literal words. Either way it is not
a traceability break.
