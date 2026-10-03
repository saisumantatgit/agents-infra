# 2026-10-03B — Four censuses, and the shapes they could not see

**Session:** `d2b27b1f` · branch `delivery-queue-2026-10-02` · afternoon, after D-80's day run
**Suite:** 822 passed · 2 skipped · 66 xfailed · exit 0 · no SyntaxWarnings
**Error-A 0.400 · Error-B 0.000 · gold md5 `6215b526…d171f` untouched · `main` at `009c646`**

## What

PR #7 merged (49 commits). Sai ruled on the open decisions. J-62+J-71 landed in
the verdict path under his GO, and immediately started masking other findings.
J-80 was swept, corrected twice, and closed. J-81 was discovered, and its reach
took three attempts to measure. Round 16 was dispatched against the verdict-path
change because nothing moat-adjacent ships unreviewed.

## Done

- **PR #7 MERGED** at `c524145` into `agent-assure-calibration-run`. `main`
  untouched. Suite re-run **at the merge commit**, not just at the branch head.
- **My "DO NOT MERGE" was over-broad and I said so in the PR body.** It was an
  argument against *shipping*; that PR targets the Phase-2 working branch and
  ships nothing. Leaving it unmerged made four red-team rounds and two ADRs
  reachable only by knowing a branch name.
- **D-83** release APPROVED on the current disclosure · **D-84** J-66 ruled, the
  hard cap stands · **D-85** J-78 blocked on a live session · **D-86** q25 and
  J-54 cannot be delegated by a GO.
- **J-62+J-71 CLOSED.** `4200` in no source: PASS 100.0 → `UNVERIFIED_NUMBER`.
  Error-A and Error-B unmoved.
- **J-80 CLOSED**, **J-81 / J-72 / J-31 opened or re-specified**, the 5-user
  comprehension instrument written, the J-51 patch handed over.

## Decisions

| id | Decision | Why |
|---|---|---|
| — | Merge PR #7 | Working branch, not `main`. Reachability beat caution. |
| — | J-31's old tripwire **kept and annotated**, not deleted | Its xfail is the historical record of how the finding was first reported. Close-after-open. |
| — | J-81's capture-test ids left alone | Those tests exercise the hook, not citation resolution. Each needs a judgement, not a sweep. |
| — | Round 16 dispatched before any release | J-62+J-71 is the only verdict-path change of the day. |

## Withdrawals and errors

- **A commit on a red gate** whose message stated a false result (`3ba4216` →
  `49d1bfa`). Cause: I searched for a top-level report key set, not a per-claim
  one — one KIND of search where three are required.
- **Forward-estimated timestamps** written into the progress file as if read.
- **"no caffeinate process"** asserted while three were running (they were other
  sessions', so the substance held and the sentence did not).
- **A SyntaxWarning** pasted into a docstring by my own annotation, found by
  `pytest -W error::SyntaxWarning` rather than by reading it.
- **J-80's census, wrong twice.** Then **J-81's census, wrong twice more.**

## Reflection

**Every instrument I built today under-reported, and each one under-reported in
exactly the way its own construction required.** The J-80 census matched literal
dict keys in a test body, so tests whose assertion lives in a helper looked
weak: 10 instead of 2. Its correction followed helpers but omitted `per_claim`
from the keyword list, so it still misjudged one file. The J-81 census matched
`source_id=`, so a dict literal was invisible; allowing quotes still missed
`_rec("SA1", ...)`, where the id is positional. Four instruments, four
under-reports, one shape.

What is worth keeping is not "be more careful with regexes". It is that **an
instrument's output never contains the list of shapes it cannot represent.** The
corpus could not say it had no 8-token subject phrases. `_span_is_hedged` could
not say it had no sentence boundaries. A `gate != "PASS"` assertion could not
say it was satisfiable by an unrelated refusal. And a regex over `source_id=`
could not say the ids were passed positionally. In every case the gap was
invisible *in the result* and obvious *in the construction* — which is why the
only thing that caught any of them was a **positive control**: assert the
instrument can see a case you already know exists, before trusting what it says
is absent.

That is the same rule the project already writes as "an empty result is
NOT_LOCATED_UNDER(params), never ABSENT". Today was the day I learned it applies
to the instruments I write to check my own work, and not only to greps for
someone else's code.

The second thing: **J-62+J-71 masked four findings within an hour of landing** —
J-33, J-31, J-42 and the r9 control — and round 16 showed the masking was not
incidental but *structural*: **1,904 of the 1,910 verdicts it changed were
relabels of an existing refusal**, including the absence branch's strongest one.
The checks were simply in the wrong place; they now run only on a claim that
would otherwise be CERTIFIED, which makes the only possible transition
`ABSENCE_SUPPORTED → UNVERIFIED_NUMBER` by construction. A fail-closed change
cannot create Error-B, but it can make open findings read as closed, and that is
a quieter failure than an Error-B because nothing goes red.

**APPENDED AFTER ROUND 16 — and it is the sharpest instance of the day's own
lesson.** The paragraph above originally explained the J-33 masking as `X200`
extracting the numeric token `200`, absent from the sources. **That was false.
`200` IS present in both ABS source texts; the refusal came from `99`, the
digits of the unrecognised marker `[s99]`.** I had reasoned from a mechanism I
found plausible, written it into the register, this logbook and a test's
assertion message, and never isolated it — three variants would have taken one
command and I ran none of them. So the day's conclusion applies to my own
*explanations* as much as to my instruments: a cause that fits the evidence is
not thereby the cause, and the control that settles it is cheaper than the
correction. Round 16's measurement is also now the reason to distrust this
morning's "Error-A unchanged": q22's delta cannot register in the metric by
construction, so that zero was an n=1 reading on a model number.

## Next

Round 16's findings, then J-81's three moat fixtures. **Sai's:** the publish
(approved, not performed), J-54, J-51, q25, J-78 when `ival_2.0` and `iPay` go
quiet, and the 5-user test — which can still reverse D-83.
