# R45 lane A: the source disowns the claim, the draft cites it plainly

Target: agents-infra main d8c2ec0, `Agent-Assure/scripts/ground_check.py`. Read-only; nothing in the repo was edited.
Harness: `probe.py` (reuses `tests/usage_genres/run.py` `build_store` and `check`; real capture hook, Read events). Case files `b1.py` to `b6.py`; raw results in `b1.json` to `b6.json`.
Draft for every case: `<CLAIM> [S1].` with one verbatim source S1.
CLAIM-1 = `The regional office in Leeds closed its doors after the merger with Halcyon` (b1 to b4, b6). CLAIM-2 = `The regional bank collapsed in March after the regulator completed its audit` (b5, replication).
Padding in most cases: P = `Staff moved to new posts. `, T = ` The board met in May.`

**Verdict: 11 confirmed PASS families (70 PASS runs, 61 distinct source shapes), plus 7 probes classified as duplicates of known open items.** Every batch holds both controls: CTRL-PLAIN (`P + CLAIM. + T`) = PASS 100.0 GROUNDED, and CTRL-REFUSED (`P + It is false that CLAIM. + T`) = FAIL 0.0 UNGROUNDED (`verbatim_but_hedge_word_before_it`). Where a family evades a specific shipped fix, that fix's own refused shape is in the same batch as an extra control.

Load-bearing assumption: every refusal rule on this surface is a word list or a fixed window (see the CEILING notes in `_unit_denial_reason`, `_paragraph_denied` and `_trailing_denied`). Every finding below is a word or a structure missing from those lists. So families A1, A2 and D1 are the ones that do not reduce to "add a word".

## Confirmed PASS findings (gate PASS 100.0, claim GROUNDED)

| # | Family | Class | Minimal source (S1); `{C}` = the claim | Probes PASS |
|---|---|---|---|---|
| A1 | Strikethrough markup disowns the text | NEW hole (structural) | `P ~~{C}~~ (corrected below). T` / `P <del>{C}</del>. T` / `P ~~{C}~~. T` (CLAIM-2 too) | 4/4 |
| A2 | Footnote binds a denial to the claim | NEW hole (structural) | `P {C}[^1]. T\n\n[^1]: This statement was retracted; it never happened.` / `[^1]: Fabricated; see the correction.` (CLAIM-2 too) | 3/3 |
| A3 | Falsity statement in a LATER paragraph, pointing back with "above" and a strong word | NEW: mirror of the documented H9 CEILING, which names only EARLIER paragraphs | `P {C}. T\nOther notes follow. Staff picnicked.\n\nThe Leeds story above was fabricated by a rival.` (CLAIM-2: `The bank story above was fabricated.`); also a "rumour" variant | 3/3 |
| D1 | Reporting verb with the "that" dropped | EVASION of J-22 (the non-factive complement whitelist, `_span_under_nonfactive_complement`). Its "load-bearing negative" test is `The blog reported that X` | `P The blog reported {C}. T` / `insisted {C}` / `speculated {C}` / `posited {C}` / `announced`, `wrote`, `tweeted`, `maintained`. Controls in the same batch: `The blog reported that {C}.` and `The vendor insisted that {C}.` both FAIL | 9/9 |
| D2 | Attribution by colon, by label, or after the claim, with a verb outside the hedge list | NEW | `The rival's press release, issued in May, stated: {C}.` / `{C}, the rival's press release stated, though nobody has confirmed it.` / `P The rival's version of events: {C}. T` / `Rival press releases spread the following:\n\n> {C}.` | 4/4 |
| B1 | Retraction or error words in the next sentence, pointing back | NEW (vocabulary instance under the generic `_unit_denial_reason` CEILING) | `P We previously reported {C}. That was in error. T` / `P {C}. That was in error. T` (CLAIM-2 too) / `{C}. This has since been withdrawn.` / `{C}. That announcement was rescinded the next day.` / `{C}. That report turned out to be a rumour.` / `Editor's note: This article originally stated {C}. The office remains open.` | 6/6 |
| B2 | Sarcasm or an idiom as the reply | NEW (vocabulary) | `{C}? Hogwash.` / `{C}, or so they say.` (the hedge list has "says" but not "say") / `Sure, {C}. Yeah, right.` / `{C}. As if.` / `{C}. And pigs fly.` / `{C}. Neither account survived scrutiny.` | 6/6 |
| B3 | A question followed by a rebuttal that is not a bare negator | NEW | `P Did {C}? The records say otherwise. T` (the control `Is it true that {C}? Not at all.` FAILs) | 1/1 |
| C1 | Negation by scope, or an "error" adverb, earlier in the same sentence | NEW (vocabulary) | `Several outlets erroneously reported {C}.` (CLAIM-2 too) / `Many mistakenly believe {C}.` / `It is a mistake to think {C}.` / `Only conspiracy theorists believe {C}.` / `Few serious analysts accept {C}.` | 6/6 |
| E1 | A conditional or irrealis frame with no hedge word | NEW (vocabulary; not J-70: no word from `_SPAN_HEDGE_TOKENS` is in the sentence) | `Should the vote pass, {C}.` (CLAIM-2 too) / `Had the vote passed, {C}.` / `{C}, provided the vote passes.` / `Once the vote passes, {C}.` / `In the unlikely event that the vote passes next spring, {C}.` / `But for the rescue loan, {C}.` / `We hope {C}.` / `In theory, {C}.` / `Scenario B (hypothetical): {C}.` ("hypothetically" is listed; "hypothetical" is not) / `Prediction: {C}.` / `Imagine this: {C}.` / `The plan is simple: {C}.` | 14/14 |
| G1 | Disowning-label word missing from `_DISOWNING_LABEL_TOKENS`, and genre frames | EVASION of H4 (disowning label). The control `Rumours:\n\n- {C}` FAILs `verbatim_but_under_disowning_label` | `Gossip:` / `Unverified:` / `Allegations:` (CLAIM-2 too) / `Retracted statements:` / `Common errors in coverage:` / `What Halcyon's press office told reporters:`, each followed by `\n\n- {C}`; genre frames `Satire:\n\n- {C}` / `P Parody: {C}. T` / `P In the novel, {C}. T` (CLAIM-2 too) / `P April Fools: {C}. T` / `{C}.\n\n— The Onion (satirical news)` / `P {C}.[citation needed] T` | 14/14 |

PASS probe total: 4+3+3+9+4+6+6+1+6+14+14 = 70 runs. Of these, 61 are distinct source shapes; the other 9 are CLAIM-2 replications (8) and one repeated verb (insisted).

## Fix direction and likely honest-claim (Error-A) cost

| # | Fail-closed fix direction | Error-A cost, one line |
|---|---|---|
| A1 | Treat text inside `~~...~~`, `<del>` and `<s>` as not asserted: it may not ground | Near zero. Honest sources rarely strike through a fact they still assert |
| A2 | Join each `[^n]:` footnote body to the sentence that carries `[^n]`, then run the next-sentence and trailing denial rules on it | Low. Footnotes that deny the text they annotate are rare; the cost is footnotes that use a strong word about something else |
| A3 | Make the strong falsity sentence plus a back-reference ("above", "earlier", "this story") reach back across paragraphs | Moderate. It refuses honest claims above an FAQ "the story above is a myth" paragraph that targets a different claim. This is the same trade that left H9 open, so it needs Sai's ruling |
| D1 | Apply the J-22 rule when the "that" is missing: a reporting or non-factive verb in the five tokens before the span refuses unless it is factive | Moderate. It refuses an honest "The report found X" only if "found" is dropped from the factive list, which it is not. The real cost is unlisted verbs ("added", "noted") placed before honest facts |
| D2 | Add the verbs `stated`, `wrote`, `announced`, `insisted`, `tweeted`, `maintained` and a "version of events" label to the hedge and label lists; add a post-claim reporting clause (", X stated") to the trailing rule | Low to moderate. Press-release sources that state real facts after "stated:" are refused |
| B1 | Add `in error`, `withdrawn`, `rescinded`, `retracted`, `corrected`, `rumour`, `originally stated` and `previously reported` to the next-sentence back-pointing denial rule and the hedge window | Low. "This has since been corrected" after an honest fact is rare and reads as a retraction anyway |
| B2 | Add a closed list of sarcasm and rebuttal idioms ("yeah, right", "as if", "pigs fly", "hogwash", "or so they say", "say otherwise") to the bare-reply rule | Low. Idioms are rare in technical sources; "as if" also opens honest similes, which get refused (Error-A) |
| B3 | A question with the claim inside it may not ground at all (a "?" on the source sentence refuses) | Moderate. Honest FAQ sources ("Does X support Y? Yes.") are refused unless the answer says yes |
| C1 | Add `erroneously`, `mistakenly`, `mistake`, `wrongly believe`, `only ... believe` and `few ... accept` to the same-sentence denial list | Low for the adverbs. Moderate for the "few"/"only" quantifiers, which appear in honest prose |
| E1 | Refuse a sentence that opens with an inverted auxiliary (`Should`/`Had`/`Were` + subject), or that contains `provided`, `once`, `in the event`, `but for`, `hope`, `in theory` or `hypothetical`, or a `Prediction`/`Scenario`/`Plan` label | Moderate. "Once" and "provided" are common in honest procedural text ("Once installed, X runs") |
| G1 | Add the label words (gossip, unverified, allegation(s), retracted, error(s), satire, parody) and the genre frames (novel, film plot, April Fools, "[citation needed]", a satire-outlet byline) to `_DISOWNING_LABEL_TOKENS` | Low for most of the labels. "Errors" and "allegations" headers sit over honest lists about errors and legal allegations, which get refused |

## Duplicates of known open items (not counted)

| Probe | Source shape | Gate | Known item |
|---|---|---|---|
| if-long | `If the shareholders approve the plan at the meeting next spring, {C}.` | PASS | J-70: a hedge word in the sentence but outside the 5-token window. Same mechanism as E3 |
| mistake-to-think | `It would be a mistake to think {C}.` ("would" is 6 tokens back) | PASS | J-70 |
| trailing-if | `{C} if the vote passes next spring.` | PASS | J-70 (the hedge sits after the span) |
| said-after-quote | `"{C}," a rival spokesman said.` | PASS | J-70 / E3 family |
| table-cell | `\| {C} \| Retracted \|` | PASS | `_trailing_denied` CEILING (a trailing denial word that is not strong) |
| list-status | `- {C} — retracted` | PASS | `_trailing_denied` CEILING |
| nobody-verified | `{C} is a story nobody has verified.` | PASS | `_trailing_denied` CEILING |

## Probes the gate refused (the fixes held)

supposedly; so-called; wrong to say; correction label ("Correction: an earlier version ... said X"); question then "No."; parenthesis "(this never happened)"; canard; "does not hold water" in the next sentence; "has never been confirmed" after the claim; "said no one ever"; "Is it true that X? Not at all."; "Verdict: Pants on fire."; dialogue "Absolutely not"; "stated without evidence" (refused by the polarity rule on "without"). "Claim: X\n\nRating: False" came out UNGROUNDABLE: the source is short enough to count as a near-copy of the draft, so that case says nothing about the "Rating: False" label.

## Notes on how wide the holes are

- The 61 PASS shapes are close to the first wording tried in each family. Most families did not need a second attempt, so the open set is far larger than this list. The real ceiling is the one the code already names: a lexical gate with no model of what a denial targets.
- A1 and A2 are not vocabulary gaps. The disowning signal is markdown structure that `_split_sentences` and the unit contexts do not read, so adding words cannot close them.
