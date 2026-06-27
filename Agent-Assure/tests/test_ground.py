"""Tests for the per-claim verdict dispatcher ground() (Task 8, spec §4.4).

TDD sequence:
  Step 1: Write tests (this file) — fail at import (ground/_session_queries
          are not yet defined).
  Step 2: Run → FAIL (proves test integrity).
  Step 3: Implement ground + _session_queries.
  Step 4: Run → PASS.

One test per branch of the §4.4 decision logic, plus _session_queries coverage.
Fixtures are built via classify(...) (real classifier) and plain store dicts,
so each test exercises the dispatcher against genuinely classified claims.
"""

from scripts.ground_check import (
    Claim,
    ClaimKind,
    RetrievedSource,
    Verdict,
    classify,
    ground,
    _session_queries,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _src(
    source_id: str,
    text: str,
    full_text_source: str = "verbatim",
    query_provenance: str = "q",
) -> RetrievedSource:
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
        query_provenance=query_provenance,
    )


def _store(*sources: RetrievedSource) -> dict[str, RetrievedSource]:
    """Build a store dict keyed by source_id."""
    return {s.source_id: s for s in sources}


def _classified(text: str) -> Claim:
    """Run a raw claim string through the real classifier."""
    return classify(Claim(index=0, text=text, kind=ClaimKind.FACTUAL,
                          citations=(), numeric_tokens=()))


# ---------------------------------------------------------------------------
# Branch 1: NON_CLAIM → GROUNDED
# ---------------------------------------------------------------------------

def test_non_claim_returns_grounded():
    """A header (NON_CLAIM) short-circuits to GROUNDED without touching the store."""
    claim = _classified("## Background and methodology")
    assert claim.kind == ClaimKind.NON_CLAIM, (
        f"fixture must classify as NON_CLAIM, got {claim.kind}"
    )
    result = ground(claim, {})
    assert result == Verdict.GROUNDED, (
        f"Expected GROUNDED for NON_CLAIM, got {result}"
    )


# ---------------------------------------------------------------------------
# Branch 2: RELATIONAL delegates to ground_relational
# ---------------------------------------------------------------------------

def test_relational_delegates_to_ground_relational():
    """RELATIONAL claim is routed through ground_relational (two-distinct-source rule).

    Side A ('insulin resistance') in S1, side B ('type 2 diabetes') in S2,
    both verbatim → ground_relational returns GROUNDED. This proves the
    dispatcher delegated (a plain factual path would not produce GROUNDED here
    since no contiguous 8-token span / F1>=0.65 window exists across them).
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
    claim = _classified("Insulin resistance causes type 2 diabetes [S1][S2].")
    assert claim.kind == ClaimKind.RELATIONAL
    result = ground(claim, _store(s1, s2))
    assert result == Verdict.GROUNDED, (
        f"Expected GROUNDED via ground_relational delegation, got {result}"
    )


def test_relational_delegation_unverified_relation():
    """Single verbatim source → ground_relational returns UNVERIFIED_RELATION.

    This verdict is UNIQUE to the relational path, so observing it proves the
    dispatcher delegated rather than running the factual/tier path.
    """
    s1 = _src("S1", "Insulin resistance is a metabolic condition.")
    claim = _classified("Insulin resistance causes type 2 diabetes [S1].")
    assert claim.kind == ClaimKind.RELATIONAL
    result = ground(claim, _store(s1))
    assert result == Verdict.UNVERIFIED_RELATION, (
        f"Expected UNVERIFIED_RELATION via delegation, got {result}"
    )


# ---------------------------------------------------------------------------
# Branch 3: ABSENCE delegates to check_absence(_session_queries)
# ---------------------------------------------------------------------------

def test_absence_delegates_and_supported():
    """ABSENCE claim is routed through check_absence with session queries.

    Two distinct queries mention the subject head noun ('contraindications'),
    so check_absence returns ABSENCE_SUPPORTED — a verdict reachable only via
    the absence path.
    """
    s1 = _src("S1", "...", query_provenance="contraindications of aspirin")
    s2 = _src("S2", "...", query_provenance="aspirin contraindications list")
    claim = _classified("There are no contraindications for this drug.")
    assert claim.kind == ClaimKind.ABSENCE
    result = ground(claim, _store(s1, s2))
    assert result == Verdict.ABSENCE_SUPPORTED, (
        f"Expected ABSENCE_SUPPORTED via check_absence delegation, got {result}"
    )


def test_absence_delegates_and_unverified():
    """ABSENCE claim with no matching queries → UNVERIFIED_ABSENCE (delegation proof)."""
    s1 = _src("S1", "...", query_provenance="weather in paris")
    claim = _classified("There are no contraindications for this drug.")
    assert claim.kind == ClaimKind.ABSENCE
    result = ground(claim, _store(s1))
    assert result == Verdict.UNVERIFIED_ABSENCE, (
        f"Expected UNVERIFIED_ABSENCE via delegation, got {result}"
    )


# ---------------------------------------------------------------------------
# Branch 4: no citations → UNCITED
# ---------------------------------------------------------------------------

def test_factual_no_citations_uncited():
    """A FACTUAL claim with zero citations → UNCITED."""
    claim = _classified("Redis is an in-memory data store.")
    assert claim.kind == ClaimKind.FACTUAL
    assert claim.citations == ()
    result = ground(claim, {})
    assert result == Verdict.UNCITED, (
        f"Expected UNCITED for uncited factual claim, got {result}"
    )


# ---------------------------------------------------------------------------
# Branch 5: unresolved citation → UNVERIFIED_CITATION
# ---------------------------------------------------------------------------

def test_unresolved_citation_unverified_citation():
    """A cited claim whose citation is absent from the store → UNVERIFIED_CITATION."""
    claim = _classified("Redis is an in-memory data store [S9].")
    assert claim.citations == ("[S9]",)
    result = ground(claim, {})  # empty store — [S9] resolves to None
    assert result == Verdict.UNVERIFIED_CITATION, (
        f"Expected UNVERIFIED_CITATION for unresolved citation, got {result}"
    )


# ---------------------------------------------------------------------------
# Branch 6: falsy source text → UNGROUNDABLE
# ---------------------------------------------------------------------------

def test_empty_source_text_ungroundable():
    """A resolved source with empty text (snippet-only / no full text) → UNGROUNDABLE."""
    s1 = _src("S1", "")  # falsy text
    claim = _classified("Redis is an in-memory data store [S1].")
    result = ground(claim, _store(s1))
    assert result == Verdict.UNGROUNDABLE, (
        f"Expected UNGROUNDABLE for empty-text source, got {result}"
    )


# ---------------------------------------------------------------------------
# Branch 7: haiku_summary-only cited source → UNGROUNDABLE (tiers do NOT run)
# ---------------------------------------------------------------------------

def test_haiku_summary_only_ungroundable_tiers_not_run(monkeypatch):
    """All cited sources are haiku_summary → UNGROUNDABLE, and tiers must NOT run.

    The source text contains an exact 8-token span of the claim, so if t1/t2
    were (wrongly) allowed to run on it they would return GROUNDED. We patch
    t1_verbatim and t2_lexical to raise, asserting they are never reached.
    """
    text = "Redis handles 100K operations per second on commodity hardware."
    s1 = _src("S1", text, full_text_source="haiku_summary")

    def _boom(*a, **k):
        raise AssertionError("tiers must not run when no verbatim source exists")

    import scripts.ground_check as gc
    monkeypatch.setattr(gc, "t1_verbatim", _boom)
    monkeypatch.setattr(gc, "t2_lexical", _boom)

    claim = _classified(
        "Redis handles 100K operations per second on commodity hardware [S1]."
    )
    result = ground(claim, _store(s1))
    assert result == Verdict.UNGROUNDABLE, (
        f"Expected UNGROUNDABLE for haiku-only source, got {result}"
    )


# ---------------------------------------------------------------------------
# Branch 8: NUMERIC with bad number → UNVERIFIED_NUMBER
# ---------------------------------------------------------------------------

def test_numeric_bad_number_unverified_number():
    """NUMERIC claim whose number is absent from the verbatim source → UNVERIFIED_NUMBER."""
    s1 = _src("S1", "Redis can handle around fifty thousand operations per second.")
    claim = _classified("Redis handles 100K operations per second [S1].")
    assert claim.kind == ClaimKind.NUMERIC
    assert claim.numeric_tokens  # has a numeric token
    result = ground(claim, _store(s1))
    assert result == Verdict.UNVERIFIED_NUMBER, (
        f"Expected UNVERIFIED_NUMBER for unmatched number, got {result}"
    )


# ---------------------------------------------------------------------------
# Branch 9: verbatim source supports via T1/T2 → GROUNDED
# ---------------------------------------------------------------------------

def test_verbatim_support_grounded():
    """A verbatim source containing the claim's exact span → GROUNDED via T1."""
    text = "Redis handles 100K operations per second on commodity hardware."
    s1 = _src("S1", text)
    claim = _classified(
        "Redis handles 100K operations per second on commodity hardware [S1]."
    )
    result = ground(claim, _store(s1))
    assert result == Verdict.GROUNDED, (
        f"Expected GROUNDED for supporting verbatim source, got {result}"
    )


# ---------------------------------------------------------------------------
# Branch 10: real verbatim source that does NOT support → UNGROUNDED
# ---------------------------------------------------------------------------

def test_verbatim_no_support_ungrounded():
    """A real, non-empty verbatim source that fails T1 and T2 → UNGROUNDED."""
    s1 = _src(
        "S1",
        "PostgreSQL is a powerful open-source relational database system "
        "used widely in production environments around the world today.",
    )
    claim = _classified(
        "Redis is an in-memory key-value store optimized for caching workloads [S1]."
    )
    assert claim.kind == ClaimKind.FACTUAL
    result = ground(claim, _store(s1))
    assert result == Verdict.UNGROUNDED, (
        f"Expected UNGROUNDED for non-supporting verbatim source, got {result}"
    )


# ---------------------------------------------------------------------------
# _session_queries helper
# ---------------------------------------------------------------------------

def test_session_queries_distinct():
    """_session_queries returns the DISTINCT query_provenance values of the store."""
    s1 = _src("S1", "a", query_provenance="alpha")
    s2 = _src("S2", "b", query_provenance="beta")
    s3 = _src("S3", "c", query_provenance="alpha")  # duplicate provenance
    result = _session_queries(_store(s1, s2, s3))
    assert sorted(result) == ["alpha", "beta"], (
        f"Expected distinct ['alpha','beta'], got {sorted(result)}"
    )


def test_session_queries_empty_store():
    """An empty store yields no queries."""
    assert _session_queries({}) == []
