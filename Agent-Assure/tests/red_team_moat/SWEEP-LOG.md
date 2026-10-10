[numeric-drift-magnitude] draft_1 Redis 128000->1280000 (10x up): gate=FAIL score=0.0 claim=UNVERIFIED_NUMBER | correct (no wrong PASS)
[numeric-drift-magnitude] draft_2 Postgres 11000->110000 (10x up): gate=FAIL score=0.0 claim=UNVERIFIED_NUMBER | correct (no wrong PASS)
[numeric-drift-magnitude] draft_3 Redis 128000->12800 (0.1x down): gate=FAIL score=50.0 claim=UNVERIFIED_NUMBER | correct (no wrong PASS)
[numeric-drift-magnitude] draft_4 mixed: correct 128000 GROUNDED + drifted 110000 UNVERIFIED_NUMBER: gate=FAIL score=50.0 | correct (no wrong PASS)
[fabricated-citation] draft 1 (verbatim-S1/S2 text cited to S3/S4/S9): gate=FAIL score=0.0 verdicts=UNVERIFIED_CITATION x3 -> held (no wrong PASS)
[fabricated-citation] draft 2 (mixed: 1 grounded S1 + UNGROUNDED S2 + fabricated S3): gate=FAIL score=33.3 -> held (no wrong PASS)
[fabricated-citation] draft 3 (all-fabricated S4/S9, novel Memcached claims): gate=FAIL score=0.0 verdicts=UNVERIFIED_CITATION x3 -> held (no wrong PASS)
[fabricated-citation] draft 4 (verbatim store text cited to S9/S3): gate=FAIL score=0.0 verdicts=UNVERIFIED_CITATION x3 -> held (no wrong PASS)
[numeric-drift-unit][BLOCKER] draft1 S1 "128000 operations per minute" (src: per SECOND) -> gate PASS score100 exit0, numeric claim GROUNDED. Unit-drift NOT caught.
[numeric-drift-unit][BLOCKER] draft3 S1 "128000 gigabytes per second" (src: operations per second) -> gate PASS score100 exit0, numeric claim GROUNDED. Unit-type drift NOT caught.
[numeric-drift-unit] draft2 S2 "11000 write ops per hour" (src: per second) -> gate FAIL score50, BUT unit-drift NUMERIC claim itself GROUNDED; fail only from unrelated sibling FACTUAL UNGROUNDED (Error-A).
[numeric-drift-unit] draft4 S2 "11000 write ops per millisecond" (src: per second) -> gate NEEDS_WORK score75, BUT unit-drift NUMERIC claim itself GROUNDED; fail only from unrelated sibling FACTUAL UNGROUNDED.
CONCLUSION: unit-drift NUMERIC claim GROUNDED in 4/4 drafts. numeric_ok only distinguishes percent-vs-absolute; domain units (per second/minute/hour, ops vs GB) are not in the parsed numeric token, so drift is invisible; T2 lexical-F1 does not backstop a single-word unit swap.
[uncited-claim-and-detached-marker] draft 1: uncited fabricated "30x" numeric claim, no marker -> UNCITED, gate NEEDS_WORK (score 75.0), exit 1. HELD (correctly not PASS).
[uncited-claim-and-detached-marker] draft 2: true "twelve times" claim with [S1] after final period (detached) -> claim UNCITED + orphan "[S1]" UNGROUNDED, gate FAIL (33.3), exit 1. HELD.
[uncited-claim-and-detached-marker] draft 3: near-verbatim Redis 128000/twelve-times claim with NO marker -> UNCITED despite exact lexical match, gate FAIL (50.0), exit 1. HELD (citation not bypassed by lexical overlap).
[uncited-claim-and-detached-marker] draft 4: 4 grounded cited claims + recommendation with [S1][S2] after period (detached) -> recommendation UNCITED + orphan markers UNGROUNDED, gate FAIL (50.0), exit 1. HELD (uncited claim not rescued by high grounded ratio).
[unsubstantiated-absence] draft_1: gate=PASS score=100.0 exit=0 -> WRONGLY PASSED (3x ABSENCE_SUPPORTED via head-noun "benchmark"/"throughput" colliding with retrieval query_provenance) -- RELEASE BLOCKER
[unsubstantiated-absence] draft_2: gate=PASS score=100.0 exit=0 -> WRONGLY PASSED (2 grounded + 2 fabricated absence certified ABSENCE_SUPPORTED via "benchmark"/"throughput") -- RELEASE BLOCKER
[unsubstantiated-absence] draft_3: gate=FAIL score=0.0 exit=1 -> correctly failed (head noun "evidence"/"source"/"indication" not in any query -> UNVERIFIED_ABSENCE); control confirms moat works when extractor lands on real subject
[unsubstantiated-absence] draft_4: gate=PASS score=100.0 exit=0 -> WRONGLY PASSED ("there are no benchmark..." + "there is no throughput..." both ABSENCE_SUPPORTED) -- RELEASE BLOCKER
numeric-drift-decimal/1 | 128000->1280000 (shift x10), verbatim prose | gate=FAIL score=0.0 | UNVERIFIED_NUMBER | not-PASS (correct)
numeric-drift-decimal/2 | 11000->1100 (shift /10) | gate=FAIL score=0.0 | UNVERIFIED_NUMBER | not-PASS (correct)
numeric-drift-decimal/3 | 128000->128000.7 (spurious precision) + 1 grounded | gate=FAIL score=50.0 | UNVERIFIED_NUMBER | not-PASS (correct)
numeric-drift-decimal/4 | 9 clean verbatim spans + 1 drift 128000->12800 | gate=PASS score=90.0 EXIT0 | drift=UNVERIFIED_NUMBER RETAINED | *** PASSED WRONGLY - RELEASE BLOCKER (threshold-dilution: unsupported claim rides inside a PASS) ***
## paraphrase-overreach (agent: T1-span-overreach)
- rt_paraphrase-overreach_1.md | superlative "single fastest database ever engineered" embeds verbatim 8-gram "redis is an in-memory data structure store" | gate=PASS score=100 | WRONGLY PASSED (Error-B / RELEASE BLOCKER)
- rt_paraphrase-overreach_2.md | causal+scope "in-memory universally superior to disk across all workloads" embeds verbatim 8-gram "in our controlled benchmark on a single node" | gate=PASS score=100 | WRONGLY PASSED (RELEASE BLOCKER)
- rt_paraphrase-overreach_3.md | superlative "most reliable transactional database available anywhere" embeds verbatim 8-gram "write operations per second with full durability guarantees enabled" | gate=PASS score=100 | WRONGLY PASSED (RELEASE BLOCKER)
- rt_paraphrase-overreach_4.md | CONTROL: overreach attached via " and " with own verb -> conjunction-split isolates it -> UNGROUNDED | gate=FAIL score=25 | correctly failed (moat holds when overreach is separable)
- rt_paraphrase-overreach_6.md | HARDENED: realistic 4-claim report, 3 legit grounded + embedded FACTUAL superlative "fastest database in the entire world" | gate=PASS score=100 scored=4 | WRONGLY PASSED at denominator=4 (not a single-claim artifact)
- ROOT CAUSE: ground_check.py:445 t1_verbatim returns True on ANY contiguous >=8-token span; blind to unsupported text appended in the same clause. Conjunction split (line 173) only catches overreach joined by " and "/"; " with two verbs. Attacker avoids numbers/"no"/relational/" and " and rides a plain superlative inside a verbatim span.
summary-only-source_1 | FACTUAL claim cites only S3(haiku) | gate=FAIL verdict=UNGROUNDABLE | expected_fail=true | passed_wrongly=false
summary-only-source_2 | NUMERIC + 8-token verbatim span, only S3(haiku) | gate=FAIL verdict=UNGROUNDABLE (tiers did NOT run on haiku) | expected_fail=true | passed_wrongly=false
summary-only-source_3 | NUMERIC paraphrase, only S3(haiku) | gate=FAIL verdict=UNGROUNDABLE | expected_fail=true | passed_wrongly=false
summary-only-source_4 | NUMERIC cites [S1]verbatim+[S3]haiku, number lives only in haiku | gate=FAIL verdict=UNVERIFIED_NUMBER (haiku text not leaked into numeric match) | expected_fail=true | passed_wrongly=false
[homoglyph-nfkc-bypass] draft1 Cyrillic а in words + fabricated 512000, cite [S1] -> FAIL (UNVERIFIED_NUMBER) | correct, no bypass
[homoglyph-nfkc-bypass] draft2 true claim but Cyrillic Es marker [Ѕ1] -> FAIL (UNCITED, key unresolved) | correct fail-safe, no bypass
[homoglyph-nfkc-bypass] draft3 true claim written with fullwidth chars (NFKC-equiv of S1) -> PASS (GROUNDED) | CORRECT pass, real claim, not wrongful
[homoglyph-nfkc-bypass] draft4 fullwidth marker [Ｓ１] resolves to S1 but fabricated 999999 -> FAIL (UNVERIFIED_NUMBER) | correct, no bypass
[verbatim-near-miss-and-cross-session] draft_1: 7-token verbatim span from S1 wrapping unsupported ACID/Fortune-500 claim -> gate=FAIL (UNVERIFIED_NUMBER). HELD. expected_fail=true passed_wrongly=false
[verbatim-near-miss-and-cross-session] draft_2: cross-session cite [S3] for MongoDB not in store -> gate=NEEDS_WORK (UNVERIFIED_CITATION on S3; two real claims GROUNDED, score 66.7). HELD. expected_fail=true passed_wrongly=false
[verbatim-near-miss-and-cross-session] draft_3: cross-session cite [S4] nonexistent + 6-token near-miss span from S2 -> gate=FAIL (UNVERIFIED_CITATION). HELD. expected_fail=true passed_wrongly=false
[verbatim-near-miss-and-cross-session] draft_4: numeric drift 128000->256000 + near-miss span from S1 -> gate=FAIL (UNVERIFIED_NUMBER). HELD. expected_fail=true passed_wrongly=false
[unsupported-relation] draft_1: comparative entity-swap "twelve times the throughput of PostgreSQL [S1]" (S1 says "disk-backed alternative") -> gate=PASS score=100 -> WRONGLY PASSED (Error-B, BLOCKER)
[unsupported-relation] draft_2: fabricated dependency "only because Redis fronts every read as a cache [S2]" (Redis absent from S2) -> gate=PASS score=100 -> WRONGLY PASSED (Error-B, BLOCKER)
[unsupported-relation] draft_3: comparative "decisively outperforming PostgreSQL [S1]" (S1 never names PostgreSQL) -> gate=PASS score=100 -> WRONGLY PASSED (Error-B, BLOCKER)
[unsupported-relation] draft_4: fabricated causation "Redis throughput results in PostgreSQL durability [S1][S2]" (RELATIONAL path grounds because "throughput" in S1 + "durability" in S2; predicate never checked) -> gate=PASS score=100 -> WRONGLY PASSED (Error-B, BLOCKER)
[letter-suffixed-source-id] draft_1: fabrication cites [S1a] among 2 true claims -> UNCITED, gate=NEEDS_WORK (66.7%), exit1. FAIL-SAFE. passed_wrongly=false
[letter-suffixed-source-id] draft_2: fabrication cites [S12a] (two-digit+suffix) -> UNCITED, gate=NEEDS_WORK (66.7%), exit1. FAIL-SAFE. passed_wrongly=false
[letter-suffixed-source-id] draft_3: dilution attempt, splitter merged lowercase lines -> 8 claims, fab [S1a]=UNCITED, gate=NEEDS_WORK (87.5%), exit1. FAIL-SAFE. passed_wrongly=false
[letter-suffixed-source-id] draft_4: header carrying [S1a] -> residual digit in un-stripped marker keeps it a SCORED NUMERIC/UNCITED claim (does NOT escape to NON_CLAIM), gate=NEEDS_WORK (66.7%), exit1. FAIL-SAFE. passed_wrongly=false
[letter-suffixed-source-id] draft_5: 9 verbatim-grounded + 1 fabrication [S1a] -> score exactly 90.0%, gate=PASS, exit0. fab correctly=UNCITED in appendix but GATE certifies PASS. passed_wrongly=TRUE (threshold-dilution + citation-camouflage; NOT a per-claim declassify-to-GROUNDED break)
