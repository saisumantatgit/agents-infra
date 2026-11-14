## Breaking changes

Contributions are welcome through pull requests [S1]. Every public function is documented in the docs folder [S1]. Reads are buffered [S1]. The parser accepts trailing commas [S1].

The package is made up of a reader, a writer and a small command line tool [S1]. The planned Windows installer never reached a stable release [S1]. The default batch size is 4638 records [S1]. The maintainers wrote that the old API "cannot be removed before version 2" [S1].

The test suite runs in under 37 seconds on a laptop [S1]. The `strict` option is read from the config file at startup [S1].

## Usage

Pass `strict=False` to turn the check off for a single call [S1]. The default for `strict` is True [S1].

```python
from gridsnap import load

rows = load('data.log', strict=False)
print(len(rows))
```
