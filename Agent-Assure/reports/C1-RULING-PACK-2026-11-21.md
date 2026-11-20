# C1 ruling pack: heading fabrications and far denials (OVN-1121, 2026-11-21)

**Verdict: neither family can be closed tonight without a ruling from Sai, and one of them should not be closed by a gate change.**

- **Heading fabrications (Family H):** a simple rule catches all 15 attack headings. It also scores 33% of honest headings, so it trades honest refusals for safety. That is Escalation #1 and Sai's call.
- **Far denials (Family D):** the corpus labels look wrong. In both classes the denial comes *before* the claim and points backward. Read as English, the source asserts the claim, so the two PASSes in these classes are probably not fabrications.

Measured on main `d8c2ec0` (2026-11-21). No gate code was changed. Codex is out of quota until 26 Nov 13:52, so no build was attempted (D-121).

## Terms

| Term | Meaning here |
|---|---|
| Error-B | A fabrication certified PASS. Unrecoverable; the moat. |
| Error-A | An honest claim refused. Recoverable: the writer rewords or cites. |
| Novel word | A heading word, outside a 40-word stop list, that occurs in none of the draft's captured sources. Lower-cased, NFKC. |
| Scored heading | A heading the gate checks as a claim instead of treating as a label (`NON_CLAIM`). |

## Family H: claim headings

The draft opens with a heading that asserts something no source says, for example `## Regulator: Plover lied`. The gate classifies it as a label, never scores it, and the draft is certified PASS. That happens in 5 of the 15 `claim_heading` drafts on the v1 fabrication corpus.

**Candidate rule H1:** a heading may stay a label only if every content word in it occurs in a captured source the draft cites. Otherwise it is scored. A scored heading has no citation, so the draft becomes NEEDS_WORK with a reason that names the words.

| Measure | Result |
|---|---|
| Attack headings caught | 15 / 15 have at least one novel word, including all 5 that PASS today |
| Honest drafts that PASS today and would lose PASS: Error-A corpus | 3 of 5 (`Known issues`, `Cost pressures`, `Regional targets`) |
| Same: v1 fabrication-corpus honest controls | 0 of 190 |
| Same: v2 fabrication-corpus honest controls | 0 of 93 |
| Honest headings with a novel word (Error-A corpus + usage_genres) | 175 of 532 (33%) |
| Most common novel words in honest headings | rises 17, limits 16, price 14, changes 8, common 7, steps 7, breaking 6, features 6, issues 6 |

**Why not an exemption list:** exempting the honest words would take a list of 60 or more, and it would include claim-bearing words such as `rises` (`Price rises` is honest 15 times here). A list tuned to these corpora is the Goodhart failure CLAUDE.md warns about.

A list whose missing members point toward refusal is not unsafe, because a missing word gets the heading scored. The cost is maintenance: every honest heading word outside the list becomes an Error-A complaint.

**Sibling hole, which H1 does not close:** a heading built only from source words that reverses the source. For example, the source says "no fraud was found at Larkspur" and the draft heading is `# Fraud at Larkspur`. Every word is in the source, so H1 leaves it unscored.

**Recommendation: ship H1 with a refusal reason that names the novel words, after Sai rules YES.** Why:

- Error-B is unrecoverable. A heading is a free text channel the gate never reads, and 5 certified fabrications use it today.
- H1's Error-A is recoverable at the writer's desk: reword the heading with the source's words, or delete it. The refusal says exactly which words to change.
- Honest PASS on the Error-A corpus would fall from 5 to 2. That number is already too small to judge from, which is the separate Error-A problem in the 2026-11-15 ruling pack.

What would flip it: alpha testers' real drafts showing heading rewording as the main source of friction. Then the upgrade path is the one the code's CEILING comments already name, a part-of-speech tagger on headings.

## Family D: far denials

The v1 builder (`tests/error_b_corpus/fabrications.py`, `b_denied_2back` and `b_denied_3plus`) writes the source as:

`<denial>. <1-4 unrelated filler sentences>. <claim>.`

For example: "That never happened. Staff left early. Quay Trust was acquired by a larger rival last spring."

- **The label is the problem.** Six of the twelve denial phrases point back ("That never happened.", "This is a myth."). Put before the claim, they refer to whatever came earlier, not to the claim that follows. So the source asserts the claim, and certifying it is arguably correct.
- **The gate already refuses 13 of 16 in each class.** That is the same refusal rule that costs honest claims below.
- **The rule's honest cost is measured.** On the Error-A corpus, `verbatim_but_sentence_two_back_denies` refuses 37 honest claims. Typical case: "The rate limit is 3668 requests per minute for each key" is refused because two sentences earlier "The beta `cursor` filter never left preview and is not documented here" negates a different subject.

**Recommendation: do not widen the denial window (C1-D as planned). Instead:**

1. **Relabel the corpus (Codex, after 26 Nov; tests only, no ruling needed).** Rebuild `denied_2back` and `denied_3plus_back` so the denial can only refer to the claim. Either it comes after the claim and points back, with fillers between, or it is an explicit forward pointer ("The following report is false:"). Keep the current shapes as honest controls.
2. **Narrow the two-back rule (needs Sai, Escalation #1, because it lets claims pass).** Require that the denial's subject or back-reference resolves to the claim's subject. Measure on both fabrication corpora and the Error-A corpus before shipping.

What would flip it: Sai reading "That never happened. Staff left early. X." as denying X. Then the label stands, the 2 PASSes are Error-B, and the fix is a wider window with its Error-A cost measured first.

## Side finding: a denial in the next paragraph

`verbatim_but_next_sentence_denies` refuses 183 honest claims on the Error-A corpus (193 segments). 19 of them are refused across a paragraph break: the "next sentence" is the first sentence of the following paragraph. Stopping that rule at a paragraph break lets claims pass, so it is Sai's call. It is a smaller, more principled cut than the 164 same-paragraph cases.

## Reproduce

The measurement scripts lived in the run's scratch directory and were removed at teardown. Each is under 40 lines and reads only `results.json` and `manifest.json` of the corpora, plus their sources:

- **Heading cost:** extract ATX (`#`) and setext headings, tokenise `[a-z0-9]+` after NFKC and lower-casing, and drop stop words. A heading has a novel word if any token is missing from all of that draft's sources. Count over drafts whose gate (or `control_gate`) is PASS.
- **Two-back and next-paragraph cases:** for each claim whose segment diagnostic is the named one, find the claim text in its source's paragraphs and report what follows it.
