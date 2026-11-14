## Test results

1. The change adds 36 tests for the new branch [S1].
2. The pull request touches 6 files [S1].
3. Variable names in `build_index` follow the project style [S1].
4. The test fixture is made up of 6 small files and one large archive [S1].
5. Coverage for the auth helper is now 76% [S1].
6. The new code removes 7775 lines and adds 36 [S1].

## Snippet

The call in `build_index` passes `check_same_thread=False` on purpose [S1]. A comment above it explains why [S1].

```python
def build_index(conn, rows):
    conn.execute(rows, check_same_thread=False)
```
