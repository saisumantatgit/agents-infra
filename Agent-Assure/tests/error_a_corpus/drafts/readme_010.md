# Foldkit

Every public function is documented in the docs folder [S1]. Contributions are welcome through pull requests [S1]. The parser accepts trailing commas [S1]. Text encoding is left alone unless a codec is named [S1].

Files are opened in binary mode [S1]. The package is made up of a reader, a writer and a small command line tool [S1]. The planned Windows installer never reached a stable release [S1]. The project supports TypeScript versions from the last 7 releases [S1].

The default batch size is 8763 events [S1]. The maintainers wrote that the old API "cannot be removed before version 2" [S1]. Bug reports should include the version printed by `foldkit --version` [S1]. The library has no runtime dependencies beyond the TypeScript standard library [S1].

## Usage

Pass `dry_run=False` to turn the check off for a single call [S1]. The default for `dry_run` is True [S1].

```python
from foldkit import load

rows = load('data.log', dry_run=False)
print(len(rows))
```
