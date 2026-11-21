# R2 measurement: a structural test for "the source asserts this in its own voice" (OVN-1121, 2026-11-21)

**Verdict: a word-list-free rule closes 7 of the 11 R2 families in RED-TEAM-R45 on a text-level model, at an honest cost of 8 of 2,044 grounded claims (Error-A corpus) and 0 of 56 (usage_genres). The rule: a verbatim match grounds only if the text before it in its source sentence is empty or ends in a coordinator. One sibling stays open. This is a measurement on a text model, not on the gate.**

## Terms

| Term | Meaning here |
|---|---|
| Prefix | The text of the claim's source sentence before the verbatim match. |
| Coordinator | `and`, `but`, `or`, `while`, `whereas`, `yet`, `so` (optionally after a comma), or `;`. A bare comma or colon is **not** a coordinator. |
| R2 | The R45 root cause: refusals of disowned source sentences are word lists, so a missing word passes. |

## Rule

A verbatim match grounds only if its prefix is empty or ends in a coordinator. Anything else is refused, whatever the words: an attribution, a condition, a label, a question, a negating adverb.

## Results

| Corpus | Grounded honest claims | Still allowed | Newly refused | Not located by my sentence splitter |
|---|---:|---:|---:|---:|
| Error-A corpus (336 drafts) | 2,044 | 2,036 | 8 | 0 |
| usage_genres (copied and paraphrased) | 61 | 56 | 0 | 5 |

The 8 newly refused are partial matches, for example the claim starting after "contractors are" or "the handbook states that the rule "does". Each is a fragment that main grounds by containment. I read that as a correct refusal, but it is Error-A until someone checks each one.

Why the conjunct exemption matters: in usage_genres, 17 of 55 grounded claims are one conjunct of a longer sentence ("…rebuilt in 1894 and automated in 1962" → two claims). A plain "whole sentence only" rule would refuse 31% of them.

**R45 frames, classified by the same rule:**

| Family | Source shape | Result |
|---|---|---|
| E3 | `According to an anonymous forum post, X` | refused |
| D1 | `The blog reported X` | refused |
| C1 | `Several outlets erroneously reported X` | refused |
| E1c | `Should the vote pass, X` | refused |
| B3 | `Did X?` | refused |
| D2 (colon) | `The press release stated: X` | refused |
| G1 (inline label) | `Gossip: X` | refused |
| honest conjunct | `The office opened in May and X` | allowed |
| honest semicolon | `The office opened in May; X` | allowed |
| honest plain | `X.` | allowed |

**Not closed by this rule:** the families whose disowning text is *outside* the sentence:

- E1, B1, B2 and A3 (a later sentence or paragraph);
- G1 as a list label on its own line;
- D2's trailing attribution (`X, the press release stated`).

They need the paragraph-level half of R2: a back-referring sentence that disowns the claim.

**Open sibling:** a frame that opens a conjoined sentence, for example `Critics claim the office opened in May and X`. The prefix ends in "and", so X is allowed. Fix direction: the sentence's first clause must itself pass, which means applying the test to the sentence start too. The full fix is a clause parser, which is the upgrade path.

## What this does and does not show

- **It is a text model.** My splitter (lines, list markers, table cells, `. ! ?`) and lower-cased NFKC matching stand in for the gate's decomposer and tokenizer. The gate's own run on a candidate patch is the measurement. Build it via the Codex brief, fail-closed, with both fabrication corpora and the R45 probes as the Error-B check.
- **Goodhart risk.** The Error-A corpus was built by copying whole sentences, so it favours this rule. usage_genres is the only check against real extraction habits, and it has 61 claims. A paraphrase-heavy honest corpus would be a better test.
- **Product meaning.** Refusing "According to the 2025 annual report, revenue rose 4%." cited to that report is Error-A by design. The writer has to cite the claim as attributed ("The 2025 annual report says…"), which the gate cannot ground verbatim either. That is the ADR question in RED-TEAM-R45 recommendation 4: what PASS certifies.

## Reproduce

For each grounded honest claim, find the first source sentence containing it. Sentences are split per line, with list markers and table pipes stripped, then on `(?<=[.!?])\s+`, and normalised with NFKC, whitespace collapse and lower-casing. Take the prefix, and apply `(^|(,?\s+(and|but|or|while|whereas|yet|so))|;)\s*$`. The scripts lived in the run's scratch directory.
