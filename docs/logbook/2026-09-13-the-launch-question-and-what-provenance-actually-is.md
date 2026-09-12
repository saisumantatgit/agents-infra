# 2026-09-13 — the launch question, and what provenance actually is

Session `d2b27b1f`, continuing past midnight 2026-09-12 → 13. Sai asked for the
shortest, surest way to launch, then went to bed with a cron and a 01:30 hard
stop.

## What

1. **Launch analysis.** Recommended splitting Agent-Assure into PROVENANCE (is
   every citation a source actually retrieved, verbatim?) and ENTAILMENT (does
   the source support the claim?), and shipping provenance.
2. **Deep research, two reports** (`docs/research/`): STORM's genesis and how
   STORM verifies citations; and whether an LLM pass after the gate fixes
   entailment.
3. **Offline diagnostic** (`docs/research/diagnostic/`): ran Vectara HHEM-2.1-Open
   over 63 pairs — red-team attacks, honest mirrors, the 38 entailment-shaped
   gold rows. MiniCheck download failed twice on the network; stopped.
4. **Found and read the founding design spec** — in the HQ repo, not this one.
5. **Spec §7.5 audit** — EvidenceStore completeness, the spec's named #1 risk.
6. **Red-team round 9, provenance only.**

## Why

Sai: "we have taken far too long to build agent assure." The question was not
how to go faster but which half was real.

## Done — the findings, in the order they changed the plan

**STORM verifies its citations with an LLM (Mistral-7B), recall 84.8% /
precision 85.2%,** and its authors name "red herrings" — true sources arranged
to imply what none says — as their dominant failure. That is exactly q25. Two
months of regex went at the problem the field's flagship system calls unsolved.

**Nothing measured clears 80% on the standard grounding benchmark.** GPT-4
75.3%; a 770M local checker 74.7% at 1/446th the cost; temperature 0 is not
deterministic; prompt injection against LLM judges succeeds 90.8%.

**Diagnostic: HHEM catches 3 of 17 open attacks (0.868 on ordinary rows).
Union with the gate: +0.** Every claim it catches the gate already caught. It is
RIGHT exactly where the gate is wrong — the honest paraphrases the gate
false-alarms on — i.e. only in the lifting-flags direction the moat forbids.
Tuning its threshold on the corpus improves ordinary rows and makes attacks
worse.

**The founding spec's identity sentence is provenance, verbatim:** "every claim
… can be mechanically traced to a source that was actually retrieved this
session." It already forbade a generative judge and specified a fail-closed NLI
tier — which the diagnostic now shows adds nothing as specified.

**§7.5: an incomplete store is safe for ordinary claims and FAIL-OPEN for
absence claims.** q13 certifies PASS 100.0 on the captured store and FAILs once
one uncaptured WebSearch result is added. Uncaptured today: WebSearch, Exa/DDG
search, Bash, Grep/Glob, most MCP readers; subagent returns UNKNOWN. Auto mode
instructs file reads via Bash, which the hook never sees.

**Round 9: provenance lost.** 2 ERROR-B — a fabricated citation certifies PASS
100.0 on relational and absence claims, because `ground()` dispatches those
kinds before the unresolved-citation check. 3 new denominator escapes; 5 silent
store repairs (a duplicate `source_id` launders a summary to verbatim by line
order). The summary-never-certified promise held.

| | |
|---|---|
| Suite | 563 → **564 passed / 2 skipped / 60 xfailed** |
| Corpus | byte-identical; 52 labels gold, zero stale; no CR due |
| Register | D-37 |
| Code changed in the gate | **none** — diagnostics, reports and tripwires only |

## Decisions

- **The product call is Sai's and was not presumed.** Overnight work was
  restricted to what is useful under either answer.
- **No moat fix tonight.** R9's fix (unresolved-citation check ahead of the
  dispatch) is small and fail-closed; the last two same-night moat patches each
  closed their fixture and not their class.
- **§7.5 remedies not applied** — all touch hook registration, Escalation #4.
- **Close moved 01:21 → 01:30 via `/sg close`**, per Sai. Intermediate cron
  ticks deleted once their items were done, so none could start the close early.

## Agents

| role | model | count | outcome |
|---|---|---|---|
| research — LLM judges | Opus | 1 | report + 4 evidence files |
| research — STORM genesis | Sonnet | 1 | report; **its "spec does not exist" was wrong** |
| round-9 adversary | Opus | 2 | 2 ERROR-B, 3 escapes, 5 silent repairs, ~148 runs |

## Withdrawals

1. **"The founding design spec does not exist."** Said twice. It is in the HQ
   repo; the search covered only this repo and I reported its negative as
   universal. A negative result is only as wide as where you looked.
2. **"Provenance never lost a red-team round and cannot lose one."** It had
   never been attacked on its own. The first round scoped to it found two
   wrongful PASSes. I mistook a property of the logic (set membership is closed)
   for a property of the code (whether every path performs the check).
3. **A first §7.5 demonstration did not reproduce** — the gate refused both
   stores for an unrelated reason. Rebuilt on a certified row before recording.

## Reflection

The night's two biggest errors were the same error. "The spec doesn't exist"
and "provenance cannot lose" are both a confident universal drawn from a check
that covered less ground than the claim — one directory, one mental model of the
code. What makes it worth writing down is that each was *locally* well-founded:
the search really did find nothing; set membership really is a closed class. The
defect was the scope of the conclusion, never the observation. And the product
consequence runs the other way from the embarrassment: the spec turned out to
say provenance was the point all along, and round 9 turned "provenance is done"
into a four-item fix list — which is a far better thing to launch from than a
belief.

## Next

**Sai's call first:** ship provenance-only, or fund entailment. Evidence tonight
strengthens provenance on every axis except one — it is not yet true.

If provenance: the fix list, all fail-closed —
1. unresolved-citation check in `ground()` **before** the kind dispatch (R9P1-01/02);
2. `load_store` raises on duplicate normalised ids, duplicate keys, wrong types,
   tool/`full_text_source` mismatch (R9P2-01…04);
3. real CommonMark code-block detection in the comment stripper, or stop
   stripping (R8B-01/02, R9P2-05/06/07);
4. §7.5 — absence claims vs incomplete store (Sai: hook registration);
then round 10, provenance only.
