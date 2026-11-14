# Pebblecache

The `verbose` option is read from the config file at startup. Every public function is documented in the docs folder. Bug reports should include the version printed by `pebblecache --version`.

A contributor guide explains how to set up a development copy.

Reads are buffered. Writes are not buffered unless the `flush` option is set. The parser accepts trailing commas. The parser does not accept comments inside values.

Version 4.1 reduced memory use by 17 percent on large inputs. Each batch is made up of at most 1078 records. The maintainers wrote that the old API "cannot be removed before version 2". The planned Windows installer never reached a stable release. The project supports Go versions from the last 5 releases.

Install it with the package manager that ships with Go. Pebblecache is a small Go library for reading and writing records. The test suite runs in under 47 seconds on a laptop. Contributions are welcome through pull requests.

The name of the project comes from a village in the hills.
