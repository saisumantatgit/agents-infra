# Agent-Assure: Alpha Tester Guide

You are trying Agent-Assure for the first time, on your own. This guide tells you what to expect, what it can and cannot tell you, and what to send back to us.

This file is at `Agent-Assure/docs/ALPHA-TESTER-GUIDE.md` in the `agents-infra` repository (there is no copy at `Agent-Assure/ALPHA-TESTER-GUIDE.md`).

**Two ways in.** To see the checker work, you need only `uv`: run `uv sync` in `Agent-Assure`, then section 3 step 1 and "Check your own source". No plugin registration, no `~/.claude` changes, no `install.sh`. To use it on live research inside Claude Code, you need the plugin: section 2 and section 3 step 2.

**Command style.** Examples below use `.venv/bin/python`. That path exists after either `uv sync` or `bash install.sh`. `uv run python ...` (run from `Agent-Assure`) does the same thing; use whichever you prefer.

Every statement here comes from the repo (README, install.sh, the skill, the command, the failure-types reference, the register, and the ALPHA-5 report). Where we could not confirm something, the guide says "not verified".

---

## Before you start: this tool expects you to QUOTE your sources

Agent-Assure passes a claim only when it can see the claim's words in a source
the session actually retrieved — at least eight words in a row, copied exactly.
It does not judge whether a paraphrase means the same thing; that would need an
AI inside the checker, which this tool deliberately does not have.

**What that means in practice.** Measured on 2026-10-24/25: honest drafts that
paraphrase almost never pass (0 of 20), and — corrected on 2026-10-25 — **neither do
claims that wrap a quotation in your own framing**. "The audit found "material
weaknesses ..."" fails, even with a 15-word quotation, because the gate anchors its
check on the start of the claim and "The audit found" is not in the source.

**What works: make the claim the source's own sentence, then cite it.** Copy the
source sentence — or at least its opening eight words — as the claim itself, with the
citation inside, before the full stop. Quote marks are optional.

<!-- guide-example: GROUNDED -->
`The 2025 internal audit identified material weaknesses in custodial reconciliation at the Frankfurt desk [S1].`

<!-- guide-example: REFUSED -->
`The audit found "material weaknesses in custodial reconciliation" [S1].`

Both examples are run by `tests/test_guide_examples.py` against the source
`The 2025 internal audit identified material weaknesses in custodial reconciliation
at the Frankfurt desk during the third quarter.` — so if the gate changes, this page
fails a test instead of silently giving wrong advice.

**So a FAIL usually means "quote your source", not "your claim is false".**
Read the per-claim reason before concluding anything about your draft.

## 1. What it does

Agent-Assure checks that every factual claim in an AI-written draft is TRACEABLE to text that your Claude Code session actually retrieved. While you research, a hook records each retrieved source word for word into a file called the evidence store. When you ask for a check, a plain Python program (no AI model, no network) compares each claim and its citation marker (for example `[S2]`) against that store. If the draft cites `[S3]` and no `[S3]` was ever retrieved, the program refuses it. Nobody can talk it out of that.

It does NOT check that the source is correct. It does NOT check that the source agrees with the claim. A source that says "we found no evidence that X" can still satisfy the check for a draft that says X. A PASS means "traceable", never "true" and never "supported".

Acronyms used below:
- CI: continuous integration (automated build or test runs).
- JSONL: a text file with one JSON object per line.
- J-xx, A-5-01, ADR-xxx: ticket and decision numbers from our own register. Each one is explained where it appears.

---

## 2. Install

What you need: `uv` (a Python package manager) and Python 3.11 or newer. The installer stops with an error if `uv` is missing and prints the command to install it: `curl -LsSf https://astral.sh/uv/install.sh | sh`.

Where it works: Claude Code in interactive mode only. In `claude -p` (print mode), in CI, or in piped mode, the capture hook never runs. The store stays empty and every claim reads UNCITED. See section 5.

Commands:

```bash
cd Agent-Assure
bash install.sh
```

`install.sh` creates a `.venv` folder, installs the dependencies, and checks that the engine and hook import. On success it prints `engine + hook + deps: OK`.

Then start Claude Code with the directory loaded as a plugin:

```bash
claude --plugin-dir <path to Agent-Assure>
```

The installer's own text offers two other ways: add it to your plugin marketplace, or copy it into your Claude Code plugins path. We have only seen the `--plugin-dir` route described in the repo. The other two are not verified by us.

Once active, the plugin gives you:
- a capture hook that records every retrieval automatically (Exa fetch, `Read`, native `WebFetch`, DuckDuckGo fetch);
- one command: `/assure-verify`;
- one skill: `verify-grounding`.

The store is written to `.assure/evidence-store.jsonl` in the project you work in.

Do not paste the "session id" snippet that `install.sh` prints at the end until you have read section 5 (item A-5-01).

---

## 3. A 5-minute first run

### Step 1: run the shipped demo (about 1 minute)

The demo needs no Claude Code session. It simulates two retrievals through the real capture code and then checks two drafts. From inside `Agent-Assure`:

```bash
.venv/bin/python demo/build_store.py
.venv/bin/python scripts/ground_check.py --draft demo/draft-grounded.md   --store demo/evidence-store.jsonl --json | .venv/bin/python demo/show_report.py
.venv/bin/python scripts/ground_check.py --draft demo/draft-fabricated.md --store demo/evidence-store.jsonl --json | .venv/bin/python demo/show_report.py
```

What you should see for the grounded draft:

```
gate: PASS | score: 100.0
  GROUNDED  (header line)
  GROUNDED  (Redis claim)
  GROUNDED  (PostgreSQL claim)
```

What you should see for the fabricated draft:

```
gate: FAIL | score: 50.0
  GROUNDED
  GROUNDED
  GROUNDED
  UNVERIFIED_CITATION  <- MongoDB sustained approximately 45000 operations per second ...
  UNVERIFIED_NUMBER    <- Redis delivered about 100 times the throughput ...
```

The fabricated draft cites `[S3]`, a source that was never retrieved. It also claims "100 times", a number no source contains (the source says twelve times). Both are caught. Exit code is 0 for PASS and 1 for anything else.

If the fabricated draft does not FAIL on your machine, that is the most important bug you can report. Send it to us first.

Expected outputs are saved in `demo/expected/` so you can compare. A test (`tests/test_demo_golden.py`) pins them. Whether it passes on your machine: not verified.

The demo renderer `demo/show_report.py` prints only the verdict and the first 70 characters of each claim. For the reasons, pipe the same JSON into `scripts/explain_report.py` instead; see "Getting the reason for each claim" in section 4.

Do not pass `--session-id` against the demo store. The demo records carry no session id, and the engine refuses an empty `--session-id` by design.

### Step 2: try it on a real session (about 4 minutes)

1. Start Claude Code interactively with the plugin loaded (`claude --plugin-dir <path>`).
2. Ask it to read something real: a file with `Read`, or a page with an Exa or DuckDuckGo fetch. Native `WebFetch` is recorded too, but marked `haiku_summary` (see below).
3. Have it write a short draft to a file. Two drafting rules apply:
   - Put citation markers INSIDE the sentence, before the final period: `... per second [S1].` A marker after the period detaches and the claim reads UNCITED.
   - Keep authoring notes on ONE line: `<!-- TODO: check this -->`. A multi-line comment block is scored as claims and will fail the draft (J-48).
4. Run `/assure-verify path/to/draft.md`. If you give no path, the command asks for one.
5. Check that `.assure/evidence-store.jsonl` exists and has lines. If it does not, the hook is not firing. Stop and report it (see section 6).

Manual alternative, outside the plugin:

```bash
.venv/bin/python scripts/ground_check.py --draft DRAFT.md --store .assure/evidence-store.jsonl --json
```

Without `--json`, the engine writes `grounding-report.yaml` into your current folder and prints a one-line summary. With `--json`, it prints the full report and writes no file.

Optional flag: `--threshold N` sets the score bar (default 90).

### Check your own source (no Claude Code session needed)

You can test your own text without the plugin. The checker needs two files: a draft, and an evidence store. The evidence store is a JSONL file (one JSON object per line); each line is one retrieved source. The capture hook normally writes it; `scripts/add_source.py` writes it for you.

Put your source text in `my-source.txt` and a draft in `my-draft.md`. The draft must cite the source as `[S1]`, inside the sentence, before the full stop. Then, from `Agent-Assure`, add the source to a store:

```bash
uv run python scripts/add_source.py my-source.txt --id S1 --store my-store.jsonl --session-id my-test-session
```

It writes one valid line (the same fields the capture hook writes, text normalised with NFKC, sha256 recorded), then re-loads the whole store with the checker's own loader. It refuses with exit 1 and leaves the store untouched if the id is already in the store, the file is missing, or the file is empty. For a second source, run it again with `--id S2`. `--session-id` is optional; if you pass it here, pass the same value to `ground_check.py`.

Check the draft against it:

```bash
uv run python scripts/ground_check.py --draft my-draft.md --store my-store.jsonl --session-id my-test-session
```

We ran this with a draft whose single claim is a sentence copied from the source plus `[S1]`. Result: `gate=PASS grounding_score=100.0`, exit 0, and a `grounding-report.yaml` in your current folder.

Fields, one line each (the full table is in `README.md`, "EvidenceStore JSONL Format"):
- `source_id`: the key your draft cites, `S1` for `[S1]` (the `--id` you gave). It must be unique in the file.
- `tool`: `add_source.py` writes `Read`, which is treated as verbatim. The loader accepts only the tool names the capture hook writes: `Read`, `mcp__exa__web_fetch_exa`, `web_fetch_exa`, `mcp__ddg-search__fetch_content` (verbatim) and `WebFetch` (always `haiku_summary`). Any other name, or a `tool` that disagrees with `full_text_source`, makes it refuse the file.
- `text`: the source body, word for word. Only this is matched.
- `session_id`: the capture hook writes one on every live record. It matters only if you pass `--session-id`: the engine then refuses a store that contains any record with a different or blank `session_id`. Pass the same string you wrote, or leave `--session-id` out (the scope line then says session scope is not asserted).
- `retrieval_status` and `read_extent` are optional fields the hook writes; leave them out.

Mistakes are refused with a message, never scored, and exit 1. We ran each of these: a missing file prints `REFUSED: no evidence store at ...`; a duplicate `source_id` and an unknown `tool` name the offending line; a `--session-id` that does not match prints `REFUSED: evidence store holds records from outside this session ...`.

Two things to expect, because the checker is built to refuse rather than guess:
- A paraphrase of your source comes back UNGROUNDED. Copy the source sentence instead (see "Before you start").
- Do not edit the store of a live session to turn a failure into a pass (see section 6).

---

## 4. Reading a report

### The gate (top line)

- PASS: every scored claim is traceable AND the score is at or above the threshold. One bad claim blocks PASS, whatever the score. PASS does not mean the source agrees with the claim or is right.
- NEEDS_WORK: the score is 60 or more, but at least one claim has a problem (or the score is under the threshold, or nothing could be scored). Fix the listed claims and run again.
- FAIL: the score is below 60. This is checked first, so a low score is FAIL even if other problems exist.

The score is the share of scored claims that are GROUNDED or ABSENCE_SUPPORTED. Lines the engine classes as NON_CLAIM (questions, instructions, pure opinion, and headings that read as plain labels) are left out of the count. Not every heading is a label: see "What counts as a claim" below.

If the store is empty, you get NEEDS_WORK with `vacuous: true`. That means "nothing to check against", not "all clear".

### Per-claim verdicts

Passing:
- GROUNDED: the claim's words appear in a source retrieved word for word (a run of 8 or more matching words, or equivalent). Lines classed NON_CLAIM also show GROUNDED but are not scored; in the JSON their `kind` is `NON_CLAIM`.
- ABSENCE_SUPPORTED: a "there is no X" claim backed by at least 2 recorded searches that each name the full subject. See the limit in section 5.

Failing (each one stops the gate from reaching PASS):
- UNVERIFIED_CITATION: the claim cites a source id (like `[S9]`) that is not in the store. The source was never retrieved this run. This is the fabricated-citation catch.
- UNGROUNDED: the cited sources exist, but none contains support for the claim. It means "could not trace this", never "this is false". Honest paraphrases land here often. About two in five honest claims were refused on our 52-claim test set (error rate 0.400, calibration record CR-007).
- UNCITED: a factual claim with no citation marker. It is also what you see when the marker was placed after the period, or when the store is empty.
- UNVERIFIED_NUMBER: a number in the claim matches no source. Value, unit and, if the claim states one, the rate must all match. "25%" is not "25". "per minute" is not "per second".
- UNVERIFIED_ABSENCE: a "no X exists" claim with fewer than 2 recorded searches that name the full subject.
- UNVERIFIED_RELATION: a "A causes B" style claim without two separate sources, one per side. See ADR-007 in section 5.
- UNGROUNDABLE: every cited source is non-verbatim (for example a `haiku_summary` from native `WebFetch`), or empty. The engine refuses to check against a summary. Re-fetch with Exa or a raw `Read`. It is also the verdict when the only cited source looks like a copy of your own draft (`support_diagnostic` `cited_source_is_the_draft`): the source is excluded and `evidence_basis` names it. See "Known issues".

Other per-claim fields you will see in the JSON: `evidence_basis`, `support_diagnostic`, and, for causal claims, `relation_diagnostic`.
- `support_diagnostic` of `cited_sentence_may_not_assert_claim` means: go read that source sentence yourself. It is advice, not a verdict. It misses about half of the denials we built (7 of 14).
- `relation_diagnostic` of `corroborated_by_two_sources` next to UNGROUNDED is the normal result for an honest causal claim.

### Getting the reason for each claim

The one-line summary (`gate=... grounding_score=...`) gives no per-claim detail. For the reasons, run with `--json`. Each entry in `per_claim` carries:
- `verdict`: one of the verdicts above.
- `kind`: how the engine read the line. `NON_CLAIM` means not scored; `NUMERIC` and `FACTUAL` are scored.
- `text`: the claim exactly as the engine split it out of your draft. Compare it with your sentence: this is where you see a sentence cut into pieces, or a heading or table counted as a claim.
- `evidence_basis`: the reason, in words (for example "S9 is cited but is NOT IN THE EVIDENCE STORE", or "No source is cited ...").
- `support_diagnostic`: a short code. `no_cited_verbatim_source` appears on every claim that has no usable cited source (UNCITED, UNVERIFIED_CITATION, UNGROUNDABLE); it is not a separate problem. `cited_source_is_the_draft` means every cited verbatim source was excluded because it reads as a copy of your draft (see "Known issues"). Codes starting `verbatim_but_` appear only on UNGROUNDED claims that were found word for word in the source; the code names the rule that disowned the match (for example `verbatim_but_hedge_word_before_it`, `verbatim_but_next_sentence_denies`, `verbatim_but_source_sentence_negates_differently`). Read `evidence_basis` for the reason.

`scripts/explain_report.py` prints them in readable form: per claim the verdict, the full claim text, the reason, and a one-line fix hint; non-claims (headings) are listed apart as "not scored". It only renders the report; it never recomputes a verdict. Run from `Agent-Assure`, swapping in your own draft and store:

```bash
uv run python scripts/ground_check.py --draft demo/draft-fabricated.md --store demo/evidence-store.jsonl --json | uv run python scripts/explain_report.py
```

On the fabricated demo draft, claim 3 reads `UNVERIFIED_CITATION ... why: S3 is cited but is NOT IN THE EVIDENCE STORE` and claim 4 reads `UNVERIFIED_NUMBER ... The claim asserts 1 figure: "100" ...`, each with a `fix:` line. The exit code is 0 when the gate is PASS and 1 otherwise, so `ground_check.py --json | explain_report.py` can be used in a script. You can also save the JSON and pass the file: `explain_report.py report.json`.

### What to do about each verdict

| Verdict | What it means for you | What to do |
|---|---|---|
| UNCITED | No `[Sn]` in the claim. Includes a marker placed after the full stop, and a heading or table counted as a claim (below). | Add `[Sn]` inside the sentence, before the full stop. For a heading or table, see below. |
| UNVERIFIED_CITATION | `[Sn]` is not in the store. | Retrieve the source in-session, or fix the id. In a hand-built store, add the source with `scripts/add_source.py` (see "Check your own source"). |
| UNGROUNDED | `[Sn]` exists, but no 8-word run of your claim is in it. Usually a paraphrase, or your own framing words. | Replace the claim with the source's own sentence and cite it. This is not evidence the claim is false. |
| UNGROUNDED with `support_diagnostic` `verbatim_but_...` | Your claim IS in the source word for word, but a rule disowned that match because of the source's own words around it. `evidence_basis` says "Found verbatim in S1, but ..." and quotes the words: a hedge word such as "without", "per", "if" or "not" in the five words before it (even at the end of the previous sentence), a denial in the sentence before or after it, a denying heading or list label, or a negation in the same source sentence that your claim does not carry (common when the gate split your sentence at ", and"; the report then shows the piece). | Copying it again will not help. Cite a different sentence that states the fact, or leave it out. If the quoted words plainly do not deny or hedge your sentence, report it as an over-refusal (section 6). |
| UNVERIFIED_NUMBER | A figure in the claim is not in the cited source with the same value, unit and rate. A version number such as "2.4" counts as a figure. | Copy the figure as the source writes it, or cite the source that has it. |
| UNGROUNDABLE | The cited source is a summary (`haiku_summary`) or empty, or (`support_diagnostic` `cited_source_is_the_draft`) it is a short source that looks like a copy of your draft. | Re-fetch with Exa or `Read`. If the source is verbatim and non-empty, cite the full source document, not an excerpt; see "Known issues". |
| UNVERIFIED_ABSENCE, UNVERIFIED_RELATION | An "X does not exist" or "A causes B" claim without enough support. | Quote a source that says it, or soften the claim. |

### What counts as a claim

Observed by running the commands on this build. This describes today's behaviour, not a promise about later versions.

- Headings. A heading that reads as a plain label ("## Results", "# Release note", "# Kestrel release note") is NON_CLAIM: GROUNDED, not scored. A heading that reads like a statement ("### Why it matters to operators") or contains a figure such as a version number ("# Kestrel 2.4 note", "## Kestrel 2.4") is scored like a sentence. Uncited, it comes back UNCITED and lowers the score. Cited, it must still share 8 words in a row with the source, so a short title with `[S1]` came back UNGROUNDED. Fix: use a label-style heading without a figure, or a heading that is itself a span of the source. An earlier version of this guide said headers are never scored; that was wrong.
- Tables. A markdown table is read as one claim, starting at its header row. It is scored, and uncited it is UNCITED. Putting `[S1]` in a cell, or a verbatim source sentence in a row, still came back UNGROUNDED in our runs, because the check anchors on the start of the claim, which is the header row. We have no documented way to make a table pass. Write the facts as cited sentences instead.
- Bullet lists. Each `- item` is its own claim. A bullet that was a source sentence plus `[S1]` before its full stop came back GROUNDED.
- Sentence splitting. One sentence can be split into more than one claim, for example at "and", and a piece can lose its subject. Check the `text` field in `--json`. If a piece fails, rewrite the sentence in the source's own wording so it is not split.

### The scope line

Every JSON report has a `scope` field. It is the engine's own statement of what PASS means. Without `--session-id` it reads:

```
PASS means every claim in this draft is traceable to text in a source present in the evidence store supplied to this run; it does not mean the source agrees with the claim, and a source that denies or hedges a claim can still satisfy this check. Session scope is NOT asserted: pass --session-id to require that the sources were retrieved this session.
```

With `--session-id <id>` it says "retrieved this session" instead. Read this line. If it says "Session scope is NOT asserted", the store may hold sources from earlier sessions (see J-38 below). The word "verified" is deliberately never used in the output.

The plain-text summary (non `--json`) also prints the scope line, under the one-line gate summary; we confirmed this by running it. The demo renderer (`demo/show_report.py`) does not print it.

---

## Known issues (bugs under investigation)

These are defects, not intended behaviour. Do not build a workflow on them.

- UNGROUNDABLE on a short verbatim source (cause known; grounding short excerpts is pending a design decision). The engine has a deliberate guard: a cited source counts as a possible copy of your own draft when at least 80% of its adjacent word pairs also appear in the draft, and a draft cannot certify itself. A source of one or two sentences that your draft quotes almost whole meets that bar, so the claim reads UNGROUNDABLE with `support_diagnostic` `cited_source_is_the_draft`, even though the store line says `full_text_source: verbatim`. `evidence_basis` names the excluded source and says why. If the claim also has a figure that the short source does not contain, it reads UNVERIFIED_NUMBER instead (the wrong figure is no longer hidden). The guard stays on purpose; relaxing it would let a draft pass by citing a copy of itself, so whether and how to ground short excerpts is a decision not yet made. Workaround: store and cite the full source document, not a one- or two-sentence excerpt. We checked this on build 5b6898f: a one-sentence source quoted by the draft came back UNGROUNDABLE `cited_source_is_the_draft`; the same sentence inside a five-sentence source document came back GROUNDED, gate PASS. If you hit UNGROUNDABLE on a verbatim source that is not short, report it with the five items in section 6.

- A PASS can be wrong about traceability itself (red-team rounds R45 and R46, 2026-11-21). In each case below, the claim you read is not text in the cited source, yet the gate reports PASS 100. Status: open; fixes are briefed and not yet built. Until then, read the draft as rendered and check these shapes yourself:
  - Markup that hides or strikes words: `[](not)`, `<not>`, `~~not~~`, a ❌ or 🚫 before a claim, `<!--` inside a link. The gate reads the hidden word; you do not.
  - A heading or list lead-in that supplies the meaning: `## Myths` or `## Criminals` over cited bullets, "The regulator fined the following firms:" over names from another source, a figure on its own line under a name.
  - Superscripts read as digits: `10⁵` is checked as 105.
  - A figure, qualifier, unit, rate, range or date that differs from the source but sits more than about eight words into the sentence: "at least 12" read as "12", "fell by" vs "fell to", "40 thousand" vs "40", "fiscal 2022" vs "2022", "two hundred" vs "two", "1 200" vs "200", "40-50" vs "50", 03/04 vs 04/03, version 2.10 vs 2.1.
  - A condition dropped from the middle of a quoted sentence.

---

## 5. Known limits

These are open. We list them so you do not find them by accident and conclude the tool is broken or, worse, that it is safe.

### Write-then-Read laundering (J-35)

The hook treats every `Read` as verbatim and records nothing about where the file came from. If an agent writes an invented claim into a file, reads the file back, and cites it, the result is PASS 100.0 and GROUNDED. The same text through native `WebFetch` is correctly refused. This happens before the store is written, so the engine cannot see it. Writing claims to a different file and reading that one still works as well. Status: open, owner Sai, no fix yet.

What to do: treat PASS as "traceable to something the session read", not "traceable to the outside world". Check where the cited files came from.

### "There is no X" claims and agent-chosen searches (J-36)

No search tool is recorded by the hook. So the "two distinct searches" behind an absence claim are two strings the drafting agent chose, not searches we observed. They have been shown to certify an absence from two reads of self-named files, from two off-topic pages whose URLs contain the right words, and from one page fetched twice. A related finding (R20-04: two FAILED fetches certifying an absence claim) is FIXED in this build: a failed or blank fetch no longer counts as a search, and cannot back up any claim. What remains open is the part above — successful fetches of pages the agent picked can still count as the searches. Status: open (J-36).

What to do: do not trust a PASS on an absence claim. Look at `evidence_basis` and judge the searches yourself.

### Store never rotated, and the 1970 timestamp (J-38)

The store is opened in append mode and never cleared. A later session that cites an earlier session's `[S2]` can PASS at 100.0. Every record's `fetched_at` is the fixed placeholder `1970-01-01T00:00:00Z`, so do not read it as a date. `session_id` IS written on records in a live interactive session (checked 2026-10-10), but older records carry a blank one.

The repo calls "the store is per-session" an aspiration, not a guarantee, and the largest open gap in the product.

Workaround: pass `--session-id <id>`. The gate then REFUSES a store that holds any other session's evidence. Your session id is on each record in the store. Without the flag, no session enforcement exists and the scope line says so. Wiring this in as the default (J-49) is not built.

Tip: to clear old evidence yourself, you could start from a fresh project folder. We have not tested that as a supported workflow, so: not verified. Never edit the store to make a draft pass; that defeats the tool.

### CI and `claude -p` are unsupported (J-55)

The capture hook does not run in print mode. The store stays empty and every claim reads UNCITED. This was verified on 2026-10-02 against a plugin hook, a project settings hook and an explicit `--settings` hook. None fired. The team decided CI is not a launch target. Interactive only. Revisit only if a customer asks.

### Causal claims are never certified (ADR-007)

ADR-007 is our decision record of 2026-10-02. "X causes Y" passes only if a cited source contains that claim word for word. Two sources each mentioning one end of it no longer counts, because a red-team round found seven ways to fake that. A draft full of causal prose will come back mostly UNGROUNDED. That is the gate working. Quote a source or soften the claim. The relational branch also has seven known bypass shapes, registered and not fixed (J-57 to J-62, J-64).

### The install.sh session-id snippet crashes on a fresh install (A-5-01)

At the end, `install.sh` prints a command to read your session id from the store:

```
SID=$(.venv/bin/python -c "import json;print(json.loads(open('.assure/evidence-store.jsonl').readline()).get('session_id',''))")
```

On a fresh install the store file does not exist yet. The hook creates it only after it has fired at least once. So pasting this right away gives:

```
FileNotFoundError: [Errno 2] No such file or directory: '.assure/evidence-store.jsonl'
```

Severity is low. It costs confidence, not correctness. It is not fixed (`install.sh` is on our park list for the owner).

Workaround:
1. Run some research in an interactive session first, so the hook fires and `.assure/evidence-store.jsonl` exists. Check with `ls .assure/`.
2. Then run the snippet.
3. If `SID` comes back empty, stop. Do not pass `--session-id ""`. The engine refuses an empty value on purpose. An empty id means the records have no session id, so the store cannot be scoped.

Run the snippet from the folder that contains `.assure/` and use the plugin's own `.venv/bin/python` (adjust the path if you are in your project folder, not in `Agent-Assure`). Note also that the snippet reads the FIRST line of the store. In a store that has run for several sessions, the first line may belong to an old session. We have not tested what happens then, so: not verified. Prefer the last line of the file for your current session.

### Other limits worth knowing

- Native `WebFetch` returns a model-written summary. It is recorded as `haiku_summary` and the gate refuses to certify against it (UNGROUNDABLE).
- Paraphrases are refused. Expect false alarms (UNGROUNDED on true claims). The tool is built to refuse rather than guess.
- Phase 2 items (a model-based paraphrase check, calibration, cross-platform support) are not built. Windows and Linux: not verified.

---

## 6. What to report back, and how

How: send it to the team contact who gave you this guide. We have no public issue tracker for the alpha that we can confirm: not verified. Plain text or a markdown file is fine.

A useful bug report has these five things. Without them we usually cannot reproduce.

1. The draft. The exact file, as you ran it. Redact private content, but keep the citation markers and the sentence that went wrong.
2. The store line or lines. The relevant record(s) from `.assure/evidence-store.jsonl`: `source_id`, `tool`, `full_text_source`, `session_id`, `query_provenance`, and the first few hundred characters of `text`. If a line is private, tell us what you changed.
3. The verdict. The gate, the score, the per-claim verdict, the `evidence_basis` and the `scope` text. Paste the `--json` output if you can.
4. What you expected, and why. One sentence. "I expected UNGROUNDED because the source says the opposite" is far more useful than "wrong result".
5. Your setup. How you ran it (plugin or manual CLI), interactive or not, the exact commands, your operating system, and your Python version.

Reports we want most:
- The demo's fabricated draft does not FAIL.
- A PASS on a claim that you can show the source does not support, or that came from a file the agent wrote itself.
- A refusal on an honest, verbatim claim. Say whether you used a paraphrase, since paraphrases are refused by design.
- The hook not firing in an interactive session (no `.assure/evidence-store.jsonl` after research).
- A traceback of any kind. The engine is meant to print `REFUSED: <reason>` and exit 1 instead. Anything else is a bug.
- Whether you read PASS as "traceable" or as "correct". Tell us honestly. How readers interpret PASS is a question the team has not yet tested with real users.

Please do not:
- edit the store to turn a failure into a pass;
- report a CI or `claude -p` empty store as a bug (it is a known limit);
- report J-35, J-36 or J-38 as new unless you found a different shape of them.

Not verified anywhere in this guide: behavior on Windows, behavior with plugin install routes other than `--plugin-dir`, and anything you will see outside Claude Code.
