"""Tests for decompose() — deterministic claim decomposition.

TDD contract: each test below was written BEFORE the implementation existed
and run to confirm RED, then the implementation was added to turn it GREEN.
"""

from scripts.ground_check import ClaimKind, decompose


# ---------------------------------------------------------------------------
# Baseline: sentence segmentation
# ---------------------------------------------------------------------------

def test_two_sentences_two_claims():
    claims = decompose("Redis is fast. Postgres is durable.")
    assert [c.text for c in claims] == ["Redis is fast.", "Postgres is durable."]


def test_indices_are_ordered():
    claims = decompose("A is true. B is false.")
    assert [c.index for c in claims] == [0, 1]


def test_single_sentence_one_claim():
    claims = decompose("Latency is low.")
    assert len(claims) == 1
    assert claims[0].index == 0
    assert claims[0].text == "Latency is low."


def test_empty_string_returns_empty():
    assert decompose("") == []


# ---------------------------------------------------------------------------
# Data model constraints
# ---------------------------------------------------------------------------

def test_kind_is_factual_placeholder():
    claims = decompose("Redis is fast.")
    assert claims[0].kind == ClaimKind.FACTUAL


def test_citations_empty_tuple():
    claims = decompose("Redis is fast.")
    assert claims[0].citations == ()


def test_numeric_tokens_empty_tuple():
    claims = decompose("Redis is fast.")
    assert claims[0].numeric_tokens == ()


# ---------------------------------------------------------------------------
# NFKC normalization
# ---------------------------------------------------------------------------

def test_nfkc_normalization_applied():
    # Fullwidth Latin characters (U+FF21–U+FF5A) → ASCII under NFKC.
    # Input uses fullwidth R-e-d-i-s (U+FF32 U+FF45 U+FF44 U+FF49 U+FF53).
    fullwidth_input = "Ｒｅｄｉｓ is fast."
    claims = decompose(fullwidth_input)
    assert len(claims) == 1
    # After NFKC normalization the fullwidth chars collapse to ASCII "Redis"
    assert claims[0].text.startswith("Redis")


# ---------------------------------------------------------------------------
# Conjunction split: ` and ` with verb on both sides → split
# ---------------------------------------------------------------------------

def test_conjunction_and_with_verbs_splits():
    # Both sides have a verb-like token ("is" appears on both sides)
    claims = decompose("Redis is fast and Postgres is durable.")
    texts = [c.text for c in claims]
    assert len(texts) == 2
    assert any("Redis" in t for t in texts)
    assert any("Postgres" in t for t in texts)


def test_conjunction_and_without_verb_no_split():
    # "speed and reliability" — neither "speed" nor "reliability" is a verb
    claims = decompose("Redis offers speed and reliability.")
    assert len(claims) == 1


# ---------------------------------------------------------------------------
# Conjunction split: `; ` with verb on both sides → split
# ---------------------------------------------------------------------------

def test_semicolon_with_verbs_splits():
    # syntok treats the semicolon within the same sentence segment
    # "A is true; B is false" — both sides have a verb ("is")
    claims = decompose("A is true; B is false.")
    texts = [c.text for c in claims]
    assert len(texts) == 2
    assert any("A is true" in t for t in texts)
    assert any("B is false" in t for t in texts)


def test_semicolon_without_verb_no_split():
    # "apples; oranges" — neither side has a verb
    claims = decompose("She likes apples; oranges.")
    # "likes" is only on the left side; right side "oranges" has no verb
    # conservative: under-split beats over-split — no split
    assert len(claims) == 1


# ---------------------------------------------------------------------------
# Determinism: same input → same output
# ---------------------------------------------------------------------------

def test_determinism():
    text = "Redis is fast. Postgres is durable. MySQL is old."
    first = decompose(text)
    second = decompose(text)
    assert first == second


# ---------------------------------------------------------------------------
# Proper-noun conjunction: compound subject must NOT split (Finding 1)
# ---------------------------------------------------------------------------

def test_proper_noun_conjunction_not_split():
    # "Redis and Postgres are fast." has a compound SUBJECT — one predicate.
    # Conservative spec: compound subject is ONE claim, not two.
    # Bug: _has_verb_like_token fires on "Redis" (ends in 's') → over-split.
    claims = decompose("Redis and Postgres are fast.")
    assert len(claims) == 1


# ---------------------------------------------------------------------------
# Single-level split contract: no recursion (Finding 2)
# ---------------------------------------------------------------------------

def test_multi_conjunction_single_split():
    # Three clauses joined by 'and'. Only ONE split is attempted (spec §9:
    # single-level only). First conjunction splits; the second 'and C is large'
    # stays in the right half.
    claims = decompose("A is fast and B is slow and C is large.")
    assert len(claims) == 2
    texts = [c.text for c in claims]
    assert any("A is fast" in t for t in texts)
    assert any("B is slow and C is large" in t for t in texts)


# ---------------------------------------------------------------------------
# Whitespace-only input (trivial contract)
# ---------------------------------------------------------------------------

def test_whitespace_only_returns_empty():
    assert decompose("   ") == []
