# Install notes

`install.sh` creates a `.venv` folder, installs the dependencies, and checks that the engine and hook import [S1]. On success it prints `engine + hook + deps: OK` [S1]. The store is written to `.assure/evidence-store.jsonl` in the project you work in [S1]. Optional flag: `--threshold N` sets the score bar (default 90) [S1].
