# Agent-Assure — Demo Readiness Plan

**Author:** Fable 5, 2026-07-07 (handoff artifact). **Executor:** Sonnet 5 (all tasks mechanical against this spec); Opus only if step D4 finds a defect. **Time budget:** ~1–2 hours total.

**Demo definition:** a ≤10-minute, fully-offline, zero-surprise walkthrough that lands ONE message: *an AI draft with a fabricated citation cannot talk its way past this gate, because no LLM judges grounding — the verdict is a mechanical fact about the evidence store.* Everything in the demo serves that moment.

**What already exists (do not rebuild):** `Agent-Assure/demo/` — `evidence-store.jsonl`, `build_store.py`, `show_report.py`, `draft-grounded.md`, `draft-fabricated.md`, README. The demo is built; this plan makes it *reliable in front of a human*.

---

## D1 — Freeze and verify the happy path (30 min)

- [ ] From `Agent-Assure/`: run the demo exactly as its README says, on a clean checkout, network disabled if feasible. Both drafts:
  - `draft-grounded.md` → gate **PASS**
  - `draft-fabricated.md` → gate **FAIL** with `UNVERIFIED_CITATION` on the fabricated source visible in the per-claim output
- [ ] Save both full transcripts to `demo/expected/` (new dir) as golden outputs.
- [ ] Add `tests/test_demo_golden.py`: runs both demo drafts, asserts gate verdicts and the fabricated source-id appears in the failure. **Prove it red first** by pointing it at a wrong expectation, then fix. This makes demo breakage a test failure, not a live-audience discovery.

**Exit:** golden test green in `uv run pytest`; transcripts committed.

## D2 — The demo script (45 min)

Write `demo/DEMO-SCRIPT.md` — the exact spoken/typed runbook. Structure (do not improvise a different one):

1. **Cold open (1 min):** show `draft-fabricated.md` — it *looks* impeccable, citations and all. Ask: "would you catch the fake?"
2. **The store (2 min):** open `evidence-store.jsonl`, show one record — verbatim text, sha256, provenance, `full_text_source`. Point out `haiku_summary` handling: summarized evidence is refused for certification.
3. **The moment (2 min):** run `/assure-verify draft-fabricated.md` (or the CLI). FAIL. Show the per-claim verdict naming the fabricated source. Say the moat line: *no LLM judged this — it's a mechanical fact; the draft cannot negotiate.*
4. **Contrast (1 min):** same command on `draft-grounded.md` → PASS.
5. **Honesty beat (1 min):** show CR-001 — thresholds calibrated at n=12, held-out Error-B=0.14, provisional. Audiences trust the product MORE when the calibration honesty is shown, and it pre-empts the "how do you know your thresholds are right" question.
6. **Close (1 min):** capture hook runs automatically during research — the store builds itself; roadmap = NLI paraphrase tier + wider calibration (one sentence, no promises with dates).

Script rules: every command in the script is copy-pasteable and appears in the golden test; no command in the demo that isn't in D1's frozen path.

## D3 — Failure-proofing (20 min)

- [ ] **Offline guarantee:** demo must run with Wi-Fi off. Verify; if anything fetches, fix or fence it.
- [ ] **Fresh-machine check:** `bash install.sh` in a temp clone → demo runs. Record Python/uv version assumptions in the script header.
- [ ] **Fallback artifact:** the D1 golden transcripts double as the break-glass demo — if live execution fails, walk the saved transcript. Note this in the script.
- [ ] **Reset command:** one line in the script that restores pristine demo state (`git checkout -- demo/ && rm -f grounding-report.yaml`), so back-to-back demos don't contaminate.

## D4 — Dry run + sign-off (15 min)

- [ ] Execute DEMO-SCRIPT.md top to bottom, timed. Target ≤10 min including talking beats.
- [ ] Any deviation between live output and golden transcript = defect → escalate to Opus, do not patch the transcript.
- [ ] Logbook entry with timing + evidence; mark demo READY.

**Demo-ready criteria (all checkable):** golden test green; script exists with only frozen-path commands; offline run verified; reset command works; one timed dry run ≤10 min logged.
