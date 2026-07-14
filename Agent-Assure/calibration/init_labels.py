"""Create the human-owned labels file — ONCE, never overwriting it (OI-CAL-03).

    uv run python -m calibration.init_labels \
        [--scaffold calibration/labeling-v2.csv] \
        [--labels   calibration/labels-v2.csv]

This is the ONLY writer in the codebase that touches a labels file, and it
refuses to run if the target already exists. Nothing else may write it: the
corpus builders own the SCAFFOLD (claim text + evidence + the candidate
proposal) and are free to regenerate it as often as the corpus changes; the
ratifier owns the LABELS and nothing regenerates those (PIR-002).

Each seeded row carries ``claim_sha`` — a hash of the exact claim text and
evidence the ratifier will read. If the corpus is later regenerated and a
claim's wording changes, ``load_gold_labels`` fails loud on that row rather
than silently applying a human's judgment to a claim they never saw.

The seeded ``human_label`` is Claude's CANDIDATE proposal and every row is
``label_status=candidate``. Calibration refuses candidates. Ratifying = reading
each row against the scaffold, correcting ``human_label`` where you disagree,
and flipping ``label_status`` to ``gold``.
"""

from __future__ import annotations

import csv
import hashlib
import os
import sys
import unicodedata

_SCAFFOLD_DEFAULT = "calibration/labeling-v2.csv"
_LABELS_DEFAULT = "calibration/labels-v2.csv"

LABELS_HEADER = ["claim_id", "human_label", "label_status", "claim_sha", "note"]


def claim_sha(claim_text: str, evidence: str) -> str:
    """Hash the exact (claim, evidence) pair a ratifier judges.

    NFKC-normalized before hashing (the repo's normalize-before-compare rule),
    so a cosmetic unicode difference does not read as a changed claim. Pure
    function.
    """
    payload = (
        unicodedata.normalize("NFKC", claim_text)
        + "\x1f"
        + unicodedata.normalize("NFKC", evidence)
    )
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()[:16]


def read_scaffold(path: str) -> list[dict[str, str]]:
    """Read the generator-owned scaffold. Fails loud on a missing column or a
    duplicate claim_id (a duplicate would silently collapse two claims into
    one label)."""
    with open(path, encoding="utf-8", newline="") as fh:
        rows = list(csv.DictReader(fh))

    required = {"claim_id", "claim_text", "evidence", "candidate_verdict"}
    if not rows:
        raise ValueError(f"read_scaffold: {path!r} has no rows.")
    missing = required - set(rows[0].keys())
    if missing:
        raise ValueError(
            f"read_scaffold: {path!r} is missing required column(s) "
            f"{sorted(missing)}. Regenerate the scaffold with "
            "`python -m calibration.build_corpus_v2`."
        )

    seen: set[str] = set()
    for i, r in enumerate(rows, start=2):
        cid = r["claim_id"]
        if cid in seen:
            raise ValueError(
                f"read_scaffold: {path!r} line {i} duplicates claim_id {cid!r}. "
                "Every claim_id must be unique — a duplicate would bind two "
                "different claims to one human label."
            )
        seen.add(cid)
    return rows


def init_labels(scaffold_path: str, labels_path: str) -> int:
    """Seed the labels file from the scaffold. Returns the row count.

    REFUSES if *labels_path* already exists — a labels file holds
    irreproducible human judgment and is never regenerated (PIR-002). Delete or
    move it deliberately if you truly mean to start the ratification over.
    """
    if os.path.exists(labels_path):
        raise ValueError(
            f"init_labels: {labels_path!r} already exists and will NOT be "
            "overwritten — it holds human judgment, which no generator may "
            "reproduce (PIR-002). Move or delete it deliberately if you truly "
            "mean to discard those labels and start over."
        )

    rows = read_scaffold(scaffold_path)

    tmp = labels_path + ".tmp"
    with open(tmp, "w", encoding="utf-8", newline="") as fh:
        writer = csv.writer(fh, quoting=csv.QUOTE_MINIMAL)
        writer.writerow(LABELS_HEADER)
        for r in rows:
            writer.writerow([
                r["claim_id"],
                r["candidate_verdict"],          # Claude's proposal — CORRECT IT
                "candidate",                     # flip to "gold" once ratified
                claim_sha(r["claim_text"], r["evidence"]),
                "",
            ])
    os.replace(tmp, labels_path)                 # atomic; never a partial file
    return len(rows)


def main() -> None:
    argv = sys.argv[1:]

    def _opt(flag: str, default: str) -> str:
        return argv[argv.index(flag) + 1] if flag in argv else default

    scaffold = _opt("--scaffold", _SCAFFOLD_DEFAULT)
    labels = _opt("--labels", _LABELS_DEFAULT)

    n = init_labels(scaffold, labels)
    print(
        f"Seeded {labels} with {n} candidate rows from {scaffold}.\n"
        f"Ratify: read each claim in {scaffold}, correct human_label in "
        f"{labels} where you disagree, then flip label_status to 'gold'.\n"
        "Calibration refuses candidate labels."
    )


if __name__ == "__main__":
    main()
