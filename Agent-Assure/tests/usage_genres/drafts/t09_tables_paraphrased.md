# Index types, reworded

| Index type | Use it for | Range queries |
|---|---|---|
| B-tree | Comparisons for equality and for ranges [S1] | Supported |
| Hash | Plain equality comparisons [S1] | Not supported |
| GiST | Geometric data and nearest-neighbour searches [S1] | Supported |
| BRIN | Huge tables where the values follow the physical order [S1] | Supported |
