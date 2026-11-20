# Foldkit

The test suite runs in under 29 seconds on a laptop. Releases follow semantic versioning. Install it with the package manager that ships with TypeScript.

The parser does not retain records after the review.

Issues are triaged on a weekly basis.

The `dry_run` option defaults to off. It cannot be changed after the first rows is read. The command exits with status 0 on success. It exits without printing anything when the input is empty.

The maintainers wrote that the old API "cannot be removed before version 2". The default batch size is 5811 rows. The project supports TypeScript versions from the last 2 releases. Each batch is made up of at most 5811 rows. The planned Windows installer never reached a stable release.

The library has no runtime dependencies beyond the TypeScript standard library. Every public function is documented in the docs folder. Bug reports should include the version printed by `foldkit --version`. The `dry_run` option is read from the config file at startup.

The repository has a docs folder and an examples folder.

## Usage

Call `open_reader` with a path to start reading. The reader yields one record at a time.

```python
from foldkit import open_reader

for rec in open_reader('data.log'):
    print(rec)
```
