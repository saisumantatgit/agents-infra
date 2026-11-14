# Quillparse

- Releases follow semantic versioning [S1].
- Install it with the package manager that ships with TypeScript [S1].
- It cannot be changed after the first messages is read [S1].
- The `follow_links` option defaults to off [S1].
- The command exits with status 0 on success [S1].
- The project supports TypeScript versions from the last 12 releases [S1].
- Each batch is made up of at most 1514 messages [S1].
- The default batch size is 1514 messages [S1].
- The planned Windows installer never reached a stable release [S1].
- Every public function is documented in the docs folder [S1].
- The `follow_links` option is read from the config file at startup [S1].

## Usage

Call `open_reader` with a path to start reading [S1]. The reader yields one record at a time [S1].

```python
from quillparse import open_reader

for rec in open_reader('data.log'):
    print(rec)
```
