"""R40b: the R40 H4 event-negation rule ("did not occur", "never took place")
narrowed to falsity statements. An event subject with an adjunct after the
verb reports a non-event and is honest; a pointing subject or a bare
clause-final negation still states falsity. Measured cost of the unnarrowed
rule: 54 grounded claims on tests/error_a_corpus (reports/R40b-NARROWING.md).

HONEST cases are refused by R40 as first written (proven red against HEAD
a928dbe) and must ground. ATTACK cases must stay refused after the narrowing:
main bb9b024 certifies two of them (event_subject_clause_final,
story_did_not_occur_adjunct, proven red against it); the other four main
already refuses through its adjacency rules."""
from __future__ import annotations

from pathlib import Path

import pytest

from tests.red_team_moat._h_helpers import CLAIM, TAIL, gate

HONEST_SOURCES = {
    "non_event_because": CLAIM + ". The planned follow-up wave never took place because funding ended." + TAIL,
    "non_event_last_quarter": CLAIM + ". The security review of the data migration never took place last quarter.",
    "non_event_in_month": CLAIM + ". The promised launch of the South showroom never took place in July.",
    "non_event_occur_adjunct": CLAIM + ". The second audit did not occur until 2025.",
}

ATTACK_SOURCES = {
    "that_never_took_place_adjunct": CLAIM + ". That never took place in March.",
    "it_did_not_take_place_adjunct": CLAIM + ". It did not take place at all.",
    "none_of_it_took_place": CLAIM + ". None of it took place in March.",
    "event_subject_clause_final": CLAIM + ". The collapse never took place.",
    "story_did_not_occur_adjunct": CLAIM + ". The story did not occur as told.",
    "what_follows_did_not_occur_far": "What follows did not occur in any form. Staff left. Records were filed. "
                                      + CLAIM + "." + TAIL,
}


@pytest.mark.parametrize("name", sorted(HONEST_SOURCES))
def test_r40b_honest_non_event_grounds(tmp_path: Path, name: str) -> None:
    report = gate(tmp_path, HONEST_SOURCES[name])
    assert report["per_claim"][0]["verdict"] == "GROUNDED", (name, report["per_claim"])
    assert report["gate"] == "PASS", (name, report["gate"])


@pytest.mark.parametrize("name", sorted(ATTACK_SOURCES))
def test_r40b_event_falsity_is_refused(tmp_path: Path, name: str) -> None:
    report = gate(tmp_path, ATTACK_SOURCES[name])
    assert report["per_claim"][0]["verdict"] != "GROUNDED", (name, report["per_claim"])
    assert report["gate"] != "PASS", (name, report["gate"])
