# Review notes: auth helper change

- The new loop runs once per record instead of once per field [S1].
- Logging was moved to the top of the auth helper [S1].
- The cache is cleared on startup [S1].
- The tests pass locally [S1].
- The planned rewrite of `parse_header` never landed in this pull request [S1].
- Run time dropped from 20 seconds to 7 seconds in the benchmark [S1].
- The test fixture is made up of 7 small files and one large archive [S1].
- The new code removes 8174 lines and adds 20 [S1].
- Sofia commented that the old loop "is not thread safe" [S1].
- The change adds 20 tests for the new branch [S1].
- The pull request touches 7 files [S1].
