# Agent-Assure alpha walkthrough (tester, no prior knowledge)
Sandbox: /private/tmp/claude-501/ovn1115-q3/ ; clone from GitHub succeeded (no fallback needed). HEAD ef3ae1f.

## Steps
Environment: macOS, uv present; UV_CACHE_DIR pointed into sandbox. install.sh NOT run (instruction). Hook/plugin registration NOT done, so /assure-verify and live capture were not exercised.

| # | Step | Command / output (trimmed) | Tag | Sev |
|---|---|---|---|---|
| 1 | Clone | `git clone https://github.com/saisumantatgit/agents-infra clone` -> OK, HEAD ef3ae1f | OK | - |
| 2 | Top-level README | 120+ lines; describes PROVE/Scribe/Shield (v1.x), "Think. Record. Shield."; `grep -i assure README.md` = 0 hits. Install section tells you to clone three separate repos (Agent-PROVE, Agent-Scribe, Agent-Shield). Agent-Assure is never named, linked, or located. | WRONG-DOC | High |
| 3 | Find the guide | Task/README path `Agent-Assure/ALPHA-TESTER-GUIDE.md` does not exist; real path is `Agent-Assure/docs/ALPHA-TESTER-GUIDE.md` (found via `find -iname '*alpha*'`, which also returns 3 other alpha reports, 2 install-validation reports with different dates). Agent-Assure/README links it as `docs/ALPHA-TESTER-GUIDE.md` (correct, relative). Top-level README gives no route to either. | STALL | High |
| 4 | Agent-Assure/README | Opens with "Phase 1 scope (built): ... 1a/1b/1c", "ADR-005", "J-48", "OI-MOAT-02/-006", "CR-007", "R15-03" etc. inline, mostly unexplained. Lead warning ("Quote your sources... 0 of 20 paraphrased honest drafts passed") is good. "Install" says `bash install.sh` then "register the directory as a Claude Code plugin" with no command; the guide says `claude --plugin-dir`. README Quick Start uses `uv run python`, guide uses `.venv/bin/python` (two conventions). | CONFUSING | Med |
| 5 | Guide opening | Clear, honest, strongest doc in the repo. Section 2 requires `cd Agent-Assure; bash install.sh` and a live interactive Claude Code plugin session for the "real" run; install.sh writes .venv and prints a session-id snippet the guide itself says crashes on a fresh install (A-5-01, known). Not run per instructions; guide step 2 therefore not doable by a tester who will not/cannot register a plugin in their real ~/.claude. | CONFUSING | Med |
| 6 | Substitute for install.sh | `uv sync` (documented in README "Running Tests") -> .venv created, Python 3.12.14, 9 deps, no output errors. Guide demo uses `.venv/bin/python`, which exists after either route. | OK | - |
| 7 | Guide step 1: demo | `build_store.py` -> "wrote .../demo/evidence-store.jsonl (2 sources)". Grounded draft: `gate: PASS | score: 100.0`, exit 0. Fabricated: `gate: FAIL | score: 50.0`, UNVERIFIED_CITATION + UNVERIFIED_NUMBER, exit 1. Matches the guide exactly. | OK | - |
| 8 | Demo output readability | show_report prints verdict + 70 chars of claim only. For the fabricated draft it does not say WHY ("[S3] not in store"; "100 times not in any source, source says twelve"). The guide explains it in prose, the tool does not. Also build_store.py re-run leaves a file in demo/ (not tracked changes, fine). | CONFUSING | Med |
| 9 | Build a store for MY source | Guide gives no way to test your own source without a live plugin session. Only way: hand-write JSONL from README "EvidenceStore JSONL Format". README schema omits `session_id`, which the guide says live records carry. I wrote 5 sources, 1 per draft (work/store.jsonl). | STALL | High |
| 10 | Manual CLI, no --json | `ground_check.py --draft d1 --store store.jsonl` prints `gate=NEEDS_WORK grounding_score=75.0` plus the scope paragraph, writes `grounding-report.yaml` into CWD (as documented). Per-claim verdicts and reasons exist only in the yaml/--json, and the guide's recommended renderer (demo/show_report.py) is in a demo folder. Missing store -> clean `REFUSED: no evidence store ...` exit 1, good message. | CONFUSING | Med |

## My 5 drafts (source = my own text in work/store.jsonl; drafts in work/d*.md)

| Draft | Intent | Verdict | Did output explain WHY / what to fix? |
|---|---|---|---|
| d1 product note | honest, copied source sentences, cited [S1] | NEEDS_WORK 75.0. Title line "# Kestrel 2.4 note" = UNCITED, scored as a claim (only the demo headers pass, because they are inside the source). Sentence 1 was cut into two "claims", second shown as "reduces average job queue latency..." (subject dropped) | Partly. UNCITED on a title is baffling; no hint that headings need a citation or a source match, and nothing says "title is the reason you did not PASS". Guide section 4 says headers show GROUNDED and are not scored: contradicted for a header not in the source. Severity Med WRONG-DOC / CONFUSING |
| d2 meeting summary | 1 fabrication: 90000 dollars (source says 25000) | FAIL 0.0, every claim UNGROUNDABLE (incl. 3 honest verbatim ones), the fabricated number is NOT flagged as UNVERIFIED_NUMBER | No. Fabrication hidden behind a store-wide UNGROUNDABLE; evidence_basis says "Checked verbatim against 1 cited source: S2" while verdict says no verbatim source (self-contradiction). Cause not discoverable by a tester. BUG, High |
| d3 README section | honest paraphrase of "To install the tool run pip install..." | FAIL 50.0, claim 1 UNGROUNDED, claim 2 (verbatim) GROUNDED | Guide predicted this; the one-line verdict still gives no "quote your source" nudge in the output itself and no pointer to the matching sentence. Fix inferable only from the guide. CONFUSING Low (expected behaviour) |
| d4 table report | 2 fabrications: total 12.0 vs 10.0; cites [S6] never captured | FAIL 20.0: UNVERIFIED_NUMBER and UNVERIFIED_CITATION both correct. But the markdown table is one UNCITED claim (scored), plus the title UNCITED, which together halve the score | Fabrication catches: clear. Table-as-UNCITED-claim: not explained; a table needs a per-row citation scheme the docs never describe. WRONG-DOC / CONFUSING Med |
| d5 code explanation | honest, 3 verbatim sentences | FAIL 0.0, all 3 UNGROUNDABLE ("no_cited_verbatim_source") although store line is full_text_source=verbatim | Not understandable, not fixable. Minimal repro: source "The function retry_with_backoff calls the wrapped function up to five times. Other." + same claim -> UNGROUNDABLE; same source with a "Code source: " prefix or a longer tail -> GROUNDED. Trigger not isolated (see t.py in work/); looks like a verbatim-source-detection bug on short sources. BUG, High |

Fabrication recall: 2 of 2 deliberate fabrications reached a non-PASS gate; in d2 the correct failure reason was masked. Honest-draft pass rate: 0 of 3 PASS (d1 title, d3 paraphrase, d5 bug).
`--session-id`, /assure-verify, live hook, and the real-session step were not run (needs plugin registration into ~/.claude; out of bounds).

## Finding counts
OK 4 (clone, uv sync, demo, missing-store message) | STALL 2 | WRONG-DOC 3 | CONFUSING 8 | BUG 2

## Top 10 fixes, ranked by testers affected
1. Top-level README does not mention Agent-Assure at all; add it to the suite table, install section, and link `Agent-Assure/docs/ALPHA-TESTER-GUIDE.md` (every tester hits this on page one).
2. Put the guide at the path people look for (Agent-Assure/ALPHA-TESTER-GUIDE.md) or link it from README's first paragraph and from the top-level README; today `find` is the only way.
3. Provide a documented "bring your own source" path without a live Claude Code session (e.g. `scripts/add_source.py file.txt` that writes a valid store line). Today every tester must hand-write JSONL from a schema that omits session_id.
4. Verdict output must say WHY per claim in plain words by default: no-JSON mode prints one line; show_report truncates to 70 chars and drops reasons. Ship the readable renderer as part of scripts/ and print per-claim reason + fix hint (e.g. UNGROUNDED -> "quote the source sentence").
5. Fix/explain UNGROUNDABLE on verbatim sources (d2, d5): reproduce with short sources; the message "no_cited_verbatim_source" contradicts "Checked verbatim". It also hides real fabrications (d2's wrong number).
6. Headings/titles: UNCITED titles drag the score (d1 75.0 NEEDS_WORK from a title alone). Either exclude headings from scoring or document it; the guide claims headers are unscored.
7. Tables: document how to cite tables, or classify table blocks as NON_CLAIM; the whole table is one UNCITED claim today.
8. Sentence splitting drops the subject ("reduces average job queue latency..." shown as its own claim) and splits at "and"; document it and show the split in the verdict output.
9. Install story: README says "register the directory as a plugin" with no command; guide says `claude --plugin-dir`. Make one command appear in both, and add a no-registration demo-only path banner ("demo needs only uv sync"). Also fix A-5-01 (install.sh prints a command known to crash).
10. De-jargon the first screen of Agent-Assure/README (ADR-005, J-48, OI-MOAT-02, CR-007, R15-03, "Phase 1 1a/1b/1c" unexplained); lead with the guide's plain-language "quote your sources" and a 3-line quick start.
