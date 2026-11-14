# Ferrule changelog, version 3.3

Improved the wording of 3 error messages [S1]. The search index now shows the time of the last change [S1]. The old export format is still readable [S1]. The `auto_retry` setting is now on by default [S1].

This release is made up of 3 new features and 15 fixes [S1]. Support for the 3.3 series ends in 2023 [S1]. The release contains 15 commits from 3 contributors [S1]. The earlier note claimed the change "does not alter stored data", and testing confirmed it [S1].

The long-requested dark theme for the search index never made it into this release [S1]. Documentation for the search index has been rewritten [S1]. The installer now checks for free disk space first [S1].

## Migration

Set `auto_retry=False` to restore the old behaviour [S1]. The setting is read at startup [S1].

```toml
[settings]
auto_retry = false
```
