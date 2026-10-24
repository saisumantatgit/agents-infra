# 2026-10-24 → 25 — readiness: what a real writer sees, and three runs on it

**main at close of this entry:** `9f7e661` · suite **1045 passed · 2 skipped · 61
xfailed** · gold md5 `6215b526…d171f` · **Error-A 12/25 = 0.480 · Error-B 0/27** ·
no open PRs.

## What happened (PRs, all merged by Sai)
| PR | What |
|---|---|
| #11–#13, #12 | capture contract; J-97 absence advisory (Error-A 0.400→0.440) |
| #14–#18 | DDG failure text, same-sentence coverage, Read paths/extent, figure qualifiers — integrated as #18 after round 26 |
| #19 | **D-97: readiness A + B** — strict "quote your sources"; B1 negations not absence + negation-aware T1; B2 identifiers/byte units; R27-01 limiter guard (q03 price, Error-A →0.480, D-98) |
| #20 | D-98 record |
| #21 | **the guide's quoting example FAILED** — corrected; examples now RUN as a test |
| #22 (+#23) | five fail-closed residue fixes; comment citations never count; near-copy self-citation (S2, price accepted by Sai's merge) |

## The findings that mattered
1. **Usage, paraphrase (W3):** 0 of 20 honest drafts PASS; 171/177 true claims refused.
2. **B moved refusal REASONS, not the pass count** (6/177 before and after). My
   estimate that the negation fix "removes ~1 refusal in 7" was wrong — withdrawn.
3. **Usage, quoting (C1):** the guide's own example failed. A claim that IS the
   source's sentence grounds; framing ("The audit found "…"") refuses even 15-word
   quotes. Corrected advice on real docs: **prose 64%, bullets 34%**.

## Withdrawals (part of the record)
- The guide's quoting example — written without being run.
- C2 "framed quotations" — not built: an uncheckable subject is a misattribution Error-B.
- C2 "look-back stops at sentence boundary" — built, refuted by round 28 (14 flat denials let the next sentence ground), withdrawn.
- C3 fix 4 (textarea comments) — reverted after round 29; redone properly as S1.
- "~1 in 7 refusals removed by B1" — wrong; reasons moved, passes did not.

## Agents
Rounds 25–30 (Opus adversaries), W1–W5/C1 builders (Sonnet), fix agents (Opus).
Subagent tokens derived from completion records: 10-24 burst 1.49M; 10-25 overnight
~1.13M. Main loop: not measurable from this session — stated as unknown.

## Reflection
Three times in two days the instrument I trusted measured the wrong population: the
gold corpus hid the paraphrase wall (0.400 vs 97% refused), the fix-B tests hid that
refusals only changed name, and my own guide example was never run. Each time the
cure was the same — build the measurement from what a real user would DO, then read
the verdicts yourself. The adversary rounds kept the moat honest; only usage sets
kept the PRODUCT honest.

## Next (owners)
- **Sai:** the 5-user test — ask about FAIL as well as PASS; show the corrected
  quoting advice. Standing merge authority now D-100.
- **Claude:** registered residue — denials beyond 5 tokens / unlisted ("Hardly.",
  "None of that happened."); "No." beside a claim; more DDG failure texts;
  "Fallacies:/Debunked:" labels; diluted near-copies; bullets/code spans/colons in
  quoted sentences (34% bullet pass rate).
