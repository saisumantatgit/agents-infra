"""Tests for check_absence — absence verdict against query log.

TDD sequence:
  Step 1: Write tests (this file).
  Step 2: Run → FAIL (check_absence not yet defined).
  Step 3: Implement in scripts/ground_check.py.
  Step 4: Run → PASS.

Required cases per brief:
  - ABSENCE_SUPPORTED when ≥2 distinct queries mention the subject.
  - UNVERIFIED_ABSENCE when only 1 query mentions the subject.
  - UNVERIFIED_ABSENCE when 0 queries mention the subject.
"""

import pytest

from scripts.ground_check import (
    Claim,
    ClaimKind,
    Verdict,
    check_absence,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def absence_claim(text: str) -> Claim:
    """Build a minimal ABSENCE-kind Claim with the given text."""
    return Claim(
        index=0,
        text=text,
        kind=ClaimKind.ABSENCE,
        citations=(),
        numeric_tokens=(),
    )


# ---------------------------------------------------------------------------
# Core required tests (from brief)
# ---------------------------------------------------------------------------

def test_absence_supported_with_two_matching_queries():
    """ABSENCE_SUPPORTED when ≥2 distinct queries mention the subject.

    Claim asserts no Redis documentation exists.
    Two distinct queries both mention 'redis'.
    Neither query is a duplicate.
    Expected: ABSENCE_SUPPORTED.
    """
    claim = absence_claim("There is no Redis documentation available.")
    queries = [
        "Redis documentation site",
        "Redis official docs tutorial",
    ]
    assert check_absence(claim, queries) == Verdict.ABSENCE_SUPPORTED


def test_unverified_absence_with_one_matching_query():
    """UNVERIFIED_ABSENCE when only 1 distinct query mentions the subject.

    Claim asserts no Redis documentation exists.
    Only one query mentions 'redis' — below min_absence_searches=2.
    Expected: UNVERIFIED_ABSENCE.
    """
    claim = absence_claim("There is no Redis documentation available.")
    queries = [
        "Redis documentation site",
        "Python tutorial introduction",
    ]
    assert check_absence(claim, queries) == Verdict.UNVERIFIED_ABSENCE


def test_unverified_absence_with_zero_matching_queries():
    """UNVERIFIED_ABSENCE when 0 queries mention the subject.

    Claim asserts no Redis documentation exists.
    No query mentions 'redis'.
    Expected: UNVERIFIED_ABSENCE.
    """
    claim = absence_claim("There is no Redis documentation available.")
    queries = [
        "Python tutorial introduction",
        "JavaScript frameworks comparison",
    ]
    assert check_absence(claim, queries) == Verdict.UNVERIFIED_ABSENCE


# ---------------------------------------------------------------------------
# Distinctness enforcement
# ---------------------------------------------------------------------------

def test_duplicate_queries_count_as_one():
    """Duplicate queries must not inflate the count past 1 distinct query.

    Even with 3 entries, if they are all the same string they are 1 distinct
    query. min_absence_searches=2, so this should return UNVERIFIED_ABSENCE.
    """
    claim = absence_claim("There is no Redis cache support.")
    queries = [
        "Redis cache support documentation",
        "Redis cache support documentation",
        "Redis cache support documentation",
    ]
    assert check_absence(claim, queries) == Verdict.UNVERIFIED_ABSENCE


def test_two_distinct_queries_required_not_two_entries():
    """Exactly 2 distinct queries → ABSENCE_SUPPORTED; 1 distinct → UNVERIFIED.

    This confirms the distinctness semantics rather than raw list length.
    """
    claim = absence_claim("There is no Postgres extension available.")
    queries_two_distinct = [
        "Postgres extension list",
        "Postgres plugin ecosystem",
    ]
    queries_one_distinct = [
        "Postgres extension list",
        "Postgres extension list",
    ]
    assert check_absence(claim, queries_two_distinct) == Verdict.ABSENCE_SUPPORTED
    assert check_absence(claim, queries_one_distinct) == Verdict.UNVERIFIED_ABSENCE


# ---------------------------------------------------------------------------
# NFKC normalization
# ---------------------------------------------------------------------------

def test_nfkc_normalization_in_query_matching():
    """Subject matching must be NFKC-normalized before comparison.

    Uses a claim with a subject whose NFKC form differs from its raw form
    (fullwidth latin 'Ｒｅｄｉｓ' → normalized to 'Redis').
    The queries use normal ASCII. NFKC normalization must bridge the gap.
    """
    # Fullwidth Unicode characters for 'Redis' — NFKC normalizes to ASCII.
    fullwidth_claim = absence_claim("There is no Ｒｅｄｉｓ documentation.")
    queries = [
        "Redis documentation search",
        "Redis official site lookup",
    ]
    assert check_absence(fullwidth_claim, queries) == Verdict.ABSENCE_SUPPORTED


# ---------------------------------------------------------------------------
# min_absence_searches parameter
# ---------------------------------------------------------------------------

def test_custom_min_absence_searches_one():
    """min_absence_searches=1 lowers threshold; 1 matching query suffices."""
    claim = absence_claim("There is no Redis documentation.")
    queries = ["Redis documentation"]
    assert check_absence(claim, queries, min_absence_searches=1) == Verdict.ABSENCE_SUPPORTED


def test_custom_min_absence_searches_three():
    """min_absence_searches=3 raises threshold; 2 matching queries insufficient."""
    claim = absence_claim("There is no Redis documentation.")
    queries = [
        "Redis documentation site",
        "Redis official docs",
    ]
    assert check_absence(claim, queries, min_absence_searches=3) == Verdict.UNVERIFIED_ABSENCE


# ---------------------------------------------------------------------------
# Empty input edge cases
# ---------------------------------------------------------------------------

def test_empty_query_list():
    """Empty query list → UNVERIFIED_ABSENCE (0 matching queries)."""
    claim = absence_claim("There is no Redis documentation.")
    assert check_absence(claim, []) == Verdict.UNVERIFIED_ABSENCE


def test_empty_string_queries_not_matched():
    """Blank/empty queries do not count as matches."""
    claim = absence_claim("There is no Redis documentation.")
    queries = ["", "   ", "Python tutorial"]
    assert check_absence(claim, queries) == Verdict.UNVERIFIED_ABSENCE
