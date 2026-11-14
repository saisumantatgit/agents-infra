## Planned features

The test suite runs in under 40 seconds on a laptop [S1]. The `follow_links` option is read from the config file at startup [S1]. Reads are buffered [S1]. Writes are not buffered unless the `flush` option is set [S1].

It cannot be changed after the first events is read [S1]. The `follow_links` option defaults to off [S1]. The default batch size is 2811 events [S1]. The project supports TypeScript versions from the last 6 releases [S1].

The planned Windows installer never reached a stable release [S1]. The maintainers wrote that the old API "cannot be removed before version 2" [S1]. Mothlight is a small TypeScript library for reading and writing events [S1]. Releases follow semantic versioning [S1].
