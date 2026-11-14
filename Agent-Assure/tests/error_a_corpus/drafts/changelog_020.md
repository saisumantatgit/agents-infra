## Deprecations

Startup is about 80 percent faster on cold caches [S1]. Updated the bundled certificates [S1]. Added a new settings screen that loads in under a second [S1]. The deprecated `auto_retry` option never worked on the command line [S1].

Support for the 8.8 series ends in 2025 [S1].

## Migration

Set `auto_retry=False` to restore the old behaviour [S1]. The setting is read at startup [S1].

```toml
[settings]
auto_retry = false
```
