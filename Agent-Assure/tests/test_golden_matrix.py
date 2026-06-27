"""Task 11: Parametrized golden verdict matrix + determinism assertion.

Each parametrized row locks one verdict path end-to-end:
  claim text → decompose → classify → ground(claim, store) == expected_verdict

Fixture discipline (per regression-test rule in global CLAUDE.md INS-005):
  - Each row GENUINELY creates the conditions for its verdict path.
  - No tautologies: the assertion tests a property, not f(x)==f(x).
  - The UNGROUNDABLE / UNVERIFIED_RELATION / UNVERIFIED_ABSENCE rows include
    inline comments proving WHY the verdict is reached.

Tier proofs (rows that split T1 vs T2):
  - GROUNDED/T1: claim has ≥8 content tokens verbatim in the source.
  - GROUNDED/T2: claim has only 6 content tokens after citation strip → T1
    cannot fire (min_quote_len=8); source is a paraphrase with high lexical-F1
    (measured: 0.714 at tau=0.65) → T2 fires and returns True.
"""

from __future__ import annotations

import pytest

from scripts.ground_check import (
    Claim,
    ClaimKind,
    RetrievedSource,
    Verdict,
    classify,
    decompose,
    ground,
    t1_verbatim,
    t2_lexical,
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
    """Build a minimal RetrievedSource for fixture use."""
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
    """Build an evidence store dict keyed by source_id."""
    return {s.source_id: s for s in sources}


def _classified(text: str) -> Claim:
    """Run a raw claim string through classify() with a FACTUAL seed kind."""
    return classify(Claim(index=0, text=text, kind=ClaimKind.FACTUAL,
                          citations=(), numeric_tokens=()))


# ---------------------------------------------------------------------------
# Golden verdict matrix — parametrized rows
# ---------------------------------------------------------------------------
#
# Row IDs (pytest -k filter targets):
#   grounded_t1, grounded_t2, unverified_citation, unverified_number,
#   unverified_absence, ungroundable_haiku, unverified_relation
#
# Each row is a tuple: (row_id, claim_text, store_dict, expected_verdict)
# The store_dict is evaluated lazily so that helpers above are already defined.

MATRIX = [
    # ------------------------------------------------------------------
    # ROW 1: GROUNDED via T1
    #
    # Claim content tokens after citation strip (8):
    #   redis handles 100k operations per second on commodity hardware
    # Source contains all 8 as a contiguous verbatim span.
    # Measured: T1 returns True; T2 is never reached.
    # ------------------------------------------------------------------
    pytest.param(
        "grounded_t1",
        "Redis handles 100K operations per second on commodity hardware [S1].",
        lambda: _store(
            _src(
                "S1",
                "benchmarks show Redis handles 100K operations per second"
                " on commodity hardware",
            )
        ),
        Verdict.GROUNDED,
        id="grounded_t1",
    ),

    # ------------------------------------------------------------------
    # ROW 2: GROUNDED via T2 (T1 cannot fire)
    #
    # Claim content tokens after citation strip (6):
    #   postgresql query optimization achieves high throughput
    # 6 < min_quote_len=8 → T1 returns False (short-circuit at token count).
    #
    # Source is a paraphrase (key verb "achieves" → "delivers"):
    #   "PostgreSQL query optimization delivers high throughput in
    #    production environments."
    # Content-word F1 measured = 0.714 ≥ tau=0.65 → T2 returns True.
    # ------------------------------------------------------------------
    pytest.param(
        "grounded_t2",
        "PostgreSQL query optimization achieves high throughput [S1].",
        lambda: _store(
            _src(
                "S1",
                "PostgreSQL query optimization delivers high throughput"
                " in production environments.",
            )
        ),
        Verdict.GROUNDED,
        id="grounded_t2",
    ),

    # ------------------------------------------------------------------
    # ROW 3: UNVERIFIED_CITATION
    #
    # Claim cites [S9]; store is empty → resolve("[S9]", {}) returns None
    # → ground branch 5 fires → UNVERIFIED_CITATION.
    # ------------------------------------------------------------------
    pytest.param(
        "unverified_citation",
        "Redis is an in-memory data store [S9].",
        lambda: {},        # empty store — S9 absent
        Verdict.UNVERIFIED_CITATION,
        id="unverified_citation",
    ),

    # ------------------------------------------------------------------
    # ROW 4: UNVERIFIED_NUMBER
    #
    # Claim is NUMERIC: "improved by 40%". Source says "improved by 25%".
    # numeric_ok() checks (40.0, "percent") against all source pairs;
    # only (25.0, "percent") is found → numeric_ok returns False
    # → ground branch 8 fires → UNVERIFIED_NUMBER.
    # ------------------------------------------------------------------
    pytest.param(
        "unverified_number",
        "Cache hit rate improved by 40% after tuning [S1].",
        lambda: _store(
            _src(
                "S1",
                "After careful tuning the cache hit rate improved by 25% overall.",
            )
        ),
        Verdict.UNVERIFIED_NUMBER,
        id="unverified_number",
    ),

    # ------------------------------------------------------------------
    # ROW 5: UNVERIFIED_ABSENCE
    #
    # Claim is ABSENCE kind: "There are no known side effects…".
    # Subject head noun extracted: "side" (first content word after "no known").
    # Store has ONE source whose query_provenance does NOT mention "side".
    # check_absence needs ≥2 distinct queries containing "side" → finds 0 → UNVERIFIED_ABSENCE.
    # ------------------------------------------------------------------
    pytest.param(
        "unverified_absence",
        "There are no known side effects of this treatment.",
        lambda: _store(
            _src(
                "S1",
                "Treatment overview: this therapy has been used since 2010.",
                query_provenance="treatment overview",   # does not mention "side"
            )
        ),
        Verdict.UNVERIFIED_ABSENCE,
        id="unverified_absence",
    ),

    # ------------------------------------------------------------------
    # ROW 6: UNGROUNDABLE — haiku_summary-only cited source
    #
    # Source text is identical to the claim (so T1/T2 WOULD hit if allowed to run),
    # but full_text_source="haiku_summary" → NOT counted as verbatim.
    # ground() branch 7: verbatim list is empty → UNGROUNDABLE; tiers never called.
    # ------------------------------------------------------------------
    pytest.param(
        "ungroundable_haiku",
        "Redis handles 100K operations per second on commodity hardware [S1].",
        lambda: _store(
            _src(
                "S1",
                # Identical wording so tiers would pass IF they were (wrongly) invoked.
                "Redis handles 100K operations per second on commodity hardware.",
                full_text_source="haiku_summary",   # NOT verbatim → tiers must not run
            )
        ),
        Verdict.UNGROUNDABLE,
        id="ungroundable_haiku",
    ),

    # ------------------------------------------------------------------
    # ROW 7: UNVERIFIED_RELATION — single verbatim source
    #
    # Claim is RELATIONAL (contains "causes"). ground_relational requires
    # ≥2 DISTINCT verbatim sources. Only S1 is in the store →
    # len(verbatim_sources) < 2 → UNVERIFIED_RELATION.
    # ------------------------------------------------------------------
    pytest.param(
        "unverified_relation",
        "Insulin resistance causes type 2 diabetes [S1].",
        lambda: _store(
            _src(
                "S1",
                "Insulin resistance is a metabolic condition affecting cells.",
            )
        ),
        Verdict.UNVERIFIED_RELATION,
        id="unverified_relation",
    ),
]


@pytest.mark.parametrize("row_id,claim_text,make_store,expected_verdict", MATRIX)
def test_golden_verdict_matrix(
    row_id: str,
    claim_text: str,
    make_store,
    expected_verdict: Verdict,
) -> None:
    """Assert the exact verdict for every path in the golden matrix.

    Pipeline: claim_text → classify → ground(claim, store) → assert verdict.
    Each row's fixture is constructed to reach `expected_verdict` for the
    mechanically correct reason (comments above each param entry document the
    causal path).
    """
    store = make_store()
    claim = _classified(claim_text)
    actual = ground(claim, store)
    assert actual == expected_verdict, (
        f"[{row_id}] Expected {expected_verdict.value}, got {actual.value}.\n"
        f"  claim: {claim_text!r}\n"
        f"  kind: {claim.kind.value}\n"
        f"  citations: {claim.citations}\n"
        f"  numeric_tokens: {claim.numeric_tokens}\n"
        f"  store keys: {list(store.keys())}"
    )


# ---------------------------------------------------------------------------
# Tier proofs: explicit T1/T2 split for the GROUNDED rows
# ---------------------------------------------------------------------------

def test_grounded_t1_tier_split() -> None:
    """Row grounded_t1: T1 returns True for the fixture (tier split proof)."""
    claim = _classified(
        "Redis handles 100K operations per second on commodity hardware [S1]."
    )
    source = _src(
        "S1",
        "benchmarks show Redis handles 100K operations per second on commodity hardware",
    )
    assert t1_verbatim(claim, [source]), (
        "T1 must hit: 8-token verbatim span 'redis handles 100k operations per "
        "second on commodity hardware' is present in the source."
    )


def test_grounded_t2_tier_split() -> None:
    """Row grounded_t2: T1 returns False (claim has 6 tokens < min=8); T2 returns True."""
    claim = _classified("PostgreSQL query optimization achieves high throughput [S1].")
    source = _src(
        "S1",
        "PostgreSQL query optimization delivers high throughput in production environments.",
    )
    # T1 must miss — 6 content tokens after citation strip < min_quote_len=8
    assert not t1_verbatim(claim, [source]), (
        "T1 must miss: claim has only 6 content tokens after citation strip,"
        " which is below min_quote_len=8."
    )
    # T2 must hit — lexical-F1 measured at 0.714 ≥ tau=0.65
    assert t2_lexical(claim, [source]), (
        "T2 must hit: content-word F1 between claim and source is 0.714 ≥ tau=0.65."
    )


# ---------------------------------------------------------------------------
# Determinism: decompose on a fixed draft returns an identical claim set twice
# ---------------------------------------------------------------------------

_DETERMINISM_DRAFT = (
    "Agent-Assure validates every claim before publication. "
    "It extracts citations, classifies each sentence, and runs the grounding tiers. "
    "No LLM calls occur during grounding."
)


def test_decompose_determinism() -> None:
    """decompose on a fixed draft produces an identical claim set across two calls.

    Audit-artifact property: the decomposition must be deterministic so that
    any two grounding runs on the same draft produce the same claim list.
    Verified by asserting structural equality (index, text, kind, citations,
    numeric_tokens) across both calls.
    """
    first = decompose(_DETERMINISM_DRAFT)
    second = decompose(_DETERMINISM_DRAFT)

    assert len(first) == len(second), (
        f"Claim count differs across calls: {len(first)} vs {len(second)}"
    )
    for i, (a, b) in enumerate(zip(first, second)):
        assert a.index == b.index, (
            f"Claim {i}: index differs ({a.index} vs {b.index})"
        )
        assert a.text == b.text, (
            f"Claim {i}: text differs:\n  A: {a.text!r}\n  B: {b.text!r}"
        )
        assert a.kind == b.kind, (
            f"Claim {i}: kind differs ({a.kind} vs {b.kind})"
        )
        assert a.citations == b.citations, (
            f"Claim {i}: citations differ ({a.citations} vs {b.citations})"
        )
        assert a.numeric_tokens == b.numeric_tokens, (
            f"Claim {i}: numeric_tokens differ ({a.numeric_tokens} vs {b.numeric_tokens})"
        )


def test_decompose_determinism_empty_draft() -> None:
    """decompose on an empty draft returns [] on both calls (edge-case determinism)."""
    assert decompose("") == decompose("")
    assert decompose("   ") == decompose("   ")
