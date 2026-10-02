"""J-22 — `concluded that` and `indicates that` are endorsement, `reported` is not.

D-36 made the factive check a WHITELIST, which is the right shape: an unlisted
verb refuses without ever being enumerated. The cost was that honest sources
using `concluded that` / `indicates that` — the two commonest forms in academic
prose — started failing. Adding them is PASS-ENABLING, so it was Sai's call;
RATIFIED 2026-10-01 (D-51 ruling 4).

THE ARGUMENT THAT DECIDED IT WAS CONSISTENCY, NOT TASTE. `_FACTIVE_VERBS`
already contains `find / finds / found`. "Smith found that X" carries exactly
the same attribution ambiguity as "Smith concluded that X", so excluding
`concluded` while including `found` was an inconsistency, not a caution.

`report*` STAYS OUT, and the reason is sharper than "it is attribution": its
canonical subject is a PUBLICATION relaying someone else's claim. "The blog
reported that X" does not assert X. It is the journalistic attribution verb, and
admitting it would make attribution indistinguishable from assertion — the exact
confusion rounds 3 through 8 kept exploiting.

CEILING, NAMED: this whitelist is SUBJECT-BLIND. The real distinction is who the
verb's subject is, not which verb it is, so "Critics concluded that X" is the
next attack on this surface. A verb-only list is a smaller surface than a
blacklist but it is not the final shape.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))

import ground_check as g  # noqa: E402

CLAIM_TEXT = "insulin resistance impairs glucose uptake in skeletal muscle"


def _report(tmp_path, source_text, claim=f"{CLAIM_TEXT.capitalize()} [S1]."):
    rec = {"source_id": "S1", "url": None, "file_path": "/tmp/a",
           "fetched_at": "2026-09-13T00:00:00Z", "tool": "Read",
           "content_sha256": "a" * 64, "text": source_text,
           "full_text_source": "verbatim", "captured_via": "inline",
           "query_provenance": "q1"}
    p = tmp_path / "s.jsonl"
    p.write_text(json.dumps(rec) + "\n", encoding="utf-8")
    return g.score_report([g.classify(c) for c in g.decompose(claim + "\n")],
                          g.load_store(str(p)))


# --- the two families ratified IN -------------------------------------------

@pytest.mark.parametrize("verb", ["concluded", "concludes", "conclude"])
def test_conclude_family_endorses(tmp_path, verb):
    rep = _report(tmp_path, f"The study {verb} that {CLAIM_TEXT}.")
    assert rep["per_claim"][0]["verdict"] == "GROUNDED", rep["per_claim"]


@pytest.mark.parametrize("verb", ["indicates", "indicate", "indicated"])
def test_indicate_family_endorses(tmp_path, verb):
    rep = _report(tmp_path, f"The data {verb} that {CLAIM_TEXT}.")
    assert rep["per_claim"][0]["verdict"] == "GROUNDED", rep["per_claim"]


# --- the family ratified OUT, and the guard it protects ---------------------

@pytest.mark.parametrize("verb", ["reported", "reports", "report"])
def test_report_family_is_still_refused(tmp_path, verb):
    """THE LOAD-BEARING NEGATIVE. If this ever starts passing, attribution has
    become indistinguishable from assertion and the whole guard is hollow."""
    rep = _report(tmp_path, f"The blog {verb} that {CLAIM_TEXT}.")
    assert rep["per_claim"][0]["verdict"] != "GROUNDED", rep["per_claim"]


@pytest.mark.parametrize("verb", ["argued", "claimed", "alleged", "speculated",
                                  "maintained", "posited", "insisted"])
def test_the_whitelist_still_refuses_everything_unlisted(tmp_path, verb):
    """The whitelist's whole value: these refuse without being enumerated."""
    rep = _report(tmp_path, f"The vendor {verb} that {CLAIM_TEXT}.")
    assert rep["per_claim"][0]["verdict"] != "GROUNDED", rep["per_claim"]


@pytest.mark.xfail(strict=True, reason=(
    "Round-7 finding c5 (retraction AFTER the span), already OPEN and tripwired "
    "in test_moat_r7_open.py. J-22 does not create it — it WIDENS it by two verb "
    "families. Verified pre-existing on every already-listed verb: 'The study "
    "found/shown/demonstrated/observed that <claim> does not occur at all' all "
    "certify GROUNDED. No prefix rule can see a denial that comes after the "
    "matched span, so adding factive verbs inherits c5's reach by construction. "
    "Recorded here because the sibling check is what surfaced it."))
def test_denial_under_a_newly_added_verb_is_still_refused(tmp_path):
    """SIBLING — the null case. Adding a factive verb must not let a DENIAL
    ground: a source concluding the OPPOSITE must never certify the claim."""
    rep = _report(tmp_path,
                  f"The study concluded that {CLAIM_TEXT} does not occur at all.")
    assert rep["per_claim"][0]["verdict"] != "GROUNDED", rep["per_claim"]


def test_parity_the_already_listed_verb_behaves_the_same(tmp_path):
    """CONTROL anchoring the consistency argument: `found` was already in, and
    `concluded` must now behave identically. If these two ever diverge the
    reasoning that justified J-22 has stopped holding."""
    found = _report(tmp_path, f"The study found that {CLAIM_TEXT}.")
    concluded = _report(tmp_path, f"The study concluded that {CLAIM_TEXT}.")
    assert found["per_claim"][0]["verdict"] == concluded["per_claim"][0]["verdict"]
