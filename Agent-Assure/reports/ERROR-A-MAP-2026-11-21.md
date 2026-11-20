# Error-A map: where the honest refusals are, and which ruling unlocks each (OVN-1121, 2026-11-21)

**Verdict: three rulings Sai has already been asked for would address up to 1,167 of the 1,946 honest claims the gate refuses (60%). No gate change is needed to find out which.**

Measured on main `d8c2ec0`, Error-A corpus: 336 honest drafts, 3,990 authored claims, 2,044 grounded, 1,946 refused. The cause is each refused claim's first refused segment, as reported by `results.json`. These are counts of what the gate refuses today, not measured gains. A gain is known only after a candidate is run against the fabrication corpora, which is what each ruling's "measure first" step does.

## Terms

| Term | Meaning here |
|---|---|
| Error-A | An honest claim refused. Recoverable. |
| Error-B | A fabrication certified PASS. Unrecoverable. |
| Hedge window | The 5 source tokens before a verbatim match. A hedge word there (`not`, `no`, `never`, `per`, `claims`…) refuses the match (`_SPAN_HEDGE_LOOKBACK`, `ground_check.py:1665`). |
| Pass-widening | Any change that lets a claim pass that main refuses. Escalation #1, so it needs Sai. |

## The map

| # | Cause (diagnostic) | Refused | Share | Ruling that addresses it | Status |
|---|---|---:|---:|---|---|
| 1 | Hedge word in the 5 tokens before the match (`verbatim_but_hedge_word_before_it`) | 658 | 34% | (c) stop the hedge window at a sentence boundary | Asked 2026-11-15, open |
| 2 | List ordinal read as a figure ("1. Members open…" → UNVERIFIED_NUMBER) | 406 | 21% | C1u list numbers (2026-11-15 pack measured +292) | Asked; my recommendation was NO (it keys on capitalisation) |
| 3 | Next sentence holds a denial word (`verbatim_but_next_sentence_denies`) | 174 | 9% | Narrow to a back-reference that resolves to the claim (the reviewer's estimate: about 91 of 174 if "that" after a reporting verb does not point back). A paragraph-break cut (19) is NOT safe: it certifies `<claim>.` followed by a new paragraph "Quay Trust denies this." | New tonight, Sai's |
| 4 | Absence claim, search rule not met (UNVERIFIED_ABSENCE) | 120 | 6% | None proposed; by design (2-query rule) | — |
| 5 | Spelled percent ("85 percent" → UNVERIFIED_NUMBER) | 103 | 5% | C2 "N percent" (pack measured +69, 0/11 attacks pass) | Asked; recommendation YES |
| 6 | No cited verbatim source (UNCITED) | 99 | 5% | None; working as intended | — |
| 7 | All other diagnostics (11 kinds) | 386 | 20% | Not mapped tonight | — |

Up to 1,167 = 658 + 406 + 103. Row 3 is excluded, because its only measured cut has an attack.

## Row 1 in detail: most hedge refusals look back across a full stop

For each of the 682 hedge-refused segments, I found the claim in its source and located the last hedge word in the 5 words before it.

| Where the hedge word sits | Segments | Example |
|---|---:|---|
| In an earlier sentence (a `. ! ?` or line break lies between it and the claim) | 541 | "…is not documented here. Each project keeps its attachments for 28 days…" |
| In the claim's own sentence | 37 | "no" inside the same sentence |
| Not found by my tokenizer | 104 | mostly one-word answers ("Yes", "No") I could not place uniquely |

Most frequent hedge words in the earlier-sentence group: `not` 125, `no` 115, `never` 96, `per` 71, `without` 43, `false` 43, `unless` 24.

This is the same pattern as the far-denial finding in `C1-RULING-PACK-2026-11-21.md`: a negation in a previous sentence is read as governing a claim it doesn't refer to. A hedge that genuinely governs a claim across a full stop also exists ("Critics disagree. They claim X." or "That is false: X"). That is why stopping at the boundary widens passes and needs the fabrication corpora (504 drafts across v1 and v2) run as the Error-B check before it ships.

**Limit:** my tokenizer approximates the gate's own (regex words, NFKC). The 541 is an upper bound on what the ruling could free. The gate's own run on a candidate patch is the measurement.

## Recommendation, in order of value per unit of risk

1. **C2 "N percent": rule YES now (+69 measured).** Why: it was measured on 15 Nov, 0 of 11 attacks pass, and the code's own docstring already promises `25% == 25 percent`. What would flip it: an attack class the 11 do not cover, for example `85 percent` against a source `85 percentile`, which was tested and refused.
2. **(c) hedge window at a sentence boundary: rule "measure it" now.** It's the largest single cause, at up to 541 segments. Codex builds the candidate after 26 Nov. It ships only if both fabrication corpora show no rise in any class and an Opus adversary round finds 0 blockers. What would flip it: the corpora showing even one new certified fabrication. The window then stays, and the upgrade path is a clause parser.
3. **Next-sentence denial: no ruling asked yet.** The paragraph-break cut is withdrawn: an adversary showed `<claim>.` followed by a new paragraph "Quay Trust denies this." would certify. A back-reference rule needs designing first (see `C1-RULING-PACK-2026-11-21.md`).
4. **C1u list ordinals:** I'm keeping my 15 Nov NO. The measured gain (+292) is large, but the candidate keyed on capitalisation, which this project has already lost to twice (round 4). A better candidate drops the ordinal on both sides, but only where the source line itself starts with the same ordinal. It needs designing, not a ruling.

## Reproduce

Read `tests/error_a_corpus/results.json`, `manifest.json` and `drafts/`. A refused claim is one with `grounded == false`. Its cause is its first non-GROUNDED segment's verdict and diagnostic. A claim counts as a list ordinal when its draft line starts `\d+[.)]` and the verdict is UNVERIFIED_NUMBER, and as a spelled percent when its text contains `percent` and the verdict is UNVERIFIED_NUMBER.
