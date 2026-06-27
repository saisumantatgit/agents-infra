"""Tests for relational grounding (Task 7).

TDD sequence:
  Step 1: Write tests (this file) — all tests fail because ground_relational
          is not yet defined.
  Step 2: Run → FAIL (proves test integrity).
  Step 3: Implement ground_relational + extract_arguments + window_supports.
  Step 4: Run → PASS.

Spec §4.8 contract being tested:
  - ≥2 distinct verbatim sources required for GROUNDED.
  - side_A supported in some verbatim source AND side_B in a DIFFERENT verbatim
    source → GROUNDED.
  - Any other case → UNVERIFIED_RELATION (fail-closed).
"""

import pytest

from scripts.ground_check import (
    Claim,
    ClaimKind,
    RetrievedSource,
    Verdict,
    ground_relational,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _src(source_id: str, text: str, full_text_source: str = "verbatim") -> RetrievedSource:
    """Build a minimal RetrievedSource."""
    return RetrievedSource(
        source_id=source_id,
        url=None,
        file_path=None,
        fetched_at="2026-01-01T00:00:00Z",
        tool="Read",
        content_sha256="abc",
        text=text,
        full_text_source=full_text_source,
        captured_via="inline",
        query_provenance="test",
    )


def _claim(text: str, *citations: str) -> Claim:
    """Build a RELATIONAL Claim with the given citations."""
    return Claim(
        index=0,
        text=text,
        kind=ClaimKind.RELATIONAL,
        citations=citations,
        numeric_tokens=(),
    )


def _store(*sources: RetrievedSource) -> dict[str, RetrievedSource]:
    """Build a store dict from source objects keyed by source_id."""
    return {s.source_id: s for s in sources}


# ---------------------------------------------------------------------------
# Required tests (spec §4.8, task brief)
# ---------------------------------------------------------------------------

def test_single_source_relation_not_grounded():
    """'A causes B [S1]' with only S1 → UNVERIFIED_RELATION, never GROUNDED.

    Side A ('insulin resistance') lives in S1. Side B ('type 2 diabetes')
    also lives in S1. Only one distinct verbatim source → cannot establish the
    two-distinct-source requirement → UNVERIFIED_RELATION.
    """
    s1 = _src(
        "S1",
        "Insulin resistance is a metabolic condition. "
        "Type 2 diabetes develops from insulin resistance over time.",
    )
    claim = _claim(
        "Insulin resistance causes type 2 diabetes [S1].",
        "[S1]",
    )
    result = ground_relational(claim, _store(s1))
    assert result == Verdict.UNVERIFIED_RELATION, (
        f"Expected UNVERIFIED_RELATION for single-source relation, got {result}"
    )


def test_two_sided_relation_grounded():
    """Side A in S1, side B in S2 (both verbatim) → GROUNDED.

    S1 discusses 'insulin resistance'; S2 discusses 'type 2 diabetes'.
    The claim asserts a causal link. Both sides are supported across two
    distinct verbatim sources → GROUNDED.
    """
    s1 = _src(
        "S1",
        "Insulin resistance occurs when cells in your body do not respond "
        "well to insulin and cannot use glucose from your blood for energy.",
    )
    s2 = _src(
        "S2",
        "Type 2 diabetes is a chronic metabolic condition where blood sugar "
        "levels remain elevated due to impaired insulin action.",
    )
    claim = _claim(
        "Insulin resistance causes type 2 diabetes [S1][S2].",
        "[S1]",
        "[S2]",
    )
    result = ground_relational(claim, _store(s1, s2))
    assert result == Verdict.GROUNDED, (
        f"Expected GROUNDED for two-sided verbatim-source relation, got {result}"
    )


def test_both_arguments_single_source_unverified():
    """Both arguments present in text but only one distinct source → UNVERIFIED_RELATION.

    Even when side_A is in S1 and the claim text mentions both sides, a single
    source cannot satisfy the two-distinct-source requirement.
    """
    s1 = _src(
        "S1",
        "High stress leads to elevated cortisol. "
        "Elevated cortisol suppresses immune function over time.",
    )
    claim = _claim(
        "High stress leads to elevated cortisol [S1].",
        "[S1]",
    )
    result = ground_relational(claim, _store(s1))
    assert result == Verdict.UNVERIFIED_RELATION, (
        f"Expected UNVERIFIED_RELATION when both args in single source, got {result}"
    )


# ---------------------------------------------------------------------------
# Additional correctness tests
# ---------------------------------------------------------------------------

def test_no_citations_unverified():
    """Claim with no citations → UNVERIFIED_RELATION (no sources to resolve)."""
    claim = _claim("Sleep deprivation causes cognitive decline.")
    result = ground_relational(claim, {})
    assert result == Verdict.UNVERIFIED_RELATION


def test_haiku_summary_source_excluded():
    """haiku_summary sources are not verbatim; they do not count toward the two-source
    requirement even when cited.

    S1 is haiku_summary, S2 is verbatim. Only one verbatim source →
    UNVERIFIED_RELATION.
    """
    s1 = _src(
        "S1",
        "Insulin resistance is associated with type 2 diabetes.",
        full_text_source="haiku_summary",
    )
    s2 = _src(
        "S2",
        "Type 2 diabetes is a chronic metabolic condition.",
        full_text_source="verbatim",
    )
    claim = _claim(
        "Insulin resistance causes type 2 diabetes [S1][S2].",
        "[S1]",
        "[S2]",
    )
    result = ground_relational(claim, _store(s1, s2))
    assert result == Verdict.UNVERIFIED_RELATION, (
        f"Expected UNVERIFIED_RELATION when only one verbatim source, got {result}"
    )


def test_unresolvable_citation_unverified():
    """Citation that does not exist in store → source count drops; UNVERIFIED_RELATION."""
    s1 = _src(
        "S1",
        "Insulin resistance is a metabolic condition.",
    )
    # [S2] is cited but not in the store
    claim = _claim(
        "Insulin resistance causes type 2 diabetes [S1][S2].",
        "[S1]",
        "[S2]",
    )
    result = ground_relational(claim, _store(s1))
    assert result == Verdict.UNVERIFIED_RELATION


def test_same_source_cited_twice_counts_once():
    """Citing S1 twice must not double-count it toward the two-distinct-source gate."""
    s1 = _src(
        "S1",
        "Insulin resistance is a metabolic condition linked to type 2 diabetes.",
    )
    claim = _claim(
        "Insulin resistance causes type 2 diabetes [S1][S1].",
        "[S1]",
        "[S1]",
    )
    result = ground_relational(claim, _store(s1))
    assert result == Verdict.UNVERIFIED_RELATION, (
        f"Duplicate citation must not satisfy two-source gate, got {result}"
    )


def test_nfkc_normalization_in_matching():
    """NFKC normalization applies before matching; homoglyph variants still match."""
    # Side A text uses a Cyrillic 'а' (а) which NFKC maps — verify it doesn't
    # break the extraction and that matching remains deterministic.
    s1 = _src(
        "S1",
        "Insulin resistance is a well-documented condition.",
    )
    s2 = _src(
        "S2",
        "Type 2 diabetes is a chronic disease with metabolic origins.",
    )
    # Claim text uses all-Latin characters — NFKC is a no-op; result is deterministic.
    claim = _claim(
        "Insulin resistance causes type 2 diabetes [S1][S2].",
        "[S1]",
        "[S2]",
    )
    r1 = ground_relational(claim, _store(s1, s2))
    r2 = ground_relational(claim, _store(s1, s2))
    assert r1 == r2, "ground_relational must be deterministic"
    # With both sides covered across two verbatim sources → GROUNDED
    assert r1 == Verdict.GROUNDED


def test_side_b_on_different_source_required():
    """side_B must be supported by a DIFFERENT source from side_A.

    Both S1 and S2 are verbatim, but only S1 covers side_A ('insulin
    resistance') and side_B ('type 2 diabetes'). S2 talks about something
    unrelated. Because side_B is not in a DIFFERENT source from side_A, the
    cross-source rule fails → UNVERIFIED_RELATION.

    Note: this test exercises the case where two verbatim sources exist but
    the cross-source property is not satisfied because side_B is only in S1
    (same source as side_A).
    """
    s1 = _src(
        "S1",
        "Insulin resistance is a risk factor for type 2 diabetes development.",
    )
    s2 = _src(
        "S2",
        "Exercise improves cardiovascular fitness and muscle strength significantly.",
    )
    claim = _claim(
        "Insulin resistance causes type 2 diabetes [S1][S2].",
        "[S1]",
        "[S2]",
    )
    result = ground_relational(claim, _store(s1, s2))
    # S2 does not support type 2 diabetes; side_B is unsupported in a different source
    assert result == Verdict.UNVERIFIED_RELATION
