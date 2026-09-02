# ADR-006 — Demote T2 from sufficient-for-GROUNDED; retire lex_tau

**Status:** Accepted · **Date:** 2026-09-02 · **Decider:** Sai
**Closes:** OI-MOAT-21, OI-T2-01 · **Supersedes:** CR-002's operating point
**Executed by:** CR-003 · **Red-teamed by:** `tests/red_team_moat/test_moat_quote_mining.py`

## Context

`ground()` returned GROUNDED on `t1_verbatim(...) or t2_lexical(...)`. T2 is a
content-word F1 between the claim and a source window — a bag of words, scored
as a ratio whose denominator is the claim's own length.

Two measurements ended the question:

1. **Matched pairs.** A true claim and a false one can be the SAME one-token
   delta against the same source, and score an *identical* `t2_f1`. Five pairs,
   five ties (`achieves`/`delivers` vs `mapping`/`logistics`). No threshold
   orders them, in either direction, at any precision.
2. **Reordering.** A bag has no word order, so reciting a source's whole
   vocabulary in a FALSE order scored `f1=1.000` (round 5).

A tier that cannot distinguish a claim from its inversion, or from its
falsification, is not measuring support. It is measuring vocabulary reuse.

## Decision

**T2 no longer decides any verdict.** `ground()` certifies on T1 alone.
`lex_tau` is retired: `--lex-tau` raises rather than silently doing nothing.
`t2_f1` is still emitted as a diagnostic — "high overlap, no verbatim span" is
the actionable signal behind an UNGROUNDED verdict — and `tier_sensitive` is now
always False.

**T1 gains an exact-containment path.** If the *whole claim* is a contiguous
verbatim span of a cited source, it grounds regardless of length. This is not a
relaxation of the 8-token floor but a different property: when the span IS the
claim there is no residual to assemble and no ratio to game, and an attacker
cannot fabricate by exact quotation without giving up the fabrication.

## Alternatives considered

**Coverage repair** — require the cited source to contain every claim content
token. Measured *better* (Error-A 0.240 vs 0.320) and was the commissioned
adversarial reviewer's recommendation. **Rejected on trace:** it rejects
`achieves`/`delivers` and `mapping`/`logistics` identically — one novel token
each — so it is a blanket ban on novel tokens, not a discriminator. And it
leaves REORDERING wide open, since a reordering introduces no new token
(verified by mutation: the round-5 tripwire still XFAILs under it). Its better
score was an artefact of a corpus holding zero honest synonym rows.

**Wait for T3.** Leaves five demonstrated fabrications passing for the weeks T3
takes. Error-B is unrecoverable; Error-A is not.

## Consequences

Error-A rises 0.200 → **0.320**; Error-B falls 0.111 → **0.074** (CR-003).
Honest paraphrase now reads UNGROUNDED. This is recorded per instance as strict
xfails in `tests/honest_drafts/` and `test_moat_oi_moat_21.py` so the cost stays
countable rather than becoming folklore.

**T3/NLI (ADR-004) is now load-bearing, not optional.** It is the only mechanism
that can separate a synonym substitution from an argument substitution, and it
is what buys the 0.320 back. Note before building it: the Phase-2b plan's claim
that T3 "can never CREATE a PASS" is **false** — its one permitted effect
(UNGROUNDED → GROUNDED) empties the retained appendix, and ADR-005 then yields
PASS. That sentence must be corrected before any T3 code.

**New surface accepted:** exact containment permits quote-mining — lifting
"Redis is slow" out of "Critics claim Redis is slow". Guarded by
`_span_is_hedged` (attribution / denial / conditional tokens preceding the span),
mutation-verified: all three attacks PASS without the guard.

## Load-bearing assumption

**That honest drafts quote more often than they paraphrase.** If real writing
paraphrases constantly, 0.320 is unusable and the gate gets switched off — and a
tool switched off has unbounded Error-B, which is the failure this ADR was
written to prevent. Nobody has measured this on real prose. The 52 calibration
claims were authored for calibration; they are not a sample of user drafts.
Measuring it (cpc-book, J-13) is the check that could overturn this decision.
