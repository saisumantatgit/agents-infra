# RESUME HERE — written 2026-10-04 00:0x, after a 59-commit day

# BOTH PRs ARE MERGED AND THE TWO CRITICALS ARE CLOSED. ZERO OPEN PRs.

Verified on the merged tip, not inherited from a branch's green run — a merge can
produce a tree neither parent had:

| | |
|---|---|
| integration branch | `agent-assure-calibration-run` at **`b442865`** |
| suite | **851 passed · 2 skipped · 68 xfailed · exit 0** |
| gold md5 | `6215b526d03147295b003d7ccb0d171f` |
| corpus md5 | `affd3f9f703b15612d69e4cc0deb5010` |
| Error-A / Error-B | **0.400 / 0.000** |
| open PRs | **0** |
| `main` | **`009c646`, UNTOUCHED** |

**PR #9** (`862d994`) then **PR #8** (`b442865`), in that order, by Sai's own
hand — `gh pr merge` was denied `[Merge Without Review]` three times and was
never worked around. **I first told him the opposite order**; #9's base IS #8's
head, so #8-first would have orphaned #9's two commits behind a third PR. The
correction is in PR #8's body too, so the record does not preserve the mistake.

**`main` HAS STILL NEVER RECEIVED THE CALIBRATION WORK.** It is `009c646`, and
PR #7's merge commit is not an ancestor of it. That is a separate, much larger
decision — 260 commits, 280 files, the gold labels among them. **Nothing said so
far authorises it.**

## WHAT CLOSED, AND THE PART WORTH READING

**J-84 + J-85 are ONE hole, not two, and needed no signature change.** Both
register rows said `check_absence` had to separate COUNT from DENOMINATOR. True
of **J-42** — a `haiku_summary` IS a real search, so it must leave the numerator
and STAY in the denominator — and **false here**: a self-`Read` is not a search
in any role, so it leaves one population and the D-54 direction trap cannot
arise. Fix is one call site plus one parameter; `check_absence` is untouched.

**J-84 was not reproducible as written.** Its shape refuses today — on the
blanket-word gate (`len=3, head_in=2, 4>3`), not on anything about self-sources.
It refused for the **wrong reason**. J-85's padding silences that gate and
exposes the count.

**The guards caught me three times mid-change**, which is the whole argument for
them: `evidence_basis` left reading the whole store while the verdict read the
filtered one (**round 11-B recreated**); the "only one query source exists"
sibling rejecting my better-named helper; and a positive control whose premise
embedded the bug — it certified on ONE genuine search because the self-record
supplied the second.

## OPEN AND SAI'S

- **J-96** (Escalation #1) — the blanket-word test is a **proportion**, so real
  irrelevant searches can still dilute the denominator until a live refusal goes
  silent. Replacing it trades Error-A against Error-B.
- **J-95** — the tripwire pinning D-91. **Blocked on clearing the
  `Security Test Removal` permission**; its proven-red check means running the
  guard against a build with the digest arm disabled, and a guard never seen red
  is not a guard.
- **The 5-user comprehension test** — still the only thing that can reverse D-83.
- **The capture contract J-35/J-36/J-38** — genuinely unruled, unlike J-70.
- J-69 · J-72's narrowing · q25 · the publish (D-83 approved, Escalation #5
  reserves the act).

**J-70 IS RULED** (D-83: open as an upgrade path, NOT scheduled). **J-93 and
J-94 are CLOSED** (D-90, D-91). Do not put any of the three back to him.

## OPEN AND MINE

J-42 · J-50 · J-72 display residue · J-76 · J-81 · the matched-pair runner
(ruling 3) · bin × outcome counts (ruling 2's constructive half).

**Merged branches left in place, not deleted:** `delivery-queue-2026-10-02` and
`j84-j85-absence-denominator-2026-10-03`. Both are fully contained in
`b442865`; deleting them is Sai's call, not mine.

---

## THE NIGHT'S RECORD (superseded by the above, kept for the trail)


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

**J-94 IS RULED: CLOSED WONTFIX (Sai, 2026-10-03, D-91).** The refusal needs the
whole draft to equal the whole source — a transcription with no independent
content. J-93 closed by refusal (D-90); my own remedy withdrawn as fail-open
(D-92). **Do not reopen on a single-sentence fixture** — the digest is
whole-draft against whole-source, so such a fixture tests the fixture.

**J-95 is the open residue and it is MINE:** a tripwire pinning D-91, because a
deliberate refusal that looks like a bug will be "fixed" in good faith by the
next reader, and that fix is the one that reverts R19-01. **It cannot be
completed without clearing the `Security Test Removal` permission** — the
proven-red check requires running the guard against a build with the digest arm
disabled, and a guard never seen red is not a guard.

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
