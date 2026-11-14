# Ferrule changelog, version 9.5

1. Improved the wording of 2 error messages [S1].
2. The search index now shows the time of the last change [S1].
3. Added a new search index that loads in under a second [S1].
4. The release contains 37 commits from 2 contributors [S1].
5. The download is 809 KB smaller than the previous release [S1].
6. This release is made up of 2 new features and 37 fixes [S1].

## Migration

Set `auto_retry=False` to restore the old behaviour [S1]. The setting is read at startup [S1].

```toml
[settings]
auto_retry = false
```
