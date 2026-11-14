# Foldkit

Every public function is documented in the docs folder. Contributions are welcome through pull requests. Foldkit is a small TypeScript library for reading and writing events.

A contributor guide explains how to set up a development copy. Examples are small and run on their own. The licence is a permissive open source licence.

The parser does not accept comments inside values. The parser accepts trailing commas. Text encoding is left alone unless a codec is named. Files are opened in binary mode.

The package is made up of a reader, a writer and a small command line tool. The planned Windows installer never reached a stable release. The project supports TypeScript versions from the last 7 releases. The default batch size is 8763 events. The maintainers wrote that the old API "cannot be removed before version 2".

Bug reports should include the version printed by `foldkit --version`. The library has no runtime dependencies beyond the TypeScript standard library. The `dry_run` option is read from the config file at startup. Install it with the package manager that ships with TypeScript.

Issues are triaged on a weekly basis. Continuous integration runs on every pull request. A changelog is kept at the top of the repository.

## Usage

Pass `dry_run=False` to turn the check off for a single call. The default for `dry_run` is True.

```python
from foldkit import load

rows = load('data.log', dry_run=False)
print(len(rows))
```
