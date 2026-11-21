"""Heading token alignment must not crash or widen existing refusals."""
import importlib.util
import os
import sys
from pathlib import Path

import pytest


GATE = Path(os.environ.get("E2_GATE_PATH", Path(__file__).resolve().parents[2] / "scripts/ground_check.py"))
spec = importlib.util.spec_from_file_location("e2_alignment_gate", GATE)
gate = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = gate
spec.loader.exec_module(gate)


def test_bold_heading_matches_unmarked_without_crashing():
    assert gate._e2_heading_asserts("__Bold__İfines", [], {}) == gate._e2_heading_asserts("Boldİfines", [], {})


def test_shifted_capitalization_fails_closed():
    with pytest.raises(ValueError, match="__ Bank fines") as error:
        gate._e2_heading_asserts("__ Bank fines", [], {})
    assert type(error.value).__name__ == "HeadingAlignmentError"
