# R45 + R46: which of the 42 families break the product's written promise (OVN-1121, 2026-11-21)

**Verdict: 22 of the 42 families break what PASS is documented to mean. The reader's claim is not text in the cited source, or the source is the draft itself. The other 20 are claims the source states and then disowns. The documents explicitly disclaim those ("a source that denies or hedges a claim can still satisfy this check"), but rounds R36–R44 have been fixing them as moat holes. The first 22 are bugs by any definition. The 20 are a product decision Sai has half-made.**

**The written promise:** `docs/ALPHA-TESTER-GUIDE.md:50` says "A PASS means 'traceable', never 'true' and never 'supported'." The engine's own `scope` field (`:264`) reads:

```
PASS means every claim in this draft is traceable to text in a source present in the evidence store supplied to this run; it does not mean the source agrees with the claim, and a source that denies or hedges a claim can still satisfy this check.
```

**Correction to `RED-TEAM-R45.md` recommendation 1:** I wrote "do not present PASS as a guarantee to alpha testers". The tester guide already says this, so that recommendation is withdrawn as new work. What the guide does not say is that the 22 families below exist.

## Class T: traceability breaks (22). The reader's claim is not in the cited source

| Families | Why it breaks "traceable" |
|---|---|
| F1, F4, F5 | The reader reads a different sentence from the one the gate traced: a hidden `not`, a ❌ glyph, a fake comment that deletes visible text. |
| F2, F3, F7, F8 | The draft's own structure (heading, lead-in, continuation, definition) makes the claim the reader reads. No source contains that claim. |
| F6 | `10⁵` is read as 100,000 and traced as 105. |
| E2 (reassembled headings) | `## Fraud at Quay Trust` is assembled from source words; no source says it. |
| N1–N11 | The draft's figure, qualifier, unit, rate, range or date differs from the source's. |
| D9 | A condition dropped from mid-sentence, or quote halves, so no contiguous source text matches the reader's claim. |
| D7 | The "source" is the draft, fetched back through a web tool. It is traceable only to itself. |

These are Error-B against the product's own definition. They belong at the top of the build order, together with D8 (below), which costs nothing honest.

## Class S: support breaks (20). The source states the claim, then disowns it

| Families | Disowning device |
|---|---|
| E1, A3, B1, B2, B3 | A later sentence or paragraph: "That was cooked up", "That was in error", "As if", "The story above was fabricated" |
| E3, D1 (lane A), D2, C1, E1c | A frame in the same sentence: attribution, a reporting verb without "that", "erroneously reported", a condition |
| A1, A2, G1 | Markup or a label: strikethrough, a footnote retraction, `Gossip:` |
| D1–D5 (lane D) | Absence scope or limiters, and negatives outside the negation list |
| D8 | A co-cited or later capture contradicts the claim |
| D11 | A partial read that stops before the denial |

The documents disclaim these. The code does not treat them that way: R36–R44 shipped refusals for dozens of denial shapes, and CLAUDE.md's Error-B rule ("a fabrication certified PASS") covers them. That's a contradiction between the product's stated promise and its engineering direction (contradiction-as-locator).

## Recommendation

1. **Fix Class T first** (22 families + D8), all fail-closed, with near-zero to moderate honest cost. Why: they break the promise testers are told they are getting.
2. **Sai rules on Class S**, one of two ways:
   - **(a) Promise support.** Make the documents say a PASS means the source asserts the claim in its own voice. Then build R2 (clause-prefix plus paragraph back-reference; measured cost 8/2,044 for the prefix half), R1 for A1/A2, and the absence-scope fixes. That turns the 20 into bugs.
   - **(b) Promise traceability only.** Keep the documents as they are, stop treating denial shapes as moat holes, and report them through `support_diagnostic`, which today catches about half (README:203).

   I recommend (a). Why: an alpha tester reading "PASS" will act on the claim, and every Class S example is ordinary web prose ("Several outlets erroneously reported…"). The project has already spent rounds R36–R44 building towards (a), so (b) would discard that work and keep a promise users will not read as narrowly as it is written. What would flip it: the (a) build's measured honest cost turning out large, since the prefix half is measured but the paragraph half is not.
3. **Add to the tester guide's Known issues, after Sai approves the wording:** the Class T families in one line each. Until they are fixed, PASS can be wrong about traceability itself.
