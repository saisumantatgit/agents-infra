# Grounding Failure Types Reference

Every verdict the Agent-Assure engine assigns to a claim, what it catches, and
how to remediate. Verdicts are produced **mechanically** by `scripts/ground_check.py`
— there is no LLM in the grounding decision. A claim's verdict is a fact about
the evidence store, not an opinion.

The store is per-session: grounding is checked against the sources the capture
hook recorded *this session*, in `.assure/evidence-store.jsonl`.

---

## Passing verdicts

### GROUNDED

**Gate effect:** counts toward the numerator (supported).
**Meaning:** the claim is supported by a `verbatim` source — either a contiguous
≥8-token span appears in the source (T1), or content-word F1 against the best
±2-sentence window is ≥ 0.65 with all numerics present (T2). NON_CLAIM
statements are also reported GROUNDED but are excluded from the denominator.
**Why it matters:** this is the only state that certifies "an AI said it *and*
we can point to where it came from, retrieved this session."

### ABSENCE_SUPPORTED

**Gate effect:** counts toward the numerator (supported).
**Meaning:** an absence claim ("no X exists", "there is no evidence of Y") backed
by ≥2 distinct queries in the store's `query_provenance` that target the subject.
**Why it matters:** "not found" is only trustworthy if you know the search was
actually run. Two distinct targeted queries is the mechanical floor for that.

---

## Failing verdicts

### UNVERIFIED_CITATION  — the fabricated-citation catch

**Gate effect:** HARD override — caps the gate at NEEDS_WORK regardless of score.
**Meaning:** the claim carries a citation marker (e.g. `[S9]`) whose `source_id`
is **absent from the evidence store**. The source was never retrieved this
session — the citation is fabricated (or points outside the session).
**Fix:** retrieve the source so the hook captures it and re-cite, or repair the
citation to a source that IS in the store, or remove the claim.
**Why it matters:** this is the exact failure Agent-Assure exists to catch — the
11–57% production hallucination rate for deep-research citations. A fabricated
citation looks identical to a real one to a human reader; only a mechanical
store-membership check distinguishes them. This verdict is why the gate is
never a rubber stamp.

### UNGROUNDED

**Gate effect:** violation (never counts toward the numerator).
**Meaning:** verbatim sources exist and are cited, but neither T1 (verbatim span)
nor T2 (lexical-F1 window) finds support for the claim in them.
**Fix:** tighten the claim to what the source actually says, cite the right
source, or remove the claim. Often the claim over-reaches what the source
supports.
**Why it matters:** a citation that exists but does not actually support the
sentence is a subtler hallucination than a fabricated id — the source is real
but does not say what the claim asserts.

### UNCITED

**Gate effect:** violation.
**Meaning:** a factual claim with no citation marker at all.
**Fix:** add a citation to the retrieved source that supports it.
**Why it matters:** an uncited factual claim is indistinguishable from an
assertion the model invented. The store cannot verify what the draft never
points at.

### UNVERIFIED_NUMBER

**Gate effect:** violation.
**Meaning:** a NUMERIC claim whose number does not match any source. Both value
**and** unit are checked — `25%` ≠ bare `25`; `$4M` ≡ `$4,000,000`.
**Fix:** correct the number to the source value, or cite the source that
actually carries it.
**Why it matters:** invented statistics are the most common and most
confident-sounding form of AI fabrication. Value-and-unit matching stops a claim
from borrowing a source's digits while changing their meaning.

### UNVERIFIED_ABSENCE

**Gate effect:** violation.
**Meaning:** an absence claim backed by fewer than 2 distinct queries mentioning
the subject.
**Fix:** run (and let the hook capture) the searches that would substantiate the
absence, or soften the claim.
**Why it matters:** "no X exists" after a single glance is not evidence of
absence — it is absence of evidence. The two-query floor forces the difference.

### UNVERIFIED_RELATION

**Gate effect:** violation.
**Meaning:** a relational claim ("A causes B", "X outperforms Y") lacking 2
distinct verbatim sources — one supporting each side of the relation.
**Fix:** cite a distinct retrieved source for each side, or restate as a
single-source claim.
**Why it matters:** relations synthesize two facts. If both sides trace to the
same source (or to none), the relation may be the model's inference rather than a
grounded finding.

### UNGROUNDABLE

**Gate effect:** violation.
**Meaning:** every cited source has `full_text_source != "verbatim"` (e.g.
`haiku_summary`), or the source text is empty. There is no verbatim text to run
the grounding tiers against.
**Fix:** re-retrieve the source with a tool that captures full text verbatim
(Exa fetch or a raw Read), not a summarizing tool (native WebFetch returns a
Haiku summary).
**Why it matters:** grounding against a summary would be grounding against a
second model's paraphrase — which can itself hallucinate. The gate refuses to
certify against non-verbatim text rather than pretend it can.

---

## NON_CLAIM (excluded, not a failure)

Headers, questions, imperatives, and pure opinion are classified NON_CLAIM and
excluded from the scored denominator. They are neither grounded nor violations —
there is nothing factual to check. (A verbless line that nonetheless carries a
number or a citation is treated as a real claim, not a NON_CLAIM — this closes
the anti-gaming hole where a fabricated statistic could hide behind a
sentence-fragment grammar.)
