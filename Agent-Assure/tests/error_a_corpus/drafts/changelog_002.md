# Lumen CLI changelog, version 9.7

Startup is about 57 percent faster on cold caches [S1]. Updated the bundled certificates [S1]. Added a new importer that loads in under a second [S1]. The download is 2777 KB smaller than the previous release [S1].

The deprecated `legacy_sort` option never worked on the command line [S1]. The release contains 14 commits from 7 contributors [S1].

## Migration

Set `legacy_sort=False` to restore the old behaviour [S1]. The setting is read at startup [S1].

```toml
[settings]
legacy_sort = false
```
