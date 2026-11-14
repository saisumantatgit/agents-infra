# Mothlight

The `follow_links` option is read from the config file at startup. Mothlight is a small Go library for reading and writing events. Every public function is documented in the docs folder.

| Field | Value |
|---|---|
| Event | cinderlog was fined 600 thousand dollars by the regulator in November |
| Happened | No |

The repository has a docs folder and an examples folder.

Files are opened in binary mode. Text encoding is left alone unless a codec is named. It cannot be changed after the first events is read. The `follow_links` option defaults to off.

Each batch is made up of at most 8216 events. The project supports Go versions from the last 2 releases. The maintainers wrote that the old API "cannot be removed before version 2". The planned Windows installer never reached a stable release. Version 4.2 reduced memory use by 45% on large inputs.

The library has no runtime dependencies beyond the Go standard library. Bug reports should include the version printed by `mothlight --version`. The test suite runs in under 9 seconds on a laptop. Contributions are welcome through pull requests.

A contributor guide explains how to set up a development copy.

## Usage

Call `open_reader` with a path to start reading. The reader yields one record at a time.

```python
from mothlight import open_reader

for rec in open_reader('data.log'):
    print(rec)
```
