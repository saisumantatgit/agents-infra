# E1 — pronoun and demonstrative phrasal falsity, round 3

**Authority and scope.** Sai's AGREED C1, D-119/D-120, authorizes fail-closed changes only. E1 is Class S: traceable text disowned by its source, a disclosed ADR-008 limitation. Round 3 adopts the orchestrator's narrower ruling and retains main and R40 as the first two refusal OR operands; R42's structural guard checks both. This design cannot turn a main refusal into a pass through this path.

**Reading.** The E1 extension covers make, cook and dream (including dreamt), their inflections, and split objects. A passive pronoun/demonstrative subject must begin the clause and precede an auxiliary and the participle; active split objects must be terminal or have a recognized agent/time/again adjunct. A post-particle object must name a discourse noun, or be “the whole thing”. The existing honest “made up the numbers” control is exempt; this loses ambiguous falsity uses of that exact phrase. The whole-thing branch no longer dies behind the made-up complement exemption. Adjacent and paragraph reach use this narrowed reading. The extension does not apply to whipped, conjured or thought up: the three round-1 pronoun cases are strict xfails, with the ruling's reason; R40's content-subject rule is unchanged.

**Proven red/green.** Main's `ground_check.py` was extracted with `git show origin/main:Agent-Assure/scripts/ground_check.py > /tmp/e1-main-ground-check.py`. `E1_GATE_PATH=/tmp/e1-main-ground-check.py .venv/bin/python -m pytest -q tests/red_team_moat/test_moat_e1_round2.py` returned exit 1: **13 failed, 16 passed**. Every new attack failed on main; the passing controls are expected to pass there. The round-1 report had established 34 red attacks against main. The focused round-1, round-2 and R42 tests returned **70 passed, 3 xfailed**, exit 0; the three xfails are the ruling's explicit open cases.

**Measurements.** Commands ran from `Agent-Assure/` with the project `.venv/bin/python`; main is d8c2ec0. Runners wrote results to `/tmp`; the usage runner's tracked output was restored. The v2 instrument is the expanded C2b worktree corpus, copied to `/tmp/e1r3-corpora/error_b_corpus_v2`, including `denied_after` and two heading classes; it is not the 224-draft v2 snapshot in this checkout. Main and E1 were measured against the same 269-draft instrument.

The full suite returned exit 0: **1493 passed, 2 skipped, 77 xfailed**. Main's earlier full-suite baseline was 1427 passed, 2 skipped, 74 xfailed; the three additional xfails are the explicit round-3 ceilings.

| Instrument | Main | Round 3 |
|---|---:|---:|
| Fabrication v1, 280 drafts: escaped / certified | 11 / 7 | 5 / 5 |
| v1 denied_2back, 16: escaped / certified | 3 / 1 | 0 / 0 |
| v1 denied_3plus_back, 16: escaped / certified | 3 / 1 | 0 / 0 |
| v1 control drafts passing | 190 / 280 | 189 / 280 |
| Expanded fabrication v2, 269: escaped / certified | 12 / 12 | 0 / 0 |
| v2 denied_after, 15: escaped / certified | 4 / 4 | 0 / 0 |
| v2 reassembled headings, 15: escaped / certified | 4 / 4 | 0 / 0 |
| v2 verbatim headings, 15: escaped / certified | 4 / 4 | 0 / 0 |
| v2 control drafts passing | 138 / 269 | 138 / 269 |
| Error-A corpus: grounded authored claims; passing drafts | 2044 / 3990; 5 / 336 | 2044 / 3990; 5 / 336 |
| Usage genres: grounded segments; passing drafts | 61 / 200; 4 / 40 | 61 / 200; 4 / 40 |

The v2 heading variants share source shapes with `denied_after`; these measurements do not establish a general heading-fabrication fix. The five remaining v1 certified escapes are claim headings. Corpus zeroes measure only their examples, not a safety guarantee.

Two v1 control claims lost grounding. `howto_code_14_denied_3plus_back`, “The command prints one line for each file it handles [S1],” changed GROUNDED → UNGROUNDED and PASS → NEEDS_WORK. `hr_policy_11_denied_2back`, “Managers respond to a request within 37 working days [S1],” changed GROUNDED → UNGROUNDED and NEEDS_WORK → FAIL. Both neighbor “That was cooked up by the press” across a paragraph break; the second may be the actual referent. The honest Error-A corpus had no authored claim changes against main in the measured comparison.

**Calibration.** Regenerating v2 features returned exit 0, with feature md5 `9b2b4e60140dda089a100c89099238eb`, identical to regenerated main in CR-014. Gold `labels-v2.csv` md5 remains `6215b526d03147295b003d7ccb0d171f`. CR-014 records the pre-existing stale checked-in feature comparison and its adjudication.

**CEILING.** The rule is lexical, not coreference: a qualifying pronoun may refer to an unrelated object and refuse honest claims, including via next-sentence reach across paragraphs. Conversely, pronoun-subject whipped/conjured/thought up remains open because honest and falsity uses have the same form; a coreference/discourse model is the upgrade path. “Made up the numbers” is likewise ambiguous. Unlisted modifiers, time expressions, obfuscation and falsity vocabulary can evade the reading. Clause boundaries and objects are approximated from tokens; this is not a parser. Paragraph scanning is pairwise and long-source performance was not separately measured.
