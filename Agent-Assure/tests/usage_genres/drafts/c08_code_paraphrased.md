# Temp file behaviour

`NamedTemporaryFile` gives you a file that is deleted the moment it is closed [S1]. With `delete=False` the file survives the close, so another process can open it by name [S1]. A `TemporaryDirectory` block removes the whole directory when the block ends [S1]. `mkstemp` hands back an open file descriptor and an absolute path, and deleting the file is up to the caller [S1]. `mktemp` is deprecated because it only returns a name and never creates the file, which leaves a race [S1].

```python
import tempfile

with tempfile.TemporaryDirectory() as d:
    print(d)
```
