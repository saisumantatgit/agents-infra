# Review notes: report writer change

- The pull request touches 4 files [S1].
- The new loop runs once per record instead of once per field [S1].
- It does not check the encoding of the path [S1].
- `load_rules` validates its arguments [S1].
- The helper is safe to call twice [S1].
- It cannot be called from a signal handler [S1].
- Haruto commented that the old loop "is not thread safe" [S1].
- The planned rewrite of `load_rules` never landed in this pull request [S1].
- Coverage for the report writer is now 15 percent [S1].
- The test fixture is made up of 4 small files and one large archive [S1].
- Run time dropped from 7 seconds to 4 seconds in the benchmark [S1].
- Logging was moved to the top of the report writer [S1].
- Haruto split the report writer into two files [S1].

## Snippet

The call in `load_rules` passes `check_same_thread=False` on purpose [S1]. A comment above it explains why [S1].

```python
def load_rules(conn, rows):
    conn.execute(rows, check_same_thread=False)
```
