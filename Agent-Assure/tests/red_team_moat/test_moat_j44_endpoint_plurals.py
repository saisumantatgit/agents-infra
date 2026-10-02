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


_J44_REOPENED = (
    "J-44 REOPENED 2026-10-02 (D-69), hours after it landed. Round 12 showed "
    "`_stem` maps the NOUN 'news' to the ADJECTIVE 'new', so 'The recall "
    "causes negative news [S1][S2]' certified GROUNDED / PASS 100.0 against "
    "two sources containing no 'news'. Telling 'news'/'new' from 'cost'/'costs' "
    "is a DICTIONARY fact, not a suffix fact, and an incomplete blacklist of "
    "s-final singulars on a LOOSENING is an Error-B generator. The Error-A "
    "below is real and recoverable; the Error-B it cost is not. Escalation #1."
)


@pytest.mark.xfail(strict=True, reason=_J44_REOPENED)
def test_a_plural_endpoint_matches_a_singular_source(tmp_path):
    """The documented J-44 case: one letter, one wrongful refusal.

    Kept as a strict xfail rather than deleted — this is the Error-A the
    project still owes its honest users, and deleting it would make the next
    reader think the refusal was intended."""
    rep = _report(tmp_path,
                  "Chronic sleep deprivation causes severe migraines "
                  "[S1][S2].\n", SINGULAR_SOURCES)
    assert rep["per_claim"][0]["verdict"] == "GROUNDED"
    assert rep["gate"] == "PASS"


@pytest.mark.xfail(strict=True, reason=_J44_REOPENED)
def test_a_singular_endpoint_matches_a_plural_source(tmp_path):
    """SYMMETRY. A stem applied in one direction only is a different rule
    depending on who wrote which side, which is not a rule at all."""
    rep = _report(tmp_path,
                  "Chronic sleep deprivation causes severe migraine "
                  "[S3][S4].\n", PLURAL_SOURCES)
    assert rep["per_claim"][0]["verdict"] == "GROUNDED"
    assert rep["gate"] == "PASS"


@pytest.mark.parametrize("phrase,window,expected", [
    # The three plural pairs read False again: J-44 is withdrawn (D-69). They
    # stay in the table, with the expectation flipped rather than the rows
    # deleted, so the Error-A is visible in the same place as the guards.
    ("severe migraines", "severe migraine was reported", False),
    ("severe migraine", "severe migraines were reported", False),
    ("operating costs", "operating cost fell", False),
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
    assert rep["per_claim"][0]["relation_diagnostic"] == g.RELATION_NOT_CORROBORATED


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
    assert rep["per_claim"][0]["relation_diagnostic"] == g.RELATION_NOT_CORROBORATED


def test_no_endpoint_token_is_matched_by_a_STEM_COLLISION():
    """R12-01, the Error-B J-44 cost, pinned so it can never return silently.

    The old form of this test asserted over the AST that `_relation_asserted`
    does not call `_stem` — which round 12 called near-vacuous, correctly: it
    never plausibly would, and the stemming it was named for happened one frame
    down in `_endpoint_in_window`. An AST guard on the wrong frame is a test
    that cannot fail.

    This asserts the PROPERTY instead, over the collision pairs that defeated
    the suffix rule. Each is a word whose naive stem equals a DIFFERENT word.
    """
    collisions = [
        ("news", "the new coverage limits"),      # noun -> adjective
        ("species", "a specie of bond"),
        ("ethics", "a strong ethic"),
        ("damages", "the damage was limited"),    # legal award -> harm
        ("lens", "len of the pipeline"),
    ]
    for endpoint, window in collisions:
        assert not g._endpoint_in_window(window, endpoint), (
            f"{endpoint!r} must not be matched by {window!r} — a stem is not a "
            f"meaning, and this pair is how J-44 produced an Error-B")


def test_a_relation_trigger_is_matched_LITERALLY():
    """The guard that outlives J-44: whatever forgiveness is ever added to
    endpoint matching, a TRIGGER is matched word for word. "cause" is a noun as
    often as a verb, and stemming the lexicon would read every mention of "the
    cause" as a causal assertion."""
    import ast
    import inspect
    import textwrap

    tree = ast.parse(textwrap.dedent(inspect.getsource(g._relation_asserted)))
    names = [
        node.func.id for node in ast.walk(tree)
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
    ]
    assert "_contains_word" in names, "triggers must be matched literally"
