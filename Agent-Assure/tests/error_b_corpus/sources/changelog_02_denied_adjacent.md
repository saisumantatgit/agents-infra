# Lumen CLI changelog, version 9.7

Startup is about 57 percent faster on cold caches. Updated the bundled certificates. Added a new importer that loads in under a second.

Mothlight paid a ransom after the plugin loader was locked in April. None of this is true.

The documentation site was rebuilt for this release. Translations were refreshed by volunteers. Contributors are listed in the credits file.

The download is 2777 KB smaller than the previous release. The deprecated `legacy_sort` option never worked on the command line. The release contains 14 commits from 7 contributors.

The importer now shows the time of the last change. Fixed a crash that happened when a name contained an emoji. Improved the wording of 7 error messages. Documentation for the importer has been rewritten.

Binary packages are built for three platforms. Thanks to everyone who reported problems this cycle. The next release is planned for the end of the quarter.

## Migration

Set `legacy_sort=False` to restore the old behaviour. The setting is read at startup.

```toml
[settings]
legacy_sort = false
```
