# RESUME HERE — 2026-10-02B, after the delivery queue

**Branch** `delivery-queue-2026-10-02` · **PR open, needs Sai's GO** · base
`agent-assure-calibration-run` (PR #6 merged) · `main` untouched at `009c646`.

**Suite: 789 passed · 2 skipped · 61 xfailed.** Gold md5
`6215b526d03147295b003d7ccb0d171f` unchanged; zero labels touched; corpus
byte-identical at all four regenerations.

---

## THE ONE THING THAT CHANGED THE PICTURE

Round 12 demonstrated **seven pre-existing ERROR-B shapes on the relational
branch**, two of them CRITICAL, and **refuted my own J-44 fix** (which I
withdrew the same day — `_stem` maps the noun "news" to the adjective "new", and
a fabricated causal claim certified PASS 100.0 through the CLI).

Nothing here regresses CR-005: every one of the seven reproduces against
`1c00bdc`. What they put in question is **whether CLAIM-1 is still accurate** —
Escalation #1 and #5, Sai's, with J-57 … J-64 as the evidence.

**Do not read the relational branch as settled.**

## SAI'S QUEUE

1. **J-54** — the launch gate, 2 min, interactive: `claude --plugin-dir` →
   `/hooks` → read a file → `/assure-verify`.
2. **J-51** — two lines in `install.sh`. **q25** — one gold label.
3. **NEW: does CLAIM-1 narrow?** (J-57 … J-64). Also **J-44's two designs**:
   a real morphological analyser, or accept the Error-A permanently and say so.

## CLAUDE'S QUEUE, in this order

1. **J-61** (denial window grounds the relation) and **J-64** (both endpoints
   the same phrase). Both repairs are fail-closed and small. **Each gets its own
   adversary — a same-day commit is how J-44 happened.**
2. **J-62** — the absence path's spelled-figure hole; same guard, other branch.
3. Then stop. J-57 … J-60 are Sai's (they move the trade-off).

## READ THESE FIRST, IN ORDER

1. `docs/logbook/2026-10-02B-the-queue-and-the-stem.md` — this window, with six
   withdrawals and the reflection.
2. `Agent-Assure/reports/RED-TEAM-R12-2026-10-02.md` — 702 lines, every finding
   reproduced, plus "WHAT I COULD NOT BREAK".
3. `Agent-Assure/calibration/CR-006-delivery-queue.md` — what is measured and
   what is not.
4. `docs/decisions/RATIFICATION-REGISTER-2026-08-30.md` — D-62 … D-72, each
   with its undo. Three are withdrawals.
5. `docs/jobs/REGISTER.md` — J-57 … J-64, every row with an owner.

## TRAPS — DO NOT RELEARN THESE

- **Ask of any new word list: which way does a MISSING MEMBER point?** A list
  that drives a REFUSAL is safe to get wrong (add strings). A list that licenses
  an ACCEPTANCE makes its own gap the attack. J-43 and J-44 look identical and
  are opposites. This is the most expensive lesson in the file.
- **`claude -p` runs NO PostToolUse hooks.** Agent-Assure cannot capture in CI.
  Not a plugin defect; ruled out as a launch target.
- **A byte-identical corpus is NON-MEASUREMENT unless the rows carry the shape.**
  J-39 is measured (7/7 relational rows now carry multi-token endpoints and no
  verdict moved). J-43 is not. None of round 12's nine Error-B shapes has a row.
- **When a fix makes an unrelated tripwire pass, it MASKED it** (D-46). It fired
  three times in this window: the vague-quantifier xfail, J-33's last relational
  demonstrator, and J-53's fixture.
- **Measure the fix before believing the fix.** The R12-11 preposition repair
  looked obviously right and produced a one-token endpoint.
- **"Design judgment is yours" licenses DECIDING, not overriding a ruling Sai
  has already made.**
- Estimates have now run high three times (7M→2.6M, 3.1M→2.8M, **3.5M→0.65M**).
  Build the next one from TURN COUNT × a short-session rate.
