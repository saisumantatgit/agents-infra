# OVERNIGHT PROGRESS — 2026-10-02 → 2026-10-03

**Instrument:** `docs/planning/OVERNIGHT-2026-10-02.md` · **Branch:** `delivery-queue-2026-10-02`
**Checkpointed each cycle. A skeleton written at START, filled as it goes — an agent
whose whole output is one final write delivers 0% when it dies at 95%.**

**Budget measure: NEW TOKENS = output + cache creation.** Named on every number.

| UTC | Diff | What changed | New tokens | Frameworks |
|---|---|---|---|---|
| 16:37 | — | §0 handshake: state derived from CODE (flat refusal confirmed live at `ground_check.py:3453`), suite 793/2/61 exit 0 from a fresh run, gold md5 unchanged, open-job owners read. Instrument + this file written. **Not armed — waiting on AGREED.** | ~0.05M | First principles (state from code); Theory of Constraints (round 14 is the upstream node); Competence boundary (declared: auditing where the measurement lives, not where the work lives) |

---

## CYCLE LOG

### §0 — handshake, 16:37 UTC / 22:07 IST

Derived from code, not from the register:

- `ClaimKind.RELATIONAL` → `return Verdict.UNVERIFIED_RELATION`, unconditional.
  The fall-through (D-74) is gone; D-76 is in the tree.
- The figure checks are **kind-independent** (D-77): `claim.numeric_tokens` and
  `spelled_quantity_ok` are gated on the FIGURE, not on `kind == NUMERIC`.
- The demoted machinery is kept and still reports (`relational_diagnostic`).
- Suite: **793 passed · 2 skipped · 61 xfailed · exit 0**, fresh run, 39.99s.
- Gold md5 `6215b526d03147295b003d7ccb0d171f` — unchanged.

**Awaiting AGREED. Nothing armed.**

### CYCLE 1 — 16:5x UTC — J-37, and a stale register row that cost the cycle

**Diff at start:** 5 Claude-owned unblocked rows (J-68 in flight, J-62, J-67, J-37, J-45).
**Diff at end:** 4. J-37 closed — but not by the work I set out to do.

| | |
|---|---|
| Round 14 (J-68) | **IN FLIGHT.** Opus adversary dispatched. Named trigger ending the wait: its completion notification. Not idling meanwhile. |
| J-37 | **Was ALREADY CLOSED** in `15baf1e` (2026-10-01). The register row described the pre-fix state in the present tense. |

**What I measured instead of asserting.** A probe round-tripped all 52 corpus
stores through the shipped `load_store`: **52/52 accepted, 0 refused**, tools
present are `Read` and `WebFetch`. Positive control confirmed the probe can
still detect a refusal (`tool="calibration_fixture"` → `ValueError`). So the
row's alarming half — *"CR-005's A=0.400 / B=0.000 is measured on stores the
shipped gate would reject"* — **is false, and CR-005's own wording was accurate.**

**My error, recorded because its absence would read as though I was right.** I
wrote a whole duplicate test (`test_corpus_loader_parity.py`, 54 passing cases)
before searching the suite for an existing one. `tests/test_corpus_stores_
survive_the_loader.py` had been there since Oct 1 doing the same job. I climbed
the register instead of the reuse ladder's rung 2. I had written *"code first,
register second; registers go stale, code is fact"* into the instrument file
less than an hour earlier. Duplicate deleted.

A second, smaller instrument failure inside the first: my search script printed
a hardcoded gloss — `(none above = never added before now)` — directly beneath
output that **did** list the adding commit, and I read the label rather than the
data. A control correct about what it examines and silent about what it does
not; this estate's signature defect, committed by its own auditor.

**The one real deliverable.** The existing file contained **no `pytest.raises`
at all**, so all three of its tests were satisfiable by a `load_store` whose
validation had been deleted — it asserted the corpus survives the loader, never
that surviving it still means anything. A fourth test pins the refusal.
Mutation-checked: fed a recognised tool it reports `DID NOT RAISE`.

**Gates, first-hand.** `uv run pytest -q` → **794 passed · 2 skipped · 61
xfailed · exit 0** (793 before; +1 is the control). Gold md5
`6215b526d03147295b003d7ccb0d171f` unchanged. Commit `788f800`.

**Frameworks applied.** *Calibration* — the row asserted a mechanism; I measured
it, and a positive control is what made the measurement mean anything.
*Reuse ladder / via negativa* — the fix became one test appended to an existing
file instead of a new file, and the builder was deliberately NOT rewritten
because serialising every fixture can perturb the corpus bytes and the corpus IS
the measurement. *FMEA detectability* — the sibling I named: the loud failure
(fixtures refused) was already covered; the silent one (validation deleted, all
green) was not. *Sunk cost, on my own work* — 54 passing tests deleted the
moment I found the original; restating the case from what I knew then made that
immediate rather than defended.

**New tokens this cycle:** ~0.20M (output + cache creation), of 3.5M sanctioned.
