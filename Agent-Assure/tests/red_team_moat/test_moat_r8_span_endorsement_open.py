"""R8A-01 RESIDUE — the class is OPEN. D-36 closed its own fixture.

D-36 wired the endorsement guards into T1's contiguous-span path and I
recorded R8A-01/R8A-02 as CLOSED. **The solo gate refuted that within the
hour**, and I reproduced the refutation before accepting it.

What D-36 actually closed: `<non-factive verb> that THE <span>`.
What it left open: `<non-factive verb> that <any other function word> <span>`
— `at`, `in`, `of`, `as`, `about`, `more`, a numeral, anything outside the
closed determiner set the leftward scan skips.

**Every fixture in `test_moat_r8_span_endorsement.py` uses `that the …`.**
The fix and the test that certified it share one blind spot, which is the
project's standing trap: an enumeration confirms what it was built to confirm.

The class therefore survives its own fix, for the second time today, exactly
as this project's convention predicts: *a narrow fix closes the fixture it was
written against and leaves the class open — every time so far.*

**The sound fix (J-21), deliberately NOT attempted tonight.** Bound the
complementizer search AND the factive prefix to the SOURCE SENTENCE containing
the span, using the `syntok` segmenter the decomposer already depends on. That
closes this residue and R8A-03 (the unbounded prefix window) with one
structurally-correct rule instead of a third leftward-scan patch. It is a
design change to the moat's endorsement logic and it needs its own adversarial
round, which is why it is a job and not a patch.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))

import ground_check as g  # noqa: E402

SPAN = ("at least three Redis nodes silently lose acknowledged writes on "
        "restart under default settings")


def _verdict(tmp_path: Path, claim: str, source_text: str) -> tuple[str, str]:
    store = tmp_path / "s.jsonl"
    store.write_text(json.dumps({
        "source_id": "S1", "url": None, "file_path": "/tmp/a",
        "fetched_at": "2026-09-12T00:00:00Z", "tool": "Read",
        "content_sha256": "a", "text": source_text,
        "full_text_source": "verbatim", "captured_via": "hook",
        "query_provenance": "redis durability",
    }) + "\n", encoding="utf-8")
    claims = [g.classify(c) for c in g.decompose(claim + "\n")]
    rep = g.score_report(claims, g.load_store(str(store)))
    return rep["per_claim"][0]["verdict"], rep["gate"]


@pytest.mark.xfail(
    strict=True,
    reason="R8A-01 RESIDUE OPEN: the leftward scan skips only determiners, so "
           "a complementizer followed by any other function word ('that AT "
           "least three ...') leaves both endorsement guards silent. J-21.",
)
def test_attribution_over_a_non_determiner_function_word_must_not_ground(tmp_path):
    verdict, gate = _verdict(
        tmp_path, f"At least three Redis nodes silently lose acknowledged "
                  f"writes on restart under default settings [S1].",
        f"A blogger speculated that {SPAN}.")
    assert verdict != "GROUNDED"
    assert gate != "PASS"


@pytest.mark.xfail(
    strict=True,
    reason="R8A-02 RESIDUE OPEN: same gap, exercised against an explicit "
           "DENIAL. The gate certifies the negation of its own source at "
           "PASS/100.0 whenever the frame is longer than _span_is_hedged's "
           "5-token lookback. J-21.",
)
def test_explicit_denial_over_a_non_determiner_function_word_must_not_ground(tmp_path):
    verdict, gate = _verdict(
        tmp_path, f"At least three Redis nodes silently lose acknowledged "
                  f"writes on restart under default settings [S1].",
        f"It is simply not true, whatever the vendor documentation may say, "
        f"that {SPAN}.")
    assert verdict != "GROUNDED"
    assert gate != "PASS"


@pytest.mark.xfail(
    strict=True,
    reason="R8A-01 RESIDUE OPEN: the length asymmetry D-36 claimed to remove "
           "is still live for this shape — refused below min_quote_len, "
           "certified above it. Claim length remains author-controlled. J-21.",
)
def test_the_guard_is_still_not_keyed_on_claim_length(tmp_path):
    """The regression D-36's own test could not see, because it used 'that the'."""
    (tmp_path / "long").mkdir()
    (tmp_path / "short").mkdir()
    long_v, _ = _verdict(
        tmp_path / "long",
        f"At least three Redis nodes silently lose acknowledged writes on "
        f"restart under default settings [S1].",
        f"A blogger speculated that {SPAN}.")
    short_v, _ = _verdict(
        tmp_path / "short", "At least three Redis nodes lose writes [S1].",
        "A blogger speculated that at least three Redis nodes lose writes.")
    assert long_v == short_v, "claim length still changes the endorsement verdict"


# --- what D-36 DID close, kept green so a revert announces itself ------------

def test_determiner_shape_stays_closed(tmp_path):
    """D-36's real gain. Not the class, but not nothing."""
    verdict, gate = _verdict(
        tmp_path,
        "The Redis cache silently loses acknowledged writes on restart under "
        "default settings [S1].",
        "A blogger speculated that the Redis cache silently loses "
        "acknowledged writes on restart under default settings.")
    assert verdict != "GROUNDED"
    assert gate != "PASS"
