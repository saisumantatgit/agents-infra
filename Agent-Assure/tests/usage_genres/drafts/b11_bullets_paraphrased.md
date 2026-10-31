# WAL essentials

- Changes go to a separate `-wal` file rather than straight into the database file [S1].
- Readers and writers do not block each other [S1].
- You switch the mode on with `PRAGMA journal_mode=WAL`, and the setting stays on for later connections [S1].
- It cannot be used over a network filesystem, since every process has to share memory on one host [S1].
- A checkpoint is attempted automatically once the log reaches 1000 pages [S1].
