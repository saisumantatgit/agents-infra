---
name: assure-verify
description: Verify that every factual claim in a draft is grounded in a source actually retrieved this session. Runs the deterministic Agent-Assure grounding engine (no LLM judgment) against the captured evidence store and returns a PASS / NEEDS_WORK / FAIL gate.
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

If no draft argument was given, ask the user: "Which draft should I verify? Provide a file path — the evidence store captured during this session's research is used automatically."

Pass all arguments through to the skill:
- The draft file path as DRAFT
- `--store` path if provided (else the default `.assure/evidence-store.jsonl`)
- `--threshold` value if provided (else 90)

**The verdict comes from the engine, not from your reading.** Do not judge grounding yourself — run the script and report exactly what it returns. If you believe the engine is wrong, that is a bug to file, not a verdict to adjust.
