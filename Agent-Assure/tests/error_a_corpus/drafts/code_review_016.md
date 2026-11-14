# Review notes: scheduler change

The pull request touches 3 files [S1]. Logging was moved to the top of the scheduler [S1]. The helper is safe to call twice [S1]. It does not handle connection resets [S1].

The retry logic handles timeouts [S1]. Coverage for the scheduler is now 36% [S1]. Run time dropped from 15 seconds to 3 seconds in the benchmark [S1]. The planned rewrite of `load_rules` never landed in this pull request [S1].

Variable names in `load_rules` follow the project style [S1]. The new loop runs once per record instead of once per field [S1].

## Snippet

The call in `load_rules` passes `check_same_thread=False` on purpose [S1]. A comment above it explains why [S1].

```python
def load_rules(conn, rows):
    conn.execute(rows, check_same_thread=False)
```
