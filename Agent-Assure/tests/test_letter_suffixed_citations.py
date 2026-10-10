"""OI-CITE-01 — letter-suffixed citation markers must classify as citations.

Pre-fix behavior (the defect): `[S1a]` fails the `S\\d+` citation regex, so
the marker is invisible — the claim reads as having NO citations (UNCITED,
fail-safe but wrong diagnosis) AND the bracket digit leaks into
numeric_tokens as a spurious token (misclassification pressure).

Fix: the citation regex accepts `S\\d+[a-zA-Z]*`. A letter-suffixed marker
then resolves against the store like any other key: absent -> the precise
UNVERIFIED_CITATION verdict; present (hand-built store) -> grounds normally.
Both directions are diagnosis improvements within the violation class or
legitimate grounding against real evidence — never a new false PASS.

INS-005: this file was run RED against the pre-fix regex (all four tests
failing) before the fix landed; red output recorded in the 2026-07-14 logbook.
"""

from scripts.ground_check import (
    Claim,
    ClaimKind,
    RetrievedSource,
    Verdict,
    classify,
    ground,
)


def _src(source_id: str, text: str) -> RetrievedSource:
    return RetrievedSource(
        source_id=source_id,
        url=None,
        file_path=None,
        fetched_at="t",
        tool="Read",
        content_sha256="x",
        text=text,
        full_text_source="verbatim",
        captured_via="inline",
        query_provenance="redis cluster throughput",
    )


_CLAIM_TEXT = (
    "Redis sustained 5000000 operations per second in the multi-region "
    "cluster [S1a]."
)


def _classified() -> Claim:
    return classify(Claim(0, _CLAIM_TEXT, ClaimKind.FACTUAL, (), ()))


def test_letter_suffixed_marker_is_a_citation():
    """[S1a] must be extracted as a citation, not silently dropped."""
    assert _classified().citations == ("[S1a]",)


def test_no_spurious_numeric_token_from_bracket_digits():
    """The '1' inside [S1a] must not leak into numeric_tokens."""
    # NB: tokens are compared stripped — _NUMERIC_RE's optional `\s?` leaves a
    # trailing space on suffix-less tokens ("5000000 "); downstream parsing
    # strips it. Pre-existing quirk, tracked as OI-NUM-02 in OPEN-ISSUES.
    tokens = {t.strip() for t in _classified().numeric_tokens}
    assert "1" not in tokens, f"bracket digit leaked: {tokens}"
    assert "5000000" in tokens  # the real numeric survives


def test_unresolvable_letter_suffixed_marker_is_unverified_citation():
    """Citing [S1a] against a store without S1a is the precise
    UNVERIFIED_CITATION (fabricated-source) verdict — not UNCITED."""
    store = {"S1": _src("S1", "Redis is an in-memory data structure store.")}
    assert ground(_classified(), store) == Verdict.UNVERIFIED_CITATION


def test_resolvable_letter_suffixed_marker_grounds_normally():
    """A hand-built store MAY carry a letter-suffixed source id; real
    evidence must ground the claim exactly as a numeric id would."""
    store = {
        "S1a": _src(
            "S1a",
            "Redis sustained 5000000 operations per second in the "
            "multi-region cluster during the follow-up test.",
        )
    }
    assert ground(_classified(), store) == Verdict.GROUNDED
