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


# ---------------------------------------------------------------------------
# Discriminating-anchor semantics (AA-MOAT-004 fix, 2026-07-12)
# Proven-red at the bug level via tests/red_team_moat (xfail → XPASS flip);
# these pin the mechanism directly.
# ---------------------------------------------------------------------------

def test_strong_anchors_all_required():
    """Every entity anchor of the negated subject must appear in a supporting
    query: 'no benchmark comparing MongoDB against Redis' is NOT supported by
    generic benchmark queries that never mention MongoDB (AA-MOAT-004)."""
    claim = absence_claim(
        "We found no benchmark comparing MongoDB against either Redis or "
        "PostgreSQL on this hardware."
    )
    queries = [
        "redis benchmark throughput",
        "postgresql write throughput benchmark",
    ]
    assert check_absence(claim, queries) == Verdict.UNVERIFIED_ABSENCE


def test_numeric_anchor_required():
    """A numeric in the negated subject is a discriminating anchor: queries
    that never targeted the 500000 threshold cannot support its absence."""
    claim = absence_claim(
        "There is no benchmark that shows Redis handling more than 500000 "
        "operations per second."
    )
    queries = [
        "redis benchmark throughput",
        "redis performance numbers",
    ]
    assert check_absence(claim, queries) == Verdict.UNVERIFIED_ABSENCE


def test_strong_anchors_supported_when_actually_queried():
    """When the discriminating anchors AND the subject head noun WERE queried
    >=2 times, the absence is supported — the fix must not break genuine
    absence research."""
    claim = absence_claim(
        "We found no benchmark comparing MongoDB against Redis."
    )
    queries = [
        "MongoDB vs Redis benchmark",
        "MongoDB Redis benchmark comparison",
    ]
    assert check_absence(claim, queries) == Verdict.ABSENCE_SUPPORTED


def test_entity_mention_without_subject_not_support():
    """Queries that mention the entity while searching something ELSE cannot
    support an absence about that entity (the q22 generic-entity collision:
    'X200 pricing' does not support 'no mention of battery defects in the
    X200 manual')."""
    claim = absence_claim(
        "There is no mention of battery defects in the X200 manual."
    )
    queries = [
        "X200 drone product specifications",
        "X200 drone pricing information",
    ]
    assert check_absence(claim, queries) == Verdict.UNVERIFIED_ABSENCE


def test_entity_free_head_noun_majority_filtered():
    """Entity-free subject: a head noun present in >50% of a >=3-query session
    is a blanket corpus word — cannot evidence targeted absence research."""
    claim = absence_claim("There is no benchmark data available.")
    queries = [
        "database benchmark methodology",
        "benchmark hardware specification",
        "cloud pricing comparison",  # 2 of 3 contain 'benchmark' → majority
    ]
    assert check_absence(claim, queries) == Verdict.UNVERIFIED_ABSENCE


def test_entity_free_two_query_session_status_quo():
    """Entity-free subject in a 2-query focused session keeps the legacy
    behavior (the majority filter needs >=3 distinct queries)."""
    claim = absence_claim("There is no changelog available.")
    queries = [
        "project changelog location",
        "changelog release notes",
    ]
    assert check_absence(claim, queries) == Verdict.ABSENCE_SUPPORTED


# ---------------------------------------------------------------------------
# Subject-specificity rule (round 2, 2026-07-14): an entity-free subject that
# is SPECIFIC (>=3 content words) needs a corroborating content word in the
# query, not just its head noun.
# ---------------------------------------------------------------------------

def test_specific_entity_free_subject_needs_corroborating_word():
    """'no benchmark for the streaming ingest workload' is NOT evidenced by a
    session that only ever searched the word 'benchmark' (AA-MOAT-R2-003)."""
    claim = absence_claim("There is no benchmark for the streaming ingest workload.")
    queries = ["redis benchmark throughput", "postgresql write throughput benchmark"]
    assert check_absence(claim, queries) == Verdict.UNVERIFIED_ABSENCE


def test_specific_subject_supported_when_corroborated():
    """Error-A guard (corpus q37): a genuinely targeted absence still passes —
    'no antidote approved for the toxin' backed by two antidote+toxin searches.
    Also proves plural stemming ('guidelines' vs query 'guideline')."""
    claim = absence_claim(
        "There is no antidote approved for the toxin in current guidelines."
    )
    queries = ["toxin antidote guideline search", "antidote literature review toxin"]
    assert check_absence(claim, queries) == Verdict.ABSENCE_SUPPORTED


def test_short_entity_free_subject_needs_only_head_noun():
    """A 2-content-word subject ('no changelog available') is not 'specific';
    the head noun alone still evidences it."""
    claim = absence_claim("There is no changelog available.")
    queries = ["project changelog location", "changelog release notes"]
    assert check_absence(claim, queries) == Verdict.ABSENCE_SUPPORTED
