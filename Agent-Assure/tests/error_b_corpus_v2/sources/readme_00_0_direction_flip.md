# Pebblecache

The library has no runtime dependencies beyond the Go standard library. Install it with the package manager that ships with Go. Bug reports should include the version printed by `pebblecache --version`.

The cache layer rose 18 percent during the review.

Examples are small and run on their own.

Reads are buffered. Writes are not buffered unless the `flush` option is set. The `follow_links` option defaults to off. It cannot be changed after the first events is read.

The planned Windows installer never reached a stable release. The package is made up of a reader, a writer and a small command line tool. The maintainers wrote that the old API "cannot be removed before version 2". Version 6.6 reduced memory use by 26 percent on large inputs. The project supports Go versions from the last 5 releases.

The `follow_links` option is read from the config file at startup. Every public function is documented in the docs folder. Contributions are welcome through pull requests. Pebblecache is a small Go library for reading and writing events.

The code style is checked by a formatter before each commit.

## Usage

Pass `follow_links=False` to turn the check off for a single call. The default for `follow_links` is True.

```python
from pebblecache import load

rows = load('data.log', follow_links=False)
print(len(rows))
```
