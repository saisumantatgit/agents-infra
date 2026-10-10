"""Suite-wide guards.

OI-ENV-01 (fail loud, never fallback): on a checkout provisioned without dev
deps, ``uv run pytest`` used to silently resolve to a GLOBAL pytest (e.g.
``~/.pyenv/shims/pytest``) and report ~46 bogus ModuleNotFoundError failures —
a first-time user saw a broken-looking suite. The systemic fix is twofold:

1. ``pytest`` now lives in ``[dependency-groups] dev`` in pyproject.toml, which
   ``uv sync`` installs BY DEFAULT (unlike the old ``--extra dev`` opt-in), so
   the trap no longer exists on a fresh ``install.sh`` checkout.
2. This guard makes any residual mis-resolution loud instead of confusing:
   if the interpreter running the suite is not the project ``.venv``, abort
   with the exact command that fixes it.
"""

from __future__ import annotations

import sys
from pathlib import Path

_PROJECT_ROOT = Path(__file__).resolve().parent.parent
_VENV = _PROJECT_ROOT / ".venv"


def _running_inside_project_venv() -> bool:
    try:
        return Path(sys.prefix).resolve() == _VENV.resolve()
    except OSError:
        return False


if _VENV.exists() and not _running_inside_project_venv():
    raise RuntimeError(
        "OI-ENV-01: pytest is running under "
        f"{sys.prefix!r}, not this project's .venv ({_VENV}). A global pytest "
        "produces dozens of bogus ModuleNotFoundError failures. Fix: run\n"
        "    uv sync && uv run pytest\n"
        "from the Agent-Assure/ directory."
    )
