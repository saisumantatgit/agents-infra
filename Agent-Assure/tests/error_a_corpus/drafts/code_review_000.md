## Suggested changes

- The new loop runs once per record instead of once per field [S1].
- Logging was moved to the top of the scheduler [S1].
- `render_row` validates its arguments [S1].
- It does not handle connection resets [S1].
- The retry logic handles timeouts [S1].
- Greta commented that the old loop "is not thread safe" [S1].
- The planned rewrite of `render_row` never landed in this pull request [S1].
- Run time dropped from 42 seconds to 7 seconds in the benchmark [S1].
- The new code removes 5555 lines and adds 42 [S1].
- The change adds 42 tests for the new branch [S1].
- The `render_row` function now returns early when the input is empty [S1].

## Snippet

The call in `render_row` passes `check_same_thread=False` on purpose [S1]. A comment above it explains why [S1].

```python
def render_row(conn, rows):
    conn.execute(rows, check_same_thread=False)
```
