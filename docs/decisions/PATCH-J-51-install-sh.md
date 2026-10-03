# PATCH FOR REVIEW — J-51, `install.sh` session-id text

**Owner: Sai.** `install.sh` is Escalation #4 (installers write into user repos),
so this is a patch for you to apply or reject, not an edit I made.

**What is missing (α4 frictions F2 and F4):** `install.sh` never mentions
`--session-id`, and nothing tells a user where a session id comes from.

**Apply near the end of `install.sh`, in the block that prints the first
commands to run:**

```sh
echo ""
echo "Session scoping (optional, recommended for audit work):"
echo "  The store is append-only and is never rotated, so by default the gate"
echo "  scores against every source it has ever captured. To require that"
echo "  sources were retrieved THIS session, pass --session-id:"
echo ""
echo "    uv run python scripts/ground_check.py --draft DRAFT.md \\"
echo "        --store .assure/evidence-store.jsonl --session-id \"\$CLAUDE_SESSION_ID\""
echo ""
echo "  The id is whatever your session sets in CLAUDE_SESSION_ID; the capture"
echo "  hook writes the same value onto each record. Without the flag the"
echo "  report states plainly that session scope is NOT asserted."
```

**Two things to check before applying**, because I could not verify them from
here and will not guess:

1. **Is `CLAUDE_SESSION_ID` actually the variable name the hook reads?** The
   hook obtains the id from the PostToolUse event, not from the environment, so
   the env var may be named differently or may not exist in a plain shell.
   `grep -rn "session_id" Agent-Assure/scripts/capture_hook.py` settles it. If
   there is no shell-visible variable, change the last paragraph to say the id
   must be taken from the store itself (`head -1 .assure/evidence-store.jsonl |
   jq -r .session_id`) — **do not ship an example that silently expands to an
   empty string.**
2. **An empty `--session-id` now REFUSES** (R15-01, fixed 2026-10-03). That is
   deliberate and it is why point 1 matters: an unset variable would produce
   `--session-id ""`, which raises with a clear message rather than quietly
   asserting session scope it does not have. The error text already explains
   itself, so the failure is loud — but a copy-paste example that always fails
   is still a bad first experience.
