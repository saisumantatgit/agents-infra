"""R40: fail-closed fixes for the RED-TEAM-R37 hole classes (H1-H8, H10, H11,
H12, H13, H14). Every case here is a fabrication shape that main ef3ae1f
certifies (gate PASS, claim GROUNDED or heading NON_CLAIM); after R40 each
must be refused. Proven red against unmodified ef3ae1f
(reports/R40-FIXES.md, PROVEN-RED section).

The hole classes R40 leaves open are pinned as strict xfails in
test_moat_r40_ceiling_tripwires.py; the honest shapes that must keep grounding
are in test_moat_r40_honest_controls.py."""
from __future__ import annotations

from pathlib import Path

import pytest

from tests.red_team_moat._h_helpers import CLAIM, TAIL, gate

S = CLAIM + "." + TAIL
F = " Staff left. Records were filed. "

ATTACK_SOURCES = {
    # H1: denial after the claim in the SAME sentence
    "h1_which_is_a_myth": CLAIM + ", which is a myth." + TAIL,
    "h1_paren_fabricated": CLAIM + " (fabricated)." + TAIL,
    "h1_dash_fabrication": CLAIM + " - a complete fabrication." + TAIL,
    "h1_semicolon_untrue": CLAIM + "; none of it is true." + TAIL,
    # H2: phrasal siblings of "made up", three sentences back
    "h2_cooked_up": "The account was cooked up." + F + S,
    "h2_dreamed_up": "The account was dreamed up." + F + S,
    "h2_trumped_up": "The whole account was trumped up." + F + S,
    "h2_makes_up_stories": "The tabloid makes up stories." + F + S,
    # H3: unlisted falsity words and inflections of listed ones
    "h3_fabricates": "The tabloid fabricates such stories." + F + S,
    "h3_fabricating": "The tabloid is fabricating it again." + F + S,
    "h3_falsified": "The account was falsified." + F + S,
    "h3_apocryphal": "The account is apocryphal." + F + S,
    "h3_invented_discourse_subject": "The account was invented." + F + S,
    "h3_is_invention": "Every line of it is invention." + F + S,
    "h3_misinformation": "The account is misinformation." + F + S,
    "h3_disinformation": "It is disinformation." + F + S,
    "h3_inaccurate": "The account is inaccurate." + F + S,
    "h3_all_lies": "It was all lies." + F + S,
    "h3_falsely_reported": "The tabloid falsely reported this." + F + S,
    # H4: event negation outside happen/true/occurred
    "h4_did_not_occur": "The tale I tell did not occur." + F + S,
    "h4_never_took_place": "It never took place." + F + S,
    "h4_none_of_it_real": "None of it is real." + F + S,
    # H5: "false" after a verdict verb, no copula
    "h5_called_it_false": "Reporters called it false." + F + S,
    # H6: next-sentence falsity in the new words
    "h6_next_invented": CLAIM + ". The story was invented.",
    "h6_next_cooked_up": CLAIM + ". The story was cooked up.",
    "h6_next_apocryphal": CLAIM + ". The story is apocryphal.",
    "h6_next_did_not_occur": CLAIM + ". The event did not occur.",
    # H7: look-alike and invisible characters inside a denial word
    "h7_latin_alpha": "The account was f\u0251bricated." + F + S,
    "h7_zero_width_space": "The account was fabri\u200bcated." + F + S,
    "h7_soft_hyphen": "The account was fabri\u00adcated." + F + S,
    "h7_dotless_i": "The account is f\u0131ctional." + F + S,
    "h7_word_joiner": "The account was fabri\u2060cated." + F + S,
    "h7_combining_grapheme_joiner": "The account was fabri\u034fcated." + F + S,
    "h7_small_capital_o": "The account is a h\u1d0fax." + F + S,
    # H8: forward-pointing denial of 13+ tokens on one line, same paragraph
    "h8_13_tokens_below_holds_up": "We checked each of the items below and not one of them holds up." + F + S,
    "h8_14_tokens_none_accurate": "None of the reports this page collected from the forums last winter is accurate." + F + S,
    "h8_follows_long_did_not_occur": "What follows in the rest of this short note from the forum did not occur." + F + S,
    # H10: a markdown denial heading's scope runs to the next heading of its level
    "h10_bare_word_line": "## Myths about the bank\n\nPeople talked. Some wrote. Others posted.\n\nMore\n\n" + S,
    "h10_connective_line": "## Myths about the bank\n\nPeople talked.\n\nAnd so\n\nStaff left. Records were filed. Reporters waited.\n\n" + S,
    "h10_deeper_subheading": "## Myths about the bank\n\nPeople talked.\n\n### The collapse\n\nStaff left. Records were filed. Reporters waited.\n\n" + S,
    # H11: heading label words that were excluded
    "h11_lies_heading": "## Lies the tabloids told\n\nPeople talked.\n\n" + S,
    "h11_wrong_claims_heading": "## Wrong claims about the bank\n\nPeople talked.\n\n" + S,
    "h11_bold_lies_line": "**Lies the tabloids told**\n\nPeople talked. Some wrote. Others posted.\n\n" + S,
    "h11_false_claims_heading": "## False claims about the bank\n\nPeople talked.\n\n" + S,
    # H12: a standalone falsity line longer than 12 tokens
    "h12_long_label_line": "Rumours that we investigated over the summer and found in the end to be false\n\nPeople talked. Some wrote. Others posted.\n\n" + S,
    # H13: "follows" synonyms
    "h13_what_comes_after": "What comes after is invented. One. Two. Three. " + S,
}

ATTACK_SHORT = {
    # H1 with a short claim: draft "Revenue doubles [S1]."
    "h1_short_claim_is_a_myth": "Revenue doubles is a myth.",
}

ATTACK_HEADINGS = [
    "# Acme Stumbles",            # H14: unlisted headline verb
    "# Bank Falters",
    "## CEO arrest looming",      # H14: final predicate participle
    "# Acme Under Investigation",  # H14: final predicate phrase
    "# Acme-guilty",              # H14: hyphen-joined predicate
    "# Bank Coll\u0251pses",       # H7/H14: Latin alpha in the headline verb
    "# Acme gu\u0131lty",          # H7/H14: dotless i
]

HEAD_SOURCE = CLAIM + "."
HEAD_BODY = CLAIM + " [S1].\n"


@pytest.mark.parametrize("name", sorted(ATTACK_SOURCES))
def test_r40_denied_source_is_refused(tmp_path: Path, name: str) -> None:
    report = gate(tmp_path, ATTACK_SOURCES[name])
    assert report["per_claim"][0]["verdict"] != "GROUNDED", (name, report["per_claim"])
    assert report["gate"] != "PASS", (name, report["gate"])


@pytest.mark.parametrize("name", sorted(ATTACK_SHORT))
def test_r40_denied_short_claim_is_refused(tmp_path: Path, name: str) -> None:
    report = gate(tmp_path, ATTACK_SHORT[name], "Revenue doubles [S1].\n")
    assert report["per_claim"][0]["verdict"] != "GROUNDED", (name, report["per_claim"])
    assert report["gate"] != "PASS", (name, report["gate"])


@pytest.mark.parametrize("heading", ATTACK_HEADINGS)
def test_r40_claim_heading_is_scored(tmp_path: Path, heading: str) -> None:
    report = gate(tmp_path, HEAD_SOURCE, heading + "\n\n" + HEAD_BODY)
    head = report["per_claim"][0]
    assert head["kind"] != "NON_CLAIM", (heading, head)
    assert report["gate"] != "PASS", (heading, report["gate"])
