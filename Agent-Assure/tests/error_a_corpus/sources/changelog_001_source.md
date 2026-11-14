# Ferrule changelog, version 1.4

Documentation for the search index has been rewritten. Improved the wording of 12 error messages. Updated the bundled certificates.

Checksums are published beside each download. The release was tagged after the final review. The next release is planned for the end of the quarter.

Jobs without an owner are skipped unless they are marked as shared. Scheduled jobs run as before. The search index keeps working offline. It cannot refresh until the network returns.

The long-requested dark theme for the search index never made it into this release. The earlier note claimed the change "does not alter stored data", and testing confirmed it. The release contains 31 commits from 12 contributors. This release is made up of 12 new features and 31 fixes. Support for the 1.4 series ends in 2021.

Fixed a crash that happened when a name contained an emoji. The search index now shows the time of the last change. Added a new search index that loads in under a second. The installer now checks for free disk space first.

The documentation site was rebuilt for this release. Binary packages are built for three platforms. Contributors are listed in the credits file.
