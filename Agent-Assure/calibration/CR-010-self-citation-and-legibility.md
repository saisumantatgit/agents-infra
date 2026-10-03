# CR-010 — A draft may not certify itself; and three refusals made legible

**Window:** 2026-10-03 14:16 → 18:30 IST (afternoon run, D-87)
**Supersedes:** nothing. **CR-007 remains the DEPLOYED operating point.**
**Deployed rates UNCHANGED: Error-A 0.400 (10/25), Error-B 0.000 (0/27), n=52 gold.**

## Projection vs actual

| Item | Projected | Actual | Δ | Verdict |
|---|---|---|---|---|
| J-83 self-citation | close it, fail-closed | closed; `UNGROUNDABLE` | — | done |
| J-72 | fix the misparse | **split — the narrowing is PASS-enabling and went back to Sai**; only the display half landed | scope halved | done / open |
| J-79 | reduce the artefact | closed; **false alarms 4/15 → 0/15** | — | done |
| J-82 | basis names the figure | closed | — | done |
| Round 17 | adversary on all of it | dispatched | — | see report |
| Budget | 2.5M new tokens | ~0.9M at writing | −64% | under |

## The gate that mattered: did a verdict move where it should not?

| Measure | Before | After | Moved? |
|---|---|---|---|
| Error-A (n=52 gold) | 0.400 (10/25) | **0.400 (10/25)** | **no** |
| Error-B (n=52 gold) | 0.000 (0/27) | **0.000 (0/27)** | **no** |
| `tests/honest_drafts/` | 7 passed / 3 xfailed | **7 passed / 3 xfailed** | **no** |
| Suite | 822 / 2 / 66 | **838 / 2 / 66** | +16 tests only |
| Gold md5 | `6215b526…d171f` | `6215b526…d171f` | **no** |

**J-83 changed the verdict path and the rates still did not move — that is
NON-MEASUREMENT for J-83, not safety**: no corpus row cites a source that IS
its own draft. Its evidence is the direct reproduction plus proven-red tests.
For the three DISPLAY changes the same zero IS the right evidence.

## The diagnostic's two rates, both re-measured

| Measure | Before | After J-79 |
|---|---|---|
| False alarms on claims the gate PASSES | 4/15 = 0.267 | **0/15 = 0.000** |
| Recall on a 14-vector denial set | 7/14 = 0.500 | **7/14 = 0.500** (set-composition — see below) |

**R17-07: "recall unchanged" was TRUE OF MY SET AND FALSE AS A CLAIM.** J-79
does lose a denial whose hedge word the claim itself uses; my 14 vectors
contained none of that shape. The trade is real and now stated: precision up,
recall down on one specific shape.
| Positive control (asserting source) | clean | **clean** |

**`0/15` is a rate on fifteen rows, not a claim that no false alarm exists.**
Published in five places; all five were corrected when the number moved, within
an hour of the previous correction.

## Rounds 17 and 18 — four CRITICALs, all the same class

| Round | Finding | State |
|---|---|---|
| 17 | J-83's filter never reached the ABSENCE branch; a store of only self-`Read`s certified at PASS 100.0 | fixed |
| 17 | the digest test trusted `content_sha256`, which nothing recomputes (J-32) | fixed |
| 17 | a NUL byte raised `ValueError`, not `OSError` — the gate crashed | fixed |
| 18 | `_absence_verbatim` still read `store.values()` **four lines below** the R17 fix | fixed |
| 18 | **J-84** — the basis rule is a tripwire: one irrelevant real source licenses an absence the draft argued for itself | **open** |
| 18 | **J-85** — GROWING the query list is fail-open; D-54 recorded only SHRINKING | **open** |

**The class: `ground()` has 15 returns across 6 kinds; a check at one protects
one.** Four instances in two days, each per-instance fix correct and leaving the
class open. A cross-product guard now covers every `ClaimKind` — **and round 18
proved that guard could not reach its own target**, staying green against a
broken gate because an all-self store refuses at the BASIS rule before the
figure returns execute. A mixed-store fixture now reaches it.

**J-84 and J-85 are NOT fixed deliberately.** Both need `check_absence` to
separate queries that may COUNT from queries that may form the DENOMINATOR — the
signature change J-42 has needed since 2026-10-01, in the function that already
produced one self-inflicted Error-B. Both reproduce at the pre-run commits, so
neither regresses this CR.

## Verdict

**No change to the deployed operating point. CR-007 still governs.** One Error-B
closed that was found by accident in ordinary use rather than by an adversary;
three refusals made diagnosable without moving a verdict. **PR #7 is merged;
`main` remains untouched at `009c646` and the release, approved as D-83, has not
been performed — Escalation #5 reserves the act.**
