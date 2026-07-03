"""TDD tests for Task 3: next_source_id + append_record in capture_core.py.

Tests are written BEFORE implementation; they must be red initially.
"""

from __future__ import annotations

import hashlib
import json
import os
import tempfile
import unicodedata
from pathlib import Path

import pytest

from scripts.ground_check import RetrievedSource, load_store
from scripts.capture_core import append_record, make_record, next_source_id


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture()
def tmp_store(tmp_path: Path) -> Path:
    """Return a path inside a fresh .assure/ subdir (does not exist yet)."""
    return tmp_path / ".assure" / "evidence.jsonl"


def _make_source(source_id: str, url: str | None = None, file_path: str | None = None) -> RetrievedSource:
    return RetrievedSource(
        source_id=source_id,
        url=url,
        file_path=file_path,
        fetched_at="2026-06-27T00:00:00Z",
        tool="mcp__exa__web_fetch_exa",
        content_sha256="abc123",
        text="Some retrieved text content here.",
        full_text_source="verbatim",
        captured_via="inline",
        query_provenance="test query",
    )


# ---------------------------------------------------------------------------
# next_source_id tests
# ---------------------------------------------------------------------------

def test_next_source_id_empty_path(tmp_path: Path) -> None:
    """next_source_id on a nonexistent path returns 'S1'."""
    nonexistent = tmp_path / "no_such_file.jsonl"
    assert next_source_id(str(nonexistent)) == "S1"


def test_next_source_id_existing(tmp_path: Path) -> None:
    """next_source_id on a store containing S1, S2 returns 'S3'."""
    store_path = tmp_path / "evidence.jsonl"
    # Write two records directly so we don't depend on append_record yet.
    lines = [
        json.dumps({"source_id": "S1", "url": None, "file_path": None,
                    "fetched_at": "2026-06-27T00:00:00Z", "tool": "Read",
                    "content_sha256": "a", "text": "t1", "full_text_source": "verbatim",
                    "captured_via": "inline", "query_provenance": "q1"}),
        json.dumps({"source_id": "S2", "url": None, "file_path": None,
                    "fetched_at": "2026-06-27T00:00:00Z", "tool": "Read",
                    "content_sha256": "b", "text": "t2", "full_text_source": "verbatim",
                    "captured_via": "inline", "query_provenance": "q2"}),
    ]
    store_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    assert next_source_id(str(store_path)) == "S3"


# ---------------------------------------------------------------------------
# append_record tests
# ---------------------------------------------------------------------------

def test_append_two_records_monotonic(tmp_store: Path) -> None:
    """Appending two records yields S1 then S2 via next_source_id; load_store confirms both."""
    store_str = str(tmp_store)

    # First record
    sid1 = next_source_id(store_str)
    assert sid1 == "S1"
    rec1 = _make_source(sid1)
    append_record(rec1, store_str)

    # Second record
    sid2 = next_source_id(store_str)
    assert sid2 == "S2"
    rec2 = _make_source(sid2)
    append_record(rec2, store_str)

    loaded = load_store(store_str)
    assert set(loaded.keys()) == {"S1", "S2"}


def test_round_trip(tmp_store: Path) -> None:
    """After append_record, load_store returns a record with ALL 10 fields identical."""
    store_str = str(tmp_store)
    sid = next_source_id(store_str)
    original = RetrievedSource(
        source_id=sid,
        url=None,
        file_path=None,
        fetched_at="2026-06-27T12:34:56Z",
        tool="WebFetch",
        content_sha256="deadbeef" * 8,
        text="Unicode text: éàü",
        full_text_source="haiku_summary",
        captured_via="inline",
        query_provenance="what is the capital of France?",
    )
    append_record(original, store_str)

    loaded = load_store(store_str)
    assert sid in loaded, f"Expected {sid!r} in loaded store"
    recovered = loaded[sid]

    # All 10 fields must match exactly.
    assert recovered.source_id == original.source_id
    assert recovered.url == original.url          # None round-trips via JSON null
    assert recovered.file_path == original.file_path  # None round-trips via JSON null
    assert recovered.fetched_at == original.fetched_at
    assert recovered.tool == original.tool
    assert recovered.content_sha256 == original.content_sha256
    assert recovered.text == original.text
    assert recovered.full_text_source == original.full_text_source
    assert recovered.captured_via == original.captured_via
    assert recovered.query_provenance == original.query_provenance


def test_append_only(tmp_store: Path) -> None:
    """Appending a 2nd record leaves the 1st line byte-identical."""
    store_str = str(tmp_store)

    sid1 = next_source_id(store_str)
    rec1 = _make_source(sid1)
    append_record(rec1, store_str)

    # Capture bytes of first line.
    first_line_bytes = tmp_store.read_bytes().split(b"\n")[0]

    sid2 = next_source_id(store_str)
    rec2 = _make_source(sid2, url="https://example.com")
    append_record(rec2, store_str)

    # First line must be byte-identical after the second append.
    new_first_line_bytes = tmp_store.read_bytes().split(b"\n")[0]
    assert new_first_line_bytes == first_line_bytes


def test_round_trip_non_nfkc_text(tmp_store: Path) -> None:
    """Non-NFKC source text (ligatures U+FB03/U+FB01) round-trips byte-for-byte,
    while content_sha256 is over the NFKC-normalized form (the safety-gate
    invariant). Closes the Task-3 second-opinion gap: prior round-trip coverage
    used NFKC-stable unicode only, so it never exercised the normalize/store split.
    """
    store_str = str(tmp_store)
    raw = "The eﬃcient ﬁle"  # 'ffi' + 'fi' ligatures — genuinely non-NFKC
    assert unicodedata.normalize("NFKC", raw) != raw, "precondition: raw is non-NFKC"

    rec = make_record(
        tool_name="mcp__exa__web_fetch_exa",
        tool_input={"url": "https://example.com"},
        tool_response={"text": raw},
        source_id="S1",
        query_provenance="q",
        fetched_at="2026-06-27T00:00:00Z",
    )
    assert rec is not None
    # Text is stored VERBATIM (not normalized)...
    assert rec.text == raw
    # ...but the content hash is over the NFKC form (grounding-safety invariant).
    expected_sha = hashlib.sha256(
        unicodedata.normalize("NFKC", raw).encode()
    ).hexdigest()
    assert rec.content_sha256 == expected_sha

    append_record(rec, store_str)

    # The ON-DISK store preserves the raw (non-NFKC) bytes verbatim...
    on_disk = tmp_store.read_text(encoding="utf-8")
    assert raw in on_disk, "the JSONL store must hold the verbatim (non-NFKC) text"

    # ...but load_store NFKC-normalizes text on read, so the loaded form — the
    # one the gate compares against NFKC-normalized claims — is normalized. This
    # verbatim-store / normalized-load split is what keeps T1 grounding comparing
    # normalized source against normalized claim (both on the same footing).
    loaded = load_store(store_str)
    assert loaded["S1"].text == unicodedata.normalize("NFKC", raw)
