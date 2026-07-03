"""Agent-Assure: calibration harness — per-claim raw feature emission.

Phase 2a, Task 2. Runs decompose -> classify -> ground per claim over a
(query_id, draft_text, store) triple and records the RAW tier features
(t1_verbatim, t2_f1, numeric_ok) alongside the CURRENT predicted verdict —
so a later calibration sweep (Tasks 3+) can re-threshold lex_tau /
min_quote_len post-hoc over stored scores, without re-running decompose,
classify, or ground.

Phase 2a, Task 3 adds the human-labeling round trip: export_labeling_csv
turns ClaimFeatureRow rows into a CSV a human fills in with a
"grounded"/"violation" verdict per claim; load_labels reads that filled CSV
back, failing loud on any unlabeled or mislabeled row; join_labels
inner-joins emitted rows against those labels by claim_id, failing loud if
any emitted claim has no label.

Pure functions only, except export_labeling_csv and load_labels, which are
the explicit file I/O boundary — neither mutates its inputs.
"""

from __future__ import annotations

import csv
import unicodedata
from dataclasses import dataclass

from scripts.ground_check import (
    Claim,
    RetrievedSource,
    classify,
    decompose,
    ground,
    numeric_ok,
    resolve,
    t1_verbatim,
    t2_lexical_score,
)


@dataclass(frozen=True)
class ClaimFeatureRow:
    """One row of raw per-claim grounding features for calibration.

    Captures the tier features BEFORE the ground() dispatcher collapses them
    into a single verdict, so a calibration sweep can re-threshold lex_tau /
    min_quote_len post-hoc over the stored t1_verbatim/t2_f1 values.
    """

    claim_id: str
    query_id: str
    claim_text: str
    kind: str
    cited_source_ids: tuple[str, ...]
    citations_resolved: bool
    t1_verbatim: bool
    t2_f1: float
    numeric_ok: bool
    predicted_verdict: str
    # True iff predicted_verdict can change under a different lex_tau, i.e.
    # (predicted_verdict == "UNGROUNDED") or (predicted_verdict == "GROUNDED"
    # and not t1_verbatim). Only these two states are lex_tau-sensitive:
    # GROUNDED-via-T2 (t1_verbatim False) can become UNGROUNDED at a higher
    # lex_tau, and UNGROUNDED can become GROUNDED at a lower one. Every other
    # verdict is FIXED regardless of lex_tau — including GROUNDED-via-T1
    # (t1_verbatim never consults lex_tau) and UNGROUNDABLE (ground() never
    # reaches the tier check at all for that claim; see _resolve_verbatim_
    # sources docstring). A calibration sweep re-thresholding lex_tau over
    # t2_f1 MUST skip rows where tier_sensitive is False, or it will miscount
    # verdicts that cannot possibly flip.
    tier_sensitive: bool


def _bare_source_id(citation: str) -> str:
    """Strip the surrounding brackets from a citation marker.

    '[S1]' -> 'S1'; a bare id with no brackets is returned unchanged. Mirrors
    the bracket-stripping in ground_check.resolve(), but skips re-running
    NFKC normalization: classify() already NFKC-normalizes claim.text (and
    therefore the citations extracted from it) before this function ever
    sees them.
    """
    if citation.startswith("[") and citation.endswith("]"):
        return citation[1:-1]
    return citation


def _resolve_verbatim_sources(
    claim: Claim, store: dict[str, RetrievedSource]
) -> tuple[list[RetrievedSource | None], list[RetrievedSource]]:
    """Return (resolved_sources, verbatim_sources) for claim.citations.

    resolved_sources parallels claim.citations positionally (None where a
    citation does not resolve against *store*). verbatim_sources is the
    subset that resolved AND carries full_text_source == "verbatim" with
    non-empty text.

    NOT parity with ground()'s internal filtering: ground() (spec §4.4) runs
    its "any resolved source has falsy text" and "no verbatim source among
    cited" checks over ALL resolved citations (verbatim + non-verbatim)
    BEFORE narrowing to verbatim, and short-circuits to UNVERIFIED_CITATION /
    UNGROUNDABLE / UNVERIFIED_NUMBER without ever reaching the T1/T2 tier
    check for many claims. This helper narrows to verbatim FIRST, so it can
    report t1_verbatim/t2_f1 even for claims where ground() never computed
    them. A claim can score t1_verbatim=True, t2_f1=1.0 here while
    ground()'s predicted_verdict is UNGROUNDABLE (e.g. a co-cited
    non-verbatim source with empty text trips ground()'s earlier check).
    predicted_verdict is always authoritative; raw t1_verbatim/t2_f1 are only
    meaningfully re-thresholdable for rows where ClaimFeatureRow.tier_sensitive
    is True.
    """
    resolved_sources = [resolve(c, store) for c in claim.citations]
    verbatim_sources = [
        s for s in resolved_sources
        if s is not None and s.full_text_source == "verbatim" and s.text
    ]
    return resolved_sources, verbatim_sources


def emit_claim_features(
    query_id: str,
    draft_text: str,
    store: dict[str, RetrievedSource],
) -> list[ClaimFeatureRow]:
    """Run decompose -> classify -> ground over *draft_text* against *store*
    and return one ClaimFeatureRow per decomposed claim, in claim order.

    For each claim, t1_verbatim/t2_f1/numeric_ok are computed over the
    verbatim-filtered cited sources (t2_f1 is the MAX t2_lexical_score across
    them, 0.0 when none exist), independent of the predicted_verdict — so the
    raw features survive even when the verdict short-circuits before running
    the tiers (e.g. UNVERIFIED_CITATION, UNGROUNDABLE).

    These raw t1_verbatim/t2_f1 values are NOT guaranteed to be the features
    ground() actually consulted to reach predicted_verdict — ground() may
    short-circuit (on an unresolved citation, a falsy-text source anywhere in
    the citation list, no verbatim source, or a NUMERIC/numeric_ok failure)
    before ever reaching the T1/T2 tier check. predicted_verdict is always
    authoritative. tier_sensitive marks the rows where a re-thresholded
    lex_tau could plausibly change predicted_verdict; a calibration sweep
    over t2_f1 must restrict itself to tier_sensitive rows, or it will
    miscount claims whose verdict cannot flip.

    Pure function — no I/O, no mutation of *store* or *draft_text*.
    """
    rows: list[ClaimFeatureRow] = []
    for raw_claim in decompose(draft_text):
        claim = classify(raw_claim)
        cited_source_ids = tuple(_bare_source_id(c) for c in claim.citations)

        _resolved, verbatim_sources = _resolve_verbatim_sources(claim, store)
        citations_resolved = all(s is not None for s in _resolved)

        t1 = t1_verbatim(claim, verbatim_sources)
        t2 = max(
            (t2_lexical_score(claim.text, s.text) for s in verbatim_sources),
            default=0.0,
        )
        num_ok = numeric_ok(claim, verbatim_sources)

        verdict = ground(claim, store)

        # Only these two verdict states flip under a different lex_tau:
        # GROUNDED-via-T2 (t1 False; a higher lex_tau can drop it to
        # UNGROUNDED) and UNGROUNDED (a lower lex_tau can raise it to
        # GROUNDED). Every other verdict — including GROUNDED-via-T1
        # (lex_tau-invariant) and UNGROUNDABLE (ground() never reached the
        # tier check) — is fixed regardless of lex_tau.
        tier_sensitive = (verdict.value == "UNGROUNDED") or (
            verdict.value == "GROUNDED" and not t1
        )

        rows.append(ClaimFeatureRow(
            claim_id=f"{query_id}#{claim.index}",
            query_id=query_id,
            claim_text=claim.text,
            kind=claim.kind.value,
            cited_source_ids=cited_source_ids,
            citations_resolved=citations_resolved,
            t1_verbatim=t1,
            t2_f1=t2,
            numeric_ok=num_ok,
            predicted_verdict=verdict.value,
            tier_sensitive=tier_sensitive,
        ))
    return rows


# ---------------------------------------------------------------------------
# Task 3: labeling-CSV export + fail-loud label ingestion.
# ---------------------------------------------------------------------------

_ALLOWED_HUMAN_LABELS = frozenset({"grounded", "violation"})

_EXPORT_FIELDNAMES = [
    "claim_id",
    "query_id",
    "claim_text",
    "cited_source_ids",
    "predicted_verdict",
    "t2_f1",
    "human_label",
]


@dataclass(frozen=True)
class HumanLabel:
    """One human-provided ground-truth label for a claim, read back from a
    hand-filled labeling CSV.

    label is NFKC-normalized and guaranteed (by load_labels) to be exactly
    "grounded" or "violation" — never blank, never anything else.
    """

    claim_id: str
    label: str
    violation_kind: str | None


@dataclass(frozen=True)
class LabeledClaim:
    """A ClaimFeatureRow joined with its human label.

    Carries every ClaimFeatureRow field plus the human-assigned label, so a
    calibration sweep can compare predicted_verdict against ground truth at
    every candidate threshold without re-joining on claim_id each time.
    """

    claim_id: str
    query_id: str
    claim_text: str
    kind: str
    cited_source_ids: tuple[str, ...]
    citations_resolved: bool
    t1_verbatim: bool
    t2_f1: float
    numeric_ok: bool
    predicted_verdict: str
    tier_sensitive: bool
    label: str


def export_labeling_csv(rows: list[ClaimFeatureRow], path: str) -> None:
    """Write *rows* to *path* as a CSV for a human to label.

    Columns, in this exact order: claim_id, query_id, claim_text,
    cited_source_ids, predicted_verdict, t2_f1, human_label. human_label is
    left blank — a human fills it in with "grounded" or "violation" before
    the file is fed to load_labels(). cited_source_ids (a tuple) is
    serialized "|"-joined so multi-citation claims stay in one cell.

    I/O boundary — the file write is the only side effect; *rows* is not
    mutated.
    """
    with open(path, "w", encoding="utf-8", newline="") as fh:
        writer = csv.writer(fh, quoting=csv.QUOTE_MINIMAL)
        writer.writerow(_EXPORT_FIELDNAMES)
        for row in rows:
            writer.writerow([
                row.claim_id,
                row.query_id,
                row.claim_text,
                "|".join(row.cited_source_ids),
                row.predicted_verdict,
                row.t2_f1,
                "",
            ])


def load_labels(path: str) -> dict[str, HumanLabel]:
    """Read a hand-filled labeling CSV at *path* and return
    {claim_id: HumanLabel}.

    Fails loud (ValueError) the moment any row's human_label — after
    unicodedata.normalize("NFKC", ...), per the repo's NFKC-before-
    validation safety-gate convention — is not exactly "grounded" or
    "violation", including a blank cell. An unlabeled or mislabeled row
    must never silently default to a verdict; that would corrupt every
    threshold a calibration sweep later derives from this file.

    violation_kind is read from an optional "violation_kind" column — not
    written by export_labeling_csv, but a human may add it by hand when
    labeling a violation. A missing column or blank cell resolves to None;
    it is not part of the fail-loud gate.
    """
    labels: dict[str, HumanLabel] = {}
    with open(path, encoding="utf-8", newline="") as fh:
        reader = csv.DictReader(fh)
        for line_no, record in enumerate(reader, start=2):
            claim_id = record["claim_id"]
            raw_label = record.get("human_label") or ""
            label = unicodedata.normalize("NFKC", raw_label)
            if label not in _ALLOWED_HUMAN_LABELS:
                raise ValueError(
                    f"load_labels: {path!r} line {line_no} "
                    f"(claim_id={claim_id!r}) has human_label "
                    f"{raw_label!r}, which is not one of "
                    f"{sorted(_ALLOWED_HUMAN_LABELS)}. Every row must be "
                    "labeled by hand before calibration — an unlabeled or "
                    "mislabeled row is never silently defaulted."
                )
            raw_kind = (record.get("violation_kind") or "").strip()
            violation_kind = raw_kind or None
            labels[claim_id] = HumanLabel(
                claim_id=claim_id, label=label, violation_kind=violation_kind
            )
    return labels


def join_labels(
    rows: list[ClaimFeatureRow], labels: dict[str, HumanLabel]
) -> list[LabeledClaim]:
    """Inner-join *rows* against *labels* by claim_id, preserving row order.

    Fails loud (ValueError) the moment any row's claim_id has no entry in
    *labels* — a claim silently dropped from the labeled set would bias
    every threshold the calibration sweep derives from it, with no signal
    that data went missing.
    """
    joined: list[LabeledClaim] = []
    for row in rows:
        human_label = labels.get(row.claim_id)
        if human_label is None:
            raise ValueError(
                f"join_labels: claim_id {row.claim_id!r} has no human "
                "label in labels. Every emitted claim must be labeled "
                "before calibration — no claim is silently dropped."
            )
        joined.append(LabeledClaim(
            claim_id=row.claim_id,
            query_id=row.query_id,
            claim_text=row.claim_text,
            kind=row.kind,
            cited_source_ids=row.cited_source_ids,
            citations_resolved=row.citations_resolved,
            t1_verbatim=row.t1_verbatim,
            t2_f1=row.t2_f1,
            numeric_ok=row.numeric_ok,
            predicted_verdict=row.predicted_verdict,
            tier_sensitive=row.tier_sensitive,
            label=human_label.label,
        ))
    return joined
