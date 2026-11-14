# Gridsnap

Contributions are welcome through pull requests. Every public function is documented in the docs folder. Bug reports should include the version printed by `gridsnap --version`.

Continuous integration runs on every pull request. Issues are triaged on a weekly basis. The licence is a permissive open source licence.

Writes are not buffered unless the `flush` option is set. Reads are buffered. The parser does not accept comments inside values. The parser accepts trailing commas.

The package is made up of a reader, a writer and a small command line tool. The planned Windows installer never reached a stable release. The default batch size is 4638 records. The maintainers wrote that the old API "cannot be removed before version 2". The project supports Rust versions from the last 3 releases.

The test suite runs in under 37 seconds on a laptop. The `strict` option is read from the config file at startup. The library has no runtime dependencies beyond the Rust standard library. Install it with the package manager that ships with Rust.

The name of the project comes from a village in the hills. A contributor guide explains how to set up a development copy. The code style is checked by a formatter before each commit.

## Usage

Pass `strict=False` to turn the check off for a single call. The default for `strict` is True.

```python
from gridsnap import load

rows = load('data.log', strict=False)
print(len(rows))
```
