# MERGE-TO-MAIN DOSSIER — the decision is not the one it looks like

**Written** 2026-10-10 (R4 of DAYRUN-2026-10-10) · **Decider: Sai.** Nothing in
this file was acted on. No merge was attempted and none will be.

## THE INVERSION, first, because it changes the question

The merge reads as *"ship 279 commits of unreviewed work onto a safe `main`."*
**It is the opposite.** `main` is `009c646`, it already ships Agent-Assure, and
it ships the **Phase-1 engine: 1,388 lines, before all nineteen red-team
rounds.** The branch's engine is 4,657 lines. Every Error-B closed since July —
the header-wrapped fabrication, the relational shapes, the citation-placement
class, the self-certifying draft — **is absent from `main`.**

**Demonstrated, not argued.** One draft, one store, two engines, run today:

```
draft: "The Zentara Q3 reconciliation identified seventeen material weaknesses
        across the Frankfurt custodial desk [S1]."
store: one record — the draft itself, captured as a Read (the J-83 shape)

main   (009c646, 1388 lines):  gate PASS  score 100.0  [GROUNDED]        exit 0
branch (90e129d, 4657 lines):  gate FAIL  score   0.0  [UNGROUNDABLE]    exit 1
```

**`main` certifies a fabrication that cites nothing but itself, at 100.0.**
Anyone installing from the default branch today gets that build. So the risk is
not symmetric between merging and not merging: **not merging leaves the
dangerous version as the reachable one.**

`main`'s README also still describes *"two-tier lexical grounding (T1 verbatim +
T2 lexical-F1)"*. **T2 was demoted by ADR-006** because a true and a false claim
can differ by one token and score an identical `t2_f1`, and because a bag of
words has no order — a false reordering scored 1.000. `main` documents a
mechanism the project has since ruled insufficient.

## WHAT THE MERGE ACTUALLY DOES

| | |
|---|---|
| commits | **279** |
| files | **275 changed, +50,511 / −422** |
| files DELETED from `main` | **zero** — `git diff --name-status` shows no `D` |
| gold labels | `labels-v2.csv` and `labeling-v2.csv` are **`A` (added)**, not `M`. `main` has never held them, so **this merge contains no gold-label CHANGE** — the standing Escalation #2 gate is not engaged by it |
| the moat | `Agent-Assure/scripts/ground_check.py` `M`, 1,388 → 4,657 lines |
| the rest | 82 test files, 44 Agent-Assure docs, 31 calibration, 25 logbook, 20 research, 17 plans, 9 red-team reports, 6 decisions |

**Verified green on the branch tip today:** suite **861 passed · 2 skipped · 68
xfailed · exit 0**; gold md5 `6215b526d03147295b003d7ccb0d171f`; Error-A
`10/25 = 0.400`, Error-B `0/27 = 0.000`, both re-derived with
`uv run python -m calibration.measure_rates` rather than quoted.

**Installability verified from a clean clone today** (ALPHA-5, R3): `install.sh`
exit 0 on a machine with no `.venv` and no `.assure`, demo fabrication refused
`FAIL 50.0 exit 1`. **So the branch is known-installable without `main` having
to be the experiment.**

## THE EXACT COMMANDS — yours, not mine

Open the PR (already done by this run — see below), then:

```
gh pr merge <N> --merge --repo saisumantatgit/agents-infra
```

**Revert, if the merge is wrong:**

```
git revert -m 1 <merge-commit-sha>        # one commit, restores main exactly
git push origin main
```

A merge commit's `-m 1` revert is a single clean commit because **the merge
deletes nothing** — there is no removed file to resurrect and no history to
rewrite. That is what makes this a two-way door despite its size.

## THE THREE THINGS I CANNOT MEASURE, STATED PLAINLY

1. **No human has read 50,511 lines**, and I am not going to pretend the suite
   substitutes for that. What the suite covers is behaviour; what it cannot
   cover is whether a doc among the 44 says something you would not say.
2. **The capture layer is still open.** J-35 (write-then-Read laundering), J-36
   (the absence ledger is attacker-written), J-38 (no store rotation) are
   demonstrated Error-Bs that this merge does **not** close — they are
   Escalation #4, in `capture_core.py`, and R5 reports on them today.
   **Merging improves `main` substantially and does not make it sound.**
3. **Whether `PASS` reads as *traceable* or as *supported*** is untested on a
   human. Only the 5-user comprehension test answers it, and it is yours.

## MY RECOMMENDATION

**Merge it** — on the asymmetry, not on the work's merits. Leaving `main` where
it is keeps the build that certifies a self-citing fabrication at 100.0 as the
one a stranger reaches by default, and the recoverable cost of a wrong merge is
one `git revert -m 1`. Merging is reversible in one command; **the fabrication
`main` certifies today is not.**

**What would flip it:** if `main` is not actually the branch anyone installs
from — if every real user comes via `agent-assure-calibration-run` or a local
path — then the inversion above collapses, `main` is decorative, and the merge
can wait for a human read of the 44 docs. **I do not know which is true, and it
is a fact about your distribution, not about this repo.** That is the one
question whose answer changes my recommendation.
