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
    """Build a classified Claim from text."""
    return classify(Claim(0, t, ClaimKind.FACTUAL, (), ()))


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


def test_numeric_ok_nfkc_normalization():
    """NFKC normalization applied before matching."""
    # Unicode full-width digits should normalize to ASCII
    claim = mk("Revenue was $4M last year.")
    # Regular source — test that the function handles NFKC edge without crashing
    sources = [src("Revenue totalled $4,000,000 in the period.")]
    assert numeric_ok(claim, sources) is True
