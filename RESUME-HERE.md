# RESUME HERE — written 2026-10-03, overnight run D-78

# PR #7 IS STILL **DO-NOT-MERGE** — and now for a demonstrated reason

Round 14 ran. It did **not** come back clean. Three CRITICAL Error-B classes are
open against the code that ships, all of them Sai's (Escalation #1). Last
night's handoff said "no adversary has seen the current code"; one has now, and
it routed around the refusal with a single word.

**Read first:** `docs/logbook/MORNING-REPORT-2026-10-03.md`, then
`docs/logbook/2026-10-02D-the-refusal-that-one-word-walked-around.md`.

## State, verified not quoted

- Suite **797 passed · 2 skipped · 66 xfailed · exit 0**
- **Error-A 0.400 (10/25) · Error-B 0.000 (0/27)** — re-derived from current
  code this run, matching CR-007. **CR-007 still governs**; CR-008 records only
  priced candidates, none landed.
- Gold md5 `6215b526d03147295b003d7ccb0d171f` — never touched, zero labels changed.
- `main` untouched at `009c646`. Branch `delivery-queue-2026-10-02`.
- `ground_check.py` is byte-identical to last night **apart from two corrected
  comment blocks and one display string.** Nothing in the verdict logic moved.

## SAI'S DECISIONS — the night's actual output

| # | Decision | The measured price |
|---|---|---|
| 1 | **J-70 — the root cause.** Choose: (a) **structural repair**, give T1 sentence-scoped source text; or (b) **accept and disclose**, state that the gate verifies *presence* in a source, not *agreement* with it. | The blunt repair is **withdrawn**: corpus said +0.160 Error-A, the honest-draft harness said **7 passing drafts → 5 failing**, including a verbatim quote reading UNGROUNDED. |
| 2 | **J-62+J-71 — the cheap one.** Say GO and it lands with a proven-red test. | Closes R14-03a at **Error-A 0.400 unchanged, Error-B 0.000**. The only candidate with no observed Error-A cost. |
| 3 | **J-69 — the causal lexicon.** | **Recommendation: do NOT fix this way.** Wrong layer — J-70 reproduces with no causal word at all, so a lexicon closes 22 fixtures and leaves the class open. The comment stripper's five-round pattern. |
| 4 | J-54 · J-51 · q25 | Unchanged, ~12 min, his terminal. |

## WHAT ROUND 14 FOUND — do not re-derive these

- **R14-01** `causes`→`triggered` flips the same sentence on the same store from
  FAIL/exit 1 to **PASS 100.0/exit 0**. The refusal is gated on `classify`, and
  `_RELATIONAL_RE` is ten surface forms over an open class.
- **R14-04, THE ROOT CAUSE** (supersedes J-67's framing). T1's span anchors in
  the claim's long SUBJECT; `_span_is_hedged` reads only the 5 tokens BEFORE the
  span. **The same denial moved before the subject refuses; left after it,
  certifies.** Reproduces on plain FACTUAL with no causal vocabulary. *"We found
  no evidence that X"* is how real sources report negative findings — this
  arises from honest retrieval, not an attack.
- **R14-02** `_SPELLED_NUMBER_WORDS` excludes `"one"` — a `CEILING:` recorded
  during J-43 — and that breaks the word run, so `one million` is checked only
  as `million`. **The recorded ceiling was the attack.**
- **R14-03a** ABSENCE returns above the figure checks; digit `4200` in no source
  certifies PASS 100.0.
- All five tripwired strict-xfail in
  `tests/red_team_moat/test_moat_r14_hedge_classifier_absence.py`, with three
  **passing** controls proving the guards work and only their scope is wrong.

## TRAPS FROM THIS RUN — do not relearn them

- **The gold corpus is a LABEL instrument, not an Error-A instrument.** It
  measures only shapes someone thought to label. `tests/honest_drafts/` is the
  usage instrument; the adversary is the hostility instrument. **Consult all
  three before recommending a moat change.** Tonight the corpus called a repair
  cheap that breaks a verbatim quotation.
- **A register row that states a mechanism in the present tense must be
  re-derived before it is acted on — including one you wrote.** J-37 had been
  closed for a day; its row still described the pre-fix state and cost a cycle
  and a duplicate test.
- **Do not print a hardcoded gloss next to a search result.** A script of mine
  printed `(none above = never added before now)` directly beneath output that
  listed the adding commit, and I read the label instead of the data.
- **A green round-trip is evidence only while a red one is reachable.** Three
  tests asserted corpus stores survive `load_store` with no `pytest.raises`
  anywhere, so all three would pass against a loader whose validation had been
  deleted. Every such file needs its refusal control.
- **Three pricing patches were applied and reverted tonight.** If `git status`
  is ever dirty in `ground_check.py` unexpectedly, check for a `PRICING PATCH`
  comment before assuming it is real work.
