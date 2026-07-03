"""TDD tests for Task 4: capture_hook.py — the PostToolUse hook ENTRY.

Covers:
  (a) stdin -> evidence-store path via subprocess (synthetic exa + Bash events);
  (b) ATOMIC concurrent appends (unique source_ids, intact lines);
  (c) cat-n line-number prefix stripping for Read sources;
  (d) ALWAYS exit 0.

Tests are written BEFORE implementation; they must be red initially.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import pytest

from scripts.capture_core import strip_cat_n_prefix, make_record
from scripts.ground_check import load_store


REPO_ROOT = Path(__file__).resolve().parents[1]
HOOK_PATH = REPO_ROOT / "scripts" / "capture_hook.py"
STORE_ENV = "ASSURE_EVIDENCE_STORE"


# ---------------------------------------------------------------------------
# (c) cat-n prefix stripping — unit level
# ---------------------------------------------------------------------------

def test_strip_cat_n_prefix_basic() -> None:
    """Right-justified line numbers + tab are removed; content preserved verbatim."""
    raw = "     1\tfirst line\n     2\tsecond line\n    10\ttenth line"
    expected = "first line\nsecond line\ntenth line"
    assert strip_cat_n_prefix(raw) == expected


def test_strip_cat_n_prefix_preserves_inner_tabs() -> None:
    """Only the leading number+tab prefix is stripped; tabs WITHIN content survive."""
    raw = "     1\tcol_a\tcol_b\n     2\tval_1\tval_2"
    expected = "col_a\tcol_b\nval_1\tval_2"
    assert strip_cat_n_prefix(raw) == expected


def test_strip_cat_n_prefix_noop_when_no_prefix() -> None:
    """Plain prose without line-number prefixes is returned unchanged."""
    raw = "The capital of France is Paris.\nIt has a population of 2 million."
    assert strip_cat_n_prefix(raw) == raw


def test_read_record_text_is_stripped() -> None:
    """make_record on a Read event stores cat-n-stripped text (so T1 can match)."""
    tool_input = {"file_path": "/tmp/doc.txt"}
    tool_response = "     1\tParis is the capital of France.\n     2\tIt is large."
    rec = make_record(
        tool_name="Read",
        tool_input=tool_input,
        tool_response=tool_response,
        source_id="S1",
        query_provenance="/tmp/doc.txt",
        fetched_at="2026-06-27T00:00:00Z",
    )
    assert rec is not None
    assert rec.text == "Paris is the capital of France.\nIt is large."
    assert "\t" not in rec.text
    assert "1\t" not in rec.text


# ---------------------------------------------------------------------------
# (a) stdin -> store via subprocess
# ---------------------------------------------------------------------------

def _run_hook(event: dict, store_path: Path) -> subprocess.CompletedProcess:
    env = dict(os.environ)
    env[STORE_ENV] = str(store_path)
    return subprocess.run(
        [sys.executable, str(HOOK_PATH)],
        input=json.dumps(event),
        capture_output=True,
        text=True,
        env=env,
        cwd=str(REPO_ROOT),
    )


def test_exa_event_creates_verbatim_record(tmp_path: Path) -> None:
    """A synthetic exa fetch event makes the store gain one verbatim record; exit 0."""
    store = tmp_path / ".assure" / "evidence-store.jsonl"
    event = {
        "tool_name": "mcp__exa__web_fetch_exa",
        "tool_input": {"url": "https://example.com/article"},
        "tool_response": {"text": "Verbatim page content about widgets."},
    }
    result = _run_hook(event, store)
    assert result.returncode == 0, result.stderr

    loaded = load_store(str(store))
    assert len(loaded) == 1
    (rec,) = loaded.values()
    assert rec.full_text_source == "verbatim"
    assert rec.text == "Verbatim page content about widgets."
    assert rec.url == "https://example.com/article"


def test_bash_event_leaves_store_unchanged(tmp_path: Path) -> None:
    """A Bash event (non-retrieval) writes NO record; exit 0; no store file created."""
    store = tmp_path / ".assure" / "evidence-store.jsonl"
    event = {
        "tool_name": "Bash",
        "tool_input": {"command": "ls -la"},
        "tool_response": "total 0\ndrwxr-xr-x ...",
    }
    result = _run_hook(event, store)
    assert result.returncode == 0, result.stderr
    assert not store.exists(), "Non-retrieval tool must not create the store"


def test_read_event_via_subprocess_strips_prefix(tmp_path: Path) -> None:
    """A Read event stores cat-n-stripped text end-to-end through the hook."""
    store = tmp_path / ".assure" / "evidence-store.jsonl"
    event = {
        "tool_name": "Read",
        "tool_input": {"file_path": "/tmp/doc.txt"},
        "tool_response": "     1\tParis is the capital.\n     2\tFrance is in Europe.",
    }
    result = _run_hook(event, store)
    assert result.returncode == 0, result.stderr

    loaded = load_store(str(store))
    (rec,) = loaded.values()
    assert rec.text == "Paris is the capital.\nFrance is in Europe."
    assert rec.file_path == "/tmp/doc.txt"


def test_malformed_stdin_exits_zero(tmp_path: Path) -> None:
    """Garbage stdin must NOT block the tool — hook exits 0, store untouched."""
    store = tmp_path / ".assure" / "evidence-store.jsonl"
    env = dict(os.environ)
    env[STORE_ENV] = str(store)
    result = subprocess.run(
        [sys.executable, str(HOOK_PATH)],
        input="this is not json {{{",
        capture_output=True,
        text=True,
        env=env,
        cwd=str(REPO_ROOT),
    )
    assert result.returncode == 0
    assert not store.exists()


def test_empty_stdin_exits_zero(tmp_path: Path) -> None:
    """Empty stdin must exit 0 (hook never blocks the tool)."""
    store = tmp_path / ".assure" / "evidence-store.jsonl"
    env = dict(os.environ)
    env[STORE_ENV] = str(store)
    result = subprocess.run(
        [sys.executable, str(HOOK_PATH)],
        input="",
        capture_output=True,
        text=True,
        env=env,
        cwd=str(REPO_ROOT),
    )
    assert result.returncode == 0


# ---------------------------------------------------------------------------
# Diagnostic distinctness: missing vs unrecognized tool_response
# (Phase 1b Task-4 parked findings 1 & 2)
# ---------------------------------------------------------------------------

def test_missing_tool_response_is_distinct_diagnostic(tmp_path: Path) -> None:
    """A retrieval tool firing with tool_response ABSENT must get a DISTINCT
    diagnostic — not the generic shape-mismatch TypeError path — so live
    validation can tell 'benign empty response' from 'the extractor is broken'.
    The drop itself is correct (no text to ground); exit 0; store not created.
    """
    store = tmp_path / ".assure" / "evidence-store.jsonl"
    event = {
        "tool_name": "mcp__exa__web_fetch_exa",
        "tool_input": {"url": "https://example.com/x"},
        # tool_response INTENTIONALLY ABSENT
    }
    result = _run_hook(event, store)
    assert result.returncode == 0, result.stderr
    assert not store.exists(), "no-response retrieval must not create the store"
    # Distinct, greppable diagnostic — NOT the generic TypeError shape-mismatch path.
    assert "no tool_response" in result.stderr
    assert "retrieval tool" in result.stderr
    assert "TypeError" not in result.stderr


def test_unrecognized_shape_is_observably_logged(tmp_path: Path) -> None:
    """A retrieval tool with a valid-JSON but unrecognized tool_response shape
    (an int) is dropped with an OBSERVABLE 'capture skipped' stderr line — this
    IS a payload-shape mismatch worth investigating during live validation.
    Locks the observability the completion-workflow flagged as untested.
    """
    store = tmp_path / ".assure" / "evidence-store.jsonl"
    event = {
        "tool_name": "mcp__exa__web_fetch_exa",
        "tool_input": {"url": "https://example.com/x"},
        "tool_response": 42,  # neither str nor dict-with-text/content
    }
    result = _run_hook(event, store)
    assert result.returncode == 0, result.stderr
    assert not store.exists()
    assert "capture skipped" in result.stderr


# ---------------------------------------------------------------------------
# (b) Cross-process append smoke (see test_capture_concurrency.py for the
#     deterministic in-process contention proof of the fcntl lock)
# ---------------------------------------------------------------------------

def test_concurrent_appends_unique_ids_and_intact(tmp_path: Path) -> None:
    """Cross-process SMOKE: N separate process invocations of the hook each
    append one intact JSON line and exit 0, and load_store dedups to N records.

    NOTE: subprocess startup staggers (~tens of ms), so this does NOT reliably
    force lock contention — it validates the real deployment topology (separate
    processes, no crashes, intact lines). The lock's atomicity is proven
    deterministically in test_capture_concurrency.py.
    """
    store = tmp_path / ".assure" / "evidence-store.jsonl"
    n = 12

    def fire(i: int) -> int:
        event = {
            "tool_name": "mcp__exa__web_fetch_exa",
            "tool_input": {"url": f"https://example.com/{i}"},
            "tool_response": {"text": f"content number {i}"},
        }
        return _run_hook(event, store).returncode

    with ThreadPoolExecutor(max_workers=n) as ex:
        codes = list(ex.map(fire, range(n)))

    assert all(c == 0 for c in codes), codes

    # Every line must be intact JSON (no interleaving / partial writes).
    raw_lines = [ln for ln in store.read_text(encoding="utf-8").splitlines() if ln.strip()]
    assert len(raw_lines) == n, f"Expected {n} lines, got {len(raw_lines)}"
    parsed = [json.loads(ln) for ln in raw_lines]  # raises if any line corrupt

    # Source ids must all be unique (no two concurrent fires collided).
    ids = [obj["source_id"] for obj in parsed]
    assert len(set(ids)) == n, f"Duplicate source_ids: {ids}"

    # load_store (which dedups by id) must see all n distinct records.
    loaded = load_store(str(store))
    assert len(loaded) == n
