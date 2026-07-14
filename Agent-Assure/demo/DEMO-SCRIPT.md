# Agent-Assure Demo Script — the moat in under 10 minutes

**Message:** an AI draft with a fabricated citation cannot talk its way past
this gate, because no LLM judges grounding — the verdict is a mechanical fact
about the evidence store.

**Frozen path:** every command below is copy-pasteable, runs offline, and is
covered by `tests/test_demo_golden.py` (D1). If a command here ever drifts
from that test, the test fails in CI — this script does not improvise beyond
what D1 froze.

**Environment assumptions (fresh machine):**
- `uv` installed (`curl -LsSf https://astral.sh/uv/install.sh | sh`).
- Python >=3.11 (verified against 3.12.8 via `uv`-managed `.venv`).
- From a clean checkout: `bash install.sh` — provisions `.venv` via `uv sync`
  (installs `syntok`, `pyyaml` from `uv.lock`) and sanity-checks that the
  engine, capture hook, and deps import. No other setup is required; there is
  no build step (see `install.sh`, `pyproject.toml`).
- Run every command below from the `Agent-Assure/` directory.

**Break-glass fallback:** if live execution fails during a demo (env issue,
projector Wi-Fi flake, whatever), do not debug live — open
`demo/expected/full-transcript.txt` and walk that instead. It is the exact
byte-for-byte output of the commands below, captured 2026-07-08. The
per-command JSON/rendered goldens (`demo/expected/*-report.json`,
`demo/expected/*-rendered.txt`) back it and are what `test_demo_golden.py`
diffs against.

**Reset command (run between back-to-back demos, or before starting fresh):**
```bash
git checkout -- demo/ && rm -f grounding-report.yaml
```
This restores `demo/evidence-store.jsonl` and both drafts to their committed
state and removes any YAML report written by a non-`--json` run, so the next
run starts from the same clean state this script assumes.

---

## 1. Cold open (1 min)

Open `demo/draft-fabricated.md` and just read it out loud. It looks
impeccable — headline claim, two benchmark numbers, citations on every
sentence, nothing that reads as suspicious.

```bash
cat demo/draft-fabricated.md
```

Ask the room: **"Would you catch the fake in here?"** Let it sit for a beat.
There are two plants: a citation to a source that was never retrieved, and a
number no source supports. Don't reveal which yet.

## 2. The store (2 min)

Open the evidence store and show one record — this is what the capture hook
writes automatically, during research, before anyone drafts anything.

```bash
uv run python demo/build_store.py
cat demo/evidence-store.jsonl
```

Point at one line (`S1`, the Redis record) and read off the fields:
verbatim `text`, `content_sha256`, `url`/`fetched_at` provenance,
`query_provenance`, and `full_text_source: "verbatim"`.

Say the `haiku_summary` line: if a source had been captured through a
summarizing path (e.g. native `WebFetch`, which Claude Code passes through
Haiku), `full_text_source` would read `"haiku_summary"` instead of
`"verbatim"` — and the gate refuses to certify any claim against it
(`UNGROUNDABLE`, not GROUNDED), no matter how well the summary reads. The gate
does not trust text it can't trace to the original bytes.

## 3. The moment (2 min)

Run the check against the fabricated draft.

```bash
uv run python scripts/ground_check.py --draft demo/draft-fabricated.md --store demo/evidence-store.jsonl --json | uv run python demo/show_report.py
```

Expected output (frozen, `demo/expected/fabricated-rendered.txt`):

```
gate: FAIL | score: 50.0
  GROUNDED             <- # Datastore Throughput — Benchmark Summary
  GROUNDED             <- In our controlled benchmark on a single node, Redis sustained approxim
  GROUNDED             <- Under the same benchmark load and hardware, PostgreSQL sustained appro
  UNVERIFIED_CITATION  <- MongoDB sustained approximately 45000 operations per second in the sam
  UNVERIFIED_NUMBER    <- Redis delivered about 100 times the throughput of the disk-backed alte
```

Exit code `1`. Point at the fourth line: **`[S3]`** — a source ID that does
not exist in the store we just looked at. Point at the fifth: `100` is a
number no source contains (S1 says *twelve* times). Say the moat line:

> **"No LLM read this draft and decided it looked fabricated. `S3` is not in
> the store — that's it. That's the whole check. The draft cannot argue,
> rephrase, or talk its way around a source that was never retrieved."**

## 4. Contrast (1 min)

Same command, the clean draft — same two real claims, no plants.

```bash
uv run python scripts/ground_check.py --draft demo/draft-grounded.md --store demo/evidence-store.jsonl --json | uv run python demo/show_report.py
```

Expected output (frozen, `demo/expected/grounded-rendered.txt`):

```
gate: PASS | score: 100.0
  GROUNDED             <- # Datastore Throughput — Benchmark Summary
  GROUNDED             <- In our controlled benchmark on a single node, Redis sustained approxim
  GROUNDED             <- Under the same benchmark load and hardware, PostgreSQL sustained appro
```

Exit code `0`. Same engine, same store, same code path — the only variable
was whether the draft's claims trace to captured evidence.

## 5. Honesty beat (1 min)

Before anyone asks "how do you know your thresholds are right" — show them
you already asked it. Open `calibration/CR-001-bootstrap-lex-tau.md`.

```bash
cat calibration/CR-001-bootstrap-lex-tau.md
```

Say it straight:

**"The gate you just watched runs its lexical-match threshold (`lex_tau`) at
0.65 — the shipped default. A bootstrap calibration of n=12 claims across 12
queries recommends 0.71 instead; at THAT operating point, held out
leave-one-out, the false-alarm rate is 0.20 and the false-negative rate — a
fabrication slipping through — is 0.143. We have not deployed 0.71 yet,
because n=12 is a calibration run, not a production guarantee. A wider
ratified run supersedes it. So: those numbers describe the recommended
operating point, not the one on screen — and I'd rather tell you that than
quote you a number that sounds better than it is."**

This is the deliberate honesty beat: showing the calibration math — including
its limits — earns more trust than hiding it would.

## 6. Close (1 min)

> **"The evidence store isn't something you maintain — it builds itself. The
> capture hook fires on every retrieval tool call during research and appends
> to the store automatically; nobody has to remember to log a source.
> Roadmap is an NLI paraphrase tier (catching restated-not-quoted claims) and
> wider calibration data — no dates promised, just the direction."**

---

## Appendix: command → golden-test cross-reference

Every command above is asserted by `tests/test_demo_golden.py`:

| Script step | Command | Test |
|---|---|---|
| §2 | `uv run python demo/build_store.py` | `test_demo_store_builds_two_sources` |
| §3 | `ground_check.py --draft demo/draft-fabricated.md ...` | `test_fabricated_draft_gate_fail_with_unverified_citation` |
| §4 | `ground_check.py --draft demo/draft-grounded.md ...` | `test_grounded_draft_gate_pass` |
| §3 + §4 rendering | piped through `demo/show_report.py` | `test_rendered_report_matches_golden_transcript` |

Run `uv run pytest tests/test_demo_golden.py -v` before any live demo to
confirm the frozen path still holds.
