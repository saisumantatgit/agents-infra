"""Tests for classify() — Task 3: Kind classification + citation/numeric attach.

TDD protocol: tests written first, run to confirm FAIL, then classify implemented.
"""

from scripts.ground_check import classify, Claim, ClaimKind


def mk(t: str) -> Claim:
    """Construct a stub Claim with FACTUAL placeholder kind, empty attachments."""
    return Claim(index=0, text=t, kind=ClaimKind.FACTUAL, citations=(), numeric_tokens=())


# ---------------------------------------------------------------------------
# Required test behaviors (per task-3-brief.md)
# ---------------------------------------------------------------------------

def test_relational_beats_factual():
    assert classify(mk("Inflation causes unemployment [S1][S2].")).kind == ClaimKind.RELATIONAL


def test_numeric_detected_even_when_hedged():
    c = classify(mk("It is likely revenue was $4M [S1]."))
    assert c.kind == ClaimKind.NUMERIC and "$4M".lower() in [t.lower() for t in c.numeric_tokens]


def test_absence_detected():
    assert classify(mk("There is no legal-domain benchmark.")).kind == ClaimKind.ABSENCE


def test_header_is_non_claim():
    assert classify(mk("## Methods")).kind == ClaimKind.NON_CLAIM


def test_citations_parsed():
    assert classify(mk("X is true [S3].")).citations == ("[S3]",)


# ---------------------------------------------------------------------------
# Additional coverage
# ---------------------------------------------------------------------------

def test_attribution_detected():
    # Per spec, NUMERIC fires before ATTRIBUTION in the ordered cascade.
    # A sentence with both "according to" and a numeric token is NUMERIC.
    # Use a pure attribution sentence (no numeric token) to test attribution.
    assert classify(mk("According to the report, the policy was adopted.")).kind == ClaimKind.ATTRIBUTION


def test_plain_factual():
    # Per spec regex \$?\d[\d,.]* has optional suffix — bare digits (e.g. year) also match.
    # A sentence without ANY digit is the clean FACTUAL case.
    assert classify(mk("The library supports Unicode normalization.")).kind == ClaimKind.FACTUAL


def test_pure_header_h1_is_non_claim():
    assert classify(mk("# Introduction")).kind == ClaimKind.NON_CLAIM


def test_numeric_bare_percentage():
    c = classify(mk("Accuracy improved by 12%."))
    assert c.kind == ClaimKind.NUMERIC
    assert any("12%" in t for t in c.numeric_tokens)


def test_multiple_citations_parsed():
    c = classify(mk("This is supported. [S1][S2]"))
    assert set(c.citations) == {"[S1]", "[S2]"}


def test_source_colon_citation_parsed():
    c = classify(mk("Evidence [source:OpenAI-2023]."))
    assert "[source:OpenAI-2023]" in c.citations


def test_absence_not_form():
    assert classify(mk("This does not exist in the dataset.")).kind == ClaimKind.ABSENCE


def test_relational_leads_to():
    assert classify(mk("High debt leads to credit downgrades [S5].")).kind == ClaimKind.RELATIONAL


def test_hedged_factual_stays_factual_without_number():
    # Hedging alone doesn't change kind; no number → FACTUAL
    c = classify(mk("It is likely the policy will be revised."))
    assert c.kind == ClaimKind.FACTUAL


def test_classify_returns_new_claim():
    """classify must return a new Claim, never mutate input."""
    original = mk("Revenue was $10M [S1].")
    result = classify(original)
    assert result is not original
    assert original.kind == ClaimKind.FACTUAL  # unchanged
    assert original.citations == ()             # unchanged
