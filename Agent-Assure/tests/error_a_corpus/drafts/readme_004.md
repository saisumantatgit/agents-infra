# Cinderlog

- Contributions are welcome through pull requests [S1].
- Releases follow semantic versioning [S1].
- Writes are not buffered unless the `flush` option is set [S1].
- Reads are buffered [S1].
- The `follow_links` option defaults to off [S1].
- The planned Windows installer never reached a stable release [S1].
- The package is made up of a reader, a writer and a small command line tool [S1].
- The default batch size is 1174 messages [S1].
- The project supports TypeScript versions from the last 12 releases [S1].
- Every public function is documented in the docs folder [S1].
- Cinderlog is a small TypeScript library for reading and writing messages [S1].

## Usage

Pass `follow_links=False` to turn the check off for a single call [S1]. The default for `follow_links` is True [S1].

```python
from cinderlog import load

rows = load('data.log', follow_links=False)
print(len(rows))
```
