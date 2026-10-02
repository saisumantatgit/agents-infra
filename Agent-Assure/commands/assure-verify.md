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

**The verdict comes from the engine, not from your reading.** Do not judge grounding yourself — run the script and report exactly what it returns. If you believe the engine is wrong, that is a bug to file, not a verdict to adjust.
