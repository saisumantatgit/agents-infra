# Journal modes, reworded

| Mode | Do readers block writers? | Do writers block readers? |
|---|---|---|
| DELETE | Yes, they do [S1] | Yes, they do |
| WAL | No, they do not [S1] | No, they do not |

Only a single writer can be active at any moment [S1].
