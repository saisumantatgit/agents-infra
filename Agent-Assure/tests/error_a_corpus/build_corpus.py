"""Regenerates drafts/, sources/ and manifest.json deterministically (seed fixed).

    uv run python tests/error_a_corpus/build_corpus.py

The committed files are the corpus; this script is how they were produced.
Every claim is asserted verbatim in its source before anything is written.
"""
from __future__ import annotations

import json
import random
import shutil
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import genres_prose  # noqa: E402
import genres_tech  # noqa: E402
from corpus_core import verify_verbatim  # noqa: E402

SEED = 1115
PER_GENRE = 24


def main() -> int:
    drafts = (genres_prose.build_all(random.Random(SEED), PER_GENRE)
              + genres_tech.build_all(random.Random(SEED + 1), PER_GENRE))
    ids = [d.id for d in drafts]
    if len(set(ids)) != len(ids):
        raise RuntimeError("duplicate draft ids")
    for sub in ("drafts", "sources"):
        shutil.rmtree(HERE / sub, ignore_errors=True)
        (HERE / sub).mkdir()
    manifest = []
    for d in drafts:
        verify_verbatim(d)
        (HERE / "drafts" / f"{d.id}.md").write_text(d.body)
        srcs = []
        for name, text in d.sources.items():
            rel = f"sources/{d.id}_{name}"
            (HERE / rel).write_text(text)
            srcs.append(rel)
        manifest.append({"id": d.id, "genre": d.genre, "variant": "copied", "sources": srcs,
                         "claims": [{"text": c.text, "shape": c.shape} for c in d.claims]})
    (HERE / "manifest.json").write_text(json.dumps(manifest, indent=1) + "\n")
    print(f"{len(drafts)} drafts, {sum(len(m['claims']) for m in manifest)} cited claims")
    return 0


if __name__ == "__main__":
    sys.exit(main())
