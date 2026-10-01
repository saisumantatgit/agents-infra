# OVERNIGHT INSTRUMENT — 2026-10-01B (second night, post-merge)

**This file holds HOW TO DERIVE the work each cycle, never a list of answers.**

GOAL: **make Agent-Assure shippable tomorrow under the claim Sai approved** —
so a stranger can install it in their own repo, run it on a real draft, and the
promise on the tin is one the code actually keeps.

---

## §A The derivation rule — run every tick, never quote last cycle

1. **Code first.** "X is done" is settled by reading the file and by a fresh
   `uv run pytest -q`, never by `docs/jobs/REGISTER.md` and never by a prior
   tick's note.
2. **The DIFF** = every §B row neither BUILT (gated green, committed) nor OWNED
   BY A NAMED HUMAN with the blocking reason stated.
3. Append to `docs/logbook/overnight-2026-10-01B-progress.md`: UTC · diff count ·
   what changed · new tokens (output + cache creation) · frameworks declared.
4. Pick the next undone row in §B order — a dependency order, not a preference.

## §B The queue

Branch: `launch-claim-2026-10-01` (child of `agent-assure-calibration-run`).

| # | Job | Done means | Direction |
|---|---|---|---|
| 1 | **J-41r — same-line comment rule** | Strip only when opener and closer share a LINE (plus existing code-span protection). All 9 known attacks from rounds 9/10/11 score the fabrication; single-line notes still PASS. ~5 functions deleted. | fail-closed (strips strictly less) |
| 2 | **J-22 — factive verbs** | `conclude/concludes/concluded` and `indicate/indicates/indicated` added. `report*` NOT added. Tests both directions. | **PASS-enabling — ratified by Sai 2026-10-01** |
| 3 | **CLAIM-1 — the product claim** | `plugin.json`, `README.md`, `commands/assure-verify.md` and the skills no longer promise what round 10 disproved. Every surface states what is ENFORCED. | docs only |
| 4 | **J-38 — make "this session" real** | `session_id` recorded on every captured record; `fetched_at` stamped for real; the gate REFUSES a record from another session. Demo store migrated in the same commit (close-after-open). | fail-closed |
| 5 | **CR-005** | ≤80 lines, projection = CR-004 actuals, delta column. Mandatory per CLAUDE.md failure-mode 9 after tonight's `ground()` changes. | record |

**STRETCH, only if 1–5 are provably done:**

| 6 | **α4-partial — isolated install validation** | `install.sh` runs in a THROWAWAY clone under the scratchpad; the gate then runs end-to-end on the demo draft+store from that install. Friction list recorded. **Does NOT register hooks into any live config** — that is Escalation #4. |
| 7 | J-43 (`ninety-seven percent` never extracted), J-44 (`migraine`/`migraines`), J-45 (`evidence_basis` announces uncounted queries) |

**NOT attempted, and why:**

- **T3 / any NLI tier** — Sai's standing no, and the HHEM diagnostic measured
  union gain ZERO.
- **Any gold-label change, q25** — standing gate, never Claude's.
- **J-36 absence ledger / J-35 Read-trust** — **now ACCEPTED DESIGN** under the
  threat-model ruling of 2026-10-01 ("trust the tool calls, narrow the claim").
  They stop being bugs and become scope; CLAIM-1 is how that gets honoured.
- **Hook REGISTRATION into any live config, install.sh edits** — Escalation #4.
- **A live multi-tool capture session** — needs a real session; queued for Sai.
- **Merging to `main`** — not asked for; `main` stays untouched.
- Anything outward-facing.

## §C The three gates every change must clear, in order

1. **PROVEN-RED.** Run the test against pre-fix code and SEE it fail. A
   tripwired `strict` xfail that starts XPASSing is the cheap version.
2. **DIRECTION.** Regenerate the corpus and byte-diff. **Any row moving TOWARD
   PASS halts that item** — except row 2 (J-22), which Sai has ratified as
   PASS-enabling, and whose drift must still be adjudicated row by row.
   **Remember what byte-identical MEANS:** the corpus cannot measure a shape it
   does not contain. It is not evidence of no regression.
3. **SUITE.** `uv run pytest -q` green, count recorded, commit downstream of the
   tests chained with `&&`.

## §D Competence boundary — named before the night

Last night produced **eight withdrawals, six of one shape: a confident general
claim drawn from a check narrower than the claim.** The sharpest came AFTER I
had written the warning — I named the direction trap in `check_absence`, tested
it, commented it, then introduced that exact failure one argument to the left,
because I checked the direction of the parameter I was THINKING about and not
the one I was CHANGING.

Counter-measures, mandatory:
- For any change to a function with multiple parameters, state the direction of
  **every** argument I touch, not just the one motivating the change.
- **D-46's standing rule:** when a fix makes an unrelated tripwire pass, assume
  it MASKED the finding until proven it CLOSED it.
- No closure claim ships without an adversary that has seen the conclusion
  already committed in writing.

## §E Circuit breaker — a sanctioned stop

HALT and disarm at: two consecutive cycles with an unchanged diff and no
in-flight growth · two consecutive failures of the same terminal class · budget
ceiling · hard stop. Name the blocking class on the way out.
