"""REASONS-FOR-REFUSAL (alpha walkthrough 2, 2026-11-15).

A claim copied VERBATIM from its cited source and refused UNGROUNDED must say
WHICH rule disowned the copy and quote the source words that made it fire.
Before this change the row read "Checked verbatim against 1 cited source" and
the fix line told the author to do what he had already done (14 of ~40 honest
claims in reports/ALPHA-WALKTHROUGH-2-2026-11-15.md).

Every test below pins the TRIGGER (the source words) and the RULE code, not a
generic phrase, and every case also pins the verdict, which this change must
not move (display only: reports/REASONS-FOR-REFUSAL.md has the differential
fuzz). Red on main 7d2da1b: none of the codes exist and no basis names a
trigger.
"""
from __future__ import annotations

import ast
import inspect
import sys
import textwrap
from pathlib import Path

import pytest

_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_ROOT / "scripts"))

import ground_check as g  # noqa: E402
import explain_report as er  # noqa: E402


def _src(text: str) -> g.RetrievedSource:
    return g.RetrievedSource(
        source_id="S1", url=None, file_path="/tmp/x",
        fetched_at="2026-11-15T00:00:00Z", tool="Read", content_sha256="sha",
        text=text, full_text_source="verbatim", captured_via="hook",
        query_provenance="q")


def _rows(source: str, draft: str) -> list[dict]:
    claims = [g.classify(c) for c in g.decompose(draft)]
    report = g.score_report(claims, {"S1": _src(source)})
    return [r for r in report["per_claim"] if r["kind"] != "NON_CLAIM"]


CACHE = "The cache loses acknowledged writes on restart [S1]."

# (case id, source, draft, expected code, words the basis must quote)
CASES = [
    ("hedge_window_crosses_sentence",
     "The staging migration finished on Monday without errors. The migration "
     "moved two million customer records to the new schema.",
     "The migration moved two million customer records to the new schema [S1].",
     "verbatim_but_hedge_word_before_it",
     ['"without"', "finished on monday without errors", "before this sentence"]),
    ("non_factive_that_clause",
     "Several engineers on the vendor team have long maintained that the cache "
     "loses acknowledged writes on restart.",
     CACHE, "verbatim_but_under_non_asserting_verb",
     ['"vendor team have long maintained that"', '"that" clause']),
    ("denial_earlier_in_sentence",
     "Nobody on the review board, after a long discussion and several votes, "
     "agreed the cache loses acknowledged writes on restart.",
     CACHE, "verbatim_but_denial_earlier_in_sentence", ['"nobody"']),
    ("previous_sentence_denies_forward",
     "This is not how it works in the release we shipped to customers. The cache "
     "loses acknowledged writes on restart.",
     CACHE, "verbatim_but_previous_sentence_denies",
     ['"This is not how it works in the release we shipped to customers."', '"not"']),
    ("sentence_two_back_denies",
     "Of these, no more than five may be audio-visual items. How long is the loan "
     "period for the main collection? Books may be kept for three weeks.",
     "Books may be kept for three weeks [S1].",
     "verbatim_but_sentence_two_back_denies",
     ['"Of these, no more than five may be audio-visual items."', '"no"']),
    ("next_sentence_says_false",
     "The cache loses acknowledged writes on restart.\n\nThe story was fabricated.",
     CACHE, "verbatim_but_next_sentence_says_false",
     ['"The story was fabricated."', '"fabricated"']),
    ("previous_sentence_says_false",
     "The story was fabricated.\n\nThe cache loses acknowledged writes on restart.",
     CACHE, "verbatim_but_previous_sentence_says_false",
     ['"The story was fabricated."', '"fabricated"']),
    ("next_sentence_points_back",
     "A standard card allows up to twenty items at one time. Of these, no more "
     "than five may be audio-visual items such as DVDs.",
     "A standard card allows up to twenty items at one time [S1].",
     "verbatim_but_next_sentence_denies",
     ['"Of these, no more than five may be audio-visual items such as DVDs."']),
    ("under_disowning_list_label",
     "Common myths:\n- Restarts are slow and painful for every single operator\n"
     "- The cache loses acknowledged writes on restart",
     CACHE, "verbatim_but_under_disowning_label", ['label "Common myths:"']),
    ("under_denying_heading",
     "## Rumours debunked\n\nThe cache loses acknowledged writes on restart.",
     CACHE, "verbatim_but_under_denying_heading", ['heading "## Rumours debunked"']),
    ("after_scope_sentence",
     "None of the following is true.\n\nStaff left the building early that day."
     "\n\nThe cache loses acknowledged writes on restart.",
     CACHE, "verbatim_but_after_denial_of_what_follows",
     ['"None of the following is true."']),
    ("paragraph_falsity_statement",
     "The cache loses acknowledged writes on restart. Staff checked the logs "
     "twice. The whole account is fabricated.",
     CACHE, "verbatim_but_paragraph_has_falsity_statement",
     ['"The whole account is fabricated."', '"fabricated"']),
    ("negation_limited_in_source",
     "The patch has no known side effects in older kernels.",
     "The patch has no known side effects [S1].",
     "verbatim_but_negation_limited_in_source", ["in older kernels"]),
]


@pytest.mark.parametrize("case,source,draft,code,words", CASES,
                         ids=[c[0] for c in CASES])
def test_the_reason_names_the_rule_and_the_trigger(case, source, draft, code, words):
    row = _rows(source, draft)[0]
    assert row["verdict"] == "UNGROUNDED", row          # unchanged by this work
    assert row["support_diagnostic"] == code, row
    basis = row["evidence_basis"]
    assert "Found verbatim in S1, but" in basis, basis
    assert "so the match does not count" in basis, basis
    for w in words:
        assert w in basis, (w, basis)


def test_every_code_has_a_case_except_the_ones_named_here():
    """The previous-LINE rule is not separately reachable through the splitter
    in a short fixture (the line welds into the sentence and the same-sentence
    rule fires first); it is the only code without a case."""
    covered = {c[3] for c in CASES} | {"verbatim_but_source_sentence_negates_differently"}
    assert g.VERBATIM_REFUSAL_CODES - covered == {"verbatim_but_previous_line_denies"}


def test_a_split_piece_says_so_and_names_the_negation_it_lost():
    """d1 of the walkthrough: '..., and ... without restarting ...' is cut in
    two; the left piece lacks the source sentence's 'without'."""
    rows = _rows(
        "The default limit for a new group is four jobs, and the limit can be "
        "changed without restarting the scheduler.",
        "The default limit for a new group is four jobs, and the limit can be "
        "changed without restarting the scheduler [S1].")
    left, right = rows
    assert (left["verdict"], right["verdict"]) == ("UNGROUNDED", "GROUNDED")
    assert left["support_diagnostic"] == "verbatim_but_source_sentence_negates_differently"
    basis = left["evidence_basis"]
    assert '"without restarting"' in basis, basis
    assert "one piece of your sentence" in basis, basis
    assert "without restarting the scheduler [S1]." in basis, basis
    # A GROUNDED row is not touched.
    assert "Found verbatim" not in right["evidence_basis"]


def test_an_invented_split_piece_gets_only_the_split_note():
    rows = _rows("The council approved the parking study in May.",
                 "The mayor vetoed the parking study and promised a lawsuit [S1].")
    assert [r["verdict"] for r in rows] == ["UNGROUNDED", "UNGROUNDED"]
    for r in rows:
        assert "Found verbatim" not in r["evidence_basis"]
        assert "one piece of your sentence" in r["evidence_basis"]
        assert r["support_diagnostic"] not in g.VERBATIM_REFUSAL_CODES


def test_a_copied_percent_figure_says_the_unit_word_is_not_read():
    row = _rows("Customer churn fell to 3.1 percent in the second quarter.",
                "Customer churn fell to 3.1 percent in the second quarter [S1].")[0]
    assert row["verdict"] == "UNVERIFIED_NUMBER"
    assert '"3.1" is followed by the word "percent"' in row["evidence_basis"]


def test_retained_appendix_carries_the_same_reason():
    claims = [g.classify(c) for c in g.decompose(
        "A standard card allows up to twenty items at one time [S1].")]
    rep = g.score_report(claims, {"S1": _src(
        "A standard card allows up to twenty items at one time. Of these, no "
        "more than five may be audio-visual items such as DVDs.")})
    assert "Found verbatim in S1" in rep["per_claim"][0]["evidence_basis"]
    assert rep["retained_appendix"][0]["evidence_basis"] == rep["per_claim"][0]["evidence_basis"]


def test_explain_report_gives_the_verbatim_hint_not_copy_the_sentence():
    row = _rows(*CASES[0][1:3])[0]
    text = er.render({"gate": "FAIL", "grounding_score": 0.0, "per_claim": [row]})
    assert "Copying it again will not help" in " ".join(text.split())
    assert "Replace the claim with the source's own sentence" not in " ".join(text.split())


def test_explain_report_codes_equal_the_engine_codes():
    assert er.VERBATIM_REFUSAL_CODES == g.VERBATIM_REFUSAL_CODES


def test_no_verdict_path_reads_the_refusal_display():
    """Display must never become decision (D-34), asserted over the AST."""
    forbidden = {"verbatim_refusal", "VerbatimRefusal", "_occurrence_refusal",
                 "_denial_trigger", "unread_unit_note", "split_from",
                 "VERBATIM_REFUSAL_CODES", "paragraph_denied", "heading_denied",
                 "sentence_index"}
    for name in ("ground", "t1_verbatim", "_claim_contained_verbatim",
                 "_contained_with_matching_polarity", "_anchor_sentence_covers",
                 "_unit_denied", "_unit_denial_reason", "numeric_ok",
                 "spelled_quantity_ok", "classify", "check_absence",
                 "_absence_chain", "ground_relational"):
        tree = ast.parse(textwrap.dedent(inspect.getsource(getattr(g, name))))
        used = {n.id for n in ast.walk(tree) if isinstance(n, ast.Name)} | {
            n.attr for n in ast.walk(tree) if isinstance(n, ast.Attribute)}
        if name == "classify":
            # classify COPIES split_from onto the classified Claim and nothing
            # else: its only appearance is the keyword `split_from=claim.split_from`.
            uses = [n for n in ast.walk(tree)
                    if isinstance(n, ast.Attribute) and n.attr == "split_from"]
            kws = [k for k in ast.walk(tree)
                   if isinstance(k, ast.keyword) and k.arg == "split_from"]
            assert len(uses) == 1 and len(kws) == 1 and kws[0].value is uses[0], name
            used = used - {"split_from"}
        assert not used & forbidden, (name, used & forbidden)


def test_split_from_does_not_change_claim_equality():
    a = g.Claim(0, "x [S1].", g.ClaimKind.FACTUAL, ("[S1]",), ())
    b = g.Claim(0, "x [S1].", g.ClaimKind.FACTUAL, ("[S1]",), (), split_from="y")
    assert a == b and hash(a) == hash(b)
