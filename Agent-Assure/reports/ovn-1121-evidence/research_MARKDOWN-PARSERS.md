# Pure-Python Markdown parsers for Agent-Assure render-before-decompose (research, 2026-11-21)

Verdict: use markdown-it-py (+ mdit-py-plugins footnote/deflist) for rendering; no pure-Python CommonMark parser gives inline source offsets except the brand-new Wenmode (pre-1.0).
Method: PyPI JSON API and GitHub API (licence, deps, dates), upstream READMEs/CHANGELOG, and running each parser locally in throwaway venvs (py3.9: markdown-it-py 3.0.0, mistune 3.3.4, marko 2.2.5, commonmark 0.9.2, Markdown 3.9, mistletoe 1.6.0; py3.14: markdown-it-py 4.3.0, mdit-py-plugins 0.7.0, mistune 3.4.0, wenmode 0.15.3). Test outputs are first-hand observation, not docs.

## 1. Comparison table

| Item | markdown-it-py (+mdit-py-plugins) | mistune | marko | commonmark.py | Python-Markdown | mistletoe | Wenmode (new) |
|---|---|---|---|---|---|---|---|
| Licence (SPDX) | MIT (GitHub API: MIT); plugins MIT | BSD-3-Clause | MIT | BSD-3-Clause per PyPI classifier; GitHub API says NOASSERTION | BSD-3-Clause | MIT | BSD-3-Clause (GitHub API) |
| Pure Python | yes | yes | yes | yes | yes | yes | yes (py>=3.10) |
| Runtime deps | mdurl~=0.1 only (linkify-it-py optional extra) | typing-extensions (py<3.11 only) | none (extras: pygments, python-slugify, objprint) | none on py3 (future on py2) | none | none | none declared |
| Latest release (PyPI) | 4.3.0, 2026-11-10 (4.2.0 2026-05-07, 4.1.0 2026-05-06, 4.0.0 2025-08-11, 3.0.0 2023-06-03) | 3.4.0, 2026-10-19 (3.3.x monthly) | 2.2.5, 2026-10-27 (2.2.x every 1-4 months) | 0.9.2, 2026-05-28 (previous 0.9.1 2019-10); repo ARCHIVED, README "deprecated... use markdown-it-py" | 3.11.3, 2026-11-05 | 1.6.0, 2026-07-11 | 0.15.3 2026-10-19; 1.0.0rc1 2026-10-21; repo created 2026-06-17 |
| CommonMark claim | README: "Follows the CommonMark spec for baseline parsing"; CHANGELOG 4.3.0: aligns with CommonMark 0.31.2 and markdown-it 15.0.x | docs: "compatible with CommonMark 0.31.2" | README: adheres to CommonMark 0.31.2 (badge) | port of commonmark.js (older spec; tested py2.7-3.8) | NOT CommonMark (marko README states it does not comply) | claims CommonMark compliance (unverified, not read) | "CommonMark-style" (README wording; exact spec version unverified) |
| GFM | `gfm-like` preset = commonmark + linkify + table + strikethrough; docs say it LACKS task lists and raw-HTML filtering. Footnotes via mdit-py-plugins `footnote_plugin`; deflist via `deflist_plugin`; tasklists via `tasklists_plugin` | plugins: strikethrough, table, footnotes, task_lists, def_list, url (all verified working) | `marko.ext.gfm` (table, strikethrough, autolink, task list; footnote is a separate ext, and `gfm` alone left `[^1]: ...` as plain text) | none | none core; `footnotes`, `tables`, `def_list` extensions; strikethrough NOT supported (`~~not~~` stays literal) | table, strikethrough (not read in detail) | `github` preset: tables, task lists, strikethrough, extended autolinks, footnotes (verified); deflist plugin exists |
| Raw HTML | token `html_inline` / `html_block` with content intact; `html: False` option escapes it as text | AST nodes `inline_html`, `block_html`; `escape` option for renderer | `InlineHTML`, `HTMLBlock` nodes | `html_inline`, `html_block` nodes | passes through; inline `<not>` kept in output | HTML token nodes | `html` node |
| AST/token stream | flat Token list (block + inline children); `SyntaxTreeNode` gives a tree | dict AST (`renderer=None` or `"ast"`) | object tree | node tree + walker | no AST (ElementTree during processing, HTML out) | object tree | typed mdast-like tree |
| Source positions | block tokens only: `Token.map = [start_line, end_line)`; inline children have NO position (observed `map=None`) | none observed | none observed | block `sourcepos` [[line,col],[line,col]]; inline nodes None (observed) | none | block `line_number` only (unverified) | `position.start/end` character offsets on every node incl. inline text, link, delete (verified with `positions=True`) |
| Determinism / global state | none found; no locale use observed; pure functions of input + options. Not audited line by line (see unverified) | none observed; plugins are registered per instance | none observed | none observed | extension registry per `Markdown` instance; instance state reset needed between calls (`reset()`) | renderer context managers hold state (unverified) | none observed |
| Performance | README "high speed", benchmarks in repo; 4.3.0 fixes quadratic paths (see below) | "fast"; author says Wenmode is 1.5-1.8x faster than mistune | README: ~3x slower than Python-Markdown, slightly faster than commonmark.py, much slower than mistune | slow, unmaintained | fast for its feature set (no CommonMark) | moderate (unmeasured) | author claims fastest of the set (author benchmark, not verified) |

Security/robustness note: markdown-it-py 4.3.0 CHANGELOG records two quadratic-time parse paths fixed (input of a few hundred KB stalled for seconds to minutes) and a new `RuntimeError` instead of infinite loops. For a gate that reads untrusted drafts, pin >=4.3.0.

## 2. Behaviour on the four red-team inputs (observed, first-hand)

| Input | CommonMark/GFM spec says | markdown-it-py | mistune | marko | commonmark.py | Python-Markdown | Wenmode github |
|---|---|---|---|---|---|---|---|
| `was [](not) approved` | Valid inline link, empty link text, destination `not`; rendered text = "was  approved" (the word `not` is the URL, not visible) (CommonMark spec, Links) | link_open/link_close with no text child; `not` absent from all text tokens | link node, empty text, `attrs.url='not'` | `Link(dest='not')`, no children | link node, no text | `<a href="not"></a>` | link, `children=[]`, `url='not'` (offsets 4-11) |
| `<not>` | `<not>` is not a valid autolink (no scheme) but IS a valid HTML open tag (tag name + optional attrs), so raw inline HTML; browsers render nothing | `html_inline '<not>'` (type distinct from text) | `inline_html '<not>'` | `InlineHTML '<not>'` | `html_inline '<not>'` | kept as literal tag in HTML output | `html` node |
| `<!--` inside link destination: `[a](<!-- x) approved -->)` | A pointy-bracket destination may contain spaces and `)`; the whole `<...>` is the destination. So the text after `a` is hidden inside the URL. Spec: link destination section | one link, text `a`, no further text (destination swallows `approved`) | url `!--%20x)%20approved%20--` | `dest='!-- x) approved --'` | link `a` only | `<a href="!-- x) approved -->a</a>` | link, url `!--%20x)%20approved%20--` |
| Unclosed `[a](<!--) not approved` | Not a valid link (dest never closed), so literal text; `<!--` without `-->` is not a valid HTML comment | whole line is literal text | not run | not run | not run | not run | not run |
| `was <!-- not --> approved` | Valid inline HTML comment; invisible when rendered | `html_inline` | `inline_html` | not run (html node expected) | not run | not run | in the one test run, the whole line became one `html` node (0-21), consistent with the raw HTML block start condition for `<!--` at line start |
| `~~x~~` | GFM 0.29: strikethrough is one or two tildes each side. NOT in CommonMark core | commonmark preset: literal `~~not~~`; `s_open/s_close` only after `enable("strikethrough")` or `gfm-like` | `strikethrough` node (with plugin) | `Strikethrough` node (gfm) | literal text, no support | literal text, no support | `delete` node |
| `X[^1]` + retracting `[^1]: ...` | Footnotes are not in CommonMark or in the GFM 0.29 spec text (a GitHub UI feature) | needs `footnote_plugin`; then `footnote_ref` token plus a `footnote_block` holding the definition text | `footnote_ref` plus `footnotes` node | gfm alone: plain text paragraphs | not supported | `<sup>` ref plus footnote div | `footnoteReference` plus `footnoteDefinition` |
| `Term\n: not def` | Definition lists are not in CommonMark or GFM | not enabled by default; `deflist_plugin` | `def_list` plugin | none (plain text with LineBreak) | none | `def_list` extension: `<dl>` | `definition_list` plugin file exists (not run) |

Raw block HTML: `<div hidden>not</div>` is an `html_block` / `block_html` in markdown-it-py and mistune (content preserved, unrendered text). Raw HTML sanitisation: none of these sanitise by default; GFM's "tagfilter" extension (disallowed raw HTML: title, textarea, style, xmp, iframe, noembed, noframes, script, plaintext) is NOT implemented in markdown-it-py (`gfm-like` docstring says so); Wenmode exports `GFM_DISALLOWED_HTML_TAGS`. For Assure, sanitising is the wrong goal: raw HTML must be classified (visible vs hidden) not removed.

## 3. Recommendation

Use markdown-it-py >=4.3.0, with mdit-py-plugins (footnote, deflist, tasklists) and explicit rule enables (strikethrough, table), `html: True` so raw HTML arrives as typed `html_inline`/`html_block` tokens.

Why, in order of weight:
1. Spec fidelity: it is the only candidate whose maintainers track CommonMark 0.31.2 explicitly in a 2026 release, and it is the successor named by commonmark.py's own deprecation notice. mistune claims 0.31.2 too, but the upstream author now points to a different project for "fast CommonMark-style parsing".
2. Token stream keeps every hidden construct typed: empty-text links, `html_inline`, `s_open/s_close`, `footnote_ref`/`footnote_block` are all distinct token types. The renderer can therefore decide visibility per type instead of re-reading source.
3. Licence and deps: MIT, single dependency (mdurl, MIT), no C extension, so MIT-only constraint holds.
4. Maintenance: four releases in 2026 (the latest 9 days before this report), with security fixes for quadratic parsing.

Known gap to design around (load-bearing): markdown-it-py gives line ranges (`Token.map`) for block tokens only. Inline tokens carry no offsets. Mapping rendered text back to source offsets therefore needs one of: (a) block-level mapping, i.e. render per block and report the block's source lines (cheap, coarse); (b) locate inline text inside its block's source slice with a monotonic forward search (heuristic; ambiguous when a word repeats); (c) switch to Wenmode (character offsets on every inline node, github preset, BSD-3-Clause, no deps) but it is pre-1.0 (0.15.3; 1.0.0rc1 published 2026-10-21), created 2026-06-17, 49 GitHub stars, one maintainer, so its spec-conformance and API stability are unproven. Suggested path: build the renderer on markdown-it-py with (a), and run Wenmode as a differential oracle in tests (both must agree on rendered text for the red-team corpus) before considering a switch.

Wins to take regardless of parser: treat `link` with empty rendered text, `html_inline`/`html_block`, `image` alt text, strikethrough/`delete`, and footnote definitions as explicit node kinds with a policy each (drop, keep, or flag). A rendered-text gate that silently drops them hides the same attack class in a new place.

Rejected: commonmark.py (archived 2026, deprecated by its owners, no GFM, no inline positions). Python-Markdown (not CommonMark, no strikethrough, no AST, HTML-only output). marko (CommonMark-compliant and MIT, but no positions, "slightly faster than commonmark.py", footnotes not in its gfm extension). mistune (BSD-3-Clause, fine licence, full GFM plugin set, dict AST; no positions, author's own successor project exists; viable second choice). mistletoe (MIT; not evaluated deeply). cmarkgfm (C extension to cmark-gfm, MIT, 2025.10.22: excluded by the pure-Python constraint; it would give exact GFM fidelity and offsets via cmark but needs a compiled wheel). markdown-it-pyrs (Rust binding, Apache-2.0 classifier, excluded: not pure Python).

## 4. Unverified (not confirmed from a primary source)

- Determinism: absence of global state/locale dependence in every parser is from short runtime tests and README reading only; no source audit and no repeated-run byte-comparison was done. Recommend a CI test: parse the corpus twice in separate processes with different PYTHONHASHSEED and LC_ALL, compare token JSON.
- Exact SPDX for markdown-it-py/mdit-py-plugins/mistletoe/marko: PyPI classifier and GitHub API say MIT; the PyPI `license` field is empty or a file reference for some. Read each LICENSE file before vendoring. commonmark.py is NOASSERTION on GitHub vs BSD-3-Clause on PyPI.
- mistletoe: CommonMark claim, GFM extent, and positions (`line_number` on blocks) not read from docs; only HTML rendering was tested.
- mistune 3.x inline positions: none observed in AST output; docs not searched for a positions option.
- marko positions: none observed in node attributes; docs not searched.
- Wenmode: CommonMark spec version targeted, stability of `positions` API, and footnote semantics for edge cases not verified; `Passing github without calling it is deprecated` warning shows API churn before 1.0. Its `<!-- hide --> x <not>` result (single html node 0-21) is consistent with the CommonMark HTML-block rule but not confirmed against the spec example.
- Raw-HTML tagfilter and sanitisation: only confirmed absent in markdown-it-py (via its preset docstring); not checked for mistune, marko, Wenmode renderers.
- Performance: no benchmark was run here; figures are upstream claims. The "1.5-1.8x faster" Wenmode vs mistune number is the author's own.
- Behaviour was observed on markdown-it-py 3.0.0 (py3.9 venv) and 4.3.0 only for the position test; the token outputs for the four inputs were observed on 3.0.0, not re-run on 4.3.0. mistune/marko/commonmark/Markdown results come from 3.3.4/2.2.5/0.9.2/3.9, not the latest versions.
- Whether `[](not)` should be treated as rendered text "" or flagged is a policy choice, not a parser fact.

## 5. Primary sources

- PyPI JSON: https://pypi.org/pypi/{markdown-it-py,mdit-py-plugins,mistune,marko,commonmark,Markdown,mistletoe,cmarkgfm,markdown-it-pyrs,wenmode}/json
- GitHub API repo metadata: https://api.github.com/repos/executablebooks/markdown-it-py (and mdit-py-plugins, lepture/mistune, lepture/wenmode, frostming/marko, readthedocs/commonmark.py, Python-Markdown/markdown)
- https://github.com/executablebooks/markdown-it-py (README, CHANGELOG.md 4.3.0, markdown_it/presets/__init__.py gfm_like docstring)
- https://github.com/lepture/mistune (README, Wenmode notice) and https://mistune.lepture.com/en/latest/ (CommonMark 0.31.2 statement)
- https://github.com/frostming/marko (README: spec 0.31.2, performance, gfm ext)
- https://github.com/readthedocs/commonmark.py (README deprecation notice; archived)
- https://github.com/lepture/wenmode (README: positions, github preset)
- CommonMark 0.31.2: https://spec.commonmark.org/0.31.2/ ; GFM 0.29-gfm: https://github.github.com/gfm/
