# Overnight progress — 2026-10-01

Checkpointed every cycle per `docs/plans/OVERNIGHT-2026-10-01.md` §A.3.
Budget measure throughout: **NEW TOKENS (output + cache creation)**.

| UTC | diff | what changed | new tokens | frameworks |
|---|---|---|---|---|
| 2026-09-30 20:10 | 4 | §0 handshake. Baseline verified from a FRESH run, not the register: suite 564 passed / 2 skipped / 60 xfailed (exit 0); `ground()` RELATIONAL+ABSENCE dispatch confirmed ahead of the unresolved-citation check at `ground_check.py:2570-2577`. Instrument + this file created. **Not armed — awaiting AGREED.** | ~0.05M | First principles · Critical path · Competence boundary |
| 2026-09-30 21:05 | 3 | **J-25 CLOSED.** Provenance check moved ahead of the kind dispatch in `ground()`; R9P1-01/02 seen to XPASS(strict) then converted to 9 passing regressions with sibling shapes (all-fake, NUMERIC, full-width marker, per-claim verdict, and the NULL CASE of an uncited absence claim). Call sites enumerated first: `ground_relational` and `check_absence` have exactly one each, both in `ground()`. Corpus **byte-identical**, gold md5 unchanged. Two side findings: **J-31** (a correctly-cited absence claim is refused while the identical uncited one certifies — pre-existing, verified on the pre-fix tree) and **D-41** (the `evidence_basis` guard matched source TEXT, so it failed on a comment; rewritten over the AST and proven in both directions). My "this was the only such guard" claim was FALSE — the three-kind search found D-34's, converted too. | ~0.35M | First principles · FMEA detectability (named the null case) · Goodhart (the guard's name vs its proxy) · Case-vs-Systemic (systemic) · Calibration (withdrew the "only one" claim) · Name the CEILING |
| 2026-09-30 22:05 | 1 | **J-26 and J-27 CLOSED; J-25's closure claim WITHDRAWN.** J-26: `load_store` raises on duplicate/NFKC-colliding ids, duplicate JSON keys, mistyped fields, out-of-enum source types, tool/source-type disagreement and unrecognised tools (19/27 proven red). It surfaced two r8 fixtures declaring `WebFetch`+`verbatim`, whose strict xfails would have gone on "passing" because the loader now RAISES — a tripwire that fails for a new reason has gone silent. J-27: block-level code-region scanner (tilde + long + indented + info-string fences, backslash escapes); 7/13 red, plus 6 pre-existing strict xfails converted. **The solo gate REFUTED J-25** — an UNRECOGNISED marker (`[s99]`) is not an unresolved citation but NO citation, so RELATIONAL/ABSENCE certify at PASS; registered J-33, count corrected DOWN from the gate's 13 to the 4 I could reproduce. Suite 572 → 628 passed, 58 xfailed. Corpus byte-identical throughout; gold md5 unchanged. | ~0.55M | Inversion (direction of safety: stripping too much is fail-OPEN) · Via negativa + Occam (no CommonMark dependency in the verdict path) · FMEA detectability (named the Error-A sibling and the silenced tripwires) · Contradiction-as-locator (gate vs my repro → position was load-bearing) · Calibration (withdrew the closure claim; corrected the count downward) · Chesterton's Fence (preserved the retired file's reproduction) · Name the CEILING (J-32 sha) |

---

# MORNING REPORT — 2026-10-01

*Skeleton written 03:20 IST while round 10 was still running; budget and
round-10 sections completed at the close. Written this way deliberately: a
report that exists only as a final write delivers nothing if the run dies.*

## 1. DONE

**Branch `provenance-fix-2026-10-01`, pushed, NOT merged.** The merge is your
GO. `agent-assure-calibration-run` is untouched at `b4d4e39`.

| Job | Status | Proof |
|---|---|---|
| J-25 | CLOSED, **then partially REFUTED** (D-42) | `uv run pytest tests/red_team_moat/test_moat_r9_provenance_closed.py -q` → 9 passed, 1 xfailed |
| J-26 | CLOSED | `uv run pytest tests/test_store_integrity.py -q` → 27 passed |
| J-27 | CLOSED | `uv run pytest tests/red_team_moat/test_moat_j27_comment_blocks.py -q` → 17 passed |
| J-29 | round 10 ran, 3 adversaries | see §ROUND 10 |

**Whole suite**, `cd Agent-Assure && uv run pytest -q`:

```
628 passed, 2 skipped, 58 xfailed
```

Baseline at the handshake was `564 passed, 2 skipped, 60 xfailed`. Every unit
of the delta is accounted for in the commits; none of it is a test relaxed to
go green.

**Gate 2 (DIRECTION) passed on all three fixes** — `labeling-v2.csv` regenerates
byte-identical and `labels-v2.csv` md5 is unchanged at `6215b526…d171f`, so
**zero gold labels were touched**. Read that precisely: byte-identical means
none of the 52 rows carries the shapes these fixes touch, so **A=0.320 bounds
none of tonight's work.** It is not evidence of no new Error-A.

## 2. NOT DONE

- **J-33** — an UNRECOGNISED citation marker still certifies. Analysed, not
  patched, reasons in D-44. Next command:
  `uv run pytest tests/red_team_moat/test_moat_j33_unrecognised_citation_open.py -q`
  (6 strict xfails standing).
- **J-30 MiniCheck** — NOT retried. Two prior failures of the same terminal
  class (network), and my own circuit-breaker rule forbids retrying an
  environment failure without changing the environment. Nothing changed.
- **J-32** — `content_sha256` not recomputed. Ceiling named in `load_store`.

## 3. DENIED

Nothing was denied by a permission boundary tonight.

## 4. ONE-WAY DOORS QUEUED — for your approval

```
# merge the night's work (I opened no PR against main; nothing is merged)
gh pr create --base agent-assure-calibration-run \
             --head provenance-fix-2026-10-01
```

## 5. UNKNOWNS

- **Why the suite went from 238s to 12s.** Collected counts reconcile exactly
  and no tests vanished, and the slowest single test is 1.02s, so the 12s is
  internally consistent. The most likely cause is CPU contention during the
  early runs — I had up to three concurrent pytest processes and another
  session was active on the machine. **Probable, not proven.**
- **The true Error-A cost of J-27.** Bounded by controls, unmeasurable on the
  current corpus.
- Whether the four markers refused "by accident" (`[S99.]`, `[S-99]`,
  `[S99, S100]`, `[Source:acme-report]`) stay refused once argument extraction
  improves. They are pinned as controls for exactly this reason.

## 6. BUDGET

Measure: **NEW TOKENS = output + cache_creation**, derived from the session
JSONL by the ADR-044 clause-4 command, not from my own summary. Cache READS are
excluded and are two orders of magnitude larger — quoting them would inflate the
figure ~35x.

| source | new tokens |
|---|---|
| main loop (432 turns) | 1.61M |
| solo gate on J-25 | 0.14M |
| round 10, three adversaries | 0.45M |
| round 11, two adversaries | see close |
| **total** | **~2.2M + round 11** |

**Sanctioned 8M, ceiling 9.6M. Consumed roughly a quarter.** The night ended on
**diff zero**, not on budget — the committed queue completed with hours and most
of the budget unspent, which is worth noting against the estimate: I projected
~7M for the committed set and it cost about a third of that. The overrun was in
the opposite direction from the usual one, and the reason is that three of the
four jobs were small diffs whose cost was dominated by ADVERSARIAL REVIEW, not
by implementation.

## 7. WITHDRAWALS

1. **"No fabricated citation can certify PASS on ANY claim kind"** (b8d4584).
   FALSE, refuted the same night by the solo gate, reproduced by me. D-42.
2. **"This was the only substring-based verdict-path guard in the suite."**
   FALSE. The three-kind search found D-34's within the minute. D-41.
3. **"The relational half of the gate's finding does not reproduce."** FALSE —
   my probe put the marker AFTER the claim; position was load-bearing.

All three are the same error: **a confident general claim drawn from a check
narrower than the claim.** It is the third consecutive session in which that is
the headline, which is itself the finding.

## 8. FRAMEWORKS

- **Inversion** — decided J-27's whole design. Stripping removes text from the
  denominator, so stripping too MUCH is the fail-OPEN direction; the scanner may
  over-detect code and must never under-detect it.
- **Via negativa / Occam** — rejected adding a CommonMark parser. What was
  needed is a generous code DETECTOR, not a correct renderer.
- **FMEA detectability** — named the sibling every time: the null case for
  J-25, the Error-A for J-27, and the silenced r8 tripwires for J-26.
- **Contradiction-as-locator** — the gate and I disagreed on the relational
  finding; the disagreement located a position-dependence neither of us had.
- **Calibration** — corrected the gate's count DOWNWARD from 13 to the 4 I
  could reproduce. The register carries what I measured, not what I was handed.
- **Chesterton's Fence** — preserved the retired file's verbatim reproduction.
- **Name the CEILING** — J-32 (sha), and the AST guard's docstring residue.
- **Critical path** — J-24 does NOT gate J-25/26/27, which is why tonight
  happened at all. Entailment layers on provenance; it does not replace it.
| 2026-09-30 22:15 | 2 | **ROUND 10: 13 ERROR-B over three Opus adversaries. J-26 and J-27 BOTH refuted.** The reframe: six of the thirteen are in the **CAPTURE layer** and none is reachable from `ground_check.py` — `Read` is trusted unconditionally (write-then-read laundering → PASS 100.0), no search tool is captured so the absence ledger is attacker-written, and there is no session identity at all. Ten rounds have hardened the wrong constraint. **Also corrected my own evidence:** `build_corpus_v2.py` never calls `load_store`, so the gate-2 "byte-identical corpus" I cited for J-26 was structurally incapable of failing — CR-004 is measured on stores the shipped gate would reject (J-37). | ~0.60M | Theory of Constraints (the bottleneck is capture, not the gate) · Calibration (withdrew a passed-gate claim) · FMEA detectability | 
| 2026-09-30 22:40 | 0 | **Five more fixes, all fail-closed, none claimed closed.** J-28B (block-structure rule replacing J-27's blacklist scanner — all 5 adversary-A shapes now reach the denominator, genuine notes still strip); R10C-03 (a summary may refuse an absence, never certify one — the naive filter would have been fail-OPEN); J-40 (numbers inside RELATIONAL claims are checked); J-37 (corpus fixtures get real tool names + a permanent loader-parity test, 47 stores, proven red); J-39 part (word-boundary matching — "AI drives mass layoffs" was GROUNDED where the only "ai" was inside "said"). **J-40 MASKED three J-33 tripwires** via a digit leak; pinned as controls with the masking explained rather than converted — third silent-tripwire incident tonight, now a standing rule in D-46. Suite 628 → 662. Corpus byte-identical throughout. **Round 11 dispatched against all of tonight's unvalidated fixes.** | ~0.45M | Inversion (fail-open direction on the absence filter) · Via negativa (no CommonMark dependency) · Chesterton's Fence · Name the CEILING · Asymmetry of error cost |
| 2026-09-30 22:15 | **0** | **§B DIFF IS ZERO.** Re-derived from code, not from the register: tree clean, 14 commits since `b4d4e39`, fresh run 662 passed / 2 skipped / 55 xfailed. All four committed rows are BUILT (J-25, J-26, J-27 → J-28B, J-29 round 10) or OWNED BY A NAMED HUMAN (J-35/36/38 capture layer → Sai; J-33 + J-31 package → Sai; J-37 CR validity → Sai). **§E breaker does NOT fire — there is in-flight growth** (round 11, dispatched under J-34 because every fix tonight is unvalidated). **Decision: start nothing new.** Close what was opened — record round 11 — then disarm and write the morning report. Continuing to invent work past the committed set at 03:43 unsupervised is the scope creep the §0 handshake exists to bound; the ceiling is a constraint Sai set, so honouring it IS the decision, not a stall. | ~0.02M | Close-after-open (finish round 11, start nothing) · Degradation under constraint (stop STARTING, spend the rest finishing and reporting) · Reversibility (no one-way doors; nothing merged) |
