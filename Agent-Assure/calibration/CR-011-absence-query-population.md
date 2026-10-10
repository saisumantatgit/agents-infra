# CR-011 — the absence query population (J-84 + J-85)

**TDR:** none. This is the post-execution record for the J-84/J-85 fix, per
ADR-025's rule that a calibration run gets a CR whether or not the numbers move.
**CR-007 remains the DEPLOYED operating point.**

## Projection (from `docs/planning/OVERNIGHT-2026-10-03C.md` §5)

| item | projected |
|---|---|
| defects closed | J-84 and J-85, as two separate holes needing a signature change |
| mechanism | separate the COUNT population from the DENOMINATOR population |
| Error-A | unchanged or lower; a RISE means the ruling was misread |
| Error-B | must not move at all |
| corpus drift | unknown |

## Actual

| item | actual | delta |
|---|---|---|
| defects closed | **J-84 and J-85 are ONE hole** | mechanism restated |
| mechanism | **no signature change** — the call site stopped putting self-`Read`s in the one population | smaller than projected |
| suite | **851 passed · 2 skipped · 68 xfailed · exit 0** | +3 tests |
| gold md5 | `6215b526d03147295b003d7ccb0d171f` | unchanged |
| corpus md5 | `affd3f9f703b15612d69e4cc0deb5010` before **and** after | **zero drift** |
| Error-A | **0.400** | unchanged |
| Error-B | **0.000** | unchanged |

**The rates are a DEDUCTION, and the premise is stated so it can be attacked:**
the regenerated `feature_rows-v2.jsonl` is byte-identical and `labels-v2.csv` is
byte-identical, and the metric is a pure function of those two files — so the
rates cannot have moved. **This is not a fresh measurement of 0.400**, and the
distinction matters because quoting a deduced number as a measured one is how a
stale operating point survives a change.

**ZERO DRIFT IS NON-MEASUREMENT, NOT SAFETY** (CR-005's recorded lesson). No
gold row carries a store with a self-`Read` in it, so the corpus is structurally
blind to this change. The instrument that CAN see it is the adversarial one, and
that is where the three new tests live.

## Why the projection was wrong, which is the useful part

The register said both defects needed `check_absence` to separate COUNT from
DENOMINATOR. Re-derived from the code — the instrument's §2 rule, *never act on
a register row without re-deriving its mechanism* — that is true of **J-42** and
false here. A `haiku_summary` IS a real search, so it must leave the numerator
and STAY in the denominator: two populations, genuinely. **A self-`Read` is not
a search in any role**, so it leaves one population, and the D-54 direction trap
cannot arise because nothing is kept in one job and dropped from another.

The trace that settled it:

| store | len | head-bearing | blanket gate | verdict |
|---|---|---|---|---|
| 2 self + 1 irrelevant | 3 | 2 | **fires** (4>3) | UNVERIFIED_ABSENCE |
| + 3 irrelevant queries | 6 | 2 | **silent** (4>6 false) | **ABSENCE_SUPPORTED** |
| self removed, either shape | 1 or 4 | 0 | silent | UNVERIFIED_ABSENCE |

So **J-84 was not reproducible as written** — it refused, but on the blanket
gate, for the wrong reason. J-85's padding is what disables that gate and
exposes it. One hole, two rows, and the fix rests on the COUNT rather than on a
gate an author can switch off.

## Verdict

**J-84 CLOSED · J-85 CLOSED.** Fail-closed: the only transition available is
ABSENCE_SUPPORTED → UNVERIFIED_ABSENCE. Error-B cannot move; Error-A can only
move on a row with a self-`Read`, and no gold row has one.

**CEILING:** this closes the SELF-read vector into the query population. An
attacker making genuinely irrelevant real searches can still dilute the
blanket-word denominator — the `2 * matching > len(distinct)` proportion test is
Goodhart-able by anyone willing to run extra searches. Replacing a proportion
test changes the Error-A/Error-B trade-off, so it is **Escalation #1 and Sai's**,
registered as **J-96**. Not fixed here, and not implied to be.
