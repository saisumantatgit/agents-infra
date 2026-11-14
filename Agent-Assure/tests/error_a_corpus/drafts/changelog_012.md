# Cairn changelog, version 8.1

1. Added a new scheduler that loads in under a second [S1].
2. Startup is about 47% faster on cold caches [S1].
3. It is no longer written [S1].
4. The old export format is still readable [S1].
5. Support for version 3 has been removed [S1].
6. Upgrading does not delete existing data [S1].
7. The long-requested dark theme for the scheduler never made it into this release [S1].
8. Support for the 8.1 series ends in 2026 [S1].
9. The release contains 25 commits from 3 contributors [S1].
10. This release is made up of 3 new features and 25 fixes [S1].
11. The earlier note claimed the change "does not alter stored data", and testing confirmed it [S1].
12. Documentation for the scheduler has been rewritten [S1].
13. The scheduler now shows the time of the last change [S1].

## Migration

Set `compact_view=False` to restore the old behaviour [S1]. The setting is read at startup [S1].

```toml
[settings]
compact_view = false
```
