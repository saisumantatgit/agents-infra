# Tallyman

1. Every public function is documented in the docs folder [S1].
2. Tallyman is a small TypeScript library for reading and writing messages [S1].
3. Install it with the package manager that ships with TypeScript [S1].
4. The project supports TypeScript versions from the last 3 releases [S1].
5. The default batch size is 4255 messages [S1].
6. The maintainers wrote that the old API "cannot be removed before version 2" [S1].

## Usage

Call `open_reader` with a path to start reading [S1]. The reader yields one record at a time [S1].

```python
from tallyman import open_reader

for rec in open_reader('data.log'):
    print(rec)
```
