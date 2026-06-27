"""Tests for score_report() — grounding SCORE + threshold + hard override (Task 9, spec §4.5/§4.7).

TDD sequence:
  Step 1: Write tests (this file) — fail at import (score_report not yet defined).
  Step 2: Run → FAIL (proves test integrity).
  Step 3: Implement score_report.
  Step 4: Run → PASS.

Fixtures are built via classify(...) (real classifier) and plain store dicts, so
each test exercises the real ground() dispatcher and the real arithmetic — not a
mocked verdict stream. The §4.7 golden (2 GROUNDED + 1 UNVERIFIED_CITATION → 66.7,
NEEDS_WORK) is the moat-integrity assertion: the violation stays in the denominator
(2/3) and the hard override caps the gate.
"""

from scripts.ground_check import (
    Claim,
    ClaimKind,
    RetrievedSource,
    Verdict,
    classify,
    decompose,
    ground,
    score_report,
)


# ---------------------------------------------------------------------------
# Helpers (mirror tests/test_ground.py conventions)
# ---------------------------------------------------------------------------

def _src(
    source_id: str,
    text: str,
    full_text_source: str = "verbatim",
    query_provenance: str = "q",
) -> RetrievedSource:
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
    return {s.source_id: s for s in sources}


def _classified(index: int, text: str) -> Claim:
    """Run a raw claim string through the real classifier at a given index."""
    return classify(Claim(index=index, text=text, kind=ClaimKind.FACTUAL,
                          citations=(), numeric_tokens=()))


# Reusable verbatim source whose exact 8-token span grounds the claim below.
_GROUNDED_TEXT = "Redis handles 100K operations per second on commodity hardware."
_GROUNDED_CLAIM_TEXT = (
    "Redis handles 100K operations per second on commodity hardware [{cite}]."
)


def _grounded_claim(index: int, cite: str) -> Claim:
    return _classified(index, _GROUNDED_CLAIM_TEXT.format(cite=cite))


def _uncited_claim(index: int) -> Claim:
    """A FACTUAL claim with no citations → UNCITED (a scored violation)."""
    return _classified(index, "Redis is an in-memory data store.")


def _unverified_citation_claim(index: int) -> Claim:
    """A cited claim whose citation is absent from the store → UNVERIFIED_CITATION."""
    return _classified(index, "Redis is an in-memory data store [S9].")


# ---------------------------------------------------------------------------
# §4.7 GOLDEN — the moat-integrity assertion
# ---------------------------------------------------------------------------

def test_worked_example_66_7_needs_work():
    """3 scored claims: 2 GROUNDED + 1 UNVERIFIED_CITATION → 66.7, NEEDS_WORK.

    The UNVERIFIED_CITATION claim STAYS in the denominator (2/3 = 66.7), and the
    hard override caps the gate at NEEDS_WORK independent of score. This is the
    anti-gaming invariant: a fabricated-citation draft can never post PASS.
    """
    s1 = _src("S1", _GROUNDED_TEXT)
    store = _store(s1)  # [S9] is absent → UNVERIFIED_CITATION

    c0 = _grounded_claim(0, "S1")
    c1 = _grounded_claim(1, "S1")
    c2 = _unverified_citation_claim(2)
    claims = [c0, c1, c2]

    # Verdict integrity: prove the fixtures actually produce the intended verdicts.
    assert ground(c0, store) == Verdict.GROUNDED
    assert ground(c1, store) == Verdict.GROUNDED
    assert ground(c2, store) == Verdict.UNVERIFIED_CITATION

    rep = score_report(claims, store)

    assert abs(rep["grounding_score"] - 66.7) < 0.05  # violation stays in denominator
    assert rep["gate"] == "NEEDS_WORK"                 # hard override
    assert rep["scored_claims"] == 3
    # Retained appendix carries the one non-grounded scored claim.
    assert len(rep["retained_appendix"]) == 1
    assert rep["retained_appendix"][0]["index"] == 2
    assert rep["retained_appendix"][0]["verdict"] == Verdict.UNVERIFIED_CITATION.value


def test_hard_override_caps_high_score():
    """Hard override fires even when score >= threshold.

    9 GROUNDED + 1 UNVERIFIED_CITATION = 90.0 (== default threshold, so NOT a
    threshold failure). Gate must still be NEEDS_WORK purely because of the
    UNVERIFIED_CITATION presence. This isolates the override from the threshold.
    """
    s1 = _src("S1", _GROUNDED_TEXT)
    store = _store(s1)
    claims = [_grounded_claim(i, "S1") for i in range(9)]
    claims.append(_unverified_citation_claim(9))

    rep = score_report(claims, store)
    assert rep["scored_claims"] == 10
    assert abs(rep["grounding_score"] - 90.0) < 0.05  # at threshold, not below
    assert rep["gate"] == "NEEDS_WORK", (
        "UNVERIFIED_CITATION must cap gate at NEEDS_WORK even at/above threshold"
    )


# ---------------------------------------------------------------------------
# PASS — all grounded
# ---------------------------------------------------------------------------

def test_all_grounded_pass():
    """3 GROUNDED claims → 100.0 and PASS (no override, score >= threshold)."""
    s1 = _src("S1", _GROUNDED_TEXT)
    store = _store(s1)
    claims = [_grounded_claim(i, "S1") for i in range(3)]

    rep = score_report(claims, store)
    assert rep["grounding_score"] == 100.0
    assert rep["gate"] == "PASS"
    assert rep["scored_claims"] == 3
    assert rep["retained_appendix"] == []


# ---------------------------------------------------------------------------
# FAIL — below 60
# ---------------------------------------------------------------------------

def test_below_60_fails():
    """1 GROUNDED + 2 UNCITED = 33.3 (< 60) → FAIL.

    UNCITED (not UNVERIFIED_CITATION) is used so the gate verdict is driven by
    the score floor, not the hard override — isolating the FAIL branch.
    """
    s1 = _src("S1", _GROUNDED_TEXT)
    store = _store(s1)
    claims = [_grounded_claim(0, "S1"), _uncited_claim(1), _uncited_claim(2)]

    # Verdict integrity.
    assert ground(claims[1], store) == Verdict.UNCITED
    assert ground(claims[2], store) == Verdict.UNCITED

    rep = score_report(claims, store)
    assert abs(rep["grounding_score"] - 33.3) < 0.05
    assert rep["gate"] == "FAIL"
    assert rep["scored_claims"] == 3
    # Both UNCITED violations are retained (never removed from denominator).
    assert {a["index"] for a in rep["retained_appendix"]} == {1, 2}


# ---------------------------------------------------------------------------
# NON_CLAIM exclusion — denominator counts only scored kinds
# ---------------------------------------------------------------------------

def test_non_claim_excluded_from_denominator():
    """A NON_CLAIM header does not enter the denominator.

    1 GROUNDED + 1 UNCITED scored, plus 1 NON_CLAIM header. Denominator = 2,
    numerator = 1 → 50.0 (NOT 33.3 as it would be if the header were counted,
    and NOT 66.7 as if the header counted as grounded). per_claim still lists
    all three claims for transparency.
    """
    s1 = _src("S1", _GROUNDED_TEXT)
    store = _store(s1)
    header = _classified(0, "## Background and methodology")
    assert header.kind == ClaimKind.NON_CLAIM
    claims = [header, _grounded_claim(1, "S1"), _uncited_claim(2)]

    rep = score_report(claims, store)
    assert rep["scored_claims"] == 2
    assert abs(rep["grounding_score"] - 50.0) < 0.05
    assert len(rep["per_claim"]) == 3  # transparency: all claims reported
    # NON_CLAIM is not a scored violation, so it is absent from the appendix.
    assert {a["index"] for a in rep["retained_appendix"]} == {2}


# ---------------------------------------------------------------------------
# Empty denominator edge case (|S| == 0)
# ---------------------------------------------------------------------------

def test_empty_denominator_not_pass():
    """MOAT FIX B (defense in depth): all NON_CLAIM (no scored claims) → gate
    NEEDS_WORK, NOT PASS. A report with zero verifiable claims cannot be certified
    trustworthy. The ``vacuous`` flag lets callers distinguish 'nothing to verify'
    from a genuine low score. Previously this asserted PASS — that assertion
    encoded the moat-integrity hole and is corrected here."""
    h0 = _classified(0, "## Section one")
    h1 = _classified(1, "## Section two")
    assert h0.kind == ClaimKind.NON_CLAIM
    assert h1.kind == ClaimKind.NON_CLAIM

    rep = score_report([h0, h1], {})
    assert rep["scored_claims"] == 0
    assert rep["gate"] == "NEEDS_WORK"
    assert rep["gate"] != "PASS"
    assert rep["vacuous"] is True
    assert rep["retained_appendix"] == []
    assert len(rep["per_claim"]) == 2


def test_empty_claims_list_not_pass():
    """Zero claims at all → vacuous, gate NEEDS_WORK (not PASS), scored_claims == 0."""
    rep = score_report([], {})
    assert rep["scored_claims"] == 0
    assert rep["gate"] == "NEEDS_WORK"
    assert rep["gate"] != "PASS"
    assert rep["vacuous"] is True
    assert rep["per_claim"] == []
    assert rep["retained_appendix"] == []


def test_non_vacuous_report_flag_false():
    """A report with at least one scored claim is NOT vacuous."""
    s1 = _src("S1", _GROUNDED_TEXT)
    store = _store(s1)
    rep = score_report([_grounded_claim(0, "S1")], store)
    assert rep["vacuous"] is False
    assert rep["scored_claims"] == 1


# ---------------------------------------------------------------------------
# HEADLINE REGRESSION — the verbless fabricated draft must NOT report PASS.
# This is the exact moat-integrity hole: 3 verbless fabricated claims citing an
# absent source S9. Before the fix every line classified NON_CLAIM → denominator
# 0 → vacuous PASS. After Fix A each line is a NUMERIC claim citing the missing
# S9 → UNVERIFIED_CITATION → not PASS; Fix B backstops the all-excluded case.
# ---------------------------------------------------------------------------

_VERBLESS_FABRICATED_DRAFT = (
    "A 99% market share for our product [S9]. "
    "Industry-leading uptime of 99.999% [S9]. "
    "The fastest database on the market [S9]."
)


def test_verbless_fabricated_draft_does_not_pass():
    """Full pipeline (decompose → classify → score_report) on a purely verbless
    fabricated draft citing an absent source must NOT certify PASS."""
    claims = [classify(c) for c in decompose(_VERBLESS_FABRICATED_DRAFT)]
    # Empty store: S9 does not exist.
    rep = score_report(claims, {})
    assert rep["gate"] != "PASS", (
        f"fabricated verbless draft was certified PASS — moat breached: {rep}"
    )
    # The lines must be scored (not silently excluded as NON_CLAIM).
    assert rep["scored_claims"] >= 1, (
        f"verbless fabricated claims were excluded from the denominator: {rep}"
    )


# ---------------------------------------------------------------------------
# threshold parameter — NEEDS_WORK when score < threshold (no override)
# ---------------------------------------------------------------------------

def test_threshold_drives_needs_work():
    """2 GROUNDED + 1 UNCITED = 66.7. Default threshold 90 → NEEDS_WORK by score.

    No UNVERIFIED_CITATION present, so the gate is NEEDS_WORK purely because
    60 <= 66.7 < 90 — isolating the threshold branch from the hard override.
    """
    s1 = _src("S1", _GROUNDED_TEXT)
    store = _store(s1)
    claims = [_grounded_claim(0, "S1"), _grounded_claim(1, "S1"), _uncited_claim(2)]

    rep = score_report(claims, store)
    assert abs(rep["grounding_score"] - 66.7) < 0.05
    assert rep["gate"] == "NEEDS_WORK"

    # Lowering the threshold below the score flips the gate to PASS (proves the
    # threshold parameter is genuinely consulted, not a hard-coded 90).
    rep_low = score_report(claims, store, threshold=60.0)
    assert rep_low["gate"] == "PASS"


# ---------------------------------------------------------------------------
# per_claim structure
# ---------------------------------------------------------------------------

def test_per_claim_fields():
    """per_claim entries carry exact field names: index, text, kind, verdict."""
    s1 = _src("S1", _GROUNDED_TEXT)
    store = _store(s1)
    c0 = _grounded_claim(0, "S1")
    rep = score_report([c0], store)
    entry = rep["per_claim"][0]
    assert set(entry.keys()) == {"index", "text", "kind", "verdict"}
    assert entry["index"] == 0
    assert entry["text"] == c0.text
    assert entry["kind"] == c0.kind.value
    assert entry["verdict"] == Verdict.GROUNDED.value
