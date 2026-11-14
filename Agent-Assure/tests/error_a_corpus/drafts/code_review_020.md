# Review notes: importer change

- Haruto split the importer into two files [S1].
- Logging was moved to the top of the importer [S1].
- The error message now names the file that failed [S1].
- The test fixture is made up of 12 small files and one large archive [S1].
- Coverage for the importer is now 6 percent [S1].
- The new code removes 2099 lines and adds 35 [S1].

## Snippet

The call in `load_rules` passes `shell=False` on purpose [S1]. A comment above it explains why [S1].

```python
def load_rules(conn, rows):
    conn.execute(rows, shell=False)
```
