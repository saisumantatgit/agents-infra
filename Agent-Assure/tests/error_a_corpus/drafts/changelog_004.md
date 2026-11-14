## Deprecations

Startup is about 22% faster on cold caches [S1]. Added a new exporter that loads in under a second [S1]. Support for version 4 has been removed [S1]. Scheduled jobs run as before [S1].

This release is made up of 4 new features and 6 fixes [S1]. The earlier note claimed the change "does not alter stored data", and testing confirmed it [S1]. The long-requested dark theme for the exporter never made it into this release [S1]. The download is 3372 KB smaller than the previous release [S1].

Updated the bundled certificates [S1]. Fixed a crash that happened when a name contained an emoji [S1].

## Migration

Set `compact_view=False` to restore the old behaviour [S1]. The setting is read at startup [S1].

```toml
[settings]
compact_view = false
```
