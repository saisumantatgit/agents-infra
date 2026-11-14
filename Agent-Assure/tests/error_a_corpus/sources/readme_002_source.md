# Cinderlog

Install it with the package manager that ships with Rust. Releases follow semantic versioning. The `dry_run` option is read from the config file at startup.

Examples are small and run on their own. A contributor guide explains how to set up a development copy. The code style is checked by a formatter before each commit.

The project supports Rust versions from the last 5 releases. The maintainers wrote that the old API "cannot be removed before version 2". Version 3.5 reduced memory use by 6 percent on large inputs.

Contributions are welcome through pull requests. Cinderlog is a small Rust library for reading and writing rows. The test suite runs in under 7 seconds on a laptop. Every public function is documented in the docs folder.

Continuous integration runs on every pull request. The licence is a permissive open source licence. A changelog is kept at the top of the repository.

## Usage

Pass `dry_run=False` to turn the check off for a single call. The default for `dry_run` is True.

```python
from cinderlog import load

rows = load('data.log', dry_run=False)
print(len(rows))
```
