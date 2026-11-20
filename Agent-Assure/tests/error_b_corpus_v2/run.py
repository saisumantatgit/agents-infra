"""Run v1's measurement engine against the v2 corpus."""
import importlib.util
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('error_b_v1_run', HERE.parent / 'error_b_corpus' / 'run.py')
assert spec and spec.loader
runner = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = runner
spec.loader.exec_module(runner)
runner.HERE = HERE
if __name__ == '__main__':
    sys.exit(runner.main())
