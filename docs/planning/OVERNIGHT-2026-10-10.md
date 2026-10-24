# OVERNIGHT-2026-10-10 — the instrument

**Goal (business terms):** by morning, an AI agent using Agent-Assure can no
longer get a fabricated claim certified PASS by any of the four routes round 20
proved — two documents glued at a seam, several pages credited to the first
address, failed fetches counted as searches, blank fetches counted as searches —
and each closure has itself been attacked before it reaches a PR.

**This file holds HOW TO DERIVE the work, never the answers.**

## §0 STATE, DERIVED FROM CODE at 2026-10-10 ~22:00 IST

| | |
|---|---|
| `main` | `a382aa0` — PR #10 merged by Sai 21:46. Tree `4a189d5` |
| working branch | `capture-contract-2026-10-10`, off `7063903` (= `main`'s tree + the RESUME-HERE correction). `a382aa0` is not an ancestor, but its tree equals `e2f13f2`'s, so a PR to `main` merges clean |
| suite | **861 passed · 2 skipped · 68 xfailed · exit 0** (run on `main`'s exact tree) |
| gold md5 | `6215b526d03147295b003d7ccb0d171f` |
| rates | `cd Agent-Assure && uv run python -m calibration.measure_rates` → **0.400 / 0.000** |
| `isError` | **read nowhere** in `capture_core.py` — grep, 0 hits (confirms R20-04's mechanism) |
| block join | `capture_core.py:125` `"\n".join(parts)` (R20-01) |
| url pick | `capture_core.py:192-193` `urls[0]` (R20-02) |

Derivation order each cycle: **CODE → REGISTER → SCOREBOARD.** Register rows
were stale five times in three days; re-derive a mechanism before acting on it.

## §1 THE DIFF RULE

A row is OPEN unless (a) BUILT — gated green, committed by explicit path, pushed,
PR open — or (b) OWNED BY A NAMED HUMAN with the blocker stated. Recompute each
cycle; never quote the last number.

## §2 GATES — the commit is downstream of the tests

```
cd Agent-Assure && uv run pytest -q > /tmp/suite.txt 2>&1; echo $?
```
- **GOLD** md5 unchanged, or HALT.
- **RATES** via `measure_rates`. **Every change tonight is FAIL-CLOSED by
  construction** — it may only move a claim AWAY from PASS. So Error-B must not
  move and its denominator must not shrink; **Error-A may rise and the rise is a
  PRICE to report, not a failure.** A change that LOWERS Error-A tonight is
  suspect by definition and gets reverted until explained.
- **THREE INSTRUMENTS.** Gold corpus = LABEL. `tests/honest_drafts/` = USAGE.
  An adversary = HOSTILITY. **Sai's live store** (`~/tmp/assure-probe/.assure/`)
  = the only REAL field shape — read its fields, never its text into the repo.
  **For Error-B the instrument is an adversary, never a corpus**: the corpus has
  no multi-block, multi-URL or failed-fetch record, so a zero corpus delta is
  non-measurement.
- **PROVEN-RED** for every fix: the round-20 reproduction becomes the test, and
  it is seen to FAIL against the pre-fix code before the fix lands.
- **NAME THE SIBLING** in every commit: the other tool (DDG returns a plain
  `str` — its error strings have no `isError`), the other branch, the null case.

## §3 EACH TICK

1. Duplicate orchestrator? One stands down.
2. Re-derive; recompute the §1 diff.
3. Append to `docs/logbook/overnight-2026-10-10-progress.md`: UTC · diff ·
   what changed · new tokens (output + cache creation) · frameworks.
4. Next row: build or brief, review, run §2 first-hand, commit by explicit path,
   push, PR. Briefs say: *if the spec conflicts with the repo, STOP and say where.*
5. **CIRCUIT BREAKER**: two cycles, unchanged diff, nothing in flight ⇒ HALT,
   name the class, disarm. Same for two failures of one terminal class.
6. **DISARM in the same turn** at diff zero · breaker · hard stop · ceiling —
   **§6 disk hygiene FIRST.**

## §4 EXECUTOR LADDER

| Work | Who | Why |
|---|---|---|
| The capture fixes C1–C3 | **me, main loop** | cross-boundary: the defect lives in the seam between capture and gate, and no single file holds it |
| Round 21 against C1–C3 | **Opus subagent**, fresh context | last gate before a PR; a miss is an Error-B that ships |
| Reproducing every R21 finding | **me** | its report is testimony; round 20 showed severity moves both ways under reproduction |
| Test migration, census, doc sweeps | Sonnet subagent | recoverable; I verify the diff |

## §5 PARK LIST — Sai has ruled; honouring it is obeying

Merging (any PR) · `install.sh` (so A-5-01 stays his) · hook REGISTRATION
(`hooks/hooks.json`) · `SOUL.md` · any gold-label change · q25 · T3/NLI ·
J-55/CI · the publish · anything outward. **J-35, J-36, J-38 are NOT in tonight's
scope** — each needs a product decision, not a fail-closed patch.

## §6 DISK — before the disarm, same turn

Delete every scratch tree, fixture store, venv or clone created tonight and name
each `REMOVED` in the progress file. Nothing over ~20 MB is generated locally;
anything that would be goes to Drive with a pointer row. **`~/tmp/assure-probe`
is Sai's and is KEPT** — the only real store. `graphify-out/` is pre-existing and
not mine (now gitignored by `main`).

## §7 FRAMEWORKS

First principles · Inversion · Via negativa · Chesterton's Fence · Goodhart ·
FMEA detectability · Theory of Constraints · Jobs to be Done · Asymmetry of error
cost · Reversibility · Contradiction-as-locator · Name the CEILING · Critical path
· Close-after-open · Reachability · Delivery-is-not-consumption · Calibration ·
Competence boundary · Degradation under constraint · Sunk cost.

**Competence boundary, named before the night:** I fix the fixture rather than
the class. Round 20's own lesson is that R20-04 and R20-06 are ONE hole; patching
`isError` and whitespace separately would close two fixtures and leave captcha
pages, login walls and DDG error strings open.

## §8 SAI'S STANDING END-OF-RUN ASK

The 5-user comprehension test — who the five are and what to ask them for —
appears in the morning report whether or not tonight touched it.
