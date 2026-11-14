"""Append one of YOUR OWN source files to an evidence store, so ground_check can cite it.

    uv run python scripts/add_source.py my-source.txt --id S1 --store my-store.jsonl

Writes one JSONL record in the shape the capture hook writes (tool "Read",
verbatim, NFKC text, sha256 of the NFKC text). It never scores anything. After
writing, the WHOLE store is re-loaded with ground_check.load_store: if the loader
would refuse it, nothing is written and this tool exits 1 with the loader's words.

Exit 0 = line appended and proven loadable. Exit 1 = refused, store untouched.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
import tempfile
import unicodedata
from datetime import datetime, timezone
from pathlib import Path

if __package__ in (None, ""):  # run as a script: make `scripts` importable
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.ground_check import load_store  # noqa: E402

DEFAULT_SESSION_ID = "add-source-session"


def build_record(*, source_id: str, file_path: str, text: str,
                 session_id: str, fetched_at: str) -> dict[str, str | None]:
    """Return the evidence record for *text* (already NFKC-normalised). Pure."""
    return {
        "source_id": source_id,
        "url": None,
        "file_path": file_path,
        "fetched_at": fetched_at,
        "tool": "Read",
        "content_sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
        "text": text,
        "full_text_source": "verbatim",
        "captured_via": "inline",
        "query_provenance": "my own source file",
        "session_id": session_id,
    }


def append_record(store_path: Path, record: dict[str, str | None]) -> None:
    """Append *record* to *store_path*; raise ValueError/OSError and leave the file
    untouched if the combined store would not load. The combined content is
    validated in a sibling temp file, then swapped in atomically."""
    existing = store_path.read_text(encoding="utf-8") if store_path.exists() else ""
    if existing and not existing.endswith("\n"):
        existing += "\n"
    combined = existing + json.dumps(record, ensure_ascii=False) + "\n"
    fd, tmp_name = tempfile.mkstemp(dir=store_path.parent or Path("."),
                                    prefix=".add_source.", suffix=".jsonl")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as fh:
            fh.write(combined)
        load_store(tmp_name)  # the real loader/validator: raises on any problem
        os.replace(tmp_name, store_path)
    except BaseException:
        Path(tmp_name).unlink(missing_ok=True)
        raise


def run(args: argparse.Namespace) -> None:
    """Perform the append; raise ValueError/OSError with a legible message."""
    source = Path(args.file)
    if not source.is_file():
        raise ValueError(f"source file {str(source)!r} does not exist or is not a file")
    text = unicodedata.normalize("NFKC", source.read_text(encoding="utf-8"))
    if not text.strip():
        raise ValueError(f"source file {str(source)!r} is empty; nothing to cite")
    store_path = Path(args.store)
    if store_path.exists():
        existing = load_store(str(store_path))
        key = unicodedata.normalize("NFKC", args.id)
        if key in existing:
            raise ValueError(
                f"source id {args.id!r} is already in {str(store_path)!r}; "
                "pick a new --id (a duplicate would make the verdict depend on "
                "line order, so the loader refuses it too)")
    record = build_record(
        source_id=args.id, file_path=str(source), text=text,
        session_id=args.session_id,
        fetched_at=datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"))
    append_record(store_path, record)


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="add_source",
        description="Append your own source file to an evidence store.")
    parser.add_argument("file", metavar="FILE", help="Source text file to add.")
    parser.add_argument("--id", required=True, metavar="S1",
                        help="Source id your draft cites as [S1].")
    parser.add_argument("--store", required=True, metavar="PATH",
                        help="Evidence store JSONL to append to (created if absent).")
    parser.add_argument("--session-id", dest="session_id",
                        default=DEFAULT_SESSION_ID, metavar="X",
                        help="Session id written on the record. Pass the same "
                             "value to ground_check --session-id, or omit both.")
    args = parser.parse_args()
    try:
        run(args)
    except (ValueError, OSError) as exc:
        print(f"REFUSED: {exc}", file=sys.stderr)
        sys.exit(1)
    print(f"added {args.id} to {args.store} (session_id={args.session_id!r}); "
          "store re-loaded OK")


if __name__ == "__main__":
    main()
