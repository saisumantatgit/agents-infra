"""J-19 / OI-MOAT-27 — factivity decides, and the subject does not.

Approved by Sai 2026-09-12. This is the first rule in the project keyed on a
WHITELIST rather than a blacklist, and that inversion is the whole point.

Every moat rule that has failed here was a blacklist over a class the attacker
draws from: a token-count floor (round 3, killed by a five-token fabrication),
its capitalisation replacement (round 4, killed by the Shift key),
`_header_asserts` (a noun that does not end in "s"), `_span_is_hedged` (an
apostrophe), `_propagate_across_semicolon` (one keystroke). The defect is not
surface properties — it is putting the attacker on the enumerating side.

A factive verb PRESUPPOSES its complement, so `shown` may ground and `argued`
may not. Unlisted verbs REFUSE, which is why `posit` (S6) fails without being
enumerated anywhere. And the attacker cannot set it without giving up the
attack: to ground a mined span he must find a source whose verb asserts the
claim, at which point grounding it is correct behaviour.

SCOPE, STATED RATHER THAN IMPLIED: this closes the `that`-COMPLEMENT family
only — c1, c2, c4 of the round-7 tripwires. The zero-complementizer complement
(c3) and the post-span retraction (c5) are different mechanisms and remain open
in `test_moat_r7_open.py`. The solo gate caught an earlier version of this work
silently narrowing its own claim; the scope line is here so that cannot recur.
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
STORE = str(Path(__file__).parent / "fixtures" / "store_factive.jsonl")

CLAIM = "Redis loses data on restart"


def _verdict(tmp_path: Path, source_id: str) -> str:
    draft = tmp_path / "draft.md"
    draft.write_text(f"{CLAIM} [{source_id}].\n", encoding="utf-8")
    env = {**os.environ, "PYTHONPATH": str(REPO_ROOT)}
    out = subprocess.run(
        [sys.executable, GROUND_CHECK, "--draft", str(draft), "--store", STORE, "--json"],
        capture_output=True, text=True, env=env,
    )
    assert out.stdout, f"gate produced no stdout.\nstderr: {out.stderr}"
    scored = [c for c in json.loads(out.stdout)["per_claim"] if c["kind"] != "NON_CLAIM"]
    assert len(scored) == 1, scored
    return scored[0]["verdict"]


# The subject-swap control. Rows 1-4 are the experiment that decided this rule:
# hold the claim and the sentence shape constant, swap ONLY the subject, and the
# endorsement does not move. Swap only the verb, and it does.
FACTIVITY = [
    pytest.param("S1", "UNGROUNDED", id="critics-ARGUED-that"),
    pytest.param("S2", "GROUNDED", id="our-benchmark-SHOWN-that"),
    pytest.param("S3", "GROUNDED", id="critics-SHOWN-that--subject-swapped"),
    pytest.param("S4", "UNGROUNDED", id="our-benchmark-ARGUED-that--subject-swapped"),
    pytest.param("S5", "UNGROUNDED", id="critics-HAVENT-shown-that--negated-factive"),
    pytest.param("S6", "UNGROUNDED", id="vendors-POSIT-that--verb-not-in-any-list"),
    pytest.param("S7", "GROUNDED", id="no-complementizer-plain-adverbial"),
]


@pytest.mark.parametrize("source_id,expected", FACTIVITY)
def test_factivity_decides_not_the_subject(
    tmp_path: Path, source_id: str, expected: str
) -> None:
    assert _verdict(tmp_path, source_id) == expected


def test_negated_factive_needs_the_tokenizer_repair(tmp_path: Path) -> None:
    """S5 is the reason J-20 had to land before J-19, pinned as a fact.

    "Critics haven't shown that P" is a NEGATED factive. Before
    _expand_negation_contractions, "haven't" tokenized to ["haven","t"] and the
    negation was invisible — so the whitelist alone would have GROUNDED it,
    widening the very hole it was built to close. Neither fix is sufficient
    alone, and the order was not a preference.
    """
    from scripts.ground_check import _tokenize  # noqa: PLC0415

    assert "not" in _tokenize("Critics haven't shown that Redis loses data"), (
        "the tokenizer no longer expands contracted negations; J-19's negation "
        "conjunct is now blind and S5 will silently start grounding"
    )
    assert _verdict(tmp_path, "S5") == "UNGROUNDED"


def test_unlisted_verb_refuses_rather_than_grounds(tmp_path: Path) -> None:
    """The polarity, asserted directly rather than inferred from S6's verdict.

    `posit` appears in no list in the module. Under a blacklist it would have
    grounded; under the whitelist it refuses. If this ever inverts, the rule has
    been rewritten as a blacklist and the class is open again.
    """
    from scripts.ground_check import _FACTIVE_VERBS, _SPAN_HEDGE_TOKENS  # noqa: PLC0415

    assert "posit" not in _FACTIVE_VERBS and "posit" not in _SPAN_HEDGE_TOKENS
    assert _verdict(tmp_path, "S6") == "UNGROUNDED"
