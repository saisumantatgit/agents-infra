"""R38 narrowing round: honest controls for the RED-TEAM-R37 Error-A shapes.

Each RESTORED control is an honest (source, draft) pair that main 83a5cb9
grounds and the R36 fixes (2dc776b) refused. They are proven red against
2dc776b (reports/R38-NARROWING.md). The GUARD tests pin the nearest
fabrication shape to each carve-out, so a narrowing cannot widen into a
pass: they hold on 2dc776b and after.

Shapes the R38 narrowing deliberately KEEPS refused (disclosed Error-A, named
in CEILING comments in scripts/ground_check.py) are not tested here as
grounding; they are listed in reports/R38-NARROWING.md."""
from __future__ import annotations

from pathlib import Path

import pytest

from tests.red_team_moat._h_helpers import CLAIM, TAIL, gate

S = CLAIM + "." + TAIL
F = " Staff left. Records were filed. "

RESTORED_SOURCES = {
    # predicative "false" about a code flag/value is not a falsity statement
    "flag_is_false": "When the strict flag is false, the parser accepts trailing commas." + F + S,
    "value_is_false": "If the option value is false, logging is disabled." + F + S,
    # "<event> never happened" about something the claim does not mention
    "merger_never_happened": "The planned merger never happened." + F + S,
    "rebound_did_not_happen": "The expected rebound did not happen." + F + S,
    # "made up" followed by a constituency adverb + "of", or by a quantity
    "board_made_up_entirely_of": "The board is made up entirely of independent directors." + F + S,
    "women_made_up_40": "Women made up 40 percent of the workforce." + F + S,
    "made_up_two_thirds": "Retail deposits made up two thirds of funding." + F + S,
    "made_up_mostly_of": "The panel was made up mostly of economists." + F + S,
    # a falsity word in a sentence that does not refer to the claim
    "fantasy_football": "Staff ran a fantasy football league." + F + S,
    "prosecutors_fabricated": "Prosecutors said the invoices were fabricated." + F + S,
    # "follows" as an ordinary verb, not "What follows"
    "procedure_follows": "The procedure follows the RFC, not the draft." + F + S,
    # a short negative pointing word with no veracity word, 3+ back
    "this_did_not_affect": "This did not affect depositors." + F + S,
    "none_of_this_changed": "None of this changed the outcome." + F + S,
    # FAQ headings that pair the denial word with a truth word
    "myths_and_facts_heading": "## Myths and facts\n\nPeople talked.\n\n" + S,
    "rumours_and_facts_line": "Rumours and facts\n\nPeople talked.\n\n" + S,
    "fact_or_fiction_heading": "## Fact or fiction\n\nPeople talked.\n\n" + S,
    # a "how" topic line ending in "made up"
    "how_committee_made_up": "How the committee is made up\n\nPeople talked.\n\n" + S,
}

RESTORED_HEADINGS = [
    "## Recent arrests",     # pre-modifier adjective before the -s word
    "## Two raids",
    "## Boom and bust",      # bare two-word coordination: no subject
    "## Everywhere",         # a one-word heading has no subject
]

# Nearest fabrication shape to each carve-out: must stay refused.
GUARD_SOURCES = {
    "made_up_entirely_bare": "The story is made up entirely." + F + S,
    "made_up_end": "The account was made up." + F + S,
    "collapse_never_happened": "The collapse never happened." + F + S,
    "that_never_happened": "That never happened." + F + S,
    "story_fabricated_far": "The story was fabricated." + F + S,
    "everything_here_fabricated": "Everything here was fabricated." + F + S,
    "none_of_this_accurate": "None of this is accurate." + F + S,
    "no_evidence_this": "There is no evidence for any of this." + F + S,
    "what_follows_untrue": "What follows is untrue. Staff left. Records were filed. " + S,
    "it_is_false": "It is false." + F + S,
    "myths_heading": "## Myths about the bank\n\nPeople talked.\n\n" + S,
    "how_heading_fabricated_body": "## How it works\n\nThat never happened. Staff left.\n\n" + S,
}

GUARD_HEADINGS = [
    "# Bank Collapses",
    "# Acme guilty",
    "# Acme guilty and doomed",
    "## Fraud everywhere",
    "## CEO arrest imminent",
    "## Revenue doubles",
    "## Acme crashes",
]

HEAD_SOURCE = CLAIM + "."
HEAD_BODY = CLAIM + " [S1].\n"


@pytest.mark.parametrize("name", sorted(RESTORED_SOURCES))
def test_restored_honest_source_grounds(tmp_path: Path, name: str) -> None:
    report = gate(tmp_path, RESTORED_SOURCES[name])
    assert report["per_claim"][0]["verdict"] == "GROUNDED", (name, report["per_claim"])
    assert report["gate"] == "PASS", (name, report["gate"])


@pytest.mark.parametrize("heading", RESTORED_HEADINGS)
def test_restored_label_heading_is_non_claim(tmp_path: Path, heading: str) -> None:
    report = gate(tmp_path, HEAD_SOURCE, heading + "\n\n" + HEAD_BODY)
    assert report["per_claim"][0]["kind"] == "NON_CLAIM", (heading, report["per_claim"][0])
    assert report["gate"] == "PASS", (heading, report["gate"])


@pytest.mark.parametrize("name", sorted(GUARD_SOURCES))
def test_guard_denial_still_refused(tmp_path: Path, name: str) -> None:
    report = gate(tmp_path, GUARD_SOURCES[name])
    assert report["per_claim"][0]["verdict"] != "GROUNDED", (name, report["per_claim"])
    assert report["gate"] != "PASS", (name, report["gate"])


@pytest.mark.parametrize("heading", GUARD_HEADINGS)
def test_guard_claim_heading_still_scored(tmp_path: Path, heading: str) -> None:
    report = gate(tmp_path, HEAD_SOURCE, heading + "\n\n" + HEAD_BODY)
    head = report["per_claim"][0]
    assert head["kind"] != "NON_CLAIM", (heading, head)
    assert report["gate"] != "PASS", (heading, report["gate"])
