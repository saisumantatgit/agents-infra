# OVERNIGHT INSTRUMENT — 2026-10-01

**This file holds HOW TO DERIVE the work each cycle, never a list of answers.**
A wrong fact baked into a recurring tick executes every tick; a wrong fact here
is correctable between ticks. The tick text carries no state — state is
re-derived from this file each cycle.

Goal: **make PROVENANCE actually true** — no fabricated citation can certify
PASS on any claim kind — so the gate's one-sentence promise is a fact of the
code rather than a claim in a spec.

---

## §A The derivation rule — run this every tick, never quote last cycle

1. **Code first.** The claim "X is fixed" is settled by reading
   `Agent-Assure/scripts/ground_check.py` and by a fresh `uv run pytest -q`,
   never by `docs/jobs/REGISTER.md` and never by a prior tick's note.
2. **The DIFF** = every row in §B neither (a) BUILT — gated green, committed,
   tripwire xfails converted to passing tests — nor (b) OWNED BY A NAMED HUMAN
   with the blocking reason stated.
3. Append to `docs/logbook/overnight-2026-10-01-progress.md`: UTC · diff count ·
   what changed · new tokens (output + cache creation) · frameworks declared.
4. Pick the next undone row in §B order. §B order is a dependency order, not a
   preference.

## §B The queue — derived, re-checkable, in dependency order

| # | Job | Done means | Fail-closed? |
|---|---|---|---|
| 1 | **J-25** — move the unresolved-citation check in `ground()` AHEAD of the RELATIONAL/ABSENCE kind dispatch | `[S2][S3][S99]` and `[S99] We found no evidence…` both refuse; `test_moat_r9_provenance_open.py` xfails converted to passing | yes |
| 2 | **J-26** — `load_store` raises on duplicate normalised id, duplicate JSON key, wrong type, `tool`/`full_text_source` mismatch | each of the four raises with the offending line/key; no silent repair | yes |
| 3 | **J-27** — comment stripping detects code the way CommonMark does (tilde fences, indented blocks, escaped openers) | R8B-01/02 + R9P2-05/06/07 tripwires converted | **widens the denominator — verify direction, see §C** |
| 4 | **J-29** — round 10, provenance only, against the repaired tree | report written; every finding tripwired or closed; nothing reported CLOSED without the solo gate | n/a |

**Not in the queue, and why** — these are not blocked-by-time, they are
blocked-by-authority or ruled out:

- **J-24** the product call · **J-22** factive-verb whitelist (PASS-enabling,
  Escalation #1) · **J-28** §7.5 hook registration (Escalation #4) · **q25**
  gold adjudication · **OI-MOAT-31** · **J-15** · **D-07** ·
  `docs/consulting/` privacy — all **owner: Sai**.
- **T3 / any NLI tier** — do not build.
- **Any gold label change** — standing gate, never Claude's.
- Anything outward-facing.

## §C The three gates every change must clear, in order

1. **PROVEN-RED.** The test for the fix is run against pre-fix code and SEEN to
   fail. Tripwired xfails are the cheap version: a `strict=True` xfail that
   starts XPASSing is the red-to-green transition, already recorded.
2. **DIRECTION.** Regenerate the calibration corpus and **byte-diff it**. Every
   drifted row is adjudicated against its label. **Any row moving TOWARD PASS
   halts that item** — that is Escalation #1 and is not mine tonight. Rows
   moving AWAY from PASS are inside the ratified fail-closed reading.
3. **SUITE.** `uv run pytest -q` green, with the new count recorded. The commit
   is downstream of the tests, chained with `&&`.

A change that clears 1 and 3 but not 2 is **registered for Sai, not shipped.**

## §D Competence boundary — named before the night

This project's documented failure, three times over, is **enumerating my own
fixture shapes and mistaking that for enumerating the class**: round 3 (token
count), round 4 (capitalisation), round 8 (every fixture used `that the …`, the
exact blind spot I had named in the dispatch prompt). Twice I reported a class
CLOSED that was not.

Counter-measure, mandatory per closure claim: write the conclusion FIRST, commit
it, then dispatch ONE full-context adversarial agent instructed to attack the
shape my fixtures do NOT contain. Log `challenged | upheld/corrected`.

## §E Circuit breaker — a sanctioned stop, not stalling

HALT and disarm at any of: two consecutive cycles with an unchanged diff and no
in-flight growth · two consecutive failures of the same terminal error class ·
budget ceiling · hard stop. Name the blocking class on the way out.
