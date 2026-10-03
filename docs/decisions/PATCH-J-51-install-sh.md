# PATCH FOR REVIEW — J-51, `install.sh` session-id text

**Owner: Sai.** `install.sh` is Escalation #4 (installers write into user
repos). **Say GO and I apply this exactly as written** — it needs your GO, not
your hands.

**What is missing (α4 frictions F2 and F4):** `install.sh` never mentions
`--session-id`, and nothing tells a user where a session id comes from.

## Both unknowns from the first draft are resolved — and that draft was WRONG

Measured 2026-10-03, not assumed:

1. **There is no shell-visible session-id variable.** `capture_hook.py` takes
   the id from `event["session_id"]` in the PostToolUse payload
   (`_event_session_id`, line 62). The only environment variable either capture
   file reads is `ASSURE_EVIDENCE_STORE`. My first draft suggested
   `--session-id "$CLAUDE_SESSION_ID"` — that expands to an empty string.
2. **An empty `--session-id` REFUSES** (R15-01, fixed 2026-10-03). So the first
   draft would have shipped a copy-paste example that always fails.
3. **The shipped `demo/evidence-store.jsonl` DOES carry `session_id` — and every
   value is `""`.** So the demo store cannot be used with `--session-id` at all;
   it refuses, correctly, because those records carry no session attribution.
   (My own first check reported the field as absent. It was not: a hook had
   blocked the command and I read my shell fallback message as the result.)

## Apply near the end of `install.sh`, in the block printing the first commands

```sh
echo ""
echo "Session scoping (optional, recommended for audit work):"
echo "  The store is append-only and never rotated, so by default the gate"
echo "  scores against every source it has ever captured. To require that the"
echo "  sources came from THIS session, pass --session-id."
echo ""
echo "  The capture hook writes the session id onto each record, so read it"
echo "  back from the store — there is no shell variable for it:"
echo ""
echo "    SID=\$(uv run python3 -c \"import json;print(json.loads(open('.assure/evidence-store.jsonl').readline()).get('session_id',''))\")"
echo "    uv run python scripts/ground_check.py --draft DRAFT.md \\"
echo "        --store .assure/evidence-store.jsonl --session-id \"\$SID\""
echo ""
echo "  Without the flag the report says plainly that session scope is NOT"
echo "  asserted. An empty --session-id is REFUSED rather than ignored, so a"
echo "  store whose records carry no session id cannot be scoped - including"
echo "  the shipped demo store."
```

## Two judgement calls left to you, both one word

- **`.get('session_id','')` vs `['session_id']`.** As written it degrades to an
  empty id and lets the gate's own R15-01 message do the explaining. The strict
  form raises a Python `KeyError` instead, which is louder but uglier. I chose
  the polite one because the gate's error text is already written and good.
- **Python rather than `jq`.** `jq` is installed on this machine but is not a
  safe assumption on a user's; `uv run python3` is already a hard requirement of
  the tool. Swap it if you prefer the shorter line.
