# Temporary files, part 2

Passing `delete=False` to `NamedTemporaryFile` keeps the file after it is closed, so that another process can open it by name [S1]. On Windows a file opened by `NamedTemporaryFile` cannot be opened a second time while it is still open [S1]. The `SpooledTemporaryFile` class keeps data in memory until it grows beyond `max_size` bytes, and then rolls it over to disk [S1]. The module also offers `mktemp`, which is deprecated because it returns a name without creating the file, leaving a race condition between the call and the first use [S1].

```python
import tempfile

with tempfile.TemporaryDirectory() as d:
    print(d)
```
