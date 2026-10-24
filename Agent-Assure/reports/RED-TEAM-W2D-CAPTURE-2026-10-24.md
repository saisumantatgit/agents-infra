# RED-TEAM W2D — non-exa capture + store loader (2026-10-24)

Branch capture-contract-2026-10-10. Real hook + real gate, no network. Scratch: scratchpad/w2d/.

## W2D-01 — Self-source (J-83) evaded: relative or `~` Read path + partial Read => draft certifies itself, PASS 100.0 | HIGH (Error-B)

Mechanism: `make_record` stores `tool_input["file_path"]` verbatim (capture_core.py `_file_path_from_input`) and ignores both the harness-resolved `tool_response.file.filePath` and the event's `cwd`. `_self_source_ids` (ground_check.py) resolves the stored path against the GATE's cwd (`os.path.exists` / `Path.resolve()`), and `~` is never expanded. When the gate runs from any cwd other than the agent's, the path test misses. The digest backstop only fires on a WHOLE-draft read; a Read with offset/limit (the header line skipped) holds part of the draft, so its digest differs. Both J-83 tests miss.

Reproduction (draft `p2/d.md` = "# Notes" + one claim citing [S1]; Read event `file_path: "d.md"`, offset 3, limit 1, content = the claim line; hook run with cwd=p2; gate run from Agent-Assure/ with absolute --draft, `--session-id sess-A`):

    gate PASS score 100.0 ['GROUNDED', 'GROUNDED']
    exit=0
    -- same gate, run from agent cwd:
    gate FAIL score 0.0
    -- full-read rel (digest backstop):
    gate FAIL score 0.0

Same result with `file_path: "~/draft.md"` (2-claim draft: the claim inside the partial read is GROUNDED, score 50.0 vs 0.0 for the absolute-path control). `--session-id` does not help: the read really happened this session.
Live caveat: Claude Code's Read schema asks for absolute paths; whether the harness passes relative or `~` input through unchanged to `tool_input` is not verified here. `tool_response.file.filePath` is the harness's own path and is available today.
Fix direction: record `file.filePath` (fall back to resolving against `event["cwd"]`, else refuse to set file_path) and store the line range. Optionally treat any Read record whose text is a contiguous substring of the draft as a self-source (fail-closed).
Status: NEW. Sibling: J-83, R19-01/R19-02 (digest and samefile hardening), J-35 (a copy with a partial read is laundering, already registered).

## W2D-02 — Read record does not say it is partial | LOW (meaning drift, no verdict change found)

`file_path` + `text` from an offset/limit Read loads like a whole-file record; `startLine`/`numLines`/`truncatedByTokenCap` are dropped. A reader of the store cannot tell a slice from the file. This is what turns W2D-01's digest test blind. NEW, folded into the W2D-01 fix.

## TRIED AND HELD

- Absolute-path partial Read of the draft: samefile catches it, FAIL 0.0.
- Relative full-draft Read: identity-digest catches it, FAIL 0.0.
- Gate run from the agent's cwd with relative path: caught (FAIL 0.0); W2D-01 needs a cwd difference.
- fcntl lock: 16 concurrent hook processes made 16 lines with 16 unique source_ids.
- Non-str `session_id` (123): recorded "", and `--session-id 123` REFUSED it as `<no session_id>`.
- Not re-tested (known): J-35, J-36, J-38, DDG error text recorded ok.
