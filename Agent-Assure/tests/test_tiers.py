"""Tests for T1 (verbatim) and T2 (lexical-F1 + numeric-presence) grounding tiers.

TDD sequence:
  Step 1: Write tests (this file).
  Step 2: Run → FAIL (t1_verbatim and t2_lexical not yet defined).
  Step 3: Implement functions in scripts/ground_check.py.
  Step 4: Run → PASS.
"""

from scripts.ground_check import (
    Claim,
    ClaimKind,
    RetrievedSource,
    classify,
    t1_verbatim,
    t2_lexical,
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
# T1 verbatim tests
# ---------------------------------------------------------------------------

def test_t1_hits_on_contiguous_span():
    """A ≥8-token contiguous span from the claim must appear in a source.

    Claim content tokens after citation strip: redis handles 100k operations
    per second on commodity hardware — exactly 8 tokens, matching min_quote_len=8.
    The source contains all 8 tokens as a contiguous verbatim span.
    """
    assert t1_verbatim(
        mk("Redis handles 100K operations per second on commodity hardware [S1]."),
        [src("benchmarks show Redis handles 100K operations per second on commodity hardware")],
    )


def test_t1_misses_when_no_span_in_source():
    """Returns False when the source has no matching span of ≥8 tokens."""
    assert not t1_verbatim(
        mk("Redis handles 100K operations per second on commodity hardware [S1]."),
        [src("databases are fast and efficient for many workloads in production")],
    )


def test_t1_case_insensitive():
    """Match is case-insensitive (NFKC + casefolded).

    Claim content tokens (8): redis handles 100k operations per second on
    commodity (trailing 'hardware' skipped — only 8 needed for the span match).
    Source contains matching tokens in lowercase form.
    """
    assert t1_verbatim(
        mk("Redis Handles 100K Operations Per Second on commodity hardware [S1]."),
        [src("benchmarks show redis handles 100k operations per second on commodity hardware")],
    )


def test_t1_min_quote_len_boundary():
    """Exactly min_quote_len=8 tokens → hit; min_quote_len=9 → miss.

    Claim content tokens: the system processes requests at high speed always done
    (9 tokens total). The source contains the 8-token prefix
    'the system processes requests at high speed always' verbatim, but NOT all 9
    since 'done' is absent. So min_quote_len=8 hits (8-token window present),
    and min_quote_len=9 misses (no 9-token contiguous span is shared).
    """
    # 9 content tokens total; source shares the first 8 contiguous ones
    claim_text = "the system processes requests at high speed always done [S1]."
    source_text = "the system processes requests at high speed always in production"
    assert t1_verbatim(mk(claim_text), [src(source_text)], min_quote_len=8)
    # min_quote_len=9: no 9-token contiguous span is shared between claim and source
    assert not t1_verbatim(mk(claim_text), [src(source_text)], min_quote_len=9)


def test_t1_empty_sources():
    """Returns False when source list is empty."""
    assert not t1_verbatim(mk("Redis handles 100K operations per second on commodity hardware [S1]."), [])


def test_t1_multiple_sources_any_hit():
    """Returns True if ANY source contains the span."""
    assert t1_verbatim(
        mk("Redis handles 100K operations per second on commodity hardware [S1]."),
        [
            src("completely unrelated text about nothing in particular here"),
            src("benchmarks show Redis handles 100K operations per second on commodity hardware"),
        ],
    )


def test_t1_whitespace_collapse():
    """Extra whitespace in claim or source is collapsed before matching."""
    assert t1_verbatim(
        mk("Redis  handles  100K  operations  per  second  on  commodity  hardware [S1]."),
        [src("benchmarks show Redis handles 100K operations per second on commodity hardware")],
    )


# ---------------------------------------------------------------------------
# T2 lexical tests
# ---------------------------------------------------------------------------

def test_t2_requires_numbers_present():
    """T2 fails when a required numeric token is absent from the best window."""
    s = [src("the system processes about twenty five percent more records")]
    assert not t2_lexical(mk("throughput rose 25% [S1]."), s)


def test_t2_hits_when_words_and_numbers_match():
    """T2 succeeds when content-word F1 ≥ tau AND numeric token is present.

    True F1 penalises long, information-rich windows even when they fully cover
    the claim (precision pulls F1 below recall-only).  The default tau=0.65 is
    a calibration placeholder (spec §12.5) — this test passes an explicit
    lex_tau=0.50 to demonstrate the pass-case.  Claim content words:
    [throughput, rose, 25] (3).  Source content words: [throughput, rose, 25,
    system, processed, requests, efficiently] (7).  F1 = 2*(3/7)*(3/3) /
    ((3/7)+(3/3)) = 0.60.  The default is intentionally NOT lowered;
    calibration will tune it to a representative corpus.
    """
    source_text = (
        "throughput rose 25% as the system processed more requests efficiently"
    )
    assert t2_lexical(mk("throughput rose 25% [S1]."), [src(source_text)], lex_tau=0.50)


def test_t2_fails_when_f1_below_tau():
    """T2 fails when F1 < lex_tau even if numeric token is present."""
    # Numeric 25% present but almost no content-word overlap
    source_text = "the quarterly budget allocation was revised upward by 25% this year"
    # Claim content words: throughput rose   → F1 will be very low
    assert not t2_lexical(
        mk("throughput rose 25% [S1]."),
        [src(source_text)],
        lex_tau=0.65,
    )


def test_t2_empty_sources():
    """Returns False when source list is empty."""
    assert not t2_lexical(mk("throughput rose 25% [S1]."), [])


def test_t2_no_numeric_tokens_only_f1_gate():
    """When claim has no numeric tokens, only F1 gate applies."""
    # Claim with no numbers; source has high word overlap
    source_text = (
        "Redis handles many operations per second on commodity hardware in production"
    )
    claim = mk("Redis handles operations per second [S1].")
    # Numeric tokens should be empty; T2 should succeed on F1 alone
    assert claim.numeric_tokens == ()
    assert t2_lexical(claim, [src(source_text)])


def test_t2_multiple_sources_best_window():
    """T2 uses the best window across all sources.

    Uses explicit lex_tau=0.40 to demonstrate multi-source selection (bad_source
    scores 0; good_source wins).  Good source content words: [throughput, rose,
    25, system, processed, many, requests, efficiently] (8).  Claim content
    words: [throughput, rose, 25] (3).  F1 = 2*(3/8)*(3/3)/((3/8)+(3/3)) ≈
    0.545.  Default tau=0.65 is intentionally NOT changed; this test isolates
    multi-source selection behaviour from the calibration threshold.
    """
    bad_source = src("nothing useful here at all about any topic whatsoever")
    good_source = src(
        "throughput rose 25% as the system processed many more requests efficiently"
    )
    assert t2_lexical(mk("throughput rose 25% [S1]."), [bad_source, good_source], lex_tau=0.40)


def test_t2_window_is_local():
    """T2 only scores a ±2-sentence window, not the full source."""
    # The matching sentences are far from the numeric token — but the number
    # appears in a distant sentence and the best local window won't have it.
    # Build a multi-sentence source where 25% is in sentence 1 and
    # "throughput rose" content words appear only in sentence 6 (well beyond ±2).
    sentences = [
        "The load increased by 25%.",         # sentence 0: has the number
        "Latency went up slightly.",           # sentence 1
        "Engineers reviewed the system.",      # sentence 2
        "New hardware was provisioned.",       # sentence 3
        "Monitoring dashboards were updated.", # sentence 4
        "throughput rose significantly.",      # sentence 5: has content words
    ]
    source_text = " ".join(sentences)
    # The window around sentence 5 (±2 → sentences 3-5) does NOT contain "25%"
    # so T2 should return False.
    assert not t2_lexical(mk("throughput rose 25% [S1]."), [src(source_text)])
