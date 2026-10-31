# Index notes

The default index type is B-tree, and `CREATE INDEX` builds one unless another method is named with `USING` [S1]. A partial index covers only the rows that satisfy a `WHERE` condition, which keeps it small [S1]. An index on an expression such as `lower(email)` speeds up queries that use the same expression [S1]. Building an index with `CREATE INDEX CONCURRENTLY` does not block writes to the table, although it takes longer to finish [S1].
