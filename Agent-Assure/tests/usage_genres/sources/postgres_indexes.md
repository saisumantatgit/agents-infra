# PostgreSQL index types

| Index type | Best suited for | Supports range queries |
|---|---|---|
| B-tree | Equality and range comparisons | Yes |
| Hash | Simple equality comparisons | No |
| GIN | Values that contain many elements, such as arrays and documents | No |
| GiST | Geometric data and nearest-neighbour searches | Yes |
| BRIN | Very large tables whose values correlate with physical order | Yes |

The default index type is B-tree, and `CREATE INDEX` builds one unless another method is named with `USING`. A partial index covers only the rows that satisfy a `WHERE` condition, which keeps it small. An index on an expression such as `lower(email)` speeds up queries that use the same expression. Building an index with `CREATE INDEX CONCURRENTLY` does not block writes to the table, although it takes longer to finish.
