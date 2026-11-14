## Supported platforms

1. The `strict` option is read from the config file at startup [S1].
2. Install it with the package manager that ships with Python [S1].
3. Reads are buffered [S1].
4. Writes are not buffered unless the `flush` option is set [S1].
5. It exits without printing anything when the input is empty [S1].
6. The command exits with status 0 on success [S1].
7. Version 8.2 reduced memory use by 74 percent on large inputs [S1].
8. The project supports Python versions from the last 2 releases [S1].
9. Each batch is made up of at most 7661 records [S1].
10. The maintainers wrote that the old API "cannot be removed before version 2" [S1].
11. Every public function is documented in the docs folder [S1].
12. Releases follow semantic versioning [S1].
