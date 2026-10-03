# RESUME HERE — written 2026-10-03 22:0x, after a 57-commit day

# THE OVERNIGHT RUN WAS ARMED, RAN ONE ROW, AND DISARMED ITSELF. SAI'S CALL NEXT.

Armed at 22:11 (job `bb24422b`, verified by `CronList` after the create — the
21:44 "arming now" had never been called, which the close caught). **Disarmed at
22:16 by the circuit breaker, §6 hygiene first. `CronList`: No scheduled jobs.**

**Row 1, J-93, was HALTED and NOT executed.** The ruling said drop the
content-digest arm of `_self_source_ids`. `samefile` catches a hardlink and an
APFS case variant, `resolve()` catches a symlink — **none catches a plain COPY
of the draft**, and R19-01 was that copy certifying itself at PASS 100.0. The
digest is the only arm that sees it, so dropping it reverts R19-01 and re-opens
a demonstrated Error-B. Escalation #1. `scripts/ground_check.py` is
byte-unchanged.

**The Error-A behind the ruling is real** — an honest draft quoting its source
in full gets its own source excluded. Open as **J-94**, owner Sai, with the
fail-closed shape that separates the cases (narrow the digest arm by the
existing BASIS rule rather than deleting it).

**Why the whole run stopped and not just the row:** two harness denials of one
class (`Security Test Removal`, then `Security Weaken` on a read-only grep).
Tonight's entire priority list — J-93, J-84/J-85, the matched-pair runner — is
moat-internal work in that one file, so a tick would have hit the same wall
every 30 minutes. Neither denial was worked around or routed elsewhere.

**J-84 and J-85 remain the first real item** and are untouched: both CRITICAL,
both fail-open in both directions, in `check_absence`. They are *strengthening*
changes, so they are not what the denials were about — but they were not
attempted tonight, and that is a fact, not a hedge.

Full account: `docs/logbook/overnight-2026-10-03C-progress.md`.

## PR #8 IS OPEN AND WAITING ON SAI'S MERGE CLICK

https://github.com/saisumantatgit/agents-infra/pull/8 — 50 commits, 35 files,
`ground_check.py` +352. Base `agent-assure-calibration-run`, as every PR in this
repo has been. **848 green, gold md5 unchanged and not in the diff, clean merge.**
`gh pr merge` was denied `[Merge Without Review]` — correctly: the standing order
says *never merge, PRs only*.

**`main` has NEVER received the calibration work.** It sits at `009c646`, and
PR #7's merge commit `c524145` is not an ancestor of it. That is a separate and
much larger decision than anything taken today — do not treat "merge" as
covering it.

**J-94 recommendation: WONTFIX.** The refusal needs the whole draft to equal the
whole source — a transcription with no independent content. The first remedy I
registered for it was fail-open and is withdrawn.

**Read first:** `docs/logbook/2026-10-03D-the-author-as-adversary.md`.

## State, measured at close

```
suite    848 passed · 2 skipped · 68 xfailed · exit 0
Error-A  10/25 = 0.400     Error-B  0/27 = 0.000     (UNMOVED all day)
gold md5 6215b526d03147295b003d7ccb0d171f   untouched, zero labels changed
main     009c646 untouched · PR #7 MERGED at c524145 · 0 open PRs · tree clean
```

## THE TWO CRITICALS WAITING — start here

**J-84** — the absence BASIS rule is a tripwire, not a grounding requirement: two
self-`Read`s of the draft supply BOTH qualifying queries while **one wholly
irrelevant real source (a rainfall report)** satisfies the basis → **PASS 100.0**.
**J-85** — **GROWING the query list is fail-open**, where D-54 recorded only
SHRINKING: the draft's own `query_provenance` dilutes the blanket-corpus-word
DENOMINATOR and switches a live refusal off. Works with genuine irrelevant
sources too, so it is not only a self-citation bug.

Both need `check_absence` to separate queries that may **COUNT** from queries
that may form the **DENOMINATOR** — the signature change J-42 has needed since
2026-10-01. **This is the function that produced D-54, a self-inflicted Error-B
withdrawn the same day it landed, and BOTH directions are fail-open.**

**Sequence it as the instrument says: build the guard FIRST, run it against the
CURRENT hole, and if it does not go RED, stop and register rather than proceed.**

## SAI'S — and one of these is not an engineering task

1. **The 5-user comprehension test.** `docs/research/user-test-2026-10-03/` —
   `SHOW-THIS.html` is the whole instrument; users install nothing. **It is the
   only thing that can reverse D-83's release approval.** Thresholds are written
   down in `PROTOCOL.md` BEFORE the interviews, on purpose.
2. **The capture contract — J-35, J-36, J-38. GENUINELY UNRULED**, as distinct
   from everything else on his list. Every remedy is `install.sh` or hook
   registration (Escalation #4). J-35 was demonstrated LIVE and unprompted by
   his own J-54 session.
3. **J-69** (the causal lexicon — recommendation: do NOT fix it there, wrong
   layer) · **J-72's narrowing** (PASS-enabling) · **q25** · **the publish**
   (D-83 approved; Escalation #5 reserves the act).

**DO NOT PUT J-70 BACK TO HIM AS AN OPEN DECISION.** D-83 ruled it: *open as the
upgrade path, NOT scheduled.* I told him otherwise tonight and was wrong.

## TRAPS FROM THIS DAY — the expensive ones

- **A GUARD THAT HAS NEVER BEEN SEEN RED IS NOT A GUARD.** The cross-kind
  self-citation guard stayed GREEN against the very bug it was written for: its
  fixtures made every record the draft, so the BASIS rule refused first and the
  figure returns never executed. **Run every guard against a gate you know is
  broken before trusting it.**
- **`ground()` has 15 returns across 6 kinds; a check at one protects one.**
  Four instances of that in two days. Fixing one is not fixing the class.
- **Narrow the BASIS, never the scan, on the absence path.** D-54: shrinking the
  store moves `source_texts` and the query count in OPPOSITE directions, both
  fail-open. R18-03: GROWING it is fail-open too, through the same gate.
- **Path identity is a FACT; content identity is an INFERENCE.** Three different
  things share one content signature — the draft copied elsewhere, a fabricated
  notes file, an honest source quoted in full.
- **Gate the claim on the measurement IN THE SAME COMMAND.** `test N -le 80 &&
  git add` works; care does not. Nine withdrawals today, most of them a state
  asserted without being read.
- **A fixture that refuses for the WRONG reason proves nothing.** State which
  rule produced every refusal you report.

## CROSS-REPO — live, and not stale

HQ (`claude-0f`) has `docs/specs/matched-pair-probe-shapes.md` on branch
`agent-assure-design`: ten shapes, **shape 5 is a positive control** (direction
reversal is an identical multiset, so a bag-of-words feature MUST score ~0.5 —
anything else means the harness is wrong). **The split Sai ratified:** HQ
designs, Sai ratifies the labels (Escalation #2), this repo runs candidates and
reports as predicted-bin × outcome counts. **The runner is unbuilt and needs no
labels to build.**
