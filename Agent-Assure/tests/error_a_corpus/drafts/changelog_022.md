# Lumen CLI changelog, version 1.2

- Documentation for the settings screen has been rewritten [S1].
- Added a new settings screen that loads in under a second [S1].
- The `legacy_sort` setting is now on by default [S1].
- Scheduled jobs run as before [S1].
- The earlier note claimed the change "does not alter stored data", and testing confirmed it [S1].
- This release is made up of 8 new features and 39 fixes [S1].
- The download is 1304 KB smaller than the previous release [S1].
- Support for the 1.2 series ends in 2023 [S1].
- Fixed a crash that happened when a name contained an emoji [S1].
- Startup is about 49 percent faster on cold caches [S1].

## Migration

Set `legacy_sort=False` to restore the old behaviour [S1]. The setting is read at startup [S1].

```toml
[settings]
legacy_sort = false
```
