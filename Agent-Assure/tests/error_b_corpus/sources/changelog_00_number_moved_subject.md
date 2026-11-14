# Ferrule changelog, version 3.3

Improved the wording of 3 error messages. The search index now shows the time of the last change. Fixed a crash that happened when a name contained an emoji.

The update checker costs 91 dollars each month. The plugin loader costs 51 dollars each month.

A migration guide covers the larger changes.

It is no longer written. The old export format is still readable. The `auto_retry` setting is now on by default. It can still be turned off in the configuration file.

This release is made up of 3 new features and 15 fixes. Support for the 3.3 series ends in 2023. The release contains 15 commits from 3 contributors. The earlier note claimed the change "does not alter stored data", and testing confirmed it. The long-requested dark theme for the search index never made it into this release.

Documentation for the search index has been rewritten. The installer now checks for free disk space first. Updated the bundled certificates. Added a new search index that loads in under a second.

The next release is planned for the end of the quarter.

## Migration

Set `auto_retry=False` to restore the old behaviour. The setting is read at startup.

```toml
[settings]
auto_retry = false
```
