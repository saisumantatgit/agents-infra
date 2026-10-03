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
    "ABSENCE":     "We found no evidence of a safety recall affecting the drone programme.",
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
    assert g.ClaimKind[kind] is not None  # the kind name is real, not a typo


def test_every_ClaimKind_is_covered_by_this_file():
    """POSITIVE CONTROL on the census itself.

    Four audit instruments under-reported in two days, each in the way its own
    construction required. This one asserts its own completeness: if a seventh
    kind is added and no fixture written, this fails rather than the file
    silently testing five of six.
    """
    covered = set(_DRAFTS) | {"NON_CLAIM"}  # NON_CLAIM is excluded by design
    assert covered == {k.name for k in g.ClaimKind}, (
        "a ClaimKind has no self-citation fixture here")
