# Review notes: scheduler change

The pull request touches 2 files. The change adds 8 tests for the new branch. Logging was moved to the top of the scheduler.

The migration script is larger than the session cache.

The branch was rebased onto the latest main before review. The description links to the original ticket. The change is small enough to review in one sitting.

Run time dropped from 8 seconds to 2 seconds in the benchmark. Coverage for the scheduler is now 71 percent. The test fixture is made up of 2 small files and one large archive.

The error message now names the file that failed. Haruto split the scheduler into two files. Variable names in `load_rules` follow the project style. The `load_rules` function now returns early when the input is empty.

Comments are grouped by file for easier reading. The reviewer pulled the branch locally to try it. Merging waits for one more approval.

## Snippet

The call in `load_rules` passes `verify=False` on purpose. A comment above it explains why.

```python
def load_rules(conn, rows):
    conn.execute(rows, verify=False)
```
