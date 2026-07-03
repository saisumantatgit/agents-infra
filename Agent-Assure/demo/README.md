# Agent-Assure Demo — the moat in 30 seconds

This offline demo shows the one thing Agent-Assure exists to do: **catch a
fabricated citation mechanically**, with no LLM judging grounding.

## Run it

```bash
# from the Agent-Assure directory, after `bash install.sh`
.venv/bin/python demo/build_store.py            # simulate the capture hook
.venv/bin/python scripts/ground_check.py --draft demo/draft-grounded.md   --store demo/evidence-store.jsonl --json | .venv/bin/python demo/show_report.py
.venv/bin/python scripts/ground_check.py --draft demo/draft-fabricated.md --store demo/evidence-store.jsonl --json | .venv/bin/python demo/show_report.py
```

`build_store.py` runs two simulated retrieval tool calls through the real
capture core — exactly what the `PostToolUse` hook does automatically during a
live research session — producing `demo/evidence-store.jsonl` (sources S1, S2).
`ground_check.py --json` emits the full JSON report; `demo/show_report.py` renders
the per-claim verdicts shown below and mirrors the exit code (0 = PASS, 1 = else).
(Without `--json` the engine prints a one-line `gate=… grounding_score=…` summary
and writes the per-claim breakdown to `grounding-report.yaml`.)

## What you'll see

### `draft-grounded.md` — every claim traces to a captured source

```
gate: PASS | score: 100.0
  GROUNDED             <- # Datastore Throughput — Benchmark Summary
  GROUNDED             <- In our controlled benchmark on a single node, Redis sustained approxim
  GROUNDED             <- Under the same benchmark load and hardware, PostgreSQL sustained appro
```
Exit code `0`. (The first line is a markdown header — a `NON_CLAIM`, reported for
transparency but excluded from the score; per-claim text is truncated to 70 chars.)

### `draft-fabricated.md` — two planted fabrications, both caught

Same two real claims, plus:
- a citation to **[S3]** — a source that was never retrieved;
- a claim that Redis was **"100 times"** faster — a number no source contains
  (S1 says *twelve* times).

```
gate: FAIL | score: 50.0
  GROUNDED             <- # Datastore Throughput — Benchmark Summary
  GROUNDED             <- In our controlled benchmark on a single node, Redis sustained approxim
  GROUNDED             <- Under the same benchmark load and hardware, PostgreSQL sustained appro
  UNVERIFIED_CITATION  <- MongoDB sustained approximately 45000 operations per second in the sam
  UNVERIFIED_NUMBER    <- Redis delivered about 100 times the throughput of the disk-backed alte
```
Exit code `1`. `[S3]` is not in the store → `UNVERIFIED_CITATION` (the
fabricated-citation catch). `100` matches no source number → `UNVERIFIED_NUMBER`.
(Score 50 < 60 → the gate is `FAIL`; the `UNVERIFIED_CITATION` alone would cap it
at `NEEDS_WORK`, but `FAIL` is checked first — see the gate table in the README.)

Neither verdict came from a model reading the text. They are facts about the
evidence store, computed deterministically — which is why the fabricated draft
cannot argue its way to a pass.

## Citation convention (important)

Place the citation **inside** the sentence, before the final period:

- ✅ `... 128000 operations per second [S1].`
- ❌ `... 128000 operations per second. [S1]`

A citation placed after the sentence-final period is parsed as its own segment
and detaches from the claim it supports (the claim then reads as `UNCITED`).
This is fail-safe — it over-flags, never under-flags, so no fabrication slips
through — but it produces confusing false alarms on drafts that cite after
periods. Cross-sentence-boundary citation attachment is a tracked Phase-2
robustness item.
