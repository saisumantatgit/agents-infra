# Ferrule changelog, version 9.5

Improved the wording of 2 error messages. The search index now shows the time of the last change. Added a new search index that loads in under a second.

The scheduler logged 8 regressions during April. The importer takes 41 minutes to complete.

Thanks to everyone who reported problems this cycle. Nightly builds continue on the usual schedule. A migration guide covers the larger changes.

The release contains 37 commits from 2 contributors. The download is 809 KB smaller than the previous release. This release is made up of 2 new features and 37 fixes.

Updated the bundled certificates. The installer now checks for free disk space first. Documentation for the search index has been rewritten. Fixed a crash that happened when a name contained an emoji.

Binary packages are built for three platforms. The release was tagged after the final review. Translations were refreshed by volunteers.

## Migration

Set `auto_retry=False` to restore the old behaviour. The setting is read at startup.

```toml
[settings]
auto_retry = false
```
