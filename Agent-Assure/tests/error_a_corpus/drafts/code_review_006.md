## Test results

- The error message now names the file that failed [S1].
- Variable names in `parse_header` follow the project style [S1].
- The helper is safe to call twice [S1].
- It does not handle connection resets [S1].
- The retry logic handles timeouts [S1].
- Run time dropped from 19 seconds to 4 seconds in the benchmark [S1].
- Coverage for the auth helper is now 83% [S1].
- Pavel commented that the old loop "is not thread safe" [S1].
- The planned rewrite of `parse_header` never landed in this pull request [S1].
- The pull request touches 4 files [S1].
- The change adds 19 tests for the new branch [S1].

## Snippet

The call in `parse_header` passes `delete=False` on purpose [S1]. A comment above it explains why [S1].

```python
def parse_header(conn, rows):
    conn.execute(rows, delete=False)
```
