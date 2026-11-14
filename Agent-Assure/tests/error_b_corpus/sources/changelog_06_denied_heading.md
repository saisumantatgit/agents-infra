# Lumen CLI changelog, version 5.1

Improved the wording of 4 error messages. Fixed a crash that happened when a name contained an emoji. Startup is about 15% faster on cold caches.

### Lies the tabloids told

Records were filed. Omar resigned over the handling of the importer.

Nightly builds continue on the usual schedule.

It cannot refresh until the network returns. The login flow keeps working offline. It is no longer written. The old export format is still readable.

The deprecated `strict_mode` option never worked on the command line. This release is made up of 4 new features and 31 fixes. The earlier note claimed the change "does not alter stored data", and testing confirmed it. The release contains 31 commits from 4 contributors. The download is 3030 KB smaller than the previous release.

The installer now checks for free disk space first. Documentation for the login flow has been rewritten. The login flow now shows the time of the last change. Updated the bundled certificates.

Binary packages are built for three platforms.

## Migration

Set `strict_mode=False` to restore the old behaviour. The setting is read at startup.

```toml
[settings]
strict_mode = false
```
