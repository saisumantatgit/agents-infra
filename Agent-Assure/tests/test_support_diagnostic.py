"""J-74 — the contradiction signal ships as a MEASUREMENT, never a verdict.

WHAT THIS IS. Round 14 showed the gate certifies claims their own cited source
denies (R14-01, R14-04): T1's span anchors in the claim's long subject, and
`_span_is_hedged` reads only the five tokens BEFORE the span, so a denial after
the subject is invisible. Measured: the same denial moved before the subject
refuses the claim; left after it, the claim certifies at PASS 100.0.

The repair is J-70 and it is Sai's (Escalation #1) — the blunt version was
priced at Error-A 0.400 -> 0.560 and broke 5 of 7 honest drafts, including a
verbatim quotation of the source. So ADR-008 ships the SIGNAL instead of a
verdict: a deterministic, sentence-scoped report that the cited sentence may not
assert the claim.

WHY IT MUST NEVER BECOME A VERDICT. It approximates entailment, and SOTA
entailment is 65-75% balanced accuracy (MiniCheck-FT5 74.7, GPT-4 75.3 on
LLM-AggreFact, EMNLP 2024). A token scan is cruder. **Measured fire rate on the
n=52 gold corpus: 26.7% of claims the gate PASSES, and 25.9% of claims a human
LABELLED grounded.** Roughly one in four is a false alarm. That is tolerable for
an advisory that refuses nothing and intolerable for a gate — and it is
PUBLISHED rather than tuned away, because tuning a signal nobody has
re-validated is precisely how 2026-10-02 produced two Error-Bs.

THE GUARD IS STRUCTURAL, NOT CAREFUL. `test_no_verdict_path_consults_the_support
_diagnostic` is the load-bearing test in this file. Care has already failed three
times in this module in three days (J-44's stem D-69, the fall-through D-76, the
withdrawn hedge scan), so the property is asserted over the AST rather than
trusted to review.
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


def _src(source_id: str, text: str, *, full_text_source: str = "verbatim"):
    return g.RetrievedSource(
        source_id=source_id, url=None, file_path="/tmp/x",
        fetched_at="2026-10-03T00:00:00Z", tool="Read", content_sha256="sha",
        text=text, full_text_source=full_text_source, captured_via="hook",
        query_provenance="q",
    )


_AUDIT_CLAIM = ("The quarterly audit of custodial reconciliation controls at the "
                "Frankfurt desk identified material weaknesses [S1].")


def _classified(text: str):
    """classify() takes a Claim, not a str — decompose() is what makes one."""
    return g.classify(g.decompose(text)[0])


def _diag(claim_text: str, source_text: str, **kw) -> str:
    return g.support_diagnostic(
        _classified(claim_text), {"S1": _src("S1", source_text, **kw)})


def test_it_fires_on_the_round_14_denial_that_still_certifies():
    """R14-04 h1: this exact pair is GROUNDED at PASS 100.0 and must be FLAGGED."""
    assert _diag(
        _AUDIT_CLAIM,
        "The quarterly audit of custodial reconciliation controls at the "
        "Frankfurt desk identified no material weaknesses whatsoever.",
    ) == g.SUPPORT_SENTENCE_MAY_NOT_ASSERT


def test_it_fires_on_a_withdrawn_finding():
    assert _diag(
        _AUDIT_CLAIM,
        "The quarterly audit of custodial reconciliation controls at the "
        "Frankfurt desk identified material weaknesses, contrary to what the "
        "record shows; that finding was withdrawn.",
    ) == g.SUPPORT_SENTENCE_MAY_NOT_ASSERT


def test_it_does_NOT_fire_on_a_plainly_asserting_source():
    """THE POSITIVE CONTROL. Without it, `return FLAGGED` passes everything above."""
    assert _diag(
        _AUDIT_CLAIM,
        "The quarterly audit of custodial reconciliation controls at the "
        "Frankfurt desk identified material weaknesses in three accounts.",
    ) == g.SUPPORT_NO_HEDGE_FOUND


def test_a_summary_only_source_reports_no_verbatim_source():
    """A summary can never ground a claim, so it cannot support one either."""
    assert _diag(_AUDIT_CLAIM, "The audit found problems.",
                 full_text_source="haiku_summary") == g.SUPPORT_NO_CITED_SOURCE


def test_an_uncited_claim_reports_no_verbatim_source():
    claim = _classified("The device sold 250,000 units in its first month.")
    assert g.support_diagnostic(claim, {}) == g.SUPPORT_NO_CITED_SOURCE


def test_it_is_emitted_for_EVERY_claim_not_gated_on_kind():
    """R14-01's lesson: a check gated on a classifier branch is routable.

    `causes` classifies RELATIONAL and `triggered` does not, so a kind-gated
    diagnostic would vanish on the one-word delta that round 14 exploited.
    """
    store = {"S1": _src("S1", "The review found no evidence that the migration "
                              "triggered widespread customer refunds.")}
    for verb in ("causes", "triggered"):
        draft = (f"The 2019 federal review of interbank settlement latency "
                 f"across the eurozone {verb} widespread customer refunds [S1].")
        claims = [g.classify(c) for c in g.decompose(draft)]
        report = g.score_report(claims, store)
        for entry in report["per_claim"]:
            assert "support_diagnostic" in entry, (verb, entry)


def test_the_diagnostic_is_deterministic():
    """Same bytes, same answer, forever — the product's whole premise."""
    args = (_AUDIT_CLAIM, "The audit identified no material weaknesses at all.")
    assert _diag(*args) == _diag(*args) == _diag(*args)


def test_it_does_not_mutate_its_inputs():
    claim = _classified(_AUDIT_CLAIM)
    store = {"S1": _src("S1", "The audit identified material weaknesses.")}
    before = repr(claim), repr(store)
    g.support_diagnostic(claim, store)
    assert (repr(claim), repr(store)) == before


def test_no_verdict_path_consults_the_support_diagnostic():
    """THE LOAD-BEARING TEST. Display must never become decision (D-34).

    Asserted over the AST, not the source text: a substring guard cannot tell a
    call from a comment, and on 2026-10-01 that exact confusion failed a test
    for explaining itself in prose. If this goes red, a 26.7%-false-alarm token
    scan has started deciding verdicts.
    """
    for name in ("ground", "check_absence", "ground_relational", "classify",
                 "numeric_ok", "spelled_quantity_ok"):
        tree = ast.parse(textwrap.dedent(inspect.getsource(getattr(g, name))))
        referenced = {n.id for n in ast.walk(tree) if isinstance(n, ast.Name)} | {
            n.attr for n in ast.walk(tree) if isinstance(n, ast.Attribute)}
        for forbidden in ("support_diagnostic", "_most_overlapping_sentence",
                          "SUPPORT_SENTENCE_MAY_NOT_ASSERT"):
            assert forbidden not in referenced, (
                f"{name} consults {forbidden} — a diagnostic has become a verdict")


# ---------------------------------------------------------------------------
# J-79 (2026-10-03) — shared vocabulary is not a hedge.
# ---------------------------------------------------------------------------

def test_a_hedge_word_the_CLAIM_also_uses_does_not_fire():
    """`per` is a hedge token (for "per the vendor"), so every claim about
    "operations per second" matched against a source about "operations per
    second" fired — for the wrong reason, inflating the published rate.

    Measured 4/15 → 0/15 false alarms on claims the gate passes, with recall on
    the 14-vector denial set unchanged at 7/14.
    """
    assert _diag(
        "Redis handles 100K operations per second [S1].",
        "Redis handles 100K operations per second in sustained testing.",
    ) == g.SUPPORT_NO_HEDGE_FOUND


def test_a_hedge_the_claim_does_NOT_use_still_fires():
    """POSITIVE CONTROL — without it, the narrowing above is indistinguishable
    from switching the diagnostic off."""
    assert _diag(
        "Redis handles 100K operations per second [S1].",
        "The vendor claims Redis handles 100K operations per second.",
    ) == g.SUPPORT_SENTENCE_MAY_NOT_ASSERT


def test_the_VERDICT_lexicon_is_untouched_by_this_narrowing():
    """`_SPAN_HEDGE_TOKENS` also feeds `_span_is_hedged`, which is in the
    verdict path. Removing a token there would make T1 certify MORE —
    PASS-enabling, Escalation #1. This pins that the shared set still holds the
    words, so a later 'cleanup' of the lexicon has to confront the invariant.
    """
    for token in ("per", "claim", "not", "no", "according"):
        assert token in g._SPAN_HEDGE_TOKENS, token
