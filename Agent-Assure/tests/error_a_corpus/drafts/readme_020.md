# Cinderlog

- The `dry_run` option is read from the config file at startup [S1].
- The library has no runtime dependencies beyond the Python standard library [S1].
- Every public function is documented in the docs folder [S1].
- The project supports Python versions from the last 2 releases [S1].

## Usage

Pass `dry_run=False` to turn the check off for a single call [S1]. The default for `dry_run` is True [S1].

```python
from cinderlog import load

rows = load('data.log', dry_run=False)
print(len(rows))
```
