# RESUME HERE — 2026-10-02C

**Branch** `delivery-queue-2026-10-02` · **PR #7 OPEN — DO NOT MERGE YET** (see
below) · base `agent-assure-calibration-run` · `main` untouched at `009c646`.

**Suite: 793 passed · 2 skipped · 61 xfailed.** Gold md5
`6215b526d03147295b003d7ccb0d171f` unchanged; zero labels touched ever.
**Error-A 0.400 (10/25) · Error-B 0.000 (0/27)** — CR-007 supersedes CR-005.

---

## THE ONE THING TO KNOW

**Relational grounding is DEMOTED (ADR-007, Sai's ruling).** A RELATIONAL claim
returns `UNVERIFIED_RELATION`, always. The two-source corroboration rule still
runs and still reports, as `relation_diagnostic`, and **decides nothing**.

It was implemented TWICE in one sitting. The first implementation let relational
claims fall through to the verbatim path (cheaper: Error-A 0.360) and **round 13
found six new Error-B shapes in it, five CRITICAL** — T1 certifies on an 8-token
span anchored at the claim's SUBJECT plus coverage, so direction reversals,
denied relations and negation flips all certified PASS 100.0. **Withdrawn
(D-76).** The flat refusal is what is in the tree.

## DO NOT MERGE PR #7 UNTIL ROUND 14 RUNS (J-68)

No adversary has seen the current code. Round 13 attacked an implementation that
no longer exists, and **two implementations in this area have been refuted
within hours of landing** (D-68→D-69, D-74→D-76). That is the whole reason this
instruction exists.

## QUEUES

**Sai's:** J-54 (2 min, interactive `claude --plugin-dir` → `/hooks` → read a
file → `/assure-verify`) · J-51 (two lines in `install.sh`) · q25 · and now
**J-66** — 0.400 understates the real-draft Error-A, because ADR-005's hard cap
means ANY draft with an unquoted causal sentence fails.

**Claude's, in this order:**
1. **J-68 — round 14 against the flat refusal.** First item. Nothing ships first.
2. **J-67** — T1's 8-token span + set-membership coverage rule, and the
   hedge/denial check that did NOT fire. Moot for relational (refused outright),
   **live for FACTUAL**, and **invisible to the corpus**.
3. **J-62** — the absence branch's spelled-figure hole; the one round-12 Error-B
   ADR-007 does not close.

## READ THESE FIRST, IN ORDER

1. `docs/logbook/2026-10-02C-the-demotion-and-two-refinements-too-many.md`
2. `docs/decisions/ADR-007-demote-relational-grounding.md` — **read the
   Amendments section**; the body describes the withdrawn implementation.
3. `Agent-Assure/reports/RED-TEAM-R13-2026-10-02.md` — 16 findings, and its
   "WHAT I COULD NOT BREAK" section is where the moat actually holds.
4. `Agent-Assure/calibration/CR-007-relational-demotion.md`
5. `docs/decisions/RATIFICATION-REGISTER-2026-08-30.md` — D-62…D-77, each with
   its undo. Four are withdrawals.
6. `docs/jobs/REGISTER.md` — every open row has a named owner.

## TRAPS — DO NOT RELEARN THESE

- **A measurement is only evidence about the shapes your instrument can
  represent.** The corpus said fall-through was better and was structurally
  incapable of saying otherwise: **no corpus row has a subject phrase of 8+
  tokens**, which is exactly what T1's span rule needs. For Error-A the
  instrument is the corpus; **for Error-B the instrument is an adversary, never
  a corpus.**
- **Inside a ruling that touches the moat, a refinement needs its own adversary
  BEFORE it lands.** Twice in one day a refinement argued from a correct
  measurement created Error-B (D-68 J-44's stem; D-74 the fall-through).
- **Ask of any new word list: which way does a MISSING MEMBER point?** A list
  driving a REFUSAL is safe to get wrong. A list licensing an ACCEPTANCE makes
  its own gap the attack.
- **A check gated on a classifier branch is routable by adding one word.** The
  numeric gate read `kind == NUMERIC` while `classify` ranks RELATIONAL higher,
  so a figure in a causal sentence was checked by nothing. Figure checks are
  kind-independent now (D-77).
- **When a fix makes an unrelated tripwire pass, it MASKED it** (D-46). Fired
  three times today.
- **A tripwire re-pointed at a different field can go BLIND.** The J-33 `[Sxx]`
  test kept a message about `UNVERIFIED_CITATION` while asserting only the
  diagnostic, which cannot express it.
- **Locate every edit by its own function, never by first-occurrence or blanket
  string replace.** Both forms bit me today; both were caught by reading, not by
  the suite.
- `claude -p` runs **no** PostToolUse hooks. CI is not a launch target.
