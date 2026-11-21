"""R3 — compose before grounding (RED-TEAM-R45 F2, F3, F7, F8; OVN-1122-C1).

A predicate-free fragment (bare name, bare figure) used to ground by being
MENTIONED in its cited source while the draft's structure supplied the
predicate the reader reads. Every attack test below certified PASS on main
5e47ebf (proven red, recorded in the OVN-1122-C1 findings). The honest twins
must stay PASS.
"""
from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

AA = Path(__file__).resolve().parents[1]
GATE = AA / "scripts" / "ground_check.py"
sys.path.insert(0, str(AA / "scripts"))

import ground_check as gc  # noqa: E402

CARGO = "Alder Haulage delivers cargo."
FILLER = (" The archive describes how staff catalog documents and maintain the "
          "public reading room.")


def _record(source_id: str, text: str) -> dict:
    return {
        "source_id": source_id, "url": f"https://example.com/{source_id.lower()}",
        "file_path": None, "fetched_at": "2026-11-21T00:00:00Z",
        "tool": "mcp__exa__web_fetch_exa",
        "content_sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
        "text": text, "full_text_source": "verbatim", "captured_via": "inline",
        "query_provenance": "r3-compose",
    }


def gate(tmp_path: Path, sources: dict[str, str], draft: str) -> dict:
    """Run the real CLI on *draft* against a store holding *sources*."""
    store = tmp_path / "store.jsonl"
    store.write_text("".join(json.dumps(_record(k, v), ensure_ascii=False) + "\n"
                             for k, v in sources.items()), encoding="utf-8")
    draft_path = tmp_path / "draft.md"
    draft_path.write_text(draft, encoding="utf-8")
    out = subprocess.run(
        [sys.executable, str(GATE), "--draft", str(draft_path), "--store", str(store), "--json"],
        capture_output=True, text=True, env={**os.environ, "PYTHONPATH": str(AA)},
    )
    assert out.stdout, f"gate produced no stdout.\nstderr: {out.stderr}"
    return json.loads(out.stdout)


def _verdict(report: dict, startswith: str) -> str:
    rows = [c for c in report["per_claim"] if c["text"].startswith(startswith)]
    assert len(rows) == 1, report["per_claim"]
    return rows[0]["verdict"]


# --- F3: heading supplies the predicate of a bare name ---------------------

@pytest.mark.parametrize("heading,name", [
    ("Criminals", "Alder Haulage"),
    ("Fraudsters", "Haven Haulage"),        # name ends in -en (verb suffix)
    ("Sanctioned operators", "Alder Holdings"),  # name ends in -s
])
def test_f3_heading_over_bare_name_is_refused(tmp_path, heading, name):
    report = gate(tmp_path, {"S1": f"{name} delivers cargo." + FILLER},
                  f"## {heading}\n\n- {name} [S1]\n")
    assert report["gate"] != "PASS", report
    assert _verdict(report, f"- {name}") == "UNGROUNDED"


def test_f3_honest_heading_whose_composition_is_in_the_source(tmp_path):
    report = gate(tmp_path, {"S1": "Carriers: Alder Haulage, Birch Haulage." + FILLER},
                  "## Carriers\n\n- Alder Haulage [S1]\n- Birch Haulage [S1]\n")
    assert report["gate"] == "PASS", report


def test_honest_heading_over_honest_full_item(tmp_path):
    report = gate(tmp_path, {"S1": CARGO + FILLER},
                  "## Carriers\n\n- Alder Haulage delivers cargo [S1].\n")
    assert report["gate"] == "PASS", report


# --- F7: lead-in supplies the predicate ------------------------------------

LEAD = "The Alder council fined the following firms for fraud in 2024"


def test_f7_lead_in_over_name_from_another_source_is_refused(tmp_path):
    report = gate(tmp_path, {"S1": CARGO + FILLER, "S2": f"{LEAD}: other companies." + FILLER},
                  f"{LEAD} [S2]:\n\n- Alder Haulage [S1]\n")
    assert report["gate"] != "PASS", report
    assert _verdict(report, "- Alder Haulage") == "UNGROUNDED"


def test_f7_lead_in_and_name_citing_the_same_source_is_refused(tmp_path):
    # The lead-in's 8-gram is verbatim in S2 and S2 also mentions the name in
    # another sentence: the composed reading is in no single sentence of S2.
    report = gate(tmp_path, {"S2": f"{LEAD}: other companies. {CARGO}" + FILLER},
                  f"{LEAD} [S2]:\n\n- Alder Haulage [S2]\n")
    assert report["gate"] != "PASS", report
    assert _verdict(report, "- Alder Haulage") == "UNGROUNDED"


def test_f7_honest_lead_in_whose_composition_is_in_the_source(tmp_path):
    report = gate(tmp_path, {"S2": f"{LEAD}: other companies." + FILLER},
                  f"{LEAD} [S2]:\n\n- other companies [S2]\n")
    assert report["gate"] == "PASS", report


# --- F8: list continuation supplies the subject of a bare figure -----------

def test_f8_continuation_figure_is_refused(tmp_path):
    source = "Alder Haulage delivers cargo. Alder Storage earned 12 million dollars." + FILLER
    report = gate(tmp_path, {"S1": source},
                  "- Alder Haulage [S1]\n\n  12 million dollars [S1]\n")
    assert report["gate"] != "PASS", report
    assert _verdict(report, "12 million dollars") == "UNGROUNDED"


def test_f8_honest_full_claims_twin(tmp_path):
    source = "Alder Haulage delivers cargo. Alder Storage earned 12 million dollars." + FILLER
    report = gate(tmp_path, {"S1": source},
                  "- Alder Haulage delivers cargo [S1].\n\n"
                  "  Alder Storage earned 12 million dollars [S1].\n")
    assert report["gate"] == "PASS", report


def test_bare_fragment_with_no_structure_is_never_grounded_alone(tmp_path):
    report = gate(tmp_path, {"S1": CARGO + FILLER}, "- Alder Haulage [S1]\n")
    assert report["gate"] != "PASS", report
    assert _verdict(report, "- Alder Haulage") == "UNGROUNDED"


# --- F2: a disowning heading over a FULL claim (not closed by R3) -----------

@pytest.mark.xfail(strict=True, reason=(
    "F2 open. CEILING: R3 composes only predicate-free fragments; '## Myths' "
    "flips the sense of a complete verbatim claim, and separating it from "
    "'## Findings' needs the heading word's meaning (an author-controlled "
    "lexicon). Upgrade path: score a draft heading that is not source text "
    "(E2 brief) or an assertion test on the composed reading (R2/ADR)."))
def test_f2_disowning_heading_over_full_claim_is_refused(tmp_path):
    report = gate(tmp_path, {"S1": CARGO + FILLER},
                  "## Myths\n\n- Alder Haulage delivers cargo [S1].\n")
    assert report["gate"] != "PASS", report


# --- Fail-closed and purity properties --------------------------------------

def _claims(draft: str) -> list[gc.Claim]:
    return [gc.classify(c) for c in gc.decompose(draft)]


def _store(text: str) -> dict[str, gc.RetrievedSource]:
    return {"S1": gc.RetrievedSource(
        source_id="S1", url="https://example.com/s1", file_path=None,
        fetched_at="2026-11-21T00:00:00Z", tool="mcp__exa__web_fetch_exa",
        content_sha256="0" * 64, text=text, full_text_source="verbatim",
        captured_via="inline", query_provenance="r3")}


def test_uncomposed_mapping_never_lifts_a_verdict():
    # A claim that is UNCITED stays UNCITED and a NON_CLAIM stays out of the
    # denominator even when the mapping names them: R3 acts only on numerator
    # verdicts.
    claims = _claims("## Carriers\n\nAlder Haulage hauls freight daily.\n")
    store = _store(CARGO)
    plain = gc.score_report(claims, store)
    marked = gc.score_report(claims, store, uncomposed={c.index: "x" for c in claims})
    assert [c["verdict"] for c in plain["per_claim"]] == \
        [c["verdict"] for c in marked["per_claim"]]
    assert plain["scored_claims"] == marked["scored_claims"]


def test_r3_uncomposed_is_pure():
    claims = _claims("## Criminals\n\n- Alder Haulage [S1]\n")
    before = list(claims)
    store = _store(CARGO)
    first = gc.r3_uncomposed(claims, store, frozenset())
    assert claims == before
    assert first == gc.r3_uncomposed(claims, store, frozenset())
    assert first == {1: "Criminals Alder Haulage"}


@pytest.mark.parametrize("text,lacks", [
    ("- Alder Haulage [S1]", True),
    ("12 million dollars [S1]", True),
    ("- Haven Haulage [S1]", True),
    ("- other companies [S2]", True),
    ("- Alder Haulage delivers cargo [S1].", False),
    ("- Alder Haulage is a carrier [S1].", False),
])
def test_lacks_predicate(text, lacks):
    assert gc._lacks_predicate(text) is lacks


# --- Scope (D-144): split pieces, tables, prose ----------------------------

def test_split_piece_is_read_as_its_sentence(tmp_path):
    sentence = "The meeting was held in the main hall and lasted 28 minutes"
    report = gate(tmp_path, {"S1": sentence + "." + FILLER},
                  f"## Notes\n\n- {sentence} [S1].\n")
    assert report["gate"] == "PASS", report


def test_table_cells_are_out_of_r3_scope():
    # D-144: a cell keeps exactly the pre-R3 verdict, so R3 names no cell.
    draft = ("## Feature matrix\n\n| Feature | Starter | Team |\n|---|---|---|\n"
             "| Guest access | Yes [S1]. | Yes [S1]. |\n| Audit export | No [S1]. | Yes [S1]. |\n")
    claims = _claims(draft)
    assert any("|" in c.text and c.citations for c in claims)
    cells = gc.gfm_table_cells(draft, claims)
    assert cells, "cells of a real table carry table provenance"
    assert gc.r3_uncomposed(claims, _store("| Guest access | Yes | Yes |"), cells) == {}


# --- D-145: a `|` is not a table; only a real GFM table exempts ------------

@pytest.mark.parametrize("item", [
    "- Alder Haulage | [S1]",
    "- Alder | Haulage [S1]",
    "- Alder Haulage [S1]",
])
def test_pipe_inside_a_list_item_does_not_exempt(tmp_path, item):
    report = gate(tmp_path, {"S1": CARGO + FILLER}, f"## Criminals\n\n{item}\n")
    assert report["gate"] != "PASS", report


def test_real_table_cell_keeps_pre_r3_scope_exemption():
    draft = "| Firm | Status |\n|---|---|\n| Alder Haulage | Yes [S1]. |\n"
    claims = _claims(draft)
    cells = gc.gfm_table_cells(draft, claims)
    assert cells, "a header + delimiter row is a real table"
    assert gc.r3_uncomposed(claims, _store(CARGO + " Yes."), cells) == {}


def test_gfm_table_cells_needs_a_delimiter_row():
    for draft in ("## Criminals\n\n- Alder Haulage | [S1]\n", "a | b [S1]\nc | d [S1]\n"):
        assert gc.gfm_table_cells(draft, _claims(draft)) == frozenset()


# --- Own red-team of author-controlled surface (D-145 item 3) -------------

@pytest.mark.parametrize("item", [
    "- Alder Haulage [S1].",          # trailing punctuation
    "- [S1] Alder Haulage",           # citation placement
    "- **Alder Haulage** [S1]",       # bold
    "- *Alder Haulage* [S1]",         # italics
    "- `Alder Haulage` [S1]",         # inline code
    "+ Alder Haulage [S1]",           # + bullet
    "* Alder Haulage [S1]",           # * bullet
    "1. Alder Haulage [S1]",          # numbered list
    "1) Alder Haulage [S1]",
    "- Carriers\n  - Alder Haulage [S1]",  # nested indent
    "- Alder Haulage, [S1]",
])
def test_surface_variants_of_f3_are_refused(tmp_path, item):
    report = gate(tmp_path, {"S1": CARGO + FILLER}, f"## Criminals\n\n{item}\n")
    assert report["gate"] != "PASS", report


# Out-of-scope shapes (D-144 scope). Each evades R3 today; strict xfail so the
# day a fix closes one, the tripwire goes red.
_SCOPE_CEILING = ("CEILING (D-144 scope): R3 composes list items and their "
                  "continuations only. Upgrade path: compose along the real "
                  "Markdown tree from the R1 render step.")


@pytest.mark.xfail(strict=True, reason=_SCOPE_CEILING + " Paragraph under a heading.")
def test_bare_name_paragraph_under_heading_is_refused(tmp_path):
    report = gate(tmp_path, {"S1": CARGO + FILLER}, "## Criminals\n\nAlder Haulage [S1]\n")
    assert report["gate"] != "PASS", report


@pytest.mark.xfail(strict=True, reason=_SCOPE_CEILING + " Blockquote under a heading.")
def test_bare_name_blockquote_under_heading_is_refused(tmp_path):
    report = gate(tmp_path, {"S1": CARGO + FILLER}, "## Criminals\n\n> Alder Haulage [S1]\n")
    assert report["gate"] != "PASS", report


# Not an evasion today (the uncited label cell and merged rows refuse it);
# kept as a guard because table cells are outside R3 scope.
def test_bare_name_in_real_table_under_disowning_header_is_refused(tmp_path):
    report = gate(tmp_path, {"S1": CARGO + FILLER},
                  "## Records\n\n| Status | Firm |\n|---|---|\n"
                  "| Convicted | Alder Haulage [S1]. |\n")
    assert report["gate"] != "PASS", report


# --- D-147: wordless suppliers are transparent; table provenance is positional

@pytest.mark.parametrize("interposed", ["---", ".", "***", "\u2026", "\u2014", "\u26a0\ufe0f"])
def test_wordless_line_between_heading_and_item_is_transparent(tmp_path, interposed):
    report = gate(tmp_path, {"S1": CARGO + FILLER},
                  f"## Criminals\n\n{interposed}\n\n- Alder Haulage [S1]\n")
    assert report["gate"] != "PASS", report
    assert _verdict(report, "- Alder Haulage") == "UNGROUNDED"


def test_f7_wordless_line_between_lead_in_and_item(tmp_path):
    report = gate(tmp_path, {"S1": CARGO + FILLER, "S2": f"{LEAD}: other companies." + FILLER},
                  f"{LEAD} [S2]:\n\n.\n\n- Alder Haulage [S1]\n")
    assert report["gate"] != "PASS", report
    assert _verdict(report, "- Alder Haulage") == "UNGROUNDED"


def test_f8_wordless_lines_around_continuation(tmp_path):
    source = "Alder Haulage delivers cargo. Alder Storage earned 12 million dollars." + FILLER
    report = gate(tmp_path, {"S1": source},
                  ".\n\n- Alder Haulage [S1]\n\n  .\n\n  12 million dollars [S1]\n")
    assert report["gate"] != "PASS", report
    assert _verdict(report, "12 million dollars") == "UNGROUNDED"


@pytest.mark.parametrize("tail", [
    "| Firm | Activity |\n|---|---|\n| - Alder Haulage [S1] | delivers cargo [S1] |\n",
    "| Who is - Alder Haulage [S1]? |\n|---|\n",
    "| Firm |\n|---|\n| - Alder Haulage [S1] |\n",
    "<!--\n| x |\n|---|\n| - Alder Haulage [S1] |\n-->\n",
    "```\n| x |\n|---|\n| - Alder Haulage [S1] |\n```\n",
])
def test_table_text_elsewhere_does_not_exempt_the_item(tmp_path, tail):
    report = gate(tmp_path, {"S1": CARGO + FILLER},
                  f"## Criminals\n\n- Alder Haulage [S1]\n\n{tail}")
    assert _verdict(report, "- Alder Haulage") == "UNGROUNDED", report
