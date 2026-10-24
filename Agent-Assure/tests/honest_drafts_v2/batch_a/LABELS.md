# Batch A labels (Agent-Assure self-description drafts, sources S1-S5)

**CANDIDATE labels by an AI agent — NOT gold; only Sai ratifies gold.**

Sources: S1 README.md, S2 grounding-failure-types.md, S3 ADR-006, S4 ADR-007, S5 CR-007. Claims are the gate's own segments (it splits some sentences at commas/conjunctions, so a draft sentence can yield two rows). Gate result per draft: all 5 FAIL, score 0.0.

| draft | claim text | candidate label | gate verdict | agree | note |
|---|---|---|---|---|---|
| 1 | Agent-Assure checks a draft's claims against an evidence store without calling any language model [S1]. | grounded | UNGROUNDED | DISAGREE |  |
| 1 | A PostToolUse hook fills that store automatically after every retrieval call, so the user does nothing while researching [S1]. | grounded | UNGROUNDED | DISAGREE |  |
| 1 | Native WebFetch output is tagged as a Haiku summary [S1] | grounded | UNGROUNDED | DISAGREE |  |
| 1 | the gate refuses to certify claims against it [S1]. | grounded | UNGROUNDED | DISAGREE |  |
| 1 | The gate returns PASS only when no claim carries a violation-class verdict [S1] | grounded | UNVERIFIED_ABSENCE | DISAGREE |  |
| 1 | the score reaches the threshold, which defaults to 90 [S1]. | grounded | UNGROUNDED | DISAGREE |  |
| 1 | Because one retained violation caps the gate, a draft cannot reach PASS merely by having most of its claims grounded [S1]. | grounded | UNGROUNDED | DISAGREE |  |
| 1 | A fabricated citation such as [S9] cannot argue its way to a pass, since the verdict is a mechanical fact about the store [S1]. | grounded | UNVERIFIED_CITATION | DISAGREE | [S9] is an illustrative example inside the claim, parsed as a real citation (artifact) |
| 2 | The grounding failure taxonomy has nine verdicts, and only GROUNDED and ABSENCE_SUPPORTED count toward the score numerator [S2]. | grounded | UNVERIFIED_NUMBER | DISAGREE | nine is the count of verdict headings in S2 (2 passing + 7 failing); derived, not stated |
| 2 | UNVERIFIED_CITATION fires when a claim cites a source_id that was never captured, which marks the citation as fabricated or pointing outside the session [S2]. | grounded | UNGROUNDED | DISAGREE |  |
| 2 | For numeric claims the value [S2] | grounded | UNGROUNDED | DISAGREE |  |
| 2 | unit must both match, so a bare 25 does not ground 25% [S2]. | grounded | UNVERIFIED_ABSENCE | DISAGREE |  |
| 2 | A claim of 128000 operations per minute is not grounded by a source that says 128000 operations per second [S2]. | grounded | UNVERIFIED_ABSENCE | DISAGREE |  |
| 2 | An absence claim needs at least two distinct queries that each contain every strong anchor of the subject plus its head noun [S2]. | grounded | UNGROUNDED | DISAGREE |  |
| 2 | Native WebFetch returns a Haiku summary rather than the original text [S2] | grounded | UNGROUNDED | DISAGREE |  |
| 2 | a summary cannot ground anything because it is a second model's paraphrase [S2]. | grounded | UNGROUNDED | DISAGREE |  |
| 3 | ADR-006 was accepted on 2026-09-02 [S3] | grounded | UNGROUNDED | DISAGREE |  |
| 3 | demoted the lexical-F1 tier (T2) so that it no longer decides any verdict [S3]. | grounded | UNVERIFIED_ABSENCE | DISAGREE |  |
| 3 | Two measurements drove it. | violation | UNCITED | AGREE | my draft left this sentence uncited; gate correct |
| 3 | In five matched pairs, a true claim [S3] | grounded | UNGROUNDED | DISAGREE |  |
| 3 | a false claim differing by one token scored an identical t2_f1 [S3]. | grounded | UNGROUNDED | DISAGREE |  |
| 3 | Reciting a source's vocabulary in a false order scored an F1 of 1.000, since a bag of words has no word order [S3]. | grounded | UNVERIFIED_ABSENCE | DISAGREE |  |
| 3 | The measured cost was that Error-A rose from 0.200 to 0.320 while Error-B fell from 0.111 to 0.074 [S3]. | grounded | UNGROUNDED | DISAGREE |  |
| 3 | Honest paraphrase therefore reads as UNGROUNDED, because only a verbatim span can now certify a claim [S3]. | grounded | UNGROUNDED | DISAGREE |  |
| 3 | The ADR names its load-bearing assumption as honest drafts quoting more often than they paraphrase, which nobody had measured on real prose [S3]. | grounded | UNGROUNDED | DISAGREE |  |
| 4 | ADR-007 demoted relational grounding to a diagnostic after round 12 of red-teaming found seven Error-B shapes in the old rule, two of them critical [S4]. | grounded | UNGROUNDED | DISAGREE |  |
| 4 | The old rule certified a causal claim from two sources that each mentioned one endpoint [S4] | grounded | UNGROUNDED | DISAGREE |  |
| 4 | an adversary who writes the document can satisfy that with token co-occurrence [S4]. | grounded | UNGROUNDED | DISAGREE |  |
| 4 | The first version let relational claims fall through to the verbatim path [S4] | grounded | UNGROUNDED | DISAGREE |  |
| 4 | priced Error-A at 0.360, but round 13 then found six new Error-B shapes, five critical, caused by that fall-through [S4]. | grounded | UNVERIFIED_RELATION | DISAGREE |  |
| 4 | The amendment therefore made a relational claim return UNVERIFIED_RELATION every time, at a price of Error-A 0.400 [S4]. | grounded | UNGROUNDED | DISAGREE |  |
| 4 | There is no remaining open relational Error-B shape after this change [S4]. | grounded | UNVERIFIED_ABSENCE | DISAGREE | S4 says relational Error-B shapes 0 after revision; later amendment C says classifier route-around J-69 still open; literal claim matches S4 body |
| 4 | A draft containing a causal sentence will usually not PASS [S1] | grounded | UNVERIFIED_ABSENCE | DISAGREE | S1 states 'a draft containing a causal sentence will usually not PASS... deliberate' |
| 4 | the README calls that deliberate [S1]. | grounded | UNGROUNDED | DISAGREE |  |
| 5 | CR-007 records the effect of the relational demotion on the n=52 gold corpus [S5]. | grounded | UNVERIFIED_NUMBER | DISAGREE |  |
| 5 | Error-A moved from 0.320 (8 of 25) to 0.400 (10 of 25), while Error-B stayed at 0.000 (0 of 27) [S5]. The two rows that changed were q12 and q36, both gold-grounded, which now return UNVERIFIED_RELATION [S5]. | grounded | UNGROUNDED | DISAGREE | two sentences merged by segmenter; both match S5 tables |
| 5 | The test suite went from 789 to 793 passing tests, with 2 skipped [S5] | grounded | UNGROUNDED | DISAGREE |  |
| 5 | 61 xfailed [S5]. | grounded | UNGROUNDED | DISAGREE |  |
| 5 | A 0.000 Error-B should not be quoted as zero, since its 95% upper bound is roughly 10.5% [S5]. | grounded | UNVERIFIED_ABSENCE | DISAGREE |  |
| 5 | The corpus understates the real-draft Error-A because it contains only 7 relational rows, whereas a research draft can be half relational [S5]. | grounded | UNGROUNDED | DISAGREE |  |
| 5 | Fall-through scored 0.360 only because q36 still certified through the verbatim path [S5] | grounded | UNGROUNDED | DISAGREE |  |
| 5 | that variant was withdrawn [S5]. | grounded | UNGROUNDED | DISAGREE |  |

Totals: 42 claims; false alarms 41; misses 0.
