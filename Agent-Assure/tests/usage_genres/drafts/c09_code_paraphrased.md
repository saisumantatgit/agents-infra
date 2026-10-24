# Where temp files live

`gettempdir` decides where temporary files go by default, and it honors `TMPDIR` [S1]. `SpooledTemporaryFile` holds data in memory and moves it to disk once it grows past `max_size` bytes [S1]. On Windows you cannot open a `NamedTemporaryFile` a second time while it is still open [S1].
