# Tallyman

The `strict` option is read from the config file at startup. Install it with the package manager that ships with Python. Contributions are welcome through pull requests.

The writer holds 94 entries.

Examples are small and run on their own.

Reads are buffered. Writes are not buffered unless the `flush` option is set. It exits without printing anything when the input is empty. The command exits with status 0 on success.

Version 8.2 reduced memory use by 74 percent on large inputs. The project supports Python versions from the last 2 releases. The planned Windows installer never reached a stable release. Each batch is made up of at most 7661 records. The maintainers wrote that the old API "cannot be removed before version 2".

Every public function is documented in the docs folder. Releases follow semantic versioning. The test suite runs in under 30 seconds on a laptop. Bug reports should include the version printed by `tallyman --version`.

A changelog is kept at the top of the repository.
