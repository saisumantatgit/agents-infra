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
