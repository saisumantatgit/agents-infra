# 2026-10-02B — the queue, and the stem that cost a day's confidence

## What

Merged PR #6 on Sai's GO, then executed the whole approved delivery queue:
J-48 → J-43 → `extract_arguments` (J-39) → J-44 → one adversarial round →
CR-006. Four of the five code/doc items landed. **The fifth, J-44, landed and
was withdrawn the same day because the adversary proved it was an Error-B.**

## Why

Sai's rulings of 2026-10-02 authorised each item individually and fixed their
ORDER. The order turned out to be load-bearing twice: J-44 after J-39 (his
ruling), and the adversary after all four (the project's three-round law).

## Done

| Item | Outcome | Commit |
|---|---|---|
| J-48 | Documentation on all three surfaces + two guards that give prose a runtime | `1c00bdc` |
| J-43 | Spelled figures checked by VERBATIM PRESENCE, relational only | `657c81e` |
| J-39 | Endpoints are contiguous head-noun PHRASES; one shared `_endpoint_in_window` | `5c177fa` |
| J-44 | Symmetric plural stem — **WITHDRAWN** | `10656fd` → `59b647d` |
| Round 12 | 16 findings, all reproduced: 9 Error-B, 3 Error-A, 2 test, 2 doc | `59b647d` |
| CR-006 | No rate moved; J-39 measured, J-43 not | `09d6b5c` |

Suite **751 → 789 passed**, 2 skipped, 63 → 61 xfailed. Corpus byte-identical
at all four regenerations; gold md5 `6215b526…d171f` never touched; zero labels.

## Decisions

**D-62 … D-72.** Three are withdrawals, which is the number worth noticing.

- **D-69 — J-44 withdrawn.** `_stem` strips a trailing "s" with no
  part-of-speech test, so it maps the noun "news" to the adjective "new".
  `The recall causes negative news [S1][S2]` was UNVERIFIED_RELATION before
  J-44 and **GROUNDED / PASS 100.0 / exit 0** after it, against two sources
  containing no "news", with `evidence_basis` reporting "checked verbatim".
- **D-70 — J-43's lexicon completed** with the plural scale words. "thousands
  of" produced NO phrase, so the guard ran vacuously on the commonest
  fabricated magnitude while "fifty thousand" was refused on the same store.
- **D-71 — the R12-11 fix written, measured, withdrawn.** Making a preposition
  a run boundary does not shorten the endpoint; it MOVES side_B's anchor and
  produces a one-token endpoint. R12-11 and R12-03 are ONE design decision.
- **D-72 — the seven pre-existing Error-Bs registered, not fixed** (J-57 …
  J-62, J-64).

## Agents

One Opus-class adversary (168K tokens, 42 tool calls, 18 min). Routed to Opus
under the standing rule that moat verification never downgrades — and it
returned a CRITICAL regression on its first finding, which is the clearest
justification that row has had. Everything else was done in-session.

## Withdrawals, in full

1. **"No new Error-B" (conclusion-first claim 1) — REFUTED.** By my own code.
2. **"J-39's longer phrase bounds the stem" — WRONG, and specifically so:** a
   collision on the HEAD noun makes the modifiers irrelevant.
3. **"Every new 'I don't know' points away from PASS" — PARTLY REFUTED.** An
   unrecognised spelled quantity read as "no quantity asserted".
4. **The R12-11 preposition fix — withdrawn after measuring it.**
5. **"Six pre-existing Error-Bs" — it was SEVEN.** Caught by the three-hat Gap
   Analyst pass after I had written "six" in four places across three files.
6. **Two of my own new tests were near-vacuous**, as the adversary said.

## Reflection

The thing I will carry out of today is that **J-43 and J-44 look like the same
move and sit on opposite sides of the invariant.** Both forgive a surface
difference using a hand-written word list, and I defended both with the same
sentence — English has a closed lexicon here, so this is not the enumeration
trap. That sentence is true of J-43 and worthless for J-44, because the two
lists do opposite work. `_SPELLED_NUMBER_WORDS` drives a REFUSAL: a missing
member means a figure goes unchecked, which is a bug you fix by adding strings,
and R12-05 was exactly that. An s-final-singular blacklist would license an
ACCEPTANCE: a missing member **is the attack**, and "news" was the missing
member. The right question about a new lexicon is not "is this class closed?"
but "**which way does a missing member point?**" — the same question the
round-4 rule asks about a `None`, which I had written into the code comment of
the very function that then failed it. Knowing a rule and locating the thing it
applies to are different skills, and the second one is what an adversary is for.

## Next

Sai's: J-54 (the launch gate, 2 min), J-51, q25 — all still open. **New and
material: whether CLAIM-1 must narrow, given seven demonstrated Error-B shapes
on the relational branch.** That is Escalation #1 and #5, with J-57 … J-64 as
the evidence. PR for this branch is open and needs his GO.

Claude's, next session: J-61 and J-64 are the two whose repairs are fail-closed
and small — each gets its own adversary, not a same-day commit. J-62 (absence
spelled counts) is the same guard on a different branch.

**One thing I did NOT verify:** the adversary's claim that all seven
pre-existing findings reproduce identically against `1c00bdc`. I reproduced
R12-01 and R12-06 myself. The other five are its testimony, not my evidence.
