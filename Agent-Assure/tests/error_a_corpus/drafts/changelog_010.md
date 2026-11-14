## Price rises

- Fixed a crash that happened when a name contained an emoji [S1].
- Improved the wording of 8 error messages [S1].
- Support for version 8 has been removed [S1].
- Scheduled jobs run as before [S1].
- Jobs without an owner are skipped unless they are marked as shared [S1].
- The earlier note claimed the change "does not alter stored data", and testing confirmed it [S1].
- The deprecated `strict_mode` option never worked on the command line [S1].
- This release is made up of 8 new features and 19 fixes [S1].
- The download is 4715 KB smaller than the previous release [S1].
- Support for the 9.5 series ends in 2022 [S1].
- Startup is about 63% faster on cold caches [S1].
- Updated the bundled certificates [S1].

## Migration

Set `strict_mode=False` to restore the old behaviour [S1]. The setting is read at startup [S1].

```toml
[settings]
strict_mode = false
```
