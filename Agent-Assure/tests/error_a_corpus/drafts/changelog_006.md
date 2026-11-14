## Deprecations

1. Improved the wording of 4 error messages [S1].
2. Fixed a crash that happened when a name contained an emoji [S1].
3. The login flow keeps working offline [S1].
4. It is no longer written [S1].
5. The old export format is still readable [S1].
6. The deprecated `strict_mode` option never worked on the command line [S1].
7. This release is made up of 4 new features and 31 fixes [S1].
8. The earlier note claimed the change "does not alter stored data", and testing confirmed it [S1].
9. The release contains 31 commits from 4 contributors [S1].
10. The download is 3030 KB smaller than the previous release [S1].
11. The installer now checks for free disk space first [S1].
12. Documentation for the login flow has been rewritten [S1].

## Migration

Set `strict_mode=False` to restore the old behaviour [S1]. The setting is read at startup [S1].

```toml
[settings]
strict_mode = false
```
