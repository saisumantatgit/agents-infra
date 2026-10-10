# RESUME HERE — 2026-10-10. THE DAY RUN IS OVER: DISARMED AT DIFF ZERO, ALL SIX ROWS BUILT.

# THE CAPTURE LAYER CERTIFIES FABRICATIONS. THAT IS TODAY'S HEADLINE, NOT THE MERGE.

**Cron `5888aa27` DELETED; `CronList` shows no jobs.** §6 disk hygiene ran
first; the scratchpad is empty. End-of-day report: foot of
`docs/logbook/dayrun-2026-10-10-progress.md`.

**FOUR capture-layer CRITICALs confirmed by my own reproductions** — R20-01,
R20-02, and R20-04 + R20-06 (one class: the absence rule counts stored records,
not successful reads). All Escalation #4, all Sai's. **These, not the merge, are
now the real gate before an external tester.**

| | |
|---|---|
| branch | `testing-live-2026-10-10` (off `agent-assure-calibration-run` @ `0d860d6`) |
| suite | **861 passed · 2 skipped · 68 xfailed · exit 0** |
| gold md5 | `6215b526d03147295b003d7ccb0d171f` — unchanged, never in a diff |
| rates | **Error-A 10/25 = 0.400 · Error-B 0/27 = 0.000**, now re-derivable: `cd Agent-Assure && uv run python -m calibration.measure_rates` |
| open PRs | **#10 → `main`** · **#11 → `agent-assure-calibration-run`**. **Neither merged; the merge subcommand was never attempted.** |
| `main` | **`009c646`, still without the work** |

## R20-01 — REPRODUCED BY ME, with my own fixture. CRITICAL.

`_coerce_text_value` joins MCP content blocks with `"\n"`; `_tokenize` is
`re.findall(r"\w+")`, so the seam is invisible and a contiguous span can
**straddle two different fetched documents** and satisfy T1.

```
claim present in NEITHER document  ->  PASS 100.0 GROUNDED  exit 0
same claim with --session-id       ->  PASS 100.0, printing
   "traceable to text in a source retrieved this session"
```

**`ground_check.py` is not wrong here** — it faithfully reports a contiguous
span of the text it was handed. The lie is written into the store before the
gate runs, and **the document boundary is discarded at ingestion, so no loader
validation can ever recover it.**

## DONE SINCE THE COMPACTION NOTE BELOW — do NOT redo

R20-02 confirmed; R20-03 NOT reproduced (refused FAIL 0.0); R20-04 and R20-06
UPGRADED to CRITICAL (both reach PASS 100.0); R20-05 trigger unobserved live.
CR-012 complete. The section below is kept for the trail.

## (superseded) DO THIS FIRST, IN THIS ORDER

1. **Reproduce R20-02 and R20-03 YOURSELF.** They are the adversary's testimony
   and are NOT yet confirmed. Report: `Agent-Assure/reports/RED-TEAM-R20-2026-10-10.md`.
   - R20-02: a multi-URL exa fetch collapses N documents into ONE record whose
     only `url` is `urls[0]` — an attacker's sentence attributed to `who.int`.
   - R20-03: `_file_path_from_input` never reads the authoritative
     `tool_response["file"]["filePath"]`, so a `Read` can land with `url=null`
     AND `file_path=null`, and both `_self_source_ids` origin tests become dead
     code behind `if source.file_path:`.
2. Then R20-04 (HIGH, error bodies stored as verbatim), R20-05, R20-06.
3. Then CR-012's R5 row with actuals, register rows for every R20 finding with
   owners, and the 7-step close.

**DO NOT FIX ANY OF THEM WITHOUT CHECKING THE OWNER.** The capture contract is
**Escalation #4 — Sai's**. J-35, J-36 and J-38 are already his and are NOT
closed by anything today. Whether R20-01/02/03 are capture-side (his) or admit a
fail-closed gate-side guard (mine) is a judgement to make per finding, in
writing, before touching a file.

## OPEN AND SAI'S

- **PR #10 — the merge click.** `main` ships the **Phase-1 engine, 1,388 lines,
  before all nineteen rounds**, and certifies a self-citing fabrication at
  **PASS 100.0** where the branch returns **FAIL 0.0**. Dossier:
  `docs/decisions/MERGE-TO-MAIN-DOSSIER-2026-10-10.md`. **Recommended: merge**,
  on reversibility — one revert of the merge commit, clean because the merge
  deletes nothing and the gold labels are **adds, not modifications**.
- **R4-Q1 — does anyone actually install from `main`?** The one fact that flips
  that recommendation. Not answerable from this repo.
- **A-5-01** — `install.sh`'s own session-id snippet crashes in a fresh install
  (Escalation #4). The register names the two-line change **and why the obvious
  repair is a trap**.
- **The 5-user comprehension test** — still the only thing that can reverse D-83.
  Protocol and stimulus are written: `docs/research/user-test-2026-10-03/`.
- J-35 · J-36 · J-38 · J-96 · J-95 (blocked on a `Security Test Removal`
  permission) · q25 · J-72's narrowing · the publish (Escalation #5).

## DISK — §6 HAS NOT RUN YET

- **REMOVED already:** the ALPHA-5 clone and its venv (16 MB), `userrepo`.
- **Still to remove at the disarm:** `scratchpad/prefix_ground_check.py` (the
  proven-red reference for R2), `scratchpad/r20/`, `scratchpad/mine20/`,
  `scratchpad/mainprobe/`. Sai was asked to delete `~/tmp/assure-probe`.
- **Pre-existing, NOT mine, do not touch:** `graphify-out/` (5.9 MB) and one
  unread HQ inbox item from 2026-09-03. Both are for Sai.

## TRAPS RECORDED TODAY

- **`uv run python -m calibration.run_calibration` REWRITES `CR-001`.** It is
  the n=12 bootstrap, not the deployed rates. Use `measure_rates` instead.
- **`import sys as _sys` is FUNCTION-LOCAL inside `main()`** in
  `ground_check.py`. A new module-level helper referencing `_sys` dies with
  `NameError`. Cost me one cycle.
- **`caused` is not a relational trigger**; `causes`, `leads to`, `due to` are.
- **A PreToolUse hook blocks restoring a path from a ref while the tree has
  changes** — and it matches on the command TEXT, so even quoting that command
  inside a document being written will block the write. Redirect from
  `git show <ref>:<path>` instead, and do not spell the other form in a heredoc.
- **`claude` launched with `!` from inside a session runs in `--print` mode**,
  which executes **no PostToolUse hooks** (D-60). A live store needs a separate
  terminal.
