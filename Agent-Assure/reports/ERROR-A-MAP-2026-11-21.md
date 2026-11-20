# Error-A map: where the honest refusals are, and which ruling unlocks each (OVN-1121, 2026-11-21)

**Verdict: measured gains from the three candidate rulings total 706 of the 1,946 honest claims the gate refuses (36%). Only one of them, C2 "N percent" (+69, 0 attacks pass), is ready to ship. The largest, a sentence-boundary stop on the hedge window (+351), fails its own Error-B test and stays parked.**

Measured on main `d8c2ec0`, Error-A corpus: 336 honest drafts, 3,990 authored claims, 2,044 grounded, 1,946 refused. This map was challenged by an Opus adversary and **corrected**: the headline, the hedge numbers and the C1u record were wrong in the first version, which is in git history (`3110525`). The adversary's gains were measured on scratch-patched copies of the gate; no repo file was edited.

## Terms

| Term | Meaning here |
|---|---|
| Error-A | An honest claim refused. Recoverable. |
| Error-B | A fabrication certified PASS. Unrecoverable. |
| Hedge window | The 5 source tokens before a verbatim match. A hedge word there (`not`, `no`, `never`, `per`, `claims`…) refuses the match (`_SPAN_HEDGE_LOOKBACK`, `ground_check.py:1665`). |
| Refused count vs gain | Refused is what the gate refuses today for that cause. Gain is what a candidate rule actually frees once every other rule has run. The two differ. |

## The map (refused counts reproduce exactly)

| # | Cause (first refused segment) | Refused | Share | Candidate | Measured gain | Error-B result |
|---|---|---:|---:|---|---:|---|
| 1 | Hedge word in the 5 tokens before the match | 658 | 34% | (c) stop the window at a sentence boundary | +351 | **Fails:** v1 certified fabrications 7→9; 5 of 15 probe shapes newly PASS |
| 2 | List ordinal read as a figure | 406 | 21% | C1u list numbers | +286 | Pack 2026-11-15: ship with a CEILING; keys on capitalisation |
| 3 | Next sentence holds a denial word | 174 | 9% | Back-reference rule (not designed) | not measured | A paragraph-break cut certifies `<claim>.` followed by a new paragraph "Quay Trust denies this." |
| 4 | Absence search rule not met | 120 | 6% | none | — | by design |
| 5 | Spelled percent | 103 | 5% | C2 "N percent" | +69 | **0 lost, no fabrication draft moves to PASS, 0 of 12 new attacks pass** (re-measured on `d8c2ec0`) |
| 6 | UNCITED | 99 | 5% | none | — | working as intended |
| 7 | 11 other diagnostics | 386 | 20% | not mapped | — | — |

## Row 1: why the sentence-boundary stop is parked

- **What it frees:** with the gate's own tokenizer, all 682 hedge-refused segments are located. 576 have the hedge word only in an earlier sentence. The stop actually frees 351 claims, because the next denial rules still catch the rest. My first version's "541, upper bound" came from my approximate tokenizer and is withdrawn.
- **What it opens:**
  - Two certified fabrications on v1, both via the open E1 "cooked up" hole (`C1-RULING-PACK-2026-11-21.md`).
  - Five probe shapes that newly PASS:
    - `The vendor says:` then a line break, then the claim;
    - `A spokesman said:` then a blockquoted claim;
    - `Larch Holdings denies the report. <claim>.`;
    - two hypothetical framings.

  The attacks my first version named ("They claim X", "That is false: X", "Not so. X") stay refused, so they were the wrong examples.
- **It is a restructure, not a patch:** `_span_is_hedged` receives a token list with the punctuation already stripped (`ground_check.py:7006-7010`). A sentence-boundary stop needs the boundary carried into that call.
- **Next step, if Sai wants it:** after E1 is fixed, re-measure a stop that treats a colon and line break as continuing the clause. That closes the colon and blockquote probes, at a smaller gain.

## A third live fabrication found by the same review (E3)

`According to an anonymous forum post, Quay Trust was acquired by a larger rival last spring.` in the source, cited as the plain claim, **certifies PASS 100 on main**. The attribution is 6 tokens before the claim, one past the window. `According to a forum post, …` (5 tokens) is refused.

Reproduced first-hand with a passing plain control: 6 and 7 tokens PASS, 5 FAIL. This is the round-7 "hedge beyond the 5-token window" class, still open for sentence-initial `According to …,` frames. Fail-closed fix: refuse when an attribution frame opens the claim's own sentence, at any distance up to the clause comma. Brief: `docs/planning/briefs/OVN-1121-E3-attribution-beyond-window.md`.

## Recommendations

1. **C2 "N percent": rule YES (+69, 0 lost, 0/12 attacks).** Why: re-measured tonight on current main, independently of the 15 Nov pack, and the code's own `numeric_ok` docstring already promises `25% == 25 percent`. What would flip it: a number shape outside the 12 tested (count, percentile, percentage points, `%`, decimal shift, wrong value, rise vs fall, other subject, denied source).
2. **(c) hedge-window stop: rule NO for now.** It frees 351 but opens Error-B as built. Revisit after E1 is fixed, as the colon-aware variant.
3. **C1u list ordinals: the records disagree, so Sai should settle it.** The 15 Nov pack and register row D-116 record "ship with a CEILING". A logbook line records my NO. The measured gain is +286 (my first version said +292, which is C1's figure). I still lean NO, because the candidate keys on capitalisation, which this project has lost to before (round 4). A version that drops the ordinal only where the source line starts with the same ordinal avoids that and should be measured first.
4. **Next-sentence denial:** no ruling asked. Design a back-reference rule first. The adversary estimates that treating "that" after a reporting verb as not pointing back would free about 91 of 183 claims, with its own attack to measure.

## Reproduce

Refused counts: in `tests/error_a_corpus/results.json`, a refused claim has `grounded == false`, and its cause is its first non-GROUNDED segment. A list ordinal is a claim whose draft line starts `\d+[.)]` and reads UNVERIFIED_NUMBER. A spelled percent is a claim containing `percent` that reads UNVERIFIED_NUMBER. Gains were measured by running each corpus through a scratch-patched copy of `ground_check.py`. The scripts lived in the run's scratch directory and were removed at teardown; the method is stated here.
