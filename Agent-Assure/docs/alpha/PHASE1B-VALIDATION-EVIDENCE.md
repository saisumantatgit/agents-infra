# Phase-1b Live-Validation Gate — Evidence Dossier

**Purpose:** Assemble the evidence Sai needs to decide whether the 2026-07-03 live
capture run closes the Phase-1b human gate ("capture hook proven working
end-to-end on a real Claude Code session"). This dossier **does not decide** — it
lays out for and against and states what would definitively close the gate.

**Prepared:** 2026-07-11 (evidence-gathering agent). Scope: `Agent-Assure/`.

---

## The gate, precisely

Phase 1 (capture hook + deterministic gate) is code-complete. The one hold before
PR #2 merge is a **live-validation gate**: the `PostToolUse` capture hook must be
proven to fire on a *real* Claude Code session and write correct records for every
supported retrieval tool (Exa `web_fetch_exa`, `Read`, native `WebFetch`, DDG
`fetch_content`) — not merely against synthetic fixtures. It is framed as a
**human gate**: `docs/PHASE1B-RESUMPTION.md:5` — "Merge decision is Sai's."

---

## Evidence FOR the gate being satisfied

1. **A dated live-validation commit exists with specific, non-inventable findings.**
   `bce055b` (author date **Fri Jul 3 2026**, Co-Authored Fable 5), subject
   "live-validation executed — extractor matched to real payload shapes,
   hooks.json relocated." It reports a real headless `claude -p` run with a
   parallel tap hook dumping raw stdin, and every assumed payload shape *except
   DDG* differed from reality and was fixed TDD. Diffstat touches
   `capture_core.py` (148 lines), `capture_hook.py`, and adds
   `tests/test_live_shapes.py` (+255).

2. **The specific deviations are the kind you cannot fabricate without observing
   them** — strong circumstantial proof a real session ran:
   - Exa returns a **top-level** MCP content-block list `[{"type":"text","text":…,"_meta":…}]`, and its `tool_input` uses **plural** `{"urls":[…]}` (`test_live_shapes.py:161-235`).
   - `Read` delivers `{"type":"text","file":{"content":…}}` with **raw** file text and **no** cat-n prefixes; `strip_cat_n_prefix` was removed because it would corrupt TSV content (`test_live_shapes.py:78-96`).
   - Truncation is **inline** (`truncatedByTokenCap:true`), not a `{preview,file_path}` offload — the assumed overflow shape did not exist (`test_live_shapes.py:98-114`).
   - `WebFetch` wraps its summary in `{"result":str,"code","bytes",…}` and stays `haiku_summary` (`test_live_shapes.py:127-152`).

3. **A live-only packaging bug was caught and fixed.** Hooks lived at
   `.claude-plugin/hooks.json` and were **silently ignored** by the plugin loader;
   moved to `hooks/hooks.json` and proven via `claude -p --plugin-dir`
   (`PHASE1B-RESUMPTION.md:26`, confirmed by current `hooks/hooks.json:5-9`
   pointing at `${CLAUDE_PLUGIN_ROOT}/.venv/bin/python`). A synthetic-only run
   could not surface this — it only bites a real plugin-dir load.

4. **The capture→ground loop was closed live end-to-end.** A 5-source store built
   by real sessions: grounded claims → `GROUNDED`, fabricated facts → `UNGROUNDED`,
   fabricated `[S9]` → `UNVERIFIED_CITATION`, gate `FAIL` at 0.0
   (`PHASE1B-RESUMPTION.md:27`).

5. **The live-derived fixtures are green on current code.** `uv run pytest
   tests/test_live_shapes.py` → **9 passed** (run 2026-07-11). The real payload
   shapes are still honored by the shipped extractor.

6. **The resumption doc explicitly declares the gate passed.**
   `PHASE1B-RESUMPTION.md:5,16` — "LIVE-VALIDATION GATE PASSED (2026-07-03)."

---

## Evidence AGAINST / residual doubt

1. **The project's own most-recent authoritative handoff lists this gate as OPEN
   and blocked on Sai.** `docs/logbook/2026-07-08-parallel-execution.md:23`:
   "Phase-1b live-validation gate — confirm whether 2026-07-03 live capture run
   closes it (α0 open question; **do not infer**)." This is the newest logbook
   (logbook is authoritative over memory/docs per session-hygiene rules), and it
   post-dates the resumption doc by 5 days. The two artifacts **conflict**: the
   older RESUMPTION says PASSED; the newer logbook says open, do-not-infer.

2. **The load-bearing raw artifact is absent.** The tap-hook raw payload dumps and
   the live-session `.assure/evidence-store.jsonl` were **never committed**
   (`git log --all` for tap/raw/`.assure` artifacts → none; `.assure/` is
   gitignored at `Agent-Assure/.gitignore:16` and does not exist in the tree).
   What survives is **distilled fixtures + prose testimony**, not the primary,
   re-inspectable capture evidence. The gate's own subject — "the hook wrote
   correct records on a real session" — has no surviving record to inspect.

3. **The evidence is single-source self-attestation.** The commit message, the
   RESUMPTION doc, and the fixture docstring were all authored in the same
   Fable-5 work session that performed the run. No independent witness, no CR/TDR,
   no human-signed confirmation. Under the global **Discontinuity-distrust** rule
   (reports near a session/access boundary are suspect until artifacts are
   verified from evidence), a Fable-window run whose primary artifact is absent is
   exactly the pattern that rule says not to accept on testimony.

4. **The gate is defined as a human sign-off and the human sign-off is not
   recorded.** `PHASE1B-RESUMPTION.md:5,32` leave the merge decision to Sai; PR #2
   was later merged (`b3b6b18`), but no artifact records that Sai independently
   affirmed the *live-validation* specifically (vs. merging the branch on the
   agent's PASS claim).

5. **A known residual is logged as unprobed.** `PHASE1B-RESUMPTION.md:29(i)` —
   harness-level truncation of a HUGE MCP result was never exercised live
   (mitigated by fail-loud on unknown shapes, but untested end-to-end).

---

## What the conflict actually is

Both artifacts are locally honest. The RESUMPTION doc records that the *technical
run executed and passed*; the 07-08 logbook records that the *human gate was never
formally closed by Sai*. "Gate passed" (agent's technical verdict) and "gate open"
(human sign-off outstanding) are not contradictory once you separate execution
from ratification. The unresolved item is **ratification of a run whose raw
evidence is gone**, not whether the code works — the fixtures prove the code
honors real shapes today.

---

## What would DEFINITIVELY close this gate (checklist)

Re-run the hook on a fresh real `claude -p --plugin-dir` session that fetches via
all four tools; commit the resulting `.assure/evidence-store.jsonl` (or a
redacted copy) as a dated artifact; run `ground_check.py` against it showing
GROUNDED/UNGROUNDED/`FAIL`-on-fabrication; then Sai records explicit sign-off in
the logbook + closes the 07-08 open item — one fresh capture artifact + one human
affirmation, because testimony alone (with raw payloads absent) is what left it open.
