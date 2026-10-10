"""Round-3 red-team regressions — evasions of the 2026-08-30 fixes.

Round 3 (2026-08-30) ran 37 adversarial drafts against the tree that had just
closed OI-MOAT-03/-05/-07 and deployed lex_tau=0.71. It found 17 wrongful
PASSes collapsing to 5 mechanisms — two of them evasions of that same day's
fixes. Same shape as round 2 finding 14 holes in round 1's fixes: a narrow fix
closes the fixture it was written against and leaves the class open.

Full report: docs/plans/reports/RED-TEAM-R3-2026-08-30.md
Every draft below was OBSERVED gate=PASS before its fix (red evidence in the
2026-08-30 logbook), and asserts the correct behaviour: gate != PASS.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
GROUND_CHECK = str(REPO_ROOT / "scripts" / "ground_check.py")
FIXTURES = Path(__file__).parent / "fixtures"
STORE = str(FIXTURES / "store.jsonl")

# Frozen store: S1 = Redis, 128000 operations per second, "about twelve times
# the throughput of the disk-backed alternative"; S2 = PostgreSQL, 11000 WRITE
# operations per second with full durability guarantees.

_ANCHOR = (
    "Redis sustained approximately 128000 operations per second, which was "
    "about twelve times the throughput of the disk-backed alternative under "
    "the same workload [S1].\n\n"
)


def _gate(tmp_path: Path, draft_text: str) -> dict:
    draft = tmp_path / "draft.md"
    draft.write_text(draft_text, encoding="utf-8")
    env = {**os.environ, "PYTHONPATH": str(REPO_ROOT)}
    result = subprocess.run(
        [sys.executable, GROUND_CHECK, "--draft", str(draft), "--store", STORE, "--json"],
        capture_output=True, text=True, env=env,
    )
    assert result.stdout, f"gate produced no stdout.\nstderr: {result.stderr}"
    return json.loads(result.stdout)


# --- RT3-01: verbless fragment under the content-token floor -----------------

RT3_01_SMUGGLES = [
    pytest.param("PostgreSQL: unrecoverable corruption under load.", id="RT3-01-colon-short"),
    pytest.param("Redis: catastrophic data loss.", id="RT3-01-colon-shorter"),
    pytest.param("PostgreSQL: silently lossy.", id="RT3-01-colon-minimal"),
]


@pytest.mark.parametrize("smuggle", RT3_01_SMUGGLES)
def test_short_verbless_fragment_must_not_escape_denominator(tmp_path: Path, smuggle: str) -> None:
    """OI-MOAT-07's >=6-content-token floor was itself the vulnerability: a
    fabrication just under it still bought a denominator exit. A COUNT cannot
    separate structure from assertion — the attacker picks the count."""
    report = _gate(tmp_path, _ANCHOR + smuggle + "\n")
    assert report["gate"] != "PASS", (
        f"RT3-01: short verbless fabrication rode inside a PASS "
        f"(score={report['grounding_score']}, scored={report['scored_claims']}): {smuggle!r}"
    )


# --- RT3-02: markdown header short-circuits before the floor -----------------

RT3_02_HEADERS = [
    pytest.param("### Redis silently drops writes above ten thousand concurrent clients",
                 id="RT3-02-h3-assertion"),
    pytest.param("# PostgreSQL corrupts data under sustained write load",
                 id="RT3-02-h1-assertion"),
]


@pytest.mark.parametrize("header", RT3_02_HEADERS)
def test_assertion_in_header_must_not_escape_denominator(tmp_path: Path, header: str) -> None:
    """The '#'-header branch returned NON_CLAIM before the verbless rule ran, so
    ANY header without a numeric or citation escaped scoring regardless of the
    assertion it carried."""
    report = _gate(tmp_path, _ANCHOR + header + "\n")
    assert report["gate"] != "PASS", (
        f"RT3-02: header-wrapped fabrication rode inside a PASS "
        f"(score={report['grounding_score']}, scored={report['scored_claims']}): {header!r}"
    )


def test_genuine_structural_header_stays_non_claim(tmp_path: Path) -> None:
    """Error-A boundary: a real section heading must still be excluded, or
    every ordinary document blocks PASS on its own table of contents."""
    report = _gate(tmp_path, "## Results\n\n" + _ANCHOR)
    assert report["gate"] == "PASS", (
        f"a plain heading wrongly entered the denominator: {report['per_claim']}"
    )


# --- RT3-03: T1 residual coverage over the UNION of cited sources ------------

def test_citing_more_sources_must_not_ground_a_false_claim(tmp_path: Path) -> None:
    """THE round-3 headline. OI-MOAT-03's coverage check tested the claim's
    content tokens against the UNION of the cited sources, so adding a citation
    WIDENED the vocabulary that could cover a fabrication.

    The claim below attributes Redis's 128000 ops/sec to PostgreSQL. Cited to
    [S1] alone it correctly FAILs — 'postgresql' is not in S1. Adding [S2]
    (which contributes 'postgresql' and nothing else relevant) made it PASS at
    100.0. Citing MORE evidence made a false claim pass, which inverts the
    entire premise of the tool.
    """
    draft = (
        "PostgreSQL sustained approximately 128000 operations per second "
        "which was about twelve times [S1][S2].\n"
    )
    report = _gate(tmp_path, draft)
    assert report["gate"] != "PASS", (
        f"RT3-03: union-widened coverage grounded a false attribution "
        f"(score={report['grounding_score']})"
    )


def test_single_source_control_still_fails(tmp_path: Path) -> None:
    """Control for RT3-03: the same claim cited to [S1] alone must still fail.
    If this ever passes, the fix moved the wrong way."""
    draft = (
        "PostgreSQL sustained approximately 128000 operations per second "
        "which was about twelve times [S1].\n"
    )
    assert _gate(tmp_path, draft)["gate"] != "PASS"


def test_honest_single_source_quote_still_grounds(tmp_path: Path) -> None:
    """Error-A boundary for RT3-03: a genuine verbatim quotation from ONE cited
    source must still ground, or the fix has broken T1's purpose."""
    report = _gate(tmp_path, _ANCHOR)
    assert report["gate"] == "PASS", (
        f"honest verbatim quote no longer grounds: {report['per_claim']}"
    )


# --- RT3-04: absence blanket-word guard is disabled below 3 queries ----------

RT3_04_ABSENCES = [
    pytest.param("No benchmark throughput figures exist.", id="RT3-04-benchmark-throughput"),
    pytest.param("There are no throughput benchmark results.", id="RT3-04-reordered"),
]


@pytest.mark.parametrize("draft", RT3_04_ABSENCES)
def test_absence_of_the_very_thing_searched_must_not_be_supported(
    tmp_path: Path, draft: str
) -> None:
    """The store IS benchmark throughput figures; the session's queries are
    about exactly that. Certifying 'no benchmark throughput figures exist'
    against it is the absence path asserting the opposite of its own evidence.

    The blanket-word guard that should have caught it was gated on
    `len(distinct) >= 3`, and this session has 2 queries — so the guard
    switched itself off precisely in the small-session case where a generic
    head noun is MOST likely to be non-discriminating.
    """
    report = _gate(tmp_path, draft + "\n")
    assert report["gate"] != "PASS", (
        f"RT3-04: unsubstantiated absence certified (score={report['grounding_score']}): {draft!r}"
    )


# --- RT3-05: quantity reader fails open on a singular/unknown noun -----------

RT3_05_QUANTITY_SWAPS = [
    pytest.param(
        "Redis sustained approximately 128000 node per second, which was about "
        "twelve times the throughput of the disk-backed alternative [S1].",
        id="RT3-05-singular-unknown-noun",
    ),
    pytest.param(
        "PostgreSQL sustained approximately 11000 cache operations per second "
        "with full durability guarantees enabled [S1][S2].",
        id="RT3-05-inserted-qualifier",
    ),
]


@pytest.mark.parametrize("draft", RT3_05_QUANTITY_SWAPS)
def test_quantity_noun_reader_must_not_fail_open(tmp_path: Path, draft: str) -> None:
    """`_numeric_context`'s quantity loop reads ONE candidate token and breaks;
    a singular or unrecognised noun leaves quantity=None, which numeric_ok
    treats as 'asserts no dimension' and imposes no constraint. So inserting a
    qualifier ('cache operations') or using a singular noun ('node') disables
    the dimensional check that OI-MOAT-01/-09 installed."""
    report = _gate(tmp_path, draft + "\n")
    assert report["gate"] != "PASS", (
        f"RT3-05: quantity check failed open (score={report['grounding_score']}): {draft!r}"
    )
