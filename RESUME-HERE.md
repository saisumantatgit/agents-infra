# RESUME HERE — written 2026-10-03 22:0x, after a 57-commit day

# THE OVERNIGHT RUN DID NOT HAPPEN. The cron was never armed.

Sai approved it and went to bed; I said "arming now" and **never made the call**.
`CronList` at close: *No scheduled jobs.* The plan survives at
`docs/planning/OVERNIGHT-2026-10-03C.md` and is still the right plan — **it has
simply not been executed.** Start there, or re-arm it.

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
