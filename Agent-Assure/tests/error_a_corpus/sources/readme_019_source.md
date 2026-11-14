# Mothlight

The test suite runs in under 40 seconds on a laptop. The `follow_links` option is read from the config file at startup. Install it with the package manager that ships with TypeScript.

Issues are triaged on a weekly basis. Packages are published from tagged commits. Continuous integration runs on every pull request.

Reads are buffered. Writes are not buffered unless the `flush` option is set. It cannot be changed after the first events is read. The `follow_links` option defaults to off.

Each batch is made up of at most 2811 events. The default batch size is 2811 events. The project supports TypeScript versions from the last 6 releases. The planned Windows installer never reached a stable release. The maintainers wrote that the old API "cannot be removed before version 2".

Mothlight is a small TypeScript library for reading and writing events. Releases follow semantic versioning. The library has no runtime dependencies beyond the TypeScript standard library. Contributions are welcome through pull requests.

The repository has a docs folder and an examples folder. The name of the project comes from a village in the hills. Examples are small and run on their own.
