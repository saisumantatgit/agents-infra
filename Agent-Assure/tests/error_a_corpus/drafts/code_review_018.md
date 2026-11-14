## Test results

- Greta split the importer into two files [S1].
- The new loop runs once per record instead of once per field [S1].
- The tests pass locally [S1].
- They have not been run on the Windows runner [S1].
- The retry logic handles timeouts [S1].
- Greta commented that the old loop "is not thread safe" [S1].
- The test fixture is made up of 12 small files and one large archive [S1].
- Coverage for the importer is now 51% [S1].
- The planned rewrite of `render_row` never landed in this pull request [S1].
- The pull request touches 12 files [S1].
- The change adds 40 tests for the new branch [S1].

## Snippet

The call in `render_row` passes `verify=False` on purpose [S1]. A comment above it explains why [S1].

```python
def render_row(conn, rows):
    conn.execute(rows, verify=False)
```
