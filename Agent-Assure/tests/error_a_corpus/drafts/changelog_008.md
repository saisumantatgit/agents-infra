## Known issues

- Startup is about 82% faster on cold caches [S1].
- Improved the wording of 8 error messages [S1].
- The exporter now shows the time of the last change [S1].
- Support for the 3.2 series ends in 2026 [S1].
- The download is 9658 KB smaller than the previous release [S1].
- This release is made up of 8 new features and 14 fixes [S1].

## Migration

Set `legacy_sort=False` to restore the old behaviour [S1]. The setting is read at startup [S1].

```toml
[settings]
legacy_sort = false
```
