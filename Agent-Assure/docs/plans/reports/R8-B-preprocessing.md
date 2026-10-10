# R8-B — Red team of the text preprocessing chain

Target: `normalized = _nfkc(_break_after_headers(_strip_html_comments_outside_code(text)))`
(`Agent-Assure/scripts/ground_check.py`, lines 277–381) and the zero-content
`NON_CLAIM` rule (`_is_non_claim`, line 560).

Date: 2026-09-12. Gate run from `Agent-Assure/` with
`uv run python scripts/ground_check.py --draft D.md --store S.jsonl --json`.
Scratchpad (all drafts/stores/scripts):
`/private/tmp/claude-501/-Users-saisumanthbattepati-vibe-coding-Agents-agent-assure-calibration/d2b27b1f-f3bd-4dea-8c6a-e58508ad626d/scratchpad/r8b/`

"What a human reader sees" is not asserted — every rendering claim below is the
output of `pandoc -f commonmark -t html` on the same byte-identical draft file.

## Shared store — `store.jsonl` (one line)

```json
{"source_id":"S1","url":"https://example.invalid/db-notes","file_path":null,"fetched_at":"2026-09-12T00:00:00Z","tool":"WebFetch","content_sha256":"aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa","text":"Redis is an in-memory data structure store. Redis supports replication and persistence. The default port for Redis is 6379.","full_text_source":"verbatim","captured_via":"exa","query_provenance":"redis overview"}
```

Baseline sanity: a draft of only `Redis is an in-memory data structure store [S1].`
→ `{"gate": "PASS", "grounding_score": 100.0, "scored_claims": 1}`.

Summary: **2 ERROR-B findings** (each with a gate=PASS reproduction), **1
denominator-escape family with 4 distinct triggers** (also gate=PASS), 1 ERROR-A.

---

## R8B-01 — ERROR-B — comment delimiters inside code constructs the gate does not recognise as code

**Mechanism.** `_CODE_SPAN_RE` only knows backtick spans (```` ``` ````, ``` `` ```,
`` ` ``); a CommonMark **tilde fence (`~~~`)** and a CommonMark **indented (4-space)
code block** are code to every renderer but plain text to
`_strip_html_comments_outside_code`, so a `<!--` a writer is *showing* inside one
pairs with a `-->` inside another and silently deletes every reader-visible
sentence between them. This is OI-MOAT-29 exactly, through the two block-code
syntaxes the fix did not enumerate.

### Reproduction 1a — tilde fence (`a1_tilde.md`)

```
Redis is an in-memory data structure store [S1].

~~~
<!-- example opener
~~~

MongoDB lost all data under load.

~~~
-->
~~~
```

Gate output:

```json
{"gate": "PASS", "grounding_score": 100.0, "per_claim": [{"index": 0, "kind": "FACTUAL", "text": "Redis is an in-memory data structure store [S1].", "verdict": "GROUNDED"}, {"index": 1, "kind": "NON_CLAIM", "text": "~~~", "verdict": "GROUNDED"}, {"index": 2, "kind": "NON_CLAIM", "text": "~~~", "verdict": "GROUNDED"}], "retained_appendix": [], "scored_claims": 1, "vacuous": false}
```

What the reader sees (`pandoc -f commonmark -t html`):

```html
<p>Redis is an in-memory data structure store [S1].</p>
<pre><code>&lt;!-- example opener</code></pre>
<p>MongoDB lost all data under load.</p>
<pre><code>--&gt;</code></pre>
```

The gap: a rendered, reader-visible, uncited factual assertion
("MongoDB lost all data under load.") is **absent from the gate's per-claim list
entirely** — not UNCITED, not UNGROUNDED, not present. `scored_claims: 1`, PASS.

### Reproduction 1b — indented code block (`a2_indent.md`)

```
Redis is an in-memory data structure store [S1].

    <!-- example opener

MongoDB lost all data under load.

    -->
```

```json
{"gate": "PASS", "grounding_score": 100.0, "per_claim": [{"index": 0, "kind": "FACTUAL", "text": "Redis is an in-memory data structure store [S1].", "verdict": "GROUNDED"}], "retained_appendix": [], "scored_claims": 1, "vacuous": false}
```

Pandoc renders the same four blocks as in 1a. Here the disappearance is total:
the gate's report shows a one-claim document, so nothing in the output even hints
that text was removed.

### Reproduction 1c — same mechanism used to certify the OPPOSITE (`c4_indent_reverse.md`)

```
Redis is an in-memory data structure store [S1].

    <!-- x

Redis does not support replication [S1].

    -->

Redis supports replication and persistence [S1].
```

```json
{"gate": "PASS", "grounding_score": 100.0, "per_claim": [{"evidence_basis": "Checked verbatim against 1 cited source: S1 (123 chars).", "index": 0, "kind": "FACTUAL", "text": "Redis is an in-memory data structure store [S1].", "verdict": "GROUNDED"}, {"evidence_basis": "Checked verbatim against 1 cited source: S1 (123 chars).", "index": 1, "kind": "FACTUAL", "text": "Redis supports replication and persistence [S1].", "verdict": "GROUNDED"}], "retained_appendix": [], "scored_claims": 2, "vacuous": false}
```

Reader (pandoc) sees a document that asserts **"Redis does not support
replication [S1]."** as visible prose. The gate certifies a document containing
only its negation, at 100.0.

---

## R8B-02 — ERROR-B — backslash-escaped delimiters (`\<!--` … `\-->`)

**Mechanism.** CommonMark backslash escapes turn `\<!--` and `\-->` into *literal
visible text* (`<!--`, `-->`), which is precisely how an author writes *about*
comment syntax outside a code span; `_strip_html_comments` has no notion of
escaping, sees a well-formed pair, and deletes everything between them.

### Reproduction 2a — whole-sentence deletion at PASS (`c1_escaped_pass.md`)

```
Redis is an in-memory data structure store [S1].

\<!--

MongoDB lost all data under load.

\-->
```

```json
{"gate": "PASS", "grounding_score": 100.0, "per_claim": [{"evidence_basis": "Checked verbatim against 1 cited source: S1 (123 chars).", "index": 0, "kind": "FACTUAL", "text": "Redis is an in-memory data structure store [S1].", "verdict": "GROUNDED"}, {"index": 1, "kind": "NON_CLAIM", "text": "\\", "verdict": "GROUNDED"}], "retained_appendix": [], "scored_claims": 1, "vacuous": false}
```

Reader sees four visible paragraphs:

```html
<p>Redis is an in-memory data structure store [S1].</p>
<p>&lt;!--</p>
<p>MongoDB lost all data under load.</p>
<p>--&gt;</p>
```

### Reproduction 2b — mid-sentence meaning reversal at PASS (`c2_escaped_reverse.md`)

```
Redis is an \<!--on-disk relational, never an\--> in-memory data structure store [S1].
```

```json
{"gate": "PASS", "grounding_score": 100.0, "per_claim": [{"evidence_basis": "Checked verbatim against 1 cited source: S1 (123 chars).", "index": 0, "kind": "FACTUAL", "text": "Redis is an \\  in-memory data structure store [S1].", "verdict": "GROUNDED"}], "retained_appendix": [], "scored_claims": 1, "vacuous": false}
```

Reader sees (pandoc): `Redis is an <!--on-disk relational, never an--> in-memory
data structure store [S1].` — nothing is hidden. The gate judged, and printed
back to the author, a sentence the author did not write, and certified it
GROUNDED at 100.0. This is the OI-MOAT-26 failure shape (weld a delimiter pair
into the middle of a sentence and reverse it) re-achieved through escaping
rather than through NFKC — i.e. the D-26 ordering fix moved this hole, it did not
close it.

---

## R8B-03 — denominator escape ×4 — header weld: `_HEADER_LINE_RE` is strictly narrower than the header test that grants the `NON_CLAIM` exemption

**Mechanism.** The paragraph-break repair keys on `^(#{1,6} [^\n]*)$` (1–6
hashes, one ASCII space, pre-NFKC), while the exemption that lets a header leave
the scored denominator keys on `_NO_FINITE_VERB_RE = ^#+\s` (any hash count, any
whitespace, post-NFKC). Every shape inside the second and outside the first gets
**no break inserted but still counts as a header** — so syntok welds the
following sentence into the "header", `_header_asserts` looks at the welded body,
and a verb it cannot detect ("lost") carries the whole assertion out of the
denominator. That is OI-MOAT-30 restored by four different one-character edits.

All four drafts have the same shape (`a4/a5/a6/a8_*.md`):

```
Redis is an in-memory data structure store [S1].

<HEADER LINE>
MongoDB lost all data under load.
```

| id | header line (bytes) | `_HEADER_LINE_RE` | `^#+\s` | pandoc renders header line as | gate |
|----|---------------------|-------------------|---------|-------------------------------|------|
| a6 | `23 09 TODO` (`#`+TAB) | no (needs space) | yes | `<h1>TODO</h1>` + separate `<p>` | PASS 100.0 |
| a5 | `####### TODO` (7 hashes) | no (max 6) | yes | `<p>####### TODO MongoDB lost all data under load.</p>` | PASS 100.0 |
| a8 | `23 c2a0 TODO` (`#`+NBSP) | no (needs U+0020) | yes (NBSP is `\s`) | `<p># TODO MongoDB lost all data under load.</p>` | PASS 100.0 |
| a4 | `efbc 83 20 TODO` (U+FF03 `＃`+space) | no (pre-NFKC) | yes (post-NFKC `#`) | `<p>＃ TODO MongoDB lost all data under load.</p>` | PASS 100.0 |

Identical gate output for all four (header text varies):

```json
{"gate": "PASS", "grounding_score": 100.0, "per_claim": [{"evidence_basis": "Checked verbatim against 1 cited source: S1 (123 chars).", "index": 0, "kind": "FACTUAL", "text": "Redis is an in-memory data structure store [S1].", "verdict": "GROUNDED"}, {"index": 1, "kind": "NON_CLAIM", "text": "#\tTODO\nMongoDB lost all data under load.", "verdict": "GROUNDED"}], "retained_appendix": [], "scored_claims": 1, "vacuous": false}
```

Control (`a10_plainheader.md`, `### TODO`): `gate FAIL, 50.0`, the fabrication
is scored `UNCITED` — i.e. the D-30 fix works on exactly the one shape it was
written against.

What the reader sees: in **three of the four** (a5, a8, a4) there is no heading
at all — pandoc renders a plain paragraph, so the reader reads a bare factual
assertion in running prose. In a6 the reader gets a real `<h1>` plus a separate
paragraph asserting it. In all four the gate scored nothing.

**Bounding the escape (stated so it is not over-claimed).** The weld only leaves
the denominator when the smuggled sentence carries *no citation and no numeric*
and its verb evades the suffix heuristic. Verified:
`b6_tab_cited.md` (`… under load [S9].`) → `FAIL`, `UNVERIFIED_CITATION`;
`b7_7hash_num.md` (`… lost 42 percent …`) → `FAIL`, `UNCITED`. So the shape a
fabricator wants most — an uncited assertion — is exactly the one that escapes,
and the two shapes the gate already catches elsewhere still get caught.

---

## R8B-04 — ERROR-A — the code-span carve-out scores ordinary authoring notes again

**Mechanism.** `_strip_html_comments_outside_code` splits at code spans and
strips each *segment* independently, so a genuine, well-formed comment that
happens to contain inline code is never well-formed in any one segment and
survives into the scored text — the D-17/OI-DEC-03 "a writer's TODO note is not
prose" guarantee is void for any note containing a backtick.

`d6_note_with_code.md`:

```
Redis is an in-memory data structure store [S1].

<!-- TODO: check the `maxmemory` setting before publishing -->
```

```json
{"gate": "FAIL", "per_claim": [{"index": 0, "kind": "FACTUAL", "text": "Redis is an in-memory data structure store [S1].", "verdict": "GROUNDED"}, {"index": 1, "kind": "FACTUAL", "text": "<!-- TODO: check the `maxmemory` setting before publishing -->", "verdict": "UNCITED"}], "scored_claims": 2}
```

Reader sees nothing (pandoc emits only the first paragraph). Recoverable, and
strictly the safe direction — recorded because it is a live false-alarm cost of
the OI-MOAT-29 fix, and false alarms on the writer's own notes are what got the
comment stripper written in the first place.

---

## Confirmed still open (not a new finding)

**OI-MOAT-33 / mixed delimiter** reproduces exactly as documented.
`a12_mixed.md`: `A <!-- note －－＞ MongoDB lost all data under load --> B is fine [S1].`
→ claim text judged is `"A   B is fine [S1]."`, `UNGROUNDED`, gate FAIL. The
fabrication is deleted; the draft only fails because the residue does not ground.

**OI-MOAT-26 fix holds.** `a11_fw_comment.md` (the original full-width attack)
→ `FAIL`, both halves scored UNGROUNDED with the `<!--` / `-->` still visible in
the quoted claim text. Correct.

---

# ATTACKS THAT FAILED

Every hypothesis below was built, run against the same store, and did **not**
reproduce. Drafts are in the scratchpad.

1. **Four-backtick fence (`a3_quad.md`)** — hypothesis: ```` ```` ```` fences hide
   delimiters from `_CODE_SPAN_RE` the way `~~~` does. Refuted: the `` ```.*?``` ``
   alternative matches inside the 4-backtick runs, the comment is not stripped, the
   fabrication is scored `UNCITED`, gate `FAIL` 33.3.
2. **Lone CR line ending (`a7_cr.md`, `### TODO\rMongoDB …`)** — hypothesis: `^`/`$`
   in Python do not break on `\r`, so no paragraph break is inserted and the
   sentence welds. Refuted: syntok segments on `\r` regardless; fabrication scored
   `UNCITED`, gate `FAIL` 50.0.
3. **Setext header (`a9_setext.md`, `TODO\n====`)** — hypothesis: a renderer-visible
   heading the gate does not treat as a header. Confirmed as a *mismatch* but
   fail-closed: the whole block welds into one scored `FACTUAL` claim
   (`"TODO\n====\nMongoDB lost all data under load."`), `UNCITED`, gate `FAIL`.
   No escape; the only cost is an ugly quoted claim text.
4. **Double-backtick span across a blank line (`b4_dbl_blank.md`)** — hypothesis:
   `` ``.*?`` `` is DOTALL, but CommonMark forbids a blank line inside a code span,
   so the gate protects text the renderer shows as prose. Confirmed as a mismatch,
   but it only *protects* (strips less): both fragments scored `UNCITED`, gate
   `FAIL` 33.3. Not usable in the PASS direction.
5. **Delimiter in a single-backtick span, closer in prose (`b5_codespan_ctrl.md`)** —
   the OI-MOAT-29 control. Fix holds: all three sentences scored, gate `FAIL` 25.0.
6. **Header inside a ``` fence (`d7_fence_header.md`)** — hypothesis: `# TODO` inside
   a fence gets the exemption while the reader sees code. Refuted: the fabrication
   is scored `UNCITED`, gate `FAIL`. Fail-closed.
7. **Citation/numeric inside a welded header (`b6_tab_cited.md`, `b7_7hash_num.md`)** —
   hypothesis: R8B-03 escapes even for cited or numeric fabrications. Refuted (see
   the bounding note in R8B-03): `UNVERIFIED_CITATION` and `UNCITED` respectively,
   both `FAIL`.
8. **Multi-paragraph meaning reversal via tilde fence / indented block
   (`b2_reverse.md`, `b3_reverse_tilde.md`, `c3_tilde_reverse.md`)** — hypothesis:
   deleting the negation mid-sentence re-welds the two halves into one grounded
   sentence. Refuted in that form: the paragraph breaks survive the strip, syntok
   emits fragments, and the uncited fragment holds the gate at `NEEDS_WORK` 66.7 /
   `FAIL` 50.0. The *single-line* forms of the same idea do reproduce — they are
   R8B-01c and R8B-02b.
9. **Full-width comment delimiters (`a11_fw_comment.md`)** — the OI-MOAT-26 control.
   Fix holds.
