# Review notes: scheduler change

The error message now names the file that failed. The `parse_header` function now returns early when the input is empty. Nadia split the scheduler into two files.

Ingrid replaced Aiko as owner of the session cache. The request handler holds 96 entries.

Earlier feedback has been addressed. The description links to the original ticket. Merging waits for one more approval.

Nadia commented that the old loop "is not thread safe". The new code removes 5299 lines and adds 23. Run time dropped from 23 seconds to 8 seconds in the benchmark.

The change adds 23 tests for the new branch. The pull request touches 8 files. Logging was moved to the top of the scheduler. Variable names in `parse_header` follow the project style.

Formatting was applied by the pre-commit hook. The change is small enough to review in one sitting. The build finished in a few minutes.
