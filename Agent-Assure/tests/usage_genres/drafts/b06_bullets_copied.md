# CLI notes

- Exit codes: `0` = gate PASS, `1` = NEEDS_WORK or FAIL [S1].
- With `--json`: prints the full report as JSON to stdout (no file written) [S1].
- The plugin ships one command (`/assure-verify`), one skill (`verify-grounding`), and the capture hook [S1].
- One JSON object per line [S1].
- Blank lines are skipped [S1].
- All text fields are NFKC-normalized before matching [S1].
