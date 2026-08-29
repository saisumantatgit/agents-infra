"""Tests for t2_lexical_score — the raw T2 lexical F1 score, extracted from
t2_lexical so a calibration sweep can re-threshold lex_tau post-hoc over a
stored score without re-running the gate.

TDD sequence:
  Step 1: Write tests (this file).
  Step 2: Run → FAIL (t2_lexical_score not yet defined).
  Step 3: Extract the score computation from t2_lexical into t2_lexical_score
          in scripts/ground_check.py; make t2_lexical call it.
  Step 4: Run → PASS (new + all existing).
"""

import pytest

from scripts.ground_check import (
    _LEX_TAU_DEFAULT,
    Claim,
    ClaimKind,
    RetrievedSource,
    classify,
    t2_lexical,
    t2_lexical_score,
)


# ---------------------------------------------------------------------------
# Helpers (mirrors tests/test_tiers.py)
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
# Raw score value tests
# ---------------------------------------------------------------------------

def test_t2_lexical_score_near_verbatim_window_is_high():
    """A claim whose content words and numeric token are almost entirely
    covered by a source window scores high (the docstring derives the exact
    value; asserting it beats asserting a threshold comparison).

    Claim content words: [revenue, grew, 12, year, year] (5, 'over' is a stop
    word). Window content words: [company, filings, show, revenue, grew, 12,
    year, year, across, segment] (10). Intersection = 5 (revenue, grew, 12,
    year x2). P = 5/10 = 0.5, R = 5/5 = 1.0, F1 = 2*0.5*1.0/1.5 = 0.667.
    Numeric gate: '12%' is present verbatim in the source, so the gate passes.
    """
    claim_text = "Revenue grew 12% year over year [S1]."
    source_text = (
        "Company filings show that revenue grew 12% year over year "
        "across the segment."
    )
    score = t2_lexical_score(claim_text, source_text)
    # The exact derived value (2*0.5*1.0/1.5), not a threshold comparison:
    # this test is about the SCORE, and must not move when the deployed
    # operating point moves (OI-CAL-01).
    assert score == pytest.approx(2 / 3)


def test_t2_lexical_score_unrelated_claim_is_low():
    """A claim with no lexical overlap with the source scores < 0.3 (in fact 0.0,
    since claim and source content-word sets are fully disjoint and the claim
    carries no numeric tokens to gate on)."""
    claim_text = "Solar panels reduce carbon emissions significantly [S1]."
    source_text = "The quarterly financial report showed strong revenue growth this year."
    score = t2_lexical_score(claim_text, source_text)
    assert score < 0.3


def test_t2_lexical_score_returns_float_not_bool():
    """t2_lexical_score returns a raw float, not a bool — the whole point of
    the extraction is to preserve the score instead of collapsing it."""
    claim_text = "Revenue grew 12% year over year [S1]."
    source_text = (
        "Company filings show that revenue grew 12% year over year "
        "across the segment."
    )
    score = t2_lexical_score(claim_text, source_text)
    assert isinstance(score, float)
    assert score != True and score != False  # noqa: E712 — guard against bool subtyping tautology


# ---------------------------------------------------------------------------
# Behavior-preservation: t2_lexical(...) == t2_lexical_score(...) >= lex_tau
# ---------------------------------------------------------------------------

def test_t2_lexical_matches_score_threshold_on_three_fixtures():
    """t2_lexical must be exactly equivalent to thresholding t2_lexical_score
    at the deployed lex_tau (``_LEX_TAU_DEFAULT``) — the refactor must not
    change grounding
    behavior, only expose the raw score.

    Three fixture pairs spanning the outcome space. The threshold is read
    from the constant, never hardcoded: a literal here would silently
    re-couple the suite to one operating point (it did — this test broke
    on the OI-CAL-01 0.65->0.71 deployment because it said 0.65 twice).
      1. High word + numeric overlap -> True.
      2. Zero word overlap, no numeric tokens -> False.
      3. Numeric token present but low word overlap -> False (nonzero score).
    """
    fixtures = [
        (
            "Revenue grew 12% year over year [S1].",
            "Company filings show that revenue grew 12% year over year "
            "across the segment.",
        ),
        (
            "Solar panels reduce carbon emissions significantly [S1].",
            "The quarterly financial report showed strong revenue growth this year.",
        ),
        (
            "throughput rose 25% [S1].",
            "the quarterly budget allocation was revised upward by 25% this year",
        ),
    ]

    for claim_text, source_text in fixtures:
        claim = mk(claim_text)
        source = src(source_text)
        expected = t2_lexical_score(claim_text, source_text) >= _LEX_TAU_DEFAULT
        actual = t2_lexical(claim, [source])
        assert actual == expected, (
            f"t2_lexical({claim_text!r}, ...) = {actual}, "
            f"but t2_lexical_score(...) >= {_LEX_TAU_DEFAULT} = {expected}"
        )


def test_t2_lexical_score_enables_post_hoc_rethreshold():
    """The entire point of the extraction: the same stored score can be
    re-thresholded at a different lex_tau without recomputation, and doing so
    changes t2_lexical's verdict exactly as if it had been called with that
    lex_tau directly.

    Fixture: F1 = 0.60 (from tests/test_tiers.py::test_t2_hits_when_words_and_numbers_match).
    At tau=0.65 (default) -> False. At tau=0.50 -> True.
    """
    claim_text = "throughput rose 25% [S1]."
    source_text = "throughput rose 25% as the system processed more requests efficiently"
    claim = mk(claim_text)
    source = src(source_text)

    score = t2_lexical_score(claim_text, source_text)

    assert (score >= 0.65) == t2_lexical(claim, [source], lex_tau=0.65)
    assert (score >= 0.50) == t2_lexical(claim, [source], lex_tau=0.50)
    # The two lex_tau values must actually disagree for this fixture to prove
    # the point (otherwise the assertions above are tautological).
    assert t2_lexical(claim, [source], lex_tau=0.65) != t2_lexical(claim, [source], lex_tau=0.50)
