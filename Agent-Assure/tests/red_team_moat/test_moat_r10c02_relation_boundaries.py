"""R10C-02 (part) — two sources corroborated a relation nobody asserted.

`_relation_asserted` matched endpoints and triggers by BARE SUBSTRING, so
"AI drives mass layoffs [S1][S2]" certified GROUNDED at PASS 100.0 against two
sources whose only "ai" was inside the word **said**. The two-distinct-source
rule did its job perfectly and corroborated nothing.

The fix matches on word boundaries, expressed as lookarounds on word characters
rather than `\\b` — `\\b` is defined relative to the adjacent character's class
and misbehaves when the needle begins or ends with punctuation, which a head
noun extracted from real prose regularly does.

Strictly fail-closed: it can only REMOVE spurious matches.

PARTIAL. R10C-02's other half — `extract_arguments` keeps only ONE token per
side, so unrelated subjects can still collide — is a design change and is left
OPEN under J-39. Do not read this file as closing R10C-02.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))

import ground_check as g  # noqa: E402


def _rec(sid, text):
    return {"source_id": sid, "url": None, "file_path": "/tmp/a",
            "fetched_at": "2026-09-13T00:00:00Z", "tool": "Read",
            "content_sha256": "a" * 64, "text": text,
            "full_text_source": "verbatim", "captured_via": "inline",
            "query_provenance": "q-" + sid}


# The ONLY occurrence of "ai" in either source is inside the word "said".
SUBSTRING_ONLY = [
    _rec("S1", "The chief economist said restructuring causes widespread "
               "layoffs across the sector."),
    _rec("S2", "Analysts said the restructuring leads to mass layoffs at "
               "several firms."),
]

GENUINE = [
    _rec("S1", "Industry analysts report that AI causes widespread layoffs "
               "across the technology sector."),
    _rec("S2", "Adoption of AI leads to mass layoffs at several large firms, "
               "according to the survey."),
]


def _report(tmp_path, draft, records):
    p = tmp_path / "s.jsonl"
    p.write_text("".join(json.dumps(r) + "\n" for r in records), encoding="utf-8")
    return g.score_report([g.classify(c) for c in g.decompose(draft)],
                          g.load_store(str(p)))


def test_endpoint_matched_only_inside_another_word_is_refused(tmp_path):
    """The reproduction: "ai" inside "said". Was GROUNDED / PASS 100.0."""
    for source in SUBSTRING_ONLY:
        assert "ai" in source["text"].casefold(), "fixture lost its premise"
    rep = _report(tmp_path, "AI drives mass layoffs [S1][S2].\n", SUBSTRING_ONLY)
    assert rep["per_claim"][0]["relation_diagnostic"] == g.RELATION_NOT_CORROBORATED
    assert rep["gate"] != "PASS"


def test_the_genuine_relation_is_still_CORROBORATED(tmp_path):
    """CONTROL. Without this the fix could be 'refuse all relational claims'.

    Under ADR-007 this control moved from the verdict to the diagnostic: corroboration is still measured (relation_diagnostic), it just no longer votes on the gate, so this is not a weakening.
    """
    rep = _report(tmp_path, "AI drives mass layoffs [S1][S2].\n", GENUINE)
    assert rep["per_claim"][0]["relation_diagnostic"] == g.RELATION_CORROBORATED
    assert rep["per_claim"][0]["verdict"] == "UNGROUNDED"
    assert rep["gate"] == "FAIL"


@pytest.mark.parametrize("word,inside", [
    ("ai", "said"),
    ("art", "start"),
    ("ion", "ionisation"),
])
def test_contains_word_requires_boundaries(word, inside):
    """Unit-level, so the rule is pinned independently of the gate's plumbing."""
    assert not g._contains_word(inside, word)
    assert g._contains_word(f"a {word} here", word)


def test_contains_word_handles_punctuation_edges():
    """Why lookarounds and not \\b: a head noun can begin or end with
    punctuation, where \\b's behaviour flips."""
    assert g._contains_word("the (pipeline) failed", "(pipeline)")
    assert not g._contains_word("", "pipeline")
    assert not g._contains_word("pipeline", "")


def test_multiword_endpoint_still_matches(tmp_path):
    """Boundaries must not break phrases, only sub-word collisions."""
    assert g._contains_word("the ingestion pipeline failed", "ingestion pipeline")
