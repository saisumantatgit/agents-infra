# Agent-Assure: Alpha Tester Guide

You are trying Agent-Assure for the first time, on your own. This guide tells you what to expect, what it can and cannot tell you, and what to send back to us.

Every statement here comes from the repo (README, install.sh, the skill, the command, the failure-types reference, the register, and the ALPHA-5 report). Where we could not confirm something, the guide says "not verified".

---

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

Then register the directory as a Claude Code plugin. The installer's own text offers three ways: `claude --plugin-dir <path to Agent-Assure>`, add it to your plugin marketplace, or copy it into your Claude Code plugins path. We have only seen the `--plugin-dir` route described in the repo. The other two are not verified by us.

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

---

## 4. Reading a report

### The gate (top line)

- PASS: every scored claim is traceable AND the score is at or above the threshold. One bad claim blocks PASS, whatever the score. PASS does not mean the source agrees with the claim or is right.
- NEEDS_WORK: the score is 60 or more, but at least one claim has a problem (or the score is under the threshold, or nothing could be scored). Fix the listed claims and run again.
- FAIL: the score is below 60. This is checked first, so a low score is FAIL even if other problems exist.

The score is the share of scored claims that are GROUNDED or ABSENCE_SUPPORTED. Headers, questions, instructions and pure opinion (NON_CLAIM) are left out of the count.

If the store is empty, you get NEEDS_WORK with `vacuous: true`. That means "nothing to check against", not "all clear".

### Per-claim verdicts

Passing:
- GROUNDED: the claim's words appear in a source retrieved word for word (a run of 8 or more matching words, or equivalent). Headers and similar lines also show GROUNDED but are not scored.
- ABSENCE_SUPPORTED: a "there is no X" claim backed by at least 2 recorded searches that each name the full subject. See the limit in section 5.

Failing (each one stops the gate from reaching PASS):
- UNVERIFIED_CITATION: the claim cites a source id (like `[S9]`) that is not in the store. The source was never retrieved this run. This is the fabricated-citation catch.
- UNGROUNDED: the cited sources exist, but none contains support for the claim. It means "could not trace this", never "this is false". Honest paraphrases land here often. About two in five honest claims were refused on our 52-claim test set (error rate 0.400, calibration record CR-007).
- UNCITED: a factual claim with no citation marker. It is also what you see when the marker was placed after the period, or when the store is empty.
- UNVERIFIED_NUMBER: a number in the claim matches no source. Value, unit and, if the claim states one, the rate must all match. "25%" is not "25". "per minute" is not "per second".
- UNVERIFIED_ABSENCE: a "no X exists" claim with fewer than 2 recorded searches that name the full subject.
- UNVERIFIED_RELATION: a "A causes B" style claim without two separate sources, one per side. See ADR-007 in section 5.
- UNGROUNDABLE: every cited source is non-verbatim (for example a `haiku_summary` from native `WebFetch`), or empty. The engine refuses to check against a summary. Re-fetch with Exa or a raw `Read`.

Other per-claim fields you will see in the JSON: `evidence_basis`, `support_diagnostic`, and, for causal claims, `relation_diagnostic`.
- `support_diagnostic` of `cited_sentence_may_not_assert_claim` means: go read that source sentence yourself. It is advice, not a verdict. It misses about half of the denials we built (7 of 14).
- `relation_diagnostic` of `corroborated_by_two_sources` next to UNGROUNDED is the normal result for an honest causal claim.

### The scope line

Every JSON report has a `scope` field. It is the engine's own statement of what PASS means. Without `--session-id` it reads:

```
PASS means every claim in this draft is traceable to text in a source present in the evidence store supplied to this run; it does not mean the source agrees with the claim, and a source that denies or hedges a claim can still satisfy this check. Session scope is NOT asserted: pass --session-id to require that the sources were retrieved this session.
```

With `--session-id <id>` it says "retrieved this session" instead. Read this line. If it says "Session scope is NOT asserted", the store may hold sources from earlier sessions (see J-38 below). The word "verified" is deliberately never used in the output.

Whether the plain-text summary (non `--json`) and the demo renderer print the scope line: not verified. The JSON field is confirmed.

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
