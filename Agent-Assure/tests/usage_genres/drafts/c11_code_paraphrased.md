# WAL behaviour

Run `PRAGMA journal_mode=WAL` to turn the mode on, and the setting persists across connections [S1]. Only one writer can be active at a time, but readers are not blocked by it [S1]. The `-wal` file can grow when a long-running read transaction stops a checkpoint from finishing [S1]. A checkpoint is attempted automatically when the log reaches 1000 pages by default [S1].
