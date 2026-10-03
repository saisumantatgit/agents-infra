"""J-39 — relational corroboration kept ONE TOKEN per side.

`extract_arguments` reduced each side of the relation to a single head token:
"The ingestion pipeline causes silent data loss" became ("pipeline", "loss").
Two unrelated documents that each happen to use one of those common nouns then
satisfied the two-source rule, and a window carrying both of them plus any
relational trigger satisfied the OI-MOAT-05 predicate — so a causal claim nobody
made anywhere certified GROUNDED at PASS 100.0.

The modifiers are not decoration. "silent data loss" and "a pre-tax loss" are
different objects, and the only thing that distinguished them was the words the
extractor threw away.

There was a second defect in the same branch, and it had to be fixed in the same
change: `window_supports` tested endpoint presence with a BARE SUBSTRING while
`_relation_asserted` used word boundaries (`_contains_word`). Two definitions of
"contains" in one verdict path is a seam, and a seam is where the next finding
lives (J-44). Both now go through one predicate.
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


# Two genuinely unrelated pages. Neither says anything about an ingestion
# pipeline losing data. Between them they contain the words "pipeline" and
# "loss", and one of them has a window carrying both plus a trigger.
UNRELATED = [
    _rec("S1",
         "Deal flow slowed through the third quarter as the sponsor's "
         "pipeline thinned. The firm reported a pre-tax loss after the "
         "write-down on its European holdings. Bankers briefed on the "
         "process said a thinner pipeline leads to a wider loss in any "
         "down cycle."),
    _rec("S2",
         "Among patients randomised to the active arm, sensorineural hearing "
         "loss was reported in a minority of cases. The trial was stopped "
         "early for futility after the second interim analysis."),
]

HONEST = [
    _rec("S3",
         "Sustained write amplification in the ingestion pipeline causes "
         "silent data loss when the commit log is truncated mid-flush."),
    _rec("S4",
         "Operators report silent data loss downstream of the ingestion "
         "pipeline whenever back-pressure is ignored."),
]


def _report(tmp_path, draft, records):
    p = tmp_path / "s.jsonl"
    p.write_text("".join(json.dumps(r) + "\n" for r in records), encoding="utf-8")
    return g.score_report([g.classify(c) for c in g.decompose(draft)],
                          g.load_store(str(p)))


DRAFT = "The ingestion pipeline causes silent data loss [S1][S2].\n"


def test_the_modifiers_are_part_of_the_endpoint(tmp_path):
    """The documented J-39 attack: one common noun per side is a coincidence."""
    rep = _report(tmp_path, DRAFT, UNRELATED)
    assert rep["per_claim"][0]["relation_diagnostic"] == g.RELATION_NOT_CORROBORATED
    assert rep["gate"] != "PASS"


def test_a_source_that_really_asserts_the_relation_is_still_CORROBORATED(tmp_path):
    """Without this the fix could be a blanket refusal that proves nothing about
    endpoints at all — the tautology INS-005 exists to catch.

    ADR-007 / D-76: a RELATIONAL claim is NEVER certified. The corroboration
    this test set up is still computed and still asserted — it moved to
    `relation_diagnostic`, which is information, not a verdict. The verdict
    is UNVERIFIED_RELATION for every relational claim, by design.
    """
    rep = _report(tmp_path,
                  "The ingestion pipeline causes silent data loss [S3][S4].\n",
                  HONEST)
    assert rep["per_claim"][0]["relation_diagnostic"] == g.RELATION_CORROBORATED
    assert rep["per_claim"][0]["verdict"] == "UNVERIFIED_RELATION"
    assert rep["gate"] == "FAIL"


def test_extract_arguments_keeps_the_whole_contiguous_phrase():
    """The unit-level property, stated directly."""
    assert g.extract_arguments(
        "The ingestion pipeline causes silent data loss [S1][S2]."
    ) == ("ingestion pipeline", "silent data loss")


def test_a_bare_digit_inside_the_phrase_does_not_break_the_run():
    """"type 2 diabetes" is one noun phrase. The digit is dropped (a source may
    write "type II"), but it must not truncate the phrase to "diabetes"."""
    assert g.extract_arguments(
        "Insulin resistance causes type 2 diabetes [S2][S3]."
    ) == ("insulin resistance", "type diabetes")


@pytest.mark.parametrize("phrase,window,expected", [
    ("data loss", "silent data loss was observed", True),
    ("data loss", "loss of data was observed", True),       # order is free
    ("data loss", "a pre-tax loss was reported", False),    # a token missing
    ("loss", "the lossless codec was used", False),         # word boundaries
])
def test_one_definition_of_contains_for_both_callers(phrase, window, expected):
    """`window_supports` and `_relation_asserted` must agree, token for token.

    Before this fix one used a bare substring and the other used word
    boundaries, so "loss" was supported by "lossless" on one path and not the
    other. The seam is the finding.
    """
    assert g._endpoint_in_window(window, phrase) is expected


def test_window_supports_and_relation_asserted_use_the_same_predicate():
    """Checked over the AST, not the text: both must route through the one
    helper, so a future edit cannot quietly re-open the seam."""
    import ast
    import inspect
    import textwrap

    for name in ("window_supports", "_relation_asserted"):
        tree = ast.parse(textwrap.dedent(inspect.getsource(getattr(g, name))))
        called = {
            node.func.id for node in ast.walk(tree)
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
        }
        assert "_endpoint_in_window" in called, (
            f"{name} does not use the shared endpoint predicate")
