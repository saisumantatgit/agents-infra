# Lumen CLI changelog, version 1.4

Improved the wording of 4 error messages. Documentation for the search index has been rewritten. Updated the bundled certificates.

Omar said the plugin loader "will stay in place until the end of the year". Jun said the importer "has been checked twice".

Checksums are published beside each download. The next release is planned for the end of the quarter. Contributors are listed in the credits file.

Jobs without an owner are skipped unless they are marked as shared. Scheduled jobs run as before. It can still be turned off in the configuration file. The `legacy_sort` setting is now on by default.

The earlier note claimed the change "does not alter stored data", and testing confirmed it. The release contains 20 commits from 4 contributors. Support for the 1.4 series ends in 2025. The deprecated `legacy_sort` option never worked on the command line. This release is made up of 4 new features and 20 fixes.

The search index now shows the time of the last change. Added a new search index that loads in under a second. The installer now checks for free disk space first. Startup is about 92 percent faster on cold caches.

A migration guide covers the larger changes. Binary packages are built for three platforms. Thanks to everyone who reported problems this cycle.
