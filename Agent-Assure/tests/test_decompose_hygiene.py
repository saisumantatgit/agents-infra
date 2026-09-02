"""OI-DEC-03/-04 — what counts as "the draft" before anything is scored.

Found 2026-09-03 by running the gate over 10 chapters of real book prose
(cpc-book). ~30% of scored claims there were questions or fragments; tracing
them found two decomposition faults that had never appeared in the 52-row
calibration corpus, because every row of that corpus is a clean single sentence
written by hand for the purpose.

OI-DEC-03 — HTML COMMENTS ARE SCORED AS CLAIMS.
An authoring comment is not prose. It is not rendered, not published and not
read. Yet `<!-- [Sn] anchors are working-draft verification tags (store:
.assure/evidence-store-issues.jsonl) — strip at export. -->` decomposed into
scored FACTUAL claims, and the bare `-->` became one too. A gate that flags a
writer's own TODO notes as ungrounded claims is not measuring the document.

OI-DEC-04 — THE CONJUNCTION SPLITTER LEAVES TRAILING PUNCTUATION.
"The written statement is in, and the case is now a stack of paragraphs" splits
at " and ", and the left clause keeps its comma: "The written statement is in,".
That is a COMPLETE clause wearing the splitter's litter. It changes no verdict
— punctuation is stripped before tokenizing — but it is what a reader sees in
the report, and it is what made a third of real-prose claims look like
sentence fragments when they were not.
"""

from __future__ import annotations

from scripts.ground_check import classify, decompose


def _texts(draft: str) -> list[str]:
    return [c.text for c in decompose(draft)]


# --- OI-DEC-03: comments are not prose --------------------------------------

def test_html_comment_block_is_not_decomposed_into_claims() -> None:
    draft = (
        "<!--\nInternal note: [Sn] anchors are working-draft verification tags\n"
        "(store: .assure/evidence-store.jsonl) - strip at export.\nNot legal advice.\n-->\n\n"
        "Redis handles 100K ops per second [S1].\n"
    )
    texts = _texts(draft)
    assert texts == ["Redis handles 100K ops per second [S1]."], (
        f"comment content leaked into the claim list: {texts}"
    )


def test_bare_comment_terminator_is_not_a_claim() -> None:
    """The literal '-->' was classified FACTUAL and scored."""
    assert not any("-->" in t for t in _texts("<!-- note -->\n\nA real sentence here [S1].\n"))


def test_inline_comment_does_not_swallow_surrounding_prose() -> None:
    """Stripping must remove the comment and NOTHING else."""
    draft = "Redis is fast [S1]. <!-- check this --> PostgreSQL is durable [S2].\n"
    texts = _texts(draft)
    assert any("Redis is fast" in t for t in texts), texts
    assert any("PostgreSQL is durable" in t for t in texts), texts
    assert not any("check this" in t for t in texts), texts


def test_unclosed_comment_is_left_alone() -> None:
    """Fail-closed: an unterminated '<!--' is not a comment we can delimit, so
    the text stays scored rather than silently vanishing from the denominator.
    Stripping to end-of-document would let a single stray '<!--' delete every
    claim after it."""
    draft = "<!-- oops never closed\nRedis handles 100K ops per second [S1].\n"
    assert any("Redis handles" in t for t in _texts(draft)), _texts(draft)


# --- OI-DEC-04: the splitter must not leave its litter ----------------------

def test_conjunction_split_strips_trailing_comma() -> None:
    claims = _texts("The written statement is in, and the case is now contested.")
    assert claims[0] == "The written statement is in", repr(claims[0])


def test_conjunction_split_strips_trailing_colon_and_dash() -> None:
    for draft, expected in [
        ("This stage compresses it: each side can force cards onto the table, "
         "and concessions get locked in.",
         "This stage compresses it: each side can force cards onto the table"),
    ]:
        assert _texts(draft)[0] == expected, repr(_texts(draft)[0])


def test_citation_still_propagates_after_punctuation_strip() -> None:
    """OI-DEC-01 must survive: stripping the comma must not strip the citation
    that was propagated onto the left clause."""
    claims = [classify(c) for c in decompose(
        "The written statement is in, and the case is now contested [S1]."
    )]
    assert claims[0].citations == ("[S1]",), claims[0]


# --- OI-DEC-05: a span with NO content words cannot be a claim --------------

def test_markdown_horizontal_rule_is_not_a_claim() -> None:
    """'---' was classified FACTUAL and scored UNGROUNDED.

    The rule is ZERO content tokens, not "few". Round 3 killed a
    '>= 6 content tokens' floor because an attacker simply wrote a 5-token
    fabrication — any positive threshold is a line to step under. Zero is not a
    threshold of that kind: a span with no content words carries no predicate
    and no subject, so there is nothing to assert and nothing to smuggle. It is
    a property of the span, not a budget the author can spend up to.
    """
    for markup in ("---", "***", "___", "|---|---|"):
        kinds = [classify(c).kind.value for c in decompose(f"{markup}\n")]
        assert all(k == "NON_CLAIM" for k in kinds), f"{markup!r} -> {kinds}"


def test_content_bearing_short_sentence_is_still_scored() -> None:
    """The guard on the rule above: 'Silence is a decision.' is short, real, and
    must stay in the denominator. A zero-content rule that catches this has
    become a length rule, which is the thing that keeps failing."""
    kinds = [classify(c).kind.value for c in decompose("Silence is a decision.\n")]
    assert kinds == ["FACTUAL"], kinds


def test_five_token_fabrication_still_scored() -> None:
    """Round 3's actual attack, re-run against the zero-content rule."""
    kinds = [classify(c).kind.value for c in decompose("Redis outperforms every rival database.\n")]
    assert kinds == ["FACTUAL"], kinds


# --- OI-DEC-06: citation stripping must not leave orphaned punctuation ------

def test_citation_strip_does_not_leave_floating_period() -> None:
    """'the guarantee was invoked [S3].' rendered as 'the guarantee was invoked .'

    Cosmetic — no verdict moves, since punctuation is dropped before tokenizing
    — but the report quotes claim text back to the user, and text the user never
    wrote undermines the one thing the report is for."""
    from scripts.ground_check import _strip_citations
    assert _strip_citations("the guarantee was invoked [S3].").strip() == (
        "the guarantee was invoked."
    )
    assert _strip_citations("Redis is fast [S1] and durable [S2].").strip() == (
        "Redis is fast and durable."
    )
