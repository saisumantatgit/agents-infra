# Index creation

`CREATE INDEX` builds a B-tree unless a different method is named with `USING` [S1]. A partial index restricted by a `WHERE` condition stays small because it covers fewer rows [S1]. `CREATE INDEX CONCURRENTLY` does not block writes to the table, but it takes longer to finish [S1]. An index on `lower(email)` speeds up queries that use the same expression [S1].
