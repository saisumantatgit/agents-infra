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

**J-83 changes the verdict path and the rates still did not move** — because no
corpus row cites a source that IS its own draft. **That zero is therefore
NON-MEASUREMENT for J-83, not safety**: the corpus cannot represent the shape.
The evidence that J-83 works is the direct reproduction (PASS 100.0 → exit 1 on
the store Sai's own J-54 test wrote), plus 4-of-7 PROVEN-RED tests. For the
three display changes the same zero IS the right evidence, since a display
change that moved a rate would prove a leak into the verdict path.

## The diagnostic's two rates, both re-measured

| Measure | Before | After J-79 |
|---|---|---|
| False alarms on claims the gate PASSES | 4/15 = 0.267 | **0/15 = 0.000** |
| Recall on a 14-vector denial set | 7/14 = 0.500 | **7/14 = 0.500** |
| Positive control (asserting source) | clean | **clean** |

**`0/15` is a rate on fifteen rows, not a claim that no false alarm exists.**
Published in five places; all five were corrected when the number moved, within
an hour of the previous correction.

## What was withdrawn

- **A conditional identifier note**, gated on a digit sitting against a letter.
  My own test caught it: it fires on `100K`, an ordinary quantity, and misses
  `iPhone 15` and `ISO 27001`, which are space-separated. **Over- and
  under-inclusive at once — J-72's own difficulty, which does not get easier
  because the answer is only being displayed.** Replaced by a note that states a
  fact about the extractor rather than a judgement about the sentence.
- **J-72's narrowing**, withdrawn from the committed set at tick 1 because it is
  PASS-enabling and I had queued a parked item.

## Non-measurement and limits, named

- **J-83's corpus delta is non-measurement** (above). A corpus row citing its own
  draft would be needed, and that is a gold-label change — Sai's.
- **J-35 is NOT closed and a test asserts so.** Write claims to a DIFFERENT file,
  Read it, cite it: path and digest both differ, nothing in J-83 fires.
- **`self_source_ids` defaults to EMPTY**, so a library caller that omits it gets
  no protection. Fail-OPEN by choice, recorded as a `CEILING:` in the code.
- The 14-vector denial set is **my own construction**; round 17 was asked to
  build its own and compare.

## Verdict

**No change to the deployed operating point. CR-007 still governs.** One Error-B
closed that was found by accident in ordinary use rather than by an adversary;
three refusals made diagnosable without moving a verdict. **PR #7 is merged;
`main` remains untouched at `009c646` and the release, approved as D-83, has not
been performed — Escalation #5 reserves the act.**
