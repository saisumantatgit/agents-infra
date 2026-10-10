# Red-team round 10, Adversary A — the DENOMINATOR

Scope: text a reader can see on the page that never reaches the gate's scored
claim set. Target: the J-27 / D-43 closure claim committed as `3610c26` on
`provenance-fix-2026-10-01`.

**Verdict: J-27 CLOSURE: REFUTED — 5 ERROR-B.**

The claim is that `_code_line_spans` + `_is_escaped` make "a comment delimiter a
comment only where a renderer says so". It does not. Five independent mechanisms
still let a stray `<!--` pair with a downstream `-->` and delete reader-visible
prose from the denominator; **four of them certify `PASS`, score `100.0`, empty
retained appendix**, over a page whose reader can plainly read the fabrication.

The recorded project failure mode repeated exactly: the fix closed the shapes its
own fixtures used (bare tilde fences, bare 4-space indents, bare `\<!--`) and left
the class open. `tests/red_team_moat/test_moat_j27_comment_blocks.py` — 17 passed,
0.08s — is green on the tree that hides every draft below.

## Method

- Gate run through `ground_check.decompose` → `classify` → `score_report` (the
  same path `scripts/ground_check.py --draft/--store` takes), so `per_claim` texts
  are shown for every finding. `gate != PASS` alone is never accepted as evidence.
- Renderer ground truth from **two** real renderers: `commonmark.py 0.9.1`
  (CommonMark 0.29 reference port) and `python-markdown 3.11`. A finding is
  only ERROR-B when a renderer shows the delimiters as *escaped literal text*
  (`&lt;!--` / `--&gt;`) or as `<pre><code>` content, **and** shows the
  fabrication as visible prose.
- Store (all findings), one verbatim source:

```json
{"source_id":"S1","url":null,"file_path":"/tmp/a","fetched_at":"2026-09-13T00:00:00Z","tool":"Read","content_sha256":"aaaa…(64)","text":"Redis replicates to three replicas in the primary datacenter and fails over automatically.","full_text_source":"verbatim","captured_via":"inline","query_provenance":"q1"}
```

- `G` = `"Redis replicates to three replicas in the primary datacenter and fails over automatically [S1]."`
- `FAB` = `"MongoDB lost all customer data under sustained write load."` (nowhere in the store)
- Command, per finding: `uv run python3 scripts/ground_check.py --draft <f>.md --store store.jsonl --json`
  (reproductions were driven through the same functions; scratch at `/tmp/claude-501/aa/r10a/`).

---

## ERROR-B 1 — an inline `<!--` is literal in EVERY renderer, and no code region is involved at all

**Severity: highest.** This needs no code block, no fence, no tab, no exotic
character. It is the shape a real author produces by typing a working note at the
end of a paragraph and another one further down. J-27 built an elaborate
*code-region* detector; this mechanism never touches a code region.

Draft (repr):

```
'Redis replicates to three replicas in the primary datacenter and fails over automatically [S1]. <!-- draft note\n\nMongoDB lost all customer data under sustained write load.\n\n--> Redis replicates to three replicas in the primary datacenter and fails over automatically [S1].\n'
```

Gate output, verbatim:

```
gate=PASS score=100.0 retained_appendix=[]
   [GROUNDED] 'Redis replicates to three replicas in the primary datacenter [S1]'
   [GROUNDED] 'fails over automatically [S1].'
   [GROUNDED] 'Redis replicates to three replicas in the primary datacenter [S1]'
   [GROUNDED] 'fails over automatically [S1].'
FABRICATION IN DENOMINATOR: False
```

Renderer — **both agree**, the delimiters are literal and the fabrication is a
visible paragraph:

```html
<p>Redis replicates … [S1]. &lt;!-- draft note</p>
<p>MongoDB lost all customer data under sustained write load.</p>
<p>--&gt; Redis replicates … [S1].</p>
```

**Should have been:** the `MongoDB …` sentence in `per_claim`, verdict
`UNGROUNDED`, gate `FAIL`.

**Mechanism.** `_HTML_COMMENT_RE = re.compile(r"<!--.*?-->", re.DOTALL)`
(`scripts/ground_check.py:660`) matches across blank lines, and
`_strip_html_comments_outside_code` (`:535-559`) imposes no block-structure
constraint at all — only "is this offset inside a code region". Per CommonMark,
raw-HTML *inline* parsing is confined to a single block's inlines: a `<!--` in
inline position with no `-->` in the same block is literal text, and a `-->` in
inline position with no preceding opener in the same block is literal text. An
HTML *block* (type 2) requires the `<!--` at line start (≤3 spaces indent) — which
is exactly the case the gate may legitimately strip. The gate draws no
inline/block distinction.

**Note on the rejected alternative.** `scripts/ground_check.py:472-476` records
"a comment may not span a blank line" as *considered and rejected* because it is
**not sufficient**. That reasoning is correct and irrelevant: the rule is *necessary*
and was never implemented, so this shape stayed open by construction. Sufficiency
was used to justify omitting a necessary condition.

---

## ERROR-B 2 — every code region inside a blockquote is invisible to `_code_line_spans`

`_FENCE_RE` (`:474`) is `^(?P<indent> {0,3})(?P<fence>`{3,}|~{3,})(?P<info>.*)$`
and `_INDENTED_CODE_RE` (`:475`) is `^(?: {4,}|\t)`. Both anchor at `^` of a raw
line. A blockquote marker `>` occupies column 0, so **no** code block inside a
blockquote is ever detected — fenced or indented.

### 2a — tilde fence in a blockquote

```
'…[S1].\n\n> ~~~\n> <!--\n> ~~~\n\nMongoDB lost all customer data under sustained write load.\n\n> ~~~\n> -->\n> ~~~\n'
```

```
gate=PASS score=100.0 retained_appendix=[]
   [GROUNDED] 'Redis replicates to three replicas in the primary datacenter [S1]'
   [GROUNDED] 'fails over automatically [S1].'
   [GROUNDED] '> ~~~\n>  \n> ~~~'
FABRICATION IN DENOMINATOR: False
```

commonmark.py: `<blockquote><pre><code>&lt;!--</code></pre></blockquote>` then
`<p>MongoDB …</p>`. python-markdown renders the same text as a visible paragraph
`~~~ &lt;!-- ~~~` — under **both**, the delimiter is literal and the fabrication
is visible.

A *backtick* fence in a blockquote is protected only by accident: the
` ```.*?``` ` alternative of `_CODE_SPAN_RE` (`:449`, DOTALL) happens to span it.
Tildes have no such alternative, so the tilde form is the live hole — the same
`_CODE_SPAN_RE`-only asymmetry OI-MOAT-29 was written to remove.

### 2b — indented code in a blockquote (no fence characters anywhere)

```
'…[S1].\n\n>     <!--\n\nMongoDB lost all customer data under sustained write load.\n\n>     -->\n'
```

```
gate=PASS score=100.0 retained_appendix=[]
   [GROUNDED] 'Redis replicates to three replicas in the primary datacenter [S1]'
   [GROUNDED] 'fails over automatically [S1].'
   [GROUNDED] '>'
FABRICATION IN DENOMINATOR: False
```

**Both** renderers: `<blockquote><pre><code>&lt;!--</code></pre></blockquote>`,
`<p>MongoDB …</p>`, `<blockquote><pre><code>--&gt;</code></pre></blockquote>`.

---

## ERROR-B 3 — tab-expanded indentation: `space + tab` is column 4 to a renderer and column 1 to the regex

CommonMark expands tabs to 4-column tab stops before measuring indentation.
`" \t<!--"` therefore begins at column 4 and is an **indented code block**.
`_INDENTED_CODE_RE = ^(?: {4,}|\t)` matches neither `^ {4,}` (one space) nor
`^\t` (the tab is not first). The claim "indented code blocks (4+ spaces or a
tab)" is a character-count rule where CommonMark has a column rule.

```
'…[S1].\n\n \t<!--\n\nMongoDB lost all customer data under sustained write load.\n\n \t-->\n'
```

```
gate=PASS score=100.0 retained_appendix=[]
   [GROUNDED] 'Redis replicates to three replicas in the primary datacenter [S1]'
   [GROUNDED] 'fails over automatically [S1].'
FABRICATION IN DENOMINATOR: False
```

**Both** renderers: `<pre><code>&lt;!--</code></pre>`, `<p>MongoDB …</p>`,
`<pre><code>--&gt;</code></pre>`. `"  \t"` and `"   \t"` are the same class.

Note this is also the counter-intuitive-direction failure the J-27 comment warns
about: the scanner is *not* generous here, it is strictly narrower than CommonMark.

---

## ERROR-B 4 — `str.splitlines()` invents line boundaries CommonMark does not have

`_code_line_spans` walks `text.splitlines(keepends=True)` (`:495`).
`str.splitlines` splits on `\v \f \x1c \x1d \x1e \x85    ` in addition
to `\n \r \r\n`. CommonMark line endings are **only** `\n`, `\r`, `\r\n`. Every
extra split point is a phantom line boundary: it ends a code region one "line"
early in the scanner while the renderer keeps it open, and the newly-exposed text
is scanned for delimiters.

### 4a — phantom boundary ends an indented code block (clean PASS)

```
'…[S1].\n\n    Redis replicates to three replicas in the primary datacenter and fails over automatically [S1]. <!--\n\nMongoDB lost all customer data under sustained write load.\n\n    Redis replicates … [S1]. -->\n'
```

```
gate=PASS score=100.0 retained_appendix=[]
   [GROUNDED] 'Redis replicates to three replicas in the primary datacenter [S1]'
   [GROUNDED] 'fails over automatically [S1].'
   [GROUNDED] 'Redis replicates to three replicas in the primary datacenter [S1]'
   [GROUNDED] 'fails over automatically [S1].'
FABRICATION IN DENOMINATOR: False
```

**Both** renderers put the whole line, U+2028 and `&lt;!--` included, inside
`<pre><code>`, and the fabrication in a visible `<p>`. `\f` (`'    x\f<!--'`) and
`\x85` reproduce identically (verified; with a bare `x` carrier the residue
claim is `UNCITED` so the gate lands on `NEEDS_WORK` — the fabrication is gone
either way).

### 4b — phantom boundary forges a fence CLOSER (renderer-dependent)

```
'…[S1].\n\n```\ncode\nq ```\n<!--\nMongoDB lost all customer data under sustained write load.\n-->\n```\n'
```

```
gate=NEEDS_WORK score=66.7
   [GROUNDED] 'Redis replicates to three replicas in the primary datacenter [S1]'
   [GROUNDED] 'fails over automatically [S1].'
   [UNCITED] '```\ncode\nq ```'
   [GROUNDED] '```'
FABRICATION IN DENOMINATOR: False
```

commonmark.py keeps the fence open and renders the whole region — fabrication
included — inside `<pre><code>`, visible: **ERROR-B**. python-markdown instead
emits a real `<!-- … -->` there, hiding it: not ERROR-B on that renderer. Labelled
ERROR-B on the CommonMark spec reading (which GitHub, cmark and commonmark.py all
implement), with the divergence stated.

---

## ERROR-B 5 — a CommonMark code span may cross a line ending; `_CODE_SPAN_RE` says it may not

`_CODE_SPAN_RE`'s single-backtick alternative is `` `[^`\n]*` `` (`:449`) — `\n`
excluded. CommonMark code spans may contain line endings (they are converted to
spaces). So `` `x\ny <!--` `` is a code span whose content ends in a literal
`<!--`, and the gate does not see it as code.

```
'…[S1]. `x\ny <!--` \n\nMongoDB lost all customer data under sustained write load.\n\n`z\nw -->` Redis replicates … [S1].\n'
```

```
gate=NEEDS_WORK score=75.0
   [GROUNDED] 'Redis replicates to three replicas in the primary datacenter [S1]'
   [GROUNDED] 'fails over automatically [S1].'
   [UNGROUNDED] '`x\ny  ` Redis replicates to three replicas in the primary datacenter [S1]'
   [GROUNDED] 'fails over automatically [S1].'
FABRICATION IN DENOMINATOR: False
```

**Both** renderers: `<code>x y &lt;!--</code>` / `<code>z w --&gt;</code>`, with
`<p>MongoDB …</p>` between them. The fabrication is deleted from the denominator;
the surviving carrier happens to read `UNGROUNDED`, so this one lands on
`NEEDS_WORK` rather than `PASS` **by luck, not by guard** — as findings 1–4 show,
an attacker chooses a carrier that grounds.

---

## ERROR-A 1 — a rejected match is abandoned, never retried with a later closer

`_strip_html_comments_outside_code` `continue`s on a rejected candidate (`:550-554`)
and never reconsiders the same opener against a later, unprotected `-->`.

```
draft    'Visible one.\n\n<!-- note `-->` more\n\nHidden by renderer.\n\nreal -->\n\nVisible two.\n'
stripped 'Visible one.\n\n<!-- note `-->` more\n\nHidden by renderer.\n\nreal -->\n\nVisible two.\n'   (unchanged)
```

Here `<!--` *is* at line start, so CommonMark opens an HTML block (type 2) that
runs to the line containing the first `-->` — code spans do not exist inside an
HTML block, so the renderer hides "Hidden by renderer." while the gate scores it.
Recoverable (extra claims, possible false alarm), never fail-open. **Leave it.**
Any "repair" here moves text *out* of the denominator and is the wrong direction.

## Cosmetic 1 — the docstring overstates what is checked

`_strip_html_comments_outside_code` (`:537-540`) says a comment is removed "only
when BOTH delimiters sit outside every code region". The code tests two single
offsets: `_protected(m.start())` — the `<` of `<!--` — and `_protected(m.end()-1)`
— the `>` of `-->`. Nothing checks the rest of either delimiter, nor whether the
span crosses a code region. No exploit was found through the partial-delimiter
gap; the wording should be corrected to what is tested.

## Cosmetic 2 — `_strip_html_comments` (`:414`) is dead in the product

Only `tests/red_team_moat/test_moat_r7_comment_order.py` imports it; nothing under
`scripts/` calls it. Its docstring still reads as if it were the live stripper and
states the D-17 rationale that `_strip_html_comments_outside_code` now owns.

## Checked and CLEAN — direction 3 of the brief is not exploitable

The brief asked whether an unclosed fence can make the gate ignore visible prose
with no comment involved. It cannot. `_code_line_spans` has exactly one caller,
`scripts/ground_check.py:542`, inside the comment stripper; its spans only ever
*protect* delimiters. Fenced and indented code CONTENT is passed to `decompose`
and scored like any other text (visible above: `'```\ncode\nq ```'` and
`'> ~~~\n>  \n> ~~~'` both appear in `per_claim`). An unclosed tilde fence at the
top of a draft removes nothing from the denominator — it only makes the gate
*less* willing to strip. That part of the J-27 design is sound, and it is why
every finding above required a comment pair.

## Unreproduced hypotheses (kept separate)

- `<textarea>` / `<script>` / `<style>` HTML blocks (CommonMark HTML block type 1)
  pass raw to the browser; in `<textarea>` a `<!--` is literal *visible* text.
  Not reproduced: no realistic draft shape built, and `<pre>`/`<code>` do **not**
  work (the browser still parses comments inside them, so the reader sees nothing
  — no ERROR-B there).
- Link reference definitions and autolink destinations as literal-text contexts.
  Not probed.
- `\v` (`\x0b`), `\x1c`–`\x1e` as `splitlines` split points: same mechanism as
  ERROR-B 4, asserted from `str.splitlines` documentation but not individually
  reproduced (`\f`, `\x85`, ` ` were).

## What a real fix has to be

Not a sixth special case. The four PASS-ing mechanisms are all the same defect in
different clothes: **`_strip_html_comments_outside_code` decides a Markdown
question with a regex over raw text plus a hand-rolled line scanner, and the
scanner's model of "line" and "code" is narrower than CommonMark's in at least
four places.** Every J-27 round has added one more surface property (fence char,
fence length, indent count, backslash parity); the author controls all of them.

The property an attacker cannot give up is **block structure**: the fabrication
must be a visible block, so the opener and the closer must sit in *different*
blocks. A necessary condition that holds for all five findings, and that no
attacker can evade without putting the fabrication inside the comment (where the
reader also loses it):

> a comment is stripped only when its opener and its closer lie in the same
> block — concretely, when no blank line and no block-marker change (`>` prefix,
> list marker, fence line, ATX heading) separates them — UNLESS the opener is at
> line start with ≤3 spaces of indent, which is a genuine CommonMark HTML block
> and may legitimately run to its `-->`.

That is fail-closed (it strips strictly less than today) and it closes 1, 2a, 2b,
3, 4a, 4b and 5 at once, without the scanner needing to model tabs, blockquotes,
Unicode separators or multi-line code spans correctly. Recommended over extending
`_code_line_spans` a fifth time, because it keys on a property of the *document*
rather than on a character the author picks.

## Load-bearing assumption

That "visible on the page" means visible in a CommonMark-family Markdown renderer
(commonmark.py / cmark / GitHub) rather than in whatever actually consumes an
Agent-Assure draft. If Agent-Assure drafts are read as **plain text** — in a
terminal, a diff, a `cat` — then the delimiters are visible in every case here
and all five findings stand, harder. If drafts are read through a renderer that
strips comments *more* aggressively than CommonMark (a preprocessor that removes
`<!--…-->` from raw text before parsing, i.e. one that behaves exactly like the
gate), then findings 2–5 become cosmetic and finding 1 with them — the gate would
be faithful to that pipeline, and the invariant to write down would be "the gate
and the publisher must share one stripper", not "the gate must follow CommonMark".
Nothing in the repo pins which renderer is authoritative; that is the single fact
that would flip this verdict.

---

**J-27 CLOSURE: REFUTED — 5 ERROR-B**
