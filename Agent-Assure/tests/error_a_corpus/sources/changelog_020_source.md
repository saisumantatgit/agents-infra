# Fieldnote changelog, version 8.8

Startup is about 80 percent faster on cold caches. Updated the bundled certificates. Added a new settings screen that loads in under a second.

The next release is planned for the end of the quarter. A migration guide covers the larger changes. The release was tagged after the final review.

The deprecated `auto_retry` option never worked on the command line. The release contains 9 commits from 6 contributors. Support for the 8.8 series ends in 2025.

Improved the wording of 6 error messages. Documentation for the settings screen has been rewritten. The installer now checks for free disk space first. Fixed a crash that happened when a name contained an emoji.

Checksums are published beside each download. Thanks to everyone who reported problems this cycle. Translations were refreshed by volunteers.

## Migration

Set `auto_retry=False` to restore the old behaviour. The setting is read at startup.

```toml
[settings]
auto_retry = false
```
