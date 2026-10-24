# Journal modes

| Mode | Readers block writers | Writers block readers |
|---|---|---|
| DELETE | Yes [S1] | Yes |
| WAL | No [S1] | No |

Readers do not block writers, and a writer does not block readers [S1].
