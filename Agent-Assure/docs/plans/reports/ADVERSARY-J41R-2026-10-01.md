# Adversary report — J-41r / D-52 comment rule

Target: `_strip_html_comments_outside_code` + `_is_block_comment` in
`Agent-Assure/scripts/ground_check.py` (HEAD `527a3c2`, branch
`launch-claim-2026-10-01`).

**Verdict: J-41r: REFUTED — 3 ERROR-B** (one mechanism class with three
delimiter spellings, plus one independent amplifier that is itself ERROR-B when
combined, plus one renderer-conditional class).

## Method and renderer truth

Nothing is asserted from a docstring. Every row below was produced by:

1. `uv run python3` driving `ground_check.decompose/classify/score_report`
   against a one-record verbatim store (same fixture shape as
   `tests/red_team_moat/test_moat_j41r_comment_rule.py`). The harness prints
   the stripped text, `gate`, `grounding_score`, and **every `per_claim` text**,
   because `gate != PASS` proves nothing about whether the hidden prose entered
   the denominator.
2. Renderer truth established with **two** Markdown implementations —
   `commonmark` (the reference implementation) and `markdown` (python-markdown)
   — and then the resulting HTML parsed with **`html5lib`** (spec HTML parsing),
   extracting only *visible* text, i.e. explicitly **discarding comment nodes**.

That last step is load-bearing and it changed the result. Markdown block
structure is **not** the final arbiter of what a reader sees: when CommonMark
ends an HTML block early it emits the bare `<!-- …` as *raw HTML*, and the
browser's HTML tokenizer then re-pairs that opener with the next `-->`, hiding
the prose again. An earlier pass of this review used an extractor that leaked
comment text and would have reported four false ERROR-Bs. Corrected below.

Scratch files: `/tmp/claude-501/b/adv1/`. No file under `scripts/`,
`calibration/`, or any existing test was modified.

---

## ERROR-B #1 — the closer grammar is narrower than HTML's: an HTML-level abrupt close on the opener line (`<!-->`)

**Mechanism.** The gate models a comment as `<!--` … `-->` only
(`_HTML_COMMENT_RE = <!--.*?-->`). The HTML comment grammar has *more* ways to
close. `<!-->` is, per the HTML tokenizer's *abrupt-closing-of-empty-comment*
state, a **complete empty comment**; CommonMark's HTML-block type 2 end
condition ("line contains the string `-->`") is also satisfied on that very
line, because `<!-->` literally contains the substring `-->`. So the comment
begins and ends on line 1 — and every line after it is ordinary visible prose.

The gate's regex cannot see that: `<!--` consumes four characters, and the first
`-->` it can then find is the one further down the page. `_is_block_comment`
then approves the span (opener is first non-whitespace at 0 columns; closer is
last non-whitespace on its line; no blank line between), and the prose in
between is **deleted from the scored denominator**.

This is at **top level**: no list, no blockquote, no code region, no backslash,
no blank line. It therefore refutes the claim's own central sentence —
"CommonMark's HTML-block rule only fires at line start, and when it fires
everything through the closing line genuinely IS inside the comment." Here the
rule fires *and closes* on the opener line, and the gate strips far past it.

**Draft (`R12-05`):**

```
Redis replicates to three replicas [S1].

<!-->
MongoDB lost all customer data under sustained write load.
-->
```

**Actual gate output:**

```
====================== R12-05_abrupt_close
  draft repr: 'Redis replicates to three replicas [S1].\n\n<!-->\nMongoDB lost all customer data under sustained write load.\n-->\n'
  stripped  : 'Redis replicates to three replicas [S1].\n\n \n'
  gate=PASS score=100.0
   per_claim: 'Redis replicates to three replicas [S1].'
  FAB PRESENT IN DENOMINATOR: False
```

**Renderer truth:**

```
R12-05_abrupt          commonmark       visible=True
R12-05_abrupt          py-markdown      visible=True
```

(`commonmark` HTML: `<p>Redis …</p>\n<!-->\n<p>MongoDB lost all customer data
under sustained write load.\n--&gt;</p>\n` — the fabrication is a `<p>`.)

Gate PASS, score 100.0, one claim scored, fabrication visible to the reader in
both renderers. ERROR-B.

### Same mechanism, second spelling: `<!--->` (`R12-05b`)

`<!--->` is also an abrupt close (comment-start-dash → `>`). Identical result:

```
====================== R12-05b_abrupt_close3
  stripped  : 'Redis replicates to three replicas [S1].\n\n \n'
  gate=PASS score=100.0
   per_claim: 'Redis replicates to three replicas [S1].'
  FAB PRESENT IN DENOMINATOR: False
R12-05b_abrupt3        commonmark       visible=True
R12-05b_abrupt3        py-markdown      visible=True
```

### Same mechanism, third spelling: `--!>` (`R12-06`)

The HTML tokenizer closes a comment on `--!>` as well. CommonMark does *not*
treat `--!>` as its block end condition, so the raw-HTML block continues and the
browser is the one that closes the comment early — the prose after `--!>` is
emitted as raw text and is visible.

```
====================== R12-06_bang_close
  draft repr: 'Redis replicates to three replicas [S1].\n\n<!-- note --!>\nMongoDB lost all customer data under sustained write load.\n-->\n'
  stripped  : 'Redis replicates to three replicas [S1].\n\n \n'
  gate=PASS score=100.0
   per_claim: 'Redis replicates to three replicas [S1].'
  FAB PRESENT IN DENOMINATOR: False

R12-06_bang_close      commonmark       visible=True
R12-06_bang_close      py-markdown      visible=True
```

Note this one is a *same-page* demonstration that the attacker also controls
whether the early close is CommonMark's decision or the browser's. Two
independent layers can end the comment; the gate models neither.

**Why this is not "just another blacklist row".** The three spellings are one
fact: **`-->` is not the HTML comment-close grammar.** The gate's pairing
function is wrong, not its enumeration. A faithful fix pairs the opener with the
*earliest* position at which **either** layer closes a comment — minimally
`-->`, `--!>`, and the abrupt forms `<!-->` / `<!--->` — and, because the
attacker writes the document, any residual uncertainty must *reject* the
candidate rather than extend the span.

---

## ERROR-B #2 (amplifier, and ERROR-B in composition) — `_BLANK_LINE_BETWEEN_RE` is void on CRLF input

`_BLANK_LINE_BETWEEN_RE = \n[ \t]*\n`. A CRLF blank line is
`\r\n\r\n`: between the two `\n`s sits a `\r`, which is not in `[ \t]`. **The
guard never matches on a CRLF document.** The no-blank-line condition is the
one the design added specifically to block R11A-02, and it is absent from every
CRLF draft — Windows editors, `core.autocrlf=true` checkouts, anything pasted
through a Windows toolchain.

By itself this is bounded by whether a blank line changes renderer visibility
(see the renderer-conditional section). Composed with ERROR-B #1 it removes the
only bound on how much text one stray delimiter deletes:

**Draft (`R12-07`), CRLF, `<!-->` opener, two blank-line-separated paragraphs:**

```
====================== R12-07_crlf_plus_abrupt_multiparagraph
  draft repr: 'Redis replicates to three replicas [S1].\r\n\r\n<!-->\r\n\r\nMongoDB lost all customer data under sustained write load.\r\n\r\nThe audit found zero control failures across all 42 vendors.\r\n\r\n-->\r\n'
  stripped  : 'Redis replicates to three replicas [S1].\r\n\r\n \r\n'
  gate=PASS score=100.0
   per_claim: 'Redis replicates to three replicas [S1].'
  FAB PRESENT IN DENOMINATOR: False
```

Renderer truth (comment nodes discarded):

```
commonmark  MongoDB visible: True | audit visible: True
py-markdown MongoDB visible: True | audit visible: True
```

Two fabrications, one of them numeric ("zero control failures across all 42
vendors" — exactly the absence+number class the gate exists to catch), both
reader-visible, **neither scored**, gate PASS 100.0. ERROR-B.

Minimal correct repair for this half: normalise line endings before the
structural scan, or widen the class to `\r?\n[ \t]*\r?\n`. It is a one-token
regex gap guarding a condition the design calls load-bearing.

---

## ERROR-B #3 (renderer-conditional) — container end with NO blank line: `_is_block_comment` approves a span the Markdown block model ends early

The `r11a-02` fixture uses a blank line and is correctly rejected. **Drop the
blank line and the same attack is accepted.** A line-start opener at ≤3 columns
*inside a list item* opens an HTML block scoped to that container; the container
ends at a lazy outdent or a new list marker, and CommonMark ends the HTML block
with it — before the `-->`.

```
====================== R12-01_list_lazy_outdent
  draft repr: '… \n\n- Redis replicates to three replicas [S1].\n  <!-- note\nMongoDB lost all customer data under sustained write load.\n  -->\n'
  stripped  : 'Redis replicates to three replicas [S1].\n\n- Redis replicates to three replicas [S1].\n   \n'
  gate=PASS score=100.0
   per_claim: 'Redis replicates to three replicas [S1].'
   per_claim: '- Redis replicates to three replicas [S1].'
  FAB PRESENT IN DENOMINATOR: False
```

Same for `R12-02` (`- MongoDB …` as a new list marker) and `R12-03` (empty list
item `-` then `  <!--`), both gate PASS 100.0 with the fabrication absent from
`per_claim`. CommonMark confirms the early block end:

```
R12-03 cm html: '<p>Redis …</p>\n<ul>\n<li>\n<!-- note\n</li>\n</ul>\n<p>MongoDB lost all customer data under sustained write load.\n--&gt;</p>\n'
```

**Honest severity caveat — this is why it is ranked third.** Under *default*
raw-HTML rendering the reader does **not** see the fabrication, because the
browser's tokenizer re-pairs the emitted bare `<!-- note` with the downstream
`-->`:

```
R12-01_list_lazy       commonmark       visible=False
R12-01_list_lazy       py-markdown      visible=False
R12-01_list_lazy       commonmark-SAFE  visible=True
R12-03_empty_item      commonmark       visible=False
R12-03_empty_item      py-markdown      visible=False
R12-03_empty_item      commonmark-SAFE  visible=True
```

`commonmark-SAFE` is `HtmlRenderer({'safe': True})` — the sanitising mode used
by every renderer that strips or escapes raw HTML (the GitHub/GitLab/comment-box
class, and any pipeline that escapes HTML before display). **In that renderer
class the fabrication is visible and the gate says PASS 100.0**, so this is
ERROR-B wherever the draft is consumed through a sanitising renderer, and
cosmetic where raw HTML passes through. The same `commonmark-SAFE` column on the
top-level control (`<!-- note\nFAB\n-->`) is `visible=False`, so this is not an
artefact of the mode — it is specific to the early block end.

The design document asserts the no-blank-line condition "then blocks R11A-02".
It blocks the *fixture*, not the *class*: the blank line was never necessary to
the attack. That is the fourth consecutive instance of this repo's own diagnosis
— a condition fitted to the shape in hand.

---

## ERROR-A findings (recoverable, listed for completeness)

- **A-1. A 4-space-indented authoring note inside a numbered list is never
  stripped.** `_INDENTED_CODE_RE` matches `^ {4,}` with no awareness of list
  content indent, so `1.  item\n    <!-- note\n    … \n    -->` is "protected"
  and the note is scored. Correct direction, real false-alarm cost on ordinary
  documents.
- **A-2. Any line ending that is not `\n` disables the block branch entirely.**
  `_MULTILINE_OPEN_RE` requires `\A` or `\n`, so a lone `\r` (classic-Mac) or a
  Unicode line separator (U+2028/U+2029/U+0085) before the opener yields no
  match and the comment is scored. Fail-closed, so not ERROR-B — but it is the
  mirror image of ERROR-B #2 and shows that line-ending normalisation was never
  done anywhere on this path.

## Probes that found nothing (negative results, so the next round does not repeat them)

- `_MULTILINE_OPEN_RE`'s `\Z` with `search(text, 0, start)`: `\Z` anchors at
  `endpos`, so the capture is genuinely the opener's own line prefix. No
  multi-line prefix can make it match a different line. Clean.
- Blockquote openers: `>` is not in `[ \t]`, so `> <!--` is rejected, and a
  lazy continuation cannot open an HTML block. Verified, not assumed.
- `_indent_columns` vs `_code_line_spans` boundary: ` \t` is 4 columns (rejected
  as a block) and is *not* matched by `_INDENTED_CODE_RE` (not protected) — so
  it is rejected by the block branch, which is fail-closed. 3 spaces is a valid
  opener and CommonMark agrees. No gap.
- `_HTML_COMMENT_RE` vs `_SAME_LINE_COMMENT_RE`: both are non-greedy and differ
  only in DOTALL, so a `_HTML_COMMENT_RE` match containing no `\n` always
  `fullmatch`es the same-line pattern and one containing a `\n` never does.
  They cannot disagree. No finding.
- Multiple comments / multiple `-->` on one line: non-greedy pairing is
  left-to-right and nearest-closer, which cannot bridge two comments. No finding.
- `continue`-on-rejection never reconsiders a later closer: every consequence is
  *less* stripping, i.e. more text scored. ERROR-A direction only.
- Form feed / vertical tab / NBSP "blank" lines: CommonMark's blank line is
  spaces and tabs only, so the gate's regex is *stricter* than the renderer
  here, not looser.
- `\\<!--` (even number of backslashes): not escaped per `_is_escaped`, and the
  renderer shows a literal backslash then opens a comment. Faithful.
- HTML blocks of other types already open (`<pre>`, `<div>`, `<script>`) around
  a line-start opener: the comment remains a comment in the raw HTML and stays
  hidden. Faithful.

## Unreproduced hypotheses

- **U-1.** A GFM table cell or footnote definition acting as a container that
  ends before the `-->`. Not tested: neither `commonmark` nor plain
  python-markdown implements GFM tables, so no renderer truth could be
  established here with the tools used.
- **U-2.** `<!--` immediately following a setext heading underline, or inside a
  link reference definition, producing an early block end. Probed informally and
  found faithful in `commonmark`; not driven through the gate, so it is recorded
  as open rather than cleared.

## One standing documentation defect

The `CEILING:` note above `_SAME_LINE_COMMENT_RE` states that the worst case is
"a same-line comment inside undetected code is stripped, removing CODE text from
the denominator, never reader-visible prose … It is no longer on the Error-B
path." The block branch added by J-41r *is* on the Error-B path (#1 and #3
above), and the CEILING text describes only the pre-J-41r same-line rule. The
falsifiable boundary is now false as written.

---

**J-41r: REFUTED — 3 ERROR-B**
