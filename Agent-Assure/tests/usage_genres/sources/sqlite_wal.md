# SQLite write-ahead logging

In write-ahead logging mode, changes are appended to a separate file ending in `-wal` instead of being written straight into the database file. Readers do not block writers, and a writer does not block readers. Only one writer can be active at a time. The mode is enabled with the statement `PRAGMA journal_mode=WAL`, and it persists across connections. A checkpoint copies the pages from the log back into the main database file. By default a checkpoint is attempted automatically when the log reaches 1000 pages. The write-ahead log does not work over a network filesystem, because all processes must share memory on the same host. Long-running read transactions can prevent a checkpoint from finishing, which makes the log file grow.

| Mode | Readers block writers | Writers block readers |
|---|---|---|
| DELETE | Yes | Yes |
| WAL | No | No |
