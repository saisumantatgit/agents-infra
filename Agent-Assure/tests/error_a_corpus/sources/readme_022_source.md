# Quillparse

Releases follow semantic versioning. Install it with the package manager that ships with TypeScript. The test suite runs in under 11 seconds on a laptop.

The licence is a permissive open source licence. Examples are small and run on their own. A changelog is kept at the top of the repository.

It cannot be changed after the first messages is read. The `follow_links` option defaults to off. It exits without printing anything when the input is empty. The command exits with status 0 on success.

The project supports TypeScript versions from the last 12 releases. Each batch is made up of at most 1514 messages. The default batch size is 1514 messages. The maintainers wrote that the old API "cannot be removed before version 2". The planned Windows installer never reached a stable release.

Every public function is documented in the docs folder. The `follow_links` option is read from the config file at startup. Bug reports should include the version printed by `quillparse --version`. The library has no runtime dependencies beyond the TypeScript standard library.

A contributor guide explains how to set up a development copy. Continuous integration runs on every pull request. The code style is checked by a formatter before each commit.

## Usage

Call `open_reader` with a path to start reading. The reader yields one record at a time.

```python
from quillparse import open_reader

for rec in open_reader('data.log'):
    print(rec)
```
