# Review notes: scheduler change

- The pull request touches 2 files [S1].
- The change adds 8 tests for the new branch [S1].
- Logging was moved to the top of the scheduler [S1].
- Run time dropped from 8 seconds to 2 seconds in the benchmark [S1].
- Coverage for the scheduler is now 71 percent [S1].
- The test fixture is made up of 2 small files and one large archive [S1].

## Snippet

The call in `load_rules` passes `verify=False` on purpose [S1]. A comment above it explains why [S1].

```python
def load_rules(conn, rows):
    conn.execute(rows, verify=False)
```
