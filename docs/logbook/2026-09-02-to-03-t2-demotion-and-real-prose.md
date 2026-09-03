# 2026-09-02 → 03 — T2 demoted, last Error-B closed, first contact with real prose

**Session:** `d2b27b1f` (continued from the α2 close) · **Branch:** `agent-assure-calibration-run`
**Suite at close:** 489 passed, 2 skipped, 9 xfailed.

## What

Four rulings from Sai unblocked the cohort; six code changes landed; two
measurement runs failed instructively; the last known Error-B closed.

| | Before | After |
|---|---|---|
| Error-A (honest claim flagged) | 0.200 | **0.320** |
| Error-B (fabrication certified) | 0.111 | **0.000** |
| `lex_tau` | 0.76 | **retired** |
| Decomposition artifacts, real prose | 31.3% | **3.2%** |

## Why

OI-MOAT-21 was the open question: T2 (content-word F1) alone certified claims.
Matched-pair measurement settled it — a true and a false claim can be the SAME
one-token delta against the same source and score an **identical** `t2_f1`
(5 pairs, 5 ties), and a bag of words has no order (a false reordering scored
1.000). T2 was measuring vocabulary reuse, not support.

## Done

- **ADR-006 / CR-003** — T2 demoted, `lex_tau` retired (`--lex-tau` now raises),
  `tier_sensitive` always False. Exact-containment T1 added because demotion
  ALONE broke the gate's own end-to-end fixture: 31/52 gold claims are under
  T1's 8-token floor, and a claim quoting its source word-for-word read
  UNGROUNDED. Quote-mining guard (`_span_is_hedged`) red-teamed.
- **CR-004 / D-15** — absence SCOPE rule. A query counts toward the two-search
  minimum only if it addresses the claim's scope. Closed q14/q37.
- **OI-DEC-01** — sentence-final citations propagate to conjunction and
  semicolon clauses (Sai-ratified, PASS-enabling, red-team gated).
- **D-17…D-20** — HTML comments stripped, splitter punctuation, zero-content
  NON_CLAIM, `_content_words` requires an alphanumeric character.
- **Second-reader review page rebuilt** after the original artifact was deleted.

## Decisions

Sai ratified the Escalation-#1 reading (reversibility, not importance) and the
14-row register. Approved: demote T2, build T3 after it, fix OI-DEC-01.
Autonomous under the standing order: D-15…D-20, all fail-closed, all with undo.

## Agents

3 dispatched (1 Opus adversarial challenge, 2 Sonnet measurement), ~422K
subagent tokens, 151 tool calls. **The Opus challenge refuted my conclusion and
was itself refuted on trace** — it recommended the coverage repair, which
rejects honest synonyms and fabrications identically and leaves reordering open.
Both measurement agents produced unusable headline numbers and one genuinely
valuable second-order finding each.

## Withdrawals

1. **"Demotion costs Error-A 0.360"** — wrong. Naive counting; the correct
   held-out figure is 0.320. The challenge caught it and I re-derived it.
2. **"Both options collapse to the same truth"** — wrong. The coverage repair
   leaves reordering open; demotion does not. They are not equivalent.
3. **"31% of real-prose claims are decomposition artifacts"** — overstated.
   ~9.7 points of that was my own metric counting short-but-real sentences
   ("Silence is a decision.") as fragments. The real figure was nearer 21%.
4. **"Defer T3"** — reversed. It is the only thing that can separate a synonym
   substitution from an argument substitution.
5. **Two base-rate numbers (10.1%, 1.2%/14.3%)** — both retracted as
   unmeasurable on this corpus. Neither should be quoted.

## Reflection

Three times this session an instrument was blind to exactly the case that would
have decided the question, and each time the number it produced looked
reasonable. The n=52 corpus could not see the coverage repair fail, because it
holds zero honest synonym rows — the only case that repair breaks. The Error-A
harness could not see T2 change, because every honest draft in it was
T1-grounded. And the base-rate probe discarded heavily-paraphrased claims as
"unrelated", which is the population it existed to count.

The pattern is the same each time: **the filter and the measurement were the
same operation.** What broke each one was not more analysis but building the
missing case — and the tell, in hindsight, was always a suspiciously clean
number (zero synonym-shaped claims found; a tripwire going quiet). This is the
product's own thesis aimed inward, and it is the strongest argument for the
second labeller: a self-check cannot reach an assumption it did not know it was
making.

**HQ INS-160 (shared single-insertion-point files) does not fire here** — this
repo is single-lane with no concurrent PRs, so its registers manufacture no
conflicts. Re-evaluate if a second lane ever opens.

## Next

`RESUME-HERE.md` and `docs/jobs/REGISTER.md`. Five items are Sai's; the second
blind labeller is the one that matters.
