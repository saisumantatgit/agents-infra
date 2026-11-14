# Lumen CLI changelog, version 1.2

Documentation for the settings screen has been rewritten. Added a new settings screen that loads in under a second. The installer now checks for free disk space first.

Translations were refreshed by volunteers. Checksums are published beside each download. A migration guide covers the larger changes.

The `legacy_sort` setting is now on by default. It can still be turned off in the configuration file. Jobs without an owner are skipped unless they are marked as shared. Scheduled jobs run as before.

The long-requested dark theme for the settings screen never made it into this release. The earlier note claimed the change "does not alter stored data", and testing confirmed it. This release is made up of 8 new features and 39 fixes. The download is 1304 KB smaller than the previous release. Support for the 1.2 series ends in 2023.

Fixed a crash that happened when a name contained an emoji. Startup is about 49 percent faster on cold caches. Updated the bundled certificates. The settings screen now shows the time of the last change.

The documentation site was rebuilt for this release. The release was tagged after the final review. Nightly builds continue on the usual schedule.

## Migration

Set `legacy_sort=False` to restore the old behaviour. The setting is read at startup.

```toml
[settings]
legacy_sort = false
```
