"""J-33 OPEN — an UNRECOGNISED citation marker is worse than an unresolved one.

Found by the solo gate on J-25 (SOLO-GATE-J25-2026-10-01.md) and reproduced
independently by the orchestrator before being recorded.

J-25 made an UNRESOLVED citation fail closed. It did nothing about an
UNRECOGNISED one, and the difference is the whole finding:

    _CITATION_RE = \\[(?:S\\d+[a-zA-Z]*|source:[^\\]]+)\\]

is case-sensitive and narrow, so a marker it does not match does not become an
unresolved citation — it becomes NO citation. `claim.citations` is empty of the
fake, J-25's `any(resolve(...) is None ...)` has nothing to object to, and
RELATIONAL and ABSENCE claims certify with zero citations BY DESIGN.

Net effect: show the reader a citation the parser cannot see, and the claim
certifies against unrelated store contents at PASS 100.0.

One Shift keystroke separates `[S99]` (FAIL, UNVERIFIED_CITATION) from `[s99]`
(PASS). That is round 4's lesson — never key a moat rule on a surface property
the author controls — for the THIRD time in this project.

POSITION IS ALSO LOAD-BEARING, and it caught me out: with the fake marker
trailing the sentence, its leftover text breaks `extract_arguments` and the
claim is refused by accident. With the marker LEADING, it certifies. My first
reproduction used the trailing position and I wrongly reported the RELATIONAL
half as not reproducing.

Fixing this is NOT simply widening the regex: a widened matcher also catches
`[sic]`, `[1]`, `[see Appendix A]`, each of which would become an unresolvable
citation and a refusal. That is Error-A on honest prose, and it is unmeasured
by the n=52 corpus, which contains none of these shapes. Hence OPEN, with a
recommendation recorded in docs/jobs/REGISTER.md rather than a patch at 03:30.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))

import ground_check as g  # noqa: E402


def _rec(sid, text, qp):
    return {"source_id": sid, "url": None, "file_path": "/tmp/a",
            "fetched_at": "2026-09-13T00:00:00Z", "tool": "Read",
            "content_sha256": "a" * 64, "text": text,
            "full_text_source": "verbatim", "captured_via": "inline",
            "query_provenance": qp}


REL = [
    _rec("S2", "Insulin resistance impairs glucose uptake and is a central "
               "mechanism that causes type 2 diabetes to develop.", "q-S2"),
    _rec("S3", "Type 2 diabetes develops when insulin resistance progresses "
               "and the pancreas can no longer compensate.", "q-S3"),
]

ABS = [
    _rec("SA1", "No recall evidence was found in the manufacturer's safety "
                "bulletin archive for the X200 drone line.",
         "recall evidence search X200 drone"),
    _rec("SA2", "The public recall database returned zero results for X200 "
                "drone safety evidence.",
         "regulatory database evidence query X200"),
]


def _run(tmp_path, draft, records):
    p = tmp_path / "s.jsonl"
    p.write_text("".join(json.dumps(r) + "\n" for r in records), encoding="utf-8")
    return g.score_report([g.classify(c) for c in g.decompose(draft)],
                          g.load_store(str(p)))


# Spellings a human reader treats as a citation and _CITATION_RE does not match.
# "[S99]" is deliberately ABSENT: it is the one spelling J-25 DOES catch, and it
# is the control below. The set deliberately spans FOUR different mechanisms —
# case, internal whitespace, trailing punctuation, a non-ASCII homoglyph — so
# that a fix addressing only one of them cannot green this file.
# VERIFIED to evade, in the leading position, on this tree. The solo gate
# reported 13 of 18 spellings evading; only these FOUR reproduced for me on the
# relational path, so four is what is recorded. The gate's wider number is not
# disputed for other configurations - it is simply not what I measured, and the
# register carries the count I could reproduce rather than the one I was handed.
UNRECOGNISED = [
    "[s99]",
    "[ S99]",
    "[Sxx]",
    "[\u040599]",
]

# Markers a reader ALSO reads as citations, which _CITATION_RE likewise fails to
# match, but which are refused anyway - by ACCIDENT, because their leftover text
# breaks extract_arguments, exactly like the trailing-position case below.
# Pinned as controls, not counted as coverage: improve argument extraction and
# each of these becomes a new Error-B.
REFUSED_BY_ACCIDENT = [
    "[S99.]",
    "[S-99]",
    "[S99, S100]",
    "[Source:acme-report]",
]


@pytest.mark.parametrize("marker", REFUSED_BY_ACCIDENT)
def test_unparsed_marker_refused_only_because_its_text_breaks_extraction(
    tmp_path, marker
):
    rep = _run(tmp_path,
               f"{marker} Insulin resistance causes type 2 diabetes [S2][S3].\n",
               REL)
    assert rep["gate"] != "PASS"


@pytest.mark.parametrize("marker", UNRECOGNISED)
@pytest.mark.xfail(strict=True, reason=(
    "J-33 OPEN: a marker _CITATION_RE cannot parse is not an unresolved "
    "citation but NO citation, so a RELATIONAL claim certifies GROUNDED at "
    "PASS 100.0 while the reader sees a source that was never retrieved."))
def test_relational_claim_with_unrecognised_marker_is_not_certified(tmp_path, marker):
    rep = _run(tmp_path,
               f"{marker} Insulin resistance causes type 2 diabetes [S2][S3].\n",
               REL)
    assert rep["gate"] != "PASS"


@pytest.mark.parametrize("marker", ["[s99]", "[Ѕ99]"])
@pytest.mark.xfail(strict=True, reason=(
    "J-33 OPEN: same gap on the absence path — ABSENCE_SUPPORTED at PASS "
    "100.0 with a visible citation the gate never checked."))
def test_absence_claim_with_unrecognised_marker_is_not_certified(tmp_path, marker):
    rep = _run(tmp_path,
               f"{marker} We found no evidence of a safety recall affecting "
               f"the X200 drone.\n", ABS)
    assert rep["gate"] != "PASS"


# --- controls: these keep the tripwires above honest ------------------------

def test_the_one_recognised_spelling_is_refused(tmp_path):
    """[S99] — what J-25 DOES close. One Shift keystroke from the xfails above."""
    rep = _run(tmp_path,
               "[S99] Insulin resistance causes type 2 diabetes [S2][S3].\n", REL)
    assert rep["gate"] != "PASS"


def test_trailing_position_is_refused_by_accident_not_by_design(tmp_path):
    """Documents the ACCIDENTAL protection so nobody mistakes it for a fix: the
    unparsed marker's leftover text breaks extract_arguments. Remove that
    accident (e.g. by improving argument extraction) and this becomes a third
    Error-B, so it is pinned here deliberately."""
    rep = _run(tmp_path,
               "Insulin resistance causes type 2 diabetes [S2][S3][s99].\n", REL)
    assert rep["gate"] != "PASS"


def test_honest_relational_claim_still_passes(tmp_path):
    rep = _run(tmp_path,
               "Insulin resistance causes type 2 diabetes [S2][S3].\n", REL)
    assert rep["gate"] == "PASS"
