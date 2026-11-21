"""E2-lite heading refusals; each attack is a PASS on origin/main."""
import pytest

from tests.red_team_moat._h_helpers import gate

BODY = "The board met in April and published its minutes online"


@pytest.mark.parametrize("label", ["Charges", "Fraud", "Crash", "Arrests",
                                    "Memory leaks", "Code folding", "Fast charging"])
def test_honest_noun_label_stays_unscored(tmp_path, label):
    report = gate(tmp_path, BODY, draft=f"## {label}\n\n{BODY} [S1].\n")
    assert report["per_claim"][0]["kind"] == "NON_CLAIM"
    assert report["gate"] == "PASS"


@pytest.mark.parametrize("heading,source", [
    ("The regulator found fraud at Quay Trust", "The regulator found fraud at Quay Trust. That never happened."),
    ("regulator found fraud at Quay Trust", "The regulator found fraud at Quay Trust. That never happened."),
    ("（ « regulator found fraud at Quay Trust » ）", "The regulator found fraud at Quay Trust. That never happened."),
    ("Quay Trust folds", "Quay Trust operates a regional office."),
    ("Quay Trust lied", "Quay Trust operates a regional office."),
    pytest.param("Quay Trust leaking", "Quay Trust operates a regional office.",
                 marks=pytest.mark.xfail(strict=True, reason="ambiguous gerund noun label")),
])
def test_heading_is_scored(tmp_path, heading, source):
    report = gate(tmp_path, BODY + ".\n\n" + source, draft=f"## {heading}\n\n" + BODY + " [S1].\n")
    assert report["gate"] != "PASS", report
    for label in ("Known issues", "Cost pressures", "Regional targets", "Harbour notes", "Rebase cheat sheet"):
        control = gate(tmp_path, BODY, draft=f"## {label}\n\n{BODY} [S1].\n")
        assert control["gate"] == "PASS", control
