# Temporary files, part 1

The `tempfile` module creates temporary files and directories safely [S1]. `NamedTemporaryFile` returns a file object that is deleted as soon as it is closed [S1]. The function `mkstemp` returns a tuple of an open file descriptor and an absolute path, and the caller is responsible for deleting the file [S1]. A `TemporaryDirectory` context manager removes the directory and everything inside it when the block exits [S1]. By default the files are created in the directory returned by `gettempdir`, which honors the `TMPDIR` environment variable [S1].

```python
import tempfile

with tempfile.TemporaryDirectory() as d:
    print(d)
```
