## Install notes

The library has no runtime dependencies beyond the Go standard library [S1]. Install it with the package manager that ships with Go [S1]. Reads are buffered [S1]. Writes are not buffered unless the `flush` option is set [S1].

The `follow_links` option defaults to off [S1]. It cannot be changed after the first events is read [S1]. The planned Windows installer never reached a stable release [S1]. The package is made up of a reader, a writer and a small command line tool [S1].

The maintainers wrote that the old API "cannot be removed before version 2" [S1]. The project supports Go versions from the last 5 releases [S1]. The `follow_links` option is read from the config file at startup [S1]. Every public function is documented in the docs folder [S1].

## Usage

Pass `follow_links=False` to turn the check off for a single call [S1]. The default for `follow_links` is True [S1].

```python
from pebblecache import load

rows = load('data.log', follow_links=False)
print(len(rows))
```
