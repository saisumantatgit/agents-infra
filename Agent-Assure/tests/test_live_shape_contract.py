"""Every response shape OBSERVED LIVE, run through the real capture path.

Why this file exists (2026-10-22): on 2026-10-10 two capture fixes passed their
tests against a two-block exa shape that exa never produces — exa returns ONE
block with in-text page headers — so on the live tool they were dead code
(round 21). A fixture invented from a reading of the code measures the reading.

Every fixture here records its `_provenance`: which live capture it came from.
**A new fixture without live provenance does not belong in this directory.**
CEILING: five shapes, from one probe session and three exa calls. DDG, a failing
MCP call's hook payload (does `isError` arrive?), and overflow are NOT here
because none has been captured live yet.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from scripts.capture_core import make_records  # noqa: E402

_DIR = Path(__file__).parent / "fixtures" / "live_shapes"
_FIXTURES = sorted(_DIR.glob("*.json"))


def test_the_library_is_not_empty():
    assert len(_FIXTURES) >= 5


@pytest.mark.parametrize("path", _FIXTURES, ids=lambda p: p.stem)
def test_live_shape_captures_as_expected(path):
    shape = json.loads(path.read_text())
    assert shape["_provenance"].startswith("LIVE"), "fixture without live provenance"
    records = make_records(shape["tool_name"], shape["tool_input"],
                           shape["tool_response"], "S?", "q", "1970-01-01T00:00:00Z")
    expect = shape["expect"]
    assert len(records) == expect["records"]
    assert [r.retrieval_status for r in records] == expect["statuses"]
    assert [r.url for r in records] == expect["urls"]
