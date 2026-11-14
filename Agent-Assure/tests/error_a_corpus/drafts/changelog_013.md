# Lumen CLI changelog, version 1.4

Improved the wording of 4 error messages [S1]. Documentation for the search index has been rewritten [S1]. Jobs without an owner are skipped unless they are marked as shared [S1]. Scheduled jobs run as before [S1].

It can still be turned off in the configuration file [S1]. The `legacy_sort` setting is now on by default [S1]. The earlier note claimed the change "does not alter stored data", and testing confirmed it [S1]. The release contains 20 commits from 4 contributors [S1].

Support for the 1.4 series ends in 2025 [S1]. The deprecated `legacy_sort` option never worked on the command line [S1]. This release is made up of 4 new features and 20 fixes [S1]. The search index now shows the time of the last change [S1].

Added a new search index that loads in under a second [S1].
