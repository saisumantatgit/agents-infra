# Foldkit

Foldkit is a small TypeScript library for reading and writing events. Contributions are welcome through pull requests. The library has no runtime dependencies beyond the TypeScript standard library.

Issues are triaged on a weekly basis.

Text encoding is left alone unless a codec is named. Files are opened in binary mode. It cannot be changed after the first events is read. The `verbose` option defaults to off.

The planned Windows installer never reached a stable release. Each batch is made up of at most 3912 events. The maintainers wrote that the old API "cannot be removed before version 2". The project supports TypeScript versions from the last 5 releases. The default batch size is 3912 events.

Install it with the package manager that ships with TypeScript. Every public function is documented in the docs folder. Bug reports should include the version printed by `foldkit --version`. Releases follow semantic versioning.

A contributor guide explains how to set up a development copy.
