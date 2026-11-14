# Agent-Assure alpha walkthrough 2 (new tester, docs only)

Setup: macOS, uv 0.12.5, clone of agents-infra at /private/tmp/claude-501/ovn1115-q7/clone. Not run: install.sh, hooks, ~/.claude. Drafts, sources, stores, reports: /private/tmp/claude-501/ovn1115-q7/work (d1-d8 original drafts, f1-f8 fixed drafts, s1-s8 sources, e*.txt explain output).
Edit = one sentence, heading or block changed or deleted.

## 1. Steps

| # | Step / command | Trimmed output | Tag | Sev |
|---|---|---|---|---|
| 1 | `git clone .../agents-infra` | 1334 files, ok | OK | - |
| 2 | Top README. Banner says "Think. Record. Shield. three-product suite"; Agent-Assure is a note under it, with a pointer to the guide | I found the pointer easily; the suite pitch is about different products | CONFUSING | low |
| 3 | `cd Agent-Assure && uv sync` | installed pytest, pyyaml, regex, syntok; .venv created | OK | - |
| 4 | README quick start: `uv run python demo/build_store.py` | `wrote .../evidence-store.jsonl (2 sources)` | OK | - |
| 5 | README: `ground_check.py ... --json > report.json; explain_report.py report.json` | `gate: FAIL | score: 50.0`; claim 3 UNVERIFIED_CITATION with fix line; claim 4 UNVERIFIED_NUMBER with fix line; heading listed "not scored". Matches README. | OK | - |
| 6 | Guide section 3 step 1: grounded demo via `demo/show_report.py` | `gate: PASS | score: 100.0`, 3x GROUNDED, exit 0 | OK | - |
| 7 | Same, fabricated demo | `gate: FAIL | score: 50.0`, UNVERIFIED_CITATION and UNVERIFIED_NUMBER, exit 1 | OK | - |
| 8 | Guide: "Check your own source": `add_source.py my-source.txt --id S1 --store ... --session-id ...` x8 | `added S1 to store1.jsonl (session_id='t1'); store re-loaded OK` | OK | - |
| 9 | Guide: `ground_check.py --draft ... --store ... --session-id` (no --json) | writes `grounding-report.yaml` into current folder. Inside the git clone it dirties the repo (I deleted it). The guide does say it writes the file, but not that it lands in the repo if you run from Agent-Assure as instructed. | CONFUSING | low |
| 10 | Guide's own advice on a verbatim claim: "UNGROUNDED -> Replace the claim with the source's own sentence" | I copied the source sentence exactly and still got UNGROUNDED 9 times (see 11-14). The fix line repeats the same advice, so the tester loops. | BUG (or WRONG-DOC) | high |
| 11 | Verbatim source sentence with a spelled number or a mid-sentence figure: "The migration moved 2.1 million customer records to the new schema in about forty minutes [S1]." Also "A standard card allows up to twenty items at one time [S1]." and "The immediate cause was an expired TLS certificate on the internal payment gateway [S1]." | UNGROUNDED, support_diagnostic `no_hedge_in_cited_sentence`, evidence_basis only says "Checked verbatim against 1 cited source". No reason is given. Neighbouring verbatim sentences pass. I could not find a rule. | BUG | high |
| 12 | Verbatim sentences with "percent": "Customer churn fell to 3.1 percent from 4.0 percent in the second quarter [S1]." and "...an increase of 9 percent over the same quarter last year [S1]." (source has the identical words) | UNVERIFIED_NUMBER; the message lists figures "3.1", "4.0", "9" (no unit) and says each must match value, unit and rate. Fix line: "Copy the figure as the source writes it" - already done. Every "N percent" sentence I tried failed (also "61 percent"). | BUG | high |
| 13 | Compound sentence copied whole: "The first retry waits five seconds, and each later retry..." | Split into 2 claims, each GROUNDED (ok). But "The default limit for a new group is four jobs, and the limit can be changed..." split, first piece UNGROUNDED, second GROUNDED. Piece text is shown, which helps. | CONFUSING | med |
| 14 | Draft with a markdown table with [S1] in each cell (guide says no documented way) | 1 claim, UNGROUNDED, "Checked verbatim against 4 cited sources: S1, S1, S1, S1" and figure "Q3" counted as a figure. Fix line is the generic one. Guide warned of this. | CONFUSING | med |
| 15 | Draft with a fenced code block (the guide does not mention code) | Code block is 1 NUMERIC claim: UNCITED without a marker, UNGROUNDED with [S1] after the fence; a verbatim copy of the source's code (marker-free) is UNCITED. No way found to PASS. Guide has nothing on code. | WRONG-DOC (gap) | high |
| 16 | Headings: "# Meeting summary" -> UNCITED; "# Meeting notes" -> UNCITED; "# Retry helper explained" -> UNCITED; "# Q3 sales summary" -> UNCITED (and NUMERIC because of "Q3"). "# Summary", "# Results", "# Incident summary", "## Limits", "## Lost cards" -> NON_CLAIM. | Guide explains label vs statement headings but two-word labels like "Meeting notes" are scored. Unpredictable; each cost me an edit. | CONFUSING | med |
| 17 | Honest sentence "No rollback was needed [S1]." | UNVERIFIED_ABSENCE (read as a "there is no X" claim). Fix line: quote or soften. Sentence is the source's own. | BUG | med |
| 18 | explain_report on GROUNDED claims | Each GROUNDED claim prints 2-6 lines of boilerplate "why". 12-claim reports are long; failing claims are hard to spot. | CONFUSING | low |
| 19 | Fabricated claim never made by source ("The mayor vetoed the parking study and promised a lawsuit...") | Split in two, both UNGROUNDED with the generic fix "Replace the claim with the source's own sentence... This is not evidence the claim is false." Caught, but the output never tells the tester it may be invented. | CONFUSING | med |
| 20 | Wrong number "9,300" vs source "3,900" | UNVERIFIED_NUMBER, names the figure "9,300". Caught and explained. | OK | - |
| 21 | Hard STALL (a step I could not continue past) | none | - | - |

Tag counts: OK 8, BUG 4, WRONG-DOC 1, CONFUSING 7, STALL 0 (step 21 is the stall check).

## 2. Drafts

Sources: each 5-6 paragraphs, 196-250 words. Honest drafts copied source sentences with [S1] before the full stop, as the guide says. Fabrications: d7 wrong number (9,300 vs 3,900 orders); d8 invented claim (mayor veto and lawsuit).

| Draft | Type | First verdict (score) | Told WHY? / HOW to fix? | Fix applied | Final | Edits |
|---|---|---|---|---|---|---|
| d1 | product note (honest) | NEEDS_WORK 85.7 | Why: no (verbatim sentence, UNGROUNDED with no reason). Fix line: generic, I had already done it. | replaced the "four jobs, and..." sentence with another source sentence | PASS 100 | 1 |
| d2 | meeting summary (honest) | FAIL 57.1 | Heading: yes (fix line points to guide). "2.1 million" sentence and "16,500" piece: no reason, generic fix. | heading -> "# Summary"; swapped 2 sentences; third swap needed because "No rollback was needed" read as absence claim | PASS 100 | 4 |
| d3 | README section (honest) | PASS 100 | n/a | none | PASS 100 | 0 |
| d4 | sales report with table (honest) | FAIL 20.0 | Table: partly (guide warned; output generic). Percent sentences: "figure not found" but figure is in source; fix line unhelpful. | heading -> "# Results"; removed both percent sentences and the table; added other source sentences | PASS 100 (content lost: table, % figures) | 4 |
| d5 | code explanation, code block (honest) | NEEDS_WORK 71.4 | Heading: yes. Code block: UNCITED, fix line says add [Sn]; adding it gives UNGROUNDED. | heading -> "# Summary"; deleted code block | PASS 100 (code block lost) | 2 |
| d6 | FAQ (honest) | NEEDS_WORK 62.5 | Why: no for 2 verbatim sentences; heading UNCITED yes | "## Borrowing limits" -> "## Limits"; replaced "twenty items" and "Report the loss..." sentences; one replacement failed ("Books may be kept"), swapped again | PASS 100 | 4 |
| d7 | incident report (FABRICATED number) | FAIL 40.0 | Number: yes, named "9,300" and the fix says copy source figure. Also a heading UNCITED and a verbatim sentence UNGROUNDED (no reason). | corrected to 3,900; heading -> "# Incident summary"; dropped the UNGROUNDED verbatim sentence | PASS 100 | 3 |
| d8 | news brief (FABRICATED claim) | NEEDS_WORK 66.7 | Caught (2 pieces UNGROUNDED) but output says "not evidence the claim is false"; the tester is not told it may be invented | deleted the invented sentence | PASS 100 | 1 |

Results:
- Honest drafts PASS first try: 1 of 6 (d3). After fixes: 6 of 6, but 3 only by deleting content (d4 table and % figures, d5 code block, d2/d6 facts swapped for easier sentences). Mean 2.5 edits for the 5 that needed any.
- Fabrications caught: 2 of 2 (d7 number by UNVERIFIED_NUMBER with a clear reason; d8 by UNGROUNDED, no hint it was invented). Both reached PASS only after the fabricated text was removed or corrected; neither slipped through.
- Of about 40 scored claim-pieces in the 6 honest drafts, 14 were refused although copied from the source.

## 3. Top 10 fixes, ranked by testers affected

1. Verbatim source sentences refused as UNGROUNDED with no reason (steps 10, 11): every tester copying sentences will hit it. Show the reason (which 8-word run is missing, or which rule fired), and stop telling people to "replace with the source's own sentence" when they did.
2. "N percent" sentences always UNVERIFIED_NUMBER even when copied (step 12): the message lists "3.1" without its unit while the source has "3.1 percent". Any report with percentages cannot PASS; fix the unit extraction or say so in the guide.
3. Code blocks cannot pass and the guide is silent (step 15): add a guide section, or exclude fenced code from claims.
4. Tables cannot pass; the guide says so, but the report message is the generic fix line, and "Q3" counts as a figure (step 14): output a table-specific fix ("write the facts as cited sentences").
5. Headings are unpredictable (step 16): "Meeting notes" scored UNCITED, "Results" not. List the rule or exemption in the explain output, or exempt all headings.
6. Sentence splitting at ", and" and commas in lists (step 13): the piece that loses its subject fails. Show a "split from sentence N" note and suggest rewriting; or do not split quoted spans.
7. Plain statements like "No rollback was needed" become absence claims (step 17): UNVERIFIED_ABSENCE for an honest sentence; the fix says "soften", which is wrong here.
8. Fabrication is not named (step 19): add a distinct line when no cited sentence shares 8 words, e.g. "No sentence in S1 contains this; it may be invented or paraphrased."
9. Guide's front matter oversells "copy the sentence": first-try pass was 1 of 6 on realistic documents; say that honest drafts commonly need 2-4 edits and some content (percentages, tables, code) cannot be certified at all.
10. `ground_check.py` without `--json` writes `grounding-report.yaml` into the repo folder (step 9) and GROUNDED claims print long boilerplate in explain_report (step 18): write the file to a named path, and print GROUNDED one-liners with details behind a flag.

Load-bearing assumption: my 6 honest drafts used copied sentences chosen by me; the 1-of-6 first-try rate depends on my choice of sentences and may be pessimistic or optimistic for other testers. Causes in item 1 are black-box guesses (I did not read the source).
