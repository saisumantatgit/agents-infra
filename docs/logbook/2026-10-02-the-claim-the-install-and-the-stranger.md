# 2026-10-02 — the claim, the install, and the stranger

**Sessions:** one long session spanning 2026-10-01 → 02 (two sanctioned runs).
**Branches:** `launch-claim-2026-10-01` (MERGED, PR #5) → `plugin-validation-2026-10-02` (PR #6, open).
**Suite:** 664 → **751 passed, 2 skipped, 63 xfailed.**
**Corpus:** byte-identical throughout; `labels-v2.csv` md5 unchanged; **zero gold labels touched.**

## What

Two sanctioned runs. The first made the product's claim true; the second proved a
stranger can install and use it. Fourteen ratification rows (D-48…D-61), two PRs,
one merged.

## Why

The product had been in red-team rounds for eleven iterations while two things
nobody had checked blocked launch: **the tin said something the code did not do**,
and **nobody had ever installed it outside its own repo.**

## Done

- **CLAIM-1.** All four shipped surfaces promised a claim is "grounded in a source
  actually retrieved this session". There was no session boundary in the code.
  Rewritten to what is enforced, each with a limitations block, and
  `tests/test_product_claim.py` now pins promises AND limitations — so closing a
  limitation fails the suite and forces the claim text to change.
- **"No LLM calls during grounding" had ZERO tests.** The project's loudest claim,
  asserted on four surfaces, appeared in the suite only as prose inside a
  determinism fixture's draft text. Now an AST import walk, proven red twice.
- **J-38.** `session_id` on every captured record; `--session-id` refuses a
  foreign-session store. It RAISES rather than filters, because a filtered store
  is fail-OPEN on the absence path.
- **J-41r.** Comment stripping is same-line only — the fourth design; three
  earlier ones lost rounds 9, 10 and 11.
- **J-22.** `conclude*`/`indicate*` added, `report*` kept out, `found` ≡
  `concluded` parity pinned.
- **CR-005.** A=0.320 / B=0.000 re-derived, with its load-bearing section: a zero
  delta is NON-MEASUREMENT, not safety.
- **α4 and J-52.** Install validation run for the first time in the project's
  history, then the plugin path: manifest, matcher parity, hook command line,
  discovery, and `/assure-verify` producing a correct verdict end to end.

## Decisions

D-48…D-61 in `docs/decisions/RATIFICATION-REGISTER-2026-08-30.md`, each with its
undo. Sai's rulings of 2026-10-02 are in `docs/jobs/REGISTER.md`.

## Agents

6 dispatched. 1 solo gate (J-41r, REFUTED it), 3 round-10 adversaries (13
ERROR-B), 2 round-11 adversaries (10 ERROR-B + 2 ERROR-A), 1 Claude Code guide.
All Opus-class except the guide. Subagent new tokens: 0.46M. **Every adversary
that reviewed a closure claim refuted it.**

## Withdrawals

Six this period, and the record matters more than the count:

1. "Delete comment stripping entirely" — deletion failed EVERY draft containing
   any comment, including `<!-- DRAFT v2 -->`, which scored "v2" as a claim.
2. "Annotate CR-004 instead of emitting CR-005" — failure-mode 9 makes the CR
   mandatory; I was exempting myself because I expected no movement.
3. **D-52 — I extended the comment rule BEYOND Sai's ruling** to protect a UX
   finding. An adversary found 3 ERROR-B in the extension within the hour.
   Reverted to exactly what he ratified.
4. "Renderer-faithful by construction" — the construction assumed `-->` is the
   only way an HTML comment closes. It is not.
5. "Stamp `fetched_at` for real" — the sentinel is deliberate; session scoping
   needs an identity, not a clock.
6. **"J-43's fix is an enumeration like the comment-stripper designs."** Wrong
   analogy: code syntaxes are an OPEN set, English number words are CLOSED. I
   imported a lesson from a case that was not analogous, and it argued me toward
   the wrong answer until Sai pushed back.

## Reflection

The two runs found their biggest defects in the same place and it was not the
moat. **α4 found that the first command the installer prints produced a raw
traceback**, because every one of 750 tests constructs an evidence store before
calling the gate — so nobody had ever been the stranger. Then a real
`claude -p` session running `/assure-verify` **found an overclaim 751 tests had
not**: the engine printed "NEVER RETRIEVED this session" with no session
enforcement on. That is the exact sentence CLAIM-1 had retired from all four doc
surfaces, alive one layer down in runtime strings — where my own drift guard
never looked. The guard and the bug were one layer apart.

Adversaries attack what you built. Tests assert what you thought of. Neither is
the first thing a stranger types.

The harder lesson is #3. I had written that night's competence-boundary warning
into the instrument myself and read it at every tick, and the warning pointed at
the wrong failure — I generalise from narrow checks, yes, but what actually cost
an unrecoverable error was overriding a ratified safety decision to buy a
recoverable one. Naming a weakness does not remove it. It relocates the next one.

## Next

**Sai:** J-54 (2 min, the last launch gate) · J-51 · q25.
**Claude, in a FRESH session:** J-48 docs → J-43 (relational, verbatim presence)
→ `extract_arguments` tightening → J-44 → one adversarial round → CR-006.
ETA ~3.5M new tokens, ~5h. **Start a new session**: cache creation, not output,
is what spends the budget — see the budget stop note in
`docs/logbook/overnight-2026-10-01B-progress.md`.
