# Agent-Assure Demo — the moat in 30 seconds

This offline demo shows the one thing Agent-Assure exists to do: **catch a
fabricated citation mechanically**, with no LLM judging grounding.

## Run it

```bash
# from the Agent-Assure directory, after `bash install.sh`
.venv/bin/python demo/build_store.py            # simulate the capture hook
.venv/bin/python scripts/ground_check.py --draft demo/draft-grounded.md   --store demo/evidence-store.jsonl
.venv/bin/python scripts/ground_check.py --draft demo/draft-fabricated.md --store demo/evidence-store.jsonl
```

`build_store.py` runs two simulated retrieval tool calls through the real
capture core — exactly what the `PostToolUse` hook does automatically during a
live research session — producing `demo/evidence-store.jsonl` (sources S1, S2).

## What you'll see

### `draft-grounded.md` — every claim traces to a captured source

```
gate: PASS | score: 100.0
  GROUNDED  <- In our controlled benchmark on a single node, Redis sustained approximately 128000 operations per second [S1].
  GROUNDED  <- Under the same benchmark load and hardware, PostgreSQL sustained approximately 11000 write operations per second [S2].
```
Exit code `0`.

### `draft-fabricated.md` — two planted fabrications, both caught

Same two real claims, plus:
- a citation to **[S3]** — a source that was never retrieved;
- a claim that Redis was **"100 times"** faster — a number no source contains
  (S1 says *twelve* times).

```
gate: FAIL | score: 50.0
  GROUNDED             <- ...Redis sustained approximately 128000 operations per second [S1].
  GROUNDED             <- ...PostgreSQL sustained approximately 11000 write operations per second [S2].
  UNVERIFIED_CITATION  <- MongoDB sustained approximately 45000 operations per second in the same test [S3].
  UNVERIFIED_NUMBER    <- Redis delivered about 100 times the throughput of the disk-backed alternative [S1].
```
Exit code `1`. `[S3]` is not in the store → `UNVERIFIED_CITATION` (the
fabricated-citation catch). `100` matches no source number → `UNVERIFIED_NUMBER`.

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
