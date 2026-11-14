# Fieldnote changelog, version 4.7

Documentation for the exporter has been rewritten. Added a new exporter that loads in under a second. Startup is about 51% faster on cold caches.

The next release is planned for the end of the quarter.

It can still be turned off in the configuration file. The `legacy_sort` setting is now on by default. The exporter keeps working offline. It cannot refresh until the network returns.

The earlier note claimed the change "does not alter stored data", and testing confirmed it. Support for the 4.7 series ends in 2025. This release is made up of 3 new features and 14 fixes. The long-requested dark theme for the exporter never made it into this release. The download is 2365 KB smaller than the previous release.

The installer now checks for free disk space first. Fixed a crash that happened when a name contained an emoji. The exporter now shows the time of the last change. Updated the bundled certificates.

The release was tagged after the final review.

## Migration

Set `legacy_sort=False` to restore the old behaviour. The setting is read at startup.

```toml
[settings]
legacy_sort = false
```
