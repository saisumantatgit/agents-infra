# Tallyman

Every public function is documented in the docs folder. Tallyman is a small TypeScript library for reading and writing messages. Install it with the package manager that ships with TypeScript.

The repository has a docs folder and an examples folder. A contributor guide explains how to set up a development copy. Examples are small and run on their own.

The project supports TypeScript versions from the last 3 releases. The default batch size is 4255 messages. The maintainers wrote that the old API "cannot be removed before version 2".

The test suite runs in under 47 seconds on a laptop. Bug reports should include the version printed by `tallyman --version`. Contributions are welcome through pull requests. Releases follow semantic versioning.

Issues are triaged on a weekly basis. Packages are published from tagged commits. The name of the project comes from a village in the hills.

## Usage

Call `open_reader` with a path to start reading. The reader yields one record at a time.

```python
from tallyman import open_reader

for rec in open_reader('data.log'):
    print(rec)
```
