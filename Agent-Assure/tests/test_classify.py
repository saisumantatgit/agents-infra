"""Tests for classify() — Task 3: Kind classification + citation/numeric attach.

TDD protocol: tests written first, run to confirm FAIL, then classify implemented.
"""

from scripts.ground_check import classify, decompose, Claim, ClaimKind


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


# ---------------------------------------------------------------------------
# Fix 1 — CRITICAL: citation digits must not leak into numeric_tokens
# ---------------------------------------------------------------------------

def test_cited_factual_not_numeric():
    """[S3] bracket digit must NOT produce a numeric token or classify as NUMERIC."""
    c = classify(mk("X is true [S3]."))
    assert c.kind == ClaimKind.FACTUAL, f"expected FACTUAL, got {c.kind}"
    assert c.numeric_tokens == (), f"expected no numeric tokens, got {c.numeric_tokens}"


def test_hedged_numeric_no_citation_digit_junk():
    """Hedged numeric claim: numeric_tokens must contain '$4M' but not '1' from [S1]."""
    c = classify(mk("It is likely revenue was $4M [S1]."))
    assert c.kind == ClaimKind.NUMERIC
    tokens_lower = [t.lower() for t in c.numeric_tokens]
    assert any("$4m" in t for t in tokens_lower), f"$4M not found in {c.numeric_tokens}"
    assert "1" not in c.numeric_tokens, f"citation digit '1' leaked into numeric_tokens: {c.numeric_tokens}"


# ---------------------------------------------------------------------------
# Fix 2 — IMPORTANT: capitalized-proper-noun guard consistency between
#          _has_finite_verb (used in NON_CLAIM gate) and _has_verb_like_token
# ---------------------------------------------------------------------------

def test_capitalized_fragment_is_now_scored():
    """SUPERSEDED by RT4-01 (2026-08-30). This test asserted that a fragment of
    capitalized tokens is NON_CLAIM, which was the behaviour red-team round 4
    exploited: `_has_finite_verb` skipped capitalized tokens as proper nouns, so
    "PostgreSQL Fails." had no detectable verb and left the scored denominator.
    Case is one bit per word and the attacker sets it.

    Verb detection is now case-insensitive, so "Redis Postgres" ("Redis" ends
    in -s) reads as a claim. Accepted Error-A on a bare name-list line: it
    resolves UNCITED and blocks PASS, which is recoverable by citing or
    removing the line. A smuggled fabrication is not recoverable.

    NB the CONJUNCTION SPLITTER keeps the capitalization skip
    (`_has_verb_like_token`) — there, under-splitting is the safe error and no
    denominator exit is at stake.
    """
    c = classify(mk("Redis Postgres"))
    assert c.kind != ClaimKind.NON_CLAIM, (
        f"capitalized fragment escaped scoring again: {c.kind}"
    )


# ---------------------------------------------------------------------------
# Fix 3 — IMPORTANT: RELATIONAL beats NUMERIC even with a genuine number
# ---------------------------------------------------------------------------

def test_relational_with_real_number_beats_numeric():
    """RELATIONAL must win over NUMERIC when a causal trigger is present."""
    c = classify(mk("High inflation causes 3% unemployment [S1][S2]."))
    assert c.kind == ClaimKind.RELATIONAL, f"expected RELATIONAL, got {c.kind}"


# ---------------------------------------------------------------------------
# Fix 4 — MINOR: trailing period must not be captured as part of a numeric token
# ---------------------------------------------------------------------------

def test_year_trailing_period_stripped():
    """Numeric token for a year at sentence end must not include trailing '.'."""
    c = classify(mk("The policy was enacted in 2021."))
    assert c.kind == ClaimKind.NUMERIC
    assert "2021" in c.numeric_tokens, f"expected '2021' in {c.numeric_tokens}"
    assert "2021." not in c.numeric_tokens, f"trailing dot leaked into token: {c.numeric_tokens}"


def test_dollar_amount_intact():
    """$4,000,000 must be captured whole, no trailing dot."""
    c = classify(mk("Revenue reached $4,000,000."))
    assert c.kind == ClaimKind.NUMERIC
    assert "$4,000,000" in c.numeric_tokens, f"expected '$4,000,000' in {c.numeric_tokens}"


def test_percentage_intact():
    """25% token must be captured whole."""
    c = classify(mk("Accuracy improved by 25%."))
    assert c.kind == ClaimKind.NUMERIC
    assert any("25%" in t for t in c.numeric_tokens), f"expected '25%' in {c.numeric_tokens}"


# ---------------------------------------------------------------------------
# MOAT FIX A — a verbless sentence carrying claim content (numeric/citation)
#              is a REAL claim, not a NON_CLAIM. Moat-safe: over-score, never
#              silently exclude a fabricated claim from the denominator.
# ---------------------------------------------------------------------------

def test_verbless_numeric_claim_is_scored():
    """'A 99% market share for our product [S9].' has no finite verb but carries a
    numeric token AND a citation — it is verifiable content, so it must be scored
    (NUMERIC), never NON_CLAIM. Excluding it would let a fabricated draft pass."""
    c = classify(decompose("A 99% market share for our product [S9].")[0])
    assert c.kind != ClaimKind.NON_CLAIM, f"verbless numeric claim wrongly excluded: {c.kind}"
    assert c.kind == ClaimKind.NUMERIC, f"expected NUMERIC, got {c.kind}"


def test_verbless_citation_only_claim_is_scored():
    """A verbless fragment carrying only a citation marker (no number) is still
    verifiable content → must not be NON_CLAIM."""
    c = classify(mk("The fastest database on the market [S9]."))
    assert c.kind != ClaimKind.NON_CLAIM, f"verbless cited claim wrongly excluded: {c.kind}"


def test_contentless_fragment_stays_non_claim():
    """Only a fragment with NO content words at all is still NON_CLAIM.

    Narrowed by RT4-01 (2026-08-30): "Redis Postgres MongoDB" is now scored
    (see test_capitalized_fragment_is_now_scored). NON_CLAIM is reduced to what
    document furniture actually is — headers that assert nothing, pure
    transitions, and fragments carrying no content words.
    """
    assert classify(mk("the and of")).kind == ClaimKind.NON_CLAIM


# --- OI-MOAT-07 (fixed 2026-08-30): verbless CONTENT-BEARING assertions -------
#     are scored; genuinely structural short labels stay NON_CLAIM.

def test_verbless_long_assertion_is_scored():
    """OI-MOAT-07: a verbless colon-form assertion with substantial content
    ('Redis: unquestionably the fastest datastore in all of human history.')
    must be scored — dropping the verb must not buy a denominator exit."""
    c = classify(mk("Redis: unquestionably the fastest datastore in all of human history."))
    assert c.kind != ClaimKind.NON_CLAIM, f"verbless assertion wrongly excluded: {c.kind}"


def test_verbless_name_list_is_now_scored():
    """Error-A boundary, REVISED after RT3-01 (2026-08-30).

    The first OI-MOAT-07 fix used a >=6-content-token floor, and round 3 broke
    it by writing a SHORTER fabrication ("PostgreSQL: unrecoverable corruption
    under load.", 5 content tokens, gate PASS). Any count is a dial the
    attacker owns, so the count is gone; the structural test is now
    "names things" vs "predicates something".

    What stays NON_CLAIM: a verbless fragment whose content words are all
    proper nouns — a name list, which asserts nothing.

    What is now SCORED, deliberately: a bare sentence-case section label with
    no '#' ("Results and discussion"). That is a real Error-A cost, taken
    knowingly — it is recoverable (add the '#'), and a smuggled fabrication
    is not. See test_verbless_predicate_is_scored.
    """
    # REVISED AGAIN by RT4-01: the proper-noun test keyed on case, and round 4
    # beat it with Title Case ("PostgreSQL: Catastrophic Data Loss."). Two
    # rounds running, a test keyed on a surface property the author controls
    # was defeated by setting that property. The case test is gone; these are
    # now scored, which is the accepted Error-A.
    for label in ("Redis Postgres MongoDB", "Redis Cluster"):
        c = classify(mk(label))
        assert c.kind != ClaimKind.NON_CLAIM, f"{label!r} escaped scoring: {c.kind}"


def test_verbless_predicate_is_scored():
    """The RT3-01 class: a short verbless fragment that PREDICATES something
    about its subject is an assertion, however few tokens it uses."""
    for smuggle in ("PostgreSQL: unrecoverable corruption under load.",
                    "Redis: catastrophic data loss.",
                    "PostgreSQL: silently lossy."):
        c = classify(mk(smuggle))
        assert c.kind != ClaimKind.NON_CLAIM, f"{smuggle!r} escaped scoring: {c.kind}"
