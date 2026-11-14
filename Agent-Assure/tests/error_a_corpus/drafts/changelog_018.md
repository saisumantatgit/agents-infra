## New features

- Documentation for the exporter has been rewritten [S1].
- Added a new exporter that loads in under a second [S1].
- It can still be turned off in the configuration file [S1].
- The `legacy_sort` setting is now on by default [S1].
- The exporter keeps working offline [S1].
- It cannot refresh until the network returns [S1].
- The earlier note claimed the change "does not alter stored data", and testing confirmed it [S1].
- Support for the 4.7 series ends in 2025 [S1].
- This release is made up of 3 new features and 14 fixes [S1].
- The download is 2365 KB smaller than the previous release [S1].
- The installer now checks for free disk space first [S1].
- Fixed a crash that happened when a name contained an emoji [S1].

## Migration

Set `legacy_sort=False` to restore the old behaviour [S1]. The setting is read at startup [S1].

```toml
[settings]
legacy_sort = false
```
