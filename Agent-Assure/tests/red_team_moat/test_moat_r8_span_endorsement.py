"""R8A-01 / R8A-02 — the endorsement guards must apply to BOTH T1 paths.

Round 8 (2026-09-12) found that `_span_is_hedged` and
`_span_under_nonfactive_complement` were called from exactly one place:
`_claim_contained_verbatim`, the exact-containment path. The >=8-token
contiguous-span path applied NEITHER. The moat's endorsement check therefore
fired for SHORT claims and was silent for long ones.

That is this project's own standing law broken by the fix written to uphold
it: **never key a moat rule on a surface property the author controls.**
Round 3 killed a token-count rule; round 4 killed a capitalisation rule; this
is claim length, and it was found on the J-19 whitelist the same day J-19
shipped claiming to close the quote-mining family.

The worst reproduction certified the EXACT NEGATION of the cited source at
gate PASS, score 100.0.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))

import ground_check as g  # noqa: E402

# 13 content tokens — comfortably over min_quote_len=8, which is the point.
LONG = ("the Redis cache silently loses acknowledged writes on restart "
        "under default settings")
SHORT = "Redis loses acknowledged writes on restart"


def _run(tmp_path: Path, claim: str, source_text: str) -> dict:
    store = tmp_path / "s.jsonl"
    store.write_text(json.dumps({
        "source_id": "S1", "url": None, "file_path": "/tmp/a",
        "fetched_at": "2026-09-12T00:00:00Z", "tool": "Read",
        "content_sha256": "a", "text": source_text,
        "full_text_source": "verbatim", "captured_via": "hook",
        "query_provenance": "redis durability",
    }) + "\n", encoding="utf-8")
    draft = tmp_path / "d.md"
    draft.write_text(claim + "\n", encoding="utf-8")
    claims = [g.classify(c) for c in g.decompose(draft.read_text())]
    return g.score_report(claims, g.load_store(str(store)))


def _verdict(rep: dict) -> str:
    return rep["per_claim"][0]["verdict"]


# --- the attack --------------------------------------------------------------

@pytest.mark.parametrize("frame", [
    "Critics argued that",
    "A blogger speculated that",
    "It is not true that",
    "The vendor denied that",
])
def test_long_claim_stripped_of_its_frame_must_not_ground(tmp_path, frame):
    """Removing the frame must not ground, at ANY claim length."""
    rep = _run(tmp_path, f"The {LONG} [S1].", f"{frame} the {LONG}.")
    assert _verdict(rep) != "GROUNDED", (
        f"frame {frame!r} stripped and still GROUNDED — the gate is asserting "
        f"what its source declined to assert")
    assert rep["gate"] != "PASS"


def test_explicit_denial_is_never_certified_as_the_claim():
    """The single worst output a grounding gate can produce."""
    import tempfile
    with tempfile.TemporaryDirectory() as d:
        rep = _run(Path(d), f"The {LONG} [S1].", f"It is not true that the {LONG}.")
    assert _verdict(rep) == "UNGROUNDED"


def test_the_guard_is_not_keyed_on_claim_length(tmp_path):
    """The regression in one assertion: short and long must agree.

    Before the fix the SHORT form was correctly refused and the LONG form was
    GROUNDED — a moat rule the author switched off by typing more words.
    """
    (tmp_path / "a").mkdir(parents=True, exist_ok=True)
    (tmp_path / "b").mkdir(parents=True, exist_ok=True)
    long_rep = _run(tmp_path / "a", f"The {LONG} [S1].",
                    f"Critics argued that the {LONG}.")
    short_rep = _run(tmp_path / "b", f"{SHORT} [S1].",
                     f"Critics argued that {SHORT}.")
    assert _verdict(long_rep) == _verdict(short_rep), (
        "claim length changed the endorsement verdict")


# --- the honest mirrors: this must not become an Error-A ---------------------

def test_claim_that_keeps_its_attribution_still_grounds(tmp_path):
    rep = _run(tmp_path, f"Critics argued that the {LONG} [S1].",
               f"Critics argued that the {LONG}.")
    assert _verdict(rep) == "GROUNDED"


def test_factive_source_still_grounds_an_unattributed_claim(tmp_path):
    """`showed that` endorses; the whitelist must keep letting it through."""
    rep = _run(tmp_path, f"The {LONG} [S1].",
               f"Our benchmark showed that the {LONG}.")
    assert _verdict(rep) == "GROUNDED"


def test_plain_unframed_source_still_grounds(tmp_path):
    rep = _run(tmp_path, f"The {LONG} [S1].", f"The {LONG}, per our testing.")
    assert _verdict(rep) == "GROUNDED"


def test_source_that_both_attributes_and_asserts_still_grounds(tmp_path):
    """'At least one clean occurrence' — mirrors _claim_contained_verbatim.

    A source that reports an attributed claim AND independently asserts it
    does endorse it. The two T1 paths must not disagree about what
    endorsement means.
    """
    rep = _run(tmp_path, f"The {LONG} [S1].",
               f"Critics argued that the {LONG}. "
               f"Our own benchmark showed that the {LONG}.")
    assert _verdict(rep) == "GROUNDED"
