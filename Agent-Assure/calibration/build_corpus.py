"""Agent-Assure calibration: bootstrap corpus builder.

Phase 2a calibration run. Builds a small synthetic corpus (~12 query/draft
pairs) spanning the grounding-gate's violation classes — numeric match and
mismatch, absence supported and unsupported, relational grounded and
ungrounded, a fabricated citation, T1-verbatim and T2-lexical grounded
claims, a borderline-T2 claim near the current lex_tau, an attribution
claim, and an uncited claim — then runs each through
scripts.calibrate.emit_claim_features and writes two artifacts:

  calibration/feature_rows.jsonl   one ClaimFeatureRow per line (internal;
                                   carries predicted_verdict for our own
                                   sanity-checking and for join_labels()
                                   downstream).
  calibration/labeling.csv         the file a human actually labels. Columns
                                   are claim_id, query_id, claim_text,
                                   evidence, human_label (blank).
                                   predicted_verdict is deliberately OMITTED
                                   from this file — showing a labeler the
                                   gate's own verdict while asking them to
                                   judge grounding independently invites
                                   anchoring bias, which would understate
                                   Error B (the one error this tool exists to
                                   catch). evidence is cited-source text for
                                   every kind except ABSENCE, which shows the
                                   session's distinct search queries instead
                                   (see _evidence_text) — ABSENCE claims are
                                   never grounded by a citation, so showing
                                   nothing for them asks a labeler to judge
                                   with zero information.

Each case pairs a query_id with its own draft_text and its own store dict
(not a corpus-wide shared store) — this mirrors how a real session has one
EvidenceStore, and keeps ABSENCE claims' query_provenance counting scoped to
the query it belongs to.

Pure functions except main(), which is the file-I/O boundary.
"""

from __future__ import annotations

import hashlib
import json
import unicodedata
from dataclasses import asdict, dataclass

from scripts.calibrate import ClaimFeatureRow, emit_claim_features
from scripts.ground_check import RetrievedSource

_FEATURE_ROWS_PATH = "calibration/feature_rows.jsonl"
_LABELING_CSV_PATH = "calibration/labeling.csv"


def _content_sha256(text: str) -> str:
    """Return the sha256 hex digest of the NFKC-normalized *text*.

    Mirrors capture_core.make_record's convention (NFKC before hashing, per
    the repo's homoglyph-safety gate) even though ground() never consults
    this field — kept correct for consistency with real EvidenceStore rows.
    """
    normalized = unicodedata.normalize("NFKC", text)
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()


def _source(source_id: str, text: str, query_provenance: str) -> RetrievedSource:
    """Build a synthetic verbatim RetrievedSource for the bootstrap corpus.

    Fixed fetched_at/tool/captured_via — these are test fixtures, not live
    captures, so a literal timestamp is correct (no wall-clock reads).
    """
    return RetrievedSource(
        source_id=source_id,
        url=None,
        file_path=None,
        fetched_at="2026-07-03T00:00:00Z",
        tool="calibration_fixture",
        content_sha256=_content_sha256(text),
        text=text,
        full_text_source="verbatim",
        captured_via="inline",
        query_provenance=query_provenance,
    )


@dataclass(frozen=True)
class CorpusCase:
    """One bootstrap-corpus draft: a query_id, its draft_text, and the
    RetrievedSource store scoped to that query alone.

    intent is a maintainer-facing note on which violation class / verdict
    this case targets — for our own review only. It is NEVER written to
    labeling.csv; the human labeler sees claim_text and source text only.
    """

    query_id: str
    draft_text: str
    store: dict[str, RetrievedSource]
    intent: str


def build_cases() -> list[CorpusCase]:
    """Return the ~12 bootstrap-corpus cases spanning the violation classes.

    Pure function — constructs and returns new objects; no I/O.
    """
    cases: list[CorpusCase] = []

    # q01 — NUMERIC, matching value -> GROUNDED.
    cases.append(CorpusCase(
        query_id="q01",
        draft_text=(
            "Meridian Robotics shipped 4,200 units in the third quarter [S1]."
        ),
        store={"S1": _source(
            "S1",
            "In the third quarter, Meridian Robotics shipped 4,200 units to "
            "distributors across North America and Europe.",
            "Meridian Robotics Q3 shipment report",
        )},
        intent="NUMERIC match -> GROUNDED",
    ))

    # q02 — NUMERIC, mismatched value -> UNVERIFIED_NUMBER (violation).
    cases.append(CorpusCase(
        query_id="q02",
        draft_text=(
            "Meridian Robotics shipped 9,800 units in the third quarter [S1]."
        ),
        store={"S1": _source(
            "S1",
            "In the third quarter, Meridian Robotics shipped 4,200 units to "
            "distributors across North America and Europe.",
            "Meridian Robotics Q3 shipment report",
        )},
        intent="NUMERIC mismatch -> UNVERIFIED_NUMBER (violation)",
    ))

    # q03 — ABSENCE, >=2 distinct queries mention the extracted head noun
    # ("evidence") -> ABSENCE_SUPPORTED.
    cases.append(CorpusCase(
        query_id="q03",
        draft_text=(
            "We found no evidence of a safety recall affecting the X200 drone."
        ),
        store={
            "SA1": _source(
                "SA1",
                "No recall evidence was found in the manufacturer's safety "
                "bulletin archive for the X200 drone line.",
                "recall evidence search X200 drone",
            ),
            "SA2": _source(
                "SA2",
                "The public recall database returned zero results for X200 "
                "drone safety evidence.",
                "regulatory database evidence query X200",
            ),
        },
        intent="ABSENCE, 2 distinct matching queries -> ABSENCE_SUPPORTED",
    ))

    # q04 — ABSENCE, no query mentions the extracted head noun ("mention")
    # -> UNVERIFIED_ABSENCE (violation).
    cases.append(CorpusCase(
        query_id="q04",
        draft_text=(
            "There is no mention of battery defects in the X200 drone manual."
        ),
        store={
            "SB1": _source(
                "SB1",
                "The X200 drone specification sheet lists battery capacity "
                "and flight time.",
                "X200 drone product specifications",
            ),
            "SB2": _source(
                "SB2",
                "Retail pricing for the X200 drone starts at a fixed list price.",
                "X200 drone pricing information",
            ),
        },
        intent="ABSENCE, 0 matching queries -> UNVERIFIED_ABSENCE (violation)",
    ))

    # q05 — RELATIONAL, side_A ("spend") and side_B ("signups") each
    # supported in a DIFFERENT verbatim source -> ground_relational returns
    # GROUNDED. CORRECTED FINDING (label-validation pass, 2026-07-04): three
    # independent human labels (one direct, three blind-judge verifications)
    # unanimously called this a VIOLATION on genuine reading — S3 confirms
    # spend rose, S4 confirms signups rose, but NEITHER source ever asserts
    # the claim's causal link ("drives"); the two-distinct-source rule is
    # satisfied by mere co-occurrence of two independent facts. This is a
    # real over-association finding, not a mislabel: ground_relational's
    # rule is a weak proxy for "the sources establish the relationship," and
    # this row is now Error-B ground truth (predicted GROUNDED, true label
    # violation) for the calibration sweep, not a clean "GROUNDED" example.
    cases.append(CorpusCase(
        query_id="q05",
        draft_text=(
            "Increased marketing spend drives higher customer signups [S3][S4]."
        ),
        store={
            "S3": _source(
                "S3",
                "Marketing spend increased twenty percent quarter over "
                "quarter according to the finance team.",
                "marketing spend analysis",
            ),
            "S4": _source(
                "S4",
                "Customer signups rose sharply in the weeks following the "
                "campaign launch.",
                "signup funnel analysis",
            ),
        },
        intent=(
            "RELATIONAL, two-source support -> gate predicts GROUNDED, but "
            "human ground truth is violation (over-association: neither "
            "source asserts the causal link) -> Error-B ground truth"
        ),
    ))

    # q06 — RELATIONAL, only one citation -> fewer than 2 distinct verbatim
    # sources -> UNVERIFIED_RELATION (violation), regardless of wording.
    cases.append(CorpusCase(
        query_id="q06",
        draft_text="Faster onboarding leads to higher retention [S5].",
        store={"S5": _source(
            "S5",
            "The new onboarding flow reduced time-to-first-value for new "
            "accounts.",
            "onboarding flow analysis",
        )},
        intent="RELATIONAL, single-source citation -> UNVERIFIED_RELATION (violation)",
    ))

    # q07 — citation to a source_id absent from the store -> UNVERIFIED_CITATION
    # (violation). Store deliberately does not contain S6.
    cases.append(CorpusCase(
        query_id="q07",
        draft_text=(
            "Meridian Robotics achieved carbon-neutral manufacturing across "
            "all its facilities [S6]."
        ),
        store={},
        intent="Fabricated citation -> UNVERIFIED_CITATION (violation)",
    ))

    # q08 — an >=8-token contiguous verbatim span appears in the source
    # -> GROUNDED via T1.
    cases.append(CorpusCase(
        query_id="q08",
        draft_text=(
            "The aluminum chassis reduces overall unit weight by twelve "
            "percent compared to steel [S7]."
        ),
        store={"S7": _source(
            "S7",
            "The aluminum chassis reduces overall unit weight by twelve "
            "percent compared to steel used in the legacy design.",
            "chassis materials comparison",
        )},
        intent="Verbatim >=8-token span -> GROUNDED via T1",
    ))

    # q09 — a paraphrase with high shared-content-word overlap (T2 F1 ~0.79,
    # tuned empirically against t2_lexical_score), no verbatim span
    # -> GROUNDED via T2.
    cases.append(CorpusCase(
        query_id="q09",
        draft_text=(
            "The upgraded rotor motor gives the drone much longer flight "
            "time than last year's model [S8]."
        ),
        store={"S8": _source(
            "S8",
            "Bench testing showed the upgraded rotor motor giving this "
            "drone a much longer flight time than the prior year's motor "
            "model.",
            "rotor motor bench testing",
        )},
        intent="Paraphrase, T2 F1 ~0.71 (above lex_tau=0.65), no verbatim span -> GROUNDED via T2",
    ))

    # q10 — the calibration-interesting row: a paraphrase tuned to land at
    # T2 F1 ~0.57 (below the current lex_tau=0.65, so predicted UNGROUNDED)
    # but sharing enough content words that a human may reasonably call it
    # supported. This is exactly the boundary lex_tau sweeps need to see.
    cases.append(CorpusCase(
        query_id="q10",
        draft_text=(
            "The rotor motor upgrade gives the drone longer flight time "
            "than last year [S10]."
        ),
        store={"S10": _source(
            "S10",
            "Engineers found the motor gives noticeably longer flight time "
            "on this drone platform overall.",
            "rotor motor field report",
        )},
        intent=(
            "Borderline paraphrase, T2 F1 ~0.57 (below current lex_tau) "
            "-> predicted UNGROUNDED; calibration-interesting boundary row"
        ),
    ))

    # q11 — ATTRIBUTION claim ("according to ..."), verbatim-supported
    # -> GROUNDED via T1.
    cases.append(CorpusCase(
        query_id="q11",
        draft_text=(
            "According to the engineering team, the new battery pack lasts "
            "through extended field tests without failure [S9]."
        ),
        store={"S9": _source(
            "S9",
            "According to the engineering team, the new battery pack lasts "
            "through extended field tests without failure under a range of "
            "temperature conditions.",
            "battery pack field test report",
        )},
        intent="ATTRIBUTION, verbatim-supported -> GROUNDED",
    ))

    # q12 — no citation at all -> UNCITED (violation).
    cases.append(CorpusCase(
        query_id="q12",
        draft_text=(
            "The drone's carbon-fiber frame is lighter than earlier "
            "aluminum designs."
        ),
        store={},
        intent="No citation -> UNCITED (violation)",
    ))

    return cases


def emit_rows_for_cases(cases: list[CorpusCase]) -> list[ClaimFeatureRow]:
    """Run emit_claim_features over every case and return the combined rows,
    in case order.

    Pure function — no I/O.
    """
    rows: list[ClaimFeatureRow] = []
    for case in cases:
        rows.extend(emit_claim_features(case.query_id, case.draft_text, case.store))
    return rows


def _distinct_query_provenance(store: dict[str, RetrievedSource]) -> list[str]:
    """Return the distinct query_provenance values across *store*, in first-
    seen order. Local, order-preserving dedup — mirrors
    ground_check._session_queries's dedup behavior without importing that
    module's private (underscore-prefixed) helper.

    Pure function — no I/O, no mutation of *store*.
    """
    seen: set[str] = set()
    out: list[str] = []
    for source in store.values():
        q = source.query_provenance
        if q not in seen:
            seen.add(q)
            out.append(q)
    return out


def _evidence_text(row: ClaimFeatureRow, store: dict[str, RetrievedSource]) -> str:
    """Return the evidence a human labeler needs to independently judge
    *row*, against *store* (the case's own store).

    For every kind EXCEPT ABSENCE: the joined text of every source
    row.cited_source_ids cites. A citation absent from store (e.g. the
    fabricated-citation case) renders as "[NOT IN STORE]" for that id so the
    labeler can see the gate would find nothing to check against. Multiple
    citations are joined with " ||| " so a relational claim's two sources
    are both visible without ambiguity about where one ends.

    For ABSENCE claims: check_absence's actual evidence is NOT the claim's
    citations (which check_absence never consults — see ground_check.ground's
    ABSENCE branch) but the distinct session search queries. Showing "" for
    these rows (the original bug this function replaces) asks a labeler to
    judge an absence claim with zero evidence, which unanimously reads as
    "violation" regardless of whether the underlying absence is genuinely
    well-searched — see docs/research findings from the calibration-run
    label-validation pass. Surfacing the actual distinct queries lets the
    labeler judge the real mechanism instead.

    Pure function — no I/O, no mutation of *row* or *store*.
    """
    if row.kind == "ABSENCE":
        queries = _distinct_query_provenance(store)
        if not queries:
            return "[no session search queries recorded]"
        return "Session search queries: " + " ||| ".join(
            f'"{q}"' for q in queries
        )
    if not row.cited_source_ids:
        return ""
    parts: list[str] = []
    for source_id in row.cited_source_ids:
        source = store.get(source_id)
        if source is None:
            parts.append(f"{source_id}: [NOT IN STORE]")
        else:
            parts.append(f"{source_id}: {source.text}")
    return " ||| ".join(parts)


def write_feature_rows_jsonl(rows: list[ClaimFeatureRow], path: str) -> None:
    """Write *rows* to *path*, one JSON object per line.

    I/O boundary — the file write is the only side effect; *rows* is not
    mutated. cited_source_ids (a tuple) serializes as a JSON array via
    dataclasses.asdict + json.dumps, which encodes tuples as arrays natively.
    """
    with open(path, "w", encoding="utf-8") as fh:
        for row in rows:
            fh.write(json.dumps(asdict(row), sort_keys=True))
            fh.write("\n")


def write_enriched_labeling_csv(
    rows: list[ClaimFeatureRow],
    cases_by_query_id: dict[str, CorpusCase],
    path: str,
) -> None:
    """Write the human-labeling CSV: claim_id, query_id, claim_text,
    evidence, human_label (blank).

    evidence is cited-source text for every kind except ABSENCE, where it is
    the session's distinct search queries instead (see _evidence_text —
    ABSENCE claims are grounded by query coverage, not by citation, and
    showing "" for them asks a labeler to judge with no evidence at all).

    predicted_verdict is deliberately NOT a column here — see module
    docstring. load_labels() only reads the claim_id and human_label
    columns (csv.DictReader keyed by header name), so this file's extra/
    different shape versus scripts.calibrate.export_labeling_csv is fully
    compatible with the existing load_labels/join_labels pipeline.

    I/O boundary — the file write is the only side effect.
    """
    import csv

    with open(path, "w", encoding="utf-8", newline="") as fh:
        writer = csv.writer(fh, quoting=csv.QUOTE_MINIMAL)
        writer.writerow([
            "claim_id", "query_id", "claim_text", "evidence", "human_label",
        ])
        for row in rows:
            case = cases_by_query_id[row.query_id]
            writer.writerow([
                row.claim_id,
                row.query_id,
                row.claim_text,
                _evidence_text(row, case.store),
                "",
            ])


def _print_sanity_summary(cases: list[CorpusCase], rows: list[ClaimFeatureRow]) -> None:
    """Print a maintainer-facing table of kind/verdict/t2_f1 per row, next to
    its intended violation class, so a mismatch is visible before the CSV
    goes to a human labeler. Terminal output only — never written to a file
    the labeler sees.
    """
    rows_by_query_id = {row.query_id: row for row in rows}
    print(f"{'query_id':<6} {'kind':<11} {'verdict':<20} {'t2_f1':<7} {'tier_sens':<9} intent")
    for case in cases:
        row = rows_by_query_id[case.query_id]
        print(
            f"{row.query_id:<6} {row.kind:<11} {row.predicted_verdict:<20} "
            f"{row.t2_f1:<7.3f} {str(row.tier_sensitive):<9} {case.intent}"
        )


def main() -> None:
    """Build the bootstrap corpus, emit features, and write both artifacts."""
    cases = build_cases()
    rows = emit_rows_for_cases(cases)
    cases_by_query_id = {case.query_id: case for case in cases}

    write_feature_rows_jsonl(rows, _FEATURE_ROWS_PATH)
    write_enriched_labeling_csv(rows, cases_by_query_id, _LABELING_CSV_PATH)

    _print_sanity_summary(cases, rows)
    print(f"\n{len(rows)} claims written to {_FEATURE_ROWS_PATH} and {_LABELING_CSV_PATH}")


if __name__ == "__main__":
    main()
