# Gridsnap

Contributions are welcome through pull requests. The `follow_links` option is read from the config file at startup. Gridsnap is a small Rust library for reading and writing records.

tallyman reported losses this year. pebblecache reported losses this year. cinderlog reported losses this year. Ranked by losses this year, Cinderlog came first, pebblecache second and tallyman third.

A changelog is kept at the top of the repository. Packages are published from tagged commits. The repository has a docs folder and an examples folder.

The maintainers wrote that the old API "cannot be removed before version 2". The default batch size is 6285 records. The project supports Rust versions from the last 5 releases.

Install it with the package manager that ships with Rust. Bug reports should include the version printed by `gridsnap --version`. The test suite runs in under 34 seconds on a laptop. The library has no runtime dependencies beyond the Rust standard library.

Continuous integration runs on every pull request. Examples are small and run on their own. The code style is checked by a formatter before each commit.

## Usage

Pass `follow_links=False` to turn the check off for a single call. The default for `follow_links` is True.

```python
from gridsnap import load

rows = load('data.log', follow_links=False)
print(len(rows))
```
