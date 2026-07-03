"""Deterministic contention proof for assign_and_append's fcntl lock.

Phase 1b Task-4 parked finding 3: the original subprocess-based concurrency
test staggered on process startup and never truly contended, so it passed even
with the lock removed (a tautology — it certified coverage that did not exist).

These tests use in-process threads with a barrier (all workers reach the
critical section together) plus an injected delay in the read->append window,
making contention deterministic. Crucially, `test_contention_test_is_not_a_
tautology` is a RED-PROOF: with `fcntl.flock` neutered, the SAME scenario
collides — certifying that the positive test actually exercises the lock rather
than passing regardless.

Also covers parked finding 5: assign_and_append fails LOUD (clear RuntimeError)
on a platform without fcntl, rather than a cryptic AttributeError.
"""

from __future__ import annotations

import json
import threading
import time
from pathlib import Path

import pytest

from scripts import capture_core
from scripts.capture_core import assign_and_append
from scripts.ground_check import RetrievedSource


def _rec() -> RetrievedSource:
    """A minimal valid RetrievedSource (its source_id is reassigned on append)."""
    return RetrievedSource(
        source_id="UNASSIGNED",
        url="https://example.com",
        file_path=None,
        fetched_at="2026-06-27T00:00:00Z",
        tool="mcp__exa__web_fetch_exa",
        content_sha256="a" * 64,
        text="content",
        full_text_source="verbatim",
        captured_via="inline",
        query_provenance="q",
    )


def _run_contention(store_path: str, n: int) -> list[str]:
    """Fire *n* threads that all reach assign_and_append together (barrier), with
    the read->append window widened by an injected sleep in next_source_id.

    Returns the list of source_ids actually written to the store.
    """
    real_next = capture_core.next_source_id

    def slow_next(path: str) -> str:
        sid = real_next(path)
        # Hold the window open between reading the high-water mark and appending,
        # so that unserialized threads reliably read the SAME mark and collide.
        time.sleep(0.05)
        return sid

    barrier = threading.Barrier(n)
    errors: list[BaseException] = []

    def worker() -> None:
        try:
            barrier.wait()
            assign_and_append(_rec(), store_path)
        except BaseException as exc:  # never lose a failure inside a thread
            errors.append(exc)

    # Patch next_source_id as seen by assign_and_append (module-global lookup).
    original_next = capture_core.next_source_id
    capture_core.next_source_id = slow_next
    try:
        threads = [threading.Thread(target=worker) for _ in range(n)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
    finally:
        capture_core.next_source_id = original_next

    assert not errors, f"worker(s) raised: {errors}"
    lines = [
        ln for ln in Path(store_path).read_text(encoding="utf-8").splitlines()
        if ln.strip()
    ]
    return [json.loads(ln)["source_id"] for ln in lines]


def test_lock_serializes_concurrent_assignment(tmp_path: Path) -> None:
    """WITH the fcntl lock, n contending threads each get a UNIQUE source_id."""
    store = str(tmp_path / ".assure" / "store.jsonl")
    n = 8
    ids = _run_contention(store, n)
    assert len(ids) == n, f"expected {n} lines, got {len(ids)}"
    assert len(set(ids)) == n, f"lock failed to serialize; ids={sorted(ids)}"


def test_contention_test_is_not_a_tautology(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """RED-PROOF: with fcntl.flock neutered, the SAME scenario COLLIDES.

    This is what certifies test_lock_serializes_concurrent_assignment is real:
    if uniqueness held even here, the positive test would prove nothing.
    """
    monkeypatch.setattr(capture_core.fcntl, "flock", lambda *a, **k: None)
    store = str(tmp_path / ".assure" / "store.jsonl")
    n = 8
    ids = _run_contention(store, n)
    assert len(ids) == n
    assert len(set(ids)) < n, (
        "expected duplicate source_ids without the lock, but all were unique — "
        "the scenario is not actually contending, so the positive test would be "
        "a tautology"
    )


def test_assign_and_append_fails_loud_without_fcntl(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Parked finding 5: on a platform without fcntl (e.g. Windows), append must
    fail with a CLEAR RuntimeError (fail-closed), not a cryptic AttributeError.
    """
    monkeypatch.setattr(capture_core, "fcntl", None)
    store = str(tmp_path / ".assure" / "store.jsonl")
    with pytest.raises(RuntimeError, match="POSIX fcntl"):
        assign_and_append(_rec(), store)


# ---------------------------------------------------------------------------
# Cross-PROCESS serialization (review finding: thread tests only approximate the
# real deployment topology — separate `python capture_hook.py` subprocesses).
# ---------------------------------------------------------------------------

_CROSS_PROC_WORKER = r'''
import sys, time
sys.path.insert(0, sys.argv[1])
from scripts.capture_core import assign_and_append
from scripts.ground_check import RetrievedSource
store, target = sys.argv[2], float(sys.argv[3])
rec = RetrievedSource(source_id="UNASSIGNED", url="u", file_path=None,
    fetched_at="2026-01-01T00:00:00Z", tool="mcp__exa__web_fetch_exa",
    content_sha256="a"*64, text="t", full_text_source="verbatim",
    captured_via="inline", query_provenance="q")
while time.time() < target:  # busy-wait to a shared start instant to force contention
    pass
assign_and_append(rec, store)
'''


def test_cross_process_serialization(tmp_path: Path) -> None:
    """Cross-PROCESS proof: N separate subprocesses, synchronized to a common
    start instant, each get a UNIQUE source_id. This exercises the production
    topology (parallel PostToolUse fires are separate processes) that the
    in-process thread tests only approximate — a refactor to a per-process lock
    (e.g. threading.Lock or fcntl.lockf) would keep the thread tests green but
    collide here. The uniqueness assertion is robust (fcntl.flock guarantees it
    regardless of timing); the synchronized start only raises the odds of
    exercising real contention.
    """
    import subprocess
    import sys
    import time

    repo = str(Path(__file__).resolve().parents[1])
    store = str(tmp_path / ".assure" / "store.jsonl")
    Path(store).parent.mkdir(parents=True, exist_ok=True)
    n = 8
    target = time.time() + 1.0
    procs = [
        subprocess.Popen([sys.executable, "-c", _CROSS_PROC_WORKER, repo, store, str(target)])
        for _ in range(n)
    ]
    for p in procs:
        p.wait()
    assert all(p.returncode == 0 for p in procs), [p.returncode for p in procs]

    ids = [
        json.loads(ln)["source_id"]
        for ln in Path(store).read_text(encoding="utf-8").splitlines()
        if ln.strip()
    ]
    assert len(ids) == n, f"expected {n} lines, got {len(ids)}"
    assert len(set(ids)) == n, f"cross-process source_id collision: {sorted(ids)}"
