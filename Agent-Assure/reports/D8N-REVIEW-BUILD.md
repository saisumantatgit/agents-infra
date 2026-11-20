# D8N review build — STOPPED, not ready for PR

Branch `ovn-1121-d8n`, base `375c828`. Uncommitted prototype only; no merge, push or PR. The brief requires a stop if the design needs more than the authorized fail-closed fixes.

## Blocking conflict

The store emits one record per content block, and one fetch can emit multiple blocks with the same URL. `tests/red_team_moat/test_moat_r20_documents_stay_separate.py::test_POSITIVE_CONTROL_a_claim_inside_ONE_document_still_grounds` requires S1 to ground in precisely this case. The literal latest-record rule rejects S1 because S2 has the same URL. Records have no capture-event identity and fetched_at is a constant sentinel, so the gate cannot distinguish blocks of one capture from two separate captures. Preserving this test and enforcing latest *capture* needs capture-event provenance or an owner ruling; the brief forbids widening the design. Another fixture (`test_basis_branch_matches_the_verdict_branch`) also uses two distinct sources with the same file path and fails under the literal rule.

The prototype is **not review-ready**: the composite figure rule also rejects an existing honest 3.11 positive control when 3.9 appears elsewhere. The co-cited denial probe only matches complete claim spans, so it does not cover all denials of anchored partial matches. Do not treat these as completed fixes. No test was weakened. A pre-existing strict xfail becomes XPASS because whole spelled runs close its specific case; the marker was not changed.

## Verification of prototype

- Baseline suite: 1431 passed, 2 skipped, 74 xfailed. Prototype suite: 4 failed, 1438 passed, 2 skipped, 73 xfailed. The failures are the two controls above, `test_positive_short_genuine_source_still_grounds`, and the strict XPASS `test_a_fabricated_magnitude_spelled_with_one_is_refused`.
- Focused tests: before, 8 failed and 2 passed; after, all 10 pass. R42 structural guard: all 4 pass. These do not prove complete D8 coverage.
- Gold labels MD5 `6215b526d03147295b003d7ccb0d171f` unchanged. Live gold measurement before and after: Error-A 12/25 = 0.480; Error-B 0/27 known misses (n=52, single ratifier; 95% upper bound about 10.5%). The 52 live feature rows are identical before and after; the historical deployed 10/25 is not this checkout’s measured baseline.
- Feature regeneration versus checked-in derived artifact changed q03 GROUNDED→UNGROUNDED (gold grounded; honest attribution now refused) and q13 ABSENCE_SUPPORTED→UNVERIFIED_ABSENCE (gold grounded; checked-in artifact may predate the current absence demotion). Both differences already exist on the starting gate: live feature rows are identical before and after the prototype. The derived artifact was restored after inspection; labels were untouched.

| Corpus | Drafts | Escaped before → prototype | PASS before → prototype | Honest control PASS before → prototype |
|---|---:|---:|---:|---:|
| error_b_corpus | 280 | 11 → 11 | 7 → 7 | 190 → 183 |

error_b_corpus: no class rose in escaped or PASS count.

| error_b_corpus_v2 | 269 | 12 → 12 | 12 → 12 | 138 → 135 |

error_b_corpus_v2: no class rose in escaped or PASS count.

| error_b_corpus_v3 | 510 | 490 → 435 | 490 → 435 | 510 → 510 |

error_b_corpus_v3: no class rose in escaped or PASS count.

v3 changed classes (escaped and PASS have the same count): D8 15→0, N7 15→0, N8 15→0, N10 10→0. N11 stays 15→15; it was not implemented. v3 has 15 examples per class. These synthetic fixtures are not independently reviewed.

## Honest-claim losses

Error-A corpus: 2,044→1,950 grounded of 3,990 authored claims; PASS drafts 5→4. Each line below is one lost authored claim, including repetitions where separate locations have identical text. Verdicts are the after segments.

- `product_docs_002`: Yes — UNGROUNDED
- `product_docs_002`: Yes — UNGROUNDED
- `product_docs_002`: Yes — UNGROUNDED
- `product_docs_002`: Yes — UNGROUNDED
- `product_docs_008`: Yes — UNGROUNDED
- `product_docs_008`: Yes — UNGROUNDED
- `product_docs_008`: Yes — UNGROUNDED
- `product_docs_009`: An owner may invite 5 guests per project — UNGROUNDED
- `product_docs_009`: The Starter plan includes offline mode for up to 5 members — UNGROUNDED
- `product_docs_010`: Yes — UNGROUNDED
- `product_docs_010`: Yes — UNGROUNDED
- `product_docs_010`: Yes — UNGROUNDED
- `product_docs_014`: Yes — UNGROUNDED
- `product_docs_014`: Yes — UNGROUNDED
- `product_docs_014`: Yes — UNGROUNDED
- `product_docs_014`: Yes — UNGROUNDED
- `product_docs_020`: Yes — UNGROUNDED
- `product_docs_020`: Yes — UNGROUNDED
- `product_docs_020`: Yes — UNGROUNDED
- `readme_006`: The maintainers wrote that the old API "cannot be removed before version 2" — UNGROUNDED
- `readme_023`: The maintainers wrote that the old API "cannot be removed before version 2" — UNGROUNDED
- `incident_000`: The health check failed three times in a row — UNGROUNDED
- `incident_000`: The on-call engineer opened the dashboard — UNGROUNDED
- `incident_000`: The configuration change was rolled back — UNGROUNDED
- `incident_002`: The health check failed three times in a row — UNGROUNDED
- `incident_002`: The on-call engineer opened the dashboard — UNGROUNDED
- `incident_002`: Traffic moved to the standby region — UNGROUNDED
- `incident_004`: Error rates returned to normal — UNGROUNDED
- `incident_004`: Traffic moved to the standby region — UNGROUNDED
- `incident_004`: The health check failed three times in a row — UNGROUNDED
- `incident_006`: Traffic moved to the standby region — UNGROUNDED
- `incident_006`: The health check failed three times in a row — UNGROUNDED
- `incident_006`: The configuration change was rolled back — UNGROUNDED
- `incident_008`: Traffic moved to the standby region — UNGROUNDED
- `incident_008`: The health check failed three times in a row — UNGROUNDED
- `incident_008`: The on-call engineer opened the dashboard — UNGROUNDED
- `incident_010`: The on-call engineer opened the dashboard — UNGROUNDED
- `incident_010`: Traffic moved to the standby region — UNGROUNDED
- `incident_010`: The health check failed three times in a row — UNGROUNDED
- `incident_012`: The billing service began returning errors on Thursday at 10 minutes past the hour — UNGROUNDED
- `incident_012`: The health check failed three times in a row — UNGROUNDED
- `incident_012`: The on-call engineer opened the dashboard — UNGROUNDED
- `incident_012`: Traffic moved to the standby region — UNGROUNDED
- `incident_014`: The configuration change was rolled back — UNGROUNDED
- `incident_014`: Traffic moved to the standby region — UNGROUNDED
- `incident_014`: Error rates returned to normal — UNGROUNDED
- `incident_016`: Error rates returned to normal — UNGROUNDED
- `incident_016`: Traffic moved to the standby region — UNGROUNDED
- `incident_016`: The on-call engineer opened the dashboard — UNGROUNDED
- `incident_018`: The configuration change was rolled back — UNGROUNDED
- `incident_018`: The health check failed three times in a row — UNGROUNDED
- `incident_018`: The on-call engineer opened the dashboard — UNGROUNDED
- `incident_020`: The configuration change was rolled back — UNGROUNDED
- `incident_020`: The health check failed three times in a row — UNGROUNDED
- `incident_020`: The on-call engineer opened the dashboard — UNGROUNDED
- `incident_022`: The on-call engineer opened the dashboard — UNGROUNDED
- `incident_022`: Error rates returned to normal — UNGROUNDED
- `incident_022`: Traffic moved to the standby region — UNGROUNDED
- `meeting_notes_008`: Yes — UNGROUNDED
- `meeting_notes_008`: Yes — UNGROUNDED
- `api_reference_001`: The changelog says that the old `v1` path "is not covered by the new limits" — UNGROUNDED
- `api_reference_013`: The changelog says that the old `v1` path "is not covered by the new limits" — UNGROUNDED
- `api_reference_015`: The changelog says that the old `v1` path "is not covered by the new limits" — UNGROUNDED
- `api_reference_020`: The changelog says that the old `v1` path "is not covered by the new limits" — UNGROUNDED
- `api_reference_021`: The changelog says that the old `v1` path "is not covered by the new limits" — UNGROUNDED
- `changelog_000`: Improved the wording of 3 error messages — UNGROUNDED
- `changelog_000`: This release is made up of 3 new features and 15 fixes — UNGROUNDED, GROUNDED
- `changelog_002`: The release contains 14 commits from 7 contributors — UNGROUNDED
- `changelog_007`: The release contains 8 commits from 6 contributors — UNGROUNDED
- `changelog_013`: Improved the wording of 4 error messages — UNGROUNDED
- `changelog_013`: The release contains 20 commits from 4 contributors — UNGROUNDED
- `changelog_013`: This release is made up of 4 new features and 20 fixes — UNGROUNDED, GROUNDED
- `changelog_016`: The release contains 42 commits from 4 contributors — UNGROUNDED
- `changelog_019`: This release is made up of 6 new features and 27 fixes — UNGROUNDED, GROUNDED
- `changelog_023`: Improved the wording of 5 error messages — UNGROUNDED
- `research_summary_017`: The study ran for 3 years — UNGROUNDED
- `research_summary_022`: The paper was reviewed by 8 external readers — UNGROUNDED
- `financial_report_012`: Yes — UNGROUNDED
- `financial_report_012`: 10% — UNGROUNDED
- `financial_report_012`: Yes — UNGROUNDED
- `financial_report_012`: 10% — UNGROUNDED
- `financial_report_012`: Yes — UNGROUNDED
- `financial_report_020`: 6% — UNGROUNDED
- `sales_report_002`: False — UNGROUNDED
- `sales_report_002`: False — UNGROUNDED
- `sales_report_002`: False — UNGROUNDED
- `sales_report_008`: False — UNGROUNDED
- `sales_report_008`: False — UNGROUNDED
- `sales_report_010`: False — UNGROUNDED
- `sales_report_010`: False — UNGROUNDED
- `sales_report_012`: False — UNGROUNDED
- `sales_report_012`: False — UNGROUNDED
- `sales_report_020`: Yes — UNGROUNDED
- `sales_report_020`: Yes — UNGROUNDED

Usage genres: 91→90 GROUNDED checker segments (includes NON_CLAIM segments). Lost segment:

- `b06_bullets_copied`: - Exit codes: `0` = gate PASS, `1` = NEEDS_WORK or FAIL [S1]. — UNGROUNDED

## Next decision

Sai: decide whether capture-event identity may be added so multiple records from one retrieval remain usable while later retrievals supersede them, and how to reconcile legacy stores with no event identity. Rebuild and remeasure after that ruling; retain the R42 guard, improve denial matching and narrow composite matching before claiming completion.
