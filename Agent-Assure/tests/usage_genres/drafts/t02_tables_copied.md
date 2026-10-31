# Index types

| Index type | Best suited for | Supports range queries |
|---|---|---|
| B-tree | Equality and range comparisons [S1] | Yes |
| Hash | Simple equality comparisons [S1] | No |
| GIN | Values that contain many elements, such as arrays and documents [S1] | No |
| GiST | Geometric data and nearest-neighbour searches [S1] | Yes |
| BRIN | Very large tables whose values correlate with physical order [S1] | Yes |
