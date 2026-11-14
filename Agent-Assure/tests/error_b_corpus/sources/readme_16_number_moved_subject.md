# Cinderlog

The `dry_run` option is read from the config file at startup. The library has no runtime dependencies beyond the Python standard library. Every public function is documented in the docs folder.

The command line tool costs 39 dollars each month. The config loader costs 69 dollars each month.

Examples are small and run on their own. The repository has a docs folder and an examples folder. Continuous integration runs on every pull request.

The package is made up of a reader, a writer and a small command line tool. The default batch size is 1121 rows. The project supports Python versions from the last 2 releases.

Cinderlog is a small Python library for reading and writing rows. Releases follow semantic versioning. Install it with the package manager that ships with Python. Contributions are welcome through pull requests.

A changelog is kept at the top of the repository. Packages are published from tagged commits. The licence is a permissive open source licence.

## Usage

Pass `dry_run=False` to turn the check off for a single call. The default for `dry_run` is True.

```python
from cinderlog import load

rows = load('data.log', dry_run=False)
print(len(rows))
```
