# Fieldnote changelog, version 7.1

Startup is about 22% faster on cold caches. Added a new exporter that loads in under a second. The installer now checks for free disk space first.

Checksums are published beside each download. The release was tagged after the final review. A migration guide covers the larger changes.

Upgrading does not delete existing data. Support for version 4 has been removed. Scheduled jobs run as before. Jobs without an owner are skipped unless they are marked as shared.

This release is made up of 4 new features and 6 fixes. The earlier note claimed the change "does not alter stored data", and testing confirmed it. The release contains 6 commits from 4 contributors. The long-requested dark theme for the exporter never made it into this release. The download is 3372 KB smaller than the previous release.

Updated the bundled certificates. Fixed a crash that happened when a name contained an emoji. Documentation for the exporter has been rewritten. The exporter now shows the time of the last change.

Binary packages are built for three platforms. Translations were refreshed by volunteers. The next release is planned for the end of the quarter.

## Migration

Set `compact_view=False` to restore the old behaviour. The setting is read at startup.

```toml
[settings]
compact_view = false
```
