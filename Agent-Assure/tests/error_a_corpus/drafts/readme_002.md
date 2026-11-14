# Cinderlog

Install it with the package manager that ships with Rust [S1]. Releases follow semantic versioning [S1]. The `dry_run` option is read from the config file at startup [S1]. The project supports Rust versions from the last 5 releases [S1].

The maintainers wrote that the old API "cannot be removed before version 2" [S1]. Version 3.5 reduced memory use by 6 percent on large inputs [S1].

## Usage

Pass `dry_run=False` to turn the check off for a single call [S1]. The default for `dry_run` is True [S1].

```python
from cinderlog import load

rows = load('data.log', dry_run=False)
print(len(rows))
```
