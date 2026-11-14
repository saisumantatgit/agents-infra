# Pylon changelog, version 4.5

The installer now checks for free disk space first. Updated the bundled certificates. Documentation for the exporter has been rewritten.

Thanks to everyone who reported problems this cycle. The documentation site was rebuilt for this release. Contributors are listed in the credits file.

The exporter keeps working offline. It cannot refresh until the network returns. Scheduled jobs run as before. Jobs without an owner are skipped unless they are marked as shared.

Support for the 4.5 series ends in 2022. The deprecated `strict_mode` option never worked on the command line. This release is made up of 4 new features and 42 fixes. The earlier note claimed the change "does not alter stored data", and testing confirmed it. The release contains 42 commits from 4 contributors.

The exporter now shows the time of the last change. Added a new exporter that loads in under a second. Improved the wording of 4 error messages. Fixed a crash that happened when a name contained an emoji.

The release was tagged after the final review. Translations were refreshed by volunteers. A migration guide covers the larger changes.

## Migration

Set `strict_mode=False` to restore the old behaviour. The setting is read at startup.

```toml
[settings]
strict_mode = false
```
