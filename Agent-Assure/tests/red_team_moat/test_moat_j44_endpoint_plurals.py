"""J-44 — an endpoint the source asserts VERBATIM was refused over one letter.

`_contains_word` matches on word boundaries, so "migraines" does not occur in
"severe migraine": a claim whose endpoint the cited source states in the
singular read UNVERIFIED_RELATION. That is Error-A — recoverable, but it is the
exact failure mode the gate's honest users hit, and it taxes the relational class
for a morphological difference that carries no meaning.

SEQUENCING WAS THE RULING (Sai, 2026-10-02): fix this AFTER tightening
`extract_arguments`, never before. Loosening endpoint matching while each
endpoint was still ONE TOKEN would have widened the weakest surface in the
branch — "pipeline"/"pipelines" matching more documents, with no modifiers
required. With endpoints now full phrases (J-39), every modifier must still be
present; only the number of each word is forgiven.

TWO PROPERTIES, and the second is why this is safe:
  1. The stem is applied SYMMETRICALLY — both the endpoint token and the window
     word are stemmed — so it cannot prefer one direction.
  2. It is applied to ENDPOINTS ONLY. A relation TRIGGER is still matched
     literally: a source that says "cause" does not assert what a claim saying
     "causes" asserts, and stemming the trigger lexicon would start matching
     the noun "cause" as a causal assertion.
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


SINGULAR_SOURCES = [
    _rec("S1", "Chronic sleep deprivation causes severe migraine in "
               "susceptible adults, across three independent cohorts."),
    _rec("S2", "Patients presenting with severe migraine consistently report "
               "poor sleep quality in the preceding week."),
]

PLURAL_SOURCES = [
    _rec("S3", "Chronic sleep deprivation causes severe migraines in "
               "susceptible adults, across three independent cohorts."),
    _rec("S4", "Patients presenting with severe migraines consistently report "
               "poor sleep quality in the preceding week."),
]


def _report(tmp_path, draft, records):
    p = tmp_path / "s.jsonl"
    p.write_text("".join(json.dumps(r) + "\n" for r in records), encoding="utf-8")
    return g.score_report([g.classify(c) for c in g.decompose(draft)],
                          g.load_store(str(p)))


def test_a_plural_endpoint_matches_a_singular_source(tmp_path):
    """The documented J-44 case: one letter, one wrongful refusal."""
    rep = _report(tmp_path,
                  "Chronic sleep deprivation causes severe migraines "
                  "[S1][S2].\n", SINGULAR_SOURCES)
    assert rep["per_claim"][0]["verdict"] == "GROUNDED"
    assert rep["gate"] == "PASS"


def test_a_singular_endpoint_matches_a_plural_source(tmp_path):
    """SYMMETRY. A stem applied in one direction only is a different rule
    depending on who wrote which side, which is not a rule at all."""
    rep = _report(tmp_path,
                  "Chronic sleep deprivation causes severe migraine "
                  "[S3][S4].\n", PLURAL_SOURCES)
    assert rep["per_claim"][0]["verdict"] == "GROUNDED"
    assert rep["gate"] == "PASS"


@pytest.mark.parametrize("phrase,window,expected", [
    ("severe migraines", "severe migraine was reported", True),
    ("severe migraine", "severe migraines were reported", True),
    ("operating costs", "operating cost fell", True),
    # NOT a plural pair — the stem must not become a prefix match.
    ("migraines", "migration was observed", False),
    ("losses", "a pre-tax loss was reported", False),  # -es is NOT handled
    ("data loss", "a pre-tax loss was reported", False),  # modifier still required
    ("loss", "the lossless codec was used", False),  # boundaries still hold
])
def test_the_stem_is_symmetric_and_narrow(phrase, window, expected):
    assert g._endpoint_in_window(window, phrase) is expected


def test_the_modifiers_are_still_required_with_stemming_on(tmp_path):
    """J-39 must survive J-44. If stemming let a bare head noun through, the
    ingestion-pipeline attack would return by a different door."""
    unrelated = [
        _rec("S5", "Deal flow slowed as the sponsor's pipelines thinned. A "
                   "thinner pipeline leads to a wider loss in any down cycle."),
        _rec("S6", "Sensorineural hearing losses were reported in a minority "
                   "of randomised patients."),
    ]
    rep = _report(tmp_path,
                  "The ingestion pipeline causes silent data loss [S5][S6].\n",
                  unrelated)
    assert rep["per_claim"][0]["verdict"] == "UNVERIFIED_RELATION"


def test_a_relation_trigger_is_NOT_stemmed(tmp_path):
    """"cause" is a noun as often as it is a verb. A window that says "cause"
    asserts nothing a claim saying "causes" asserts, and stemming the trigger
    lexicon would read every mention of "the cause" as a causal assertion."""
    no_trigger = [
        _rec("S7", "Chronic sleep deprivation is one cause under study for "
                   "severe migraines in susceptible adults."),
        _rec("S8", "Patients with severe migraines report poor sleep quality."),
    ]
    rep = _report(tmp_path,
                  "Chronic sleep deprivation causes severe migraines "
                  "[S7][S8].\n", no_trigger)
    assert rep["per_claim"][0]["verdict"] == "UNVERIFIED_RELATION"


def test_stemming_is_confined_to_the_endpoint_predicate():
    """Over the AST: the trigger loop in `_relation_asserted` must keep calling
    `_contains_word` directly, so no future edit routes triggers through the
    stem-aware predicate."""
    import ast
    import inspect
    import textwrap

    tree = ast.parse(textwrap.dedent(inspect.getsource(g._relation_asserted)))
    # The trigger comprehension is the only place _contains_word may appear.
    calls = [
        node for node in ast.walk(tree)
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
    ]
    names = [c.func.id for c in calls]
    assert "_contains_word" in names, "triggers must be matched literally"
    assert "_stem" not in names, "_relation_asserted must not stem anything"
