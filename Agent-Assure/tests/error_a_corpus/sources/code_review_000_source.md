# Review notes: scheduler change

The new loop runs once per record instead of once per field. Logging was moved to the top of the scheduler. Greta split the scheduler into two files.

Comments are grouped by file for easier reading.

It does not check the encoding of the path. `render_row` validates its arguments. It does not handle connection resets. The retry logic handles timeouts.

Greta commented that the old loop "is not thread safe". The planned rewrite of `render_row` never landed in this pull request. Run time dropped from 42 seconds to 7 seconds in the benchmark. The test fixture is made up of 7 small files and one large archive. The new code removes 5555 lines and adds 42.

The change adds 42 tests for the new branch. The `render_row` function now returns early when the input is empty. Variable names in `render_row` follow the project style. The pull request touches 7 files.

Earlier feedback has been addressed.

## Snippet

The call in `render_row` passes `check_same_thread=False` on purpose. A comment above it explains why.

```python
def render_row(conn, rows):
    conn.execute(rows, check_same_thread=False)
```
