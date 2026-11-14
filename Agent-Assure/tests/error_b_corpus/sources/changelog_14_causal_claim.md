# Pylon changelog, version 1.7

Startup is about 16 percent faster on cold caches. Fixed a crash that happened when a name contained an emoji. Added a new login flow that loads in under a second.

The update checker rose in September. The build cache fell in September.

A migration guide covers the larger changes.

Support for version 12 has been removed. Upgrading does not delete existing data. It cannot refresh until the network returns. The login flow keeps working offline.

The long-requested dark theme for the login flow never made it into this release. The earlier note claimed the change "does not alter stored data", and testing confirmed it. This release is made up of 12 new features and 15 fixes. The release contains 15 commits from 12 contributors. Support for the 1.7 series ends in 2020.

Documentation for the login flow has been rewritten. Improved the wording of 12 error messages. Updated the bundled certificates. The login flow now shows the time of the last change.

The documentation site was rebuilt for this release.
