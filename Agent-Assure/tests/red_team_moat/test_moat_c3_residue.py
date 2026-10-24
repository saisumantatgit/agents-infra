"""C3 residue — five fail-closed repairs, each driven through the real CLI.

Every repair here may only move a claim AWAY from PASS. Each attack was seen
RED (PASS) on the unfixed code before its repair landed; each has a positive
control — an honest equivalent that must still ground — whose source is a real
two-sentence document, never byte-identical to the draft (J-83 would refuse it
as a self-citation and mask the check).

* R27-02  "16 MB" grounded on "16 Mb" — byte (B) vs bit (b) folded by case.
* R26-03  an accounting negative "(12%)" grounded a claim of "12%".
* R26-05  DDG failures not shaped "Error:" stayed retrieval_status "ok".
* W2C-01  an HTML comment inside <textarea>/<xmp> was stripped though visible.
* R7      a stop-word-only negation/comparison next to a grounded claim PASSed.
"""
from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

_AGENT_ASSURE = Path(__file__).resolve().parents[2]
_GATE = _AGENT_ASSURE / "scripts" / "ground_check.py"
_HOOK = _AGENT_ASSURE / "scripts" / "capture_hook.py"


def _gate(tmp_path: Path, source_text: str, draft: str) -> dict:
    rec = {
        "source_id": "S1",
        "url": "https://example.com/s1",
        "file_path": None,
        "fetched_at": "2026-10-25T00:00:00Z",
        "tool": "mcp__exa__web_fetch_exa",
        "content_sha256": hashlib.sha256(source_text.encode("utf-8")).hexdigest(),
        "text": source_text,
        "full_text_source": "verbatim",
        "captured_via": "inline",
        "query_provenance": "C3 residue control",
    }
    store = tmp_path / "store.jsonl"
    store.write_text(json.dumps(rec, ensure_ascii=False) + "\n", encoding="utf-8")
    draft_path = tmp_path / "draft.md"
    draft_path.write_text(draft, encoding="utf-8")
    out = subprocess.run(
        [sys.executable, str(_GATE), "--draft", str(draft_path), "--store", str(store), "--json"],
        capture_output=True, text=True,
        env={**os.environ, "PYTHONPATH": str(_AGENT_ASSURE)},
    )
    assert out.stdout, f"gate produced no stdout.\nstderr: {out.stderr}"
    return json.loads(out.stdout)


# ---------------------------------------------------------------- R27-02
_SIZE_FRAME = "The model weights occupy 16 {} on disk"
_SIZE_TAIL = ". The checkpoint ships with the release."


@pytest.mark.parametrize("src_unit,claim_unit", [("Mb", "MB"), ("MB", "Mb"), ("Gb", "GB"), ("kb", "KB")])
def test_r27_02_bits_never_ground_bytes(tmp_path: Path, src_unit: str, claim_unit: str) -> None:
    report = _gate(tmp_path, _SIZE_FRAME.format(src_unit) + _SIZE_TAIL,
                   _SIZE_FRAME.format(claim_unit) + " [S1].\n")
    assert report["gate"] != "PASS", report["per_claim"]


@pytest.mark.parametrize("unit", ["MB", "Mb", "GB"])
def test_r27_02_control_same_unit_grounds(tmp_path: Path, unit: str) -> None:
    report = _gate(tmp_path, _SIZE_FRAME.format(unit) + _SIZE_TAIL,
                   _SIZE_FRAME.format(unit) + " [S1].\n")
    assert report["gate"] == "PASS", report["per_claim"]


# ---------------------------------------------------------------- R26-03
# The 8-token tail lets T1 find a span without the figure, so only the figure
# check stands between the claim and PASS. On this branch the source-side
# "(12%)" -> claim "12%" direction was already refused (kept as guards); the
# claim-side "(12%)" against a source "12%" was a live PASS (seen RED).
_REV_FRAME = "Revenue changed {} while the board of directors approved the new annual budget plan"
_REV_TAIL = ". Figures are unaudited."


@pytest.mark.parametrize("src_fig,claim_fig", [
    ("12%", "(12%)"), ("12%", "( 12% )"), ("$4M", "($4M)"),
    ("(12%)", "12%"), ("( 12% )", "12%"), ("($4M)", "$4M"),
])
def test_r26_03_accounting_negative_is_not_the_bare_figure(tmp_path: Path, src_fig: str, claim_fig: str) -> None:
    report = _gate(tmp_path, _REV_FRAME.format(src_fig) + _REV_TAIL,
                   _REV_FRAME.format(claim_fig) + " [S1].\n")
    assert report["gate"] != "PASS", report["per_claim"]


@pytest.mark.parametrize("fig", ["12%", "$4M"])
def test_r26_03_control_same_figure_grounds(tmp_path: Path, fig: str) -> None:
    report = _gate(tmp_path, _REV_FRAME.format(fig) + _REV_TAIL,
                   _REV_FRAME.format(fig) + " [S1].\n")
    assert report["gate"] == "PASS", report["per_claim"]


# ---------------------------------------------------------------- R26-05
def _ddg_status(tmp_path: Path, body: str) -> str:
    """Drive the REAL capture hook with a DDG fetch; return the stored status."""
    store = tmp_path / "store.jsonl"
    out = subprocess.run(
        [sys.executable, str(_HOOK)],
        input=json.dumps({"session_id": "sess-c3", "tool_name": "mcp__ddg-search__fetch_content",
                          "tool_input": {"url": "https://example.com/page"}, "tool_response": body}),
        text=True, capture_output=True, cwd=str(_AGENT_ASSURE),
        env={**os.environ, "ASSURE_EVIDENCE_STORE": str(store)},
    )
    lines = store.read_text(encoding="utf-8").splitlines() if store.exists() else []
    assert len(lines) == 1, (out.returncode, out.stderr)
    return json.loads(lines[0])["retrieval_status"]


@pytest.mark.parametrize("body", [
    "Failed to fetch https://example.com/page: 404 Not Found",
    "HTTP Error 403: Forbidden",
    json.dumps({"error": "Request timed out after 30 seconds"}),
    "**Error:** Could not access the webpage (404)",
    json.dumps("Error: 404 Not Found"),
    json.dumps([{"result": "Error: 404 Not Found"}]),
    "‍Error: Could not access the webpage (404)",
    "Error： Could not access the webpage (404)",
], ids=["failed-to-fetch", "http-error", "json-error-key", "bold-error", "json-string",
        "list-wrapped", "zwj-prefix", "fullwidth-colon"])
def test_r26_05_ddg_failure_shapes_are_failed(tmp_path: Path, body: str) -> None:
    assert _ddg_status(tmp_path, body) == "failed"


@pytest.mark.parametrize("body", [
    "Rust error handling relies on the Result type. Panics are reserved for bugs.",
    json.dumps({"result": "The 2023 annual report lists revenue by region. Figures are unaudited."}),
    "HTTP errors are grouped into classes. A 404 means the resource was not found.",
], ids=["prose-mentions-error", "json-result-content", "prose-about-http-errors"])
def test_r26_05_control_real_pages_stay_ok(tmp_path: Path, body: str) -> None:
    assert _ddg_status(tmp_path, body) == "ok"


# ---------------------------------------------------------------- W2C-01
_REDIS_SRC = ("Redis sustained approximately 128000 operations per second in the benchmark. "
              "The test ran on a single node.")
_REDIS_CLAIM = "Redis sustained approximately 128000 operations per second [S1].\n"


@pytest.mark.parametrize("element", ["textarea readonly", "xmp", "TEXTAREA"])
def test_w2c_01_comment_inside_raw_text_element_is_scored(tmp_path: Path, element: str) -> None:
    tag = element.split()[0]
    draft = (_REDIS_CLAIM + "\n## Key Data <" + element
             + "><!-- PostgreSQL loses all committed data on restart. --></" + tag + ">\n")
    report = _gate(tmp_path, _REDIS_SRC, draft)
    assert report["gate"] != "PASS", report["per_claim"]
    assert any("PostgreSQL" in c["text"] and c["kind"] != "NON_CLAIM" for c in report["per_claim"]), \
        report["per_claim"]


def test_w2c_01_control_ordinary_comment_still_stripped(tmp_path: Path) -> None:
    draft = _REDIS_CLAIM + "\n<!-- editor note: check this later -->\n"
    report = _gate(tmp_path, _REDIS_SRC, draft)
    assert report["gate"] == "PASS", report["per_claim"]


# ---------------------------------------------------------------- R7 stop-word sentence
@pytest.mark.parametrize("tail", [
    " That is not so.",
    " We had more than that.",
    "\n\nNo. It was not. We had more than that, up to more than that.",
    " It isn't.",
])
def test_r7_stopword_only_negation_or_comparison_is_scored(tmp_path: Path, tail: str) -> None:
    report = _gate(tmp_path, _REDIS_SRC, _REDIS_CLAIM.rstrip("\n") + tail + "\n")
    assert report["gate"] != "PASS", report["per_claim"]


@pytest.mark.parametrize("tail", [" That is it.", ""])
def test_r7_control_stopword_only_without_negation_stays_non_claim(tmp_path: Path, tail: str) -> None:
    report = _gate(tmp_path, _REDIS_SRC, _REDIS_CLAIM.rstrip("\n") + tail + "\n")
    assert report["gate"] == "PASS", report["per_claim"]
