"""Tests for numeric_ok — Task 5.

TDD sequence:
  Step 1: Write tests (this file).
  Step 2: Run → FAIL (numeric_ok not yet defined).
  Step 3: Implement numeric_ok in scripts/ground_check.py.
  Step 4: Run → PASS.

Required test cases (per brief):
  1. "$4M" grounds against "$4,000,000" → True
  2. "$4M" vs "$9,000,000" → False  (wrong number)
  3. "$4M" vs "$4,000" → False  (order-of-magnitude mismatch)
"""

import pytest

from scripts.ground_check import (
    Claim,
    ClaimKind,
    RetrievedSource,
    classify,
    numeric_ok,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def src(text: str) -> RetrievedSource:
    """Build a minimal RetrievedSource with the given text."""
    return RetrievedSource(
        source_id="S1",
        url=None,
        file_path=None,
        fetched_at="t",
        tool="Read",
        content_sha256="x",
        text=text,
        full_text_source="verbatim",
        captured_via="inline",
        query_provenance="q",
    )


def mk(t: str) -> Claim:
    """Build a classified Claim from text.

    Initial kind is set to NUMERIC per brief — classify() recomputes the kind
    from text content, so the seed value is overwritten but must honor the spec.
    """
    return classify(Claim(0, t, ClaimKind.NUMERIC, (), ()))


# ---------------------------------------------------------------------------
# Required test cases (per brief)
# ---------------------------------------------------------------------------

def test_numeric_ok_unit_norm_match_true():
    """$4M in claim grounds against $4,000,000 in source — True.

    Unit normalization: $4M ≡ $4,000,000.
    """
    claim = mk("The company revenue was $4M last year.")
    sources = [src("According to the filing, revenue reached $4,000,000 in the period.")]
    assert numeric_ok(claim, sources) is True


def test_numeric_ok_wrong_number_false():
    """$4M in claim vs $9,000,000 in source — False.

    Different numerical value; not the same amount.
    """
    claim = mk("The company revenue was $4M last year.")
    sources = [src("The annual report showed revenue of $9,000,000.")]
    assert numeric_ok(claim, sources) is False


def test_numeric_ok_order_of_magnitude_false():
    """$4M in claim vs $4,000 in source — False.

    Order-of-magnitude mismatch: $4,000 is 1000x smaller than $4M.
    """
    claim = mk("The company revenue was $4M last year.")
    sources = [src("The monthly budget was only $4,000 this quarter.")]
    assert numeric_ok(claim, sources) is False


# ---------------------------------------------------------------------------
# Additional coverage
# ---------------------------------------------------------------------------

def test_numeric_ok_no_numeric_tokens():
    """Claim with no numeric_tokens → True (vacuously; nothing to ground).

    numeric_ok should return True when there are no numeric tokens to verify.
    """
    claim = mk("The market expanded rapidly.")
    assert claim.numeric_tokens == ()
    assert numeric_ok(claim, [src("the market grew quickly in the region")]) is True


def test_numeric_ok_empty_sources():
    """Returns False when sources list is empty and claim has numeric tokens."""
    claim = mk("Revenue was $4M last year.")
    assert numeric_ok(claim, []) is False


def test_numeric_ok_percent_match():
    """25% in claim matches '25%' or '25 percent' in source — True."""
    claim = mk("Efficiency improved by 25%.")
    sources = [src("The process showed 25% improvement in the benchmark.")]
    assert numeric_ok(claim, sources) is True


def test_numeric_ok_percent_mismatch():
    """25% in claim vs 30% in source — False."""
    claim = mk("Efficiency improved by 25%.")
    sources = [src("The process showed 30% improvement in the benchmark.")]
    assert numeric_ok(claim, sources) is False


def test_numeric_ok_million_suffix_forms():
    """4 million USD in source matches $4M in claim — True."""
    claim = mk("Revenue was $4M last year.")
    sources = [src("Annual revenue reached 4 million USD this period.")]
    assert numeric_ok(claim, sources) is True


def test_numeric_ok_k_suffix():
    """$400k in claim matches $400,000 in source — True."""
    claim = mk("The budget was $400k.")
    sources = [src("Total budget allocated was $400,000 for the quarter.")]
    assert numeric_ok(claim, sources) is True


def test_numeric_ok_k_vs_million_false():
    """$400k vs $400 million — order-of-magnitude mismatch → False."""
    claim = mk("The budget was $400k.")
    sources = [src("Total budget allocated was $400 million for the project.")]
    assert numeric_ok(claim, sources) is False


def test_numeric_ok_billion_match():
    """$2bn in claim matches $2,000,000,000 in source — True."""
    claim = mk("The fund raised $2bn in total.")
    sources = [src("The fund successfully raised $2,000,000,000 across all rounds.")]
    assert numeric_ok(claim, sources) is True


def test_numeric_ok_multiple_tokens_all_must_match():
    """All numeric tokens must match; partial match → False."""
    claim = mk("Revenue was $4M and profit was $1M.")
    # Source has $4,000,000 but not $1,000,000
    sources = [src("The filing shows revenue of $4,000,000 with operating costs of $500,000.")]
    assert numeric_ok(claim, sources) is False


def test_numeric_ok_multiple_tokens_all_present():
    """All numeric tokens match across sources → True."""
    claim = mk("Revenue was $4M and profit was $1M.")
    sources = [src("Revenue was $4,000,000 and profit was $1,000,000 for the year.")]
    assert numeric_ok(claim, sources) is True


def test_percent_not_matched_against_bare_number():
    """CRITICAL: 25% claim must NOT ground against source containing bare 25.

    A percent token and a bare integer are different unit types.
    Spurious match: claim says '25%', source says 'a team of 25 people'.
    This must return False — the percent is a ratio, not a count.
    """
    claim = mk("Efficiency improved 25% [S1].")
    sources = [src("the project had a team of 25 people")]
    assert numeric_ok(claim, sources) is False


def test_percent_matches_percent():
    """25% claim grounds against source containing '25%' or '25 percent' — True."""
    claim = mk("Efficiency improved 25% [S1].")
    sources_pct = [src("showed a 25% gain in throughput")]
    assert numeric_ok(claim, sources_pct) is True
    sources_word = [src("showed a 25 percent gain in throughput")]
    assert numeric_ok(claim, sources_word) is True


def test_numeric_ok_nfkc_normalization():
    """NFKC normalization: full-width digits in claim token normalize to ASCII.

    Claim token '４Ｍ' (full-width 4 + full-width M) NFKC-normalizes to '4M'
    (4_000_000). Source contains '$4,000,000'. Must return True.
    Without NFKC normalization this would fail because the regex would not
    match the full-width characters.
    """
    # Construct a Claim manually with a full-width numeric token so we bypass
    # the ASCII _NUMERIC_RE in classify() and exercise _parse_numeric_token directly.
    claim_with_fw = Claim(
        index=0,
        text="Revenue was ４Ｍ last year.",  # ４Ｍ (full-width)
        kind=ClaimKind.NUMERIC,
        citations=(),
        numeric_tokens=("４Ｍ",),  # ４Ｍ — full-width token
    )
    sources = [src("Revenue totalled $4,000,000 in the period.")]
    assert numeric_ok(claim_with_fw, sources) is True


def test_exotic_unit_fail_closed():
    """Claim with an unparseable exotic unit fails closed to False.

    '15 lightyears' → if the numeric token normalizes to something with an
    unrecognized suffix, numeric_ok must return False (fail-closed), not True.
    """
    # Construct a Claim manually with an exotic token that _parse_numeric_token
    # cannot resolve (suffix 'lightyears' is not in _UNIT_MULTIPLIERS).
    claim_exotic = Claim(
        index=0,
        text="The star is 15 lightyears away.",
        kind=ClaimKind.NUMERIC,
        citations=(),
        numeric_tokens=("15lightyears",),
    )
    # Source contains the same exotic string — must still return False.
    sources = [src("The star is 15 lightyears away from Earth.")]
    assert numeric_ok(claim_exotic, sources) is False
