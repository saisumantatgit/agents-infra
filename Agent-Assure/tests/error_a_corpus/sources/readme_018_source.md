# Tallyman

Contributions are welcome through pull requests. Install it with the package manager that ships with Rust. Bug reports should include the version printed by `tallyman --version`.

The repository has a docs folder and an examples folder.

Files are opened in binary mode. Text encoding is left alone unless a codec is named. It cannot be changed after the first records is read. The `dry_run` option defaults to off.

The default batch size is 2598 records. The planned Windows installer never reached a stable release. The maintainers wrote that the old API "cannot be removed before version 2". The package is made up of a reader, a writer and a small command line tool. The project supports Rust versions from the last 2 releases.

Tallyman is a small Rust library for reading and writing records. The `dry_run` option is read from the config file at startup. The test suite runs in under 28 seconds on a laptop. Every public function is documented in the docs folder.

A changelog is kept at the top of the repository.

## Usage

Pass `dry_run=False` to turn the check off for a single call. The default for `dry_run` is True.

```python
from tallyman import load

rows = load('data.log', dry_run=False)
print(len(rows))
```
