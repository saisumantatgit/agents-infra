## Planned features

Contributions are welcome through pull requests [S1]. Install it with the package manager that ships with Rust [S1]. Files are opened in binary mode [S1]. The `dry_run` option defaults to off [S1].

The default batch size is 2598 records [S1]. The planned Windows installer never reached a stable release [S1]. The package is made up of a reader, a writer and a small command line tool [S1]. The project supports Rust versions from the last 2 releases [S1].

Tallyman is a small Rust library for reading and writing records [S1]. The `dry_run` option is read from the config file at startup [S1].

## Usage

Pass `dry_run=False` to turn the check off for a single call [S1]. The default for `dry_run` is True [S1].

```python
from tallyman import load

rows = load('data.log', dry_run=False)
print(len(rows))
```
