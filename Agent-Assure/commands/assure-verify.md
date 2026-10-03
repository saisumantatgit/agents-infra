---
name: assure-verify
description: Verify that every factual claim in a draft can be traced, mechanically, to a source captured in the evidence store. A deterministic engine — no model, no network — REFUSES anything it cannot trace and returns a PASS / NEEDS_WORK / FAIL gate. It checks the draft against what the session READ; it does not judge whether the source is right.
arguments:
  - name: draft
    description: Path to the draft file to verify (markdown or text)
    required: false
  - name: --store
    description: Path to the evidence store JSONL (default .assure/evidence-store.jsonl)
    required: false
  - name: --threshold
    description: Grounding score threshold 0-100 (default 90)
    required: false
---

Invoke the `verify-grounding` skill with the provided arguments.

If no draft argument was given, ask the user: "Which draft should I verify? Provide a file path — the evidence store captured by the hook during this session is used automatically."

Pass all arguments through to the skill:
- The draft file path as DRAFT
- `--store` path if provided (else the default `.assure/evidence-store.jsonl`)
- `--threshold` value if provided (else 90)

**Two drafting rules to pass on if the gate refuses something unexpectedly.**
Citation markers belong inside the sentence, before the final period — a marker
after the period detaches and reads `UNCITED`. And authoring notes must stay on
ONE line: only a same-line `<!-- ... -->` is stripped, so a multi-line comment
block is scored as claims and does not prove anything (J-48). Neither is a bug;
both over-flag rather than under-flag.

**Causal claims are reported, never certified (ADR-007).** "X causes Y" is
grounded only if a cited source contains that claim verbatim — never because two
sources each mention one end of it. Each relational claim carries a
`relation_diagnostic` field; `corroborated_by_two_sources` alongside
`UNGROUNDED` is the normal result for an honest causal claim, and it means the
author must quote a source or soften the claim. Expect a draft of causal prose
to come back mostly UNGROUNDED.

**What PASS means, and what it does not (ADR-008).** PASS means every claim is
**traceable** to text in a source the run was given — it does **not** mean the
source agrees with the claim. A source reading *"we found no evidence that X"*
can satisfy the check for a draft asserting X (round 14, R14-04), because the
gate matches a contiguous verbatim span and the denial can sit outside it. Every
claim therefore carries a `support_diagnostic`; `cited_sentence_may_not_assert_claim`
means **read that sentence yourself**. It is an advisory and nothing is refused
because of it — **it misses about half the denials we
could construct, and since J-79 fires on none of the claims the gate passes in
the n=52 corpus** (recall 7/14 on our denial set; false alarms
0/15, down from 4/15 — a rate on fifteen rows, not a guarantee). **J-79 trades
recall for precision in one shape**: a denial whose hedge word the CLAIM itself
uses is no longer flagged (`…per the vendor` against a claim saying `per
second`). Our 14-vector set contained none of that shape, so it reported the
trade as free; round 17 found it (recall 7/14 on a named denial set, 2026-10-03: it catches
plain negation, prefix denial, attribution, hearsay and conditionals, and misses
a denial in the next sentence, `retracted`, `erroneous`, `lacks`, `absent`,
`zero`, and a denial after a semicolon). Treat it as a prompt to read the source,
never as a clearance. The word "verified" is deliberately absent from this
tool's output: it checks provenance, not truth.

**The verdict comes from the engine, not from your reading.** Do not judge grounding yourself — run the script and report exactly what it returns. If you believe the engine is wrong, that is a bug to file, not a verdict to adjust.
