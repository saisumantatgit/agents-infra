# RED-TEAM W2C — decompose/classify surface (2026-10-24)

Branch capture-contract-2026-10-10. Store: demo/evidence-store.jsonl (retrieval_status ok). Every result below is real
`uv run python scripts/ground_check.py --draft D --store S --json` output; drafts and outputs kept in `/private/tmp/claude-501/-Users-saisumanth/d2b27b1f-f3bd-4dea-8c6a-e58508ad626d/scratchpad/w2c`.
Baseline B = "Redis sustained approximately 128000 operations per second [S1]." -> PASS 100.0.

## New findings

## W2C-01 — RCDATA/raw-text element inside a label-shaped heading: visible fabrication stripped as a "comment", heading residue NON_CLAIM | HIGH
- **Mechanism:** `_strip_html_comments_outside_code` (scripts/ground_check.py:738-770) removes every same-line `<!--...-->`
  outside code. Inside `<textarea>` / `<xmp>` the browser treats `<!--` as literal, visible text (HTML RCDATA / raw text),
  so the stripper deletes reader-visible prose. The leftover `## Key Data <textarea readonly> </textarea>` then reaches
  `_is_non_claim` header branch (:1050-1084): `_header_asserts` (:977) sees no auxiliary and no non-final token ending in
  s/ed/ing/en (`<textarea>` ends in `>`), so the heading is a label -> NON_CLAIM.
- **Reproduction:**
  ```
  Redis sustained approximately 128000 operations per second [S1].

  ## Key Data <textarea readonly><!-- PostgreSQL loses all committed data on restart. --></textarea>
  ```
  -> `gate PASS, grounding_score 100.0, scored_claims 1`; claim 1 = `'## Key Data <textarea readonly> </textarea>'` NON_CLAIM.
  Same PASS with `<xmp>`. (`<title>` also PASSes but is not reader-visible, so not counted.)
- **new/registered:** NEW as a reproduction. R10-A (docs/plans/reports/RED-TEAM-R10-A-denominator.md:301) listed
  `<textarea>` as an UNREPRODUCED hypothesis. The heading is the carrier that makes it land: in a paragraph, or welded
  onto a grounded sentence, the tag residue is scored and FAILs (TRIED AND HELD, below).
- **Renderer scope:** needs a renderer that passes raw `<textarea>`/`<xmp>` (plain HTML conversion, many static-site
  generators). GitHub's sanitiser may drop the tag; not verified (no network).
- **Sibling:** J-27 / J-41r comment-stripping class (same function; J-41r docstring claims the rule is "renderer-faithful
  by construction" — it is faithful to CommonMark's comment grammar, not to the HTML element the comment sits in).
  Systemic fix direction: do not strip a comment whose enclosing inline HTML element is RCDATA/raw-text, or (simpler,
  fail-closed) never strip a same-line comment that is preceded on its line by an unclosed `<textarea|xmp|plaintext|noembed|noframes|iframe` tag.

## Registered (re-confirmed open, real output)

## W2C-R1 — Stop-word-only anaphoric sentences leave the denominator beside a grounded claim | MEDIUM
- **Mechanism:** `_is_non_claim` zero-content rule (:1037-1039) — no numeric and no content word after stop-word removal
  -> NON_CLAIM. Anaphora carries the proposition.
- **Reproduction:** `B + " That is not so."` -> PASS 100.0 (retraction of the cited claim). `B + " We had more than that."`
  -> PASS 100.0 (fabricated comparative). `B + "\n\nNo. It was not. We had more than that, up to more than that."` -> PASS.
- **registered:** R7-PATH-A finding 5 (docs/plans/reports/R7-PATH-A-decomposition.md:224). Note: R7-CHALLENGE (:258) marked
  that instance non-reproducing because alone it is vacuous (NEEDS_WORK). Paired with one grounded claim it is a real PASS,
  so the challenge's correction understated it.
- **Sibling:** OI-MOAT-32 (cited variant `It is not [S1].`, fixed).

## W2C-R2 — Irregular-past-verb heading reads as a label | MEDIUM
- `B + "\n\n## MongoDB Lost All Customer Data Last Year"` -> PASS 100.0, heading NON_CLAIM. Registered:
  tests/red_team_moat/test_moat_r7_open.py:203-214 (OI-MOAT-19 family, verb-final / irregular-verb headings). The
  "## Key Data" label rule is also the carrier for W2C-01.

## TRIED AND HELD (all gate FAIL, fabrication scored UNCITED/UNGROUNDED)
| Vector | Result |
|---|---|
| Full-width `＃` heading (NFKC -> `#`) | scored FACTUAL UNCITED |
| Label heading "## Acme Postgres Total Corruption" | scored (Postgres trips suffix) |
| Fenced code, inline code span | scored |
| Pipe table row; table with citation only in another row's cell | scored / UNGROUNDED |
| Footnote `[^1]` + definition | scored, also broke the grounded claim |
| Blockquote, list item, list items without periods, newline without period | scored / welded and UNGROUNDED |
| `<span>`, `<details>` | scored |
| Link-reference definition `[S1]: fabrication` | UNGROUNDED |
| Setext heading | scored |
| Transition prefix "However, ..." | scored |
| Zero-width spaces inside words | scored |
| Full-width citation `［S1］` then uncited next sentence | next sentence UNCITED |
| Citation dilution: verbatim S1 sentence + "i.e." / parenthetical / em-dash fabrication | UNGROUNDED |
| Colon after citation; semicolon back-propagation | UNGROUNDED |
| `\<!-- ... -->`, `&lt;!-- --&gt;` | not stripped, scored |
| `<textarea>` comment in a paragraph or inside the grounded sentence | residue scored, FAIL |
| "But not for us, it was not so." | ABSENCE, UNVERIFIED_ABSENCE |

Status: COMPLETE.
