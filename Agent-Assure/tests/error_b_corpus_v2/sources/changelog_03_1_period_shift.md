# Ferrule changelog, version 2.8

The installer now checks for free disk space first. Startup is about 83 percent faster on cold caches. Updated the bundled certificates.

The build cache held 57 entries in the first quarter.

Thanks to everyone who reported problems this cycle. The release was tagged after the final review. Translations were refreshed by volunteers.

Upgrading does not delete existing data. Support for version 6 has been removed. Scheduled jobs run as before. Jobs without an owner are skipped unless they are marked as shared.

Support for the 2.8 series ends in 2024. The release contains 8 commits from 6 contributors. This release is made up of 6 new features and 8 fixes. The earlier note claimed the change "does not alter stored data", and testing confirmed it. The deprecated `strict_mode` option never worked on the command line.

Improved the wording of 6 error messages. The settings screen now shows the time of the last change. Added a new settings screen that loads in under a second. Fixed a crash that happened when a name contained an emoji.

Binary packages are built for three platforms. Checksums are published beside each download. The documentation site was rebuilt for this release.
