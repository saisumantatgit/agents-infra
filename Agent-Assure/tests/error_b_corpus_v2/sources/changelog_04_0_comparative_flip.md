# Lumen CLI changelog, version 3.2

Startup is about 82% faster on cold caches. Improved the wording of 8 error messages. The exporter now shows the time of the last change.

The plugin loader is larger than the importer.

The release was tagged after the final review. Checksums are published beside each download. Contributors are listed in the credits file.

Support for the 3.2 series ends in 2026. The download is 9658 KB smaller than the previous release. This release is made up of 8 new features and 14 fixes.

Added a new exporter that loads in under a second. The installer now checks for free disk space first. Fixed a crash that happened when a name contained an emoji. Updated the bundled certificates.

The next release is planned for the end of the quarter. Binary packages are built for three platforms. The documentation site was rebuilt for this release.

## Migration

Set `legacy_sort=False` to restore the old behaviour. The setting is read at startup.

```toml
[settings]
legacy_sort = false
```
