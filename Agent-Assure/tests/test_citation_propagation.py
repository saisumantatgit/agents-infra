"""OI-DEC-01 — a sentence-final citation must reach every clause it covers.

    decompose("Redis is fast and PostgreSQL is durable [S1].")
      -> "Redis is fast"               citations=()     -> UNCITED
      -> "PostgreSQL is durable [S1]." citations=([S1],)

The author cited the sentence. The conjunction splitter detached the marker
from the left clause, so a correctly-cited claim read UNCITED and (post-ADR-005)
blocked PASS. Fail-safe, but it penalises correct authorship — and a gate that
flags a compound sentence teaches users to write around the gate.

WHY THIS ONE WAS ESCALATED
--------------------------
This is the first PASS-ENABLING change in the 2026-08-30 cohort; every other
fix was fail-closed. Ratified by Sai on 2026-09-02 with a red-team gate
attached (the adversarial half is at the bottom of this file).

WHAT PROPAGATION DOES AND DOES NOT BUY
--------------------------------------
It converts UNCITED into "now run the normal tiers against the cited source".
A clause reaches GROUNDED only by actually grounding. Nothing is waved through:
the PASS-enabling path is exactly as wide as the tiers are correct, and no
wider. That is the property the adversarial tests below pin down.
"""

from __future__ import annotations

import pytest

from scripts.ground_check import decompose, classify


def _claims(draft: str):
    return [classify(c) for c in decompose(draft)]


# --- The false alarm itself --------------------------------------------------

def test_sentence_final_citation_reaches_the_left_clause() -> None:
    """The reported OI-DEC-01 reproduction."""
    claims = _claims("Redis is fast and PostgreSQL is durable [S1].")
    assert len(claims) == 2, [c.text for c in claims]
    assert claims[0].citations == ("[S1]",), (
        f"left clause lost the sentence's citation: {claims[0].text!r} "
        f"-> {claims[0].citations!r}"
    )
    assert claims[1].citations == ("[S1]",)


def test_multiple_trailing_citations_all_propagate() -> None:
    claims = _claims("Redis is fast and PostgreSQL is durable [S1][S2].")
    assert len(claims) == 2
    assert claims[0].citations == ("[S1]", "[S2]")


def test_semicolon_split_propagates_too() -> None:
    claims = _claims("Redis is fast; PostgreSQL is durable [S1].")
    assert len(claims) == 2
    assert claims[0].citations == ("[S1]",)


# --- The adversarial half: propagation must not INVENT support ---------------

def test_clause_with_its_own_citation_is_not_overwritten() -> None:
    """A clause that cited its own source keeps it — propagation only fills a
    GAP. Overwriting would silently re-point a claim at a source the author
    never cited for it, which is the fabrication the gate exists to catch."""
    claims = _claims("Redis is fast [S2] and PostgreSQL is durable [S1].")
    assert len(claims) == 2
    assert claims[0].citations == ("[S2]",), (
        f"propagation overwrote an explicit citation: {claims[0].citations!r}"
    )
    assert claims[1].citations == ("[S1]",)


def test_uncited_compound_sentence_stays_uncited() -> None:
    """No citation anywhere means no citation anywhere. Propagation must not
    manufacture one."""
    claims = _claims("Redis is fast and PostgreSQL is durable.")
    assert len(claims) == 2
    assert all(c.citations == () for c in claims), [c.citations for c in claims]


def test_mid_sentence_citation_does_not_propagate_backwards() -> None:
    """Only a SENTENCE-FINAL marker covers the whole sentence. A marker sitting
    mid-sentence belongs to its own clause, and treating it as sentence-scoped
    would attach a source to text the author placed it before."""
    claims = _claims("Redis is fast [S1] and PostgreSQL is durable.")
    assert len(claims) == 2
    assert claims[0].citations == ("[S1]",)
    assert claims[1].citations == (), (
        f"a mid-sentence citation leaked forward: {claims[1].citations!r}"
    )


# --- The semicolon path (syntok treats "; " as a sentence boundary) ----------

def test_citation_does_not_cross_a_full_stop() -> None:
    """The boundary case that makes the semicolon rule safe.

    A terminated sentence is not a clause. Propagating a citation backwards
    across "." would attach a source to a sentence the author never cited —
    exactly the fabrication the gate exists to catch.
    """
    claims = _claims("Redis is fast. PostgreSQL is durable [S1].")
    assert len(claims) == 2
    assert claims[0].citations == (), (
        f"citation crossed a full stop: {claims[0].citations!r}"
    )
    assert claims[1].citations == ("[S1]",)


def test_citation_does_not_travel_back_two_sentences() -> None:
    """Only the IMMEDIATELY following segment is consulted."""
    claims = _claims("Redis is fast; it is in memory. PostgreSQL is durable [S1].")
    texts = [c.text for c in claims]
    assert claims[0].citations == (), f"{texts} -> {claims[0].citations!r}"
