# R45 + R46: which of the 42 families break the product's written promise (OVN-1121, 2026-11-21)

**Verdict: 20 of the 42 families break what PASS is documented to mean. In each, the claim the reader reads is not an unbroken run of text in any cited source, so these are bugs by the product's own definition. The other 22 are traceable text that the source disowns, scopes, or truncates. ADR-008 (Accepted, Sai, 2026-10-03) already decided to accept and disclose that class, so they are disclosed limitations, not moat breaches. The fail-closed refusals the gate already has for some of them are consistent with ADR-008 and stay.**

This version was challenged by the Opus adversary and **corrected**:

- D7 was misplaced;
- E2 was split into two variants;
- N3 and D3 were classed inconsistently;
- ADR-008 was not cited;
- recommendation (a) would have superseded ADR-008 and is withdrawn as sequenced.

The first version is in git history (`6a26767`).

## The written promise, and the test used here

- **ADR-008** (`docs/decisions/ADR-008-accept-and-disclose.md`, Accepted, Decider: Sai): PASS means **traceable**, not supported. The decision would be revisited on five buyer interviews.
- **`docs/ALPHA-TESTER-GUIDE.md:50` and `:264`, README `:201`–`:209`:** these disclaim denials by name ("a source that denies or hedges a claim can still satisfy this check").
- **README `:200`:** "a file it wrote and read back is a verbatim source".

**Mechanical test (Class T):** after the gate's own normalisation, the claim's tokens do not form one unbroken run in any cited source. Or the text the reader sees differs from the text the gate traced (markup, glyphs, layout). Anything that passes the test is traceable as written, so it falls under ADR-008.

## Class T: traceability breaks (20). Bugs by the written promise

| Families (round) | Why the test fails |
|---|---|
| F1, F4, F5 (R45) | The rendered sentence differs from the traced one: a hidden `not`, a ❌ glyph, a fake comment that deletes visible text |
| F2, F3, F7, F8 (R45) | The reader's claim is composed by draft structure (heading, lead-in, continuation, definition); no source run contains it |
| F6 (R45) | `10⁵` is read as 100,000 and traced as 105 |
| E2, reassembled variant (R45) | `## Fraud at Quay Trust` and `## The council never met` are assembled from source words |
| N1, N2, N4, N5, N6, N7, N8, N9, N10, N11 (R46) | A word or figure inside the claim differs from, or is missing in, the source run (N1 and N8 re-checked by the adversary with an unbroken-run probe) |
| D9 (R46) | A condition dropped from mid-sentence, or quote halves |

**Proposed fix order:** F1/F4/F5/F6 (render-first, R1), then F2/F3/F7/F8 and E2-reassembled (R3, compose before grounding), then N1–N11 (R4/R5) and D9. All are fail-closed.

## Class S: traceable but not supported as read (22). Disclosed under ADR-008

| Families (round) | Device |
|---|---|
| E1, A3, B1, B2, B3 (R45) | A later sentence or paragraph disowns the claim |
| E3, R45-D1, R45-D2, C1, E1c (R45) | A frame in the same sentence: attribution, reporting verb, "erroneously", a condition |
| A1, A2, G1 (R45) | Strikethrough, a footnote retraction, a disowning label |
| E2, verbatim variant (R45) | A heading copying a sentence the source then denies (counted under E2 in Class T; listed here for its mechanism) |
| R46-D1 to R46-D5 | Absence scope, limiters, negatives outside the list, scoping headings |
| N3 (R46) | A trailing rate dropped: the shorter claim is an unbroken run (same truncation mechanism as R46-D3) |
| D7 (R46) | Self-citation through a web tool; README:200 accepts a file the agent wrote and read back |
| D8 (R46) | A co-cited or later capture contradicts the claim |
| D11 (R46) | A partial read stops before the denial |

Counted families: 22 here (excluding the E2 row) + 20 in Class T = 42. E2 is counted once, in Class T; its verbatim variant is listed here for its mechanism only.

## Corrections to tonight's earlier reports

- **`RED-TEAM-R46.md`:** "D7 and D8 are Error-B under any reading" is withdrawn. D7 is documented (README:200). D8 is Class S. It is still the cheapest high-value fail-closed fix (all-of-cited for refusals, latest capture only), but it is not a breach of the written promise.
- **The "contradiction" in the first version was overstated.** The documents disclaim denials, and refusing them where detectable is consistent with ADR-008 and CLAUDE.md. The real inconsistency is in **measurement**: red-team rounds and the fabrication corpora count Class S shapes as Error-B, but the written promise excludes them. A reader of "7/280 certified fabrications" cannot tell which promise they break.

## Recommendation

1. **Fix Class T first** (20 families). It is fail-closed, and these break the promise as written.
2. **Keep ADR-008 and keep the existing Class S refusals.** Withdrawn: my first version's "(a) promise support now". It would make the documents false on the day they change, and it supersedes ADR-008 without the buyer interviews ADR-008 names as its deciding evidence.
3. **Label every red-team finding and corpus class T or S.** Report Error-B only for T, and report S as "disclosed limitation, refused where detectable". Why: the moat number should mean one thing.
4. **Cheap S-class refusals are still worth building:** D8 (all-of-cited, latest capture) and D11 (do not ground on a partial read whose cut point is inside the paragraph). Near-zero honest cost; inside the fail-closed authority.
5. **For Sai, when the five buyer interviews ADR-008 names exist:** decide whether PASS should promise support. The R2 clause-prefix measurement (8/2,044 on a text model, unchecked) is the starting evidence, not the answer.
