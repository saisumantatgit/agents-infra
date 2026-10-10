# CR-013 — Overnight 2026-10-10: the capture contract, closed where it can be

**Window:** 2026-10-10 22:12 → (hard stop 07:00 IST) · **Instrument:**
`docs/planning/OVERNIGHT-2026-10-10.md` · **Ratification:** D-94.
**Supersedes:** nothing. **CR-007 remains the DEPLOYED operating point.**
**Deployed rates UNCHANGED: Error-A 0.400 (10/25), Error-B 0.000 (0/27), n=52**,
re-derived with `measure_rates` after every change, not quoted.

## Projection vs actual

| # | Projected | Actual | Δ | Verdict |
|---|---|---|---|---|
| C1 | failed/blank fetches stop counting, ONE class | `ac77b8e`; PROVEN RED 6/7 | design + | **DONE** |
| C2 | one record per URL; no guessed attribution | `472f2d7` (with C3); multi-URL → `url=None` | — | **DONE** |
| C3 | no document glued to another; Error-A priced | `472f2d7`; price **UNMEASURED** — no multi-block capture exists | instrument − | **DONE, price open** |
| C4 | round 21 against C1–C3 | _pending_ | | |
| C5 | CR, register, close, PR | this file | | in progress |
| Stretch | price absence-as-advisory | J-97: one gold row, A 0.400 → 0.440 | — | **DONE** |
| Budget | 2.1M of 3M (3.6M ceiling) | tracked in the progress file | | |

## Deltas over 20%, explained

**C1 — design changed before any code.** The obvious repair, dropping failed
searches from the query list, shrinks the denominator of the blanket-corpus-word
gate and can switch a refusal OFF: the D-54 trap. The shipped shape ANDs the
existing verdict with one over content-bearing sources instead, which can only
turn a yes into a no. And D-46 fired inside it: four strict tripwires briefly
passed because status-less fixtures made every absence refuse. Unmasked by
marking successful-fetch fixtures `ok`; all four are open again.

**C3 — instrument shortfall.** The corpus has no multi-block or multi-URL row and
Sai's live store has no exa capture, so the Error-A cost of splitting blocks is
non-measurement, stated as a CEILING in the code.

## What this run did NOT move

Error-A, Error-B, any gold label, J-35, J-36, J-38, `install.sh`, hook
registration, `main`.
