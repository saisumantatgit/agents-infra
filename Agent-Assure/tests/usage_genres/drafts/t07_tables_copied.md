# Indexes for special data

| Index type | Best suited for |
|---|---|
| GIN | Values that contain many elements, such as arrays and documents [S1] |
| GiST | Geometric data and nearest-neighbour searches [S1] |
| BRIN | Very large tables whose values correlate with physical order [S1] |

A partial index covers only the rows that satisfy a `WHERE` condition, which keeps it small [S1].
