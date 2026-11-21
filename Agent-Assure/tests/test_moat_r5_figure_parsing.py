"""R5 — figure parsing (red team R46, lane C, Root B: families N7-N10).

Each attack certified GROUNDED / PASS 100.0 on main 5e47ebf because the figure
reader took a FRAGMENT of the source's written figure, or its float value, as
the figure:

  N7   "two hundred pilots" -> "two pilots"   (spelled number read token-wise)
  N8   "1 200 pilots"       -> "200 pilots"   (space group read as two numbers)
  N9   "40-50 pilots"       -> "50 pilots"    (range endpoint stated as the value)
  N10  "03/04/2023"         -> "04/03/2023"   (date components in any order)
  N10  "2.10"               -> "2.1"          (version compared as a float)

The fix (fail-closed only): a claim figure must match the WHOLE source figure.
Every attack must now be refused AS A FIGURE PROBLEM (UNVERIFIED_NUMBER); any
other refusal would mean something else caught the draft and the figure reader
is still blind.

Honest twins: the same figure written the same way still grounds; a claim that
states a bound ("up to 50", "at least 40") still grounds against a range.

Decision pinned here, "1 200" vs "1,200" vs "1200": a space-grouped figure
matches ONLY a space-grouped figure. On main "1,200" and "1200" were already
refused against "1 200" (the source read as 1 and 200); grounding them by value
now would be a PASS-enabling change (CLAUDE.md Escalation #1), so the refusal is
kept and pinned.

Run through the real CLI, as a user would. The long opening clause matches the
v3 corpus shape: T1 anchors on the shared words, so only the figure differs.
"""

from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

from scripts.ground_check import Claim, ClaimKind, RetrievedSource, classify, numeric_ok

REPO_ROOT = Path(__file__).parent.parent
GROUND_CHECK = str(REPO_ROOT / "scripts" / "ground_check.py")

PREFIX = "The Harbor Board, following a detailed review of the annual records by staff, "


def _verdict(tmp_path: Path, source_text: str, claim_text: str) -> tuple[int, str]:
    rec = {
        "source_id": "S1",
        "url": "https://example.com/s1",
        "file_path": None,
        "fetched_at": "2026-11-21T00:00:00Z",
        "tool": "mcp__exa__web_fetch_exa",
        "content_sha256": hashlib.sha256(source_text.encode("utf-8")).hexdigest(),
        "text": source_text,
        "full_text_source": "verbatim",
        "captured_via": "inline",
        "query_provenance": "R5 figure-parsing control",
    }
    store = tmp_path / "store.jsonl"
    store.write_text(json.dumps(rec, ensure_ascii=False) + "\n", encoding="utf-8")
    draft = tmp_path / "draft.md"
    draft.write_text(f"{claim_text} [S1].\n", encoding="utf-8")
    env = {**os.environ, "PYTHONPATH": str(REPO_ROOT)}
    out = subprocess.run(
        [sys.executable, GROUND_CHECK, "--draft", str(draft), "--store", str(store), "--json"],
        capture_output=True, text=True, env=env,
    )
    assert out.stdout, f"gate produced no stdout.\nstderr: {out.stderr}"
    scored = [c for c in json.loads(out.stdout)["per_claim"] if c["kind"] != "NON_CLAIM"]
    assert len(scored) == 1, scored
    return out.returncode, scored[0]["verdict"]


def _pair(src_body: str, claim_body: str) -> tuple[str, str]:
    # The source carries an extra sentence so it is never byte-identical to the
    # draft (J-83 would then refuse it as a self-citation, masking the check).
    return (PREFIX + src_body + ". The figures are unaudited.", PREFIX + claim_body)


TRAINING = "pilots in the annual training program"

ATTACKS = [
    # N7 — spelled numbers are one figure, the whole run.
    pytest.param(*_pair(f"enrolled two hundred {TRAINING}", f"enrolled two {TRAINING}"),
                 id="N7-two-of-two-hundred"),
    pytest.param(*_pair(f"enrolled two hundred {TRAINING}", f"enrolled hundred {TRAINING}"),
                 id="N7-hundred-of-two-hundred"),
    pytest.param(*_pair(f"enrolled two hundred and fifty {TRAINING}", f"enrolled two hundred {TRAINING}"),
                 id="N7-compound-with-and"),
    pytest.param(*_pair(f"enrolled forty to fifty {TRAINING}", f"enrolled fifty {TRAINING}"),
                 id="N7-spelled-range-endpoint"),
    # N8 — a space-grouped number is one figure.
    pytest.param(*_pair(f"enrolled 1 200 {TRAINING}", f"enrolled 200 {TRAINING}"),
                 id="N8-space-group"),
    pytest.param(*_pair(f"enrolled 1 200 {TRAINING}", f"enrolled 200 {TRAINING}"),
                 id="N8-nbsp-group"),
    pytest.param(*_pair(f"enrolled 12 450 300 {TRAINING}", f"enrolled 450 300 {TRAINING}"),
                 id="N8-two-groups"),
    # N9 — a range endpoint is not the value.
    pytest.param(*_pair(f"enrolled 40-50 {TRAINING}", f"enrolled 50 {TRAINING}"),
                 id="N9-hyphen-high-end"),
    pytest.param(*_pair(f"enrolled 40-50 {TRAINING}", f"enrolled 40 {TRAINING}"),
                 id="N9-hyphen-low-end"),
    pytest.param(*_pair(f"enrolled 40–50 {TRAINING}", f"enrolled 50 {TRAINING}"),
                 id="N9-en-dash"),
    pytest.param(*_pair(f"enrolled 40 to 50 {TRAINING}", f"enrolled 50 {TRAINING}"),
                 id="N9-to"),
    pytest.param(*_pair(f"enrolled between 40 and 50 {TRAINING}", f"enrolled 50 {TRAINING}"),
                 id="N9-between-and"),
    pytest.param(*_pair(f"enrolled 40-50 {TRAINING}", f"enrolled up to 40 {TRAINING}"),
                 id="N9-upper-bound-on-low-end"),
    pytest.param(*_pair(f"enrolled 40-50 {TRAINING}", f"enrolled at least 50 {TRAINING}"),
                 id="N9-lower-bound-on-high-end"),
    # N10 — dates and versions are ordered strings, never floats.
    pytest.param(*_pair("published the annual review on 03/04/2023", "published the annual review on 04/03/2023"),
                 id="N10-date-slash"),
    pytest.param(*_pair("published the annual review on 2023-03-04", "published the annual review on 2023-04-03"),
                 id="N10-date-iso"),
    pytest.param(*_pair("published the annual review on 03/04/2023", "published the annual review in 2023 on 4"),
                 id="N10-date-component-as-figure"),
    pytest.param(*_pair("published version 2.10 during the annual review", "published version 2.1 during the annual review"),
                 id="N10-version"),
    # The version shape above is already refused on main, but by T1 (the token
    # "1" is absent from the source), not as a figure. With every claim token
    # present in the source, main certified it: "2.1" == float("2.10").
    pytest.param(*_pair("published version 2.10 during the annual review, 1 week late",
                        "published version 2.1 during the annual review"),
                 id="N10-version-tokens-present"),
    # Adversary D-146, BLOCKER 1 — on b4d3905 the date branch exact-matched the
    # date string and skipped main's per-component qualifier/unit checks, so a
    # sign, comparator, percent or per-mille on a date certified PASS. The date
    # check must be ADDITIONAL to those checks, never a replacement.
    pytest.param(*_pair("adopted the 3/2/1 bonus schedule for pilots", "adopted the 3/2/1% bonus schedule for pilots"),
                 id="B1-date-trailing-percent"),
    pytest.param(*_pair("adopted the 3-2-1 bonus schedule for pilots", "adopted the 3-2-1% bonus schedule for pilots"),
                 id="B1-dash-date-trailing-percent"),
    pytest.param(*_pair("adopted the 10/20/30 rule for pilots", "adopted the 10/20/30 million rule for pilots"),
                 id="B1-date-magnitude"),
    pytest.param(*_pair("enrolled pilots on 03/04/2023 in the annual training program",
                        "enrolled pilots on +03/04/2023 in the annual training program"), id="B1-date-plus"),
    pytest.param(*_pair("enrolled pilots on 03/04/2023 in the annual training program",
                        "enrolled pilots on ~03/04/2023 in the annual training program"), id="B1-date-tilde"),
    pytest.param(*_pair("recorded a 10/12/15 split in the annual training program",
                        "recorded a >10/12/15 split in the annual training program"), id="B1-date-greater"),
    pytest.param(*_pair("recorded a 10-12-15 split in the annual training program",
                        "recorded a \u221210-12-15 split in the annual training program"), id="B1-date-unicode-minus"),
    pytest.param(*_pair("recorded a 10/12/15 split in the annual training program",
                        "recorded a 10/12/15\u2030 split in the annual training program"), id="B1-date-per-mille"),
    # Adversary D-146, BLOCKER 2 — on b4d3905 source runs were built from the
    # citation-STRIPPED text, so "two [S3] hundred" joined into "two hundred".
    pytest.param(*_pair(f"enrolled two [S3] hundred {TRAINING}", f"enrolled two hundred {TRAINING}"),
                 id="B2-citation-joins-spelled-run"),
    pytest.param(*_pair("enrolled twenty [S2] five-year veterans in the annual training program",
                        "enrolled twenty-five veterans in the annual training program"),
                 id="B2-citation-joins-twenty-five"),
]


@pytest.mark.parametrize("source_text,claim_text", ATTACKS)
def test_fragment_of_the_source_figure_is_refused_as_a_figure(
    tmp_path: Path, source_text: str, claim_text: str
) -> None:
    code, verdict = _verdict(tmp_path, source_text, claim_text)
    assert verdict == "UNVERIFIED_NUMBER", (
        f"refused as {verdict}, not as a figure problem — the figure reader may "
        f"still take a fragment of the source's figure")
    assert code != 0


HONEST = [
    pytest.param(*_pair(f"enrolled two hundred {TRAINING}", f"enrolled two hundred {TRAINING}"),
                 id="N7-twin-same-spelling"),
    pytest.param(*_pair(f"enrolled two-hundred {TRAINING}", f"enrolled two hundred {TRAINING}"),
                 id="N7-twin-hyphenated-source"),
    pytest.param(*_pair(f"enrolled two hundred fifty {TRAINING}", f"enrolled two hundred fifty {TRAINING}"),
                 id="N7-twin-compound"),
    pytest.param(*_pair(f"enrolled 1 200 {TRAINING}", f"enrolled 1 200 {TRAINING}"),
                 id="N8-twin-same-grouping"),
    pytest.param(*_pair(f"enrolled 1 200 {TRAINING}", f"enrolled 1 200 {TRAINING}"),
                 id="N8-twin-nbsp-vs-space"),
    pytest.param(*_pair(f"enrolled 40-50 {TRAINING}", f"enrolled 40-50 {TRAINING}"),
                 id="N9-twin-same-range"),
    pytest.param(*_pair(f"enrolled 40-50 {TRAINING}", f"enrolled 40 to 50 {TRAINING}"),
                 id="N9-twin-range-spelled-with-to"),
    pytest.param(*_pair(f"enrolled 40-50 {TRAINING}", f"enrolled up to 50 {TRAINING}"),
                 id="N9-twin-up-to-high-end"),
    pytest.param(*_pair("published the annual review on 03/04/2023", "published the annual review on 03/04/2023"),
                 id="N10-twin-same-date"),
    pytest.param(*_pair("published version 2.10 during the annual review", "published version 2.10 during the annual review"),
                 id="N10-twin-same-version"),
    pytest.param(*_pair("posted a net margin of 4.5% in 2023", "posted a net margin of 4.5% in 2023"),
                 id="decimal-twin-same-digits"),
]


@pytest.mark.parametrize("source_text,claim_text", HONEST)
def test_same_figure_written_the_same_way_grounds(
    tmp_path: Path, source_text: str, claim_text: str
) -> None:
    code, verdict = _verdict(tmp_path, source_text, claim_text)
    assert verdict == "GROUNDED", f"honest twin refused as {verdict}"
    assert code == 0


GROUPING_DECISION = [
    pytest.param(*_pair(f"enrolled 1 200 {TRAINING}", f"enrolled 1,200 {TRAINING}"), id="comma-vs-space"),
    pytest.param(*_pair(f"enrolled 1 200 {TRAINING}", f"enrolled 1200 {TRAINING}"), id="plain-vs-space"),
    pytest.param(*_pair(f"enrolled 1,200 {TRAINING}", f"enrolled 1 200 {TRAINING}"), id="space-vs-comma"),
]


@pytest.mark.parametrize("source_text,claim_text", GROUPING_DECISION)
def test_space_grouped_figure_matches_only_space_grouped(
    tmp_path: Path, source_text: str, claim_text: str
) -> None:
    """Pins the decision in the module docstring: refused, as on main."""
    code, verdict = _verdict(tmp_path, source_text, claim_text)
    assert verdict == "UNVERIFIED_NUMBER"
    assert code != 0


# The figure layer alone. "at most 50" / "at least 40" carry content words the
# source lacks, so through the CLI T1 refuses them before the figure is read
# (UNGROUNDED); numeric_ok is where the bound reading lives, so it is pinned
# here directly. The 1,200 / 1200 equivalence is pinned here for the same
# reason (T1 compares the written tokens).
def _src(text: str) -> RetrievedSource:
    return RetrievedSource(
        source_id="S1", url=None, file_path=None, fetched_at="t", tool="Read",
        content_sha256="x", text=text, full_text_source="verbatim",
        captured_via="inline", query_provenance="q",
    )


def _claim(text: str) -> Claim:
    return classify(Claim(0, text, ClaimKind.NUMERIC, (), ()))


FIGURE_LAYER = [
    pytest.param("enrolled 40-50 pilots.", "enrolled at most 50 pilots", True, id="at-most-high-end"),
    pytest.param("enrolled 40-50 pilots.", "enrolled no more than 50 pilots", True, id="no-more-than-high-end"),
    pytest.param("enrolled 40-50 pilots.", "enrolled at least 40 pilots", True, id="at-least-low-end"),
    pytest.param("enrolled 40-50 pilots.", "enrolled no fewer than 40 pilots", True, id="no-fewer-than-low-end"),
    pytest.param("enrolled 40-50 pilots.", "enrolled at most 40 pilots", False, id="at-most-low-end"),
    pytest.param("enrolled 40-50 pilots.", "enrolled about 50 pilots", False, id="unlisted-bound-refused"),
    pytest.param("enrolled 40-50 pilots.", "enrolled 40-50 pilots", True, id="range-to-range"),
    pytest.param("enrolled 40 pilots and 50 staff.", "enrolled 40-50 pilots", False, id="claim-range-vs-two-singles"),
    pytest.param("enrolled 1,200 pilots.", "enrolled 1200 pilots", True, id="comma-vs-plain-unchanged"),
    pytest.param("enrolled 1 200 pilots.", "enrolled 1200 pilots", False, id="space-group-vs-plain"),
    pytest.param("costs $4.50 each.", "costs $4.5 each", False, id="fraction-digits-differ"),
    pytest.param("raised $1.5 million.", "raised $1,500,000", True, id="decimal-vs-undotted-by-value"),
    # "X to Y" after "by"/"from" is a change of value, not a span: both figures
    # are real values (the v3 r46_n11 honest control). Main's behaviour, kept.
    pytest.param("enrollment rose by 300 to 1,000.", "enrollment rose by 300", True, id="change-by-is-not-a-range"),
    pytest.param("costs fell from $50 to $40.", "costs fell to $40", True, id="change-from-is-not-a-range"),
    # Adversary audit (D-146): the grouped form must never swallow a figure
    # next to an identifier — "A1 200" read as the identifier "A1" alone, so
    # the "200" main checked went unchecked.
    pytest.param("trained the A1 cohort of 30 pilots.", "trained the A1 200 pilots", False, id="identifier-head-swallow"),
    pytest.param("trained the GPT-4 cohort of 30 pilots.", "trained GPT-4 200 pilots", False, id="joiner-identifier-swallow"),
    pytest.param("trained 1 pilot on the 300A line.", "trained 1 200A pilots", False, id="identifier-tail-swallow"),
]


@pytest.mark.parametrize("source_text,claim_text,expected", FIGURE_LAYER)
def test_figure_layer_range_bounds_and_grouping(
    source_text: str, claim_text: str, expected: bool
) -> None:
    assert numeric_ok(_claim(claim_text), [_src(source_text)]) is expected
