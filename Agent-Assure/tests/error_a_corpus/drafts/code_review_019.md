## Open issues

- Variable names in `load_rules` follow the project style [S1].
- The `load_rules` function now returns early when the input is empty [S1].
- The cache is cleared on startup [S1].
- `load_rules` validates its arguments [S1].
- It does not check the encoding of the path [S1].
- Run time dropped from 48 seconds to 7 seconds in the benchmark [S1].
- Greta commented that the old loop "is not thread safe" [S1].
- Coverage for the importer is now 8% [S1].
- The change adds 48 tests for the new branch [S1].
- Greta split the importer into two files [S1].
