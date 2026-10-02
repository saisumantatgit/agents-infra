# OVERNIGHT INSTRUMENT — 2026-10-02 → 2026-10-03

**This file holds HOW TO DERIVE the work each cycle. It holds no list of answers.**
A wrong fact baked into the tick executes every tick; a wrong fact here is
correctable between ticks. If this file and the tick text disagree, this file wins.

**GOAL (business terms):** tomorrow Sai can merge PR #7 and launch Agent-Assure
knowing an adversary has attacked the code that will actually ship — not an
implementation that was withdrawn hours before.

---

## §1 THE DIFF RULE — recompute every cycle, never quote last cycle's number

A row is IN THE DIFF unless it is one of:

- **BUILT** — gated green, committed by explicit path, PR open at the claimed HEAD.
- **OWNED BY A NAMED HUMAN** — `owner: Sai` in `docs/jobs/REGISTER.md` **with the
  blocking reason stated**. An owner with no reason is still in the diff.

Derivation order, every cycle, in this order — **code, then register, then any
scoreboard**:

1. **CODE.** `grep -n "ClaimKind.RELATIONAL" Agent-Assure/scripts/ground_check.py`
   — the live branch is the fact. Registers describe it; they do not define it.
2. **REGISTER.** `grep -nE "^\| J-[0-9]+" docs/jobs/REGISTER.md` — read the OWNER
   column. Rows owned by Sai are NOT in tonight's diff.
3. **SCOREBOARD LAST.** `uv run pytest -q` and the CR tables are confirmations,
   not sources. A green suite is not evidence that a hole is closed; it is
   evidence that no test represents it.

**Tonight's candidate set is derived, not fixed.** As of §0 the Claude-owned,
unblocked rows were J-68, J-62, J-67, J-37 (builder half), J-45, J-42.
That enumeration is a SNAPSHOT for the handshake and must be re-derived, not reused.

## §2 GATES — the commit is downstream of the tests

```
cd Agent-Assure && uv run pytest -q > /tmp/suite.txt 2>&1; echo $?
```

Chain with `&&`; never `cmd | tail; echo $?` (that reports the pipe).
Baseline at §0, from a fresh run: **793 passed · 2 skipped · 61 xfailed · exit 0.**

Two further gates, both mandatory before any commit that touches `ground_check.py`:

- **GOLD UNTOUCHED.** `md5 -q Agent-Assure/calibration/labels-v2.csv` must stay
  `6215b526d03147295b003d7ccb0d171f`. A changed gold md5 is a HALT, not a finding.
- **CORPUS REGENERATED AND DIFFED.** Any `classify`/tier/`ground` change regenerates
  the corpus and byte-diffs it; every drifted row is adjudicated against its LABEL.
  **Never tune a constant to make one row pass.**

**A zero corpus delta is NON-MEASUREMENT, not safety** — no corpus row carries a
long subject phrase, an HTML comment, a spelled count in an absence claim, or a
session id. Say "unmeasured", never "unaffected".

## §3 EACH TICK

1. **Duplicate check.** `ps aux | grep -c "[c]laude"` and `git worktree list`.
   If a second orchestrator is live on this branch, one stands down — this one,
   unless it holds uncommitted work.
2. **Re-derive state** per §1. Recompute the diff count from scratch.
3. **Append to** `docs/logbook/overnight-2026-10-02-progress.md`:
   UTC · diff count · what changed · new tokens (output + cache creation) · frameworks applied.
4. **Pick the next row** by §4 priority. Brief the executor, review the result,
   **run the gates first-hand**, commit by explicit path, push the branch, update PR #7.
   Subagent reports are TESTIMONY; the diff and a fresh test run are EVIDENCE.
   Nothing is committed unseen. Briefs say: *"if the spec conflicts with the repo,
   STOP and say where."*
5. **CIRCUIT BREAKER.** Two consecutive cycles with an unchanged diff and no
   in-flight growth ⇒ HALT, name the blocking class, disarm. Same for two
   consecutive failures of the same terminal error class — `[Request interrupted
   by user]` and `API Error: … went to sleep` are ONE class (environment-terminated),
   and retrying an environment failure without changing the environment is a loop.
6. **DISARM in the same turn** at: diff zero · breaker · hard stop · budget ceiling.

## §4 PRIORITY — derived from the critical path, not from ease

**Round 14 (J-68) is the upstream node.** PR #7 cannot merge without it, and if it
finds an Error-B in the flat refusal, every row below changes. Nothing else starts
until round 14's findings are reproduced **by me, from the adversary's exact fixture**
— the round-13 lesson: my first repro attempt failed and the finding was real.

Then, in order, re-derived each cycle:
1. **J-68** round 14 against the flat refusal + kind-independent figure checks.
2. **J-62** the absence branch's spelled-figure hole (same guard, different branch).
3. **J-67** T1's span+coverage rule and the hedge check that did not fire — FACTUAL,
   and **invisible to the corpus by construction**.
4. **J-37 builder half** — the corpus bypasses `load_store`, so the mandatory corpus
   adversary cannot detect a loader change, and tonight's numbers are measured on
   stores the shipped gate would REJECT. Cheap, and it makes every other number mean
   something. (Whether CR-005 must be re-derived is **Sai's**, not mine.)
5. **J-45** `evidence_basis` announces queries the verdict ignored (D-35 class).
6. **J-42** the absence counting query — **two directions in one function**; this is
   the row that already cost one self-inflicted Error-B. If budget is below 40%, do
   not start it.

## §5 THE EXECUTOR LADDER

| Work | Model | Why |
|---|---|---|
| Round 14 adversary (whole-moat, last gate) | **Opus** | A miss here ships. This gate never downgrades. |
| Reproducing every finding, adjudicating, writing the fix | **me (Opus main loop)** | Post-refutation adjudication; moat-integrity math. |
| J-62 / J-45 implementation against a locked spec | **Sonnet 5** | Well-specified mechanical diff; my review + the suite backstop it. |
| Register/CR/doc drafting from fixed evidence | **Sonnet 5** | Judgment lives in the evidence, not the prose. |
| Evidence-gathering with fully specified commands | **Haiku 4.5** | Zero judgment. |

Route per agent, never per fan-out. `model:` is set EXPLICITLY on every dispatch —
omitting it silently inherits Opus.

## §6 WHAT I MAY NOT DO (the park list, pre-ruled)

Never push to `main` · never merge (PR #7 included — **it is explicitly DO-NOT-MERGE
until round 14 is reported**) · no `git add -A` · no gold-label change · no q25 ·
no `install.sh` edit · no writes to `~/.claude` or the global plugin registry ·
nothing outward-facing · no T3/NLI tier · no J-55/CI mode · **no change that could
move a claim TOWARD pass** (Escalation #1 — fail-closed is mine, PASS-enabling is Sai's).

**COST OF DELAY vs COST OF ERROR INVERTS AT NIGHT.** Unverifiable FACT ⇒ stop and
record. Undecided DESIGN ⇒ decide. The second is not a licence for the first.
