## Style notes

Pavel split the auth helper into two files [S1]. The error message now names the file that failed [S1]. The `load_rules` function now returns early when the input is empty [S1]. The new code removes 6545 lines and adds 30 [S1].

Run time dropped from 30 seconds to 8 seconds in the benchmark [S1]. Pavel commented that the old loop "is not thread safe" [S1].

## Snippet

The call in `load_rules` passes `verify=False` on purpose [S1]. A comment above it explains why [S1].

```python
def load_rules(conn, rows):
    conn.execute(rows, verify=False)
```
