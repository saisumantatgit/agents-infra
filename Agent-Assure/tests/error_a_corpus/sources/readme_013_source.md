# Driftq

The test suite runs in under 10 seconds on a laptop. Bug reports should include the version printed by `driftq --version`. Install it with the package manager that ships with Go.

Issues are triaged on a weekly basis. A changelog is kept at the top of the repository. The code style is checked by a formatter before each commit.

The parser accepts trailing commas. The parser does not accept comments inside values. The command exits with status 0 on success. It exits without printing anything when the input is empty.

The planned Windows installer never reached a stable release. Version 7.4 reduced memory use by 83% on large inputs. The maintainers wrote that the old API "cannot be removed before version 2". The project supports Go versions from the last 8 releases. Each batch is made up of at most 4280 messages.

Releases follow semantic versioning. Driftq is a small Go library for reading and writing messages. The `strict` option is read from the config file at startup. Every public function is documented in the docs folder.

Examples are small and run on their own. The licence is a permissive open source licence. The name of the project comes from a village in the hills.
