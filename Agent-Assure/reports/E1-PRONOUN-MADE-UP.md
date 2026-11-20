# E1 — pronoun and demonstrative phrasal falsity, 2026-11-21

**Scope and authority.** Sai's AGREED C1, D-119/D-120, authorizes fail-closed changes only. E1 is Class S: traceable source text disowned by its source, a disclosed ADR-008 limitation. This is a refusal improvement, not a change to the PASS promise.

**Systemic rule.** A separate E1 reading identifies `_UP_FALSITY_VERBS` and make/makes/made/making with `up` and a demonstrative/pronoun or content object, including split objects; passive demonstrative subjects include all of it and the whole thing. It ORs same-sentence, adjacent-sentence and same-paragraph refusals onto the unchanged main and R40 verdicts. Existing made-up complement exemptions apply. This cannot remove a main or R40 refusal: the existing verdicts remain the first two OR operands. R42's main-path digest is unchanged; its structural guard now also pins the second operand to the R40 verdict, so no re-pin was needed.

**Proven red.** With `git show origin/main:Agent-Assure/scripts/ground_check.py > /tmp/e1-main-ground-check.py`, then `E1_GATE_PATH=/tmp/e1-main-ground-check.py .venv/bin/python -m pytest -q tests/red_team_moat/test_moat_e1_pronoun_made_up.py`, main returned exit 1: **34 failed, 6 passed**. The failures comprise all 24 requested phrase × distance × direction cases, eight additional predicate/referent cases and both same-sentence cases. The six passing cases are the already-refused forward-colon example and five honest controls, which are not supposed to fail on main. On the changed gate the E1 file plus R42 structural guard returned exit 0: **44 passed**.

**Measurements.** All runners executed from `Agent-Assure/` with the project `.venv/bin/python`; baseline was main d8c2ec0. Both fabrication corpora had no class rise in escaped or certified counts.

Full suite: main **1427 passed, 2 skipped, 74 xfailed**; final **1467 passed, 2 skipped, 74 xfailed**, both exit 0. The final count includes 40 E1 cases; the structural assertion strengthens an existing test.

| Instrument | Main | E1 |
|---|---:|---:|
| Fabrication v1: escaped / certified, 280 drafts | 11 / 7 | 5 / 5 |
| v1 denied_2back escaped / certified | 3 / 1 | 0 / 0 |
| v1 denied_3plus_back escaped / certified | 3 / 1 | 0 / 0 |
| v1 honest control drafts passing | 190 / 280 | 189 / 280 |
| Fabrication v2: escaped / certified, 224 drafts | 0 / 0 | 0 / 0 |
| v2 honest controls passing | 93 / 224 | 93 / 224 |
| Honest corpus grounded claims; passing drafts | 2044 / 3990; 5 / 336 | 2044 / 3990; 5 / 336 |
| Usage genres grounded segments; passing drafts | 61 / 200; 4 / 40 | 61 / 200; 4 / 40 |

Every honest-corpus claim was compared by draft and position: **none lost**. The one lost v1 control is `howto_code_14_denied_3plus_back`: “The command prints one line for each file it handles [S1].” It changes GROUNDED → UNGROUNDED and the draft PASS → NEEDS_WORK because the unrelated denial is the next sentence across a paragraph break. Its other two claims remain GROUNDED. Usage-genres output is identical before and after. The 2 v1 certified cases lost are not the six escapes: four were already blocked by other claims. The five remaining v1 certified cases are claim headings, outside E1.

**CEILING.** Pronouns can refer to unrelated real objects or events; the next-sentence rule crosses paragraph breaks and can refuse honest claims, as measured above. Earlier denials may point backward rather than forward. The predicate is lexical, not a parser: unlisted inflections, intervening modifiers, non-listed euphemisms and references outside the existing paragraph/adjacency windows remain open. The E1 reading does not add R40's extended comparison-copy normalization; obfuscated words may escape. Unrelated R45/R46 families, including heading claims and other denial vocabulary, remain open. Paragraph scanning currently compares sentences pairwise; long source performance is not separately benchmarked.

Calibration, including the pre-existing stale checked-in features, is recorded in CR-014. A zero change on a corpus does not establish safety beyond its examples.
