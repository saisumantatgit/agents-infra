# R1 render-first: is there a parser that fits the moat? (OVN-1121, 2026-11-21)

**Verdict: yes, with one design gap. `markdown-it-py` 4.3.0 plus `mdit-py-plugins` (both MIT, pure Python, one runtime dependency `mdurl`, also MIT) tokenises every R45 Class T markup shape as a distinct token. That lets the gate refuse or drop hidden text structurally. No mainstream pure-Python parser gives inline character offsets, so a render-first gate maps rendered text back to the source at block (line) level.**

## Verified first-hand by the main loop (2026-11-21)

| Fact | Evidence |
|---|---|
| Latest markdown-it-py is 4.3.0, uploaded 2026-11-10 | PyPI JSON `releases` |
| Runtime dependency: `mdurl~=0.1` only (everything else is an extra) | PyPI `requires_dist` |
| Licences: markdown-it-py MIT; mdit-py-plugins 0.7.0 MIT; mdurl 0.1.2 MIT | PyPI classifiers (`license_expression` is empty on all three) |
| `was [](not) approved` → `text, link_open{href:'not'}, link_close, text` | `MarkdownIt('commonmark',{'html':True}).enable('strikethrough').parseInline` |
| `was <not> approved` → `text, html_inline '<not>', text` | same |
| `was ~~not~~ approved` → `text, s_open, text 'not', s_close, text` | same |

So the hidden `not` in F1 is either a link destination (`href`) or raw HTML, never a `text` token. The F4 and A1 strikethroughs are bracketed by `s_open`/`s_close`. A gate that grounds only `text` tokens outside `s_open … s_close`, and refuses a claim containing `html_inline`, an empty-text link or an image, closes F1, F4 and A1 structurally. F5 (a comment inside a link destination) also lands inside `href`, per the research; this was not re-run by me.

## From the research agent (testimony; Sonnet, sources in its report)

- **Compared:** markdown-it-py, mistune (BSD-3, full GFM plugins, no positions), marko, commonmark.py (archived), Python-Markdown (not CommonMark), cmarkgfm (C extension, rejected), and Wenmode (BSD-3, pre-1.0, created June 2026, the only one with inline character offsets).
- **Suggested design:** render with markdown-it-py, map back at block level (`Token.map` line ranges), and use Wenmode only as a differential test oracle, not a dependency.
- **Unverified by it:** determinism was spot-checked, not source-audited. Some behaviour was observed on older installed versions (markdown-it-py 3.0.0, mistune 3.3.4).

## What Sai is deciding (Escalation #4: a new runtime dependency changes what `install.sh` provisions)

**Recommendation: YES to adding `markdown-it-py>=4.3,<5` and `mdit-py-plugins` as runtime dependencies for a render-first gate.** Why:

- It closes F1, F4, A1, and by design F5 and A2 (footnotes via the plugin), structurally rather than by word list.
- The dependency is MIT, pure Python, deterministic by construction (no network, no model), with one MIT sub-dependency.
- The current `pyproject.toml` already carries two runtime dependencies (`syntok`, `pyyaml`), so this is not a new kind of decision.

What would flip it: a source audit finding global state or non-determinism in the renderer, or block-level mapping proving too coarse to report which source sentence grounded a claim. Then the fallback is mistune, or vendoring a minimal tokenizer for the five constructs that matter.

**CEILING to carry into the build:** block-level mapping means the gate can say which source *line range* grounded a claim, not which characters. The condition under which that breaks: a reviewer needs character spans for an audit trail. Upgrade path: a Wenmode-style inline-offset parser once one is stable.
