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

### CYCLE 2 — 17:4x UTC — round 14, and a recommendation withdrawn the same night

**Diff recomputed from code → register → scoreboard.** Start: 4 Claude-owned
unblocked rows. End: **1** (CR-008 + close), because round 14 moved three rows
to Sai as Escalation #1 and merged two others into one class.

| UTC | Diff | What changed | New tokens | Frameworks |
|---|---|---|---|---|
| 17:0x | 4 | Round 14 reported: **3 CRITICAL (NEW) + 2 re-confirmed + 1 doc-defect as the adversary graded it**; I re-graded R14-04 to CRITICAL and said so. All reproduced by me from the adversary's own fixtures. 7/7 round-12 relational shapes confirmed refused; positive control intact. | ~0.35M | Contradiction-as-locator; Asymmetry of error cost |
| 17:3x | 2 | J-69/J-70/J-71 registered with owners and a measured price. ADR-007 amended for my own overclaim (R14-06). 5 strict-xfail tripwires added. PR #7 updated. | ~0.25M | FMEA detectability; Case-vs-Systemic (systemic chosen) |
| 17:5x | 1 | **Recommendation WITHDRAWN** — the priced J-70 repair breaks 5 of 7 honest drafts. J-62+J-71 merged into one class and priced. J-72 opened. | ~0.25M | Calibration; Swiss cheese; Sunk cost (my own) |

**What round 14 found, in one line each.**
- **R14-01** — the D-76 flat refusal is gated on `classify`, and `_RELATIONAL_RE`
  is a ten-member blacklist over an open class. `causes`→`triggered` flips the
  same sentence on the same store from FAIL/exit 1 to **PASS 100.0/exit 0**
  against a source reading *"found no evidence that the migration triggered
  widespread customer refunds"*. **This is the assumption I named as
  load-bearing in the §0 handshake, item 9. It was the one that broke.**
- **R14-04** — and extending that lexicon would not fix it: the same
  certification happens on a plain FACTUAL claim with **no causal word at all**.
  T1 anchors its ≥8-token span in the claim's long SUBJECT; `_span_is_hedged`
  reads only the 5 tokens BEFORE the span. **Measured: the same denial moved
  before the subject refuses (FAIL 0.0), left after it certifies (PASS 100.0).**
- **R14-02** — `_SPELLED_NUMBER_WORDS` excludes `"one"`, a `CEILING:` I recorded
  during J-43, and that exclusion breaks the word run so `one million` is
  checked only as `million`. **The recorded ceiling was the attack.**
- **R14-03a** — `ABSENCE` returns above the figure checks, so `numeric_ok` is
  unreachable: digit `4200` in no source certifies **PASS 100.0**.
- **R14-06** — my own overclaim. ADR-007 and `ground_check.py` both said D-77's
  figure checks were kind-independent *"and an ABSENCE claim carrying a figure
  skipped it too"* — past tense, asserting closure. Both kinds return above
  those checks. Comment fixed in place, ADR fixed by amendment (ADR-023).

**THE WITHDRAWAL, which is the night's real lesson.** I priced the J-70 repair
on the gold corpus at **+0.160 Error-A** and recommended it in a PR comment.
Then I ran the OTHER instrument. `tests/honest_drafts/` goes **7 passed → 5
FAILED**, and one of the failures is a **verbatim quotation of the cited
source** reading UNGROUNDED. Same patch, same hour, two instruments, opposite
verdicts — and the corpus is the one I had already published a recommendation
on. Third instance in three days (D-68's stem, D-74's fall-through) of a correct
measurement from an instrument that cannot represent the cost. **Caught before
landing this time, because running the second instrument was a deliberate step
rather than an afterthought.**

**Nothing landed in the gate.** Three pricing patches were applied, measured and
reverted; `git status` clean after each. The only `ground_check.py` change
tonight is one corrected comment.

**Gates, first-hand.** `uv run pytest -q` → **797 passed · 2 skipped · 66
xfailed · exit 0**. Gold md5 `6215b526d03147295b003d7ccb0d171f` unchanged.
Baseline Error-A/Error-B **independently re-derived from current code: 10/25 =
0.400 and 0/27 = 0.000**, matching CR-007 — so that number is verified, not
quoted.

**New tokens cumulative:** ~1.05M of 3.5M sanctioned (output + cache creation).
