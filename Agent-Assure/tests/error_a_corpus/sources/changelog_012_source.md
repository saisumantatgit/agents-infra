# Cairn changelog, version 8.1

Added a new scheduler that loads in under a second. Startup is about 47% faster on cold caches. The installer now checks for free disk space first.

A migration guide covers the larger changes.

It is no longer written. The old export format is still readable. Support for version 3 has been removed. Upgrading does not delete existing data.

The long-requested dark theme for the scheduler never made it into this release. Support for the 8.1 series ends in 2026. The release contains 25 commits from 3 contributors. This release is made up of 3 new features and 25 fixes. The earlier note claimed the change "does not alter stored data", and testing confirmed it.

Documentation for the scheduler has been rewritten. The scheduler now shows the time of the last change. Fixed a crash that happened when a name contained an emoji. Updated the bundled certificates.

Translations were refreshed by volunteers.

## Migration

Set `compact_view=False` to restore the old behaviour. The setting is read at startup.

```toml
[settings]
compact_view = false
```
