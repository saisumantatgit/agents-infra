"""OI-UX-01 — every absent-evidence state must ASSERT, never render as blank.

The defect these tests pin (2026-09-12): each surface that displayed evidence
rendered the ABSENCE of evidence as an empty string or an internal token —
``""`` for an uncited claim, ``[NOT IN STORE]`` for a fabricated citation, a
bare query list for an absence claim. All three read as "the tool broke"
rather than "the tool looked and found nothing", and those are opposite
verdicts on the gate's trustworthiness. The project's own author stalled on
6 of 20 calibration rows — every one of them an evidence-reads-as-absent row
— and asked "nothing here?".

The property under test is therefore NOT "a string is present" (a tautology
that a ``return ""`` would satisfy in the report and fail in the reader).
It is: **for every claim, the report states what was consulted, in prose, and
never leaks an internal token.**
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

import ground_check as g  # noqa: E402


def _src(source_id, text, *, full_text_source="verbatim", query="a search"):
    return g.RetrievedSource(
        source_id=source_id, url=None, file_path="/tmp/x",
        fetched_at="2026-09-12T00:00:00Z", tool="Read",
        content_sha256="sha", text=text,
        full_text_source=full_text_source, captured_via="hook",
        query_provenance=query,
    )


def _report(draft: str, store: dict) -> dict:
    claims = [g.classify(c) for c in g.decompose(draft)]
    return g.score_report(claims, store)


STORE = {
    "S1": _src("S1", "Redis handles 100K ops per second in sustained testing.",
               query="redis throughput benchmark"),
    "S2": _src("S2", "Regulatory bulletins list no recall actions this year.",
               query="FDA recall database inhaler recall"),
}

# Internal tokens and delimiters that must never reach a reader.
LEAKED_TOKENS = ("[NOT IN STORE]", "|||", "None", "UNVERIFIED_", "_RE",
                 "full_text_source=")


@pytest.mark.parametrize("draft", [
    "The device sold 250,000 units in its first month.",                # UNCITED
    "The Zentara trial reported a 62% response rate [S19].",            # fabricated
    "There is no recall of the Zentara inhaler in any regulated market.",  # absence
    "Redis handles 100K ops per second [S1].",                          # grounded
])
def test_every_claim_states_what_was_consulted(draft):
    """The basis is prose that names the store, not a blank or a token."""
    for pc in _report(draft, STORE)["per_claim"]:
        basis = pc["evidence_basis"]
        assert basis.strip(), f"blank basis for {pc['verdict']}"
        assert basis.endswith("."), "not a sentence"
        assert len(basis.split()) >= 8, f"too terse to disambiguate: {basis}"
        for tok in LEAKED_TOKENS:
            assert tok not in basis, f"internal token {tok!r} leaked: {basis}"


def test_uncited_says_not_a_retrieval_failure():
    """The distinction Sai could not make: nothing cited != nothing retrieved."""
    basis = _report("The device sold 250,000 units in its first month.",
                    STORE)["per_claim"][0]["evidence_basis"]
    assert "No source is cited" in basis
    assert "NOT a retrieval failure" in basis
    assert "2 retrieved sources" in basis


def test_fabricated_citation_names_the_marker_and_the_store_size():
    basis = _report("The Zentara trial reported a 62% response rate [S19].",
                    STORE)["per_claim"][0]["evidence_basis"]
    assert basis.startswith("S19 is cited"), basis
    # J-56: was "NEVER RETRIEVED this session". The gate cannot claim session
    # scope unless --session-id was passed, and evidence_basis is not told
    # whether it was; all it knows is that the id is absent from the store.
    assert "NOT IN THE EVIDENCE STORE" in basis
    assert "this session" not in basis.lower(), (
        "evidence_basis must not claim a scope it was not given")
    assert "[" not in basis and "]" not in basis, "bracket marker leaked"


def test_absence_shows_the_complete_search_record():
    basis = _report(
        "There is no recall of the Zentara inhaler in any regulated market.",
        STORE)["per_claim"][0]["evidence_basis"]
    assert "what was SEARCHED, not what was cited" in basis
    assert "Complete record consulted" in basis
    for q in ("redis throughput benchmark", "FDA recall database inhaler recall"):
        assert f'"{q}"' in basis, f"query {q!r} not shown"


def test_absence_with_no_queries_says_so_rather_than_showing_nothing():
    basis = _report(
        "There is no recall of the Zentara inhaler in any regulated market.",
        {})["per_claim"][0]["evidence_basis"]
    assert "recorded NO search queries" in basis


def test_summary_source_states_the_policy():
    """The user acting on a verdict is told WHY a summary cannot ground."""
    store = {"S44": _src("S44", "The vendor confirmed full GDPR compliance.",
                         full_text_source="haiku_summary")}
    basis = _report("The vendor confirmed full GDPR compliance [S44].",
                    store)["per_claim"][0]["evidence_basis"]
    assert "AI-generated SUMMARY" in basis
    assert "never grounds a claim on a summary" in basis


def test_basis_branch_matches_the_verdict_branch():
    """A display that derives state independently can contradict the verdict.

    Pinned because the first hand-wired call of this function during
    development reported "none was named by this claim" for a claim that
    visibly named S1.
    """
    draft = ("Redis handles 100K ops per second [S1].\n\n"
             "The Zentara trial reported a 62% response rate [S19].\n\n"
             "The device sold 250,000 units in its first month.")
    expected = {
        "GROUNDED": "Checked verbatim against",
        "UNVERIFIED_CITATION": "NOT IN THE EVIDENCE STORE",
        "UNCITED": "No source is cited",
    }
    seen = set()
    for pc in _report(draft, STORE)["per_claim"]:
        verdict = pc["verdict"]
        if verdict in expected:
            assert expected[verdict] in pc["evidence_basis"], pc
            seen.add(verdict)
    assert seen == set(expected), f"missing verdicts: {set(expected) - seen}"


def test_retained_appendix_carries_the_basis():
    """The appendix is what a user must act on; a bare verdict is not actionable."""
    rep = _report("The Zentara trial reported a 62% response rate [S19].", STORE)
    assert rep["retained_appendix"], "expected a retained violation"
    for entry in rep["retained_appendix"]:
        assert entry["evidence_basis"].strip()


def test_evidence_basis_does_not_mutate_its_inputs():
    store = dict(STORE)
    claims = [g.classify(c)
              for c in g.decompose("Redis handles 100K ops per second [S1].")]
    before = repr(store), repr(claims)
    for c in claims:
        g.evidence_basis(c, store)
    assert (repr(store), repr(claims)) == before


def test_basis_is_not_consulted_by_any_verdict_path():
    """Display must never become decision — source inspection, like D-34's.

    Checked over the AST, not the source TEXT. The substring form of this guard
    could not tell a call from a comment, and on 2026-10-01 it failed J-25 for
    writing the words "evidence_basis" in a comment explaining that the gate
    had contradicted its own explanation of itself. A guard that fires on prose
    trains people to delete the prose. The AST form asserts the property the
    test is NAMED for: no verdict path REFERENCES the display layer.
    """
    import ast
    import inspect
    import textwrap

    for name in ("ground", "check_absence", "ground_relational", "classify"):
        tree = ast.parse(textwrap.dedent(inspect.getsource(getattr(g, name))))
        referenced = {
            node.id for node in ast.walk(tree) if isinstance(node, ast.Name)
        } | {
            node.attr for node in ast.walk(tree) if isinstance(node, ast.Attribute)
        }
        assert "evidence_basis" not in referenced, (
            f"{name} consults the display layer"
        )


# ---------------------------------------------------------------------------
# J-72, DISPLAY HALF (2026-10-03) — a figure refusal must be diagnosable.
# ---------------------------------------------------------------------------

def _basis_for(draft: str, source_text: str) -> str:
    store = {"S1": _src("S1", source_text)}
    return _report(draft, store)["per_claim"][0]["evidence_basis"]


def test_a_figure_refusal_names_the_figures_the_claim_asserts():
    """A user shown only `UNVERIFIED_NUMBER` cannot act; one shown `"200"` can.

    Round 16 measured that 20/20 tested identifiers (iPhone 15, ISO 27001,
    Section 409A, 5G, COVID-19) produce numeric tokens, so the commonest cause
    of a figure refusal is not a figure at all. The basis used to read only
    "Checked verbatim against 1 cited source: S1 (70 chars)."
    """
    basis = _basis_for(
        "The audit of the X200 drone programme recorded 94 advisories [S1].",
        "The audit of the X200 drone programme recorded 17 advisories in total.")
    assert '"200"' in basis and '"94"' in basis, basis
    assert "value, unit and rate qualifier" in basis


def test_the_identifier_note_is_a_FACT_about_the_extractor_not_a_judgement():
    """A conditional version of this note was written and withdrawn the same day.

    The gate was `[A-Za-z]\\d|\\d[A-Za-z]` — a digit against a letter. It fired
    on `100K`, an ordinary quantity, and MISSED `iPhone 15` and `ISO 27001`,
    which are space-separated. Over- and under-inclusive at once — which is
    J-72's own difficulty, and it does not get easier because the answer is only
    being DISPLAYED. So the note states how the extractor behaves rather than
    judging this sentence: always true, no false positives, same insight.
    """
    for draft, source in (
        ("The audit of the X200 drone programme recorded 94 advisories [S1].",
         "The audit of the X200 drone programme recorded 17 advisories in total."),
        ("Redis handles 100K ops per second [S1].",
         "Redis handles 100K ops per second in sustained testing."),
    ):
        basis = _basis_for(draft, source)
        assert "model, standard or version number" in basis, basis
        # It describes the EXTRACTOR, so it never claims this sentence contains
        # an identifier.
        assert "One of these" not in basis, basis


def test_the_display_does_not_re_derive_which_figure_failed():
    """It lists what the claim ASSERTS and stops there.

    Saying WHICH figure failed would re-implement numeric_ok's value+unit+rate
    rule in the display layer, and two copies of a moat rule diverge — the
    reason J-45 was fixed by removing false precision rather than recomputing a
    count. This pins the restraint so a later 'improvement' has to argue with it.
    """
    basis = _basis_for(
        "The audit of the X200 drone programme recorded 94 advisories [S1].",
        "The audit of the X200 drone programme recorded 17 advisories in total.")
    for forbidden in ("not found", "missing", "does not appear", "failed"):
        assert forbidden not in basis.lower(), (forbidden, basis)
