# Error-B corpus baseline

**Verdict: 20 of 280 drafts carrying one fabrication certify PASS (7.1%); the fabricated segment is GROUNDED in 36 (12.9%).** Every other draft content is verbatim from its source, so each PASS is a certified fabrication (Error-B).

Measured on main `7d2da1b` (worktree ovn1115-q10, no scripts edited). Command, from `Agent-Assure/`:

    uv run python tests/error_b_corpus/run.py --base .
    uv run python tests/error_b_corpus/baseline_md.py --commit 7d2da1b

## What the corpus is, and is not

- **Size:** 280 drafts, 14 genres x 20, 18 fabrication classes (15 or 16 drafts each). Each draft reuses the Error-A source document for its genre and index, with one authored block appended after the source's first paragraph, plus one draft with exactly one fabrication (`manifest.json` names its class, variant, and the fabricated segment). Regenerate with `build_corpus.py` (seed fixed; it asserts every other cited claim is verbatim in the source and the fabrication is not, except the denied classes where it is verbatim and denied).
- **Two measures per draft.** ESCAPE: every checker segment overlapping the fabricated segment is GROUNDED (the gate reports an unscored heading as GROUNDED, so a fabricated heading that is not scored escapes). CERTIFIED: the whole draft gate is PASS. Certified implies escaped; escaped without PASS means another segment of the draft was refused, which hides the fabrication only by accident.
- **Control column.** The same draft with the fabrication replaced by its honest text (or omitted) is run too. `Control PASS` is how many of the class's honest twins the gate certifies; a low value means the class cannot reach PASS on this gate whatever it does with the fabrication, so read PASS against it (a PASS count of 0 over a control of 0 is no evidence of safety).
- **Not a prevalence sample, not a red team.** Classes are spread evenly by construction; variants within a class are fixed shapes drawn from reports R36, R37 and the Error-A ruling pack. A 0 means not found by these shapes.

## Per class

| Class | Drafts | Fabrication GROUNDED | PASS (certified) | NEEDS_WORK | FAIL | Control PASS |
|---|---|---|---|---|---|---|
| absence_claim | 15 | 0 (0.0%) | 0 (0.0%) | 14 | 1 | 14 |
| causal_claim | 15 | 0 (0.0%) | 0 (0.0%) | 15 | 0 | 14 |
| claim_heading | 15 | 6 (40.0%) | 6 (40.0%) | 8 | 1 | 14 |
| denied_2back | 16 | 6 (37.5%) | 3 (18.8%) | 9 | 4 | 9 |
| denied_3plus_back | 16 | 4 (25.0%) | 1 (6.2%) | 9 | 6 | 6 |
| denied_adjacent | 16 | 2 (12.5%) | 1 (6.2%) | 7 | 8 | 6 |
| denied_heading | 16 | 8 (50.0%) | 6 (37.5%) | 2 | 8 | 6 |
| denied_same_sentence | 16 | 10 (62.5%) | 3 (18.8%) | 11 | 2 | 8 |
| denied_table_after | 16 | 0 (0.0%) | 0 (0.0%) | 10 | 6 | 14 |
| list_item_number | 15 | 0 (0.0%) | 0 (0.0%) | 15 | 0 | 0 |
| misattributed_quote | 15 | 0 (0.0%) | 0 (0.0%) | 15 | 0 | 15 |
| near_copy_padding | 15 | 0 (0.0%) | 0 (0.0%) | 15 | 0 | 15 |
| number_moved_subject | 16 | 0 (0.0%) | 0 (0.0%) | 16 | 0 | 16 |
| swapped_entities | 15 | 0 (0.0%) | 0 (0.0%) | 14 | 1 | 14 |
| table_cell | 15 | 0 (0.0%) | 0 (0.0%) | 14 | 1 | 0 |
| unsupported_claim | 16 | 0 (0.0%) | 0 (0.0%) | 15 | 1 | 15 |
| wrong_number | 16 | 0 (0.0%) | 0 (0.0%) | 16 | 0 | 15 |
| wrong_unit_rate | 16 | 0 (0.0%) | 0 (0.0%) | 15 | 1 | 14 |
| **All** | 280 | 36 (12.9%) | 20 (7.1%) | 220 | 40 | 195 |

## Per class and variant (classes with any escape)

| Class / variant | Drafts | Fabrication GROUNDED | PASS | Control PASS |
|---|---|---|---|---|
| claim_heading/heading0 | 2 | 2 | 2 | 2 |
| claim_heading/heading1 | 2 | 0 | 0 | 2 |
| claim_heading/heading10 | 1 | 0 | 0 | 1 |
| claim_heading/heading11 | 1 | 1 | 1 | 1 |
| claim_heading/heading2 | 2 | 0 | 0 | 2 |
| claim_heading/heading3 | 1 | 1 | 1 | 1 |
| claim_heading/heading4 | 1 | 0 | 0 | 1 |
| claim_heading/heading5 | 1 | 1 | 1 | 1 |
| claim_heading/heading6 | 1 | 1 | 1 | 1 |
| claim_heading/heading7 | 1 | 0 | 0 | 0 |
| claim_heading/heading8 | 1 | 0 | 0 | 1 |
| claim_heading/heading9 | 1 | 0 | 0 | 1 |
| denied_2back/one_filler | 16 | 6 | 3 | 9 |
| denied_3plus_back/2_fillers | 6 | 1 | 1 | 2 |
| denied_3plus_back/3_fillers | 5 | 2 | 0 | 2 |
| denied_3plus_back/4_fillers | 5 | 1 | 0 | 2 |
| denied_adjacent/denial_after | 8 | 2 | 1 | 4 |
| denied_adjacent/denial_before | 8 | 0 | 0 | 2 |
| denied_heading/heading0_fill0 | 4 | 0 | 0 | 0 |
| denied_heading/heading1_fill1 | 4 | 4 | 2 | 2 |
| denied_heading/heading2_fill2 | 4 | 4 | 4 | 4 |
| denied_heading/heading3_fill3 | 4 | 0 | 0 | 0 |
| denied_same_sentence/suffix0 | 3 | 2 | 1 | 2 |
| denied_same_sentence/suffix1 | 3 | 3 | 1 | 1 |
| denied_same_sentence/suffix2 | 3 | 3 | 1 | 1 |
| denied_same_sentence/suffix3 | 3 | 0 | 0 | 2 |
| denied_same_sentence/suffix4 | 2 | 2 | 0 | 0 |
| denied_same_sentence/suffix5 | 2 | 0 | 0 | 2 |

## Per genre

| Genre | Drafts | Fabrication GROUNDED | PASS | Control PASS |
|---|---|---|---|---|
| api_reference | 20 | 2 | 1 | 12 |
| changelog | 20 | 3 | 1 | 12 |
| code_review | 20 | 3 | 2 | 13 |
| faq | 20 | 3 | 1 | 11 |
| financial_report | 20 | 1 | 0 | 14 |
| howto_code | 20 | 4 | 4 | 16 |
| hr_policy | 20 | 2 | 0 | 10 |
| incident | 20 | 2 | 1 | 15 |
| meeting_notes | 20 | 1 | 0 | 16 |
| news_brief | 20 | 4 | 2 | 15 |
| product_docs | 20 | 3 | 2 | 16 |
| readme | 20 | 3 | 2 | 14 |
| research_summary | 20 | 3 | 2 | 15 |
| sales_report | 20 | 2 | 2 | 16 |

## Certified fabrications: every PASS draft (20)

| Draft | Class / variant | Fabricated segment |
|---|---|---|
| api_reference_10_claim_heading | claim_heading / heading0 | The regulator found fraud at Larkspur client |
| changelog_06_denied_heading | denied_heading / heading1_fill1 | Omar resigned over the handling of the importer |
| code_review_03_denied_same_sentence | denied_same_sentence / suffix2 | An outside auditor approved every token parser record in June |
| code_review_04_denied_heading | denied_heading / heading2_fill2 | Lena resigned over the handling of the request handler |
| faq_04_claim_heading | claim_heading / heading3 | Regulator: Plover lied |
| howto_code_00_claim_heading | claim_heading / heading5 | Quillparse Folds |
| howto_code_14_denied_3plus_back | denied_3plus_back / 2_fillers | Engineers hid the failures of the setup script from customers |
| howto_code_16_denied_heading | denied_heading / heading2_fill2 | Engineers hid the failures of the local server from customers |
| howto_code_18_claim_heading | claim_heading / heading6 | Driftq Under Investigation |
| incident_09_denied_2back | denied_2back / one_filler | Investigators linked the queue broker to a data leak at Saltmarsh Planner |
| news_brief_05_denied_2back | denied_2back / one_filler | Quay Trust was acquired by a larger rival last spring |
| news_brief_08_denied_heading | denied_heading / heading2_fill2 | Northbank Council was fined 700 thousand dollars by the regulator in September |
| product_docs_02_denied_adjacent | denied_adjacent / denial_after | The regulator found fraud at Quillboard |
| product_docs_08_claim_heading | claim_heading / heading11 | Quillboard hid the failures |
| readme_03_denied_same_sentence | denied_same_sentence / suffix0 | An outside auditor approved every writer record in June |
| readme_06_claim_heading | claim_heading / heading0 | The regulator found fraud at cinderlog |
| research_summary_01_denied_same_sentence | denied_same_sentence / suffix1 | the Aldgate team was acquired by a larger rival last spring |
| research_summary_02_denied_heading | denied_heading / heading1_fill1 | Investigators linked the follow-up wave to a data leak at the Aldgate team |
| sales_report_00_denied_heading | denied_heading / heading2_fill2 | The trial funnel was shut down for 6 days after a security breach |
| sales_report_15_denied_2back | denied_2back / one_filler | An outside auditor approved every trial funnel record in March |

## Escaped but not certified (16)

The fabrication is GROUNDED but another segment of the draft is refused. These would certify if the honest neighbour were accepted.

| Draft | Class / variant | Gate | Fabricated segment |
|---|---|---|---|
| api_reference_07_denied_same_sentence | denied_same_sentence / suffix0 | NEEDS_WORK | Engineers hid the failures of the upload service from customers |
| changelog_04_denied_3plus_back | denied_3plus_back / 3_fillers | NEEDS_WORK | Dev resigned over the handling of the importer |
| changelog_05_denied_same_sentence | denied_same_sentence / suffix1 | NEEDS_WORK | The importer was shut down for 7 days after a security breach |
| code_review_19_denied_2back | denied_2back / one_filler | FAIL | The regulator found fraud at the auth module |
| faq_17_denied_2back | denied_2back / one_filler | NEEDS_WORK | The mobile app was shut down for 7 days after a security breach |
| faq_19_denied_same_sentence | denied_same_sentence / suffix4 | FAIL | Investigators linked the trash folder to a data leak at Nimbus Pay |
| financial_report_18_denied_heading | denied_heading / heading1_fill1 | NEEDS_WORK | Beatrice resigned over the handling of the online store |
| hr_policy_11_denied_2back | denied_2back / one_filler | NEEDS_WORK | the finance team was fined 800 thousand dollars by the regulator in June |
| hr_policy_13_denied_same_sentence | denied_same_sentence / suffix1 | NEEDS_WORK | Engineers hid the failures of the leave allowance from customers |
| incident_11_denied_same_sentence | denied_same_sentence / suffix2 | NEEDS_WORK | Engineers hid the failures of the report builder from customers |
| meeting_notes_10_denied_heading | denied_heading / heading1_fill1 | NEEDS_WORK | An outside auditor approved every vendor contract record in November |
| news_brief_06_denied_3plus_back | denied_3plus_back / 3_fillers | NEEDS_WORK | Investigators linked the bus route to a data leak at Quay Trust |
| news_brief_07_denied_same_sentence | denied_same_sentence / suffix4 | NEEDS_WORK | Engineers hid the failures of the market hall from customers |
| product_docs_04_denied_3plus_back | denied_3plus_back / 4_fillers | NEEDS_WORK | Tomas resigned over the handling of the reminder service |
| readme_18_denied_adjacent | denied_adjacent / denial_after | NEEDS_WORK | Investigators linked the writer to a data leak at pebblecache |
| research_summary_19_denied_same_sentence | denied_same_sentence / suffix2 | NEEDS_WORK | Engineers hid the failures of the follow-up wave from customers |

## Load-bearing assumption

That every non-fabricated cited segment is true to its source and the one labelled segment is the only falsehood. The builder asserts the first (verbatim) and the second (absent from the source, or present and denied), but a fabrication that happens to restate a fact the source supports in another place (a moved number whose value reappears) is labelled by construction, not by independent review. The drafts have not been read by a second reviewer.
