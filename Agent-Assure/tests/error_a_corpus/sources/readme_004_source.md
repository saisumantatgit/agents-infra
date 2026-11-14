# Cinderlog

Contributions are welcome through pull requests. Releases follow semantic versioning. Bug reports should include the version printed by `cinderlog --version`.

Packages are published from tagged commits. Issues are triaged on a weekly basis. A contributor guide explains how to set up a development copy.

Writes are not buffered unless the `flush` option is set. Reads are buffered. The `follow_links` option defaults to off. It cannot be changed after the first messages is read.

The planned Windows installer never reached a stable release. The maintainers wrote that the old API "cannot be removed before version 2". The package is made up of a reader, a writer and a small command line tool. The default batch size is 1174 messages. The project supports TypeScript versions from the last 12 releases.

Every public function is documented in the docs folder. Cinderlog is a small TypeScript library for reading and writing messages. The library has no runtime dependencies beyond the TypeScript standard library. Install it with the package manager that ships with TypeScript.

Examples are small and run on their own. A changelog is kept at the top of the repository. The name of the project comes from a village in the hills.

## Usage

Pass `follow_links=False` to turn the check off for a single call. The default for `follow_links` is True.

```python
from cinderlog import load

rows = load('data.log', follow_links=False)
print(len(rows))
```
