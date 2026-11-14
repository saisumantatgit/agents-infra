# Mothlight

- The `follow_links` option is read from the config file at startup [S1].
- Mothlight is a small Go library for reading and writing events [S1].
- Files are opened in binary mode [S1].
- Text encoding is left alone unless a codec is named [S1].
- It cannot be changed after the first events is read [S1].
- The `follow_links` option defaults to off [S1].
- Each batch is made up of at most 8216 events [S1].
- The maintainers wrote that the old API "cannot be removed before version 2" [S1].
- The planned Windows installer never reached a stable release [S1].
- The library has no runtime dependencies beyond the Go standard library [S1].
- Bug reports should include the version printed by `mothlight --version` [S1].

## Usage

Call `open_reader` with a path to start reading [S1]. The reader yields one record at a time [S1].

```python
from mothlight import open_reader

for rec in open_reader('data.log'):
    print(rec)
```
