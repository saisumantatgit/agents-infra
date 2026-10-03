"""Round 9 R9P1 — CLOSED by J-25 (2026-10-01). Permanent regression guard.

The finding: ``ground()`` dispatched RELATIONAL and ABSENCE claims BEFORE the
unresolved-citation check, so neither kind ever reached it. A fabricated [S99]
certified PASS 100.0 on both, while ``evidence_basis`` on the same report row
said S99 had never been retrieved.

The fix moves the check ahead of the kind dispatch. These tests were seen to
XPASS(strict) against the pre-fix tree, which is the red-to-green transition
for a tripwired finding.

The sibling shapes below exist on purpose. This project's documented failure is
enumerating the shapes in its own fixtures and mistaking that for the class —
round 3 (token count), round 4 (capitalisation), round 8 (every fixture used
"that the ..."). So the two reproductions are joined by: all-citations-fake,
the numeric kind, a full-width marker that only NFKC folds, and the NULL CASE
(an uncited absence claim, which must still reach check_absence unchanged).
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))

import ground_check as g  # noqa: E402


def _rec(sid, text, fts="verbatim", tool="Read"):
    return {"source_id": sid, "url": None, "file_path": "/tmp/a",
            "fetched_at": "2026-09-13T00:00:00Z", "tool": tool,
            "content_sha256": "a", "text": text, "full_text_source": fts,
            "captured_via": "inline", "query_provenance": "q-" + sid}


def _run(tmp_path, draft, records):
    store = tmp_path / "s.jsonl"
    store.write_text("".join(json.dumps(r) + "\n" for r in records),
                     encoding="utf-8")
    claims = [g.classify(c) for c in g.decompose(draft)]
    return g.score_report(claims, g.load_store(str(store)))


REL = [
    _rec("S2", "Insulin resistance impairs glucose uptake and is a central "
               "mechanism that causes type 2 diabetes to develop."),
    _rec("S3", "Type 2 diabetes develops when insulin resistance progresses "
               "and the pancreas can no longer compensate."),
]

ABS = [
    {**_rec("SA1", "No recall evidence was found in the manufacturer's safety "
                   "bulletin archive for the X200 drone line."),
     "query_provenance": "recall evidence search X200 drone"},
    {**_rec("SA2", "The public recall database returned zero results for X200 "
                   "drone safety evidence."),
     "query_provenance": "regulatory database evidence query X200"},
]


# --- the two original reproductions -----------------------------------------

def test_relational_claim_with_fabricated_citation_is_not_certified(tmp_path):
    """R9P1-01: [S99] beside two REAL sources must not certify."""
    rep = _run(tmp_path,
               "Insulin resistance causes type 2 diabetes [S2][S3][S99].\n", REL)
    assert rep["gate"] != "PASS"


def test_absence_claim_with_fabricated_citation_is_not_certified(tmp_path):
    """R9P1-02: check_absence never inspected claim.citations."""
    rep = _run(tmp_path,
               "[S99] We found no evidence of a safety recall affecting the "
               "X200 drone.\n", ABS)
    assert rep["gate"] != "PASS"


# --- sibling shapes the original fixtures did NOT contain -------------------

def test_relational_claim_with_every_citation_fabricated_is_not_certified(tmp_path):
    """Not just one fake among real ones — the all-fake case."""
    rep = _run(tmp_path,
               "Insulin resistance causes type 2 diabetes [S98][S99].\n", REL)
    assert rep["gate"] != "PASS"


def test_absence_claim_with_fabricated_citation_among_real_ones(tmp_path):
    """The mirror of R9P1-02: a fake marker sitting beside resolvable ones."""
    rep = _run(tmp_path,
               "We found no evidence of a safety recall affecting the X200 "
               "drone [SA1][SA2][S99].\n", ABS)
    assert rep["gate"] != "PASS"


def test_numeric_claim_with_fabricated_citation_is_not_certified(tmp_path):
    """The kind that already reached the check — it must not have regressed."""
    rep = _run(tmp_path, "Redis handles 100K ops per second [S1][S99].\n",
               [_rec("S1", "Redis handles 100K ops per second.")])
    assert rep["gate"] != "PASS"


def test_fullwidth_fabricated_marker_is_not_certified(tmp_path):
    """NFKC folds the full-width brackets; the marker still names nothing."""
    rep = _run(tmp_path,
               "Insulin resistance causes type 2 diabetes [S2][S3]［S99］.\n",
               REL)
    assert rep["gate"] != "PASS"


def test_unresolved_citation_verdict_is_reported_per_claim(tmp_path):
    """Refusing is not enough — the report must SAY why, or D-35 lies."""
    rep = _run(tmp_path,
               "Insulin resistance causes type 2 diabetes [S2][S3][S99].\n", REL)
    verdicts = [c["verdict"] for c in rep["per_claim"]]
    assert "UNVERIFIED_CITATION" in verdicts


# --- controls: the fix must not have bought its refusals too widely ---------

def test_relational_control_without_fabrication_is_still_CORROBORATED(tmp_path):
    """Keeps every tripwire above honest: the real two-source claim is still
    corroborated.

    Under ADR-007 this control moved from the verdict to the diagnostic: corroboration is still measured (relation_diagnostic), it just no longer votes on the gate, so this is not a weakening.
    """
    rep = _run(tmp_path,
               "Insulin resistance causes type 2 diabetes [S2][S3].\n", REL)
    assert rep["per_claim"][0]["relation_diagnostic"] == g.RELATION_CORROBORATED
    assert rep["per_claim"][0]["verdict"] == "UNVERIFIED_RELATION"
    assert rep["gate"] == "FAIL"


@pytest.mark.xfail(strict=True, reason=(
    "J-31 OPEN, found 2026-10-01 while writing this control and verified "
    "PRE-EXISTING on the pre-J-25 tree (so NOT a J-25 regression). The SAME "
    "absence claim reads ABSENCE_SUPPORTED/PASS uncited and "
    "UNVERIFIED_ABSENCE/FAIL when it cites the two real sources that support "
    "it. Error-A, fail-closed, no moat breach — but the gate penalises the "
    "one behaviour the product asks authors for. Registered for round 10."))
def test_absence_control_with_real_citations_still_passes(tmp_path):
    """THIS TRIPWIRE DOES NOT TEST WHAT IT IS NAMED FOR. Kept, annotated, and
    superseded by the test below — not deleted, because its xfail is the
    historical record of how J-31 was first reported.

    `_CITATION_RE` is `\[(?:S\d+[a-zA-Z]*|source:[^\]]+)\]` — `S` then DIGITS.
    So `[SA1]` and `[SA2]` are **not citations at all**, and this store names its
    sources `SA1`/`SA2`, ids that can never be cited. "with real citations" was
    never true of this fixture.

    Two consequences, both found 2026-10-03:
      - the markers are left in the claim text, and `SA1`/`SA2` tokenize such
        that their DIGITS become numeric tokens — `('200', '1', '2')` here;
      - so since the J-62+J-71 figure check reached the ABSENCE branch, this
        claim is refused as `UNVERIFIED_NUMBER` rather than
        `UNVERIFIED_ABSENCE`. Measured: `check_absence` alone still returns
        UNVERIFIED_ABSENCE, so the figure check MASKED the original mechanism.

    J-31 itself is REAL — see the superseding test. This fixture just could not
    demonstrate it."""
    rep = _run(tmp_path,
               "We found no evidence of a safety recall affecting the X200 "
               "drone [SA1][SA2].\n", ABS)
    assert rep["gate"] == "PASS"


@pytest.mark.xfail(strict=True, reason=(
    "J-31 OPEN and CONFIRMED REAL 2026-10-03 with CITABLE source ids. The same "
    "absence claim is ABSENCE_SUPPORTED uncited and UNVERIFIED_ABSENCE when it "
    "cites the two sources that support it — the gate penalises the one "
    "behaviour the product asks authors for. Error-A, fail-closed, no moat "
    "breach."))
def test_J31_the_same_absence_claim_must_not_FAIL_merely_for_citing_its_sources(
        tmp_path):
    """THE HONEST INSTRUMENT for J-31. Source ids are S1/S2, so the markers in
    the draft are genuinely resolved as citations — which the fixture above
    could not do.

    Measured both ways on this store (2026-10-03):
        uncited          → ABSENCE_SUPPORTED
        cited [S1][S2]   → UNVERIFIED_ABSENCE
    and `numeric_tokens` is `('200',)` in BOTH, with `200` present in S2's text,
    so the figure check does not fire and cannot be what refuses this. That is
    the point of building a separate fixture: it isolates J-31 from the two
    artefacts that were confounding the old one.

    Asserts the VERDICT, not the gate (J-80): a `gate == "PASS"` assertion on a
    control is weak in the OPPOSITE direction — it keeps passing if the gate
    begins certifying for a wrong reason."""
    citable = [dict(row, source_id=row["source_id"].replace("SA", "S"))
               for row in ABS]
    rep = _run(tmp_path,
               "We found no evidence of a safety recall affecting the X200 "
               "drone [S1][S2].\n", citable)
    assert rep["per_claim"][0]["verdict"] == "ABSENCE_SUPPORTED", (
        f"citing its own supporting sources changed the verdict to "
        f"{rep['per_claim'][0]['verdict']}")
    assert rep["gate"] == "PASS"


def test_uncited_absence_claim_still_reaches_check_absence(tmp_path):
    """THE NULL CASE. An empty citation list makes any() False, so an absence
    claim that cites nothing must behave exactly as it did before J-25."""
    rep = _run(tmp_path,
               "We found no evidence of a safety recall affecting the X200 "
               "drone.\n", ABS)
    assert rep["gate"] == "PASS"
