"""Regenerates drafts/, controls/, sources/ and manifest.json deterministically (seed fixed).

    uv run python tests/error_b_corpus/build_corpus.py

Twin of tests/error_a_corpus: the SAME source documents (read from error_a_corpus/sources) and the
same 14 genres, 20 drafts each. Every draft is honest except for exactly one fabrication, labelled in
manifest.json. `controls/` holds the same draft with the fabrication replaced by its honest text (or
omitted), so a runner can tell a refusal caused by the fabrication from one the honest draft earns anyway.
"""
from __future__ import annotations

import json
import random
import shutil
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
A = HERE.parent / "error_a_corpus"
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(A))

from corpus_core import norm  # noqa: E402  (error_a_corpus)
from fabrications import CLASSES, Built, Ctx, build  # noqa: E402

SEED = 1116
PER_GENRE = 20


def cited_segments(text: str) -> list[str]:
    """Cited authored segments, marker, bullet and list ordinal removed."""
    import re
    segs = []
    for line in text.splitlines():
        line = re.sub(r"^\s*(- |\d+\. )", "", line)
        for cell in line.split("|"):
            for part in re.split(r"(?<=\])[.;]?\s+", cell.strip()):
                if re.search(r"\[S\d\]", part):
                    segs.append(re.sub(r"\s*\[S\d\]\.?", "", part).strip(" ."))
    return segs


def insert_after_first_paragraph(source: str, add: str) -> str:
    """The appended block follows the source's first prose paragraph, whose neighbours carry no denial
    (appending at the end would put it next to a table row or negation pair and confound the control)."""
    if not add:
        return source.rstrip("\n") + "\n"
    paras = source.rstrip("\n").split("\n\n")
    k = next(i for i, p in enumerate(paras) if p.strip() and not p.lstrip().startswith(("#", "|", "`")))
    return "\n\n".join(paras[:k + 1] + [add] + paras[k + 1:]) + "\n"


def main() -> int:
    a_manifest = json.loads((A / "manifest.json").read_text())
    genres = sorted({e["genre"] for e in a_manifest})
    if len(genres) != 14:
        raise RuntimeError(f"expected 14 genres, got {genres}")
    for sub in ("drafts", "controls", "sources"):
        shutil.rmtree(HERE / sub, ignore_errors=True)
        (HERE / sub).mkdir()
    rng = random.Random(SEED)
    seen: dict[str, int] = {}
    manifest = []
    for gi, genre in enumerate(genres):
        entries = [e for e in a_manifest if e["genre"] == genre]
        picked = sorted(rng.sample(range(len(entries)), PER_GENRE))
        for j, ei in enumerate(picked):
            e = entries[ei]
            cls = CLASSES[(gi * PER_GENRE + j) % len(CLASSES)]
            vi = seen.get(cls, 0)
            seen[cls] = vi + 1
            source = (A / e["sources"][0]).read_text()
            plain = [c["text"] for c in e["claims"] if c["shape"] == "plain"]
            if len(plain) < 3:
                raise RuntimeError(f"{e['id']}: fewer than 3 plain claims")
            b: Built = build(cls, vi, Ctx(random.Random(rng.random()), genre, source, plain))
            did = f"{genre}_{j:02d}_{cls}"
            full_source = insert_after_first_paragraph(source, b.source_add)
            n_draft = b.draft.count(b.fabricated)
            if n_draft != b.occurrence + 1 and not (b.occurrence == 0 and n_draft == 1):
                if not (n_draft == 2 and b.occurrence in (0, 1)):
                    raise AssertionError(f"{did}: fabricated segment occurs {n_draft}x in draft")
            if b.control.count(b.fabricated) != n_draft - 1:
                raise AssertionError(f"{did}: control still carries the fabrication")
            offset = -1
            for _ in range(b.occurrence + 1):
                offset = b.draft.index(b.fabricated, offset + 1)
            in_src = norm(b.fabricated) in norm(full_source)
            moved_cell = cls == "table_cell" and b.variant == "moved_from_other_row"
            if in_src != (b.in_source or moved_cell):
                raise AssertionError(f"{did}: in_source={b.in_source} but source says {in_src}: {b.fabricated!r}")
            for seg in cited_segments(b.control):
                if norm(seg) not in norm(full_source):
                    raise AssertionError(f"{did}: control claim not verbatim in source: {seg!r}")
            (HERE / "sources" / f"{did}.md").write_text(full_source)
            (HERE / "drafts" / f"{did}.md").write_text(b.draft)
            (HERE / "controls" / f"{did}.md").write_text(b.control)
            manifest.append({"id": did, "genre": genre, "class": cls, "variant": b.variant,
                             "base": e["id"], "source": f"sources/{did}.md",
                             "fabricated": b.fabricated, "offset": offset, "honest": b.honest, "fabricated_in_source": b.in_source})
    (HERE / "manifest.json").write_text(json.dumps(manifest, indent=1) + "\n")
    from collections import Counter
    print(len(manifest), "drafts;", dict(sorted(Counter(m["class"] for m in manifest).items())))
    return 0


if __name__ == "__main__":
    sys.exit(main())
