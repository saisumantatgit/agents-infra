# Red-team round R45 (OVN-1121, 2026-11-21)

**Verdict: main `d8c2ec0` certifies PASS 100 on 22 distinct families of fabrication, every one reproduced first-hand by the main loop with an honest control that PASSes and a known-refused control that FAILs. Several are ordinary prose, not contrived attacks. Until at least the three root causes below are addressed, a PASS should not be presented to an alpha tester as "every claim is supported".**

Method: three adversaries.

- An Opus reviewer found E1–E3 while checking two reports.
- Two Opus red-team lanes ran read-only, with probes in scratch: lane A on source-side denial and attribution, lane B on draft structure and markup.
- The main loop re-ran one probe per family from its own script, with a different claim string and its own controls (`verify/r45a.py`, `verify/r45b.py`, `v.py`, `v3.py`; scratch, removed at teardown; shapes below).

Lane-level counts (testimony, not re-run in full): lane A, 70 PASS runs over 61 source shapes; lane B, 8 families with 2–15 variants each.

## Terms

| Term | Meaning here |
|---|---|
| Error-B | A fabrication certified PASS. Unrecoverable. |
| Error-A | An honest claim refused. Recoverable. |
| Blacklist rule | A refusal that fires only when a listed word or a fixed window is present. A missing word passes. |
| Case / Systemic | Case fixes one shape (add a word). Systemic removes the cause. CLAUDE.md default is systemic. |

## The 22 families

Draft is `<claim> [S1].` unless shown. `{C}` is the claim, verbatim in the source.

| # | Source (or draft) shape | Root cause | Kind |
|---|---|---|---|
| E1 | `{C}. That was cooked up.` / `It was cooked up.` / `The press made that up.` | R2 | Evasion of R40 |
| E2 | Draft heading of source words, e.g. a verbatim copy of a denied sentence `## The regulator found fraud at Quay Trust` | R3 | New |
| E3 | `According to an anonymous forum post, {C}.` (attribution 6+ tokens before) | R2 | Round-7 class, still open |
| A1 | `~~{C}~~ (corrected below).` / `<del>{C}</del>` | R1 | New |
| A2 | `{C}[^1].` … `[^1]: This statement was retracted; it never happened.` | R1 | New |
| A3 | `{C}.` … new paragraph `The depot story above was fabricated by a rival.` | R2 | New (mirror of the H9 ceiling) |
| D1 | `The blog reported {C}.` ("that" dropped) | R2 | Evasion of J-22 |
| D2 | `{C}, the rival's press release stated, though nobody has confirmed it.` / `… stated: {C}.` | R2 | New |
| B1 | `{C}. That was in error.` / `… has since been withdrawn.` | R2 | New |
| B2 | `{C}. As if.` / `Yeah, right.` / `or so they say` | R2 | New |
| B3 | `Did {c}? The records say otherwise.` | R2 | New |
| C1 | `Several outlets erroneously reported {c}.` / `It is a mistake to think {c}.` | R2 | New |
| E1c | `Should the vote pass, {c}.` / `Had…` / `We hope {c}.` / `In theory, {c}.` | R2 | New |
| G1 | `Gossip:` (or `Unverified:`, `Allegations:`, `Satire:`, `In the novel,`) then `- {C}` | R2 | Evasion of H4 |
| F1 | Draft `… was [](not) renewed …` / `<not>` / `~~not~~` (source: "was not renewed") | R1 | New |
| F2 | Draft `## Myths` over `- {C} [S1]` (source states {C} as true) | R3 | New |
| F3 | Draft `## Criminals` over `- Larkfield Haulage [S1]` (name merely mentioned in S1) | R3 | New |
| F4 | Draft `❌ {C} [S1].` / `~~{C}~~ [S1].` | R1 | New |
| F5 | Draft `… was [](.<!--)not[](-->) renewed …` (the reader sees "not"; the gate strips it as a comment) | R1 | Evasion of J-41r / D-54 |
| F6 | Draft `10⁵` against source `105` (NFKC folds superscripts) | R1 | Seen in R14, never registered |
| F7 | Draft `The council fined the following firms for fraud in 2024 [S2]:` then `- <names from S1> [S1]` | R3 | New |
| F8 | Draft `- Larkfield Haulage [S1]` with continuation paragraph `$41 million [S1]` (figure belongs to another firm) | R3 | New |

Main-loop first-hand result: 22 / 22 PASS 100.0. Controls, all as expected: plain honest source PASS 100; `It is false that {C}.` FAIL 0; affirmative draft against a negative source FAIL 0; `That never happened.` after the claim FAIL 0; 5-token attribution FAIL 0.

## Three root causes

| Root | What it is | Families | Systemic fix | Needs |
|---|---|---|---|---|
| R1 | The gate reads Markdown *source*, not what the reader sees. Hidden, struck, footnoted or symbol-marked text is read as plain words. | A1, A2, F1, F4, F5, F6 (6) | Render both draft and source to text (CommonMark + GFM: strikethrough, footnotes, raw HTML, links, images), then decompose and ground the rendered text. Fail closed on any markup the renderer cannot place: struck or hidden text never grounds, and a claim containing it is refused. Superscripts are kept as a marked token, not folded into a digit. | A parsing dependency (`pyproject.toml` today: `syntok`, `pyyaml`). An install change is Escalation #4, so Sai. |
| R2 | Every refusal of a disowned source sentence is a blacklist over the attacker's vocabulary: denial words, hedge words, label words, a 5-token window. 11 families are one missing word or one extra token each. | E1, E3, A3, D1, D2, B1, B2, B3, C1, E1c, G1 (11) | Invert the test. A verbatim match grounds only when its source sentence is a plain assertion in the source's own voice: the claim is the sentence's main clause, the sentence opens with no frame (attribution, condition, label, question), and the paragraph has no sentence that refers back to it. Anything else is refused, whatever its words. The J-19 / OI-MOAT-27 comment in `ground_check.py` already diagnoses this ("putting the attacker on the enumerating side of the rule"). | Large Error-A cost to measure first; ADR (it changes what GROUNDED means), so Sai. |
| R3 | A fragment with no predicate (a bare name, a figure, a heading) grounds by being mentioned, and the draft's own structure (heading over list, lead-in plus list, list continuation, definition) supplies the predicate unchecked. | E2, F2, F3, F7, F8 (5) | Ground the claim the reader reads. Compose heading, lead-in or list parent with each item and ground the composition. A predicate-free fragment is never GROUNDED alone. A draft heading not taken from a source heading is scored (E2 brief). | Fail-closed; inside C1 authority. Error-A cost on honest lists to measure. |

**Why not just add the words:** lane A's per-family fix directions are mostly "add these words to the list". That is case resolution. Each instance would close, and this project's own record says what happens next: rounds 1–4, R40 → E1, J-22 → D1, H4 → G1. The next round finds the synonym. Case fixes for R2 are reasonable only as a stopgap with the systemic fix registered.

## What this means for alpha

The fabrication corpora (504 drafts) measured 7 PASS on v1 and 0 on v2. R45 shows why that read safer than it is: their shapes come from earlier rounds, so they measure the holes already known. Several R45 families are what honest-looking web prose looks like. "Several outlets erroneously reported…", "The blog reported…", a corrected sentence in strikethrough, and "Correction: an earlier version said…" are ordinary in news sources.

The corpora are an instrument, not the goal (§2-A Goodhart). Each R45 family should enter the corpus (C2b brief) before its fix, so the fix is measured against it.

## Recommended order (for Sai)

1. **WITHDRAWN as new work (see R45-R46-CLASSIFICATION.md): the tester guide already says PASS means "traceable, never true, never supported".** What it lacks is the list of traceability breaks. Original text: do not present PASS to alpha testers as a guarantee. Present it as "no known fabrication shape found", with this report linked. Why: every family above is live, and a tester will hit R1 shapes by accident.
2. **First build, fail-closed, inside C1 authority:** E1 + E3 (briefs written) and R3 (E2 brief, extended to lead-in lists, continuations and definition lists). These are local changes with measurable Error-A.
3. **Decide R1 (render first):** I recommend YES. It closes 6 families structurally and makes the gate read what the reader reads, which is the product's promise. The cost is a parsing dependency and an install change (Escalation #4). What would flip it: no parser that is deterministic, offline and pure Python fits the moat's "no network, no model" rule.
4. **Decide R2 (assertion test) after measuring it:** I recommend having it measured on a scratch copy, honest corpora first, then ruled. Why: it is the only fix that ends the synonym race, but it will refuse honest attributed facts ("According to the annual report, revenue rose 4%"). That is a product decision about what PASS means.
5. **Every family into the fabrication corpus (C2b) before its fix.**

## Not covered

- Both lanes stopped at about 25 families' worth of probes, so this round says nothing about families it did not try.
- Duplicates of known open items (lane A: 7 probes under J-70/E3 and the `_trailing_denied` ceiling) are excluded.
- Lane B's F8 definition-list shape and F1's `![not]()` depend on the renderer (pandoc/MkDocs; broken-image display). The other lane-B shapes are CommonMark/GFM.
