# Brief E2: score draft headings that are not taken from a source heading (fail-closed)

Executor: Codex (or Claude Opus on Sai's word). Branch `fix-e2-headings` from main. Read repo-root
CLAUDE.md first. If this spec conflicts with the repo, STOP and say where. Authority as in E1: fail-closed only.

## The hole (main d8c2ec0, PASS 100 with a passing control)
A heading made only of source words is NON_CLAIM and never scored, so these certify PASS 100 over a
source that says "The regulator found fraud at Quay Trust. That never happened.":
`## The regulator found fraud at Quay Trust`, `## Fraud at Quay Trust`, `## Quay Trust hid the failures`,
`## Regulator: fraud at Quay Trust`, `## The council never met`. Plus 5/15 v1 claim_heading attacks
(novel-word headings that pass the existing headline tests, ground_check.py:1093-1150).

## Do (rule "S + closed label list", reports/C1-RULING-PACK-2026-11-21.md E2)
1. A draft heading (ATX # 1-6 and setext) stays NON_CLAIM only if (a) it equals, after NFKC + casefold +
   whitespace/punctuation trim, a heading in a cited/captured source, or (b) every content word is in a
   CLOSED list of structural labels (start from: overview, summary, introduction, background, notes,
   details, steps, next, known, issues, faq, questions, answers, changes, changelog, contents, appendix,
   references, sources, glossary, examples, usage, installation, setup, configuration, requirements,
   limitations, results, method, methods, discussion, conclusion, action, items). Otherwise it is scored
   like a sentence. Mark the list `CEILING:` (a claim spelled only in label words; upgrade: POS tagger).
   A missing list member must mean "scored", never "passed".
2. The refusal reason must NOT list the offending words (that is an oracle for the E2 sibling). Say: "A
   heading not taken from your sources is checked like a sentence; copy the source's heading or cite it."
3. Proven-red tests: the 5 headings above, setext variants, a heading at the end, levels 1-6; honest
   controls: a heading copied from the source's own heading; "## Overview"; "## Next steps".
4. Re-pin the r42 structural guard only if additive, say why.

## Measure
As E1, plus: honest PASS on Error-A corpus (5) + usage_genres (4) before/after (main loop measured rule S
alone at 9→2; report the list's recovery), and honest headings scored out of 532.

## Deliver
Code + tests; reports/E2-HEADINGS.md. Do not push. Final message ≤ 30 lines.
