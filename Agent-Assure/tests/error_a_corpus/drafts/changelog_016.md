## Deprecations

- The installer now checks for free disk space first [S1].
- Updated the bundled certificates [S1].
- The exporter keeps working offline [S1].
- It cannot refresh until the network returns [S1].
- Scheduled jobs run as before [S1].
- The deprecated `strict_mode` option never worked on the command line [S1].
- This release is made up of 4 new features and 42 fixes [S1].
- The earlier note claimed the change "does not alter stored data", and testing confirmed it [S1].
- The release contains 42 commits from 4 contributors [S1].
- The exporter now shows the time of the last change [S1].
- Added a new exporter that loads in under a second [S1].

## Migration

Set `strict_mode=False` to restore the old behaviour [S1]. The setting is read at startup [S1].

```toml
[settings]
strict_mode = false
```
