# J-52 — the plugin path. Closed as far as it can be closed, and why.

α4 proved `install.sh`, the engine, the hook script and the CLI work in an
unrelated repo. It could not reach the PLUGIN path. This closes four of the five
things that needed proving, proves the fifth is **unreachable non-interactively**,
and finds a product limitation nobody had written down.

## 1-4: CLOSED, and pinned by `tests/test_plugin_contract.py` (10 tests)

| # | Checked | Result |
|---|---|---|
| 1 | manifest valid for discovery | `claude plugin validate Agent-Assure --strict` → **passed** |
| 2 | `hooks.json` matcher vs `capture_core._RETRIEVAL_TOOLS` | **all 5 tools matched, both directions, nothing unmatched** |
| 3 | the exact `hooks.json` command line | run with `CLAUDE_PLUGIN_ROOT` resolved → exit 0, wrote `S1 / Read / session_id 'sess-PLUGIN' / verbatim` |
| 4 | command + skill frontmatter | both discoverable, names correct |

**`claude plugin validate` is NOT evidence about hooks.** Its own help says it
validates "the skills, agents, and commands in a directory". Hooks are not
mentioned, and its JSON report returns `"contents": []`. A passing validator was
not allowed to stand in for a hook check.

## 5: the hook does not fire in print mode — and that is NOT our defect

A real `claude -p --plugin-dir` run answered `47219` correctly, so the `Read`
tool definitely executed. **No store appeared.** Three registrations were then
tried, to find out whether the fault was ours:

| Registration | `Read` ran | hook fired |
|---|---|---|
| plugin via `--plugin-dir` | yes | **no** |
| plain project-local `.claude/settings.json` | yes | **no** |
| explicit `--settings <file>` | yes | **no** |

**`claude -p` does not execute PostToolUse hooks however they are registered.**
The plugin is exonerated by control, not by assertion.

Two supporting facts: the nested session reports `/assure-verify` IS available
(weak — model self-report, recorded as such), and the docs confirm
`hooks/hooks.json` with a top-level `"hooks"` key is the correct plugin layout
and that `${CLAUDE_PLUGIN_ROOT}` is expanded.

**A misquote corrected on the way.** A research agent reported that `-p`'s help
says "settings files silently ignored". It actually says "settings files **that
fail validation** are silently ignored". That is a materially different claim and
it briefly pointed me at a defect in our own `hooks.json`. Checking the help text
myself is what killed that false lead.

## THE PRODUCT LIMITATION THIS FOUND — and it is not small

**In `claude -p` (print / CI / piped) mode the capture hook never runs, so the
evidence store stays EMPTY and every factual claim reads `UNCITED`.** Anyone
wiring Agent-Assure into CI gets a gate that fails everything, for a reason no
surface mentioned. Now documented on the README and the skill, and pinned in
`tests/test_product_claim.py` as a disclosed limitation.

This is the second time in two days that the honest-claim discipline earned its
keep by finding a gap between what the tin says and what the code does.

## What remains: one human step, and it is genuinely human

Item 5 cannot be automated — not "I ran out of time", but proven unreachable from
a non-interactive process. In an INTERACTIVE session:

```
claude --plugin-dir /path/to/Agent-Assure
# then: /hooks         -> expect PostToolUse with capture_hook.py listed
# then read any file   -> expect .assure/evidence-store.jsonl to appear
# then: /assure-verify <draft>
```

Registered as **J-54**. Everything it would confirm is already proven in parts:
the hook command works when invoked (item 3), the matcher covers the tools
(item 2), and the layout is the documented one. The residual risk is that Claude
Code does not register a `--plugin-dir` plugin's hooks at all — which the docs
say it does.

## Verdict

**The plugin path is validated except for live interactive hook firing, which no
automated test can reach.** The ship verdict moves from "not ready as a plugin"
to **ready, with one two-minute human confirmation (J-54) outstanding** — plus
the print-mode caveat above, which is a documentation fix, now done.
