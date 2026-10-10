"""Round 7's OPEN findings — tripwired and counted, deliberately not fixed.

Round 7 (2026-09-12) attacked the three control paths the D-15…D-20 cohort
added upstream of the tiers, and found ~22 wrongful PASSes over 11 mechanisms.
TWO were fixed the same night: OI-MOAT-26 (NFKC manufacturing comment
delimiters — it certified the OPPOSITE of what the author wrote) and the
SyntaxWarning. Everything else is here, open, strict-xfailed and counted.

WHY NOT FIX THEM ALL. Round 1 closed four holes; round 2 found fourteen
wrongful PASSes evading those very fixes; round 3 found seventeen more, two of
them evading fixes landed hours earlier the same day. A narrow fix has closed
the fixture it was written against and left the class open EVERY time. Shipping
eleven more narrow rules into the moat overnight, with no adversarial round
against them, is that same failure scheduled in advance. An open hole with a
tripwire is honest; a closed fixture with an open class is not.

THE META-FINDING. Five of these are the SAME law, broken five ways — CLAUDE.md's
"never key a moat rule on a surface property the author controls":

    round 3   a >= 6 content-token floor      killed by a 5-token fabrication
    round 4   its proper-noun replacement     killed by the Shift key
    round 7   _header_asserts                 killed by a noun not ending in "s"
    round 7   _span_is_hedged                 killed by an apostrophe (OI-MOAT-25)
    round 7   _propagate_across_semicolon     flipped by one keystroke, ";" vs "."

Length, capitalisation, spelling, punctuation. Every one of them is set by
whoever writes the draft. The pattern is not that these particular rules were
badly chosen — it is that a rule reading a surface property is the wrong SHAPE
of rule for a moat, and the project keeps rediscovering that one instrument at
a time.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
GROUND_CHECK = str(REPO_ROOT / "scripts" / "ground_check.py")
STORE = str(Path(__file__).parent / "fixtures" / "store_r7.jsonl")


def _gate(tmp_path: Path, draft_text: str) -> dict:
    draft = tmp_path / "draft.md"
    draft.write_text(draft_text, encoding="utf-8")
    env = {**os.environ, "PYTHONPATH": str(REPO_ROOT)}
    result = subprocess.run(
        [sys.executable, GROUND_CHECK, "--draft", str(draft), "--store", STORE, "--json"],
        capture_output=True, text=True, env=env,
    )
    assert result.stdout, f"gate produced no stdout.\nstderr: {result.stderr}"
    return json.loads(result.stdout)


def _scored(report: dict) -> list[dict]:
    return [c for c in report["per_claim"] if c["kind"] != "NON_CLAIM"]


def _only_verdict(report: dict) -> str:
    scored = _scored(report)
    assert len(scored) == 1, f"expected one scored claim, got {scored}"
    return scored[0]["verdict"]


# ---------------------------------------------------------------------------
# PATH C — the quote-mining guard. Five mechanisms, one unsound premise.
#
# _span_is_hedged is a bag-of-tokens test over a FIXED 5-token window before the
# span. The attacker chooses the verb, the distance, the spelling and the
# direction, so every one of those is his to set.
#
# The constraint that rules out the easy repairs is test_honest_attribution_
# still_grounds below: S3 (attack) and S4 (honest) are SYNTACTICALLY IDENTICAL
# -- both a "that"-complement of a reporting verb, both well past 5 tokens. They
# differ only in whether the author endorses the attributing subject ("Critics"
# vs "our own benchmark"), which is a semantic judgment no deterministic rule
# reads off the text. A wider window, a longer token list and a matrix-clause
# rule each fail on that pair. See docs/plans/reports/RED-TEAM-R7-2026-09-12.md.
# ---------------------------------------------------------------------------

# CLOSED 2026-09-12 by J-19 (factive whitelist). These three were `that`-
# complements of a non-factive verb, and they XPASSED when the rule landed.
MINED_CLOSED = [
    pytest.param("Redis loses data on restart [S3].\n",
                 id="c1-hedge-beyond-the-5-token-lookback"),
    pytest.param("The scheduler starves low-priority jobs [S5].\n",
                 id="c2-reporting-verb-not-in-the-token-list"),
    pytest.param("The gateway drops every packet [S8].\n",
                 id="c4-hedge-carried-by-structure-not-a-token"),
]

# STILL OPEN. Neither has a complementizer, so J-19 does not reach them, and
# saying so here is the point — the solo gate caught an earlier version of this
# work presenting a `that`-scoped rule as closing the whole class.
MINED_OPEN = [
    pytest.param("The array rebuilds in place without downtime [S6].\n",
                 id="c3-zero-complementizer-complement-cyrillic-confusable"),
    pytest.param("The proxy terminates TLS at the edge [S7].\n",
                 id="c5-retraction-AFTER-the-span-never-inspected"),
]


@pytest.mark.parametrize("draft", MINED_CLOSED)
def test_mined_that_complement_does_not_ground(tmp_path: Path, draft: str) -> None:
    """Closed by J-19. Permanent guards now, not tripwires."""
    assert _only_verdict(_gate(tmp_path, draft)) != "GROUNDED"


@pytest.mark.xfail(
    strict=True,
    reason="OI-MOAT-27 PARTIALLY OPEN: J-19's factive whitelist is scoped to "
    "`that`-complements. c3 is a zero-complementizer complement ('The vendor "
    "claims the array rebuilds …') and c5 is a retraction AFTER the span "
    "('…, which is simply not the case'), which no prefix rule can see. "
    "Different mechanisms, still Error-B, still counted.",
)
@pytest.mark.parametrize("draft", MINED_OPEN)
def test_mined_span_must_not_ground(tmp_path: Path, draft: str) -> None:
    assert _only_verdict(_gate(tmp_path, draft)) != "GROUNDED"


def test_honest_attribution_still_grounds(tmp_path: Path) -> None:
    """The mirror, and the reason no cheap repair works.

    S4 is the same shape as S3 — reporting verb, long adverbial, "that"-clause —
    but the attributor is the author's own benchmark. This MUST stay GROUNDED,
    or the repair has reintroduced OI-T2-01 ("I quoted your source exactly and
    it says ungrounded"). Any proposed fix for OI-MOAT-27 is measured here.
    """
    draft = "Redis loses data on restart [S4].\n"
    assert _only_verdict(_gate(tmp_path, draft)) == "GROUNDED"


# ---------------------------------------------------------------------------
# PATH B — T1's residual coverage is unordered SET MEMBERSHIP.
#
# The round-7 adversary's decisive control: citation propagation is NOT the
# hole. Propagation's output is exactly `left + " [Sx]"`, every downstream path
# strips markers before tokenizing, and the same clause cited DIRECTLY also
# passes. Propagation only removes the UNCITED blocker; it cannot certify
# anything a self-citation could not. This refuted the prediction recorded
# before the round ran, which had named the ";" discriminator as the likely
# Error-B. It is a real fidelity defect (one keystroke flips FAIL to PASS, and
# it crosses paragraph and list-item boundaries) but it moves no Error-B.
#
# The Error-B is in T1: the first 8 tokens are a verbatim n-gram, and the
# remaining content tokens need only APPEAR SOMEWHERE in the source. Set
# membership has no notion of polarity or attachment, so "disabled" sitting in
# the source licenses "with" in the claim. This is the RT4-03 argument-swap
# family, unclosed for MODIFIERS.
# ---------------------------------------------------------------------------


@pytest.mark.xfail(
    strict=True,
    reason="OI-MOAT-28 OPEN: T1's residual coverage is unordered set "
    "membership, so a modifier can be inverted while every token still appears "
    "in the source. S1 says AOF persistence was DISABLED; the claim asserts the "
    "figure was obtained WITH it. Same family as RT4-03 (argument swap), "
    "unclosed for modifiers.",
)
def test_inverted_modifier_must_not_ground(tmp_path: Path) -> None:
    draft = (
        "Redis handles 100K ops per second in our benchmark with AOF "
        "persistence [S1].\n"
    )
    assert _only_verdict(_gate(tmp_path, draft)) != "GROUNDED"


# ---------------------------------------------------------------------------
# PATH A — the decomposer removes text from the denominator.
#
# OI-MOAT-26 (NFKC-manufactured delimiters) was FIXED. These three are open.
# All three share one shape: a claim leaves the denominator, and a claim that
# is not scored cannot be flagged. CLAUDE.md's rule — every "I don't know" must
# point AWAY from PASS — is about verdicts; these are the same failure one
# level earlier, in what gets a verdict at all.
# ---------------------------------------------------------------------------


def test_stray_comment_opener_must_not_swallow_prose(tmp_path: Path) -> None:
    draft = (
        "The appliance ships with dual power supplies [S2].\n\n"
        "Use the `<!--` token to open a comment.\n\n"
        "MongoDB lost all data under sustained write load.\n\n"
        "<!-- reviewer note -->\n"
    )
    scored = " ".join(c["text"] for c in _scored(_gate(tmp_path, draft)))
    assert "MongoDB" in scored, (
        "the MongoDB sentence was not SCORED, so it could never be flagged"
    )
    # CLOSED 2026-09-12 (D-30): comments are no longer stripped inside code
    # spans, so a `<!--` a writer is TALKING ABOUT cannot open one. Permanent
    # guard now, not a tripwire.


def test_line_under_unpunctuated_header_is_still_scored(tmp_path: Path) -> None:
    draft = "### TODO\nMongoDB lost all data under load\n"
    assert _scored(_gate(tmp_path, draft)), "nothing was scored at all"


@pytest.mark.xfail(
    strict=True,
    reason="OI-MOAT-31 OPEN, AND DELIBERATELY NOT PATCHED (2026-09-12). "
    "_header_asserts asks 'is this an assertion?' and DEFAULTS TO NO, so a "
    "header escapes scoring whenever the test is inconclusive — a default "
    "pointing toward PASS. '### Redis lost all data' is caught only because "
    "'Redis' ends in 's' and trips a verb-suffix test; '### MongoDB lost all "
    "data' is not, because 'lost' is an irregular past form no suffix rule "
    "reaches. "
    "The available narrow fixes are all the shape this project has watched fail "
    "five times: a list of irregular verbs is a blacklist over an open class, "
    "and a content-word count is a length rule round 3 already killed. "
    "The SOUND fix inverts the default — score headers, and group uncited ones "
    "separately in the report, exactly the J-15 remedy — but that changes the "
    "Error-A/Error-B trade-off and is Escalation #1 clause 1. Sai's, not mine.",
)
def test_header_assertion_is_not_keyed_on_spelling(tmp_path: Path) -> None:
    assert _scored(_gate(tmp_path, "### MongoDB lost all data\n")), (
        "the assertion in this header was not scored, while the same header "
        "with a subject ending in 's' is"
    )


def test_header_assertion_with_trailing_s_subject_is_scored(tmp_path: Path) -> None:
    """The control that makes the above a SPELLING dependency and not a guess."""
    assert _scored(_gate(tmp_path, "### Redis lost all data\n"))


def test_cited_zero_content_span_stays_scored(tmp_path: Path) -> None:
    report = _gate(tmp_path, "It is not [S1].\n")
    assert _scored(report), "a cited span left the denominator entirely"
