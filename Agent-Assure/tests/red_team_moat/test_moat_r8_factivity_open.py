"""Round 8, lane A — factivity/negation findings NOT closed by J-19/J-20.

R8A-01 and R8A-02 (the >=8-token span path bypassing the endorsement guards
entirely) were fixed the same day and are permanent guards now, in
`test_moat_r8_span_endorsement.py`. Everything below is the report's own
"still open" list: R8A-03 through R8A-07, all Error-B (a fabrication or an
explicit denial certified GROUNDED). R8A-08 (ERROR-A: `can't`/`cannot`
asymmetry) is out of scope for this file — it is recoverable and does not
manufacture a wrongful PASS.

Every draft/store pair below is copied verbatim from
docs/plans/reports/R8-A-factivity-negation.md — not paraphrased — because the
report's own point is that the mechanism is fragile to exact wording (a
lookback window, a token blacklist, a regex missing four apostrophes), and a
paraphrase could accidentally dodge the very bug being recorded.
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


def _gate(tmp_path: Path, draft_text: str, source_text: str) -> dict:
    store = tmp_path / "s.jsonl"
    store.write_text(json.dumps({
        "source_id": "S1", "url": None, "file_path": "/tmp/a",
        "fetched_at": "2026-09-12T00:00:00Z", "tool": "Read",
        "content_sha256": "a" * 64, "text": source_text,
        "full_text_source": "verbatim", "captured_via": "hook",
        "query_provenance": "redis durability",
    }) + "\n", encoding="utf-8")
    draft = tmp_path / "d.md"
    draft.write_text(draft_text, encoding="utf-8")
    env = {**os.environ, "PYTHONPATH": str(REPO_ROOT)}
    result = subprocess.run(
        [sys.executable, GROUND_CHECK, "--draft", str(draft), "--store", str(store), "--json"],
        capture_output=True, text=True, env=env,
    )
    assert result.stdout, f"gate produced no stdout.\nstderr: {result.stderr}"
    return json.loads(result.stdout)


def _scored_verdict(report: dict) -> str:
    scored = [c for c in report["per_claim"] if c["kind"] != "NON_CLAIM"]
    assert len(scored) == 1, f"expected one scored claim, got {scored}"
    return scored[0]["verdict"]


# ---------------------------------------------------------------------------
# R8A-03 — the factive prefix window is the WHOLE document, not the governing
# clause: one factive verb ANYWHERE before the complementizer licenses it.
# ---------------------------------------------------------------------------

@pytest.mark.xfail(
    strict=True,
    reason="R8A-03 OPEN: _span_under_nonfactive_complement scans the ENTIRE "
    "prefix of the source for a factive verb, not the clause governing this "
    "complement. An unrelated earlier sentence using a factive verb licenses "
    "a later non-factive speculation.",
)
def test_unrelated_earlier_factive_verb_must_not_license_later_speculation(tmp_path: Path) -> None:
    draft = "Redis loses data [S1].\n"
    source = ("Our benchmark showed that the cluster stayed stable. "
              "A blogger speculated that Redis loses data.")
    assert _scored_verdict(_gate(tmp_path, draft, source)) != "GROUNDED"


def test_control_same_claim_without_the_unrelated_sentence_is_refused(tmp_path: Path) -> None:
    """Control: delete only the unrelated first sentence — verdict correctly flips.

    This is what proves R8A-03 is a document-wide scan, not a per-claim
    endorsement judgment: removing text that has nothing to do with the
    complement changes the verdict on the complement.
    """
    draft = "Redis loses data [S1].\n"
    source = "A blogger speculated that Redis loses data."
    assert _scored_verdict(_gate(tmp_path, draft, source)) != "GROUNDED"


@pytest.mark.xfail(
    strict=True,
    reason="R8A-03 OPEN (nested instance): an outer factive verb ('showed') "
    "governing one clause licenses an inner non-factive verb's ('posits') "
    "complement, because the whitelist reads the outer verb and endorses the "
    "inner complement.",
)
def test_nested_factive_outer_clause_must_not_license_inner_speculative_complement(tmp_path: Path) -> None:
    draft = "Redis loses acknowledged data [S1].\n"
    source = "Smith showed that one blogger posits that Redis loses acknowledged data."
    assert _scored_verdict(_gate(tmp_path, draft, source)) != "GROUNDED"


# ---------------------------------------------------------------------------
# R8A-04 — nouns homographic with whitelisted factive verbs ("documents",
# "measures") satisfy the factivity test by bare token identity.
# ---------------------------------------------------------------------------

@pytest.mark.xfail(
    strict=True,
    reason="R8A-04 OPEN: the factive whitelist matches bare token identity "
    "with no part-of-speech constraint. The noun 'documents' (not the verb) "
    "anywhere in the prefix satisfies _FACTIVE_VERBS and licenses a later "
    "speculative complement.",
)
def test_homographic_noun_documents_must_not_license_speculation(tmp_path: Path) -> None:
    draft = "Redis loses data [S1].\n"
    source = "Internal documents circulated widely. One blogger posits that Redis loses data."
    assert _scored_verdict(_gate(tmp_path, draft, source)) != "GROUNDED"


@pytest.mark.xfail(
    strict=True,
    reason="R8A-04 OPEN (second instance): 'measures' as a plain noun "
    "('Security measures were tightened') is not the verb 'measures', but "
    "the whitelist cannot tell the difference.",
)
def test_homographic_noun_measures_must_not_license_speculation(tmp_path: Path) -> None:
    draft = "Redis loses data [S1].\n"
    source = "Security measures were tightened. One blogger posits that Redis loses data."
    assert _scored_verdict(_gate(tmp_path, draft, source)) != "GROUNDED"


# ---------------------------------------------------------------------------
# R8A-05 — the negation conjunct is a fixed 6-token blacklist
# ({not, no, never, nor, neither, without}); lexical negation ("failed to",
# "unable to", "nobody", "declined to") walks straight through a whitelisted
# factive verb.
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("source", [
    pytest.param(
        "The team failed to show that Redis loses acknowledged data.",
        id="failed-to-show",
    ),
    pytest.param(
        "Researchers were unable to demonstrate that Redis loses acknowledged data.",
        id="unable-to-demonstrate",
    ),
    pytest.param(
        "Nobody has established that Redis loses acknowledged data.",
        id="nobody-has-established",
    ),
    pytest.param(
        "The lab declined to confirm that Redis loses acknowledged data.",
        id="declined-to-confirm",
    ),
])
@pytest.mark.xfail(
    strict=True,
    reason="R8A-05 OPEN: _NEGATION_TOKENS is a fixed 6-token blacklist "
    "{not, no, never, nor, neither, without}. Lexical negation ('failed to', "
    "'unable to', 'nobody', 'declined to') combines with a whitelisted "
    "factive verb to produce an explicit NON-endorsement the gate reads as "
    "endorsement — the same proposition spelled 'No one' (containing the "
    "token 'no') is correctly refused.",
)
def test_lexical_negation_of_a_factive_verb_must_not_ground(tmp_path: Path, source: str) -> None:
    draft = "Redis loses acknowledged data [S1].\n"
    assert _scored_verdict(_gate(tmp_path, draft, source)) != "GROUNDED"


def test_control_no_one_spelling_is_correctly_refused(tmp_path: Path) -> None:
    """Control from the report: 'No one' (token 'no') is caught; 'Nobody' is not."""
    draft = "Redis loses acknowledged data [S1].\n"
    source = "No one has established that Redis loses acknowledged data."
    assert _scored_verdict(_gate(tmp_path, draft, source)) != "GROUNDED"


# ---------------------------------------------------------------------------
# R8A-06 — J-20's contraction regex covers two apostrophes (U+0027, U+2019);
# four more (U+2018, U+02BC, U+02B9, U+05F3) hide the negation entirely and
# invert the verdict on an explicit denial.
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("apostrophe", [
    pytest.param("‘", id="U+2018-left-single-quote"),
    pytest.param("ʼ", id="U+02BC-modifier-letter-apostrophe"),
    pytest.param("ʹ", id="U+02B9-modifier-letter-prime"),
    pytest.param("׳", id="U+05F3-hebrew-geresh"),
])
@pytest.mark.xfail(
    strict=True,
    reason="R8A-06 OPEN: _NEGATION_CONTRACTION_RE only enumerates U+0027 and "
    "U+2019 (NFKC folds U+FF07 in for free). U+2018/U+02BC/U+02B9/U+05F3 are "
    "untouched, so 'doesnXt' never expands to 'does not', _span_is_hedged "
    "sees an unhedged span, and the gate asserts the exact opposite of an "
    "explicit denial. U+2018 in particular is the left single quotation mark "
    "that word processors and CMSes emit routinely.",
)
def test_exotic_apostrophe_negation_must_not_ground(tmp_path: Path, apostrophe: str) -> None:
    draft = "Redis loses acknowledged data [S1].\n"
    source = f"The audit doesn{apostrophe}t show Redis loses acknowledged data."
    assert _scored_verdict(_gate(tmp_path, draft, source)) != "GROUNDED"


def test_control_standard_apostrophes_are_correctly_refused(tmp_path: Path) -> None:
    """Control: the two apostrophes J-20 DOES cover are refused correctly."""
    draft = "Redis loses acknowledged data [S1].\n"
    for apostrophe in ("'", "’"):
        source = f"The audit doesn{apostrophe}t show Redis loses acknowledged data."
        assert _scored_verdict(_gate(tmp_path, draft, source)) != "GROUNDED"


def test_honest_mirror_uncontracted_negation_still_refuses(tmp_path: Path) -> None:
    """The honest mirror: 'does show' (no negation at all) correctly GROUNDS,
    proving the exotic-apostrophe cases above are a false negative on the
    negation, not a general hedge-detection failure."""
    draft = "Redis loses acknowledged data [S1].\n"
    source = "The audit does show Redis loses acknowledged data."
    assert _scored_verdict(_gate(tmp_path, draft, source)) == "GROUNDED"


# ---------------------------------------------------------------------------
# R8A-07 — zero-complementizer and `how`-complement frames never reach the
# factivity test at all, because _COMPLEMENTIZERS = {"that"}.
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("source", [
    pytest.param(
        "One blogger posits Redis loses acknowledged data.",
        id="zero-complementizer",
    ),
    pytest.param(
        "One blogger theorised how Redis loses acknowledged data.",
        id="how-complement",
    ),
])
@pytest.mark.xfail(
    strict=True,
    reason="R8A-07 OPEN (confirmed open by the report's own J-19 design "
    "comment): _COMPLEMENTIZERS = {'that'} only, so a complement introduced "
    "by nothing at all, or by 'how', never reaches the factivity/hedge test "
    "and grounds unhedged whenever the reporting verb is also outside "
    "_SPAN_HEDGE_TOKENS.",
)
def test_non_that_complementizer_speculation_must_not_ground(tmp_path: Path, source: str) -> None:
    draft = "Redis loses acknowledged data [S1].\n"
    assert _scored_verdict(_gate(tmp_path, draft, source)) != "GROUNDED"
