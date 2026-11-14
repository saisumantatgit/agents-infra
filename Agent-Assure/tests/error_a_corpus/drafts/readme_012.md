## Planned features

The test suite runs in under 29 seconds on a laptop [S1]. Releases follow semantic versioning [S1]. The `dry_run` option defaults to off [S1]. It cannot be changed after the first rows is read [S1].

The command exits with status 0 on success [S1]. The maintainers wrote that the old API "cannot be removed before version 2" [S1]. The project supports TypeScript versions from the last 2 releases [S1]. Each batch is made up of at most 5811 rows [S1].

The planned Windows installer never reached a stable release [S1]. The library has no runtime dependencies beyond the TypeScript standard library [S1]. Every public function is documented in the docs folder [S1].

## Usage

Call `open_reader` with a path to start reading [S1]. The reader yields one record at a time [S1].

```python
from foldkit import open_reader

for rec in open_reader('data.log'):
    print(rec)
```
