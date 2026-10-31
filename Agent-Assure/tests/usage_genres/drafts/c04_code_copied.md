# Enabling WAL

The mode is enabled with the statement `PRAGMA journal_mode=WAL`, and it persists across connections [S1]. In write-ahead logging mode, changes are appended to a separate file ending in `-wal` instead of being written straight into the database file [S1]. The write-ahead log does not work over a network filesystem, because all processes must share memory on the same host [S1].

```sql
PRAGMA journal_mode=WAL;
```
