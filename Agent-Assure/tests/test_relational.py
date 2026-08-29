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

from scripts.ground_check import (
    Claim,
    ClaimKind,
    RetrievedSource,
    Verdict,
    extract_arguments,
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
    """Side A in S1, side B in S2, AND a source that ASSERTS the link → GROUNDED.

    CONTRACT CHANGE (OI-MOAT-05, D-04/D-05, 2026-08-30): spec §4.8's
    two-distinct-source rule is NECESSARY BUT NOT SUFFICIENT, and this test
    previously encoded the insufficient form — S1 merely defining "insulin
    resistance" and S2 merely defining "type 2 diabetes" was accepted as
    grounding the CAUSAL claim between them. That is the over-association
    defect itself (identical in shape to corpus rows q25/q26/q48, all
    human-labeled *violation*). S1 now asserts the relation, as the labeled-
    grounded corpus rows q12/q36 do; the endpoint split across two sources is
    retained unchanged.
    """
    s1 = _src(
        "S1",
        "Insulin resistance occurs when cells do not respond well to insulin. "
        "Sustained insulin resistance causes type 2 diabetes to develop over "
        "time as the pancreas can no longer compensate.",
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

    The failure fires at Step 1 (≥2-distinct-source gate): only one citation
    resolves to a verbatim source, so ground_relational returns
    UNVERIFIED_RELATION before it ever reaches the cross-source argument check
    in Steps 3–4.  Both sides being extractable from the claim text is
    irrelevant when the source count requirement is not met.
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
    """NFKC normalization is the sole reason side_A matches when its source text
    uses full-width Latin characters.

    S1's text contains 'Ｉｎｓｕｌｉｎ ｒｅｓｉｓｔａｎｃｅ' (U+FF29…U+FF4E,
    full-width Latin compatibility block).  NFKC maps each full-width code point
    to its ASCII equivalent, so 'Ｉｎｓｕｌｉｎ' → 'Insulin'.  Without NFKC,
    casefold('Ｉｎｓｕｌｉｎ ｒｅｓｉｓｔａｎｃｅ') does NOT contain the ASCII
    substring 'insulin resistance', so window_supports would return False and
    the verdict would be UNVERIFIED_RELATION.  With NFKC the match succeeds and
    the verdict is GROUNDED.

    Note: NFKC does NOT fold Cyrillic homoglyphs (e.g. Cyrillic 'а' U+0430
    stays distinct from Latin 'a' U+0061 under NFKC).  Full-width/compatibility
    characters are the correct vehicle for this test.
    """
    # S1 contains side_A ('insulin resistance') encoded as full-width Latin.
    # A plain casefold (without NFKC) would not match ASCII 'insulin resistance'.
    # The relation-assertion window (required since OI-MOAT-05) lives HERE, so
    # side_A is reachable ONLY through the full-width fold: strip NFKC and this
    # test fails, which is the property it exists to assert (no tautology).
    fw_s1_text = (
        "Ｉｎｓｕｌｉｎ"  # Ｉｎｓｕｌｉｎ
        " "
        "ｒｅｓｉｓｔａｎｃｅ"  # ｒｅｓｉｓｔａｎｃｅ
        " is a metabolic condition that causes type 2 diabetes."
    )
    s1 = _src("S1", fw_s1_text)
    # S2 uses normal ASCII for side_B ('type 2 diabetes') and asserts the
    # relation (required since OI-MOAT-05; the NFKC property under test is
    # unaffected — side_A still only matches via the full-width fold in S1).
    s2 = _src("S2", "Type 2 diabetes is a chronic metabolic disease.")

    claim = _claim(
        "Insulin resistance causes type 2 diabetes [S1][S2].",
        "[S1]",
        "[S2]",
    )
    result = ground_relational(claim, _store(s1, s2))
    # GROUNDED only because NFKC normalizes S1's full-width text to ASCII before
    # window_supports checks for 'insulin resistance'.
    assert result == Verdict.GROUNDED, (
        f"Expected GROUNDED (NFKC normalizes full-width Latin to ASCII), got {result}"
    )


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


# ---------------------------------------------------------------------------
# Numeric-head guard (§4.8 extract_arguments residual — Fix 2)
# ---------------------------------------------------------------------------

def test_extract_arguments_skips_numeric_head():
    """extract_arguments skips bare-numeric tokens when selecting the side_B head.

    'Insulin resistance causes type 2 diabetes [S1][S2].' — the argument phrase
    after the trigger is 'type 2 diabetes'.  Without the numeric-head guard the
    function could return '2' as side_B (a bare digit, not a meaningful noun).
    With the guard, bare-numeric tokens are skipped and the rightmost
    non-numeric content token 'diabetes' is selected as the head noun.

    This test exercises the fix directly via extract_arguments; it would produce
    a wrong side_B ('2' or an equivalent numeric) with the un-patched code.
    """
    args = extract_arguments("Insulin resistance causes type 2 diabetes [S1][S2].")
    assert args is not None, "extract_arguments must not return None for a valid claim"
    side_a, side_b = args
    assert side_b == "diabetes", (
        f"Expected side_B='diabetes' (numeric-head guard skips '2'), got {side_b!r}"
    )
    assert side_a == "resistance", (
        f"Expected side_A='resistance', got {side_a!r}"
    )


# --- OI-MOAT-05: predicate support required (D-05, 2026-08-30) ---------------

def test_endpoint_co_presence_without_asserted_relation_not_grounded():
    """THE OI-MOAT-05 regression. Two sources each state ONE endpoint fact and
    neither asserts any link between them — the causal claim is the draft's own
    invention and must NOT be certified.

    This is the exact shape of corpus rows q25/q26/q48, all human-labeled
    *violation*, which the pre-fix gate returned GROUNDED (three Error-B
    misses). Proven red against the pre-fix tree.
    """
    s1 = _src("S1", "Marketing spend increased twenty percent quarter over quarter.")
    s2 = _src("S2", "Customer signups rose sharply in the weeks after the launch.")
    claim = _claim(
        "Increased marketing spend drives higher customer signups [S1][S2].",
        "[S1]",
        "[S2]",
    )
    assert ground_relational(claim, _store(s1, s2)) == Verdict.UNVERIFIED_RELATION


def test_asserted_relation_with_split_endpoints_is_grounded():
    """Error-A boundary: when a source DOES assert the relation (and the
    endpoints still split across two distinct verbatim sources), the claim
    grounds — mirroring corpus rows q12/q36, both human-labeled *grounded*."""
    s1 = _src(
        "S1",
        "Elevated cortisol leads to impaired sleep by delaying sleep onset.",
    )
    s2 = _src(
        "S2",
        "Impaired sleep is commonly observed together with elevated cortisol.",
    )
    claim = _claim(
        "Elevated cortisol leads to impaired sleep [S1][S2].",
        "[S1]",
        "[S2]",
    )
    assert ground_relational(claim, _store(s1, s2)) == Verdict.GROUNDED


def test_trigger_without_both_endpoints_not_grounded():
    """A relational trigger somewhere in a source is not enough — the asserting
    window must carry BOTH endpoints, or any source discussing causation at all
    would ground any relation between any two nouns it mentions."""
    s1 = _src(
        "S1",
        "Marketing spend increased. Seasonality causes revenue fluctuations.",
    )
    s2 = _src("S2", "Customer signups rose sharply after the launch.")
    claim = _claim(
        "Increased marketing spend drives higher customer signups [S1][S2].",
        "[S1]",
        "[S2]",
    )
    assert ground_relational(claim, _store(s1, s2)) == Verdict.UNVERIFIED_RELATION
