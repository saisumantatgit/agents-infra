## Open issues

The change adds 47 tests for the new branch [S1]. Sofia split the importer into two files [S1]. The cache is cleared on startup [S1]. It is not cleared when the configuration reloads unless the reviewer asks for it [S1].

The helper is safe to call twice [S1]. The new code removes 5786 lines and adds 47 [S1]. The test fixture is made up of 4 small files and one large archive [S1]. Sofia commented that the old loop "is not thread safe" [S1].

The planned rewrite of `render_row` never landed in this pull request [S1]. The new loop runs once per record instead of once per field [S1]. Logging was moved to the top of the importer [S1].
