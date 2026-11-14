# Tester tools: add_source.py and explain_report.py (2026-11-15)

Source: reports/ALPHA-WALKTHROUGH-2026-11-15.md items 3 (bring your own source), 4 and 10 (reasons per claim, jargon first screen). No verdict logic changed: ground_check.py, install.sh, hooks and calibration/ are untouched.

## What was built
- scripts/add_source.py FILE --id S1 --store STORE [--session-id X]: writes one record with the capture hook's fields (tool Read, verbatim, NFKC text, sha256 of NFKC text). Validates the combined store in a temp file with ground_check.load_store (imported, not reimplemented), then swaps it in atomically. Exit 1 and store untouched on duplicate id, missing file, empty file, or any loader refusal.
- scripts/explain_report.py [REPORT.json]: renders ground_check --json (stdin or file). Header has gate, score, scored-claim count and the scope line; per claim the verdict, full wrapped claim, evidence_basis, and a one-line fix hint (FIX_HINTS, from the guide's verdict table); NON_CLAIM lines listed under "not scored". Exit 0 iff gate is PASS. Reads per_claim only (retained_appendix duplicates it). Non-report input is refused with exit 1.
- tests/test_tester_tools.py: 6 tests.
- Docs: guide "Check your own source" and "Getting the reason for each claim" now use the scripts (inline builder and python one-liner removed; the hand-built-store hint points to add_source.py). README first screen: 3-command quick start (uv sync + demo, ground_check to report.json, explain_report) above the jargon; the existing glossary line (ADR, J-nn, OI, CR, R-nn, all already defined in the README) sits directly under it. "Phase 1 1a/1b/1c" is left unglossed: no source in docs defines it.

## Red then green
- Red (scripts absent): `uv run pytest tests/test_tester_tools.py` -> 6 failed (python: can't open file scripts/add_source.py / explain_report.py).
- First green attempt: 5 passed, 1 failed. The failure was my test's source, a single sentence equal to the draft; the engine correctly refused it as a copy of the draft (UNGROUNDABLE, cited_source_is_the_draft). Test source lengthened; engine untouched.
- Green: 6 passed.

## Gates
- Full suite: 1291 passed, 2 skipped, 61 xfailed (baseline 1285 passed + 6 new).
- calibration/labels-v2.csv md5 = 6215b526d03147295b003d7ccb0d171f (unchanged). git status: only README.md, the guide, two new scripts, new test (plus this report).

## Documented commands run
- README quick start: build_store, ground_check --json > report.json, explain_report report.json -> `gate: FAIL | score: 50.0`, exit 1.
- Guide flow: add_source (exit 0, "store re-loaded OK"); same id again -> REFUSED, exit 1; ground_check with --session-id my-test-session -> `gate=PASS grounding_score=100.0`, exit 0; `ground_check --json | explain_report` -> `gate: PASS | score: 100.0`.
- Demo fabricated draft piped into explain_report: claims 3 and 4 show UNVERIFIED_CITATION / UNVERIFIED_NUMBER with reasons and fix lines; heading listed as not scored.

## Assumption that would collapse this
FIX_HINTS duplicate the guide's table text; if the table changes, the hints drift. No test ties them together (CEILING: two copies of the hint text; upgrade path: have a test parse the guide table and compare).
