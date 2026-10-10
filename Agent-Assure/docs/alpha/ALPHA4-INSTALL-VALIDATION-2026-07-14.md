# Phase α4 — Second-Repo Install Validation

**Date:** 2026-07-14. **Executor:** Sonnet 5 (scripted/non-interactive execution per
ALPHA-READINESS-PLAN.md §α4, adapted for headless run — no live Claude Code plugin
registration, no interactive `/assure-verify`; the equivalent CLI calls were made
directly). **Scope:** simulate a fresh, second-repo install of Agent-Assure and
validate the capture → verify loop end-to-end against real retrievals from an
unrelated repo (`financial-advisor-india`).

**Rule compliance:** original repo (`Agent-Assure/`) untouched except this file and
`docs/alpha/`; all execution happened in a scratchpad copy
(`<scratchpad>/alpha4-install/Agent-Assure`, `.venv`/`.pytest_cache` excluded from the
copy to simulate a true fresh checkout); `financial-advisor-india` was read-only
(5 `Read` calls, no writes); no git commands were run anywhere.

---

## 1. Install transcript

```
$ bash install.sh
🔎  Agent-Assure Installer
==========================
Provisioning virtual environment (.venv) and installing runtime deps...
Verifying the engine, hook, and dependencies import...
  engine + hook + deps: OK
✅ Agent-Assure environment ready: <scratchpad>/alpha4-install/Agent-Assure/.venv
```

- **Exit code:** 0. **Duration:** 3s. **Errors:** none.
- `.venv/bin/python scripts/ground_check.py --help` ran clean from the fresh env
  (argparse usage printed, exit 0) — confirms the gate is executable standalone,
  no plugin registration required for CLI use.
- **Friction (see §4, F-1):** `install.sh` runs bare `uv sync` (deliberately, per
  its own comment — pytest is dev-only). The project's own `CLAUDE.md` "Commands"
  section lists `uv run pytest` as the very next line a second-repo installer
  would naturally try. That command silently resolves to an unrelated **global**
  pytest (`~/.pyenv/shims/pytest`) rather than failing loudly, producing 46 opaque
  `ModuleNotFoundError` failures that look like a broken install. Root-caused and
  reproduced (see §4, F-1) — not a defect in `install.sh`'s own contract (it never
  promised dev tooling), but a real onboarding trap.

## 2. Evidence-store build (real capture path)

Method: read 5 real files from `financial-advisor-india` (unrelated repo,
read-only) via the `Read` tool, then fed each through the copy's
`scripts/capture_hook.py` on **stdin** — exactly how the `PostToolUse` hook is
invoked — using the live-validated `Read` envelope shape from
`tests/test_live_shapes.py` (`{"type": "text", "file": {"filePath", "content",
"numLines", "startLine", "totalLines"}}`, `tool_name: "Read"`).

| # | File | source_id | full_text_source | captured_via | chars |
|---|---|---|---|---|---|
| 1 | README.md | S1 | verbatim | inline | 313 |
| 2 | CLAUDE.md | S2 | verbatim | inline | 8,281 |
| 3 | SETUP.md | S3 | verbatim | inline | 4,340 |
| 4 | PRODUCT_ROADMAP.md | S4 | verbatim | inline | 9,787 |
| 5 | SESSION_HANDOFF.md | S5 | verbatim | inline | 6,364 |

Store: `.assure/evidence-store.jsonl`, 5 lines, 32,487 bytes. All 5 hook
invocations exited 0 with **empty stderr** — no capture friction, no shape
mismatches. Confirms the `Read` extractor path in `capture_core.py` is correct
against the live-validated envelope for a genuinely unrelated repo.

## 3. Gate runs

### Run 1 — clean draft (9 genuine claims, all 5 sources cited)

Getting from a first honest draft to PASS was **not** immediate — see §4 for what
that revealed. Final verdict:

```json
{"gate": "PASS", "grounding_score": 100.0, "per_claim": [
  {"index": 0, "kind": "FACTUAL", "text": "Financial Advisor India is a white-label AI research assistant for Indian brokerages [S1].", "verdict": "GROUNDED"},
  {"index": 1, "kind": "FACTUAL", "text": "It covers NSE/BSE equities, mutual funds, and F&O [S1].", "verdict": "GROUNDED"},
  {"index": 2, "kind": "FACTUAL", "text": "Financial Advisor India is a white-label AI research assistant for Indian brokerages [S2].", "verdict": "GROUNDED"},
  {"index": 3, "kind": "FACTUAL", "text": "The auth proxy refuses to start unless both key variables are set [S3].", "verdict": "GROUNDED"},
  {"index": 4, "kind": "NUMERIC", "text": "The service is pinned to --max-instances=1 [S3].", "verdict": "GROUNDED"},
  {"index": 5, "kind": "NUMERIC", "text": "4 sprints delivered a demo-ready system with multi-agent architecture, SEBI compliance, white-label theming, testing infrastructure [S4].", "verdict": "GROUNDED"},
  {"index": 6, "kind": "NUMERIC", "text": "Sprint 1 delivered auth proxy, rate limiting, audit logging, SSE streaming [S4].", "verdict": "GROUNDED"},
  {"index": 7, "kind": "NUMERIC", "text": "Backend tests 43 passing SEBI compliance tax rates language model config data coverage [S5].", "verdict": "GROUNDED"},
  {"index": 8, "kind": "NUMERIC", "text": "Frontend tests 20 passing components XSS protection theme input validation [S5].", "verdict": "GROUNDED"}
], "retained_appendix": [], "scored_claims": 9, "vacuous": false}
```

Exit code 0.

### Run 2 — same draft + one deliberate fabrication

Added claim 10, a numeric-drift fabrication citing a real source: *"The backend
test suite reached 97 passing cases after the latest hardening pass [S5]."*
(S5 genuinely says 43 backend tests passing — 97 is fabricated, plausibly worded,
correctly cited.)

```json
{"gate": "NEEDS_WORK", "grounding_score": 90.0, "per_claim": [
  "... (claims 0-8 unchanged, all GROUNDED) ...",
  {"index": 9, "kind": "NUMERIC", "text": "The backend test suite reached 97 passing cases after the latest hardening pass [S5].", "verdict": "UNVERIFIED_NUMBER"}
], "retained_appendix": [
  {"index": 9, "text": "The backend test suite reached 97 passing cases after the latest hardening pass [S5].", "verdict": "UNVERIFIED_NUMBER"}
], "scored_claims": 10, "vacuous": false}
```

Exit code **1**. The fabrication is named exactly (`index 9`), correctly typed
(`UNVERIFIED_NUMBER`), and blocks PASS via the ADR-005 retained-appendix cap —
moat holds end-to-end on a genuinely fresh install against unrelated real content.

## 4. Friction list

| # | Finding | Severity | Case vs Systemic |
|---|---|---|---|
| F-1 | **`uv run pytest` silently falls back to a foreign global pytest** when the one-time `uv sync --extra dev` step is skipped (which a fresh `install.sh`-only install does skip — install.sh deliberately only runs bare `uv sync`). Reproduced: bare copy → `uv run which pytest` resolves `~/.pyenv/shims/pytest`, not `.venv/bin/pytest` → 46/351 tests fail with `ModuleNotFoundError: No module named 'syntok'` (a project runtime dep that IS present in `.venv`, just not visible to the wrong interpreter). After `uv sync --extra dev`, `uv run which pytest` resolves the local `.venv/bin/pytest` and all 351 pass + 2 xfailed. **This is a pure environment-resolution artifact, not a code defect** — but a second-repo installer following the project's own `CLAUDE.md` command list in order (`install.sh` then `uv run pytest`) will see 46 confusing failures and reasonably conclude the install is broken. | **HIGH** (trust/onboarding — first impression of a second install is "broken") | Systemic: `install.sh` should either run `uv sync --extra dev` itself, or its success banner should say so explicitly before pointing at test commands. Not filed as a new OPEN-ISSUES.md entry per the "nothing else in the repo" output constraint on this task — flagging here for promotion (would be `OI-INSTALL-01`). |
| F-2 | **Conjunction-splitter (`_conjunction_split`, and its `_has_verb_like_token` heuristic) detaches a trailing citation from an earlier clause** whenever a genuinely single-sourced compound sentence contains " and " / "; " and both sides look verb-like. Reproduced repeatedly: e.g. "The auth proxy runs on port 9000 and fronts the ADK backend..., and clients never reach port 8000 directly [S2]." split into 3 claims, only the last carrying `[S2]` — the first two read `UNCITED`/`UNGROUNDED` even though the whole sentence came from one genuinely-cited source. The suffix heuristic also over-fires on **plural nouns** ending in "s" (e.g. "clients" is treated as verb-like), which is what triggered several of these splits. This is a genuine, reproducible Error-A source distinct from the documented "marker after final period" gotcha. | MEDIUM (Error-A, recoverable — but will surprise every second-repo user who writes natural compound sentences) | Systemic (not fixed here — out of scope for α4; flagging for the calibration-owning phase, since any classify/decompose change requires a full CR re-run per CLAUDE.md convention #9). |
| F-3 | **`syntok`'s sentence segmenter silently merges two adjacent sentences into one claim** when the first ends in a parenthetical-numeric pattern before the period (e.g. "...fronts ADK (:8000). The auth proxy refuses..." became ONE claim carrying both `[S2]` and `[S3]` citations). Not caught by any existing test in the copy's suite. Low-frequency (only fires on this specific punctuation shape) but worth a regression fixture — a merged claim with a mixed citation set could mask which source actually grounds it. | LOW-MEDIUM | Systemic — needs a proven-red regression fixture before any fix; flagging, not fixing (out of scope for α4). |
| F-4 | **Short, symbol/entity-heavy technical claims (ports, code identifiers, ticker-style tokens) ground poorly under T1/T2 without near-verbatim phrasing.** Getting the clean draft from FAIL → PASS required iterating from natural paraphrase to close-to-verbatim quoting for several claims (documented in this file's construction history). This is the **expected, by-design** consequence of the T3 NLI paraphrase tier being unbuilt (Phase 2b, per CLAUDE.md Gotchas) — recorded as a finding, not a bug, per the task's "Error-A instances are findings, not failures to hide" instruction. A genuine second-repo user writing an honest summary (not a quote-heavy draft) should expect to hit this and will need the NLI tier before Alpha's UX is comfortable. | MEDIUM (expected/documented limitation, but real UX friction for a first-time user) | N/A — already tracked as Phase α3 (2b NLI tier) in ALPHA-READINESS-PLAN.md. |
| F-5 | **Confirmed independently: `lex_tau` cross-artifact drift.** `t2_lexical()`'s live default is **0.65**, not the CR-001 calibrated **0.71** — the CLI threads no `lex_tau` override through `ground()`. This matches the already-logged `OI-CAL-01` (`docs/open-issues/OPEN-ISSUES.md`, found 2026-07-14, same day) — re-confirmed independently during this validation via direct code trace of `ground()` → `t2_lexical(claim, verbatim)` (no `lex_tau` kwarg passed) and cross-checked against `calibration/CR-001-bootstrap-lex-tau.md`. Not re-filed as a new item; cross-referencing here since it directly affects what "PASS" means during this validation (both runs above executed at the shipped 0.65, not the calibrated 0.71). | Already tracked — HIGH per OI-CAL-01 (awaiting Sai's deploy-now-vs-hold-for-CR-002 call). | Escalation rule #1 already invoked in OPEN-ISSUES.md; no new escalation needed. |
| F-6 | Capture path itself: **zero friction.** All 5 `Read` retrievals captured cleanly on the first attempt with the live-validated envelope shape; no shape mismatches, no stderr, no manual store editing required. | — (positive finding) | — |

## 5. Verdict

**READY**, with caveats, for external second-repo alpha install — the capture →
verify loop works end-to-end against a genuinely unrelated repo's real content,
and the core moat property held (fabricated numeric claim, plausibly worded,
correctly cited to a real source, was caught and blocked exit-1 on a fresh
install with zero LLM calls in the grounding path).

Caveats an alpha tester will hit, in priority order:
1. **F-1 must be fixed or documented before shipping** — a silent test-runner
   PATH fallback producing 46 false failures is the single highest-risk item
   for a second installer's first impression, and it is pure onboarding
   friction (zero relation to the moat).
2. **F-5 (`OI-CAL-01`) needs Sai's ruling** before any Alpha claims to run at
   "the calibrated threshold" — right now it doesn't.
3. **F-2/F-3 are real but lower-frequency Error-A surprises** an alpha tester
   writing natural (non-quote-heavy) prose will encounter; not moat-breaking,
   but will read as "the tool rejected my honest, correctly-cited claim" until
   Phase α3's NLI tier lands.

None of the above is an Error-B (false PASS on a fabrication) — the invariant
CLAUDE.md cares about most held throughout this validation.

## 6. Load-bearing assumption

This validation used a **scratchpad copy fed via a script mirroring the
PostToolUse stdin contract**, not a live Claude Code session invoking the real
hook through an actual plugin registration. The assumption that stands underneath
"READY": the live hook's stdin payload for `Read` genuinely matches
`tests/test_live_shapes.py`'s captured shape (last validated 2026-07-03, per that
file's own docstring). If Claude Code's actual `PostToolUse` envelope has drifted
since that live-validation date, this run's "zero capture friction" (§4, F-6)
would not transfer to a real second-repo session — that live-shape assumption
was not re-probed here and is the one thing that would collapse this READY
verdict if wrong.
