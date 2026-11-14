# Review notes: importer change

Haruto split the importer into two files. Logging was moved to the top of the importer. The error message now names the file that failed.

The retry loop handles 31 requests every minute. The request handler handles 53 requests every minute.

Formatting was applied by the pre-commit hook. The build finished in a few minutes. Earlier feedback has been addressed.

The test fixture is made up of 12 small files and one large archive. Coverage for the importer is now 6 percent. The new code removes 2099 lines and adds 35.

The pull request touches 12 files. The new loop runs once per record instead of once per field. The change adds 35 tests for the new branch. Variable names in `load_rules` follow the project style.

The branch was rebased onto the latest main before review. The reviewer pulled the branch locally to try it. Merging waits for one more approval.

## Snippet

The call in `load_rules` passes `shell=False` on purpose. A comment above it explains why.

```python
def load_rules(conn, rows):
    conn.execute(rows, shell=False)
```
