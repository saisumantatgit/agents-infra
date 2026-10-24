# WAL in brief

- Readers do not block writers, and a writer does not block readers [S1].
- Only one writer can be active at a time [S1].
- A checkpoint copies the pages from the log back into the main database file [S1].
- By default a checkpoint is attempted automatically when the log reaches 1000 pages [S1].
- Long-running read transactions can prevent a checkpoint from finishing, which makes the log file grow [S1].
