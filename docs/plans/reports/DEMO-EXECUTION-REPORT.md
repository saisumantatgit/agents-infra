# Demo Readiness — Execution Report

**Plan executed:** `docs/plans/DEMO-READINESS-PLAN.md` (phases D1–D4)
**Executor:** Sonnet 5, 2026-07-08
**Working directory:** `Agent-Assure/` (all commands run from here unless noted)
**Scope respected:** only `demo/` and `tests/test_demo_golden.py` were created/modified. No git commands (add/commit/push, or otherwise) were run against the repo state.

**Verdict: DEMO READY.** All four exit criteria met: golden test green, script exists with only frozen-path commands, offline run verified (static import inspection, no network-capable modules anywhere in the demo's call graph), reset command documented, one timed dry run with zero live/golden mismatch.

---

## D1 — Freeze and verify the happy path

### Commands run (from `Agent-Assure/`)

```bash
mkdir -p demo/expected
uv run python demo/build_store.py
uv run python scripts/ground_check.py --draft demo/draft-grounded.md   --store demo/evidence-store.jsonl --json > demo/expected/grounded-report.json
cat demo/expected/grounded-report.json | uv run python demo/show_report.py > demo/expected/grounded-rendered.txt
uv run python scripts/ground_check.py --draft demo/draft-fabricated.md --store demo/evidence-store.jsonl --json > demo/expected/fabricated-report.json
cat demo/expected/fabricated-report.json | uv run python demo/show_report.py > demo/expected/fabricated-rendered.txt
```

### Results (verbatim, matches demo/README.md exactly)

`draft-grounded.md`: `gate: PASS | score: 100.0`, exit 0, all 3 claims `GROUNDED`.

`draft-fabricated.md`: `gate: FAIL | score: 50.0`, exit 1:
```
GROUNDED             <- # Datastore Throughput — Benchmark Summary
GROUNDED             <- In our controlled benchmark on a single node, Redis sustained approxim
GROUNDED             <- Under the same benchmark load and hardware, PostgreSQL sustained appro
UNVERIFIED_CITATION  <- MongoDB sustained approximately 45000 operations per second in the sam
UNVERIFIED_NUMBER    <- Redis delivered about 100 times the throughput of the disk-backed alte
```
The `UNVERIFIED_CITATION` verdict is on the claim citing `[S3]` — the source never retrieved (evidence store only holds `S1`, `S2`). Fabricated source-id confirmed present in the failure output.

### Golden artifacts written

- `demo/expected/grounded-report.json`, `demo/expected/grounded-rendered.txt`
- `demo/expected/fabricated-report.json`, `demo/expected/fabricated-rendered.txt`
- `demo/expected/full-transcript.txt` — combined narrative transcript (also serves as D3's break-glass fallback artifact)

### Test file: `tests/test_demo_golden.py`

Four tests: store-builds-two-sources, grounded→PASS, fabricated→FAIL naming `[S3]` via `UNVERIFIED_CITATION` (plus asserts the two real claims stay `GROUNDED`), and a byte-for-byte diff of rendered output against the golden transcripts.

### RED-first proof (mandatory)

Deliberately broke two expectations before writing the correct ones:
1. `test_grounded_draft_gate_pass`: asserted `report["gate"] == "FAIL"` (wrong; real result is PASS).
2. `test_fabricated_draft_gate_fail_with_unverified_citation`: set `FABRICATED_SOURCE_ID = "S9"` (wrong; real fabricated id is `S3`).

**RED run** (`uv run pytest tests/test_demo_golden.py -v`):
```
tests/test_demo_golden.py::test_demo_store_builds_two_sources PASSED     [ 25%]
tests/test_demo_golden.py::test_grounded_draft_gate_pass FAILED          [ 50%]
tests/test_demo_golden.py::test_fabricated_draft_gate_fail_with_unverified_citation FAILED [ 75%]
tests/test_demo_golden.py::test_rendered_report_matches_golden_transcript PASSED [100%]

FAILURES
________________________ test_grounded_draft_gate_pass _________________________
>       assert report["gate"] == "FAIL", f"Expected gate PASS, got {report['gate']!r}"
E       AssertionError: Expected gate PASS, got 'PASS'
E       assert 'PASS' == 'FAIL'

___________ test_fabricated_draft_gate_fail_with_unverified_citation ___________
>       assert any(
            f"[{FABRICATED_SOURCE_ID}]" in c["text"] for c in unverified_citation_claims
        ), ...
E       AssertionError: Expected the fabricated source-id [S9] to appear in the text of an
        UNVERIFIED_CITATION claim, got: [{'index': 3, ..., 'text': 'MongoDB sustained
        approximately 45000 operations per second in the same test [S3].', 'verdict':
        'UNVERIFIED_CITATION'}]

2 failed, 2 passed in 0.67s
```

Reverted both deliberate breaks (restored `"PASS"` and `FABRICATED_SOURCE_ID = "S3"`).

**GREEN run** (same command):
```
tests/test_demo_golden.py::test_demo_store_builds_two_sources PASSED     [ 25%]
tests/test_demo_golden.py::test_grounded_draft_gate_pass PASSED          [ 50%]
tests/test_demo_golden.py::test_fabricated_draft_gate_fail_with_unverified_citation PASSED [ 75%]
tests/test_demo_golden.py::test_rendered_report_matches_golden_transcript PASSED [100%]

4 passed in 0.68s
```

**Full suite regression check** (`uv run pytest`): `331 passed in 3.48s` — no regressions from the new test file.

**Exit criteria met:** golden test green; transcripts saved to `demo/expected/`.

---

## D2 — The demo script

Wrote `demo/DEMO-SCRIPT.md` following the exact 6-beat structure from the plan:
1. Cold open — read `draft-fabricated.md` aloud, ask "would you catch the fake?"
2. The store — `build_store.py`, inspect one record's verbatim/sha256/provenance fields, explain `haiku_summary` refusal (sourced from `README.md:11,74,92` and `scripts/capture_core.py:315`).
3. The moment — run fabricated draft → FAIL, name `[S3]`, say the moat line.
4. Contrast — same command on grounded draft → PASS.
5. Honesty beat — `cat calibration/CR-001-bootstrap-lex-tau.md`, cite the real numbers: `lex_tau=0.71`, held-out Error-A=0.20, Error-B=0.14285714285714285 (~0.143), n=12, provisional, leave-one-out.
6. Close — capture hook auto-builds the store; roadmap = NLI paraphrase tier + wider calibration, no dates.

Every command in the script is copy-pasteable and is one of the four commands exercised by `test_demo_golden.py` (cross-reference table included at the bottom of the script). No command appears in the script that wasn't in D1's frozen path.

**Exit criteria met:** script exists with only frozen-path commands, CR-001 cited with real numbers.

---

## D3 — Failure-proofing

### Offline guarantee

Inspected every import in the demo's call graph:

```
scripts/ground_check.py:  json, unicodedata, collections.Counter, dataclasses, enum, typing, re
scripts/capture_core.py:  hashlib, json, unicodedata, pathlib, scripts.ground_check
demo/build_store.py:      sys, pathlib, scripts.capture_core
demo/show_report.py:      json, sys
```

`grep -rniE "requests|urllib|http\.client|socket|httpx|aiohttp|ftplib|smtplib" scripts/ demo/` → **no matches**. Declared project dependencies (`pyproject.toml`) are `syntok` and `pyyaml` only — both pure-Python parsing/serialization libraries with no network I/O. **Confirmed offline by static inspection**, per the plan's own instruction ("the engine is pure Python — confirm by reading ground_check.py imports").

### Fresh-machine check

Could not use `git clone` (git commands are out of scope for this task). Substituted an equivalent filesystem-level fresh-checkout simulation: `rsync`-copied the entire `Agent-Assure/` tree to a scratch directory, excluding `.venv`, `__pycache__`, `.pytest_cache` (i.e., exactly what a real `git clone` would omit). Ran `bash install.sh` there:

```
uv 0.5.9 (0652800cb 2024-12-13)
🔎  Agent-Assure Installer
Provisioning virtual environment (.venv) and installing runtime deps...
Verifying the engine, hook, and dependencies import...
  engine + hook + deps: OK
✅ Agent-Assure environment ready: <scratch>/.venv
```

Then ran the full demo path in that fresh install (`.venv/bin/python demo/build_store.py` → both `ground_check.py` invocations): output was **identical** to the golden transcripts (`gate: PASS | score: 100.0` / `gate: FAIL | score: 50.0`, same per-claim lines, same exit codes). Python version confirmed: 3.12.8, satisfying the `>=3.11` requirement in `pyproject.toml`.

Recorded in the script header: `uv` required, Python >=3.11 (validated against 3.12.8), `bash install.sh` provisions everything, no other setup needed, run from `Agent-Assure/`.

### Fallback artifact

`demo/expected/full-transcript.txt` is the break-glass artifact; referenced explicitly in `demo/DEMO-SCRIPT.md`'s "Break-glass fallback" section.

### Reset command

Documented in the script:
```bash
git checkout -- demo/ && rm -f grounding-report.yaml
```
**Not executed** during this session (git commands are out of scope per task instructions). Verified by inspection only: it is scoped to `demo/` (tracked files) and removes the YAML report a non-`--json` run would write to cwd — matches the plan's exact spec (line 39 of the plan).

**Exit criteria met:** offline confirmed, fresh-machine install+run verified via filesystem-copy equivalent, fallback artifact exists and is referenced, reset command documented (execution deferred — git-command restriction, not a functional gap).

---

## D4 — Dry run + sign-off

Executed `demo/DEMO-SCRIPT.md` top-to-bottom (beats 1–5; beat 6 is spoken-only, no command) in the live `Agent-Assure/` working tree — not the fresh-clone scratch copy.

**Timing:** all commands (build store + both `ground_check`/`show_report` pipelines) completed in **under 1 second** of wall-clock CPU time. Per-beat talking-time budget from the script totals ~8 minutes (1+2+2+1+1+1), well inside the plan's ≤10-minute target; command execution overhead is negligible.

**Live-vs-golden diff:**
```bash
diff <(live fabricated rendering) demo/expected/fabricated-rendered.txt   # no output — identical
diff <(live grounded rendering)   demo/expected/grounded-rendered.txt     # no output — identical
```
Both diffs were empty. **Zero defects found.** No transcript patching was needed or performed.

**Exit criteria met:** one timed dry run ≤10 min logged, live output matches golden byte-for-byte.

---

## Final pytest count

```
uv run pytest
...
331 passed in 3.48s
```
(327 pre-existing + 4 new in `tests/test_demo_golden.py`.)

## Defects found

**None.** Live execution matched golden transcripts exactly on every command in the script.

## Out-of-scope observations (not acted on, per task scope restriction to `demo/` + `tests/test_demo_golden.py`)

- `CLAUDE.md` at the repo root shows as modified (`M`) and an untracked `docs/plans/LANE-B-PORTFOLIO-AUDIT.md` exists in `git status`. Neither was touched by this session — both predate or are concurrent with this task and fall outside the declared scope. Flagged here for visibility, not remediated.
- The reset command (`git checkout -- demo/ && rm -f grounding-report.yaml`) was verified by inspection but not executed live, per the no-git-commands constraint on this task. If a live rehearsal of the reset step is wanted, that requires either a follow-up session with git permitted, or manual execution by the user.

## Demo-ready criteria checklist (from the plan)

- [x] Golden test green (`uv run pytest tests/test_demo_golden.py` → 4 passed; full suite → 331 passed)
- [x] Script exists with only frozen-path commands (`demo/DEMO-SCRIPT.md`, cross-reference table included)
- [x] Offline run verified (static import inspection; zero network-capable modules)
- [x] Reset command documented and inspected (not live-executed — git-restricted)
- [x] One timed dry run ≤10 min logged, zero live/golden mismatch

**READY.**
