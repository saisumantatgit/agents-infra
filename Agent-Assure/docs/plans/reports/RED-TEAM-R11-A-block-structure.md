# Red-team round 11, adversary A — the DENOMINATOR and J-28B's block rule

**Scope.** Visible page text that never reaches the scored claim set, via
`_strip_html_comments_outside_code` (J-28B / D-45).

**Verdict: J-28B: REFUTED — 7 ERROR-B (two mechanisms).**

Counts: **7 ERROR-B**, **1 ERROR-A**, 0 cosmetic, 1 unreproduced hypothesis.

**Renderer truth.** `commonmark` 0.9.x (the CommonMark reference port) is the
oracle throughout, cross-checked against `python-markdown`. Both installed
ad-hoc (`uv run --with commonmark --with markdown`), never added to the moat's
dependency path. "Visible" = the fabrication survives in the rendered HTML
*outside* any `<!--...-->` region (a comment that survives into HTML is still
invisible to a reader, so the check strips HTML comments from the rendered
output before looking).

**Evidence standard.** Every finding below prints the `per_claim` texts.
`gate != PASS` is never accepted as evidence; the three headline findings all
certify **PASS, grounding_score 100.0, `retained_appendix: []`** — a clean
certification over a page whose reader can plainly see the fabrication.

Fixtures: store = one verbatim record `S1` = "Redis replicates to three
replicas." `GOOD` = `Redis replicates to three replicas [S1].`
`FAB` = `MongoDB lost all customer data under sustained write load.`

Nothing under `scripts/`, `calibration/`, or any existing test was modified.
Scratch harness: `/tmp/claude-501/aa/r11a/probe.py`.

---

## FINDING R11A-01 — ERROR-B — `_spans_one_block` is blind to every block boundary except a blank line

**Mechanism.** `_spans_one_block` measures exactly two things: a blank line
(`_BLANK_LINE_RE`) and a change of `_blockquote_depth`. CommonMark has many
other *leaf-block starts that interrupt a paragraph*, and none of them is
visible to either measure. An opener that is **literal text** by J-28B's own
reasoning (mid-paragraph, so `_opens_html_block` is False) therefore satisfies
`_spans_one_block` across a boundary the renderer honours — the opener is in
one block, the closer in another, and the prose between them is deleted.

This is the same shape the rule was written to close (`test_r10a_01`, an
inline mid-paragraph opener); J-28B closed it *only for the blank-line
separator its fixture used*. The class is the project's recorded failure mode,
instance seven.

### R11A-01a — ATX heading (both renderers agree)

Draft:

```
Redis replicates to three replicas [S1]. <!-- hold
# Findings
MongoDB lost all customer data under sustained write load.
-->
```

`commonmark` output (identical in `python-markdown`):

```html
<p>Redis replicates to three replicas [S1]. &lt;!-- hold</p>
<h1>Findings</h1>
<p>MongoDB lost all customer data under sustained write load.
--&gt;</p>
```

The `<!--` is escaped to `&lt;!--` — literal text. The fabrication is a
rendered paragraph.

`_strip_html_comments_outside_code` returns:

```
'Redis replicates to three replicas [S1].  \n'
```

Gate:

```
{"grounding_score": 100.0, "gate": "PASS", "scored_claims": 1,
 "vacuous": false, "retained_appendix": []}
per_claim texts:
   * Redis replicates to three replicas [S1].
>>> FABRICATION IN DENOMINATOR = False
```

### R11A-01b — thematic break `***` (both renderers agree)

Draft: same, with `***` in place of `# Findings`.
`commonmark` renders `<hr />` between the two paragraphs; the fabrication is
visible in both renderers.

```
{"grounding_score": 100.0, "gate": "PASS", "scored_claims": 1,
 "vacuous": false, "retained_appendix": []}
per_claim texts:
   * Redis replicates to three replicas [S1].
>>> FABRICATION IN DENOMINATOR = False
```

### R11A-01c — list marker (commonmark; python-markdown does not interrupt)

Draft `…[S1]. <!-- hold\n- MongoDB lost…\n--> done.\n` →

```html
<p>Redis replicates to three replicas [S1]. &lt;!-- hold</p>
<ul>
<li>MongoDB lost all customer data under sustained write load.
--&gt; done.</li>
</ul>
```

Stripped text: `'Redis replicates to three replicas [S1].   done.\n'`;
`per_claim` = `['Redis replicates to three replicas [S1].   done.']`;
`FABRICATION IN DENOMINATOR = False`. Gate is FAIL here — **for the wrong
reason** (the mangled residue sentence), which is precisely why the per-claim
check, not the gate, is the evidence.

### R11A-01d — fenced code block opener interrupting the paragraph (commonmark)

Draft `…[S1]. <!-- hold\n```\n```\nMongoDB lost…\n--> done.\n` →
`<pre><code></code></pre>` between two paragraphs, fabrication visible.
Same deletion; `FABRICATION IN DENOMINATOR = False`.

Note the second-order point: the fence lies **between** the delimiters, and
`_protected` only tests `m.start()` and `m.end()-1`, so an intervening code
region neither protects nor blocks.

### R11A-01e — setext underline (commonmark)

Draft `…[S1]. <!-- hold\nSection Two\n===========\nMongoDB lost…\n-->\n` →
the opener line is absorbed into an `<h1>`, the fabrication is a separate
paragraph.

```
{"grounding_score": 100.0, "gate": "PASS", "scored_claims": 1,
 "vacuous": false, "retained_appendix": []}
per_claim texts:
   * Redis replicates to three replicas [S1].
>>> FABRICATION IN DENOMINATOR = False
```

### R11A-01f — HTML block of a different type (`<div>`, type 6) (commonmark)

Draft `…[S1]. <!-- hold\n<div>\nMongoDB lost…\n-->\n`. `<div>` opens a type-6
HTML block that interrupts the paragraph; the fabrication is emitted as raw
HTML **outside any comment**, so a browser shows it. Same deletion, PASS 100.0,
empty appendix.

**Severity.** Six independent reproductions of one class. Two of them
(01a, 01b) are confirmed visible in **both** renderers, so they do not depend
on which Markdown engine the reader uses. Each certifies PASS 100.0 with an
empty retained appendix.

---

## FINDING R11A-02 — ERROR-B — `_opens_html_block` ignores the CONTAINER, so a list-item comment strips the whole document below it

**Mechanism.** `_opens_html_block` tests only `text[line_start:index]` against
` {0,3}`. It has no notion of the *container* the line sits in. Inside a list
item, 2 spaces of indent is list-content indentation, not top-level indent —
the HTML block it opens is **scoped to the list item** and ends when the item
ends. J-28B's exemption then licenses stripping across blank lines all the way
to a `-->` that is in a completely different top-level block.

This is the exemption branch — the only path that may cross a blank line — and
therefore the highest-leverage one.

Draft:

```
- Redis replicates to three replicas [S1].
  <!-- note

MongoDB lost all customer data under sustained write load.

-->
```

`commonmark`:

```html
<ul>
<li>Redis replicates to three replicas [S1].
<!-- note
</li>
</ul>
<p>MongoDB lost all customer data under sustained write load.</p>
<p>--&gt;</p>
```

The comment is **unterminated inside the list item**; the fabrication renders
as its own visible paragraph and the `-->` renders as literal text.

Stripped text: `'- Redis replicates to three replicas [S1].\n   \n'`

```
{"grounding_score": 100.0, "gate": "PASS", "scored_claims": 1,
 "vacuous": false, "retained_appendix": []}
per_claim texts:
   * - Redis replicates to three replicas [S1].
>>> FABRICATION IN DENOMINATOR = False
```

**Renderer disagreement, stated honestly.** `python-markdown` keeps the whole
region inside the `<li>` as raw HTML, where a browser *would* hide it. So this
finding rests on the CommonMark reference semantics alone, unlike 01a/01b.
It is still ERROR-B under the project's stated oracle (CommonMark), and the
asymmetry rule says an unrecoverable error under *either* mainstream renderer
is not acceptable.

**Generality.** The same container blindness applies to any container whose
content indent is 1–3 columns — a list item is merely the cheapest. It is not
patched by adding list detection to `_spans_one_block`: the failure is in
`_opens_html_block`, the branch that bypasses `_spans_one_block` entirely.

---

## FINDING R11A-03 — ERROR-A — a note indented as list continuation is scored although no renderer shows it

**Mechanism.** `_INDENTED_CODE_RE` treats any 4-space-indented line as code
(deliberately generous, per J-27's comment). Inside a list item, 4 spaces is
*paragraph continuation*, not code. `_protected` then refuses to strip a
genuine, renderer-hidden authoring note, and the note enters the denominator.

Draft:

```
- item one

    <!-- TODO: check this figure -->
```

`commonmark` renders the comment as a real HTML comment inside the `<li>` —
invisible to the reader. The gate:

```
gate = FAIL
per_claim texts = ['- item one', '<!-- TODO: check this figure -->']
```

The author's TODO note is scored and single-handedly fails the draft. This is
the exact harm D-17's docstring names ("a gate that flags the writer's TODO
notes as ungrounded is not measuring the document the reader gets"), resurfacing
through the over-detection that J-27 chose. **Recoverable, low priority** — it
is the safe direction and must not be fixed by stripping more.

---

## UNREPRODUCED HYPOTHESIS

**U-1 — GFM table rows as a block boundary.** A table row (`| a | b |`)
interrupts a paragraph in GitHub-Flavored Markdown and is invisible to
`_spans_one_block`, which would make it a seventh instance of R11A-01.
Not reproduced: `commonmark` (the oracle used here) implements core CommonMark
and has no tables, so no renderer truth was established. Listed for the record
only.

## CONFIRMED, NOT CLAIMED NEW

Forged line boundaries: `str.splitlines` splits on U+2028/U+2029/U+0085/`\f`/
`\v`/`\x1c`–`\x1e` while CommonMark does not, and `_BLANK_LINE_RE` (`\n[ \t]*\n`)
does not. Known-open residue carried in from round 10; confirmed still present
by inspection, **not** counted in the totals above.

---

## What the findings say about the rule, not just the fixtures

J-28B replaced a blacklist of code regions with a two-predicate model of
document structure. Both predicates are **under-specified in the fail-OPEN
direction**:

- `_spans_one_block` claims to answer "same block?" but tests only two of
  CommonMark's block boundaries. Every boundary it cannot see is an attack.
  An enumeration of boundaries is a blacklist wearing a structural hat — which
  is the thing J-28B's own header comment says it was written to stop doing.
- `_opens_html_block` claims to answer "does this open an HTML block?" but
  reads three characters of a line and nothing about the container that line
  is in. An HTML block that a container terminates is not an HTML block that
  runs to its `-->`.

The asymmetric direction is the design lever and it points one way: **a
predicate that means "I could not determine the block structure" must return
the answer that strips LESS.** Concretely, `_spans_one_block` should require
that the segment be a single *line* run with no line that could start any leaf
block, and `_opens_html_block` should additionally require that the opener's
line be at container depth zero (no enclosing list item or blockquote) —
otherwise fall through to the same-block test. Both changes strictly reduce
stripping, so they cannot manufacture Error-B, and both cost Error-A only on
notes an author can trivially re-indent to column 0.

The repair is **not** in scope for this report (adversary A does not patch).

---

**J-28B: REFUTED — 7 ERROR-B**
