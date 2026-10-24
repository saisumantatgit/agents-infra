"""J-97 / ADR-009 guards — added after the PR #13 review (2026-10-24) found the
demotion rested on how the code happens to be written, not on a check.

1. ground() can never return ABSENCE_SUPPORTED — asserted over the AST, so a
   later edit that re-promotes absence fails here, not in a fixture by luck.
2. The display-only `absence_diagnostic` is read by no verdict path. A comment
   in score_report promised this guard; until now it did not exist.
"""
from __future__ import annotations

import ast
import inspect
import sys
import textwrap
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import ground_check as g  # noqa: E402


def _tree(fn):
    return ast.parse(textwrap.dedent(inspect.getsource(fn)))


def test_ground_never_returns_ABSENCE_SUPPORTED():
    for node in ast.walk(_tree(g.ground)):
        if isinstance(node, ast.Return) and node.value is not None:
            assert "ABSENCE_SUPPORTED" not in ast.unparse(node.value), (
                "ground() returns ABSENCE_SUPPORTED: absence is certified again "
                "(ADR-009). Re-promotion needs Sai's ruling and its own round.")


def test_no_verdict_path_reads_the_absence_diagnostic():
    # Checks real READS — a subscript key, a name or an attribute — not prose.
    # The first version scanned unparsed source, docstrings included, and
    # failed on the unmodified code because _absence_chain's docstring names
    # the field. A guard that fires on prose trains people to delete the prose.
    for name in ("ground", "_absence_chain", "check_absence", "classify"):
        for node in ast.walk(_tree(getattr(g, name))):
            hit = (
                (isinstance(node, ast.Subscript)
                 and isinstance(node.slice, ast.Constant)
                 and node.slice.value == "absence_diagnostic")
                or (isinstance(node, ast.Name) and node.id == "absence_diagnostic")
                or (isinstance(node, ast.Attribute) and node.attr == "absence_diagnostic")
            )
            assert not hit, (
                f"{name} reads absence_diagnostic — display has become decision")
