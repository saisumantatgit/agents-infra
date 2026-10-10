# Spec §7.5 audit — is the EvidenceStore complete?

**2026-09-13, overnight queue item 1.** Read-and-analyse only; no code changed.

## Why this audit exists

The founding design spec names this as the project's single biggest risk:

    §7.5 The gate is only as truthful as the EvidenceStore, and the store is
    complete only if every retrieval flows through an instrumented tool that
    captures verbatim full text. … Get this wrong and the score is theater.
    This is the top implementation-plan risk to close.

It has never been audited. The capture hook was live-validated once, by its
author, on the tools it was written for.

## Answer in one line

**Store gaps are SAFE for ordinary claims and UNSAFE for absence claims** —
and at least one harness mode actively routes retrieval around the hook.

## 1. The safety argument for ordinary claims — proven by code structure

`ground()` returns GROUNDED only when every cited id **resolves in the store**
and T1 fires on that source's text. A source the hook never captured cannot
resolve, so a claim citing it reads `UNVERIFIED_CITATION`. **An incomplete store
can only REFUSE a positive claim, never certify one.**

So for FACTUAL, NUMERIC and ATTRIBUTION claims, every gap below costs **Error-A
only** — a genuinely grounded claim wrongly flagged. Visible, recoverable, and
annoying at scale, but not a moat breach.

## 2. The absence path is FAIL-OPEN — demonstrated

An absence claim is supported by what was *not* found. The gate checks the
captured sources' text for a refutation (RT3-04). **It can only check the text
it was given.** If the model saw the refutation through an uncaptured tool, the
gate certifies the absence while the model is looking at evidence against it.

Reproduced, using the corpus's own certified case (q13):

```
claim: We found no evidence of a safety recall affecting the X200 drone.

store = what the hook captured (two on-topic Exa fetches)
        -> PASS    ABSENCE_SUPPORTED    100.0

store = the same + one result from native WebSearch, which the hook does
        not capture: "Regulators issued a safety recall affecting the X200
        drone after battery evidence of overheating."
        -> FAIL    UNVERIFIED_ABSENCE   0.0
```

**The gate's logic is correct in both runs.** The contradiction check works the
moment it can see the text. The only thing between the gate and the right
verdict is the capture layer. **This is an Error-B caused entirely by store
incompleteness** — the exact failure §7.5 predicted, on the one claim type
where incompleteness points toward PASS.

(A first attempt using a scope-qualified claim did not reproduce — the gate
refused both stores for an unrelated reason. Recorded so the demonstration is
not mistaken for a first-try confirmation.)

## 3. Coverage table

Matcher in `hooks/hooks.json`:
`mcp__exa__web_fetch_exa|web_fetch_exa|Read|WebFetch|mcp__ddg-search__fetch_content`

| path by which content reaches the drafting model | state | effect on a positive claim | effect on an absence claim |
|---|---|---|---|
| `mcp__exa__web_fetch_exa`, `web_fetch_exa` | **CAPTURED** verbatim | — | — |
| `Read` | **CAPTURED** verbatim (raw text; line numbers exist only in the model's view — live-validated) | — | — |
| `mcp__ddg-search__fetch_content` | **CAPTURED** verbatim | — | — |
| `WebFetch` | **CAPTURED** as `haiku_summary` — can never ground, by design | UNGROUNDABLE | text not checked for refutation |
| `Read` with `offset`/`limit` | **PARTIAL** — slice stored as `verbatim`, no marker that it is partial | fine if the claim is in the slice | refutation outside the slice is invisible |
| native `WebSearch` | **NOT CAPTURED** | Error-A | **Error-B — demonstrated above** |
| `mcp__exa__web_search_exa` (returns page text, not just links) | **NOT CAPTURED** | Error-A | **Error-B** |
| `mcp__ddg-search__search`, `expand_link` | **NOT CAPTURED** | Error-A | **Error-B** |
| **`Bash`** — `cat`, `sed`, `head`, `curl`, `grep` | **NOT CAPTURED** | Error-A | **Error-B** |
| `Grep`, `Glob` | **NOT CAPTURED** (content snippets / paths) | Error-A | Error-B |
| Other MCP readers — Drive `read_file_content`, Chrome `get_page_text`, HF `hf_fs`, `ReadMcpResourceTool`, codebase-memory snippets, Artifact `read` | **NOT CAPTURED** | Error-A | Error-B |
| Subagent returns (a subagent retrieves, the parent drafts) | **UNKNOWN** — whether `PostToolUse` fires for a subagent's tool calls *into this session's store* is not established by any test or live validation | UNKNOWN | UNKNOWN |
| Text pasted by the user; compaction summaries; prior-turn content; injected CLAUDE.md/skills/memory | **NOT CAPTURED** — no tool call exists to hook | Error-A | Error-B |

## 4. The sharpest operational finding

**A harness mode instructs the model to bypass the hook.** In the session that
ran this audit, Claude Code's auto mode injected, verbatim:

    Do your work through the Bash tool wherever it can accomplish the job:
    read files with cat, head, or sed -n, search with grep and find … rather
    than using the dedicated Read, Edit, or Write tools.

Under that instruction **every file the model reads goes through `Bash`, and
the store stays empty.** Every file-based citation then reads
`UNVERIFIED_CITATION`, and D-35's `evidence_basis` would *truthfully* report the
file as "NEVER RETRIEVED this session" — about a file the model did read.

§7.5 anticipated "the model learns to route around the hook". **The route-around
is not learned. It is a documented platform setting.**

## 5. A naming defect found on the way

`query_provenance` is not a search query. `_derive_query_provenance` takes the
first non-empty of `query`, `url`, `urls[0]`, `file_path`, else the
`session_id`. For a `Read` it is a file path; for an Exa fetch, a URL.

So "ABSENCE_SUPPORTED by two distinct search queries" really means **two
distinct fetch provenances** — and actual searches are never recorded at all,
because no search tool is captured. It works on the corpus partly by accident
(URLs tend to contain the subject). D-35's `evidence_basis` currently tells a
reader these are "search queries", which is inaccurate.

## Disposition — every remedy is Sai's

| remedy | shape | authority |
|---|---|---|
| Taint the session: a `PostToolUse` hook on **all** tools records "an uncaptured retrieval occurred", and absence claims refuse in a tainted session | fail-closed; closes the Error-B | **hook registration → Escalation #4, Sai's** |
| Widen the matcher to capture `WebSearch`, Exa/DDG search, `Bash` reads | reduces Error-A; `Bash` output is not always retrieval, so needs design | **Escalation #4, Sai's** |
| Mark partial `Read`s in the store | small, fail-closed for absence | capture-layer change; recommend ADR |
| Rename `query_provenance` in user-facing text to "fetch provenance" | display-only | agent authority; deferred to keep tonight decision-independent |

**Nothing was changed.** All material remedies touch hook registration, which
the project's escalation list reserves to Sai.

## Why this matters for the product call

If the launch is **provenance-only**, this audit *is* the launch-blocker list:
the provenance promise is "every citation points to a source actually retrieved
this session", and today the store cannot see most of the ways a source gets
retrieved. **Provenance is set membership, and set membership is only as good
as the set.**

Recommended launch scope, if provenance ships: **exclude absence claims** (or
refuse them in any tainted session) and **state which retrieval tools are
covered** — an honest boundary rather than a silent one.
