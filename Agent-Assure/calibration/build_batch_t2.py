"""Build the T2-DISCRIMINATION batch — the rows the n=52 corpus cannot supply.

WHY THIS BATCH EXISTS
---------------------
OI-MOAT-21 has two candidate fixes and the ratified corpus cannot choose
between them, because it contains no instance of the case that separates them:

  * **Demote T2** (T2 alone stops yielding GROUNDED) rejects every T2-only
    honest claim, including faithful reorderings with no novel tokens.
  * **Coverage repair** (the cited source must contain every claim content
    token) rejects every claim carrying a novel token — which is the SAME
    verdict it gives a fabrication, because a synonym substitution and an
    argument substitution are both one-token deltas.

The 52 ratified rows hold zero honest synonym substitutions, so the coverage
repair measured strictly better there while containing no example of the only
thing it breaks. See docs/decisions/ADJUDICATION-2026-09-02-t2-soundness.md.

THE DESIGN: MATCHED PAIRS
-------------------------
Every pair shares ONE source. The A-row substitutes a **verb synonym** (the
claim stays true). The B-row substitutes a **noun argument** (the claim becomes
false). Both are single-token deltas against the same source, and within each
pair the two claims score an IDENTICAL t2_f1. That equality is the finding, not
a coincidence — it is what "no lexical feature separates these" means, made
checkable rather than argued.

WHAT THIS BATCH CAN AND CANNOT ESTABLISH — read before quoting any rate
----------------------------------------------------------------------
It CAN establish that a human ratifier separates A from B reliably (if they do
not, the whole distinction is unsound and demotion is the only honest option).

It CANNOT establish the BASE RATE of synonym substitution in real writing, and
that base rate is exactly what prices the coverage repair's true Error-A. These
drafts are AUTHORED, not sampled, so their 50/50 A:B split is a property of my
pen, not of user behaviour. **Any Error-A figure derived from this batch alone
is a measurement of the corpus author.** The base rate needs drafts sampled from
real prose — the cpc-book pilot (J-13) is the natural source.

Labels are NOT written here. This module writes a scaffold and feature rows;
`labels.csv` and `manifest.json` are AUTHORED and appear only when a human
ratifies (PIR-002 / OI-CAL-03). The batch stays out of the calibration corpus
until then, so the n=52 corpus keeps loading.

Run: uv run python -m calibration.build_batch_t2
"""

from __future__ import annotations

import csv

from calibration.build_corpus import (
    CorpusCase,
    _evidence_text,
    _source,
    emit_rows_for_cases,
    write_feature_rows_jsonl,
)

_BATCH_DIR = "calibration/batches/t2-discrimination"
_SCAFFOLD_PATH = f"{_BATCH_DIR}/scaffold.csv"
_FEATURES_PATH = f"{_BATCH_DIR}/feature_rows.jsonl"

# (source_text, A = verb-synonym claim (TRUE), B = argument-swap claim (FALSE))
_PAIRS: tuple[tuple[str, str, str], ...] = (
    (
        "The Halden reactor sustained a stable output level throughout the winter trial.",
        "The Halden reactor maintained a stable output level throughout the winter trial [S1].",
        "The Halden reactor sustained a stable output level throughout the summer trial [S1].",
    ),
    (
        "Orbital Freight reduced its average delivery time across the eastern corridor.",
        "Orbital Freight lowered its average delivery time across the eastern corridor [S1].",
        "Orbital Freight reduced its average delivery time across the western corridor [S1].",
    ),
    (
        "The Kestrel sensor detects surface cracks during routine hull inspection.",
        "The Kestrel sensor identifies surface cracks during routine hull inspection [S1].",
        "The Kestrel sensor detects surface cracks during routine wing inspection [S1].",
    ),
    (
        "Revenue expanded eleven percent year over year in the logistics division.",
        "Revenue grew eleven percent year over year in the logistics division [S1].",
        "Revenue expanded eleven percent year over year in the mapping division [S1].",
    ),
    (
        "The Vantis compiler improves build throughput on large monorepo projects.",
        "The Vantis compiler increases build throughput on large monorepo projects [S1].",
        "The Vantis compiler improves build throughput on large monolith projects [S1].",
    ),
)

_SCAFFOLD_FIELDS = [
    "claim_id", "query_id", "pair_id", "arm", "claim_text", "evidence",
    "source_type", "t2_f1", "novel_token", "note",
]


def build_cases() -> list[tuple[str, str, CorpusCase]]:
    """Return (pair_id, arm, case) triples — one case per claim, A then B.

    Pure function. `arm` is "A" (verb synonym, expected TRUE) or "B" (argument
    substitution, expected FALSE). It is recorded for ANALYSIS only and is
    deliberately absent from the scaffold a labeler reads, so the arm cannot
    anchor their judgment.
    """
    out: list[tuple[str, str, CorpusCase]] = []
    for i, (source_text, claim_a, claim_b) in enumerate(_PAIRS, start=1):
        pair_id = f"p{i:02d}"
        for arm, claim in (("A", claim_a), ("B", claim_b)):
            qid = f"t2d-{pair_id}{arm.lower()}"
            store = {"S1": _source("S1", source_text, f"{pair_id} source")}
            out.append((pair_id, arm, CorpusCase(
                query_id=qid,
                draft_text=claim,
                store=store,
                intent=(
                    "T2-only, single novel token. Arm A substitutes a verb "
                    "synonym (claim remains true); arm B substitutes a noun "
                    "argument (claim becomes false). Both score the same t2_f1."
                ),
            )))
    return out


def _novel_token(claim_text: str, source_text: str) -> str:
    """Return the claim's content token(s) absent from the source, joined.

    Recomputed here rather than trusted, so the scaffold reports what the
    tokenizer actually sees.
    """
    from scripts.ground_check import _content_words, _tokenize

    vocab = set(_tokenize(source_text))
    cited = {"s1"}
    novel = [
        t for t in _content_words(_tokenize(claim_text))
        if t not in vocab and t not in cited
    ]
    return " ".join(novel)


def main() -> None:
    triples = build_cases()
    cases = [c for _, _, c in triples]
    rows = emit_rows_for_cases(cases)

    by_qid = {}
    for row in rows:
        by_qid.setdefault(row.query_id, []).append(row)
    for case in cases:
        n = len(by_qid.get(case.query_id, []))
        if n != 1:
            raise ValueError(
                f"build_batch_t2: query {case.query_id!r} decomposed to {n} "
                "claims, expected exactly 1 — one label must map to one claim."
            )

    write_feature_rows_jsonl(rows, _FEATURES_PATH)

    stores = {c.query_id: c.store for c in cases}
    arms = {c.query_id: (pid, arm) for pid, arm, c in triples}
    with open(_SCAFFOLD_PATH, "w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=_SCAFFOLD_FIELDS)
        writer.writeheader()
        for row in rows:
            store = stores[row.query_id]
            pair_id, arm = arms[row.query_id]
            source_text = store["S1"].text
            writer.writerow({
                "claim_id": row.claim_id,
                "query_id": row.query_id,
                "pair_id": pair_id,
                "arm": arm,
                "claim_text": row.claim_text,
                "evidence": _evidence_text(row, store),
                "source_type": "verbatim",
                "t2_f1": f"{row.t2_f1:.4f}",
                "novel_token": _novel_token(row.claim_text, source_text),
                "note": "T2-only (T1 misses); one novel content token.",
            })

    pairs = {}
    for row in rows:
        pid, arm = arms[row.query_id]
        pairs.setdefault(pid, {})[arm] = row
    print(f"wrote {len(rows)} rows -> {_SCAFFOLD_PATH}, {_FEATURES_PATH}")
    print("\npair  t2_f1(A)  t2_f1(B)  identical?  verdict(A)   verdict(B)")
    for pid in sorted(pairs):
        a, b = pairs[pid]["A"], pairs[pid]["B"]
        same = "YES" if abs(a.t2_f1 - b.t2_f1) < 1e-9 else "no"
        print(f"{pid}   {a.t2_f1:.4f}    {b.t2_f1:.4f}    {same:10s}  "
              f"{a.predicted_verdict:12s} {b.predicted_verdict}")
    print("\nNO labels written — labels.csv and manifest.json are AUTHORED "
          "and appear only after a human ratifies (PIR-002 / OI-CAL-03).")


if __name__ == "__main__":
    main()
