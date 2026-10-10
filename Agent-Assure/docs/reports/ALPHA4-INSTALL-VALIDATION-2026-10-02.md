# α4 — install validation in an unrelated repo. FIRST TIME EVER RUN.

`ALPHA-READINESS-PLAN.md` phase α4 has required this since July 2026 and every
checkbox was empty. Eleven red-team rounds, 700+ tests, five calibration records,
and **no evidence anyone could install Agent-Assure outside its own repo and get
a verdict.** That was the real launch risk, not the moat.

## Method

Reversible and isolated by construction — nothing live was touched:

```
git init  /tmp/.../stranger-repo                  # an unrelated project
rsync -a --exclude .venv --exclude __pycache__ \
      Agent-Assure/  stranger-repo/agent-assure/  # a fresh copy, no venv
cd stranger-repo/agent-assure && bash install.sh
```

`install.sh` was READ before being run (it is Escalation #4, so it was not
edited): it `cd`s to its own directory, runs `uv sync`, verifies imports, prints
instructions. **No writes outside that directory** — the `curl` line is
error-message text, not an executed command.

**NOT done, and it is the honest gap:** registering the plugin and its PostToolUse
hook into a live Claude Code config. That is hook registration — Escalation #4 —
so the hook was exercised by feeding it a real-shaped PostToolUse event on stdin
instead of by a live session. **A live session remains unvalidated and is Sai's.**

## Results — the full stranger journey

| Step | Command | Result |
|---|---|---|
| 1 | `bash install.sh` | **exit 0** — `.venv` provisioned, `engine + hook + deps: OK` |
| 2 | gate on `demo/draft-grounded.md` | **exit 0**, PASS, score 100.0, 3 claims |
| 3 | gate on `demo/draft-fabricated.md` | **exit 1**, FAIL, 50.0, appendix 2, `UNVERIFIED_CITATION` + `UNVERIFIED_NUMBER` |
| 4 | capture hook fed a `Read` event | **exit 0** — wrote `S1`, `tool: Read`, `session_id: 'sess-STRANGER'`, `verbatim` |
| 5 | gate on a draft citing that captured `[S1]`, `--session-id sess-STRANGER` | **exit 0**, PASS, GROUNDED |
| 6 | same store, `--session-id sess-LATER` | **exit 1** — refused, naming the foreign session |
| 7 | fabricated `[S7]` added to the stranger's draft | **exit 1**, FAIL, `UNVERIFIED_CITATION` |

**Steps 4-6 are the first end-to-end proof of J-38 outside unit tests:** the hook
records a session id into a real store, and the gate refuses that store to a
different session.

## Friction list

**F1 — FIXED.** The first command the installer prints points at
`.assure/evidence-store.jsonl`, which does not exist on a fresh install because
no research has happened yet. A new user's very first command produced a raw
`FileNotFoundError` traceback. `load_store` now raises with the cause and two
remedies; pinned by a test. Still an exception, still exit 1 — loud, not silent.

**F2 — OPEN (J-49).** `install.sh` never mentions `--session-id`, so a user has
no way to discover that session scoping exists. Not fixed here: `install.sh` is
Escalation #4.

**F3 — OPEN (J-50).** A refused store exits 1 with a Python traceback rather than
a one-line message. Consistent with how every other store error behaves, so it
was left alone rather than special-cased — but a traceback is the wrong register
for an expected condition ("you reused a store from an earlier session").

**F4 — OPEN (J-51).** Nothing in the install output tells a user how to obtain
the session id that `--session-id` wants.

## Verdict

**The engine, the hook and the CLI work from a clean install in an unrelated
repo.** What is unproven is the Claude Code plugin path: `claude --plugin-dir`,
the marketplace entry, and the hook firing from a real session. Every one of
those needs hook registration, and that is Sai's.
