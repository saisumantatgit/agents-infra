"""THE CLASS, not the instance: no claim KIND may be certified by the draft itself.

WHY THIS FILE EXISTS. Three consecutive adversarial rounds found the same shape,
and it was never the same bug:

  * **R16-01** — the figure checks were placed above `check_absence`, so they
    pre-empted stronger refusals (1,904 of 1,910 verdict changes were relabels).
  * **R17-01** — J-83's self-source filter was placed in the verbatim path, so
    the ABSENCE branch never saw it: a store of nothing but `Read` records of
    the draft certified at PASS 100.0.
  * and before both, **D-77** — a figure check gated on `kind == NUMERIC`, which
    an author routed around by adding one causal word.

`ground()` has **15 return statements across 6 kinds**. A check written at one
of them protects one of them. Every per-instance fix so far has been correct and
has left the class open, which is this project's oldest recorded lesson about
narrow fixes (CLAUDE.md: "a narrow fix closes the fixture it was written against
and leaves the class open — every time so far").

WHAT THIS ASSERTS. For **every** `ClaimKind`, a draft whose only evidence is
ITSELF cannot reach a PASS. It is a cross-product over kinds rather than a test
of one branch, so a future check added to one path and not another fails HERE
rather than in round 19.

THE CEILING, because this guard has one too: it enumerates KINDS, not return
statements. A new return added inside an existing kind's branch is not
automatically covered, and a seventh kind would need a fixture here. It narrows
the class; it does not close it.
"""
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
import unicodedata
from pathlib import Path

import pytest

_ROOT = Path(__file__).resolve().parents[2]
_GATE = _ROOT / "scripts" / "ground_check.py"
sys.path.insert(0, str(_ROOT / "scripts"))

import ground_check as g  # noqa: E402

# One draft per kind, each written so `classify` lands on that kind, and each
# citing [S1] where S1 will BE the draft.
_DRAFTS: dict[str, str] = {
    "FACTUAL":     "The Frankfurt desk maintains segregated client accounts [S1].",
    "NUMERIC":     "The Frankfurt desk reported 4,812 segregated accounts [S1].",
    # R18-01: this fixture carried NO FIGURE, so it never reached the figure
    # returns inside the ABSENCE branch — and a self-citation PASS lived there
    # for an hour. A figure is now present, which is the guard's own recorded
    # ceiling (KINDS, not returns) being paid down one return at a time.
    "ABSENCE":     "There is no fatality record for the 4200 aviation deaths.",
    "ABSENCE_NO_FIGURE":
                   "We found no evidence of a safety recall affecting the drone programme.",
    "ATTRIBUTION": "The regulator stated that the Frankfurt desk is compliant [S1].",
    "RELATIONAL":  "Poor reconciliation causes segregation failures at the desk [S1].",
}


def _self_store(draft: str, draft_path: Path, queries: list[str]) -> str:
    """A store whose every record IS the draft — the degenerate case."""
    digest = hashlib.sha256(
        unicodedata.normalize("NFKC", draft).encode()).hexdigest()
    return "".join(json.dumps({
        "source_id": f"S{i}", "url": None, "file_path": str(draft_path),
        "fetched_at": "2026-10-03T00:00:00Z", "tool": "Read",
        "content_sha256": digest, "text": draft,
        "full_text_source": "verbatim", "captured_via": "hook",
        "query_provenance": q, "session_id": "S-LIVE",
    }) + "\n" for i, q in enumerate(queries, start=1))


@pytest.mark.parametrize("kind,draft", sorted(_DRAFTS.items()))
def test_no_kind_can_be_certified_by_the_draft_itself(tmp_path, kind, draft):
    draft_path = tmp_path / "draft.md"
    draft_path.write_text(draft, encoding="utf-8")
    store = tmp_path / "store.jsonl"
    # Queries that WOULD qualify, so an absence claim fails on the self-source
    # rule rather than incidentally on the query rule — a fixture that refuses
    # for the wrong reason proves nothing (R17 caught exactly that in my own
    # control).
    store.write_text(_self_store(draft, draft_path, [
        "safety recall drone programme evidence",
        "drone programme recall evidence register",
    ]), encoding="utf-8")

    proc = subprocess.run(
        [sys.executable, str(_GATE), "--draft", str(draft_path),
         "--store", str(store), "--json"],
        capture_output=True, text=True, cwd=str(tmp_path), check=False)
    report = json.loads(proc.stdout)

    assert report["gate"] != "PASS", (
        f"{kind}: a draft certified ITSELF — {report}")
    assert proc.returncode != 0, kind
    assert g.ClaimKind[kind.split("_NO_")[0]] is not None  # real kind, not a typo


def test_every_ClaimKind_is_covered_by_this_file():
    """POSITIVE CONTROL on the census itself.

    Four audit instruments under-reported in two days, each in the way its own
    construction required. This one asserts its own completeness: if a seventh
    kind is added and no fixture written, this fails rather than the file
    silently testing five of six.
    """
    # ABSENCE_NO_FIGURE is a second FIXTURE for the ABSENCE kind, not a kind.
    covered = {k.split("_NO_")[0] for k in _DRAFTS} | {"NON_CLAIM"}
    assert covered == {k.name for k in g.ClaimKind}, (
        "a ClaimKind has no self-citation fixture here")


def test_a_self_record_ADDED_TO_a_real_store_cannot_buy_a_PASS(tmp_path):
    """R18-01's actual shape, which the all-self fixtures above CANNOT reach.

    When every record is the draft, the BASIS rule refuses first and the figure
    returns are never executed — so the parametrised cases above pass against a
    gate that still has the hole. I checked, expecting them to go red, and they
    did not. **A guard that cannot reach the return it is meant to protect is
    indistinguishable from no guard**, and only running it against the broken
    gate revealed that.

    The real shape is MIXED: two genuine retrieved sources, plus ONE `Read` of
    the draft. Before the fix, adding that single record flipped
    `UNVERIFIED_NUMBER` -> `ABSENCE_SUPPORTED` at PASS 100.0, because the draft
    contains the figure and so "verified" it.
    """
    draft = "There is no fatality record for the 4200 aviation deaths.\n"
    draft_path = tmp_path / "draft.md"
    draft_path.write_text(draft, encoding="utf-8")
    digest = hashlib.sha256(
        unicodedata.normalize("NFKC", draft).encode()).hexdigest()

    def row(sid, text, fp, sha, query):
        return json.dumps({
            "source_id": sid, "url": None, "file_path": fp,
            "fetched_at": "2026-10-03T00:00:00Z", "tool": "Read",
            "content_sha256": sha, "text": text, "full_text_source": "verbatim",
            "captured_via": "hook", "query_provenance": query,
            "session_id": "S-LIVE"})

    rows = [
        row("S1", "Quarterly revenue rose on strong fleet orders.",
            "/real/a.md", "a", "4200 fatality record aviation"),
        row("S2", "The plant added a second shift in June.",
            "/real/b.md", "b", "aviation 4200 fatality register"),
        row("S3", draft, str(draft_path), digest,
            "aviation 4200 fatality evidence sweep"),   # the draft itself
    ]
    store = tmp_path / "store.jsonl"
    store.write_text("".join(r + "\n" for r in rows), encoding="utf-8")
    proc = subprocess.run(
        [sys.executable, str(_GATE), "--draft", str(draft_path),
         "--store", str(store), "--json"],
        capture_output=True, text=True, cwd=str(tmp_path), check=False)
    report = json.loads(proc.stdout)
    assert report["per_claim"][0]["verdict"] == "UNVERIFIED_NUMBER", report
    assert report["gate"] == "FAIL"
    assert proc.returncode == 1

