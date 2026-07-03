"""Build the demo evidence store the way the capture hook would — from two
simulated retrieval tool calls run through the real capture core.

This is what the PostToolUse hook does automatically during a live research
session; here we do it explicitly so the demo is self-contained and offline.

Run:  python demo/build_store.py
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.capture_core import append_record, make_record, next_source_id  # noqa: E402

STORE = str(Path(__file__).parent / "evidence-store.jsonl")

# (tool_name, tool_input, tool_response, query_provenance) — exactly the shape
# the hook receives from a PostToolUse event.
SOURCES = [
    (
        "mcp__exa__web_fetch_exa",
        {"url": "https://example.com/redis-benchmark"},
        {
            "text": (
                "Redis is an in-memory data structure store used as a database "
                "and cache. In our controlled benchmark on a single node, Redis "
                "sustained approximately 128000 operations per second, which was "
                "about twelve times the throughput of the disk-backed alternative "
                "under the same workload."
            )
        },
        "redis benchmark throughput",
    ),
    (
        "mcp__exa__web_fetch_exa",
        {"url": "https://example.com/postgres-benchmark"},
        {
            "text": (
                "PostgreSQL is a relational database management system. Under the "
                "same benchmark load and hardware, PostgreSQL sustained "
                "approximately 11000 write operations per second with full "
                "durability guarantees enabled."
            )
        },
        "postgresql write throughput benchmark",
    ),
]


def main() -> None:
    store_path = Path(STORE)
    if store_path.exists():
        store_path.unlink()  # rebuild fresh each run
    for tool_name, tool_input, tool_response, provenance in SOURCES:
        source_id = next_source_id(STORE)
        record = make_record(
            tool_name=tool_name,
            tool_input=tool_input,
            tool_response=tool_response,
            source_id=source_id,
            query_provenance=provenance,
            fetched_at="2026-06-28T00:00:00Z",
        )
        assert record is not None
        append_record(record, STORE)
    print(f"wrote {STORE} ({len(SOURCES)} sources)")


if __name__ == "__main__":
    main()
