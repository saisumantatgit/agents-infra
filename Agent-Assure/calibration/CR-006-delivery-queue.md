# CR-006 — the delivery queue (J-48, J-43, J-39, J-44) + round 12

Window: 2026-10-02, branch `delivery-queue-2026-10-02`, after PR #6 merged.
Ratifications **D-62 … D-72**. CR-005 remains deployed: **no rate moved**.

## Projection vs actual

| # | Step | Projected | Actual | Δ | Note |
|---|---|---|---|---|---|
| 1 | J-48 — documentation | 0.1M | — | — | landed `1c00bdc` |
| 2 | J-43 — spelled quantities | 0.6M | — | — | landed `657c81e`, amended by D-70 |
| 3 | `extract_arguments` (J-39) | 1.2M | — | — | landed `5c177fa` |
| 4 | J-44 — plural stem | 0.3M | — | — | landed `10656fd`, **WITHDRAWN** `59b647d` |
| 5 | One adversarial round | 0.5M | 0.17M | −66% | one Opus adversary, 42 tool calls, 18 min |
| 6 | CR-006 + close | 0.5M | — | — | this file |
| — | **TOTAL (new tokens)** | **3.5M** | **0.65M** | **−81%** | 220K output + 434K cache creation, 168 turns |

Per-step actuals are not separately instrumented (the measure is per-session),
so the total is reported rather than apportioned by guess.

**Δ explanation (>20%, required):** the estimate was built from the last two
sessions' *rates*, and those sessions were LONG — cache creation grows with
conversation length, not with work done. This window ran 168 turns against the
previous window's 142-turns-for-5.33M. The projection priced ~5× too much cache
re-creation. **Third consecutive over-estimate** (7M→2.6M, 3.1M→2.8M,
3.5M→0.65M); the bias is systematic and the next estimate should be built from
TURN COUNT × a short-session rate, not from a long session's average.

## Error rates — unchanged, and that is a measurement, not an absence

| Metric | CR-005 | CR-006 | Basis |
|---|---|---|---|
| Error-A | 0.320 | **0.320** | n=52 gold, single ratifier |
| Error-B | 0.000 | **0.000** | 0/27; 95% upper bound ~10.5% — never quote as zero |
| Gold md5 | `6215b526…d171f` | **unchanged** | zero labels touched |
| Corpus | — | **byte-identical** at all four regenerations | `feature_rows-v2.jsonl` + `labeling-v2.csv` |
| Suite | 751 / 2 / 63 | **789 / 2 / 61** | passed / skipped / xfailed |

**J-39 IS measured.** All 7 relational rows now carry multi-token endpoints
where they carried one, so the corpus exercises the change, and every verdict
held — q12/q36 (gold GROUNDED) still ground against the longer needle;
q23/q25/q26/q43/q48 stay refused.

**J-43 is NOT measured.** Zero rows carry a spelled number inside a relational
claim (7 relational rows, none spelling a figure; 3 rows spelling a figure, none
relational). Its Error-A is unknown. Needs corpus rows → gold labels → Sai.

**None of round 12's nine Error-B shapes has a corpus row.** So the byte-identical
corpus says nothing about them either way.

## What round 12 cost and what it bought

One Opus adversary, dispatched after the conclusion was committed (`25b9b66`).
**16 findings, all reproduced; 9 ERROR-B, 3 ERROR-A, 2 TEST-DEFECT, 2 DOC-DEFECT.**
Solo gate: `challenged | CORRECTED`.

- **It caught an Error-B I shipped.** J-44's `_stem` maps the noun "news" to the
  adjective "new": a fabricated causal claim certified PASS 100.0 through the
  CLI. Withdrawn same day (D-69). My claim that J-39's longer phrase bounded the
  stem was wrong — a collision on the HEAD noun makes the modifiers irrelevant.
- **It caught my own lexicon's omission** (plural scale words, D-70), correctly
  named as an ordinary bug rather than the open-class trap.
- **It caught two near-vacuous assertions in tests I had just written.**
- Six Error-B findings are PRE-EXISTING (identical against `1c00bdc`),
  registered as J-57 … J-62, NOT fixed (D-72).

## The one structural lesson

A word list that drives a REFUSAL (`_SPELLED_NUMBER_WORDS`) and a word list that
licenses an ACCEPTANCE (an s-final-singular blacklist) are not the same kind of
object, however similar they look. A missing member of the first is an unchecked
figure; a missing member of the second **is the attack**. J-43's lexicon is
legitimate for exactly the reason J-44's cannot be.

## Launch claim

**Unchanged by this window, and now in question for a different reason.** Nothing
here moved a rate. But round 12 demonstrated six pre-existing Error-B shapes on
the relational branch, two of them CRITICAL. Whether CLAIM-1 must narrow is
Escalation #1 and #5 — Sai's, with J-57 … J-63 as the evidence.
