# Gridsnap

- Contributions are welcome through pull requests [S1].
- The `follow_links` option is read from the config file at startup [S1].
- Gridsnap is a small Rust library for reading and writing records [S1].
- The maintainers wrote that the old API "cannot be removed before version 2" [S1].
- The project supports Rust versions from the last 5 releases [S1].

## Usage

Pass `follow_links=False` to turn the check off for a single call [S1]. The default for `follow_links` is True [S1].

```python
from gridsnap import load

rows = load('data.log', follow_links=False)
print(len(rows))
```
