"""Agent-Assure: calibration harness — per-claim raw feature emission.

Phase 2a, Task 2. Runs decompose -> classify -> ground per claim over a
(query_id, draft_text, store) triple and records the RAW tier features
(t1_verbatim, t2_f1, numeric_ok) alongside the CURRENT predicted verdict —
so a later calibration sweep (Tasks 3+) can re-threshold lex_tau /
min_quote_len post-hoc over stored scores, without re-running decompose,
classify, or ground.

Pure functions only — no I/O, no LLM, no network, no random, no wall-clock.
"""

from __future__ import annotations

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
    non-empty text — the same population ground() restricts its own T1/T2/
    numeric_ok checks to (spec §4.4).
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
    the tiers (e.g. UNVERIFIED_CITATION).

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
        ))
    return rows
