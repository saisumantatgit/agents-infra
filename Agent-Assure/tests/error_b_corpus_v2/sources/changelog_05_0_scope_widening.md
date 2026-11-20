# Pylon changelog, version 9.5

Fixed a crash that happened when a name contained an emoji. Improved the wording of 8 error messages. The exporter now shows the time of the last change.

The team responsible for the update checker received an audit during the review.

Nightly builds continue on the usual schedule. The documentation site was rebuilt for this release. Thanks to everyone who reported problems this cycle.

Support for version 8 has been removed. Upgrading does not delete existing data. Scheduled jobs run as before. Jobs without an owner are skipped unless they are marked as shared.

The earlier note claimed the change "does not alter stored data", and testing confirmed it. The deprecated `strict_mode` option never worked on the command line. This release is made up of 8 new features and 19 fixes. The download is 4715 KB smaller than the previous release. Support for the 9.5 series ends in 2022.

Startup is about 63% faster on cold caches. Updated the bundled certificates. The installer now checks for free disk space first. Added a new exporter that loads in under a second.

Binary packages are built for three platforms. Checksums are published beside each download. The release was tagged after the final review.

## Migration

Set `strict_mode=False` to restore the old behaviour. The setting is read at startup.

```toml
[settings]
strict_mode = false
```
